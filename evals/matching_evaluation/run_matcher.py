#!/usr/bin/env python3
"""
Run the Requirement–Evidence Matching benchmark against the production matcher.

Benchmark inputs:
  1) Fixed Candidate Evidence (120 evidence units)
  2) Representative Gold Requirements (32 atomic requirements)

IMPORTANT:
- This runner does NOT load the Gold output file.
- It does NOT rerun Evidence Extraction.
- It does NOT rerun Requirement Extraction.
- It calls the production matching pipeline directly:

    match_requirements_to_evidence(...)
        -> verify_negative_mappings(...)
        -> finalize_mappings(...)

Run from the AI Job Search Agent repository root, for example:

python evals/matching_evaluation/run_matcher.py \
  --evidence evals/matching_evaluation/fixed_inputs/01_input_fixed_candidate_evidence_v2.json \
  --requirements evals/matching_evaluation/fixed_inputs/02_input_representative_requirements_v2.json \
  --output evals/matching_evaluation/results/local_run.json

Required environment variables are the same ones used by the production LLM client,
for example:
  DASHSCOPE_API_KEY
  DASHSCOPE_BASE_URL
  GENERATION_MODEL
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow this runner to live under:
#   evals/matching_evaluation/run_matcher.py
# while still importing the repository-level `job_agent` package.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from job_agent.agents.evidence_matcher import match_requirements_to_evidence
from job_agent.agents.negative_conclusion_verifier import verify_negative_mappings
from job_agent.agents.reconciler import finalize_mappings, reconcile_counter_evidence
from job_agent.models.candidate import CandidateEvidenceBase, EvidenceUnit
from job_agent.models.job import JobRequirement


EXPECTED_EVIDENCE_COUNT = 120
EXPECTED_REQUIREMENT_COUNT = 32


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the fixed-input Requirement–Evidence Matching benchmark "
            "through the production matcher pipeline."
        )
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path(__file__).resolve().parent / "fixed_inputs" / "01_input_fixed_candidate_evidence_v2.json",
        help="Path to the fixed Candidate Evidence JSON.",
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        default=Path(__file__).resolve().parent / "fixed_inputs" / "02_input_representative_requirements_v2.json",
        help="Path to the 32 representative Gold Requirements JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "results" / "local_run.json",
        help="Where to write benchmark predictions.",
    )
    parser.add_argument(
        "--allow-count-mismatch",
        action="store_true",
        help=(
            "Allow inputs whose counts differ from the frozen benchmark "
            "(120 evidence / 32 requirements). Normally leave this off."
        ),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected top-level JSON object: {path}")

    return data


def load_candidate_evidence(path: Path) -> CandidateEvidenceBase:
    payload = load_json(path)
    raw_units = payload.get("evidence_units")

    if not isinstance(raw_units, list):
        raise ValueError(
            f"{path}: expected top-level 'evidence_units' list."
        )

    evidence_units: list[EvidenceUnit] = []

    for i, item in enumerate(raw_units, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: evidence item {i} is not an object.")

        evidence_units.append(
            EvidenceUnit(
                evidence_id=str(item["evidence_id"]),
                claim=str(item["claim"]),
                source_document=str(item["source_document"]),
                source_section=str(item["source_section"]),
                source_text=str(item["source_text"]),
                evidence_type=str(item["evidence_type"]),
                grounding_status=str(item["grounding_status"]),
            )
        )

    ids = [e.evidence_id for e in evidence_units]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate evidence_id values found in benchmark input.")

    return CandidateEvidenceBase(evidence_units=evidence_units)


def load_requirements(path: Path) -> list[JobRequirement]:
    payload = load_json(path)
    raw_requirements = payload.get("requirements")

    if not isinstance(raw_requirements, list):
        raise ValueError(
            f"{path}: expected top-level 'requirements' list."
        )

    requirements: list[JobRequirement] = []

    for i, item in enumerate(raw_requirements, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: requirement item {i} is not an object.")

        requirements.append(
            JobRequirement(
                requirement_id=str(item["requirement_id"]),
                requirement=str(item["requirement"]),
                category=str(item["category"]),
                requirement_level=str(item["requirement_level"]),
                jd_source_text=str(item["jd_source_text"]),
                jd_section=str(item["jd_section"]),
                grounding_status=str(item["grounding_status"]),
            )
        )

    ids = [r.requirement_id for r in requirements]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate requirement_id values found in benchmark input.")

    return requirements


def validate_frozen_inputs(
    evidence_base: CandidateEvidenceBase,
    requirements: list[JobRequirement],
    *,
    allow_count_mismatch: bool,
) -> None:
    evidence_count = len(evidence_base.evidence_units)
    requirement_count = len(requirements)

    if not allow_count_mismatch:
        if evidence_count != EXPECTED_EVIDENCE_COUNT:
            raise ValueError(
                f"Frozen benchmark expects {EXPECTED_EVIDENCE_COUNT} evidence units, "
                f"but loaded {evidence_count}. "
                "Use --allow-count-mismatch only if you intentionally changed the benchmark."
            )

        if requirement_count != EXPECTED_REQUIREMENT_COUNT:
            raise ValueError(
                f"Frozen benchmark expects {EXPECTED_REQUIREMENT_COUNT} requirements, "
                f"but loaded {requirement_count}. "
                "Use --allow-count-mismatch only if you intentionally changed the benchmark."
            )

    nonvalidated_evidence = [
        e.evidence_id
        for e in evidence_base.evidence_units
        if e.grounding_status != "VALIDATED"
    ]
    if nonvalidated_evidence:
        raise ValueError(
            "Benchmark matcher input must contain only VALIDATED evidence. "
            f"Non-validated IDs: {nonvalidated_evidence[:10]}"
        )

    nonvalidated_requirements = [
        r.requirement_id
        for r in requirements
        if r.grounding_status != "VALIDATED"
    ]
    if nonvalidated_requirements:
        raise ValueError(
            "Benchmark matcher input must contain only VALIDATED requirements. "
            f"Non-validated IDs: {nonvalidated_requirements[:10]}"
        )


def preflight_production_pipeline() -> None:
    """
    Protect benchmark integrity from a known legacy-schema mismatch.

    Some older repository snapshots referenced `requirement.importance`
    inside reconciliation even though JobRequirement no longer had that field.
    We do NOT silently monkey-patch production behavior for an evaluation run.
    """
    fields = getattr(JobRequirement, "__dataclass_fields__", {})
    source = inspect.getsource(reconcile_counter_evidence)

    if "requirement.importance" in source and "importance" not in fields:
        raise RuntimeError(
            "Production-code preflight failed: reconciler.py references "
            "`requirement.importance`, but the current JobRequirement schema "
            "does not define `importance`.\n\n"
            "Fix that production schema mismatch before running this benchmark. "
            "The evaluation runner intentionally does not patch production logic."
        )


def validate_final_coverage(
    requirements: list[JobRequirement],
    finalized_mappings: list[Any],
) -> None:
    expected_ids = {r.requirement_id for r in requirements}
    returned_ids = {m.requirement_id for m in finalized_mappings}

    missing = sorted(expected_ids - returned_ids)
    extra = sorted(returned_ids - expected_ids)

    if missing or extra:
        raise ValueError(
            "Final matcher coverage mismatch. "
            f"Missing={missing}, Extra={extra}"
        )

    if len(finalized_mappings) != len(requirements):
        raise ValueError(
            "Expected exactly one final mapping per requirement: "
            f"{len(requirements)} requirements vs "
            f"{len(finalized_mappings)} mappings."
        )


def summarize_support_levels(finalized_mappings: list[Any]) -> dict[str, int]:
    counts = {
        "STRONG": 0,
        "PARTIAL": 0,
        "WEAK": 0,
        "NOT_CLEARLY_SUPPORTED": 0,
    }

    for mapping in finalized_mappings:
        level = mapping.support_level
        counts[level] = counts.get(level, 0) + 1

    return counts


def main() -> int:
    args = parse_args()

    print("Loading frozen matcher benchmark inputs...")
    evidence_base = load_candidate_evidence(args.evidence)
    requirements = load_requirements(args.requirements)

    validate_frozen_inputs(
        evidence_base,
        requirements,
        allow_count_mismatch=args.allow_count_mismatch,
    )

    preflight_production_pipeline()

    model = os.getenv("GENERATION_MODEL")
    if not model:
        raise RuntimeError(
            "GENERATION_MODEL is not set. "
            "Use the same environment configuration as the production agent."
        )

    print(
        f"Loaded {len(evidence_base.evidence_units)} evidence units "
        f"and {len(requirements)} requirements."
    )
    print(f"Generation model: {model}")

    # ---------------------------------------------------------
    # Production Stage 1: first-pass semantic matching
    # ---------------------------------------------------------
    print("\n[1/3] Running first-pass requirement–evidence matching...")
    first_pass_mappings = match_requirements_to_evidence(
        requirements=requirements,
        evidence_base=evidence_base,
    )

    # ---------------------------------------------------------
    # Production Stage 2: challenge first-pass negatives
    # ---------------------------------------------------------
    first_pass_negative_count = sum(
        1
        for m in first_pass_mappings
        if m.support_level == "NOT_CLEARLY_SUPPORTED"
    )

    print(
        "\n[2/3] Running negative-conclusion verification "
        f"for {first_pass_negative_count} first-pass negative mappings..."
    )
    negative_verifications = verify_negative_mappings(
        mappings=first_pass_mappings,
        requirements=requirements,
        evidence_base=evidence_base,
    )

    # ---------------------------------------------------------
    # Production Stage 3: final reconciliation
    # ---------------------------------------------------------
    print("\n[3/3] Finalizing mappings...")
    finalized_mappings = finalize_mappings(
        mappings=first_pass_mappings,
        verifications=negative_verifications,
        requirements=requirements,
        evidence_base=evidence_base,
    )

    validate_final_coverage(requirements, finalized_mappings)

    prediction_payload = {
        "eval_name": "requirement_evidence_matching",
        "eval_version": "v2",
        "scope": "fixed_input_matcher_only",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "production_pipeline": [
            "job_agent.agents.evidence_matcher.match_requirements_to_evidence",
            "job_agent.agents.negative_conclusion_verifier.verify_negative_mappings",
            "job_agent.agents.reconciler.finalize_mappings",
        ],
        "model": model,
        "input_files": {
            "candidate_evidence": {
                "path": str(args.evidence),
                "sha256": sha256_file(args.evidence),
                "count": len(evidence_base.evidence_units),
            },
            "representative_requirements": {
                "path": str(args.requirements),
                "sha256": sha256_file(args.requirements),
                "count": len(requirements),
            },
        },
        "gold_output_loaded_during_run": False,
        "first_pass": {
            "mapping_count": len(first_pass_mappings),
            "negative_count": first_pass_negative_count,
            "mappings": [asdict(m) for m in first_pass_mappings],
        },
        "negative_verification": {
            "verification_count": len(negative_verifications),
            "verifications": [asdict(v) for v in negative_verifications],
        },
        "final": {
            "mapping_count": len(finalized_mappings),
            "support_distribution": summarize_support_levels(finalized_mappings),
            "mappings": [asdict(m) for m in finalized_mappings],
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(prediction_payload, f, ensure_ascii=False, indent=2)

    print("\nBenchmark run complete.")
    print(f"Predictions written to: {args.output}")
    print(
        "Final support distribution: "
        + json.dumps(
            prediction_payload["final"]["support_distribution"],
            ensure_ascii=False,
        )
    )
    print(
        "\nNext step: compare ONLY `final.mappings` against the "
        "human-adjudicated Gold output. Do not score `first_pass` as the "
        "final production prediction."
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        raise

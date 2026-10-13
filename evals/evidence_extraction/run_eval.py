"""Candidate Evidence Extraction offline evaluation runner.

Run from the repository root:

    python evals/evidence_extraction/run_eval.py

This runner intentionally evaluates ONLY the production evidence extractor:

    document -> extract_evidence_from_document() -> EvidenceUnit[]

It does not use Gmail, Web Search, Streamlit, SQLite, persistence, or the
separate evidence validator. The goal is to isolate the semantic extraction
component under controlled, repeatable inputs.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


# Allow this file to be run directly from the repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from job_agent.agents.evidence_extractor import extract_evidence_from_document


EVAL_DIR = Path(__file__).resolve().parent
INPUTS_DIR = EVAL_DIR / "inputs"
RESULTS_DIR = EVAL_DIR / "results"
RESULTS_PATH = RESULTS_DIR / "latest_predictions.json"
SUPPORTED_EXTENSIONS = {".md", ".txt"}


def evidence_to_dict(evidence, original_document_text: str) -> dict:
    """Serialize one EvidenceUnit and add deterministic contract checks."""

    source_text = evidence.source_text or ""

    return {
        "evidence_id": evidence.evidence_id,
        "claim": evidence.claim,
        "source_document": evidence.source_document,
        "source_section": evidence.source_section,
        "source_text": source_text,
        "evidence_type": evidence.evidence_type,
        "grounding_status": evidence.grounding_status,
        # These are deterministic checks, not semantic quality judgments.
        "checks": {
            "claim_nonempty": bool((evidence.claim or "").strip()),
            "source_text_nonempty": bool(source_text.strip()),
            "source_text_is_verbatim": bool(
                source_text and source_text in original_document_text
            ),
            "source_section_nonempty": bool(
                (evidence.source_section or "").strip()
            ),
            "evidence_type_nonempty": bool(
                (evidence.evidence_type or "").strip()
            ),
        },
    }


def get_input_files() -> list[Path]:
    """Return the frozen evaluation input documents in stable order."""

    if not INPUTS_DIR.exists():
        raise FileNotFoundError(
            f"Evaluation input directory does not exist: {INPUTS_DIR}"
        )

    files = sorted(
        path
        for path in INPUTS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        raise ValueError(
            "No evaluation input documents found. Put .md or .txt files in "
            f"{INPUTS_DIR.relative_to(REPO_ROOT)}"
        )

    return files


def main() -> None:
    input_files = get_input_files()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    model_name = os.getenv("GENERATION_MODEL")

    print("=" * 78)
    print("CANDIDATE EVIDENCE EXTRACTION EVALUATION")
    print("=" * 78)
    print(f"Model: {model_name or '(GENERATION_MODEL not set)'}")
    print(f"Input documents: {len(input_files)}")
    print("Scope: raw evidence extraction only")

    cases: list[dict] = []
    total_predictions = 0
    total_verbatim = 0
    total_empty_claims = 0

    for document_path in input_files:
        document_text = document_path.read_text(encoding="utf-8")

        print("\n" + "-" * 78)
        print(f"DOCUMENT: {document_path.name}")
        print("-" * 78)

        extracted = extract_evidence_from_document(
            document_name=document_path.name,
            document_text=document_text,
        )

        predictions = [
            evidence_to_dict(evidence, document_text)
            for evidence in extracted
        ]

        for item in predictions:
            total_predictions += 1
            total_verbatim += int(
                item["checks"]["source_text_is_verbatim"]
            )
            total_empty_claims += int(
                not item["checks"]["claim_nonempty"]
            )

            print(
                f"{item['evidence_id']}: "
                f"{item['claim']}"
            )
            print(
                "  source_text_is_verbatim: "
                f"{item['checks']['source_text_is_verbatim']}"
            )

        print(f"Extracted evidence count: {len(predictions)}")

        cases.append(
            {
                "document_name": document_path.name,
                "prediction_count": len(predictions),
                "predictions": predictions,
            }
        )

    verbatim_rate = (
        total_verbatim / total_predictions
        if total_predictions
        else None
    )

    output = {
        "eval_name": "candidate_evidence_extraction",
        "eval_version": "v1",
        "scope": "raw_extractor_only",
        "model": model_name,
        "input_documents": [path.name for path in input_files],
        "summary": {
            "document_count": len(input_files),
            "prediction_count": total_predictions,
            "verbatim_source_count": total_verbatim,
            "verbatim_source_rate": verbatim_rate,
            "empty_claim_count": total_empty_claims,
        },
        "cases": cases,
    }

    RESULTS_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n" + "=" * 78)
    print("RUN SUMMARY")
    print("=" * 78)
    print(f"Documents:              {len(input_files)}")
    print(f"Evidence predictions:   {total_predictions}")
    if verbatim_rate is None:
        print("Verbatim source rate:   n/a")
    else:
        print(f"Verbatim source rate:   {verbatim_rate:.1%}")
    print(f"Empty claims:           {total_empty_claims}")
    print(
        "\nPredictions written to: "
        f"{RESULTS_PATH.relative_to(REPO_ROOT)}"
    )
    print(
        "\nImportant: this runner does not decide whether the semantic "
        "evidence quality is good. Compare these predictions against the "
        "human-adjudicated gold set in the next evaluation step."
    )


if __name__ == "__main__":
    main()

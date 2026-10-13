from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Expected location:
# <repo_root>/evals/requirement_extraction/run_eval.py
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from job_agent.agents.requirement_analyzer import (  # noqa: E402
    extract_requirements_from_jd,
)


EVAL_DIR = Path(__file__).resolve().parent
CASES_PATH = EVAL_DIR / "cases_v1.json"
RESULTS_DIR = EVAL_DIR / "results"

ALLOWED_CATEGORIES = {
    "RESPONSIBILITY",
    "EXPERIENCE",
    "SKILL",
    "DOMAIN_KNOWLEDGE",
    "EDUCATION",
    "LICENSE",
    "CERTIFICATION",
    "OTHER",
}

ALLOWED_LEVELS = {
    "CORE",
    "REQUIRED",
    "PREFERRED",
}


def serialize_requirement(requirement: Any, jd_text: str) -> dict[str, Any]:
    """
    Convert the production JobRequirement object into a JSON-safe eval record.

    IMPORTANT:
    This runner evaluates the RAW requirement extractor only.
    It does NOT call requirement_validator, matching, scoring, DB, Gmail, or web.
    """
    if is_dataclass(requirement):
        raw = asdict(requirement)
    else:
        raw = {
            "requirement_id": getattr(requirement, "requirement_id", None),
            "requirement": getattr(requirement, "requirement", ""),
            "category": getattr(requirement, "category", ""),
            "requirement_level": getattr(requirement, "requirement_level", ""),
            "jd_source_text": getattr(requirement, "jd_source_text", ""),
            "jd_section": getattr(requirement, "jd_section", ""),
            "grounding_status": getattr(requirement, "grounding_status", None),
        }

    source_text = str(raw.get("jd_source_text") or "")
    requirement_text = str(raw.get("requirement") or "")
    category = str(raw.get("category") or "")
    level = str(raw.get("requirement_level") or "")
    section = str(raw.get("jd_section") or "")

    return {
        **raw,
        "checks": {
            "requirement_nonempty": bool(requirement_text.strip()),
            "category_allowed": category in ALLOWED_CATEGORIES,
            "requirement_level_allowed": level in ALLOWED_LEVELS,
            "jd_source_text_nonempty": bool(source_text.strip()),
            "jd_source_text_is_verbatim": bool(source_text) and source_text in jd_text,
            "jd_section_nonempty": bool(section.strip()),
        },
    }


def load_cases() -> list[dict[str, Any]]:
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("cases_v1.json field 'cases' must be a list.")
    return cases


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case["case_id"])
    filename = str(case["filename"])
    jd_text = str(case["jd_text"])

    try:
        requirements = extract_requirements_from_jd(jd_text)

        predictions = [
            serialize_requirement(req, jd_text)
            for req in requirements
        ]

        return {
            "case_id": case_id,
            "filename": filename,
            "status": "SUCCESS",
            "prediction_count": len(predictions),
            "predictions": predictions,
            "error": None,
        }

    except Exception as exc:
        # Eval runner isolates cases so one failure does not destroy the
        # observations from the remaining benchmark cases.
        return {
            "case_id": case_id,
            "filename": filename,
            "status": "ERROR",
            "prediction_count": 0,
            "predictions": [],
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the production Job Requirement Extractor on eval set v1."
    )
    parser.add_argument(
        "--case",
        dest="case_id",
        help="Optional single case ID, e.g. REQ001. Default: run all cases.",
    )
    args = parser.parse_args()

    cases = load_cases()

    if args.case_id:
        cases = [
            case
            for case in cases
            if str(case.get("case_id")) == args.case_id
        ]
        if not cases:
            raise ValueError(f"Unknown case_id: {args.case_id}")

    results = []

    print("=" * 72)
    print("JOB REQUIREMENT EXTRACTION EVAL")
    print("=" * 72)
    print(f"Cases: {len(cases)}")
    print()

    for index, case in enumerate(cases, start=1):
        case_id = str(case["case_id"])
        filename = str(case["filename"])

        print(f"[{index}/{len(cases)}] {case_id} — {filename}")

        result = run_case(case)
        results.append(result)

        if result["status"] == "SUCCESS":
            print(f"  extracted: {result['prediction_count']}")
            for pred in result["predictions"]:
                print(
                    "  - "
                    f"{pred.get('requirement_id')} | "
                    f"{pred.get('requirement_level')} | "
                    f"{pred.get('category')} | "
                    f"{pred.get('requirement')}"
                )
        else:
            print(
                "  ERROR: "
                f"{result['error']['type']}: "
                f"{result['error']['message']}"
            )

        print()

    all_predictions = [
        pred
        for result in results
        for pred in result["predictions"]
    ]

    verbatim_count = sum(
        1
        for pred in all_predictions
        if pred["checks"]["jd_source_text_is_verbatim"]
    )

    error_case_count = sum(
        1 for result in results
        if result["status"] == "ERROR"
    )

    output = {
        "eval_name": "job_requirement_extraction",
        "eval_version": "v1",
        "scope": "raw_extractor_only",
        "production_function": (
            "job_agent.agents.requirement_analyzer."
            "extract_requirements_from_jd"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "case_count": len(results),
        "error_case_count": error_case_count,
        "prediction_count": len(all_predictions),
        "verbatim_source_count": verbatim_count,
        "verbatim_source_rate": (
            verbatim_count / len(all_predictions)
            if all_predictions
            else None
        ),
        "cases": results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "latest_predictions.json"
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("=" * 72)
    print("COMPLETE")
    print("=" * 72)
    print(f"Predictions: {output['prediction_count']}")
    print(f"Case errors: {output['error_case_count']}")
    if output["verbatim_source_rate"] is not None:
        print(
            "Exact source-text rate: "
            f"{output['verbatim_source_rate']:.1%}"
        )
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

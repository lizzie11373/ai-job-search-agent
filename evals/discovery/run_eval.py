"""Reusable discovery-layer evaluation for Project 3."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# Allow running this file from the repository root:
#     python evals/discovery/run_eval.py
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from job_agent.agents.email_classifier import is_job_related_email
from job_agent.agents.job_candidate_extractor import (
    extract_job_candidates_from_email,
)


EVAL_DIR = Path(__file__).resolve().parent
CASES_PATH = EVAL_DIR / "cases_v1.json"
RESULTS_DIR = EVAL_DIR / "results"


def norm(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value).casefold().strip())


def candidate_to_dict(candidate) -> dict:
    return {
        "source": candidate.source,
        "source_message_id": candidate.source_message_id,
        "title": candidate.title,
        "company": candidate.company,
        "location": candidate.location,
        "source_url": candidate.source_url,
        "source_item_id": candidate.source_item_id,
    }


def find_match(expected: dict, predictions: list[dict], used: set[int]) -> int | None:
    expected_id = norm(expected.get("source_item_id"))

    # Prefer stable provider ID.
    if expected_id:
        for i, pred in enumerate(predictions):
            if i in used:
                continue
            if norm(pred.get("source_item_id")) == expected_id:
                return i

        # Fallback if the ID was preserved in the URL but not copied into source_item_id.
        for i, pred in enumerate(predictions):
            if i in used:
                continue
            if expected_id in (pred.get("source_url") or ""):
                return i

    # Fallback for providers/templates without an explicit stable ID.
    for i, pred in enumerate(predictions):
        if i in used:
            continue
        if (
            norm(pred.get("title")) == norm(expected.get("title"))
            and norm(pred.get("company")) == norm(expected.get("company"))
        ):
            return i

    return None


def percentage(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a"
    return f"{numerator / denominator:.1%}"


def ratio_or_none(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = data["cases"]

    run_timestamp = datetime.now(timezone.utc)
    run_id = run_timestamp.strftime("%Y%m%dT%H%M%SZ")

    classifier_correct = 0
    classifier_total = 0

    tp = fp = fn = 0
    matched = 0
    title_correct = 0
    company_correct = 0
    provider_id_correct = 0
    provider_id_total = 0

    prediction_cases: list[dict] = []
    evaluation_cases: list[dict] = []

    for case in cases:
        print("\n" + "=" * 78)
        print(f"{case['case_id']} | {case['source']}")
        print("=" * 78)
        print(case["subject"])

        predicted_related = is_job_related_email(
            sender=case["sender"],
            subject=case["subject"],
            snippet=case["snippet"],
        )

        expected_related = case["expected_job_related"]
        classifier_ok = predicted_related == expected_related

        classifier_total += 1
        classifier_correct += int(classifier_ok)

        print(
            f"\nClassifier: predicted={predicted_related} "
            f"expected={expected_related}"
        )

        predicted_jobs: list[dict] = []

        if predicted_related:
            candidates = extract_job_candidates_from_email(
                source=case["source"],
                message_id=case["message_id"],
                email_body=case["body"],
            )
            predicted_jobs = [candidate_to_dict(c) for c in candidates]

        expected_jobs = case.get("expected_jobs", [])
        print(
            f"Candidates: predicted={len(predicted_jobs)} "
            f"expected={len(expected_jobs)}"
        )

        used: set[int] = set()
        case_matches: list[dict] = []
        case_misses: list[dict] = []

        for expected in expected_jobs:
            idx = find_match(expected, predicted_jobs, used)

            if idx is None:
                fn += 1
                case_misses.append(expected)
                print(
                    f"\n  MISS: {expected['company']} | "
                    f"{expected['title']}"
                )
                continue

            used.add(idx)
            pred = predicted_jobs[idx]
            tp += 1
            matched += 1

            title_ok = norm(pred["title"]) == norm(expected["title"])
            company_ok = norm(pred["company"]) == norm(expected["company"])

            title_correct += int(title_ok)
            company_correct += int(company_ok)

            expected_id = expected.get("source_item_id")
            provider_id_preserved = None

            if expected_id:
                provider_id_total += 1
                provider_id_preserved = (
                    norm(pred.get("source_item_id")) == norm(expected_id)
                    or expected_id in (pred.get("source_url") or "")
                )
                provider_id_correct += int(provider_id_preserved)

            location_review = {
                "reference": expected.get("location_reference"),
                "prediction": pred.get("location"),
                "human_judgment": "PENDING",
                "notes": "",
            }

            case_matches.append(
                {
                    "expected": expected,
                    "prediction": pred,
                    "title_exact_normalized": title_ok,
                    "company_exact_normalized": company_ok,
                    "provider_id_preserved": provider_id_preserved,
                    "location_review": location_review,
                }
            )

            print(f"\n  MATCH: {pred['company']} | {pred['title']}")
            print(f"    title_exact: {title_ok}")
            print(f"    company_exact: {company_ok}")
            print(f"    provider_id_preserved: {provider_id_preserved}")
            print(f"    source_url: {pred.get('source_url')}")
            print(f"    source_item_id: {pred.get('source_item_id')}")

            # Location is intentionally manual.
            print("    --- LOCATION MANUAL REVIEW ---")
            print(
                f"    email_reference: "
                f"{expected.get('location_reference')}"
            )
            print(f"    model_output:    {pred.get('location')}")
            print("    human_judgment:  PASS / FAIL / UNCLEAR")

        extras = [
            pred
            for i, pred in enumerate(predicted_jobs)
            if i not in used
        ]
        fp += len(extras)

        if extras:
            print(f"\n  EXTRA candidates: {len(extras)}")
            for pred in extras:
                print(f"    - {pred['company']} | {pred['title']}")

        prediction_cases.append(
            {
                "case_id": case["case_id"],
                "predicted_job_related": predicted_related,
                "jobs": predicted_jobs,
            }
        )

        evaluation_cases.append(
            {
                "case_id": case["case_id"],
                "eval_bucket": case.get("eval_bucket"),
                "source": case["source"],
                "expected_job_related": expected_related,
                "predicted_job_related": predicted_related,
                "classifier_correct": classifier_ok,
                "expected_job_count": len(expected_jobs),
                "predicted_job_count": len(predicted_jobs),
                "matches": case_matches,
                "misses": case_misses,
                "extras": extras,
            }
        )

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    summary = {
        "case_count": len(cases),
        "classifier": {
            "correct": classifier_correct,
            "total": classifier_total,
            "accuracy": ratio_or_none(classifier_correct, classifier_total),
        },
        "candidate_extraction": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        },
        "matched_candidate_fields": {
            "matched_candidates": matched,
            "title_exact_normalized_correct": title_correct,
            "title_exact_normalized_accuracy": ratio_or_none(
                title_correct, matched
            ),
            "company_exact_normalized_correct": company_correct,
            "company_exact_normalized_accuracy": ratio_or_none(
                company_correct, matched
            ),
            "provider_id_cases": provider_id_total,
            "provider_id_preserved": provider_id_correct,
            "provider_id_preservation_rate": ratio_or_none(
                provider_id_correct, provider_id_total
            ),
        },
        "location_review": {
            "mode": "HUMAN_REVIEW",
            "status": "PENDING",
            "allowed_judgments": ["PASS", "FAIL", "UNCLEAR"],
        },
    }

    print("\n" + "=" * 78)
    print("DISCOVERY EVAL SUMMARY")
    print("=" * 78)

    print(
        f"Classifier accuracy: "
        f"{percentage(classifier_correct, classifier_total)}"
    )
    print(f"Candidate precision: {precision:.1%}")
    print(f"Candidate recall: {recall:.1%}")
    print(f"Candidate F1: {f1:.1%}")
    print(
        f"Title exact-normalized accuracy: "
        f"{percentage(title_correct, matched)}"
    )
    print(
        f"Company exact-normalized accuracy: "
        f"{percentage(company_correct, matched)}"
    )
    print(
        f"Provider job-ID preservation: "
        f"{percentage(provider_id_correct, provider_id_total)}"
    )
    print("Location: MANUAL REVIEW (no exact-string metric)")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Preserve the original lightweight prediction artifact for compatibility.
    predictions_payload = {
        "eval_version": data.get("version"),
        "run_id": run_id,
        "timestamp_utc": run_timestamp.isoformat(),
        "cases_sha256": file_sha256(CASES_PATH),
        "cases": prediction_cases,
    }
    predictions_path = RESULTS_DIR / "latest_predictions.json"
    predictions_path.write_text(
        json.dumps(predictions_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # 2) Save a complete scored evaluation artifact.
    evaluation_payload = {
        "eval_name": "discovery",
        "eval_version": data.get("version"),
        "scope": data.get("scope"),
        "dataset_type": data.get("dataset_type"),
        "run_id": run_id,
        "timestamp_utc": run_timestamp.isoformat(),
        "input_file": str(CASES_PATH.relative_to(REPO_ROOT)),
        "input_sha256": file_sha256(CASES_PATH),
        "summary": summary,
        "cases": evaluation_cases,
    }

    latest_evaluation_path = RESULTS_DIR / "latest_evaluation.json"
    latest_evaluation_path.write_text(
        json.dumps(evaluation_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # 3) Keep an immutable timestamped run so future runs can be compared.
    archived_evaluation_path = (
        RESULTS_DIR / f"discovery_eval_{data.get('version', 'unknown')}_{run_id}.json"
    )
    archived_evaluation_path.write_text(
        json.dumps(evaluation_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(
        f"\nPredictions written to: "
        f"{predictions_path.relative_to(REPO_ROOT)}"
    )
    print(
        f"Scored evaluation written to: "
        f"{latest_evaluation_path.relative_to(REPO_ROOT)}"
    )
    print(
        f"Archived run written to: "
        f"{archived_evaluation_path.relative_to(REPO_ROOT)}"
    )
    print(
        "\nNext step: review each matched candidate's location_review field "
        "and replace PENDING with PASS / FAIL / UNCLEAR before closing the eval."
    )
    print(
        "Reminder: aggregate scores are only useful after checking "
        "individual failures and manual-review fields."
    )


if __name__ == "__main__":
    main()

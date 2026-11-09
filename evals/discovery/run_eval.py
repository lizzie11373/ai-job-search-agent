"""Reusable discovery-layer evaluation for Project 3."""

from __future__ import annotations

import json
import re
import sys
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


def find_match(
    expected: dict,
    predictions: list[dict],
    used: set[int],
) -> int | None:
    expected_id = norm(expected.get("source_item_id"))

    # Prefer stable provider ID.
    if expected_id:
        for i, pred in enumerate(predictions):
            if i in used:
                continue
            if norm(pred.get("source_item_id")) == expected_id:
                return i

        # Fallback if the ID was preserved in the URL but not copied into
        # source_item_id.
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


def main() -> None:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = data["cases"]

    classifier_correct = 0
    classifier_total = 0

    # Candidate metrics include only cases where candidate extraction
    # completed normally. A runtime/extraction exception is tracked
    # separately as a case execution failure so it cannot be mistaken
    # for a correct "0 candidates" prediction.
    tp = fp = fn = 0
    matched = 0
    title_correct = 0
    company_correct = 0
    provider_id_correct = 0
    provider_id_total = 0
    candidate_evaluable_cases = 0

    case_total = len(cases)
    case_passes = 0
    case_execution_errors = 0

    output_cases = []

    for case in cases:
        print("\n" + "=" * 78)
        print(f"{case['case_id']} | {case['source']}")
        print("=" * 78)
        print(case["subject"])

        expected_related = case["expected_job_related"]
        expected_jobs = case.get("expected_jobs", [])

        predicted_related: bool | None = None
        predicted_jobs: list[dict] = []
        case_error: str | None = None

        # ------------------------------------------------------------
        # 1. EMAIL METADATA CLASSIFICATION
        # ------------------------------------------------------------
        try:
            predicted_related = is_job_related_email(
                sender=case["sender"],
                subject=case["subject"],
                snippet=case["snippet"],
            )
        except Exception as error:
            case_error = f"{type(error).__name__}: {error}"
            print(f"\nClassifier ERROR: {case_error}")
        else:
            classifier_total += 1
            classifier_correct += int(
                predicted_related == expected_related
            )

            print(
                f"\nClassifier: predicted={predicted_related} "
                f"expected={expected_related}"
            )

        # ------------------------------------------------------------
        # 2. JOB CANDIDATE EXTRACTION
        # ------------------------------------------------------------
        extraction_completed = False

        if case_error is None:
            if predicted_related:
                try:
                    candidates = extract_job_candidates_from_email(
                        source=case["source"],
                        message_id=case["message_id"],
                        email_body=case["body"],
                    )
                    predicted_jobs = [
                        candidate_to_dict(candidate)
                        for candidate in candidates
                    ]
                    extraction_completed = True
                except Exception as error:
                    case_error = f"{type(error).__name__}: {error}"
                    print(f"\nCandidate extraction ERROR: {case_error}")
            else:
                # If the classifier routes the email away from extraction,
                # candidate output is deterministically empty for this run.
                extraction_completed = True

        print(
            f"Candidates: predicted={len(predicted_jobs)} "
            f"expected={len(expected_jobs)}"
        )

        # ------------------------------------------------------------
        # 3. CANDIDATE-LEVEL SCORING
        # ------------------------------------------------------------
        # Do NOT score a case whose extraction raised. Treating an exception
        # as predicted_jobs=[] could falsely make an expected-empty case look
        # correct. The execution error is instead surfaced at case level.
        used: set[int] = set()
        case_tp = 0
        case_fp = 0
        case_fn = 0

        if extraction_completed and case_error is None:
            candidate_evaluable_cases += 1

            for expected in expected_jobs:
                idx = find_match(expected, predicted_jobs, used)

                if idx is None:
                    fn += 1
                    case_fn += 1
                    print(
                        f"\n  MISS: {expected['company']} | "
                        f"{expected['title']}"
                    )
                    continue

                used.add(idx)
                pred = predicted_jobs[idx]
                tp += 1
                case_tp += 1
                matched += 1

                title_ok = (
                    norm(pred["title"])
                    == norm(expected["title"])
                )
                company_ok = (
                    norm(pred["company"])
                    == norm(expected["company"])
                )

                title_correct += int(title_ok)
                company_correct += int(company_ok)

                expected_id = expected.get("source_item_id")
                provider_id_preserved = None

                if expected_id:
                    provider_id_total += 1
                    provider_id_preserved = (
                        norm(pred.get("source_item_id"))
                        == norm(expected_id)
                        or expected_id
                        in (pred.get("source_url") or "")
                    )
                    provider_id_correct += int(
                        provider_id_preserved
                    )

                print(
                    f"\n  MATCH: "
                    f"{pred['company']} | {pred['title']}"
                )
                print(f"    title_exact: {title_ok}")
                print(f"    company_exact: {company_ok}")
                print(
                    "    provider_id_preserved: "
                    f"{provider_id_preserved}"
                )
                print(
                    f"    source_url: "
                    f"{pred.get('source_url')}"
                )
                print(
                    f"    source_item_id: "
                    f"{pred.get('source_item_id')}"
                )

                # Location is intentionally manual.
                print("    --- LOCATION MANUAL REVIEW ---")
                print(
                    "    email_reference: "
                    f"{expected.get('location_reference')}"
                )
                print(
                    "    model_output:    "
                    f"{pred.get('location')}"
                )
                print(
                    "    human_judgment:  "
                    "PASS / FAIL / UNCLEAR"
                )

            extras = [
                pred
                for i, pred in enumerate(predicted_jobs)
                if i not in used
            ]
            fp += len(extras)
            case_fp += len(extras)

            if extras:
                print(
                    f"\n  EXTRA candidates: "
                    f"{len(extras)}"
                )
                for pred in extras:
                    print(
                        f"    - "
                        f"{pred['company']} | {pred['title']}"
                    )

        # ------------------------------------------------------------
        # 4. CASE-LEVEL PASS / FAIL
        # ------------------------------------------------------------
        classifier_ok = (
            predicted_related == expected_related
            if predicted_related is not None
            else False
        )

        candidate_output_ok = (
            extraction_completed
            and case_error is None
            and case_fn == 0
            and case_fp == 0
            and case_tp == len(expected_jobs)
        )

        case_pass = (
            case_error is None
            and classifier_ok
            and candidate_output_ok
        )

        if case_error is not None:
            case_execution_errors += 1

        if case_pass:
            case_passes += 1
            print("\nCase result: PASS")
        else:
            print("\nCase result: FAIL")
            if case_error is not None:
                print(f"Reason: execution error -> {case_error}")
            elif not classifier_ok:
                print(
                    "Reason: classifier mismatch "
                    f"(predicted={predicted_related}, "
                    f"expected={expected_related})"
                )
            else:
                print(
                    "Reason: candidate output mismatch "
                    f"(tp={case_tp}, fp={case_fp}, fn={case_fn})"
                )

        output_cases.append(
            {
                "case_id": case["case_id"],
                "eval_bucket": case.get("eval_bucket"),
                "expected_job_related": expected_related,
                "predicted_job_related": predicted_related,
                "expected_job_count": len(expected_jobs),
                "predicted_job_count": len(predicted_jobs),
                "candidate_metrics_included": (
                    extraction_completed
                    and case_error is None
                ),
                "case_pass": case_pass,
                "error": case_error,
                "jobs": predicted_jobs,
            }
        )

    # ------------------------------------------------------------
    # 5. AGGREGATE METRICS
    # ------------------------------------------------------------
    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0.0
    )
    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    print("\n" + "=" * 78)
    print("DISCOVERY EVAL SUMMARY")
    print("=" * 78)

    print(
        f"Case pass rate: "
        f"{percentage(case_passes, case_total)} "
        f"({case_passes}/{case_total})"
    )
    print(
        f"Case execution errors: "
        f"{case_execution_errors}"
    )
    print(
        f"Candidate-evaluable cases: "
        f"{candidate_evaluable_cases}/{case_total}"
    )

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
    print(
        "Location: MANUAL REVIEW "
        "(no exact-string metric)"
    )

    # ------------------------------------------------------------
    # 6. WRITE RESULTS
    # ------------------------------------------------------------
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        RESULTS_DIR / "latest_predictions.json"
    )

    output_path.write_text(
        json.dumps(
            {
                "eval_version": data.get("version"),
                "case_count": case_total,
                "summary": {
                    "case_passes": case_passes,
                    "case_total": case_total,
                    "case_pass_rate": (
                        case_passes / case_total
                        if case_total
                        else 0.0
                    ),
                    "case_execution_errors": (
                        case_execution_errors
                    ),
                    "candidate_evaluable_cases": (
                        candidate_evaluable_cases
                    ),
                    "classifier_correct": (
                        classifier_correct
                    ),
                    "classifier_total": classifier_total,
                    "classifier_accuracy": (
                        classifier_correct
                        / classifier_total
                        if classifier_total
                        else 0.0
                    ),
                    "candidate_tp": tp,
                    "candidate_fp": fp,
                    "candidate_fn": fn,
                    "candidate_precision": precision,
                    "candidate_recall": recall,
                    "candidate_f1": f1,
                    "title_correct": title_correct,
                    "company_correct": company_correct,
                    "matched_candidates": matched,
                    "provider_id_correct": (
                        provider_id_correct
                    ),
                    "provider_id_total": (
                        provider_id_total
                    ),
                },
                "cases": output_cases,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"\nPredictions written to: "
        f"{output_path.relative_to(REPO_ROOT)}"
    )
    print(
        "\nReminder: aggregate scores are only useful "
        "after checking individual failures, execution "
        "errors, and manual-review fields."
    )


if __name__ == "__main__":
    main()

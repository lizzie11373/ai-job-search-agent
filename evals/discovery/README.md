# Discovery Evaluation

This folder contains the reusable evaluation assets for Project 3's **Discovery layer**.

## Scope

This eval covers only:

```text
email metadata
→ job-related classifier
→ full email body
→ 0..N JobCandidates
```

It does **not** evaluate provider-page acquisition, JD verification, Web Search,
job-level deduplication, fit scoring, prioritization, persistence, or resume generation.

## Current v1 baseline

The current v1 set contains **8 sanitized real-world Gmail-derived cases**:

- 5 positive job-alert emails
  - 2 LinkedIn multi-job digests
  - 3 Indeed single-job rich-preview alerts
- 3 job-adjacent negative emails
  - career insights
  - profile/search notification
  - job-search webinar/advice

The positive cases contain **15 labeled concrete jobs** in total.

This is intentionally a small baseline. We are stopping expansion here for now
and moving to the next system layer instead of growing Discovery eval indefinitely.

## Files

- `cases_v1.json` — sanitized real-world eval cases plus human-labeled ground truth
- `run_eval.py` — reusable evaluation runner
- `README.md` — evaluation contract and methodology

Generated outputs are written to `results/`. They are run artifacts, not source-of-truth data.

## Automatically scored metrics

- Email classification accuracy
- Candidate precision
- Candidate recall
- Candidate F1
- Title exact-normalized accuracy
- Company exact-normalized accuracy
- Provider job-ID preservation when a stable ID is explicitly available

These dimensions have reasonably deterministic answers.

## Manual review

### Location groundedness

Location is **not** scored using exact string equality.

Examples of semantically acceptable variation include:

- `San Jose, CA` vs. `San Jose, California`
- `Bay Area` vs. `San Francisco Bay Area`
- `Dallas, TX` vs. `Dallas, TX (On-site)`

For each matched candidate, the runner prints the email reference and model output.
A human should judge:

> Is the extracted location supported by the email, without materially changing
> its meaning or adding unsupported specificity?

Use `PASS / FAIL / UNCLEAR`. Do not introduce an LLM judge for this in v1.

## Matching policy

When a provider exposes a stable job ID, use it as the strongest identity signal.

For LinkedIn, `/jobs/view/<job_id>/` is more meaningful than exact equality of a
long tracking URL.

When no stable provider ID is explicitly exposed, the eval falls back to normalized
`title + company` matching.

Full raw tracking-URL equality is a diagnostic only, not the primary correctness metric.

## How to run

From the repository root:

```bash
python evals/discovery/run_eval.py
```

or, if your environment uses Python 3 explicitly:

```bash
python3 evals/discovery/run_eval.py
```

The runner calls the project's current production functions:

```python
from job_agent.agents.email_classifier import is_job_related_email
from job_agent.agents.job_candidate_extractor import extract_job_candidates_from_email
```

So the same eval can be rerun after changing the model, prompt, or extraction architecture.

## How to add a future case

Do not add cases just to increase the sample count.

Add a sanitized case when it expands coverage or captures a meaningful real failure, such as:

- a new email template
- an ambiguous/noisy email
- a false positive or false negative
- a duplicate-link structure
- a missing-field case
- a real production failure worth preventing in the future

## Privacy

Only sanitized cases should be committed to a public repository.

Do not commit personal recipient addresses, private Gmail message IDs, raw authentication
or tracking tokens, full private email archives, or unnecessary personalization data.

If raw emails are ever kept locally, place them under:

```text
evals/private/
```

and keep that directory in `.gitignore`.

## Interpretation

This v1 baseline is useful for regression detection and failure analysis, but it is
not large enough to claim production-level accuracy. Always inspect individual failures
before reacting to aggregate scores.


## Recorded canonical run

`results/discovery_eval_v1_20261008T235717Z.json` records the 2026-10-08 run with matching frozen input SHA-256: classifier 8/8, candidate precision/recall 15/15, title 14/15, company 15/15, provider-ID 12/12. Location groundedness remains recorded as PENDING; no completed per-case judgments are inferred from aggregate scores.

The duplicated `latest_evaluation.json` was removed during cleanup; a new live run may regenerate ignored latest/timestamped files. The committed dated result is historical evidence, not production accuracy.

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

The current v1 set contains **9 cases: 8 sanitized real-world Gmail-derived cases and 1 synthetic regression fixture**:

- 5 positive job-alert emails
  - 2 LinkedIn multi-job digests
  - 3 Indeed single-job rich-preview alerts
- 3 job-adjacent negative emails
  - career insights
  - profile/search notification
  - job-search webinar/advice
- 1 job-related missing-company regression (`REG-01`): classify as relevant, but extract zero candidates because no employer is explicitly supported

The positive cases contain **15 labeled concrete jobs** in total.

This is intentionally a small regression set. `REG-01` was added to capture a real failure where an empty company stopped the Agent Run; it is a synthetic fixture, not a ninth real Gmail sample.

## Files

- `cases_v1.json` — nine current cases with expected classification and jobs
- `canonical_run.json` — paths and SHA-256 hashes binding the current cases to the curated saved result
- `results/discovery_eval_v1_9_cases.json` — byte-for-byte copy of the latest saved nine-case output
- `run_eval.py` — reusable evaluation runner
- `README.md` — evaluation contract and methodology

The runner writes generated output to ignored `results/latest_predictions.json`. The curated canonical copy is published separately so a later run cannot overwrite it. Exceptions are reported as case execution failures and excluded from candidate metrics; they are never treated as successful empty predictions. Case pass requires correct classification and candidate identity/count; title, company, provider ID, and manual location review are reported separately.

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


## Current canonical nine-case run

`results/discovery_eval_v1_9_cases.json` preserves the user-saved `latest_predictions.json` without changing predictions or scores. It records **9/9 case passes**, **9/9 correct classifications**, **0 execution errors**, candidate precision/recall **15/15** (0 false positives, 0 false negatives), title **15/15**, company **15/15**, and provider-ID preservation **12/12**. `REG-01` returned zero jobs as expected. Location groundedness still requires manual review; passing automated metrics does not establish it.

The original output does not contain an input hash or run timestamp. `canonical_run.json` records hashes when curating the saved output against the current input; it does not claim run-time provenance or invent a run timestamp. The offline checker independently recomputes all summary metrics from per-case predictions and current expected outputs. No new model run is required for that check.

Only the current nine-case Discovery result is selected for publication. The superseded eight-case result is kept locally under ignored results and is not included in the current version.

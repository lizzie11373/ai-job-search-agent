# JD acquisition: direct provider links to bounded search

## Product risk

A job-alert preview or provider page is not necessarily a complete JD. Accepting a login wall, incomplete preview, unrelated employer page, or stale page can contaminate every downstream requirement and fit judgment.

## Historical validation

The initial acquisition hypothesis was that an email-derived LinkedIn/Indeed URL could yield an analysis-ready JD through a cheap direct HTTP fetch. A live sanity check used four real provider leads. The preserved local result contains four `UNVERIFIED` outcomes and zero resolved postings.

This **0/4** observation supported changing the acquisition design for those samples and that fetch implementation. It was not a random sample, a permanent statement about those websites, or the entire application's success rate. The original private cases, tracking URLs, and diagnostic outputs remain local and are excluded from this repository.

The historical diagnostic assessed status/content type, redirects, visible text, and the then-current deterministic provider/official validators. Its role was to investigate why the original direct-fetch assumption failed, not to add a new benchmark or rescue cases with further search calls.

## Decision and current implementation

`job_agent/agents/job_resolution.py` now skips the provider URL for LinkedIn and Indeed and enters bounded Web Search. Other sources can try their source URL once and fall back to the same search pipeline.

The application makes one search operation, considers at most 30 ranked results, conservatively filters/deduplicates URLs, fetches at most 15 pages in batches of five, and combines structural validation with semantic lead-consistency and JD-completeness checks. It stops on the first adequate match. Search prefers employer/ATS pages, while acceptance is based on sufficient semantic consistency and complete content.

Normal misses are `UNVERIFIED`; technical search or verification failures remain retryable. Individual inaccessible pages can be skipped without losing other candidates.

## Reproducibility boundary

The original private sanity script calls `resolve_job_candidate()`. Running it against today's resolver executes the redesigned search path, so it would not reproduce the historical direct-fetch experiment. Preserve the original result and protocol; do not overwrite that evidence with a new run and call it the old experiment.

The public regression suite tests the current routing with controlled search/fetch/verifier fixtures. It establishes program behavior, not current availability of provider websites. The old validators and related manual checks have been archived locally with their import relationships preserved.

## Product learning

An acquisition assumption was tested before investing further in it; a small but decisive failure prompted a design change. The redesign makes cost and retry boundaries inspectable, but introduces dependence on search ranking, external availability, and semantic verification. Live coverage and held-out end-to-end evaluation remain future work.

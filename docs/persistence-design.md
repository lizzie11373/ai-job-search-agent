# Persistence and historical evidence

The local application uses SQLite to preserve candidate sources, evidence, opportunities, requirements, mappings, preferences, processed-email state, and product setup state. Database files are private runtime data and are never included in the public repository.

## Completed analyses are snapshots

`create_completed_job_opportunity_analysis()` writes an opportunity with its requirements and evidence mappings atomically. Existing opportunity IDs/posting URLs are not overwritten. Human decisions update decision state. A changed resume or preference profile does not silently rewrite a completed analysis.

Posting-URL dedupe is exact. It supports retries without creating duplicate persisted opportunities, but does not claim semantic identity across different URLs.

## Resume replacement is transactional

The new Markdown source is staged, extracted, and validated before it replaces the active resume. Failure preserves the previously active resume. Supporting sources accumulate; inactive resume evidence remains hydratable for historical mappings. Evidence deletion restrictions protect historical references.

## Fault isolation and processed-email state

Successfully analyzed opportunities are saved before the next candidate completes. A later candidate failure does not erase them. Technical failures keep an email retryable, while exact posting dedupe reuses already completed opportunity state. Processed-email keys include the Gmail account so switching accounts does not suppress another account's messages.

## Migration boundary

Local schema initialization adds required product state while preserving compatible historical rows. Legacy source-less evidence is not assigned fabricated provenance or silently deleted; managed resume/supporting sources determine the active future matching corpus once available.

Historical packaging notes described a copy-of-existing-database migration check and earlier test counts. Those describe past local validation, not a database distributed with this V1 repository. Current tests use temporary synthetic databases and cover replacement failure, inactive evidence hydration, create-only analysis persistence, dedupe, and partial failures.

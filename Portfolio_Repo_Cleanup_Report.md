# Portfolio V1 Cleanup Report

Date: 2026-10-13. Scope: repository cleanup and portfolio packaging; no new product features.

## Safety and privacy

A complete pre-cleanup snapshot was created and verified before edits. It includes the original environment and private files and remains local, outside this public repository. All 17,786 regular files were verified at baseline creation.

Personal candidate documents, the local database, API environment settings, OAuth credentials/token, raw provider cases/results, private pilot data, interview notes, and historical archives remain local and ignored. Fifteen private credentials/data/notes files were checked byte-for-byte against the baseline after cleanup; the private diagnostic's import paths were intentionally updated. Operating-system metadata is excluded from that data-preservation comparison.

The public candidate was scanned for exact configured secret values, key-like literals, private candidate addresses, tracking/signed URL parameters, personal absolute paths, and non-fixture email addresses. No unresolved hits were found. These checks complement an explicit public-file allowlist; they do not claim a perfect general-purpose secret detector.

## Deleted approved files

- `.DS_Store`
- `evals/.DS_Store`
- `evals/discovery/.DS_Store`
- `evals/discovery/results/latest_evaluation.json`
- `evals/evidence_extraction/.DS_Store`
- `evals/evidence_extraction/gold set/.DS_Store`
- `evals/matching_evaluation/.DS_Store`
- `evals/matching_evaluation/fixed_inputs/.DS_Store`
- `evals/requirement_extraction/.DS_Store`
- `evals/requirement_extraction/alignments/.DS_Store`
- `gitignore_snippet.txt`
- `job_agent/.DS_Store`
- `job_agent/services/.DS_Store`
- `test_job_resolution.py`

Approved generated cache directories were also removed (outside the retained `.venv`).

## Archived historical material

- `MIGRATION_NOTES.md` → local ignored history archive.
- `job_agent/agents/identity_narrower.py` → local ignored history archive.
- `job_agent/agents/job_identity_resolver.py` → local ignored history archive.
- `job_agent/agents/official_page_validator.py` → local ignored history archive.
- `job_agent/agents/official_search_filter.py` → local ignored history archive.
- `job_agent/agents/official_search_query_builder.py` → local ignored history archive.
- `job_agent/agents/provider_page_validator.py` → local ignored history archive.
- `main.py` → local ignored history archive.
- `test_fetched_page_validation.py` → local ignored history archive.
- `test_identity_narrowing.py` → local ignored history archive.
- `test_job_discovery.py` → local ignored history archive.
- `test_job_identity_resolver.py` → local ignored history archive.
- `test_live_job_search.py` → local ignored history archive.
- `test_official_page_fetch.py` → local ignored history archive.
- `test_official_search_filter.py` → local ignored history archive.
- `test_official_search_input.py` → local ignored history archive.
- `test_official_search_queries.py` → local ignored history archive.
- `test_qwen_web_search_raw_response.py` → local ignored history archive.
- `test_real_job_resolution.py` → local ignored history archive.
- `test_real_structured_job_metadata.py` → local ignored history archive.
- `test_resolution_precision_policy.py` → local ignored history archive.
- `test_web_search.py` → local ignored history archive.

The six old official/provider/identity modules and their related manual checks were archived as a group, rather than deleted merely because production did not import them. Private provider diagnostics now import the historical validators from the local archive. Original pre-cleanup bytes remain recoverable in the baseline.

## Moved and renamed

- `evals/evidence_extraction/gold set/gold_draft_v2_deeplearning.json` → `evals/evidence_extraction/gold_set/gold_v2_deeplearning.json`
- `evals/evidence_extraction/gold set/gold_draft_v2_deeplearning.md` → `evals/evidence_extraction/gold_set/gold_v2_deeplearning.md`
- `evals/evidence_extraction/gold set/gold_draft_v2_rag.json` → `evals/evidence_extraction/gold_set/gold_v2_rag.json`
- `evals/evidence_extraction/gold set/gold_draft_v2_rag.md` → `evals/evidence_extraction/gold_set/gold_v2_rag.md`
- `evals/evidence_extraction/gold set/gold_draft_v2_resume.json` → `evals/evidence_extraction/gold_set/gold_v2_resume.json`
- `evals/evidence_extraction/gold set/gold_draft_v2_resume.md` → `evals/evidence_extraction/gold_set/gold_v2_resume.md`
- `evals/evidence_extraction/gold set/job_agent_evidence_gold_v2.json` → `evals/evidence_extraction/gold_set/job_agent_evidence_gold_v2.json`
- `evals/evidence_extraction/gold set/job_agent_evidence_gold_v2_policy.md` → `evals/evidence_extraction/gold_set/job_agent_evidence_gold_v2_policy.md`
- `evals/evidence_extraction/gold set/job_agent_evidence_gold_v2_review.md` → `evals/evidence_extraction/gold_set/job_agent_evidence_gold_v2_review.md`
- `run_candidate_profile_ingestion.py` → `scripts/run_candidate_profile_ingestion.py`
- `run_candidate_upload.py` → `scripts/run_candidate_upload.py`
- `test_resolution_outcome_logging.py` → `tests/test_resolution_outcome_logging.py`
- `test_resolved_job_posting.py` → `tests/test_resolved_job_posting.py`
- `test_search_url_boundary.py` → `tests/test_search_url_boundary.py`
- `test_structured_job_metadata.py` → `tests/test_structured_job_metadata.py`
- `evals/evidence_extraction/alignments/alignment_draft_job_agent.json` → `evals/evidence_extraction/alignments/alignment_job_agent.json`
- `evals/evidence_extraction/alignments/alignment_draft_job_agent.md` → `evals/evidence_extraction/alignments/alignment_job_agent.md`
- `evals/evidence_extraction/alignments/alignment_draft_rag.json` → `evals/evidence_extraction/alignments/alignment_rag.json`
- `evals/evidence_extraction/alignments/alignment_draft_rag.md` → `evals/evidence_extraction/alignments/alignment_rag.md`
- `evals/evidence_extraction/alignments/deeplearning_alignment_draft.json` → `evals/evidence_extraction/alignments/deeplearning_alignment.json`
- `evals/evidence_extraction/alignments/deeplearning_alignment_draft.md` → `evals/evidence_extraction/alignments/deeplearning_alignment.md`
- `evals/evidence_extraction/alignments/resume_alignment_draft.json` → `evals/evidence_extraction/alignments/resume_alignment.json`
- `evals/evidence_extraction/alignments/resume_alignment_draft.md` → `evals/evidence_extraction/alignments/resume_alignment.md`

Reviewed evidence-extraction annotations no longer have misleading draft filenames/status values. The author confirmed completed human review. Status metadata and references were updated; semantic evidence, Gold labels, IDs, source text and prediction values were preserved. Historical schema keys containing `draft` remain for compatibility and are documented.

## Documentation and public evaluation package

- Rewrote the product-oriented README: problem/value, V1 boundary, end-to-end workflow, orchestration, each semantic layer, deterministic policy, durability, evaluations, limitations, next steps, and local setup.
- Added sanitized JD acquisition decision and persistence/migration design documents.
- Documented the historical 0/4 provider-fetch validation without publishing original private cases or claiming global/production accuracy.
- Reconciled closed matching evaluation state with future-work claims.
- Corrected component documentation paths, annotation states, the requirement manifest status, and matcher runner input/output defaults.
- Preserved frozen input and matching Gold bytes; retained paired JSON/Markdown evidence and selected five canonical result files. New runs remain ignored and do not overwrite canonical matching outputs by default.
- Added a blank `.env.example` and pinned direct dependency versions to the locally verified environment.
- No screenshots existed in the source export; none were fabricated.

## Verification

- Baseline suite: 46 passed. Final suite: **55 passed**; four useful manual checks were migrated into isolated collected tests. Parameterized URL cases account for part of the count increase.
- Python AST/JSON parsing and legacy-import checks passed for prepared public files.
- Offline artifact verification passed: discovery source hash; all eight requirement hashes and runner/source text consistency; matching counts/IDs, recorded input hashes, and linked evidence IDs.
- Recomputed final matching exact support accuracy: baseline 20/32, PromptFix1 20/32. Macro F1: 0.539 and 0.441. This does not establish aggregate improvement.
- CLI help/import smoke passed for the corrected matcher and candidate-ingestion helper.
- Streamlit onboarding/startup smoke completed without exceptions, credentials, or provider calls.
- Public ignore rules were verified to exclude real data/secrets/history/caches while retaining formal source, synthetic fixtures, `.env.example`, and canonical result files.
- No live Gmail/search/LLM evaluation or fresh dependency installation was run during cleanup. Current source behavior tests and historical result integrity are distinct forms of evidence.

## Known limitations

- The exact historical expanded Job Agent source README declared by the evidence Gold is absent. The supplied pre-cleanup snapshot has a different hash and contains 49/50 quoted Gold strings verbatim; E_JOB_048 is absent. This is a provenance limitation, not evidence of incomplete human review.
- Older extraction alignments refer to an earlier source/20-unit Gold; the expanded 50-unit Gold feeds the fixed matching corpus. These versions are not conflated.
- Discovery location review remains pending in the recorded result; no per-case judgments were invented.
- Model quality results are small curated offline behavioral results. No production accuracy, end-to-end user-value claim, or positive verifier aggregate lift is made.
- Live provider access and Google OAuth consent configuration remain user-specific. The public repo contains no initialized personal database or credentials.
- Local single-user V1 has no cloud deployment, autonomous application submission, resume tailoring, multi-model bakeoff, or production operations layer.

## Git publication boundary

Only the reviewed public allowlist is included in the portfolio commit. Local private files and backups are not part of Git history. GitHub account/name/visibility are confirmed separately before remote creation and push; repository tags and commit history identify the published V1 snapshot.

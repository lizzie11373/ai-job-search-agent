# AI Job Search Agent — Candidate Evidence Extraction Alignment

**Review status:** HUMAN_REVIEWED (author-confirmed for Portfolio V1; historical analysis preserved).

Gold units: **20**  
Agent predictions: **7**  
Verbatim source-text check: **4/7 (57.1%)**

## Gold → Agent alignment

| Gold | Agent | Label | AI PM interpretation |
|---|---|---|---|
| G001 | — | MISSING | The extractor missed the core end-to-end product capability stated in the opening description. |
| G002 | E002 | MATCH | The V1 human-review product boundary is captured. |
| G003 | — | MISSING | The high-level service-boundary architecture was not extracted. |
| G004 | — | MISSING | run_agent() orchestration across the full workflow was not extracted. |
| G005 | E003 | PARTIAL_MATCH | Built-in GmailEmailSource is captured, but compatibility/test inputs are not. |
| G006 | — | MISSING | Historical-snapshot and rerun semantics were not extracted. |
| G007 | — | MISSING | Safe resume replacement semantics were not extracted. |
| G008 | — | MISSING | Active-source / historical-evidence / durable-ID semantics were not extracted. |
| G009 | — | MISSING | Onboarding commit semantics were not extracted. |
| G010 | — | MISSING | Preference snapshot semantics were not extracted. |
| G011 | — | MISSING | The Requirement → Support → Evidence trace contract was not extracted. |
| G012 | — | MISSING | Database migration and evidence-protection behavior were not extracted. |
| G013 | E004 | PARTIAL_MATCH | The 40-test result is captured, but migration-preservation testing is omitted. |
| G014 | E007 | PARTIAL_MATCH | Streamlit implementation is captured, but the substantive UI/service architecture and product behaviors are omitted. |
| G015 | — | MISSING | Read-only OAuth, local token privacy, and refresh/recovery behavior were not extracted. |
| G016 | — | MISSING | Safe Gmail account switching was not extracted. |
| G017 | — | MISSING | Account-scoped processed-email dedupe was not extracted. |
| G018 | — | MISSING | Metadata-first Gmail ingestion was not extracted. |
| G019 | — | MISSING | Authorization recovery / Run Agent disable behavior was not extracted. |
| G020 | — | MISSING | Provider-neutral EmailSource.account_key() contract was not extracted. |

## Agent-only predictions

- **E001 — EXTRA_OUT_OF_SCOPE:** Packaging provenance ('integrated update built from uploaded zip') is not candidate capability evidence.
- **E005 — EXTRA_OUT_OF_SCOPE:** Packaging-environment limitation about live tests is not a candidate capability.
- **E006 — EXTRA_OUT_OF_SCOPE:** Python 3.11+ runtime requirement is environment metadata, not candidate evidence.

## Main failure patterns

1. **Severe recall problem on long product/architecture documents.** The extractor found only a small set of simple declarative facts and missed most state, architecture, privacy, recovery, and ingestion-design evidence.
2. **Selection is biased toward easy metadata.** Packaging provenance, Python-version requirements, and packaging-environment limitations were extracted even though they are weak downstream candidate evidence.
3. **The few extracted substantive facts are mostly grounded.** This is primarily a relevance/coverage problem rather than a hallucination problem.
4. **This document is a strong stress case for the extractor.** It contains many high-value product-engineering decisions embedded in prose rather than resume-style bullets, so it reveals whether the extractor can identify reusable capabilities rather than only obvious facts.

## Product implication

If Candidate Evidence feeds requirement matching, this failure pattern can create false gaps: the candidate actually has evidence for architecture, data integrity, OAuth/privacy, failure recovery, and state-management requirements, but downstream matching never sees it because extraction omitted it.
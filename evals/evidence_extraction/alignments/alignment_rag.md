# RAG Project — Candidate Evidence Extraction Alignment

**Review status:** HUMAN_REVIEWED (author-confirmed for Portfolio V1; historical analysis preserved).

Gold units: **21**  
Agent predictions: **21**  
Verbatim source-text check: **8/21 (38.1%)**

## Gold → Agent alignment

| Gold | Agent | Label | AI PM interpretation |
|---|---|---|---|
| G001 | E001 | MATCH | Product purpose is captured directly. |
| G002 | E004 | MATCH | Core ingestion/embedding/ChromaDB capability is captured. |
| G003 | E005 | MATCH | Basic RAG workflow is captured. |
| G004 | E006 | MATCH | Agentic workflow is captured at the intended capability level. |
| G005 | E007 | MATCH | Adaptive routing behavior is captured. |
| G006 | E008 | PARTIAL_MATCH | Intent categories are extracted, but the key design decision—classify user task rather than fixed role—is not fully captured. |
| G007 | E009 | MATCH | Conversation-aware rewriting and reference resolution are captured. |
| G008 | E010, E006 | PARTIAL_MATCH | Query-count and dedup behavior are partly present, but the source-file + chunk-index dedup key is omitted. |
| G009 | E011 | MATCH | Retrieval metadata retention is captured. |
| G010 | E012 | MATCH | Dedicated global Qwen reranking and top-8 selection are captured. |
| G011 | E013 | MATCH | Recall-preserving full-candidate fallback is captured. |
| G012 | E015 | MATCH | Provider-interface abstraction is captured. |
| G013 | — | MISSING | Structured output validation and rule-based fallback were not extracted. |
| G014 | E016 | MATCH | Advanced controls and user-friendly evidence-coverage controls are captured. |
| G015 | — | MISSING | Detailed retrieval/rerank transparency exposed in the UI was not extracted. |
| G016 | E017 | MATCH | Nine-question offline runner and three modes are captured. |
| G017 | E018 | PARTIAL_MATCH_WITH_OVERCLAIM | Verification/validation distinction is captured, but the prediction also adds a rubric claim that is not supported by its cited source_text. |
| G018 | — | MISSING | Automatic + manual semantic evidence-quality review dimensions were not extracted. |
| G019 | — | MISSING | Rerank/fallback evaluation fields and coverage metrics were not extracted. |
| G020 | E018 | PARTIAL_MATCH_WITH_OVERCLAIM | The prediction gestures at structured human-review rubrics, but does not capture the answer-quality dimensions or product-validation boundary and cites insufficient source_text. |
| G021 | — | MISSING | Model/run traceability was not extracted. |

## Agent-only predictions

- **E002 — EXTRA_REDUNDANT:** Use-case examples are grounded but duplicate the broader product-purpose evidence.
- **E003 — EXTRA_BUNDLED_SUMMARY:** Large capability bundle is grounded, but it violates the atomic-evidence policy and duplicates detailed units.
- **E014 — EXTRA_LOW_VALUE_CONFIGURATION:** Model/version configuration is grounded but is less useful than the provider-abstraction implementation for downstream matching.
- **E019 — EXTRA_OUT_OF_SCOPE:** Repository file structure is document metadata, not candidate capability evidence.
- **E020 — EXTRA_REDUNDANT:** Generic technology-stack list is grounded but duplicates stronger implementation evidence.
- **E021 — EXTRA_SELF_POSITIONING:** A broad 'this demonstrates the ability to...' summary is excluded when detailed implementation evidence exists.

## Main failure patterns

1. **Good coverage of the main technical path.** Basic RAG, Agentic RAG, Adaptive routing, multi-query retrieval, reranking, fallback, and provider abstraction are mostly found.
2. **Recall drops on evaluation and observability details.** Structured output validation, manual evidence-quality review, rerank/fallback evaluation, answer-quality rubrics, UI transparency, and run traceability are under-extracted.
3. **The extractor sometimes prefers broad summaries over atomic evidence.** E003 and E021 are examples: they are grounded, but too bundled or self-positioning for a clean Candidate Evidence Base.
4. **Source-text grounding is a separate problem from semantic correctness.** Several claims are broadly true but their cited `source_text` is not verbatim; E018 also adds a rubric assertion not supported by the cited excerpt.

## Why we are not freezing a final score yet

This document contains `PARTIAL_MATCH`, bundled evidence, and one prediction with an overclaim/source-attribution issue. We should first approve the Gold units and the scoring rule for partial matches before turning this into final precision/recall/F1.
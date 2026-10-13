# Job Agent Evidence Gold v2 — Annotation Policy

## Scope

This Gold set covers only `README_AI_Job_Search_Agent_COMPLETE.md`.

It replaces the previous Job Agent evidence slice. It does not modify the Resume, Deep Learning, or Adaptive RAG Gold evidence.

## Dual use

The same frozen evidence units are used in two different ways:

### Evidence Extractor Evaluation
The README is the input document. Extractor predictions are aligned to this Gold to evaluate:
- Coverage / Recall
- Selection / Precision
- Semantic Correctness
- Granularity / Atomicity
- Grounding / Source Attribution
- Duplication / Redundancy

### Requirement–Evidence Matching Evaluation
The frozen Gold evidence units are passed directly to the matcher together with fixed Gold requirements. Upstream extraction is not rerun, so matching errors can be isolated from evidence-extraction errors.

## Inclusion rule

Annotate a fact when it materially demonstrates product, AI, engineering, evaluation, reliability, integration, architecture, or implementation capability that could reasonably matter in candidate/job matching.

Do not annotate every setup command, environment variable, UI sorting detail, or incidental implementation fact.

## Limitation evidence

Explicit limitations can be valid Gold evidence when they prevent downstream overclaiming. For example, a source statement that the project is not a cloud production deployment is useful evidence for requirements involving production deployment or production observability.

## Grounding

Every Gold claim must be directly supported by the cited exact source text. No external knowledge or unstated project facts may be added.

## Freeze rule

Human review is complete, as confirmed by the author during Portfolio V1 packaging. Keep evidence IDs stable for matcher evaluation.

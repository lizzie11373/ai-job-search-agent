# Candidate Evidence Extraction evaluation

This controlled component benchmark measures `document -> extract_evidence_from_document() -> EvidenceUnit[]`. It excludes the production Evidence Validator, Gmail, Web Search, matching, persistence, and UI.

## Inputs, annotations, and results

- `inputs/`: synthetic new-grad resume and three frozen project READMEs. Historical filenames are preserved because source-document names are part of annotation/prediction provenance.
- `gold_set/`: reviewed resume, Deep Learning, RAG Gold, and the expanded Job Agent evidence Gold/policy.
- `alignments/`: reviewed human alignment evidence for the original extraction run.
- `results/evidence_extraction_baseline.json`: canonical historical prediction export.
- `source_snapshots/README_before_portfolio_cleanup.md`: the project's README as supplied for this cleanup, captured before documentation changes.

Legacy `draft` filename/status markers were normalized after the author confirmed human review completion. Evidence IDs, claims, quotes, annotation labels, and source-version distinctions were preserved.

## Evaluation contract

The runner checks nonempty claims/quotes/sections/types and verbatim quote inclusion. These are deterministic contract checks, not semantic precision or recall.

Human alignment assesses coverage/recall, selection/precision, semantic correctness, atomicity/granularity, grounding/source attribution, and redundancy. Historical predictions record 56/72 verbatim quotes (77.78%). A non-verbatim quote is not automatically an unsupported claim; semantic grounding requires separate review.

The original Job Agent alignment shows significant recall loss for architecture, evaluation, state, and privacy decisions embedded in long prose. This can create downstream false gaps even when matching behaves correctly on the evidence it receives.

## Source-version boundary

The older Job Agent alignment uses 20 Gold units from the earlier source; the expanded Job Agent Gold contains 50 units and supplies the Job Agent slice of the 120-unit matching corpus. They are different source/annotation versions.

The expanded Gold declares source `README_AI_Job_Search_Agent_COMPLETE.md` with SHA-256 `99bde3d040545d812233b7955d3783ca3275d1b06e655a4c9dd0a8ca7ea4f8fc`. That exact source file is absent from this export. The supplied pre-cleanup snapshot has SHA-256 `8c93789571b642c36bdfc34145f12443504eec73fdaf11dc15d553177864e375`; 49 of the expanded Gold's 50 quoted strings appear verbatim in it, while E_JOB_048 does not. This is documented rather than relabeled as an exact reconstruction.

The frozen matching inputs remain independently loadable. Reproducing expanded source-level extraction/quote fidelity would require the original matching source snapshot or a separately versioned benchmark. Do not silently use the new public README as the historical input.

## Run

From the root, configure the same provider settings as the app:

```bash
python evals/evidence_extraction/run_eval.py
```

The runner reads only `inputs/`, calls the current production extractor once per document, and writes ignored `results/latest_predictions.json`. It does not load Gold. Preserve the canonical baseline; a new run is a current-model prediction, not a reproduction guaranteed to equal the historical export.

# Public evaluation evidence

Four component evaluations help distinguish acquisition, extraction, and matching errors. All are small curated behavioral/regression sets; no result is a production accuracy estimate.

| Folder | Scope | Canonical evidence |
|---|---|---|
| [discovery](discovery/README.md) | Metadata classification and 0..N email lead extraction | Nine cases (eight sanitized Gmail-derived + one synthetic regression), runner, current canonical result |
| [evidence_extraction](evidence_extraction/README.md) | Document-to-evidence extractor, without separate validator | Four sources, reviewed Gold/alignments, historical prediction baseline |
| [requirement_extraction](requirement_extraction/README.md) | JD-to-requirement extractor, without separate validator | Eight sources, mixed v2/v3 reviewed Gold/alignments, baseline predictions |
| [matching_evaluation](matching_evaluation/README.md) | Fixed-input production matching/verifier/reconciliation | 120 evidence units, 32 requirements, 32 Gold records, two recorded runs |

## Annotation state and historical names

The author confirmed that Gold and alignment materials bearing legacy `draft` names/status values had completed human review. Portfolio packaging normalizes those evidence-extraction filenames and status metadata, with path references updated. Semantic labels, IDs, quoted sources, and historical predictions are unchanged. Some historical schema field names retain `draft` for compatibility; this does not indicate pending review.

Older evidence-extraction alignments describe the smaller original Job Agent README and its 20-unit annotation set. The expanded 50-unit Job Agent Gold is a different source version used in the frozen matching corpus; do not score the old extraction run against that expanded Gold and call it the same benchmark.

The expanded Gold declares a historical source filename/hash that is absent from this export. A pre-cleanup README snapshot supplies context but has a different hash; it is not substituted for the missing exact source. Human review completion and exact-source provenance are separate questions. [Provenance details](evidence_extraction/README.md).

## Canonical results versus new runs

Five canonical result files are selected for publication: the current nine-case discovery evaluation, evidence and requirement extraction baselines, and matching baseline/PromptFix1. The superseded eight-case discovery result is excluded from the current version. New generated outputs remain ignored. Re-running a semantic eval invokes the current provider/model/prompt, so it can vary and should not overwrite historical canonical evidence.

```bash
python evals/verify_artifacts.py
```

This offline command checks JSON contracts, frozen case/input hashes, unique IDs, recomputed nine-case discovery metrics against the current canonical result, and recorded matching metrics. It does not call Gmail, search, or an LLM, and is not a new semantic evaluation.

Raw Gmail cases, credentials, real candidate documents, original private provider diagnostics, and interview-preparation notes remain local. A sanitized summary of the acquisition experiment is in [the architecture decision](../docs/jd-resolution-decision.md).

# Job Requirement Extraction evaluation

Eight frozen curated JDs test `JD -> production requirement extractor -> JobRequirement[]`. The separate requirement validator, matching, scoring, Gmail/search, and persistence are excluded.

Cases cover clean baseline extraction, compound atomicity, strength wording, alternatives/equivalency, noise/negation, repetition/deduplication, license/certification/domain, and long-form FDE prose. All eight file hashes are recorded in `manifest.json`.

## Artifacts and reviewed results

- `cases/` and `cases_v1.json`: frozen input text and runner payload.
- `gold_set/` and `alignments/`: human-reviewed annotations. REQ001 uses v2, REQ002–REQ008 use v3; the benchmark is not mislabeled as eight uniformly v3 exports.
- `results/requirement_extraction_baseline.json`: canonical historical raw extractor output, 102 predictions.

Reviewed alignment summaries report 109 Gold requirements, 106/109 covered concepts, 99.0% prediction validity precision, 97.2% semantic recall, 98.1% semantic F1, 100% requirement-level accuracy, 96.0% category accuracy, and 102/102 grounding/exact quote fidelity. These are curated offline reviewed results, not production performance estimates.

Semantic coverage is scored separately from structure. One prediction can cover several Gold concepts yet be bundled; splitting an OR condition into independent requirements can distort downstream fit arithmetic. Important findings include bundled requirements, OR/substitution errors, long-prose misses, category boundaries, and deduplication.

## Contract

Fields: `requirement`, `category`, `requirement_level`, `jd_source_text`, `jd_section`. Categories include RESPONSIBILITY, EXPERIENCE, SKILL, DOMAIN_KNOWLEDGE, EDUCATION, LICENSE, CERTIFICATION, OTHER; strengths are CORE, REQUIRED, PREFERRED.

Contract checks (allowed categories, quote inclusion, nonempty fields) are not replacements for human semantic alignment. Preserve reviewed inputs/IDs; version new annotation policies or source changes separately.

## Run

With provider settings configured, run from the repository root:

```bash
python evals/requirement_extraction/run_eval.py
```

The runner calls the current extractor and writes ignored `results/latest_predictions.json`. It reads `cases_v1.json`, not the Gold files, and leaves the committed baseline intact. Live runs incur provider usage and can differ from the historical output.

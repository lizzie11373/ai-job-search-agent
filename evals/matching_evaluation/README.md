# Requirement–Evidence Matching v2

This closed Portfolio V1 evaluation fixes both upstream inputs to isolate the production matcher, negative verifier, and reconciliation. It does not rerun extractors, Gmail, JD resolution, or scoring, and the runner does not read Gold output labels.

## Frozen artifacts

- `fixed_inputs/01_input_fixed_candidate_evidence_v2.json`: 120 units — synthetic resume 37, Deep Learning 12, Adaptive RAG 21, Job Agent 50.
- `fixed_inputs/02_input_representative_requirements_v2.json`: 32 selected atomic requirements.
- `gold_set/03_gold_output_human_adjudicated_mappings_v2.json`: 32 human-reviewed reference mappings.
- Paired Markdown files support human inspection; they are not redundant scratch files.
- `alignment/Requirement_Evidence_Matching_Alignment_Report_v2.md`: historical adjudication, failure analysis, and closure decision.

## Recorded results

| Run | Final exact support accuracy | Recomputed macro F1 |
|---|---:|---:|
| Baseline | 20/32 (62.5%) | 0.539 |
| PromptFix1 | 20/32 (62.5%) | 0.441 |

Macro F1 is the unweighted mean over STRONG, PARTIAL, WEAK, NOT_CLEARLY_SUPPORTED. Values are recomputed from each run's final mappings against the frozen Gold. First-pass matcher labels varied; the observed target-case correction (MREQ029 clinical domain) does not demonstrate aggregate improvement or positive incremental verifier lift. Strong-support inflation through loss of material qualifiers remains a key failure pattern.

New benchmark content or annotation policy should receive a new version. These 32 curated requirements are not representative production accuracy evidence. Exact historical source provenance for the expanded Job Agent evidence slice has a documented limitation in [the evidence evaluation README](../evidence_extraction/README.md); fixed matcher inputs are unchanged and loadable.

## Run and verify

Offline integrity/metric check:

```bash
python evals/verify_artifacts.py
```

Live current-pipeline run, with configured model credentials:

```bash
python evals/matching_evaluation/run_matcher.py
```

Defaults resolve frozen inputs relative to the runner and write ignored `results/local_run.json`. Explicit `--evidence`, `--requirements`, and `--output` overrides are available. Neither committed canonical prediction file is overwritten by default.

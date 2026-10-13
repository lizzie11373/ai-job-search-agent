# REQ008 Alignment v3

**Status:** FINAL_ALIGNMENT_V3

## Metrics

- Gold requirements: **19**
- Agent predictions: **17**
- Gold concepts covered: **18/19**
- Prediction validity precision: **100.0%**
- Semantic Gold coverage recall: **94.7%**
- Semantic F1: **97.3%**
- Requirement-level accuracy: **100.0%**
- Category accuracy: **82.4%**
- Grounding pass: **17/17**
- Exact source fidelity: **17/17**
- Bundled predictions: **2**
- Over-split logical clusters: **1**
- Duplicate/invalid extras: **0**

## Missing Gold

- **G003:** Turn customer problem context into working AI-enabled solutions.

## Structural / logic findings

- R001 omits the independently matchable responsibility to turn customer context into working AI-enabled solutions (G003).
- R014-R016 split one PREFERRED OR-cluster into three independent preferred requirements, which can distort downstream scoring.

## Prediction alignment

- **R001 → G001, G002** — semantic `COVERS_MULTIPLE_GOLD`, level `CORRECT`, category `CORRECT`, structure `BUNDLED`, grounding `PASS`.
- **R002 → G004, G005, G006** — semantic `COVERS_MULTIPLE_GOLD`, level `CORRECT`, category `CORRECT`, structure `BUNDLED`, grounding `PASS`.
- **R003 → G007** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R004 → G008** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R005 → G009** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R006 → G010** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R007 → G011** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R008 → G012** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R009 → G013** — semantic `MATCH`, level `CORRECT`, category `MISMATCH`, structure `PASS`, grounding `PASS`.
- **R010 → G014** — semantic `MATCH`, level `CORRECT`, category `MISMATCH`, structure `PASS`, grounding `PASS`.
- **R011 → G015** — semantic `MATCH`, level `CORRECT`, category `MISMATCH`, structure `PASS`, grounding `PASS`.
- **R012 → G016** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R013 → G017** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R014 → G018** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `OVER_SPLIT_OR_CLUSTER`, grounding `PASS`.
- **R015 → G018** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `OVER_SPLIT_OR_CLUSTER`, grounding `PASS`.
- **R016 → G018** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `OVER_SPLIT_OR_CLUSTER`, grounding `PASS`.
- **R017 → G019** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
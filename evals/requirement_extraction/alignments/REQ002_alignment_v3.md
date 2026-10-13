# REQ002 Alignment v3

**Status:** FINAL_ALIGNMENT_V3

## Metrics

- Gold requirements: **21**
- Agent predictions: **17**
- Gold concepts covered: **21/21**
- Prediction validity precision: **100.0%**
- Semantic Gold coverage recall: **100.0%**
- Semantic F1: **100.0%**
- Requirement-level accuracy: **100.0%**
- Category accuracy: **94.1%**
- Grounding pass: **17/17**
- Exact source fidelity: **17/17**
- Bundled predictions: **3**
- Over-split logical clusters: **0**
- Duplicate/invalid extras: **0**

## Missing Gold

- None.

## Structural / logic findings

- R001, R002, and R004 are semantically grounded but bundle independently matchable requirements.

## Prediction alignment

- **R001 → G001, G002** — semantic `COVERS_MULTIPLE_GOLD`, level `CORRECT`, category `CORRECT`, structure `BUNDLED`, grounding `PASS`.
- **R002 → G003, G004** — semantic `COVERS_MULTIPLE_GOLD`, level `CORRECT`, category `CORRECT`, structure `BUNDLED`, grounding `PASS`.
- **R003 → G005** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R004 → G006, G007, G008** — semantic `COVERS_MULTIPLE_GOLD`, level `CORRECT`, category `CORRECT`, structure `BUNDLED`, grounding `PASS`.
- **R005 → G009** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R006 → G010** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R007 → G011** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R008 → G012** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R009 → G013** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R010 → G014** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R011 → G015** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R012 → G016** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R013 → G017** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R014 → G018** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R015 → G019** — semantic `MATCH`, level `CORRECT`, category `MISMATCH`, structure `PASS`, grounding `PASS`.
- **R016 → G020** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R017 → G021** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
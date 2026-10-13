# REQ006 Alignment v3

**Status:** FINAL_ALIGNMENT_V3

## Metrics

- Gold requirements: **12**
- Agent predictions: **13**
- Gold concepts covered: **12/12**
- Prediction validity precision: **92.3%**
- Semantic Gold coverage recall: **100.0%**
- Semantic F1: **96.0%**
- Requirement-level accuracy: **100.0%**
- Category accuracy: **100.0%**
- Grounding pass: **13/13**
- Exact source fidelity: **13/13**
- Bundled predictions: **0**
- Over-split logical clusters: **0**
- Duplicate/invalid extras: **1**

## Missing Gold

- None.

## Structural / logic findings

- R012 repeats cross-functional communication as PREFERRED even though the same qualification is already REQUIRED; keeping both can double-count and weaken semantic deduplication.

## Prediction alignment

- **R001 → G001** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R002 → G002** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R003 → G003** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R004 → G004** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R005 → G005** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R006 → G006** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R007 → G007** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R008 → G008** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R009 → G009** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R010 → G010** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R011 → G011** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
- **R012 → —** — semantic `EXTRA_DUPLICATE_WEAKER_RESTATEMENT`, level `NOT_SCORED_EXTRA`, category `NOT_SCORED_EXTRA`, structure `DUPLICATE`, grounding `PASS`.
- **R013 → G012** — semantic `MATCH`, level `CORRECT`, category `CORRECT`, structure `PASS`, grounding `PASS`.
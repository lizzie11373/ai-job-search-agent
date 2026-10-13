# Resume Evidence Extraction — Provisional Alignment

**Review status:** HUMAN_REVIEWED (author-confirmed for Portfolio V1; historical analysis preserved).

## Provisional metrics

- Gold units: **37**
- Agent predictions: **36**
- Semantic matches: **32**
- Missing Gold units: **5**
- Extra/out-of-scope or redundant Agent units: **4**
- Precision: **88.9%**
- Recall: **86.5%**
- F1: **87.7%**
- Verbatim source-text rate: **100% (36/36)**

## Missing Gold units

- **G002** — graduate coursework.
- **G034** — Product skills list.
- **G035** — AI / Data skills list.
- **G036** — Design / Collaboration skills list.
- **G037** — Tools list.

## Agent-only units

- **E001 — EXTRA_OUT_OF_SCOPE:** identity/location header.
- **E002 — EXTRA_OUT_OF_SCOPE:** synthetic-evaluation metadata.
- **E003 — EXTRA_REDUNDANT:** broad summary claim duplicated by detailed experience.
- **E004 — EXTRA_REDUNDANT:** broad summary claim duplicated by detailed experience/skills.

## Product interpretation

The strongest failure pattern is **recall on compact list-style evidence**: coursework and the Skills section were skipped even though these facts can matter to downstream job-requirement matching. The extra predictions are grounded, so this is not primarily a hallucination problem; it is a **scope/selection precision** problem.
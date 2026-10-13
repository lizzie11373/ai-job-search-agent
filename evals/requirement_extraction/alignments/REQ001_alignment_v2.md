# REQ001 Alignment v2

**Status:** FINAL_ALIGNMENT_V2

**Gold Policy:** v2

## Summary

- Gold requirements: **14**
- Agent predictions: **13**
- Semantic matches: **13**
- Missing Gold requirements: **1**
- Agent-only extras: **0**
- Semantic precision: **100.0%**
- Semantic recall: **92.9%**
- Semantic F1: **96.3%**
- Requirement-level accuracy on matched items: **100%**
- Category accuracy on matched items: **100%**
- Grounding pass on predictions: **13/13**
- Exact source fidelity on predictions: **13/13**
- Atomicity errors: **0 observed**
- Duplicate / noise / negation errors: **0 observed**

## Key revision from the previous alignment

The previous draft treated G012 and G013 as category mismatches because the old Gold policy mechanically mapped `Experience with X` to `EXPERIENCE`.

After human adjudication, Policy v2 now classifies by semantic intent:

- `EXPERIENCE` = prior doing / work history / execution
- `SKILL` = practical ability / proficiency / capability
- `DOMAIN_KNOWLEDGE` = understanding / familiarity with a domain

Therefore:

- G012 `Experience with vector databases` → `SKILL`
- G013 `Experience with prompt evaluation or LLM evaluation frameworks` → `SKILL`

The Agent's original categories for these two items are therefore considered correct under v2.

## Final case finding

REQ001 is a strong clean-baseline result. The only observed semantic failure is one recall miss from the `About the Role` section. The Agent preserved requirement strength, category semantics, logical structure, grounding, and precision for all extracted items.

# Requirement–Evidence Matching Evaluation
## Human Alignment Report and Evaluation Closure

> **Purpose**  
> This document records the completed human alignment for the **Requirement–Evidence Matching** component of the AI Job Search Agent.  
> It captures the frozen benchmark design, human-adjudicated Gold, production matcher results, the Negative Verifier failure discovered during evaluation, the targeted prompt fix, and the final decision to close this evaluation cycle rather than continue into repeated-run tuning.

---

# 1. Component under evaluation

The matching component answers a requirement-level question:

```text
one validated JobRequirement
+
complete validated CandidateEvidenceBase
        ↓
Requirement–Evidence Matching
        ↓
one RequirementEvidenceMapping
```

The semantic output contains:

```text
support_level
evidence_matches
reason
```

The four support levels are:

```text
STRONG
PARTIAL
WEAK
NOT_CLEARLY_SUPPORTED
```

Interpretation:

- **STRONG** — evidence directly and substantially establishes the material requirement.
- **PARTIAL** — substantive support exists, but a material condition, threshold, scope, or lifecycle qualifier is missing.
- **WEAK** — only indirect / adjacent support exists; the requirement itself is not substantively established.
- **NOT_CLEARLY_SUPPORTED** — the fixed evidence base does not clearly support the requirement.

Important product principle:

> `NOT_CLEARLY_SUPPORTED` means insufficient evidence in the current evidence base. It is not proof that the candidate lacks the capability in reality.

---

# 2. Why this evaluation isolates the matcher

The benchmark deliberately fixes both upstream inputs:

```text
Fixed Gold JobRequirements
+
Fixed Gold Candidate Evidence
        ↓
Production matcher pipeline
```

The benchmark does **not** rerun:

- Candidate Evidence Extraction
- Job Requirement Extraction
- Gmail ingestion
- web search / JD resolution
- persistence
- final job-level scoring

This isolates matcher behavior from upstream extraction errors.

Interview-ready framing:

> **For matcher evaluation, I fixed both upstream inputs so I could isolate the quality of the matching model itself.**

---

# 3. Frozen benchmark inputs

## Candidate Evidence Base

Total evidence units:

```text
120
```

Composition:

```text
Synthetic benchmark resume     37
Deep Learning README           12
Adaptive RAG README            21
AI Job Search Agent README     50
                              ---
Total                         120
```

The synthetic resume is a **controlled benchmark candidate source**, not the user's biography.

## Representative Job Requirements

The matcher benchmark uses:

```text
32 representative atomic requirements
```

These were curated from:

```text
109 human-reviewed Gold requirements
across 8 job-description benchmark cases
```

The 32 requirements were selected for behavioral coverage, including:

- numeric thresholds
- strength language
- AND / OR logic
- production / deployment qualifiers
- tool calling
- direct vs adjacent evidence
- credentials / licenses
- domain-specific requirements
- semantic equivalence
- no-evidence cases

The 32 requirements are **independent evaluation cases**. They must not be combined into a synthetic job-level fit score.

---

# 4. Human-adjudicated Gold

Gold status:

```text
HUMAN_ADJUDICATED_GOLD
32 / 32 reviewed
```

Gold distribution:

```text
STRONG                  13
PARTIAL                  7
WEAK                     5
NOT_CLEARLY_SUPPORTED    7
```

The most important annotation policy is qualifier preservation.

A requirement may contain material qualifiers such as:

```text
4+ years
production
deployment
clinical
collaborative
internal users
prioritized
from prototype through production
```

A candidate can have real relevant evidence and still receive `PARTIAL` or `WEAK` if an important qualifier is not established.

Examples:

```text
Git usage
≠
Git usage in a collaborative development environment

local implementation
≠
production deployment

AI decision support
≠
clinical decision support

some relevant experience
≠
2+ years of that experience
```

---

# 5. Production pipeline evaluated

The evaluated production path was:

```text
match_requirements_to_evidence
        ↓
verify_negative_mappings
        ↓
finalize_mappings
```

Model:

```text
qwen3.6-flash
```

Both benchmark runs used the same frozen inputs and the same input hashes.

Gold was **not loaded during inference**.

---

# 6. Baseline result

Baseline final support distribution:

```text
STRONG                  20
PARTIAL                  3
WEAK                     2
NOT_CLEARLY_SUPPORTED    7
```

Gold distribution:

```text
STRONG                  13
PARTIAL                  7
WEAK                     5
NOT_CLEARLY_SUPPORTED    7
```

Primary baseline metrics:

```text
Exact support-level accuracy: 62.5%  (20/32)
Macro F1:                     0.539
First-pass exact accuracy:    65.6%
```

## Baseline class-level metrics

| Gold class | Precision | Recall | F1 |
|---|---:|---:|---:|
| STRONG | 60.0% | 92.3% | 72.7% |
| PARTIAL | 0.0% | 0.0% | 0.0% |
| WEAK | 100.0% | 40.0% | 57.1% |
| NOT_CLEARLY_SUPPORTED | 85.7% | 85.7% | 85.7% |

## Baseline confusion matrix

| Gold \ Pred | STRONG | PARTIAL | WEAK | NCS |
|---|---:|---:|---:|---:|
| STRONG | 12 | 1 | 0 | 0 |
| PARTIAL | 6 | 0 | 0 | 1 |
| WEAK | 2 | 1 | 2 | 0 |
| NCS | 0 | 1 | 0 | 6 |

The clearest high-level finding was **STRONG inflation**:

```text
Gold STRONG:      13
Predicted STRONG: 20
```

The most important calibration failure was `PARTIAL`:

```text
Gold PARTIAL: 7
Correctly predicted PARTIAL: 0
```

Of the seven Gold `PARTIAL` cases, the baseline predicted:

```text
6 → STRONG
1 → NOT_CLEARLY_SUPPORTED
```

This means the model often recognized related evidence but failed to preserve a missing material qualifier.

---

# 7. Main alignment finding: middle-class calibration

The matcher was relatively good at obvious extremes:

```text
clear STRONG
clear NOT_CLEARLY_SUPPORTED
```

The more difficult boundary was:

```text
STRONG
vs
PARTIAL
vs
WEAK
```

The product-risk pattern was usually not hallucinated evidence. Instead, the model often found real evidence and then **overextended what that evidence proved**.

Typical failure modes:

### A. Material-qualifier loss

Examples:

```text
production
collaborative
clinical
internal users
prioritized
deployment
```

The evidence supported the broad capability, but not the full qualified requirement.

### B. AND-condition incompleteness

Example:

```text
practical Git capability
AND
in a collaborative development environment
```

The model had evidence for Git and separate evidence for collaboration, but not evidence that Git was used in that collaborative environment.

### C. Domain-transfer overreach

Example:

```text
customer-support decision support
→ incorrectly treated as support for
clinical decision-support tools
```

### D. Threshold calibration

Example:

```text
2+ years building customer-facing AI applications
```

The candidate had direct evidence of building relevant AI applications but the numeric duration threshold was not established.

Gold policy:

```text
real substantive activity support + missing threshold
→ PARTIAL
```

The baseline was too conservative and returned `NOT_CLEARLY_SUPPORTED`.

### E. Leadership / lifecycle overclaim

Participating in discovery or building a working local product did not establish:

```text
leading technical discovery
shipping one product from discovery through launch
prototype through production
```

---

# 8. Negative Verifier architecture

The workflow intentionally includes a second semantic pass for first-pass negative conclusions:

```text
first-pass mapping
        ↓
identify NOT_CLEARLY_SUPPORTED conclusions
        ↓
search complete evidence base for missed counter-evidence
        ↓
reconcile
        ↓
finalized mapping
```

The product rationale is asymmetric risk:

> If a first-pass matcher misses real evidence, the product can create a false candidate gap.

This second pass is a **reliability layer**, not a second independent job-fit score.

---

# 9. Negative Verifier bug discovered during alignment

In the baseline:

```text
MREQ029:
"Have familiarity with AI-assisted clinical decision-support tools."
```

First pass:

```text
NOT_CLEARLY_SUPPORTED
```

This matched Gold.

The old Negative Verifier then found non-clinical evidence such as:

```text
AI-assisted customer-support workflow
human-in-the-loop decision support
AI recommendations
job-search decision support
```

It treated those analogous capabilities as counter-evidence and caused reconciliation to change the final result to:

```text
PARTIAL
```

Gold remained:

```text
NOT_CLEARLY_SUPPORTED
```

Root cause:

> The verifier prompt behaved too much like semantic similarity search. It explicitly encouraged `DIRECT`, `TRANSFERABLE`, and `ADJACENT` support from different roles/projects/domains without sufficiently protecting material qualifiers.

---

# 10. Targeted prompt fix

The Negative Verifier prompt was changed to make the behavioral contract explicit:

```text
This is a counter-evidence verification task,
not a semantic similarity search.
```

The new policy emphasized:

- preserve every material qualifier
- analogous / transferable evidence is not enough when a qualifier remains unsupported
- cross-domain similarity does not satisfy an explicit domain requirement
- local implementation does not establish production deployment
- unspecified duration does not satisfy a numeric threshold
- individual Git usage does not establish collaborative Git usage
- return `COUNTER_EVIDENCE_FOUND` only when the recovered evidence makes the original negative conclusion materially questionable

No deterministic guardrail was added in this iteration. The experiment changed only the Negative Verifier behavioral policy/prompt.

---

# 11. PromptFix1 result

PromptFix1 final support distribution:

```text
STRONG                  21
PARTIAL                  3
WEAK                     1
NOT_CLEARLY_SUPPORTED    7
```

Aggregate metrics:

```text
Exact support-level accuracy: 62.5%  (20/32)
Macro F1:                     0.441
```

These aggregate numbers should **not** be interpreted as the causal effect of the verifier prompt change because the first-pass matcher itself varied between runs.

## Targeted case outcome

For MREQ029:

```text
Baseline first pass:
NCS

Baseline verifier:
COUNTER_EVIDENCE_FOUND
→ final PARTIAL  ❌

PromptFix1 first pass:
NCS

PromptFix1 verifier:
NO_COUNTER_EVIDENCE_FOUND
→ final NCS      ✅
```

The new verifier explicitly preserved the `clinical` domain qualifier.

This is a clean targeted signal that the prompt change addressed the observed failure mode.

---

# 12. Run-to-run variance observed

Only the Negative Verifier prompt changed, but the first-pass matcher changed four labels between the two runs:

```text
MREQ003   PARTIAL → STRONG
MREQ007   WEAK    → PARTIAL
MREQ009   NCS     → WEAK
MREQ015   WEAK    → PARTIAL
```

This explains why the number of first-pass negatives changed:

```text
Baseline:   8
PromptFix1: 7
```

The missing negative case was MREQ009, which changed from NCS to WEAK before the verifier was invoked.

Conclusion:

> The 8 → 7 negative-count change is consistent with run-to-run model variance in the first-pass matcher, not with the Negative Verifier prompt modification.

Because of this variance, the unchanged 62.5% final exact accuracy does **not** mean the prompt fix had no effect. The targeted MREQ029 behavior improved, while unrelated first-pass labels also moved.

---

# 13. Incremental value of the Negative Verifier

## Baseline

First-pass exact accuracy:

```text
65.6%
```

Final exact accuracy after verification/reconciliation:

```text
62.5%
```

The verifier made one consequential intervention:

```text
MREQ029:
NCS → PARTIAL
```

That intervention was harmful relative to Gold.

So in the baseline benchmark:

```text
correct rescue interventions: 0
harmful interventions:        1
```

## PromptFix1

The verifier checked seven first-pass negatives and returned:

```text
NO_COUNTER_EVIDENCE_FOUND
```

for all seven.

Therefore the verifier caused no final-label regressions in PromptFix1.

This does **not** prove the verifier adds positive value, because the current 32-case benchmark does not contain a demonstrated true false-negative rescue case.

The correct product conclusion is narrower:

> The architecture has a reasonable reliability rationale, the observed over-generalization bug was addressed in the targeted case, but positive incremental value of the verifier is not established by this benchmark.

---

# 14. Full 32-case alignment matrix

| ID | Requirement | Gold | Baseline first | Baseline final | PromptFix1 first | PromptFix1 final | Alignment note |
|---|---|---|---|---|---|---|---|
| MREQ001 | Partner with product and design to translate user problems into AI product requirements. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ002 | Have 4+ years of professional software development experience. | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | Aligned with Gold in the baseline final result. |
| MREQ003 | Have strong Python programming skills. | STRONG | PARTIAL | PARTIAL | STRONG | STRONG | Baseline was too conservative and missed/underweighted direct Python implementation evidence; PromptFix1 happened to recover STRONG in the first pass. |
| MREQ004 | Have experience building applications with large language models or other generative AI systems. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ005 | Have experience with vector databases. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ006 | Have experience with prompt evaluation or LLM evaluation frameworks. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ007 | Monitor latency and cost in production. | WEAK | WEAK | WEAK | PARTIAL | PARTIAL | PromptFix1 first pass drifted from WEAK to PARTIAL. Production latency/cost monitoring remains unproven; this was treated as run-to-run variance. |
| MREQ008 | Design tool-calling workflows that connect language models to internal APIs, search systems, and business data. | PARTIAL | STRONG | STRONG | STRONG | STRONG | Overclaim: real tool-enabled web search exists, but full LLM tool-calling across internal APIs and business data is not established. |
| MREQ009 | Have at least 2 years building customer-facing AI or machine-learning applications. | PARTIAL | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | WEAK | WEAK | Threshold calibration: direct customer-facing / user-oriented AI-building evidence exists, but the 2+ year threshold is unmet. Gold = PARTIAL; baseline was too harsh (NCS), PromptFix1 = WEAK. |
| MREQ010 | Have working knowledge of TypeScript. | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | Aligned with Gold in the baseline final result. |
| MREQ011 | Have hands-on capability with REST APIs. | WEAK | STRONG | STRONG | STRONG | STRONG | Specificity overclaim: hands-on API integration is evidenced, but REST specifically is not established. Gold remains WEAK. |
| MREQ012 | Be able to debug model failures. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ013 | Translate customer research into prioritized product requirements. | PARTIAL | STRONG | STRONG | STRONG | STRONG | Qualifier miss: research → requirements is direct, but prioritization of those research-derived requirements is not clearly shown. |
| MREQ014 | Have 4+ years of product management experience. | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | Aligned with Gold in the baseline final result. |
| MREQ015 | Have demonstrated experience shipping at least one software product from discovery through launch. | WEAK | WEAK | WEAK | PARTIAL | PARTIAL | PromptFix1 first pass drifted WEAK → PARTIAL. Evidence spans discovery/prototype/product work, but does not establish one product taken from discovery through launch. |
| MREQ016 | Be comfortable using SQL or another analytics tool to investigate product behavior. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ017 | Have prior work with evaluation datasets or human review workflows. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ018 | Have a Bachelor's degree in Computer Science, Data Science, Engineering, or a related field, OR equivalent practical experience. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ019 | Have experience deploying services on at least one major cloud platform: AWS, GCP, or Azure. | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | Aligned with Gold in the baseline final result. |
| MREQ020 | Have practical capability using Git in a collaborative development environment. | PARTIAL | STRONG | STRONG | STRONG | STRONG | AND-condition miss: Git usage is direct, collaboration is separately evidenced, but Git usage inside a collaborative development environment is not. |
| MREQ021 | Have practical capability with Kubernetes. | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | Aligned with Gold in the baseline final result. |
| MREQ022 | Have familiarity with LLM evaluation, retrieval systems, or vector databases. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ023 | Build AI-assisted workflow features from prototype through production. | PARTIAL | STRONG | STRONG | STRONG | STRONG | Lifecycle qualifier miss: prototype / local working product is not production deployment. |
| MREQ024 | Interview internal users and incorporate feedback into product iterations. | PARTIAL | STRONG | STRONG | STRONG | STRONG | Qualifier miss: interviews/usability are direct, but 'internal users' and incorporation through product iterations are not fully established. |
| MREQ025 | Investigate production issues across application code and model behavior. | PARTIAL | STRONG | STRONG | STRONG | STRONG | Production qualifier miss: failure investigation and fault isolation are real, but production environment is not established. |
| MREQ026 | Define success metrics and evaluation plans for new AI capabilities. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ027 | Have strong cross-functional communication skills. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |
| MREQ028 | Hold an active, unrestricted Registered Nurse (RN) license in at least one U.S. state. | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | Aligned with Gold in the baseline final result. |
| MREQ029 | Have familiarity with AI-assisted clinical decision-support tools. | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | PARTIAL | NOT_CLEARLY_SUPPORTED | NOT_CLEARLY_SUPPORTED | Domain-transfer overreach in baseline Negative Verifier: non-clinical decision-support evidence was used to challenge an explicit clinical-domain requirement. PromptFix1 fixed this case. |
| MREQ030 | Be comfortable leading technical discovery sessions. | WEAK | STRONG | STRONG | STRONG | STRONG | Leadership overclaim: participation in interviews/usability and presenting findings does not establish leading technical discovery sessions. |
| MREQ031 | Have experience deploying LLM applications. | WEAK | PARTIAL | PARTIAL | PARTIAL | PARTIAL | Deployment qualifier: building local LLM apps is adjacent to deployment experience, but deployment itself is not established. |
| MREQ032 | Have practical capability with retrieval-augmented generation, evaluation frameworks, or tool-calling agents. | STRONG | STRONG | STRONG | STRONG | STRONG | Aligned with Gold in the baseline final result. |

---

# 15. What was intentionally not pursued

This evaluation cycle is now closed.

The following were deliberately **not** pursued further:

- repeated 3–5 run stability experiments
- temperature / seed sensitivity analysis
- confidence calibration
- additional prompt tuning after PromptFix1
- LLM-as-judge scoring
- job-level synthetic fit scoring across the 32 independent cases
- production traffic sampling
- statistical confidence intervals
- redesign of the Negative Verifier architecture
- relationship-taxonomy cleanup beyond the primary support-level endpoint

Reason:

> The goal of this learning cycle is interview-ready component evaluation and failure diagnosis, not exhaustive production validation.

Run-to-run variance is recorded as a limitation rather than treated as a new optimization rabbit hole.

---

# 16. Evaluation closure

## What this benchmark established

1. The matcher can reliably handle many obvious direct-support and no-evidence cases.
2. The dominant semantic weakness is **support-level calibration around material qualifiers**, especially `PARTIAL`.
3. The baseline had a meaningful **STRONG inflation** tendency.
4. A targeted alignment review exposed a specific **domain-transfer overreach** bug in the Negative Verifier.
5. Tightening the verifier prompt corrected that observed case without changing the architecture.
6. The model shows run-to-run variance, so a single aggregate score should not be overinterpreted.
7. Component-level isolation made it possible to distinguish matcher behavior from upstream extraction behavior.

## Final status

```text
Matcher evaluation cycle: CLOSED
Gold: HUMAN_ADJUDICATED_GOLD
Representative cases: 32
Candidate evidence units: 120
Baseline exact label accuracy: 62.5%
Main weakness: STRONG inflation / PARTIAL calibration
Targeted verifier bug: fixed on observed regression case
Known limitation: stochastic run-to-run variance
```

---

# 17. Core AIPM lesson

The most important lesson is not the 62.5% number.

It is the evaluation process:

```text
define semantic contract
        ↓
freeze upstream inputs
        ↓
human-adjudicate Gold
        ↓
run production component
        ↓
align prediction ↔ Gold
        ↓
find failure pattern
        ↓
connect failure to product risk
        ↓
form targeted hypothesis
        ↓
make one behavioral change
        ↓
rerun frozen benchmark
        ↓
check target improvement + regressions
        ↓
know when to stop
```

A strong AI PM does not ask only:

> "What score did the model get?"

The stronger question is:

> **"Which behavior failed, why does that failure matter to the user, and what is the smallest testable change that should improve it?"**

---

# 18. Source artifacts

This report was built from the frozen evaluation artifacts:

```text
01_input_fixed_candidate_evidence_v2.json
02_input_representative_requirements_v2.json
03_gold_output_human_adjudicated_mappings_v2.json
matcher_predictions_v2.json
matcher_predictions_v2_promptfix1.json
```

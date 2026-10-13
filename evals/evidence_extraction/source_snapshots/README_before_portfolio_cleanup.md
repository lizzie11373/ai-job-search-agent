# AI Job Search Agent

A local AI-assisted job-search product that turns noisy job-alert emails into a durable, evidence-grounded review queue.

The system connects to Gmail, identifies job-related messages, extracts one or more job leads, resolves each lead to a usable public job description, deduplicates already-seen postings, extracts structured job requirements, compares every requirement against a grounded candidate evidence base, calculates a deterministic fit signal, applies bounded preference logic, persists completed analyses, and lets the user decide whether to **Pass**, **Save for later**, or **Pursue**.

The product is intentionally designed as a **human-in-the-loop decision-support system**, not an autonomous application bot.

---

## 1. Product Goal and Boundary

The core user problem is not simply “find more jobs.” It is:

> Reduce the repeated manual work of opening job-alert emails, locating the real job posting, deciding whether it is still valid, understanding the requirements, comparing those requirements against the candidate's actual background, and deciding which opportunities deserve attention.

V1 stops at human review:

```text
job-alert emails
    -> job-lead extraction
    -> verified public posting
    -> exact posting-URL dedupe
    -> grounded candidate/job analysis
    -> persistence
    -> human decision: Pass / Save for later / Pursue
```

V1 does **not** automatically customize resumes, submit applications, contact recruiters, or make final career decisions for the user.

The project is a working local portfolio/personal tool connected to real external services. It should not be described as a cloud production deployment.

---

## 2. End-to-End Architecture

```text
Gmail
  |
  v
Metadata-first email ingestion
  |
  v
Qwen job-related classification
  |
  +-- not job-related ----------------------> mark email processed
  |
  v
Fetch full message body only when needed
  |
  v
Qwen JobCandidate extraction
  |             (0..N candidates per email)
  v
JD Resolution / Verification
  |
  +--> source-aware routing
  +--> Qwen Responses API + hosted web_search tool
  +--> deterministic URL filtering
  +--> bounded page fetching
  +--> structural page validation
  +--> LLM semantic verification
  |
  +-- normal miss --------------------------> UNVERIFIED
  |
  v
Verified analysis-ready public posting
  |
  v
Exact posting-URL dedupe
  |
  +-- duplicate ----------------------------> reuse persisted opportunity state
  |
  v
Job Requirement Extraction
  |
  v
Requirement Grounding Validation
  |
  v
Requirement-Evidence Matching
  |       ^
  |       |
  |   Active Candidate Evidence Base
  |       ^
  |       |
  |   Resume + Supporting Materials
  |   -> evidence extraction
  |   -> grounding validation
  |
  v
Negative-Conclusion Verification
  |
  v
Finalized RequirementEvidenceMapping objects
  |
  +--> deterministic Requirement Fit
  +--> preference checks
  +--> bounded Pursuit Priority
  +--> Strong Matches / Main Gaps summaries
  |
  v
Atomic persistence
  |
  v
Streamlit review UI
  |
  v
Pass / Save for later / Pursue
```

---

## 3. Core Design Principles

### Validate before reasoning

Both sides of semantic matching are grounded before they reach the matcher:

```text
Candidate document
-> EvidenceUnit extraction
-> provenance + semantic grounding validation
-> CandidateEvidenceBase

Job description
-> JobRequirement extraction
-> provenance + semantic grounding validation
-> validated requirements
```

The matcher is therefore responsible for **support judgment**, not for re-reading raw source documents or deciding whether the upstream extraction was grounded.

### Use deterministic code for deterministic problems

Python handles boundaries that do not require semantic judgment, including:

- stable IDs and workflow state
- enum/category normalization
- URL validation and filtering
- exact posting-URL dedupe
- structured-output validation
- requirement-fit arithmetic
- preference policy
- priority thresholds
- database constraints and transactions
- processed-email state

LLMs are used where semantic interpretation is genuinely useful, including:

- email relevance classification
- job-candidate extraction
- fuzzy job-page verification
- candidate evidence extraction / grounding
- job requirement extraction / grounding
- requirement-evidence support judgment
- negative-conclusion verification

### Precision-first JD resolution

A false “verified” posting can contaminate all downstream analysis, so V1 prefers a normal `UNVERIFIED` result over accepting a questionable page.

### Human review is part of the product

Requirement-level reasoning remains inspectable. The user can see the requirement, support level, match reason, evidence claim, source document, and original source text before making a decision.

### Durable state must survive partial failures

Successfully completed opportunities are persisted immediately. A later failure should not erase earlier completed work, and retry behavior should not create duplicate opportunities.

### External integrations are isolated behind interfaces

The product uses provider-neutral boundaries where practical:

- `EmailSource` for inbox access
- shared OpenAI-compatible LLM client for Qwen
- `search_web()` for web-search provider abstraction
- backend service functions for the Streamlit UI

---

## 4. Technology Stack

- **Python 3.11+**
- **Streamlit** for the local product UI
- **SQLite** for durable local product state
- **OpenAI Python SDK** against an OpenAI-compatible Qwen / Alibaba Model Studio endpoint
- **Qwen generation models** for structured semantic tasks
- **Qwen Responses API Web Search tool** for bounded public web search
- **Gmail API** with installed-app OAuth and read-only scope
- **pytest** for deterministic unit/integration-style tests
- direct SDK / application code; no LangChain or LangGraph dependency

The architecture separates model/provider access from domain logic so the workflow is not tightly coupled to one prompt call site.

---

## 5. LLM and Search Provider Configuration

The shared generation client reads:

```bash
DASHSCOPE_API_KEY=...
DASHSCOPE_BASE_URL=...
GENERATION_MODEL=...
```

Web search uses a provider-neutral application interface:

```python
search_web(query)
```

The current provider route is Qwen:

```bash
WEB_SEARCH_PROVIDER=qwen
SEARCH_MODEL=...
```

The Qwen search adapter uses the Responses API with the provider-hosted Web Search tool:

```python
tools=[{"type": "web_search"}]
tool_choice="required"
```

This is a real tool-enabled LLM workflow. However, the overall application remains **bounded and application-orchestrated**: the program decides when JD resolution needs a search, invokes one search operation, then deterministically processes returned URLs. It is not an open-ended autonomous ReAct loop.

---

## 6. Gmail Integration

### OAuth and privacy boundary

The local UI uses Google's installed-app OAuth flow with the read-only scope:

```text
https://www.googleapis.com/auth/gmail.readonly
```

Default local files:

```text
data/private/google_credentials.json
data/private/gmail_token.json
```

The credentials and token remain local, are excluded from Git, are not stored in the application database, and are not sent to the LLM.

The product does send the minimum application content required for semantic steps—such as email metadata for classification and relevant full email content for JobCandidate extraction—to the configured model service.

Expired access tokens are refreshed automatically when a valid refresh token is available. If normal refresh cannot recover access, the UI requires the user to reconnect.

### One active Gmail account

The product keeps one active Gmail account at a time.

`Change Gmail account` uses a safe replacement flow: the old token is preserved until the new account has successfully authorized and its Gmail identity has been verified. Existing opportunities, preferences, and candidate evidence remain unchanged; only future Agent Runs use the new inbox.

Processed-email state is scoped by:

```text
account_key + message_id
```

so Gmail message IDs from one account cannot suppress messages in another account.

### Metadata-first ingestion

The ingestion boundary deliberately avoids fetching every full email:

```text
Gmail messages.list
-> messages.get(format=metadata)
-> Qwen job-related classification
-> messages.get(format=full) only for related messages
-> body + extracted HTML links
-> Qwen JobCandidate extraction
```

This reduces unnecessary Gmail payloads and unnecessary model work.

### Current discovery window

The latest low-quota test configuration uses a rolling **1-hour** default window:

```text
after:<current_epoch_minus_3600_seconds>
```

The adapter still supports overrides:

```bash
JOB_AGENT_GMAIL_LOOKBACK_HOURS=1
JOB_AGENT_GMAIL_LOOKBACK_DAYS=1
JOB_AGENT_GMAIL_MAX_MESSAGES=200
```

Only one of the hour/day lookback overrides should be used at a time. The default message cap is 200.

Optional path overrides:

```bash
JOB_AGENT_GMAIL_CREDENTIALS_PATH="/path/to/google_credentials.json"
JOB_AGENT_GMAIL_TOKEN_PATH="/path/to/gmail_token.json"
```

The legacy `JOB_AGENT_EMAIL_LOADER="module:function"` mechanism remains available for tests and custom local adapters; the product UI uses the built-in Gmail source.

---

## 7. Email Classification and JobCandidate Extraction

Each recent, unprocessed email first receives a lightweight relevance judgment from sender, subject, and snippet.

If the message is not job-related, it is marked processed without fetching the full body.

If it is job-related, the full message is fetched and the extractor can return **zero, one, or multiple `JobCandidate` objects**. A candidate represents an email-derived lead rather than a verified job posting.

A `JobCandidate` can contain fields such as:

```text
source
source message ID
company
title
location
source URL / extracted link metadata
```

The product intentionally separates:

```text
email says this job may exist
```

from:

```text
we have verified a sufficiently complete public JD that is safe to analyze
```

That separation is the purpose of JD Resolution.

---

## 8. JD Resolution, Hosted Web Search, and Verification

### Source-aware routing

Current V1 routing is intentionally bounded:

```text
LinkedIn / Indeed lead
-> skip the email/provider URL
-> go directly to bounded Web Search

Other source
-> try source_url once
-> if it does not yield an analysis-ready verified page
-> fall back to the same bounded Web Search pipeline
```

### Search query

The application creates one deterministic query from the strongest available lead fields, primarily:

```text
company + full title + optional location
```

The application then calls the provider-neutral `search_web()` interface exactly once for that search stage.

### Qwen hosted Web Search tool

The current Qwen search adapter calls the Responses API and requires the model's `web_search` tool. The search instruction emphasizes resolving an existing lead rather than discovering arbitrary new roles.

This architecture provides direct experience with an LLM using a hosted search tool while keeping orchestration under application control.

### Bounded result processing

V1 applies explicit cost and reliability bounds:

```text
up to 30 ranked search results considered
-> conservative URL cleanup / dedupe
-> preserve provider ranking
-> at most 15 page fetch attempts
-> fetch in batches of 5
-> structural page validation
-> one semantic-verification call per usable batch
-> early stop on first sufficiently matching + sufficiently complete JD
```

The deterministic URL filter removes obvious generic/index/non-posting URLs and duplicates. It deliberately avoids doing title/company/location semantic matching in Python.

### Page retrieval

Pages are fetched with deterministic HTTP logic. Individual stale, malformed, blocked, or otherwise unfetchable search candidates can be skipped without discarding the entire search result set.

A failure of the search operation itself is different: it is treated as a workflow-level technical failure and remains retryable.

### Semantic verification boundary

The semantic verifier asks two questions for each fetched page:

1. Is this page sufficiently consistent with the email-derived job lead?
2. Is the page sufficiently complete for downstream requirement extraction and fit analysis?

The verifier can tolerate reasonable company/title/location wording variants. It does not require exact string equality, the same provider job ID, or proof of exact cross-site identity.

A third-party specific job page can pass if it is a sufficiently consistent and complete public posting. The search-provider prompt may prefer employer/ATS pages, but the downstream acceptance boundary is **semantic consistency + sufficient JD completeness**, not “official domain or fail.”

### Terminal outcomes

A lead can end as:

```text
VERIFIED
UNVERIFIED
TECHNICAL_FAILURE
```

`UNVERIFIED` is a normal business outcome: the agent simply does not analyze that lead further.

A technical failure is not silently converted into “no match.” It remains retryable.

---

## 9. Exact Posting-URL Deduplication

After a posting is verified, the product checks the resolved posting URL against persisted opportunities.

```text
verified posting URL
-> existing JobOpportunity?
   -> yes: DUPLICATE
   -> no: NEW -> Opportunity Analysis
```

V1 intentionally uses exact posting URL as its durable dedupe key rather than claiming to solve global semantic job identity across different URLs and providers.

Opportunity IDs are deterministic internal IDs derived from the posting URL.

This rule is especially important during retries: an email that failed halfway through a multi-candidate run can be retried without duplicating opportunities that were already successfully persisted.

---

## 10. Candidate Background and Evidence Pipeline

### Managed sources

Candidate background is made from:

- one active **Resume**
- zero or more append-only **Supporting Materials**

Resume replacement is deliberately safe:

```text
upload replacement
-> extract evidence
-> validate evidence
-> only then switch active Resume
```

A failed replacement leaves the previous active Resume intact.

Supporting Materials remain append-only and active in V1.

Future matching uses active managed sources. Historical Job Detail pages can still hydrate evidence that came from an older inactive resume because evidence IDs remain durable and are never reused.

### Candidate evidence extraction

The extractor converts candidate documents into structured `EvidenceUnit` records:

```text
EvidenceUnit
- evidence_id
- claim
- source_document
- source_section
- source_text
- evidence_type
- grounding_status
```

The extraction prompt is intentionally conservative:

- use only explicit facts from the document
- do not infer missing facts
- do not exaggerate ownership, responsibility, impact, or technical complexity
- preserve source provenance

### Evidence validation

Evidence validation has two conceptual gates:

```text
1. deterministic provenance validation
2. semantic grounding validation
```

Only validated evidence enters `CandidateEvidenceBase` for future matching.

This creates the core upstream contract:

> If a capability is not represented in the source documents or the extractor fails to recover it, the matcher cannot legitimately claim that capability later.

---

## 11. Job Requirement Extraction

The requirement extractor transforms a verified full JD into atomic, grounded `JobRequirement` objects.

Each requirement contains:

```text
requirement_id
requirement
category
requirement_level
jd_source_text
jd_section
grounding_status
```

### Categories

The current category taxonomy supports:

```text
RESPONSIBILITY
EXPERIENCE
SKILL
DOMAIN_KNOWLEDGE
EDUCATION
LICENSE
CERTIFICATION
OTHER
```

Common variants such as `LICENSURE`, `CERTIFICATE`, `CREDENTIAL`, etc. are normalized. An unfamiliar non-critical category can fall back to `OTHER` rather than aborting the entire Agent Run.

Category is descriptive metadata; it is **not** the numeric scoring weight.

A useful semantic distinction used during evaluation is:

```text
EXPERIENCE
= what has the candidate previously done / demonstrated in prior activity?

SKILL
= what can the candidate use or do as a practical capability?
```

Surface wording such as “experience with X” is not enough by itself to determine the category.

### Requirement levels

```text
CORE
REQUIRED
PREFERRED
```

Requirement level is kept strict because it affects downstream weighting.

### Extraction rules

The extractor is instructed to:

- use only explicit JD content
- avoid outside knowledge
- avoid strengthening the employer's wording
- preserve “what the person will DO” vs “what the person must HAVE”
- avoid combining unrelated requirements
- attach exact source text and section provenance

### Requirement validation

Extracted requirements are checked for valid structure, source provenance, and semantic grounding before matching.

Only validated requirements participate in matching and scoring.

---

## 12. Requirement-Evidence Matching

### Evaluation unit

The semantic matcher works at the **requirement level**, not as a single opaque job-level similarity score.

For every validated job requirement, it evaluates the **complete validated Candidate Evidence Base** and returns one finalized mapping.

```text
one JobRequirement
+
complete CandidateEvidenceBase
-> one RequirementEvidenceMapping
```

The matching architecture intentionally avoids embedding Top-K filtering at this stage. The matcher sees the complete evidence base so complementary evidence is not silently discarded by a retrieval step.

### Support levels

Each requirement receives exactly one support level:

```text
STRONG
PARTIAL
WEAK
NOT_CLEARLY_SUPPORTED
```

Interpretation:

- **STRONG** — evidence directly and substantially supports the material requirement.
- **PARTIAL** — real, substantive support exists, but an important condition, threshold, scope, or lifecycle element is missing.
- **WEAK** — only indirect or adjacent evidence exists; it is relevant but does not substantively establish the requirement.
- **NOT_CLEARLY_SUPPORTED** — the current validated evidence base does not clearly support the requirement.

`NOT_CLEARLY_SUPPORTED` means **absence of sufficient evidence in the current evidence base**, not proof that the candidate lacks the capability in reality.

### Evidence relationships

The current product/evaluation contract uses requirement-linked evidence relationships such as:

```text
DIRECT
ADJACENT
```

A `DIRECT` evidence item can still support an overall `PARTIAL` mapping when another material condition is missing—for example a numeric years-of-experience threshold or a production-deployment requirement.

For `NOT_CLEARLY_SUPPORTED`, the evidence-match list is empty.

### Complementary evidence

Multiple atomic evidence units may jointly support one requirement when they establish complementary parts of the required capability.

The matcher must not, however, combine unrelated projects to pretend that one specific end-to-end lifecycle occurred when the evidence does not establish that lifecycle.

### Structured output validation

The application validates matcher output deterministically:

- exactly one mapping per validated requirement
- no unknown requirement IDs
- no duplicate requirement mappings
- valid support labels only
- valid evidence IDs only
- no duplicate evidence within one mapping
- required reason text
- evidence/support consistency

The model is not allowed to silently omit difficult requirements.

---

## 13. Negative-Conclusion Verification and Reconciliation

A first-pass negative judgment has asymmetric product risk: if the matcher misses existing evidence, the product may tell the user they have a gap that is not real.

Therefore the workflow adds a second semantic step for negative conclusions:

```text
first-pass mapping
-> identify negative / insufficient-support conclusions
-> search the complete evidence base again for counter-evidence
-> reconcile
-> finalized mapping
```

This is a deliberate reliability layer rather than a second independent job-fit score.

The final `RequirementEvidenceMapping` remains the source of truth for downstream scoring and UI explanation.

---

## 14. Deterministic Requirement Fit

After semantic matching is finalized, Requirement Fit is calculated in deterministic code.

It is **not** an LLM-generated probability and must not be interpreted as the probability of getting an interview, receiving an offer, or objectively liking the job.

### Support scores

```text
STRONG                  = 1.00
PARTIAL                 = 0.65
WEAK                    = 0.30
NOT_CLEARLY_SUPPORTED   = 0.00
```

### Requirement-level weights

```text
CORE        = 1.30
REQUIRED    = 1.10
PREFERRED   = 0.70
```

### Formula

```text
weighted contribution
= support score * requirement-level weight

Requirement Fit
= sum(weighted contributions)
  / sum(requirement-level weights)
  * 100
```

The score is rounded to one decimal place.

Every validated requirement must have exactly one finalized mapping before scoring is allowed.

---

## 15. Preferences and Pursuit Priority

Preferences are deliberately separated from semantic candidate/job fit.

V1 persists five optional preference categories:

```text
Location
Work Mode
Industry
Company Size
Employment Type
```

Compensation is intentionally excluded from the current V1 UI/persistence contract.

A preference check can produce:

```text
MATCH
UNKNOWN
MISMATCH
```

Preference does **not** modify Requirement Fit.

### Base priority thresholds

Prototype thresholds:

```text
Requirement Fit >= 85   -> TOP_PRIORITY
Requirement Fit >= 70   -> STRONG_OPPORTUNITY
Requirement Fit >= 55   -> WORTH_CONSIDERING
otherwise               -> DEPRIORITIZE
```

These are product hypotheses, not scientific constants.

### Bounded preference modifier

- `MATCH` is neutral.
- `UNKNOWN` is neutral.
- one or more `MISMATCH` results can downgrade priority by **at most one tier**.
- multiple mismatches do not stack into repeated automatic downgrades.
- Requirement Fit itself never changes.

This keeps “candidate capability fit” and “personal preference fit” conceptually separate.

---

## 16. Strong Matches and Main Gaps

Job-level summary fields do not introduce another semantic LLM judgment.

They are deterministic projections of finalized requirement-level mappings:

```text
STRONG
-> Strong Matches

WEAK or NOT_CLEARLY_SUPPORTED
-> Main Gaps

PARTIAL
-> remains visible in detailed requirement analysis
   but is not promoted to either summary bucket
```

The detailed requirement mapping remains the underlying reasoning source.

---

## 17. Agent Run Orchestration and Failure Semantics

`run_agent()` owns the user-facing execution sequence.

Current high-level behavior:

```text
load active candidate evidence + preferences
-> list recent Gmail metadata
-> skip already-processed messages
-> classify metadata
-> fetch full body only for job-related messages
-> extract 0..N JobCandidates
-> process candidates sequentially
-> persist each completed new opportunity immediately
-> mark the parent email processed only after all its candidates reach terminal outcomes
```

### Why email processing is committed late

If one email contains multiple opportunities and a technical failure occurs on a later candidate:

- earlier completed opportunities remain persisted
- the email remains unprocessed
- a later Agent Run retries the email
- exact posting-URL dedupe protects already-saved opportunities from duplication

This gives the workflow useful partial-progress durability without incorrectly claiming that the whole email completed.

### Fault isolation

The system distinguishes among:

```text
normal business miss
individual candidate/page failure
workflow-level technical failure
```

Examples:

- no trustworthy/complete posting found -> normal `UNVERIFIED`
- one search URL cannot be fetched -> skip that URL and continue
- hosted Web Search API itself fails -> technical failure, retry later
- semantic verification fails structurally/technically -> technical failure
- downstream analysis raises unexpectedly -> do not mark email processed

Unexpected failures are deliberately visible during development rather than silently converted into misleading business results.

### Requirement-category robustness

A prior real run exposed an unknown `LICENSE` category that could abort the workflow. The extractor was hardened to support `LICENSE` and `CERTIFICATION`, normalize common aliases, and fall back unknown non-critical categories to `OTHER` while keeping requirement-level validation strict.

---

## 18. Persistence and Durable Product State

SQLite is used as durable local product state.

A completed opportunity analysis is treated as a historical snapshot. Rerunning the agent analyzes only new exact-posting-URL opportunities. Later user decisions do not rewrite the historical analysis fields.

### Atomic completed-opportunity persistence

A completed opportunity persists the related product state together, including:

```text
JobOpportunity
JobRequirements
RequirementEvidenceMappings
EvidenceMatches
```

The intent is that persistence represents a completed product state, not a misleading half-complete analysis.

### Historical evidence integrity

The schema protects historical evidence references. Referenced candidate evidence cannot simply disappear when a resume is replaced.

Durable evidence IDs are never reused.

### Database migration

The current README-era migration adds or maintains structures including:

```text
candidate_sources
candidate_evidence.source_id
app_state
candidate_preferences
job_opportunities.job_attributes_json
job_opportunities.created_at
job_resolution_attempts
```

The `evidence_matches -> candidate_evidence` foreign-key behavior protects referenced historical evidence with `ON DELETE RESTRICT`.

---

## 19. UI-Facing Backend Services

The Streamlit UI calls high-level product services instead of directly coordinating low-level agents.

Representative actions include:

```python
list_needs_review()
list_reviewed()
get_opportunity_detail(opportunity_id)
set_user_decision(opportunity_id, decision)

get_background_state()
replace_resume(filename=..., content=...)
add_supporting_material(filename=..., content=...)

get_preferences()
save_preferences(preferences)

get_setup_completed()
mark_setup_completed()
finish_setup_and_run_agent(...)
```

This keeps UI concerns separate from ingestion, resolution, semantic analysis, and persistence internals.

---

## 20. Local Streamlit UI

The local product includes:

- first-time onboarding: **Background -> Preferences -> Ready**
- Resume upload/replacement
- Supporting Materials management
- Preferences configuration
- persistent navigation across **Opportunities / Background & Evidence / Preferences**
- **Needs Review** and **Reviewed** queues
- Job Detail with **Overview** and **Requirement Analysis** tabs
- Pass / Save for later / Pursue decisions in Job Detail
- requirement-level support explanations
- expandable grounded evidence with original source text
- safe Gmail connection/recovery states
- safe Resume replacement behavior
- append-only Supporting Materials

### User-facing Agent Run progress

The latest simplified progress experience intentionally exposes only three understandable stages:

```text
1. Checking recent emails — Found N emails
2. Processing opportunity X / Y
3. Complete
```

Internal verification, analysis, and save phases still happen, but the UI does not pretend to know a meaningful percentage for semantic work.

---

## 21. Job Detail Evidence Contract

The user-facing trace is:

```text
Requirement
-> Support Level
-> Match Reason
-> Evidence Claim
-> Source Document
-> Original Source Text
```

Internal implementation metadata such as evidence relationship labels can remain hidden when the same distinction is communicated more clearly in natural-language reasoning.

This makes the product inspectable: the user can understand not only the final fit score but why each requirement was classified the way it was.

---

## 22. Opportunity Ordering

For **Needs Review**, the current ordering is:

```text
Pursuit Priority
-> Requirement Fit
-> Preference Match
-> newer created_at
```

When the preference tie-break compares different configured denominators, it uses the match rate:

```text
matched / configured
```

`0 / 0` receives no positive tie-break advantage.

---

## 23. Onboarding and Product-State Rules

`app_state.setup_completed` is the onboarding-completion flag.

The product commits setup completion **before** starting the first Agent Run. Therefore an interrupted first run does not force the user through onboarding again; the user can return to Opportunities and run the agent again.

Candidate background rules:

```text
Resume                 -> singleton active source
Supporting Materials   -> append-only active sources
old Resume evidence    -> preserved for historical references
future matching        -> active managed sources only
```

Per-opportunity preference results are historical snapshots and are not silently recomputed when the user later changes global preferences.

---

## 24. Data / Domain Objects

Conceptually, the pipeline separates the following stages and objects:

```text
EmailMetadata
JobAlertEmail
JobCandidate
ResolvedJobPosting
JobRequirement
EvidenceUnit
CandidateEvidenceBase
EvidenceMatch
RequirementEvidenceMapping
JobOpportunity
```

That separation is intentional:

- discovery is not verification
- verification is not analysis
- extraction is not matching
- semantic matching is not numeric scoring
- numeric scoring is not user preference
- system recommendation is not the human decision

---

## 25. Evaluation Strategy

Evaluation is treated as a separate engineering discipline from normal software testing.

```text
Software testing
= Does the code/workflow function correctly?

AI behavioral evaluation
= How well does each semantic component behave?

Product validation
= Does the system actually create user value?
```

Offline semantic evaluation deliberately isolates model components from Gmail, Web Search, network availability, and persistence so model behavior can be measured under controlled inputs.

### 25.1 Candidate Evidence Extraction evaluation

The evidence-extraction benchmark uses four controlled candidate documents:

```text
Synthetic AI Product resume
Deep Learning project README
Adaptive RAG project README
AI Job Search Agent README
```

Six primary evaluation dimensions are reviewed:

```text
1. Coverage / Recall
2. Selection / Precision
3. Semantic Correctness
4. Granularity / Atomicity
5. Grounding / Source Attribution
6. Duplication / Redundancy
```

A key learning was that exact quote fidelity and semantic grounding are not the same thing. In the reviewed run, 56 of 72 generated `source_text` strings were exact substrings (77.78%); the other 16 should not automatically be labeled hallucinations because some were semantically supported but formatted, stitched, or paraphrased differently.

The largest observed product risk was upstream **recall**: architecture, evaluation, state-management, privacy, and product decisions embedded in long prose were easier to miss than short explicit bullets. An upstream evidence miss can become a downstream false candidate gap.

### 25.2 Job Requirement Extraction evaluation

A curated eight-JD behavioral benchmark was built to cover:

```text
baseline extraction
compound atomicity
strength language
alternatives / equivalency
noise / negation
repetition / deduplication
license / certification / domain taxonomy
long-form FDE prose
```

Final v3 results on that benchmark:

```text
Gold requirements:                 109
Agent predictions:                 102
Gold concepts covered:             106 / 109
Prediction validity precision:     99.0%
Semantic recall:                    97.2%
Semantic F1:                        98.1%
Requirement-level accuracy:       100.0%
Category accuracy:                  96.0%
Grounding pass:                    102 / 102
Exact source fidelity:             102 / 102
```

Structural errors are tracked separately from semantic F1 because a bundled requirement or incorrectly split OR-cluster can receive semantic credit while still being structurally wrong.

Main observed weaknesses:

- compound atomicity
- recall for requirements hidden in prose/equivalency language
- logical preservation for substitution and OR conditions
- some category-boundary errors in long-form qualifications
- semantic deduplication of repeated requirements

### 25.3 Requirement-Evidence Matching evaluation

The matcher benchmark isolates the matcher from upstream extraction errors:

```text
fixed Gold JobRequirements
+
fixed Gold Candidate Evidence
-> matcher
```

The benchmark design uses representative atomic requirements rather than treating eight source JDs as one synthetic job.

The final v2 matching benchmark is frozen with:

```text
120 human-reviewed candidate evidence units
32 curated atomic job requirements
32 / 32 human-adjudicated Gold mappings
```

The evidence corpus comprises 37 units from the synthetic benchmark resume, 12 from the Deep Learning README, 21 from the Adaptive RAG README, and 50 from the expanded AI Job Search Agent README. The 32 requirements were selected from the 109-requirement Gold pool across eight JDs.

The unit of judgment is one requirement-level mapping:

```text
requirement_id
gold_support_level
gold_reason
gold_evidence_matches[]
    evidence_id
    relationship
    reason
```

Gold labels are human-adjudicated before examining a fresh matcher run to reduce anchoring/leakage. Evaluation runs use the fixed inputs without rerunning the upstream extractors.

### Frozen benchmark artifacts and evaluation closure

The final v2 source-of-truth artifacts are:

- `evals/matching_evaluation/fixed_inputs/01_input_fixed_candidate_evidence_v2.json`
- `evals/matching_evaluation/fixed_inputs/02_input_representative_requirements_v2.json`
- `evals/matching_evaluation/gold_set/03_gold_output_human_adjudicated_mappings_v2.json`
- `evals/matching_evaluation/alignment/Requirement_Evidence_Matching_Alignment_Report_v2.md`

The initial corpus contained 90 evidence units. After expanding the Job Agent source README, its Evidence Gold was rebuilt and adjudicated, and the final corpus was frozen at 120 units. The earlier instruction to rebuild the corpus is therefore completed, not an outstanding task.

Baseline final exact support-level accuracy was **20 / 32 (62.5%)**, with macro F1 **0.539**. The main failure pattern was STRONG-support inflation caused by loss of material qualifiers.

A targeted Negative Verifier prompt change corrected the observed MREQ029 clinical-domain regression. The PromptFix1 run also had final exact accuracy of **20 / 32 (62.5%)**. First-pass matcher labels varied between runs, so the target-case correction does not establish aggregate improvement. Positive incremental lift from the verifier was not demonstrated by this benchmark.

This evaluation cycle is **closed** for the portfolio V1. Preserve the frozen v2 inputs and Gold for regression evaluation; future changes to benchmark inputs or annotation policy should create a separately versioned benchmark rather than overwrite v2. These are curated offline behavioral results, not production accuracy estimates.

---

## 26. Testing

Run the normal unit suite with:

```bash
python -m pytest -q
```

`pytest.ini` limits normal collection to the `tests/` directory so root-level live/network diagnostic scripts are not accidentally executed as part of the standard unit suite.

At the packaging snapshot documented by the existing README, the suite reported:

```text
40 passed
```

Database migration was also tested against a copy of the existing database while preserving candidate evidence, opportunity data, and historical evidence matches.

Live external-service behavior should be validated separately because normal offline test environments may not have network access, Gmail credentials, Qwen credentials, or the required provider SDK packages.

Later patches changed Gmail lookback behavior, Agent Run progress presentation, and requirement-category robustness; the full test suite should be rerun after integrating those patches into a final release snapshot.

---

## 27. Local Setup

Create a Python 3.11+ environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configure Qwen / Alibaba Model Studio:

```bash
export DASHSCOPE_API_KEY="..."
export DASHSCOPE_BASE_URL="..."
export GENERATION_MODEL="..."
export SEARCH_MODEL="..."
export WEB_SEARCH_PROVIDER="qwen"
```

Configure Gmail OAuth as described above, then launch:

```bash
python -m streamlit run app.py
```

---

## 28. Repository Architecture

Representative module responsibilities:

```text
app.py
    Streamlit presentation and user interaction

job_agent/services/
    UI-facing orchestration / aggregate product actions

job_agent/integrations/
    provider-neutral email boundary + Gmail integration

job_agent/workflows/
    core end-to-end candidate -> opportunity workflow

job_agent/agents/
    semantic extraction, validation, resolution, matching,
    verification, reconciliation

job_agent/search/
    provider-neutral search interface and Qwen Web Search adapter

job_agent/web/
    deterministic public-page retrieval and parsing

job_agent/scoring/
    deterministic Requirement Fit, preferences, pursuit priority

job_agent/storage/
    SQLite schema, migrations, repositories, processed-email state

job_agent/models/
    domain contracts

evals/
    component and discovery evaluation assets

tests/
    deterministic unit / integration-style tests
```

---

## 29. Important Product and Engineering Decisions

### Search is for resolution, not broad discovery

The product starts from user-relevant leads already present in job-alert emails. Web Search is used to resolve those leads to a usable JD rather than searching the entire internet for arbitrary jobs.

### No embedding retrieval before semantic matching

The candidate evidence base is currently small enough that the matcher can inspect the complete validated evidence corpus. This avoids false gaps caused by an upstream Top-K retrieval step dropping complementary evidence.

### Requirement Fit is deterministic

The model decides semantic support; code calculates the score. This makes score changes traceable to either semantic labels or explicit policy weights.

### Preferences are a policy layer, not a second fit score

A user may be qualified for a job they do not prefer, or prefer a job for which their evidence is weak. Keeping these signals separate preserves interpretability.

### Historical snapshots are intentional

A JobOpportunity represents what the system concluded when that posting was analyzed. Changing a resume or preferences later does not silently rewrite history.

### Retryability is explicit

Technical failure is kept distinct from negative business conclusions. A temporary search/provider failure should not become “this job does not exist” or “the candidate is not qualified.”

### Progress UI avoids fake precision

Semantic workflows have variable cost and latency, so the UI shows understandable stages and opportunity counts rather than fabricated percentage completion.

---

## 30. Current Limitations

V1 intentionally does not solve every adjacent problem:

- exact posting-URL dedupe does not guarantee cross-site semantic dedupe
- public-page retrieval can fail on heavily protected or JavaScript-only sites
- the system can return `UNVERIFIED` when no sufficiently complete posting is found
- hosted Web Search is bounded and therefore not exhaustive
- candidate evidence quality depends on the completeness of uploaded source documents
- evidence extraction can miss valid facts embedded in long prose
- requirement extraction still has atomicity / logical-structure edge cases
- matcher quality is still being benchmarked with human-adjudicated Gold
- Requirement Fit weights and Pursuit Priority thresholds are prototype policy choices that should be calibrated against real user decisions
- preference attributes can remain `UNKNOWN` when they cannot be grounded
- the tool is local/single-user rather than a multi-tenant cloud service
- the project does not yet claim production deployment, production observability, or full production latency/cost monitoring
- V1 does not automatically tailor resumes or apply to jobs
- full real-world product validation against a no-agent baseline is still future work

---

## 31. Future Work

Potential next steps include:

- refresh Candidate Evidence Gold from this expanded README
- finalize the Requirement-Evidence Matching Gold Set and component metrics
- run an end-to-end offline benchmark to measure upstream error propagation
- compare Oracle upstream inputs vs actual extractor outputs
- add pairwise/ranking evaluation for opportunity prioritization if needed
- calibrate fit weights and priority thresholds against human decisions
- improve evidence extraction recall for long-form architecture/evaluation prose
- move source attribution toward deterministic source-block IDs for exact quote fidelity
- improve cross-site semantic dedupe while preserving precision
- expand grounded job-attribute extraction for preferences
- add production-grade observability if the tool is deployed beyond local use
- evaluate user value with time-to-review, task completion, decision confidence, usefulness, and repeat usage
- add resume-tailoring only after the user explicitly chooses to pursue an opportunity

---

## 32. What This Project Demonstrates

This project demonstrates the ability to combine AI product thinking with implementation details across the full system lifecycle:

- build a working LLM application around a real user workflow rather than a standalone demo
- integrate Gmail with metadata-first, least-privilege ingestion
- use provider-hosted Web Search as an LLM tool inside a bounded application-controlled workflow
- design precision-oriented JD resolution and semantic verification
- separate deterministic filtering from semantic judgment
- build grounded candidate-evidence and job-requirement extraction pipelines
- validate model-produced claims before downstream reasoning
- design requirement-level semantic matching with inspectable evidence
- add a second verification pass for high-risk negative conclusions
- separate model judgment from deterministic scoring policy
- design explainable fit, preference, and priority layers
- build durable state and retry semantics for partial workflow failure
- preserve historical auditability when candidate background changes
- expose human-readable evidence provenance in the product UI
- design component-level Gold Sets and offline evaluation instead of relying on demos
- identify upstream error propagation and use evaluation findings to improve architecture
- maintain direct SDK/provider abstractions without a heavy orchestration framework

---

## 33. Interview Summary

> I built an AI job-search agent that turns job-alert emails into a grounded human-review queue. The system connects to Gmail, classifies message metadata before fetching full bodies, extracts job leads, and resolves those leads to analysis-ready public job descriptions. For resolution I use a provider-neutral search layer backed by Qwen's Responses API Web Search tool, then apply deterministic URL filtering, bounded page fetching, structural validation, and LLM semantic verification. Once a posting is verified and deduplicated, the system extracts and validates atomic job requirements, compares every requirement against the candidate's complete grounded evidence base, verifies negative conclusions, and produces requirement-level support judgments with traceable evidence. Numeric Requirement Fit and Pursuit Priority are calculated deterministically, with preferences kept as a separate bounded policy layer. Completed opportunities are persisted atomically and remain historical snapshots, while the Streamlit UI lets the user inspect the reasoning and choose Pass, Save for later, or Pursue. I also built offline evaluation sets for evidence extraction, requirement extraction, and requirement-evidence matching so I can measure model behavior component by component rather than relying on end-to-end demos.

---

## 34. Current Status

The project has a working local UI and real Gmail integration, uses networked Qwen generation and hosted Web Search for live runs, performs end-to-end resolution and opportunity analysis, persists completed opportunities, and supports human review decisions.

Candidate Evidence Extraction and Job Requirement Extraction have dedicated offline evaluation workflows. Requirement-Evidence Matching evaluation is the current active evaluation focus.

Because this README now captures materially more of the implemented architecture than the previous version, the Job Agent candidate-evidence benchmark should be refreshed before the matching Gold Set is finalized.

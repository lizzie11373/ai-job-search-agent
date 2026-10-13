# AI Job Search Agent — Candidate Evidence Gold v2

**Review status:** HUMAN_REVIEWED (author-confirmed for Portfolio V1; historical analysis preserved).

This rebuild covers **only the AI Job Search Agent project**. The Resume, Deep Learning project, and RAG project Gold evidence are intentionally unchanged.

This same adjudicated evidence set has two downstream uses:

1. **Candidate Evidence Extraction evaluation** — predictions from the extractor are aligned against these human-reviewed evidence units.
2. **Requirement–Evidence Matching evaluation** — after freeze, these evidence units replace the old Job Agent evidence slice inside the fixed Candidate Evidence Base.

Evidence units in this draft: **50**.

## Selection policy

- Include candidate-relevant product, AI, engineering, evaluation, reliability, and architecture evidence.
- Preserve negative/limitation evidence when it is needed to prevent overclaiming.
- Omit low-value setup trivia and configuration details that do not materially demonstrate capability.
- Keep claims conservative and directly supported by the frozen README.
- Do not use matcher outputs or fresh extractor predictions while constructing Gold.

## Coverage by area

- AI_MATCHING: 5
- AI_PRODUCT_REASONING: 1
- AI_SAFETY_QUALITY: 4
- AI_WORKFLOW: 6
- ARCHITECTURE: 3
- DATA_STATE: 4
- ENGINEERING: 2
- EVALUATION: 4
- INTEGRATION: 1
- LIMITATION: 1
- ORCHESTRATION: 1
- PRODUCT: 2
- PRODUCT_POLICY: 1
- PRODUCT_UX: 2
- RELIABILITY: 4
- SCORING_POLICY: 3
- SEARCH: 2
- SECURITY_PRIVACY: 1
- TESTING: 1
- TOOL_CALLING: 2

## Review table

| ID | Area | Gold claim | Source lines |
|---|---|---|---:|
| `E_JOB_001` | PRODUCT | Built a local AI-assisted job-search product that turns job-alert emails into a durable, evidence-grounded human-review queue. | 3–7 |
| `E_JOB_002` | PRODUCT | Designed V1 as a human-in-the-loop decision-support system that stops at Pass / Save for later / Pursue and does not automatically tailor resumes, submit applications, contact recruiters, or make final career decisions. | 17–31 |
| `E_JOB_003` | ENGINEERING | Implemented the local product in Python 3.11+ with Streamlit for the UI and SQLite for durable local state. | 184–186 |
| `E_JOB_004` | ENGINEERING | Used the OpenAI Python SDK against an OpenAI-compatible Qwen endpoint and kept the application on direct SDK/application code without LangChain or LangGraph. | 187–192 |
| `E_JOB_005` | INTEGRATION | Integrated the Gmail API using installed-app OAuth with a read-only Gmail scope. | 234–240 |
| `E_JOB_006` | SECURITY_PRIVACY | Kept Gmail credentials and tokens local, excluded them from Git and the application database, and did not send them to the LLM. | 242–251 |
| `E_JOB_007` | ARCHITECTURE | Designed metadata-first Gmail ingestion so the system classifies message metadata before fetching full bodies and only sends relevant messages to JobCandidate extraction. | 269–282 |
| `E_JOB_008` | AI_WORKFLOW | Built email relevance classification and JobCandidate extraction that can return zero, one, or multiple leads from one job-related email, while keeping an email-derived lead distinct from a verified job posting. | 315–344 |
| `E_JOB_009` | TOOL_CALLING | Implemented a provider-neutral web-search interface backed by Qwen's Responses API hosted `web_search` tool with required tool use. | 208–228 |
| `E_JOB_010` | TOOL_CALLING | Kept hosted Web Search bounded and application-orchestrated: application code decides when search is needed, invokes one search operation, and deterministically processes returned URLs instead of running an open-ended autonomous ReAct loop. | 221–228 |
| `E_JOB_011` | ARCHITECTURE | Designed source-aware JD-resolution routing: LinkedIn/Indeed leads go directly to bounded Web Search, while other sources try the source URL once before falling back to the same search pipeline. | 350–363 |
| `E_JOB_012` | SEARCH | Built one deterministic search query from company, full title, and optional location, then calls the provider-neutral `search_web()` interface once for that search stage. | 365–373 |
| `E_JOB_013` | SEARCH | Added explicit search cost/reliability bounds: up to 30 ranked results, at most 15 page fetch attempts in batches of 5, structural validation, one semantic-verification call per usable batch, and early stopping on the first sufficiently matching and complete JD. | 381–394 |
| `E_JOB_014` | ARCHITECTURE | Separated deterministic URL filtering from semantic judgment: Python removes obvious generic/index/non-posting URLs and duplicates without performing title/company/location semantic matching. | 396–396 |
| `E_JOB_015` | RELIABILITY | Implemented page-level fault isolation so individual stale, malformed, blocked, or unfetchable search results can be skipped, while a failure of the search operation itself remains a retryable workflow-level technical failure. | 398–402 |
| `E_JOB_016` | AI_WORKFLOW | Designed LLM semantic verification to judge both consistency with the email-derived job lead and completeness for downstream requirement extraction, while tolerating reasonable title/company/location wording variants. | 404–411 |
| `E_JOB_017` | PRODUCT_POLICY | Allowed a third-party specific job page to pass verification when it is semantically consistent and sufficiently complete instead of requiring an employer-official domain. | 413–413 |
| `E_JOB_018` | RELIABILITY | Modeled JD-resolution terminal outcomes separately as VERIFIED, UNVERIFIED, and TECHNICAL_FAILURE, treating UNVERIFIED as a normal business outcome and technical failures as retryable. | 415–427 |
| `E_JOB_019` | DATA_STATE | Implemented exact resolved-posting-URL deduplication with deterministic internal opportunity IDs so retries do not duplicate already persisted opportunities. | 431–446 |
| `E_JOB_020` | DATA_STATE | Designed candidate background around one active Resume plus append-only Supporting Materials, with replacement evidence extracted and validated before the active Resume is switched. | 452–470 |
| `E_JOB_021` | DATA_STATE | Preserved historical evidence from inactive resumes through durable evidence IDs that are never reused while future matching uses only active managed sources. | 470–472 |
| `E_JOB_022` | AI_WORKFLOW | Built candidate evidence extraction into structured EvidenceUnit records containing a claim, source document/section/text, evidence type, ID, and grounding status. | 474–487 |
| `E_JOB_023` | AI_SAFETY_QUALITY | Designed the candidate-evidence extraction prompt to use only explicit facts, avoid unsupported inference or exaggerated ownership/impact/complexity, and preserve source provenance. | 489–494 |
| `E_JOB_024` | AI_SAFETY_QUALITY | Implemented candidate-evidence validation with deterministic provenance validation plus semantic grounding validation, allowing only validated evidence into CandidateEvidenceBase. | 496–505 |
| `E_JOB_025` | AI_WORKFLOW | Built atomic, grounded JobRequirement extraction from verified full job descriptions with structured IDs, category, requirement level, exact JD source text/section, and grounding status. | 513–527 |
| `E_JOB_026` | AI_WORKFLOW | Designed a requirement taxonomy covering responsibility, experience, skill, domain knowledge, education, license, certification, and other; normalized common category aliases and safely fell back unknown non-critical categories to OTHER. | 529–546 |
| `E_JOB_027` | AI_PRODUCT_REASONING | Defined EXPERIENCE semantically as prior demonstrated activity and SKILL as practical capability, rather than categorizing requirements solely from surface wording such as 'experience with X'. | 548–558 |
| `E_JOB_028` | AI_WORKFLOW | Used CORE, REQUIRED, and PREFERRED requirement levels and kept them strict because they affect downstream weighting. | 560–568 |
| `E_JOB_029` | AI_SAFETY_QUALITY | Designed requirement extraction to use only explicit JD content, avoid outside knowledge and strengthened wording, preserve DO-vs-HAVE semantics, avoid unrelated bundling, and attach exact source provenance. | 570–579 |
| `E_JOB_030` | AI_SAFETY_QUALITY | Validated extracted requirements for structure, provenance, and semantic grounding before allowing them into matching and scoring. | 581–585 |
| `E_JOB_031` | AI_MATCHING | Designed requirement-level semantic matching where each validated requirement is evaluated against the complete validated CandidateEvidenceBase to produce one RequirementEvidenceMapping, without embedding Top-K prefiltering. | 589–604 |
| `E_JOB_032` | AI_MATCHING | Defined four requirement support levels—STRONG, PARTIAL, WEAK, and NOT_CLEARLY_SUPPORTED—with explicit semantics that distinguish full support, incomplete direct support, adjacent support, and insufficient evidence. | 606–624 |
| `E_JOB_033` | AI_MATCHING | Modeled evidence relationships as DIRECT or ADJACENT and allowed DIRECT evidence to contribute to an overall PARTIAL result when another material condition is missing; NOT_CLEARLY_SUPPORTED carries no evidence matches. | 626–637 |
| `E_JOB_034` | AI_MATCHING | Allowed multiple atomic evidence units to jointly support one requirement while preventing unrelated projects from being combined to fabricate an end-to-end lifecycle that the evidence does not establish. | 639–643 |
| `E_JOB_035` | RELIABILITY | Added deterministic validation of matcher output, including exactly one mapping per requirement, known requirement/evidence IDs, valid labels, no duplicates, required reasons, and evidence/support consistency. | 645–658 |
| `E_JOB_036` | AI_MATCHING | Added a second semantic verification pass for negative or insufficient-support conclusions to search the complete evidence base for missed counter-evidence before finalizing requirement mappings. | 662–678 |
| `E_JOB_037` | SCORING_POLICY | Separated semantic matching from deterministic Requirement Fit scoring: code combines support scores with CORE/REQUIRED/PREFERRED weights and computes a normalized 0–100 fit score. | 682–719 |
| `E_JOB_038` | SCORING_POLICY | Kept user preferences separate from Requirement Fit and used them only as a bounded Pursuit Priority modifier, where mismatches can downgrade priority by at most one tier without changing the fit score. | 723–770 |
| `E_JOB_039` | SCORING_POLICY | Derived job-level Strong Matches and Main Gaps deterministically from finalized requirement mappings rather than adding a second semantic LLM judgment. | 774–792 |
| `E_JOB_040` | ORCHESTRATION | Designed Agent Run orchestration to process JobCandidates sequentially, persist each completed new opportunity immediately, and mark the parent email processed only after all of its candidates reach terminal outcomes. | 796–812 |
| `E_JOB_041` | RELIABILITY | Designed partial-progress durability and fault isolation so earlier completed opportunities survive later candidate failures, retries leave the email unprocessed, exact URL dedupe prevents duplicate saves, individual page failures can be skipped, and workflow-level failures remain visible/retryable. | 814–843 |
| `E_JOB_042` | DATA_STATE | Persisted completed opportunity state atomically in SQLite as historical snapshots, including JobOpportunity, JobRequirements, RequirementEvidenceMappings, and EvidenceMatches, while preserving referenced historical candidate evidence. | 851–890 |
| `E_JOB_043` | PRODUCT_UX | Built an inspectable Streamlit review experience with Needs Review/Reviewed queues, requirement-level explanations, grounded evidence with original source text, and human Pass / Save for later / Pursue decisions. | 922–969 |
| `E_JOB_044` | PRODUCT_UX | Simplified user-facing Agent Run progress to Checking recent emails, Processing opportunity X/Y, and Complete instead of displaying a fabricated semantic-work percentage. | 940–950 |
| `E_JOB_045` | EVALUATION | Separated software testing, AI behavioral evaluation, and product validation, and designed offline semantic evaluation to isolate model components from Gmail, Web Search, network availability, and persistence. | 1041–1056 |
| `E_JOB_046` | EVALUATION | Built a candidate-evidence extraction benchmark across four controlled documents and evaluated coverage/recall, selection/precision, semantic correctness, granularity/atomicity, grounding/source attribution, and duplication/redundancy; identified upstream recall as the largest product risk. | 1058–1082 |
| `E_JOB_047` | EVALUATION | Built and reviewed an eight-JD job-requirement extraction benchmark covering atomicity, strength language, alternatives, noise/negation, deduplication, taxonomy, and long-form prose; final v3 achieved 97.2% semantic recall, 98.1% semantic F1, 100% requirement-level accuracy, 96.0% category accuracy, and 102/102 grounding/source-fidelity passes. | 1084–1122 |
| `E_JOB_048` | EVALUATION | Designed matcher evaluation with fixed Gold JobRequirements plus fixed Gold Candidate Evidence so matcher behavior is isolated from upstream extraction errors, using one human-adjudicated Gold mapping per representative atomic requirement. | 1124–1156 |
| `E_JOB_049` | TESTING | Maintained a deterministic pytest suite; the documented packaging snapshot reported 40 passing tests, and database migration testing preserved existing candidate evidence, opportunities, and historical evidence matches. | 1175–1193 |
| `E_JOB_050` | LIMITATION | The current project is a local/single-user tool and does not claim cloud production deployment, production observability, or full production latency/cost monitoring. | 1304–1321 |

## Detailed evidence records

### E_JOB_001 — PRODUCT

**Claim:** Built a local AI-assisted job-search product that turns job-alert emails into a durable, evidence-grounded human-review queue.

**Source section:** Project overview

**Source lines:** 3–7

**Exact source text:**

```text
A local AI-assisted job-search product that turns noisy job-alert emails into a durable, evidence-grounded review queue.

The system connects to Gmail, identifies job-related messages, extracts one or more job leads, resolves each lead to a usable public job description, deduplicates already-seen postings, extracts structured job requirements, compares every requirement against a grounded candidate evidence base, calculates a deterministic fit signal, applies bounded preference logic, persists completed analyses, and lets the user decide whether to **Pass**, **Save for later**, or **Pursue**.

The product is intentionally designed as a **human-in-the-loop decision-support system**, not an autonomous application bot.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_002 — PRODUCT

**Claim:** Designed V1 as a human-in-the-loop decision-support system that stops at Pass / Save for later / Pursue and does not automatically tailor resumes, submit applications, contact recruiters, or make final career decisions.

**Source section:** Product Goal and Boundary

**Source lines:** 17–31

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_003 — ENGINEERING

**Claim:** Implemented the local product in Python 3.11+ with Streamlit for the UI and SQLite for durable local state.

**Source section:** Technology Stack

**Source lines:** 184–186

**Exact source text:**

```text
- **Python 3.11+**
- **Streamlit** for the local product UI
- **SQLite** for durable local product state
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_004 — ENGINEERING

**Claim:** Used the OpenAI Python SDK against an OpenAI-compatible Qwen endpoint and kept the application on direct SDK/application code without LangChain or LangGraph.

**Source section:** Technology Stack

**Source lines:** 187–192

**Exact source text:**

```text
- **OpenAI Python SDK** against an OpenAI-compatible Qwen / Alibaba Model Studio endpoint
- **Qwen generation models** for structured semantic tasks
- **Qwen Responses API Web Search tool** for bounded public web search
- **Gmail API** with installed-app OAuth and read-only scope
- **pytest** for deterministic unit/integration-style tests
- direct SDK / application code; no LangChain or LangGraph dependency
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_005 — INTEGRATION

**Claim:** Integrated the Gmail API using installed-app OAuth with a read-only Gmail scope.

**Source section:** Gmail Integration / OAuth and privacy boundary

**Source lines:** 234–240

**Exact source text:**

```text
### OAuth and privacy boundary

The local UI uses Google's installed-app OAuth flow with the read-only scope:

```text
https://www.googleapis.com/auth/gmail.readonly
```
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_006 — SECURITY_PRIVACY

**Claim:** Kept Gmail credentials and tokens local, excluded them from Git and the application database, and did not send them to the LLM.

**Source section:** Gmail Integration / OAuth and privacy boundary

**Source lines:** 242–251

**Exact source text:**

```text
Default local files:

```text
data/private/google_credentials.json
data/private/gmail_token.json
```

The credentials and token remain local, are excluded from Git, are not stored in the application database, and are not sent to the LLM.

The product does send the minimum application content required for semantic steps—such as email metadata for classification and relevant full email content for JobCandidate extraction—to the configured model service.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_007 — ARCHITECTURE

**Claim:** Designed metadata-first Gmail ingestion so the system classifies message metadata before fetching full bodies and only sends relevant messages to JobCandidate extraction.

**Source section:** Gmail Integration / Metadata-first ingestion

**Source lines:** 269–282

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_008 — AI_WORKFLOW

**Claim:** Built email relevance classification and JobCandidate extraction that can return zero, one, or multiple leads from one job-related email, while keeping an email-derived lead distinct from a verified job posting.

**Source section:** Email Classification and JobCandidate Extraction

**Source lines:** 315–344

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_009 — TOOL_CALLING

**Claim:** Implemented a provider-neutral web-search interface backed by Qwen's Responses API hosted `web_search` tool with required tool use.

**Source section:** LLM and Search Provider Configuration

**Source lines:** 208–228

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_010 — TOOL_CALLING

**Claim:** Kept hosted Web Search bounded and application-orchestrated: application code decides when search is needed, invokes one search operation, and deterministically processes returned URLs instead of running an open-ended autonomous ReAct loop.

**Source section:** LLM and Search Provider Configuration

**Source lines:** 221–228

**Exact source text:**

```text
The Qwen search adapter uses the Responses API with the provider-hosted Web Search tool:

```python
tools=[{"type": "web_search"}]
tool_choice="required"
```

This is a real tool-enabled LLM workflow. However, the overall application remains **bounded and application-orchestrated**: the program decides when JD resolution needs a search, invokes one search operation, then deterministically processes returned URLs. It is not an open-ended autonomous ReAct loop.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_011 — ARCHITECTURE

**Claim:** Designed source-aware JD-resolution routing: LinkedIn/Indeed leads go directly to bounded Web Search, while other sources try the source URL once before falling back to the same search pipeline.

**Source section:** JD Resolution / Source-aware routing

**Source lines:** 350–363

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_012 — SEARCH

**Claim:** Built one deterministic search query from company, full title, and optional location, then calls the provider-neutral `search_web()` interface once for that search stage.

**Source section:** JD Resolution / Search query

**Source lines:** 365–373

**Exact source text:**

```text
### Search query

The application creates one deterministic query from the strongest available lead fields, primarily:

```text
company + full title + optional location
```

The application then calls the provider-neutral `search_web()` interface exactly once for that search stage.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_013 — SEARCH

**Claim:** Added explicit search cost/reliability bounds: up to 30 ranked results, at most 15 page fetch attempts in batches of 5, structural validation, one semantic-verification call per usable batch, and early stopping on the first sufficiently matching and complete JD.

**Source section:** JD Resolution / Bounded result processing

**Source lines:** 381–394

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_014 — ARCHITECTURE

**Claim:** Separated deterministic URL filtering from semantic judgment: Python removes obvious generic/index/non-posting URLs and duplicates without performing title/company/location semantic matching.

**Source section:** JD Resolution / Bounded result processing

**Source lines:** 396–396

**Exact source text:**

```text
The deterministic URL filter removes obvious generic/index/non-posting URLs and duplicates. It deliberately avoids doing title/company/location semantic matching in Python.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_015 — RELIABILITY

**Claim:** Implemented page-level fault isolation so individual stale, malformed, blocked, or unfetchable search results can be skipped, while a failure of the search operation itself remains a retryable workflow-level technical failure.

**Source section:** JD Resolution / Page retrieval

**Source lines:** 398–402

**Exact source text:**

```text
### Page retrieval

Pages are fetched with deterministic HTTP logic. Individual stale, malformed, blocked, or otherwise unfetchable search candidates can be skipped without discarding the entire search result set.

A failure of the search operation itself is different: it is treated as a workflow-level technical failure and remains retryable.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_016 — AI_WORKFLOW

**Claim:** Designed LLM semantic verification to judge both consistency with the email-derived job lead and completeness for downstream requirement extraction, while tolerating reasonable title/company/location wording variants.

**Source section:** JD Resolution / Semantic verification boundary

**Source lines:** 404–411

**Exact source text:**

```text
### Semantic verification boundary

The semantic verifier asks two questions for each fetched page:

1. Is this page sufficiently consistent with the email-derived job lead?
2. Is the page sufficiently complete for downstream requirement extraction and fit analysis?

The verifier can tolerate reasonable company/title/location wording variants. It does not require exact string equality, the same provider job ID, or proof of exact cross-site identity.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_017 — PRODUCT_POLICY

**Claim:** Allowed a third-party specific job page to pass verification when it is semantically consistent and sufficiently complete instead of requiring an employer-official domain.

**Source section:** JD Resolution / Semantic verification boundary

**Source lines:** 413–413

**Exact source text:**

```text
A third-party specific job page can pass if it is a sufficiently consistent and complete public posting. The search-provider prompt may prefer employer/ATS pages, but the downstream acceptance boundary is **semantic consistency + sufficient JD completeness**, not “official domain or fail.”
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_018 — RELIABILITY

**Claim:** Modeled JD-resolution terminal outcomes separately as VERIFIED, UNVERIFIED, and TECHNICAL_FAILURE, treating UNVERIFIED as a normal business outcome and technical failures as retryable.

**Source section:** JD Resolution / Terminal outcomes

**Source lines:** 415–427

**Exact source text:**

```text
### Terminal outcomes

A lead can end as:

```text
VERIFIED
UNVERIFIED
TECHNICAL_FAILURE
```

`UNVERIFIED` is a normal business outcome: the agent simply does not analyze that lead further.

A technical failure is not silently converted into “no match.” It remains retryable.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_019 — DATA_STATE

**Claim:** Implemented exact resolved-posting-URL deduplication with deterministic internal opportunity IDs so retries do not duplicate already persisted opportunities.

**Source section:** Exact Posting-URL Deduplication

**Source lines:** 431–446

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_020 — DATA_STATE

**Claim:** Designed candidate background around one active Resume plus append-only Supporting Materials, with replacement evidence extracted and validated before the active Resume is switched.

**Source section:** Candidate Background and Evidence Pipeline / Managed sources

**Source lines:** 452–470

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_021 — DATA_STATE

**Claim:** Preserved historical evidence from inactive resumes through durable evidence IDs that are never reused while future matching uses only active managed sources.

**Source section:** Candidate Background and Evidence Pipeline / Managed sources

**Source lines:** 470–472

**Exact source text:**

```text
Supporting Materials remain append-only and active in V1.

Future matching uses active managed sources. Historical Job Detail pages can still hydrate evidence that came from an older inactive resume because evidence IDs remain durable and are never reused.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_022 — AI_WORKFLOW

**Claim:** Built candidate evidence extraction into structured EvidenceUnit records containing a claim, source document/section/text, evidence type, ID, and grounding status.

**Source section:** Candidate Background and Evidence Pipeline / Candidate evidence extraction

**Source lines:** 474–487

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_023 — AI_SAFETY_QUALITY

**Claim:** Designed the candidate-evidence extraction prompt to use only explicit facts, avoid unsupported inference or exaggerated ownership/impact/complexity, and preserve source provenance.

**Source section:** Candidate Background and Evidence Pipeline / Candidate evidence extraction

**Source lines:** 489–494

**Exact source text:**

```text
The extraction prompt is intentionally conservative:

- use only explicit facts from the document
- do not infer missing facts
- do not exaggerate ownership, responsibility, impact, or technical complexity
- preserve source provenance
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_024 — AI_SAFETY_QUALITY

**Claim:** Implemented candidate-evidence validation with deterministic provenance validation plus semantic grounding validation, allowing only validated evidence into CandidateEvidenceBase.

**Source section:** Candidate Background and Evidence Pipeline / Evidence validation

**Source lines:** 496–505

**Exact source text:**

```text
### Evidence validation

Evidence validation has two conceptual gates:

```text
1. deterministic provenance validation
2. semantic grounding validation
```

Only validated evidence enters `CandidateEvidenceBase` for future matching.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_025 — AI_WORKFLOW

**Claim:** Built atomic, grounded JobRequirement extraction from verified full job descriptions with structured IDs, category, requirement level, exact JD source text/section, and grounding status.

**Source section:** Job Requirement Extraction

**Source lines:** 513–527

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_026 — AI_WORKFLOW

**Claim:** Designed a requirement taxonomy covering responsibility, experience, skill, domain knowledge, education, license, certification, and other; normalized common category aliases and safely fell back unknown non-critical categories to OTHER.

**Source section:** Job Requirement Extraction / Categories

**Source lines:** 529–546

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_027 — AI_PRODUCT_REASONING

**Claim:** Defined EXPERIENCE semantically as prior demonstrated activity and SKILL as practical capability, rather than categorizing requirements solely from surface wording such as 'experience with X'.

**Source section:** Job Requirement Extraction / Categories

**Source lines:** 548–558

**Exact source text:**

```text
A useful semantic distinction used during evaluation is:

```text
EXPERIENCE
= what has the candidate previously done / demonstrated in prior activity?

SKILL
= what can the candidate use or do as a practical capability?
```

Surface wording such as “experience with X” is not enough by itself to determine the category.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_028 — AI_WORKFLOW

**Claim:** Used CORE, REQUIRED, and PREFERRED requirement levels and kept them strict because they affect downstream weighting.

**Source section:** Job Requirement Extraction / Requirement levels

**Source lines:** 560–568

**Exact source text:**

```text
### Requirement levels

```text
CORE
REQUIRED
PREFERRED
```

Requirement level is kept strict because it affects downstream weighting.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_029 — AI_SAFETY_QUALITY

**Claim:** Designed requirement extraction to use only explicit JD content, avoid outside knowledge and strengthened wording, preserve DO-vs-HAVE semantics, avoid unrelated bundling, and attach exact source provenance.

**Source section:** Job Requirement Extraction / Extraction rules

**Source lines:** 570–579

**Exact source text:**

```text
### Extraction rules

The extractor is instructed to:

- use only explicit JD content
- avoid outside knowledge
- avoid strengthening the employer's wording
- preserve “what the person will DO” vs “what the person must HAVE”
- avoid combining unrelated requirements
- attach exact source text and section provenance
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_030 — AI_SAFETY_QUALITY

**Claim:** Validated extracted requirements for structure, provenance, and semantic grounding before allowing them into matching and scoring.

**Source section:** Job Requirement Extraction / Requirement validation

**Source lines:** 581–585

**Exact source text:**

```text
### Requirement validation

Extracted requirements are checked for valid structure, source provenance, and semantic grounding before matching.

Only validated requirements participate in matching and scoring.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_031 — AI_MATCHING

**Claim:** Designed requirement-level semantic matching where each validated requirement is evaluated against the complete validated CandidateEvidenceBase to produce one RequirementEvidenceMapping, without embedding Top-K prefiltering.

**Source section:** Requirement-Evidence Matching / Evaluation unit

**Source lines:** 589–604

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_032 — AI_MATCHING

**Claim:** Defined four requirement support levels—STRONG, PARTIAL, WEAK, and NOT_CLEARLY_SUPPORTED—with explicit semantics that distinguish full support, incomplete direct support, adjacent support, and insufficient evidence.

**Source section:** Requirement-Evidence Matching / Support levels

**Source lines:** 606–624

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_033 — AI_MATCHING

**Claim:** Modeled evidence relationships as DIRECT or ADJACENT and allowed DIRECT evidence to contribute to an overall PARTIAL result when another material condition is missing; NOT_CLEARLY_SUPPORTED carries no evidence matches.

**Source section:** Requirement-Evidence Matching / Evidence relationships

**Source lines:** 626–637

**Exact source text:**

```text
### Evidence relationships

The current product/evaluation contract uses requirement-linked evidence relationships such as:

```text
DIRECT
ADJACENT
```

A `DIRECT` evidence item can still support an overall `PARTIAL` mapping when another material condition is missing—for example a numeric years-of-experience threshold or a production-deployment requirement.

For `NOT_CLEARLY_SUPPORTED`, the evidence-match list is empty.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_034 — AI_MATCHING

**Claim:** Allowed multiple atomic evidence units to jointly support one requirement while preventing unrelated projects from being combined to fabricate an end-to-end lifecycle that the evidence does not establish.

**Source section:** Requirement-Evidence Matching / Complementary evidence

**Source lines:** 639–643

**Exact source text:**

```text
### Complementary evidence

Multiple atomic evidence units may jointly support one requirement when they establish complementary parts of the required capability.

The matcher must not, however, combine unrelated projects to pretend that one specific end-to-end lifecycle occurred when the evidence does not establish that lifecycle.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_035 — RELIABILITY

**Claim:** Added deterministic validation of matcher output, including exactly one mapping per requirement, known requirement/evidence IDs, valid labels, no duplicates, required reasons, and evidence/support consistency.

**Source section:** Requirement-Evidence Matching / Structured output validation

**Source lines:** 645–658

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_036 — AI_MATCHING

**Claim:** Added a second semantic verification pass for negative or insufficient-support conclusions to search the complete evidence base for missed counter-evidence before finalizing requirement mappings.

**Source section:** Negative-Conclusion Verification and Reconciliation

**Source lines:** 662–678

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_037 — SCORING_POLICY

**Claim:** Separated semantic matching from deterministic Requirement Fit scoring: code combines support scores with CORE/REQUIRED/PREFERRED weights and computes a normalized 0–100 fit score.

**Source section:** Deterministic Requirement Fit

**Source lines:** 682–719

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_038 — SCORING_POLICY

**Claim:** Kept user preferences separate from Requirement Fit and used them only as a bounded Pursuit Priority modifier, where mismatches can downgrade priority by at most one tier without changing the fit score.

**Source section:** Preferences and Pursuit Priority

**Source lines:** 723–770

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_039 — SCORING_POLICY

**Claim:** Derived job-level Strong Matches and Main Gaps deterministically from finalized requirement mappings rather than adding a second semantic LLM judgment.

**Source section:** Strong Matches and Main Gaps

**Source lines:** 774–792

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_040 — ORCHESTRATION

**Claim:** Designed Agent Run orchestration to process JobCandidates sequentially, persist each completed new opportunity immediately, and mark the parent email processed only after all of its candidates reach terminal outcomes.

**Source section:** Agent Run Orchestration and Failure Semantics

**Source lines:** 796–812

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_041 — RELIABILITY

**Claim:** Designed partial-progress durability and fault isolation so earlier completed opportunities survive later candidate failures, retries leave the email unprocessed, exact URL dedupe prevents duplicate saves, individual page failures can be skipped, and workflow-level failures remain visible/retryable.

**Source section:** Agent Run Orchestration and Failure Semantics

**Source lines:** 814–843

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_042 — DATA_STATE

**Claim:** Persisted completed opportunity state atomically in SQLite as historical snapshots, including JobOpportunity, JobRequirements, RequirementEvidenceMappings, and EvidenceMatches, while preserving referenced historical candidate evidence.

**Source section:** Persistence and Durable Product State

**Source lines:** 851–890

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_043 — PRODUCT_UX

**Claim:** Built an inspectable Streamlit review experience with Needs Review/Reviewed queues, requirement-level explanations, grounded evidence with original source text, and human Pass / Save for later / Pursue decisions.

**Source section:** Local Streamlit UI and Job Detail Evidence Contract

**Source lines:** 922–969

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_044 — PRODUCT_UX

**Claim:** Simplified user-facing Agent Run progress to Checking recent emails, Processing opportunity X/Y, and Complete instead of displaying a fabricated semantic-work percentage.

**Source section:** Local Streamlit UI / User-facing Agent Run progress

**Source lines:** 940–950

**Exact source text:**

```text
### User-facing Agent Run progress

The latest simplified progress experience intentionally exposes only three understandable stages:

```text
1. Checking recent emails — Found N emails
2. Processing opportunity X / Y
3. Complete
```

Internal verification, analysis, and save phases still happen, but the UI does not pretend to know a meaningful percentage for semantic work.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_045 — EVALUATION

**Claim:** Separated software testing, AI behavioral evaluation, and product validation, and designed offline semantic evaluation to isolate model components from Gmail, Web Search, network availability, and persistence.

**Source section:** Evaluation Strategy

**Source lines:** 1041–1056

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_046 — EVALUATION

**Claim:** Built a candidate-evidence extraction benchmark across four controlled documents and evaluated coverage/recall, selection/precision, semantic correctness, granularity/atomicity, grounding/source attribution, and duplication/redundancy; identified upstream recall as the largest product risk.

**Source section:** Evaluation Strategy / Candidate Evidence Extraction evaluation

**Source lines:** 1058–1082

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_047 — EVALUATION

**Claim:** Built and reviewed an eight-JD job-requirement extraction benchmark covering atomicity, strength language, alternatives, noise/negation, deduplication, taxonomy, and long-form prose; final v3 achieved 97.2% semantic recall, 98.1% semantic F1, 100% requirement-level accuracy, 96.0% category accuracy, and 102/102 grounding/source-fidelity passes.

**Source section:** Evaluation Strategy / Job Requirement Extraction evaluation

**Source lines:** 1084–1122

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_048 — EVALUATION

**Claim:** Designed matcher evaluation with fixed Gold JobRequirements plus fixed Gold Candidate Evidence so matcher behavior is isolated from upstream extraction errors, using one human-adjudicated Gold mapping per representative atomic requirement.

**Source section:** Evaluation Strategy / Requirement-Evidence Matching evaluation

**Source lines:** 1124–1156

**Exact source text:**

```text
### 25.3 Requirement-Evidence Matching evaluation

The matcher benchmark isolates the matcher from upstream extraction errors:

```text
fixed Gold JobRequirements
+
fixed Gold Candidate Evidence
-> matcher
```

The benchmark design uses representative atomic requirements rather than treating eight source JDs as one synthetic job.

The initial fixed-input set was built from:

```text
90 human-reviewed candidate evidence units
32 curated atomic job requirements
```

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

Gold labels are human-adjudicated before examining a fresh matcher run to reduce anchoring/leakage.
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_049 — TESTING

**Claim:** Maintained a deterministic pytest suite; the documented packaging snapshot reported 40 passing tests, and database migration testing preserved existing candidate evidence, opportunities, and historical evidence matches.

**Source section:** Testing

**Source lines:** 1175–1193

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

### E_JOB_050 — LIMITATION

**Claim:** The current project is a local/single-user tool and does not claim cloud production deployment, production observability, or full production latency/cost monitoring.

**Source section:** Current Limitations

**Source lines:** 1304–1321

**Exact source text:**

```text
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
```

**Grounding:** VALIDATED

**Adjudication:** DRAFT_FOR_HUMAN_REVIEW

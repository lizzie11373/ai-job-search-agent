# Gold Set Output — Human-Adjudicated Requirement–Evidence Mappings

**Benchmark:** Requirement–Evidence Matching Evaluation  
**Version:** v2  
**Status:** HUMAN-ADJUDICATED GOLD  
**Requirements reviewed:** 32 / 32  
**Fixed candidate evidence:** 120 evidence units

## Purpose

This file is the expected Gold output for the matcher benchmark. For each of the 32 representative atomic requirements, it records the human-adjudicated support level, rationale, and supporting evidence mappings.

The matcher evaluation compares model-produced `RequirementEvidenceMapping` outputs against this Gold set.

## Input context

```text
120 fixed Gold Candidate Evidence units
        +
32 representative Gold Requirements
        ↓
Requirement–Evidence Matcher
        ↓
32 predicted RequirementEvidenceMappings
        ↓
Compare against this Human-Adjudicated Gold Output
```

The 120 evidence units consist of 37 synthetic benchmark-resume units, 12 Deep Learning project units, 21 RAG project units, and 50 AI Job Search Agent units.

## Gold label distribution

- STRONG: 13
- PARTIAL: 7
- WEAK: 5
- NOT_CLEARLY_SUPPORTED: 7

## Adjudication policy

- **STRONG** — direct evidence sufficiently establishes the material meaning and important qualifiers of the requirement.
- **PARTIAL** — direct substantive evidence supports an important portion, but a material condition, threshold, scope, or lifecycle qualifier is missing.
- **WEAK** — evidence is only adjacent or weakly probative; the core required condition is not established.
- **NOT_CLEARLY_SUPPORTED** — the fixed evidence base does not establish the requirement; Gold evidence matches are empty.

Additional rules used during adjudication:

- Preserve numeric thresholds; do not infer missing years.
- Preserve qualifiers such as `production`, `deployment`, and `launch`.
- For AND requirements, all material parts matter for STRONG.
- For OR requirements, satisfying one valid alternative can be STRONG.
- Do not stitch unrelated projects together to fabricate a same-product lifecycle.
- Do not use outside knowledge to strengthen evidence.
- DIRECT evidence can still result in PARTIAL overall support when another material condition is missing.

## Important human-adjudication changes

- **MREQ003:** PARTIAL → **STRONG**
- **MREQ008:** WEAK → **PARTIAL**
- **MREQ020:** WEAK → **PARTIAL**

## Final 32 Gold mappings

### MREQ001 — STRONG

**Requirement:** Partner with product and design to translate user problems into AI product requirements.

**Source provenance:** REQ001 / G004

**Gold reason:** The evidence directly shows cross-functional work with product and design on an AI-assisted workflow and separately shows user research being synthesized into explicit product requirements. Together, those facts satisfy the partnership and translation-to-requirements parts of the requirement.

**Gold evidence matches:**

- `E_RES_007` — **DIRECT**
  - Direct cross-functional work with a product manager and designer on an AI-assisted workflow.
- `E_RES_008` — **DIRECT**
  - Directly translated user research findings into explicit product requirements.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ002 — NOT_CLEARLY_SUPPORTED

**Requirement:** Have 4+ years of professional software development experience.

**Source provenance:** REQ001 / G007

**Gold reason:** The evidence base does not establish 4+ years of professional software development experience. It contains internships, research work, and substantial project implementation, but no evidence proving the required duration of professional software-development employment.

**Gold evidence matches:**

- None

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ003 — STRONG

**Requirement:** Have strong Python programming skills.

**Source provenance:** REQ001 / G008

**Gold reason:** The updated evidence now establishes substantial hands-on Python implementation rather than only Python familiarity: the candidate implemented the Job Search Agent as a Python 3.11+ product and also used Python for analysis and data work. Taken together with the implemented product scope, this is sufficient evidence for strong Python programming capability.

**Gold evidence matches:**

- `E_JOB_003` — **DIRECT**
  - Directly states that the local product was implemented in Python 3.11+.
- `E_RES_011` — **DIRECT**
  - Shows hands-on Python use for test-result analysis.
- `E_RES_026` — **DIRECT**
  - Shows additional hands-on Python use for data cleaning and descriptive statistics.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ004 — STRONG

**Requirement:** Have experience building applications with large language models or other generative AI systems.

**Source provenance:** REQ001 / G009

**Gold reason:** The candidate directly built multiple LLM-powered applications, including an adaptive RAG system and the AI Job Search Agent using an OpenAI-compatible Qwen endpoint, clearly satisfying experience building applications with LLMs or other generative AI systems.

**Gold evidence matches:**

- `E_RAG_001` — **DIRECT**
  - Directly built an adaptive RAG application.
- `E_JOB_004` — **DIRECT**
  - Directly integrated an LLM provider into the implemented Job Search Agent.
- `E_RES_031` — **DIRECT**
  - Used an LLM API in an AI classification prototype.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ005 — STRONG

**Requirement:** Have experience with vector databases.

**Source provenance:** REQ001 / G012

**Gold reason:** The candidate directly implemented semantic retrieval with ChromaDB and used ChromaDB in a working RAG workflow, clearly demonstrating practical experience with a vector database.

**Gold evidence matches:**

- `E_RAG_002` — **DIRECT**
  - Implemented embeddings and ChromaDB semantic retrieval.
- `E_RAG_003` — **DIRECT**
  - Used ChromaDB in a working Basic RAG retrieval workflow.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ006 — STRONG

**Requirement:** Have experience with prompt evaluation or LLM evaluation frameworks.

**Source provenance:** REQ001 / G013

**Gold reason:** The evidence directly shows prompt-evaluation knowledge and hands-on construction of offline LLM evaluation frameworks, including curated benchmarks, structured rubrics, and component-isolated evaluation design.

**Gold evidence matches:**

- `E_RES_035` — **DIRECT**
  - Explicitly lists prompt evaluation and offline evaluation skills.
- `E_RAG_016` — **DIRECT**
  - Built an offline evaluation runner for RAG behavior.
- `E_JOB_045` — **DIRECT**
  - Designed a layered AI evaluation strategy that isolates semantic components.
- `E_JOB_048` — **DIRECT**
  - Designed a fixed-input matcher evaluation with human-adjudicated Gold mappings.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ007 — WEAK

**Requirement:** Monitor latency and cost in production.

**Source provenance:** REQ002 / G004

**Gold reason:** The candidate has adjacent evidence of run-time traceability and explicit cost/reliability bounding, but the evidence does not establish monitoring latency and cost in a production environment. The updated Job Search Agent documentation explicitly avoids claiming full production latency/cost monitoring.

**Gold evidence matches:**

- `E_RAG_021` — **ADJACENT**
  - Records elapsed time and run traceability, but not production latency/cost monitoring.
- `E_JOB_013` — **ADJACENT**
  - Imposes explicit search cost/reliability bounds, but does not monitor production latency and cost.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ008 — PARTIAL

**Requirement:** Design tool-calling workflows that connect language models to internal APIs, search systems, and business data.

**Source provenance:** REQ002 / G005

**Gold reason:** The updated evidence directly establishes a real tool-enabled search workflow: the Job Search Agent uses Qwen's hosted web_search tool through a provider-neutral interface and application-controlled orchestration. It also integrates APIs and durable application data, but those API/data integrations are not exposed as LLM-invoked tools. Therefore the search/tool-calling portion is directly supported while the full internal-API/business-data tool-calling scope is not fully established.

**Gold evidence matches:**

- `E_JOB_009` — **DIRECT**
  - Directly implements hosted web-search tool use through a provider-neutral interface.
- `E_JOB_010` — **DIRECT**
  - Directly describes the bounded application-controlled tool orchestration.
- `E_JOB_005` — **ADJACENT**
  - Demonstrates hands-on API integration through Gmail, but the Gmail API is application-invoked rather than an LLM tool.
- `E_JOB_042` — **ADJACENT**
  - Demonstrates durable business/application data integration, but not LLM tool-calling over that data store.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ009 — PARTIAL

**Requirement:** Have at least 2 years building customer-facing AI or machine-learning applications.

**Source provenance:** REQ002 / G010

**Gold reason:** The candidate has direct evidence of building user-oriented AI systems and working on an AI-assisted B2B workflow, but the evidence does not establish at least two years of customer-facing AI or machine-learning application experience.

**Gold evidence matches:**

- `E_RAG_001` — **DIRECT**
  - Built a user-oriented AI application.
- `E_RES_007` — **DIRECT**
  - Worked on an AI-assisted B2B software workflow.
- `E_JOB_001` — **DIRECT**
  - Built another user-facing AI-assisted job-search product, but without establishing the required two-year duration.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ010 — NOT_CLEARLY_SUPPORTED

**Requirement:** Have working knowledge of TypeScript.

**Source provenance:** REQ002 / G012

**Gold reason:** The evidence base contains no explicit TypeScript experience or demonstrated TypeScript knowledge.

**Gold evidence matches:**

- None

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ011 — WEAK

**Requirement:** Have hands-on capability with REST APIs.

**Source provenance:** REQ002 / G013

**Gold reason:** The candidate has hands-on API integration and API tooling evidence, including Gmail integration, an OpenAI-compatible SDK, provider abstractions, and Postman. However, the fixed evidence does not explicitly establish hands-on capability specifically with REST APIs, so the support remains adjacent rather than direct.

**Gold evidence matches:**

- `E_JOB_005` — **ADJACENT**
  - Shows hands-on Gmail API integration, but the evidence does not explicitly characterize it as REST.
- `E_JOB_004` — **ADJACENT**
  - Shows use of an OpenAI-compatible SDK/API integration, but not explicit REST implementation.
- `E_RES_037` — **ADJACENT**
  - Lists Postman, which is relevant API tooling but does not by itself establish REST capability.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ012 — STRONG

**Requirement:** Be able to debug model failures.

**Source provenance:** REQ002 / G016

**Gold reason:** The candidate directly reviewed model-output failures, documented failure modes, and implemented validation, fallback, and verification behavior for unreliable model outputs, which clearly demonstrates the ability to debug model failures.

**Gold evidence matches:**

- `E_RES_013` — **DIRECT**
  - Documented model failure cases such as missing context, unsupported claims, and malformed output.
- `E_RES_032` — **DIRECT**
  - Reviewed and categorized LLM classification errors.
- `E_RAG_013` — **DIRECT**
  - Implemented structured model-output validation and fallback behavior.
- `E_JOB_036` — **DIRECT**
  - Added a second semantic verification pass to catch missed evidence in negative matcher conclusions.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ013 — PARTIAL

**Requirement:** Translate customer research into prioritized product requirements.

**Source provenance:** REQ003 / G003

**Gold reason:** The evidence directly shows translating user research into product requirements, and the resume separately lists prioritization as a skill, but it does not clearly show the act of prioritizing those research-derived requirements.

**Gold evidence matches:**

- `E_RES_008` — **DIRECT**
  - Directly translated user interview findings into product requirements.
- `E_RES_021` — **DIRECT**
  - Wrote product requirement notes based on research findings and analytics.
- `E_RES_034` — **ADJACENT**
  - Lists prioritization as a product skill, but does not establish prioritization of the specific research-derived requirements.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ014 — NOT_CLEARLY_SUPPORTED

**Requirement:** Have 4+ years of product management experience.

**Source provenance:** REQ003 / G006

**Gold reason:** The evidence does not establish 4+ years of product management experience. It shows internships, research, and project work, but not the required duration of product-management employment.

**Gold evidence matches:**

- None

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ015 — WEAK

**Requirement:** Have demonstrated experience shipping at least one software product from discovery through launch.

**Source provenance:** REQ003 / G007

**Gold reason:** The evidence shows discovery/research work, prototype definition, and a completed local software product, but it does not establish that one software product was taken through the full lifecycle from discovery through launch. The benchmark policy does not stitch unrelated projects together to fabricate that lifecycle.

**Gold evidence matches:**

- `E_RES_029` — **ADJACENT**
  - Shows prototype definition but not shipping through launch.
- `E_JOB_001` — **ADJACENT**
  - Shows a completed local product but not the discovery-to-launch lifecycle.
- `E_JOB_043` — **ADJACENT**
  - Shows an implemented review UI but not a launch milestone.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ016 — STRONG

**Requirement:** Be comfortable using SQL or another analytics tool to investigate product behavior.

**Source provenance:** REQ003 / G009

**Gold reason:** The candidate directly used SQL to analyze user onboarding behavior and built product analytics views for activation and retention, clearly satisfying the analytics capability requirement.

**Gold evidence matches:**

- `E_RES_016` — **DIRECT**
  - Used SQL and cohort analysis to investigate onboarding behavior.
- `E_RES_020` — **DIRECT**
  - Built a dashboard for activation and retention metrics.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ017 — STRONG

**Requirement:** Have prior work with evaluation datasets or human review workflows.

**Source provenance:** REQ003 / G012

**Gold reason:** The evidence directly demonstrates both evaluation-dataset work and human-review workflow design across multiple AI projects.

**Gold evidence matches:**

- `E_RES_010` — **DIRECT**
  - Created a labeled 60-question evaluation set.
- `E_RES_033` — **DIRECT**
  - Proposed a human-review step for low-confidence model classifications.
- `E_RAG_016` — **DIRECT**
  - Built a curated offline evaluation runner.
- `E_JOB_046` — **DIRECT**
  - Built a candidate-evidence extraction benchmark with human semantic review dimensions.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ018 — STRONG

**Requirement:** Have a Bachelor's degree in Computer Science, Data Science, Engineering, or a related field, OR equivalent practical experience.

**Source provenance:** REQ004 / G004

**Gold reason:** The candidate has a Bachelor's degree in Information Science, which is a related technical/data field and directly satisfies the degree-or-equivalent requirement.

**Gold evidence matches:**

- `E_RES_004` — **DIRECT**
  - Directly establishes a B.S. in Information Science with a Statistics minor.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ019 — NOT_CLEARLY_SUPPORTED

**Requirement:** Have experience deploying services on at least one major cloud platform: AWS, GCP, or Azure.

**Source provenance:** REQ004 / G006

**Gold reason:** The evidence base does not establish deployment of services on AWS, GCP, or Azure. The updated Job Search Agent evidence explicitly does not claim cloud production deployment.

**Gold evidence matches:**

- None

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ020 — PARTIAL

**Requirement:** Have practical capability using Git in a collaborative development environment.

**Source provenance:** REQ004 / G008

**Gold reason:** The evidence directly establishes Git and GitHub as candidate tools and separately shows collaborative work with engineers, but it does not establish that Git was actually used within that collaborative development environment.

**Gold evidence matches:**

- `E_RES_037` — **DIRECT**
  - Directly lists Git and GitHub as candidate tools, supporting practical Git capability.
- `E_RES_007` — **ADJACENT**
  - Shows collaborative work with product, design, and engineering, but does not establish Git usage in that collaboration.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ021 — NOT_CLEARLY_SUPPORTED

**Requirement:** Have practical capability with Kubernetes.

**Source provenance:** REQ004 / G010

**Gold reason:** The evidence base contains no explicit Kubernetes experience or practical Kubernetes capability.

**Gold evidence matches:**

- None

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ022 — STRONG

**Requirement:** Have familiarity with LLM evaluation, retrieval systems, or vector databases.

**Source provenance:** REQ004 / G011

**Gold reason:** The candidate has extensive direct evidence across retrieval systems, vector databases, and LLM evaluation, so the disjunctive familiarity requirement is clearly satisfied.

**Gold evidence matches:**

- `E_RAG_002` — **DIRECT**
  - Direct retrieval and vector-database implementation.
- `E_RAG_016` — **DIRECT**
  - Direct LLM/RAG evaluation work.
- `E_JOB_045` — **DIRECT**
  - Direct AI evaluation architecture work.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ023 — PARTIAL

**Requirement:** Build AI-assisted workflow features from prototype through production.

**Source provenance:** REQ005 / G001

**Gold reason:** The candidate directly built AI-assisted workflow products and prototypes, including the Job Search Agent, but the evidence does not establish taking such a feature through a production deployment. The updated Job Search Agent evidence explicitly avoids claiming production deployment.

**Gold evidence matches:**

- `E_RES_007` — **DIRECT**
  - Direct work on an AI-assisted workflow prototype.
- `E_JOB_001` — **DIRECT**
  - Directly built an AI-assisted workflow product.
- `E_JOB_040` — **DIRECT**
  - Implemented durable orchestration for the workflow, but not production deployment.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ024 — PARTIAL

**Requirement:** Interview internal users and incorporate feedback into product iterations.

**Source provenance:** REQ005 / G002

**Gold reason:** The candidate directly conducted user interviews and usability sessions and translated findings into requirements, but the evidence does not clearly establish that the users were internal users or that their feedback was incorporated through iterative product cycles.

**Gold evidence matches:**

- `E_RES_008` — **DIRECT**
  - Conducted user interviews and synthesized findings into requirements.
- `E_RES_024` — **DIRECT**
  - Helped run moderated usability sessions and organized qualitative notes.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ025 — PARTIAL

**Requirement:** Investigate production issues across application code and model behavior.

**Source provenance:** REQ005 / G004

**Gold reason:** The candidate directly investigated model-output failure modes and built application-level validation, retry, and fault-isolation behavior. However, the fixed evidence does not establish that these investigations occurred in a production environment, so the production qualifier remains unmet.

**Gold evidence matches:**

- `E_RES_013` — **DIRECT**
  - Directly documents model failure cases.
- `E_RAG_013` — **DIRECT**
  - Implements application-level validation and fallback around model behavior.
- `E_JOB_041` — **DIRECT**
  - Implements application fault isolation and retry semantics, but outside a claimed production environment.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ026 — STRONG

**Requirement:** Define success metrics and evaluation plans for new AI capabilities.

**Source provenance:** REQ006 / G004

**Gold reason:** The candidate directly defined AI quality criteria and acceptance criteria, built evaluation sets and runners, and designed explicit evaluation plans for multiple AI components, clearly satisfying the requirement.

**Gold evidence matches:**

- `E_RES_009` — **DIRECT**
  - Defined AI feature acceptance criteria including relevance, factual consistency, latency, and editability.
- `E_RES_010` — **DIRECT**
  - Created a labeled evaluation set.
- `E_RAG_016` — **DIRECT**
  - Built an offline evaluation runner.
- `E_JOB_045` — **DIRECT**
  - Designed a layered evaluation strategy.
- `E_JOB_048` — **DIRECT**
  - Designed a fixed-input matching evaluation plan.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ027 — STRONG

**Requirement:** Have strong cross-functional communication skills.

**Source provenance:** REQ006 / G007

**Gold reason:** The candidate directly demonstrates cross-functional collaboration and communication through work with product, design, engineering, and presentation of recommendations to project leadership.

**Gold evidence matches:**

- `E_RES_007` — **DIRECT**
  - Worked cross-functionally with product, design, and engineering.
- `E_RES_014` — **DIRECT**
  - Presented findings and recommendations to project leadership.
- `E_RES_036` — **DIRECT**
  - Explicitly lists stakeholder communication and cross-functional collaboration.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ028 — NOT_CLEARLY_SUPPORTED

**Requirement:** Hold an active, unrestricted Registered Nurse (RN) license in at least one U.S. state.

**Source provenance:** REQ007 / G005

**Gold reason:** The evidence base contains no evidence of an active, unrestricted U.S. Registered Nurse license.

**Gold evidence matches:**

- None

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ029 — NOT_CLEARLY_SUPPORTED

**Requirement:** Have familiarity with AI-assisted clinical decision-support tools.

**Source provenance:** REQ007 / G013

**Gold reason:** The evidence base contains no evidence of familiarity with clinical workflows or AI-assisted clinical decision-support tools.

**Gold evidence matches:**

- None

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ030 — WEAK

**Requirement:** Be comfortable leading technical discovery sessions.

**Source provenance:** REQ008 / G014

**Gold reason:** The candidate has adjacent evidence of user interviews, moderated sessions, cross-functional collaboration, and presenting recommendations, but there is no clear evidence of leading technical discovery sessions.

**Gold evidence matches:**

- `E_RES_008` — **ADJACENT**
  - Shows interview/discovery activity but not technical discovery leadership.
- `E_RES_024` — **ADJACENT**
  - Shows moderated usability sessions, not technical discovery sessions.
- `E_RES_014` — **ADJACENT**
  - Shows presentation and communication, but not leading technical discovery.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ031 — WEAK

**Requirement:** Have experience deploying LLM applications.

**Source provenance:** REQ008 / G017

**Gold reason:** The candidate clearly built LLM/RAG applications and a working local LLM-enabled product, but the evidence does not establish deployment of those LLM applications in the sense required by the job. The updated Job Search Agent evidence explicitly does not claim cloud production deployment.

**Gold evidence matches:**

- `E_RAG_001` — **ADJACENT**
  - Directly establishes building an LLM/RAG application, but not deployment.
- `E_JOB_001` — **ADJACENT**
  - Directly establishes a working local AI product, but not deployment.
- `E_JOB_004` — **ADJACENT**
  - Establishes LLM provider integration, but not deployment.

**Adjudication status:** HUMAN_ADJUDICATED

### MREQ032 — STRONG

**Requirement:** Have practical capability with retrieval-augmented generation, evaluation frameworks, or tool-calling agents.

**Source provenance:** REQ008 / G018

**Gold reason:** Because the requirement is disjunctive, practical capability in any one of RAG, evaluation frameworks, or tool-calling agents is sufficient. The candidate has direct, extensive evidence of RAG implementation, evaluation-framework work, and now also hosted web-search tool use.

**Gold evidence matches:**

- `E_RAG_003` — **DIRECT**
  - Implemented a working RAG workflow.
- `E_RAG_004` — **DIRECT**
  - Implemented an agentic RAG workflow.
- `E_RAG_016` — **DIRECT**
  - Built an evaluation runner/framework.
- `E_JOB_009` — **DIRECT**
  - Implemented hosted web-search tool use through a provider-neutral interface.

**Adjudication status:** HUMAN_ADJUDICATED

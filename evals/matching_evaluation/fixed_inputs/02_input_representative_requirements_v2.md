# Gold Set Input 02 — 32 Representative Gold Requirements

**Benchmark:** Requirement–Evidence Matching Evaluation  
**Version:** v2  
**Status:** FROZEN INPUT  
**Selected requirements:** 32  
**Source pool:** 109 Gold requirements from 8 curated JDs

## Purpose

This document is the second input to the matcher benchmark. The 32 requirements are not an exhaustive requirement corpus; they are a deliberately selected set of representative **atomic requirements** chosen for evaluation value.

## Selection rationale

The set intentionally covers difficult matcher behaviors such as numeric thresholds, strength language, AND/OR logic, production/deployment qualifiers, tool calling, direct versus adjacent evidence, credentials/licenses, domain knowledge, semantic equivalence, and clear no-evidence cases.

## Evaluation rule

Each requirement is evaluated independently as an atomic semantic matching case. `source_case_id` and `source_gold_id` preserve provenance to the original curated JD Gold Set. Because the 32 requirements come from eight different JDs, they must **not** be combined into one synthetic job-level fit score.

## Distribution

### By requirement level

- CORE: 8
- REQUIRED: 16
- PREFERRED: 8

### By category

- DOMAIN_KNOWLEDGE: 2
- EDUCATION: 1
- EXPERIENCE: 8
- LICENSE: 1
- RESPONSIBILITY: 8
- SKILL: 12

### By source JD

- REQ001: 6
- REQ002: 6
- REQ003: 5
- REQ004: 5
- REQ005: 3
- REQ006: 2
- REQ007: 2
- REQ008: 3

## Requirement records

### MREQ001

**Requirement:** Partner with product and design to translate user problems into AI product requirements.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ001

**Source Gold ID:** G004

**JD section:** Responsibilities

**Exact JD source text:**

```text
Partner with product and design to translate user problems into AI product requirements.
```

### MREQ002

**Requirement:** Have 4+ years of professional software development experience.

**Category:** EXPERIENCE

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ001

**Source Gold ID:** G007

**JD section:** Minimum Qualifications

**Exact JD source text:**

```text
4+ years of professional software development experience.
```

### MREQ003

**Requirement:** Have strong Python programming skills.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ001

**Source Gold ID:** G008

**JD section:** Minimum Qualifications

**Exact JD source text:**

```text
Strong Python programming skills.
```

### MREQ004

**Requirement:** Have experience building applications with large language models or other generative AI systems.

**Category:** EXPERIENCE

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ001

**Source Gold ID:** G009

**JD section:** Minimum Qualifications

**Exact JD source text:**

```text
Experience building applications with large language models or other generative AI systems.
```

### MREQ005

**Requirement:** Have experience with vector databases.

**Category:** SKILL

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ001

**Source Gold ID:** G012

**JD section:** Preferred Qualifications

**Exact JD source text:**

```text
Experience with vector databases.
```

### MREQ006

**Requirement:** Have experience with prompt evaluation or LLM evaluation frameworks.

**Category:** SKILL

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ001

**Source Gold ID:** G013

**JD section:** Preferred Qualifications

**Exact JD source text:**

```text
Experience with prompt evaluation or LLM evaluation frameworks.
```

### MREQ007

**Requirement:** Monitor latency and cost in production.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ002

**Source Gold ID:** G004

**JD section:** What You Will Do

**Exact JD source text:**

```text
Own the evaluation pipeline for LLM outputs and monitor latency and cost in production.
```

### MREQ008

**Requirement:** Design tool-calling workflows that connect language models to internal APIs, search systems, and business data.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ002

**Source Gold ID:** G005

**JD section:** What You Will Do

**Exact JD source text:**

```text
Design tool-calling workflows that connect language models to internal APIs, search systems, and business data.
```

### MREQ009

**Requirement:** Have at least 2 years building customer-facing AI or machine-learning applications.

**Category:** EXPERIENCE

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ002

**Source Gold ID:** G010

**JD section:** What We Need

**Exact JD source text:**

```text
5+ years of software engineering experience, including at least 2 years building customer-facing AI or machine-learning applications.
```

### MREQ010

**Requirement:** Have working knowledge of TypeScript.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ002

**Source Gold ID:** G012

**JD section:** What We Need

**Exact JD source text:**

```text
Strong proficiency in Python and working knowledge of TypeScript.
```

### MREQ011

**Requirement:** Have hands-on capability with REST APIs.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ002

**Source Gold ID:** G013

**JD section:** What We Need

**Exact JD source text:**

```text
Hands-on experience with REST APIs, structured JSON outputs, and asynchronous processing.
```

### MREQ012

**Requirement:** Be able to debug model failures.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ002

**Source Gold ID:** G016

**JD section:** What We Need

**Exact JD source text:**

```text
Ability to debug model, retrieval, and application-layer failures.
```

### MREQ013

**Requirement:** Translate customer research into prioritized product requirements.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ003

**Source Gold ID:** G003

**JD section:** What You'll Do

**Exact JD source text:**

```text
Translate customer research into prioritized product requirements.
```

### MREQ014

**Requirement:** Have 4+ years of product management experience.

**Category:** EXPERIENCE

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ003

**Source Gold ID:** G006

**JD section:** Qualifications

**Exact JD source text:**

```text
You must have 4+ years of product management experience.
```

### MREQ015

**Requirement:** Have demonstrated experience shipping at least one software product from discovery through launch.

**Category:** EXPERIENCE

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ003

**Source Gold ID:** G007

**JD section:** Qualifications

**Exact JD source text:**

```text
Demonstrated experience shipping at least one software product from discovery through launch.
```

### MREQ016

**Requirement:** Be comfortable using SQL or another analytics tool to investigate product behavior.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ003

**Source Gold ID:** G009

**JD section:** Qualifications

**Exact JD source text:**

```text
You should be comfortable using SQL or another analytics tool to investigate product behavior.
```

### MREQ017

**Requirement:** Have prior work with evaluation datasets or human review workflows.

**Category:** EXPERIENCE

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ003

**Source Gold ID:** G012

**JD section:** Additional Experience

**Exact JD source text:**

```text
Prior work with evaluation datasets or human review workflows is a plus.
```

### MREQ018

**Requirement:** Have a Bachelor's degree in Computer Science, Data Science, Engineering, or a related field, OR equivalent practical experience.

**Category:** EDUCATION

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ004

**Source Gold ID:** G004

**JD section:** Required Qualifications

**Exact JD source text:**

```text
Bachelor's degree in Computer Science, Data Science, Engineering, or a related field, OR equivalent practical experience.
```

### MREQ019

**Requirement:** Have experience deploying services on at least one major cloud platform: AWS, GCP, or Azure.

**Category:** EXPERIENCE

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ004

**Source Gold ID:** G006

**JD section:** Required Qualifications

**Exact JD source text:**

```text
Experience deploying services on at least one major cloud platform: AWS, GCP, or Azure.
```

### MREQ020

**Requirement:** Have practical capability using Git in a collaborative development environment.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ004

**Source Gold ID:** G008

**JD section:** Required Qualifications

**Exact JD source text:**

```text
Experience using Git in a collaborative development environment.
```

### MREQ021

**Requirement:** Have practical capability with Kubernetes.

**Category:** SKILL

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ004

**Source Gold ID:** G010

**JD section:** Preferred Qualifications

**Exact JD source text:**

```text
Experience with Kubernetes is preferred.
```

### MREQ022

**Requirement:** Have familiarity with LLM evaluation, retrieval systems, or vector databases.

**Category:** DOMAIN_KNOWLEDGE

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ004

**Source Gold ID:** G011

**JD section:** Preferred Qualifications

**Exact JD source text:**

```text
Familiarity with LLM evaluation, retrieval systems, or vector databases is a plus.
```

### MREQ023

**Requirement:** Build AI-assisted workflow features from prototype through production.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ005

**Source Gold ID:** G001

**JD section:** Your Work

**Exact JD source text:**

```text
Build AI-assisted workflow features from prototype through production.
```

### MREQ024

**Requirement:** Interview internal users and incorporate feedback into product iterations.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ005

**Source Gold ID:** G002

**JD section:** Your Work

**Exact JD source text:**

```text
Interview internal users and incorporate feedback into product iterations.
```

### MREQ025

**Requirement:** Investigate production issues across application code and model behavior.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ005

**Source Gold ID:** G004

**JD section:** Your Work

**Exact JD source text:**

```text
Investigate production issues across application code and model behavior.
```

### MREQ026

**Requirement:** Define success metrics and evaluation plans for new AI capabilities.

**Category:** RESPONSIBILITY

**Requirement level:** CORE

**Grounding status:** VALIDATED

**Source case:** REQ006

**Source Gold ID:** G004

**JD section:** Responsibilities

**Exact JD source text:**

```text
Define success metrics and evaluation plans for new AI capabilities.
```

### MREQ027

**Requirement:** Have strong cross-functional communication skills.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ006

**Source Gold ID:** G007

**JD section:** Minimum Qualifications

**Exact JD source text:**

```text
Strong cross-functional communication skills.
```

### MREQ028

**Requirement:** Hold an active, unrestricted Registered Nurse (RN) license in at least one U.S. state.

**Category:** LICENSE

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ007

**Source Gold ID:** G005

**JD section:** Required Qualifications

**Exact JD source text:**

```text
Active, unrestricted Registered Nurse (RN) license in at least one U.S. state.
```

### MREQ029

**Requirement:** Have familiarity with AI-assisted clinical decision-support tools.

**Category:** DOMAIN_KNOWLEDGE

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ007

**Source Gold ID:** G013

**JD section:** Preferred Qualifications

**Exact JD source text:**

```text
Familiarity with AI-assisted clinical decision-support tools is preferred.
```

### MREQ030

**Requirement:** Be comfortable leading technical discovery sessions.

**Category:** SKILL

**Requirement level:** REQUIRED

**Grounding status:** VALIDATED

**Source case:** REQ008

**Source Gold ID:** G014

**JD section:** Background We Are Looking For

**Exact JD source text:**

```text
Because this role is customer-facing, you must be comfortable leading technical discovery sessions and presenting technical recommendations to mixed technical and non-technical audiences.
```

### MREQ031

**Requirement:** Have experience deploying LLM applications.

**Category:** EXPERIENCE

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ008

**Source Gold ID:** G017

**JD section:** Background We Are Looking For

**Exact JD source text:**

```text
Experience deploying LLM applications is preferred.
```

### MREQ032

**Requirement:** Have practical capability with retrieval-augmented generation, evaluation frameworks, or tool-calling agents.

**Category:** SKILL

**Requirement level:** PREFERRED

**Grounding status:** VALIDATED

**Source case:** REQ008

**Source Gold ID:** G018

**JD section:** Background We Are Looking For

**Exact JD source text:**

```text
Experience with retrieval-augmented generation, evaluation frameworks, or tool-calling agents would be a plus.
```

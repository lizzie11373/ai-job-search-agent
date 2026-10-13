# Gold Set Input 01 — Fixed Candidate Evidence

**Benchmark:** Requirement–Evidence Matching Evaluation  
**Version:** v2  
**Status:** FROZEN INPUT  
**Total evidence units:** 120

## Purpose

This document is the first input to the matcher benchmark. The matcher receives the complete fixed candidate evidence base directly; the Evidence Extractor is **not rerun** during this component evaluation.

## Composition

| Source | Evidence units |
|---|---:|
| Synthetic benchmark resume | 37 |
| Deep Learning project | 12 |
| RAG Assistant project | 21 |
| AI Job Search Agent project | 50 |
| **Total** | **120** |

### Benchmark-resume note

The resume is a deliberately constructed realistic **synthetic benchmark candidate profile**. Its contents are treated as trusted benchmark facts for controlled evaluation. They are not claims about the project author's real employment history.

### Matching-isolation rule

```text
Fixed Gold Candidate Evidence
        +
Fixed Representative Gold Requirements
        ↓
Requirement–Evidence Matcher
```

No upstream evidence extraction is rerun in this benchmark stage.

## Synthetic Benchmark Resume

### E_RES_001

**Claim:** Earned an M.S. in Human-Computer Interaction at Western Lakes University, Sep 2024–May 2026.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Education — Western Lakes University

**Grounding status:** VALIDATED

**Source Gold ID:** G001

**Source text:**

```text
### Western Lakes University
**M.S. in Human-Computer Interaction**  
Sep 2024 – May 2026
```

### E_RES_002

**Claim:** Completed coursework in Machine Learning for Product Teams, Product Analytics, Human-AI Interaction, Experiment Design, and Data Visualization.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Education — Western Lakes University

**Grounding status:** VALIDATED

**Source Gold ID:** G002

**Source text:**

```text
- Coursework: Machine Learning for Product Teams, Product Analytics, Human-AI Interaction, Experiment Design, Data Visualization.
```

### E_RES_003

**Claim:** Completed a graduate capstone focused on evaluating user trust and task completion in an AI-assisted workflow.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Education — Western Lakes University

**Grounding status:** VALIDATED

**Source Gold ID:** G003

**Source text:**

```text
- Graduate capstone focused on evaluating user trust and task completion in an AI-assisted workflow.
```

### E_RES_004

**Claim:** Earned a B.S. in Information Science at State College of Technology, Sep 2020–May 2024, with a minor in Statistics.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Education — State College of Technology

**Grounding status:** VALIDATED

**Source Gold ID:** G004

**Source text:**

```text
### State College of Technology
**B.S. in Information Science**  
Sep 2020 – May 2024

- Minor in Statistics.
```

### E_RES_005

**Claim:** Was on the Dean’s List from 2022–2024.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Education — State College of Technology

**Grounding status:** VALIDATED

**Source Gold ID:** G005

**Source text:**

```text
- Dean’s List, 2022–2024.
```

### E_RES_006

**Claim:** Worked as an AI Product Intern at Meridian Product Studio from Jun 2025–Sep 2025.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G006

**Source text:**

```text
### AI Product Intern — Meridian Product Studio
**San Francisco, CA | Jun 2025 – Sep 2025**
```

### E_RES_007

**Claim:** Worked with a product manager, designer, and three engineers on an AI-assisted customer-support workflow for a B2B software prototype.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G007

**Source text:**

```text
- Worked with a product manager, designer, and three engineers on an AI-assisted customer-support workflow for a B2B software prototype.
```

### E_RES_008

**Claim:** Conducted 12 user interviews with support specialists and synthesized recurring pain points into four product requirements.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G008

**Source text:**

```text
- Conducted 12 user interviews with support specialists and synthesized recurring pain points into four product requirements.
```

### E_RES_009

**Claim:** Defined acceptance criteria for an AI-generated response-suggestion feature across relevance, factual consistency, response latency, and user editability.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G009

**Source text:**

```text
- Defined acceptance criteria for an AI-generated response suggestion feature, including relevance, factual consistency, response latency, and user editability.
```

### E_RES_010

**Claim:** Created a 60-question evaluation set and manually labeled expected answer topics for internal testing.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G010

**Source text:**

```text
- Created a lightweight evaluation set of 60 support questions and manually labeled expected answer topics for internal testing.
```

### E_RES_011

**Claim:** Analyzed test results in Python and spreadsheets to compare two prompt variants across answer relevance and completion rate.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G011

**Source text:**

```text
- Analyzed test results in Python and spreadsheets to compare two prompt variants across answer relevance and completion rate.
```

### E_RES_012

**Claim:** Identified a tradeoff in which one prompt improved relevance but increased response length and latency, and recommended the shorter variant for the initial pilot.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G012

**Source text:**

```text
- Identified that one prompt variant improved answer relevance but increased response length and latency; recommended keeping the shorter variant for the initial pilot.
```

### E_RES_013

**Claim:** Partnered with engineering to document failure cases involving missing context, unsupported claims, and malformed structured output.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G013

**Source text:**

```text
- Partnered with engineering to document failure cases involving missing context, unsupported claims, and malformed structured output.
```

### E_RES_014

**Claim:** Presented weekly findings and product recommendations to the project lead.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — AI Product Intern, Meridian Product Studio

**Grounding status:** VALIDATED

**Source Gold ID:** G014

**Source text:**

```text
- Presented weekly findings and product recommendations to the project lead.
```

### E_RES_015

**Claim:** Worked as a Product Analytics Intern at BrightPath Learning from Jun 2024–Aug 2024.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Product Analytics Intern, BrightPath Learning

**Grounding status:** VALIDATED

**Source Gold ID:** G015

**Source text:**

```text
### Product Analytics Intern — BrightPath Learning
**Remote | Jun 2024 – Aug 2024**
```

### E_RES_016

**Claim:** Analyzed onboarding behavior for a web-based learning product using SQL and spreadsheet-based cohort analysis.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Product Analytics Intern, BrightPath Learning

**Grounding status:** VALIDATED

**Source Gold ID:** G016

**Source text:**

```text
- Analyzed onboarding behavior for a web-based learning product using SQL and spreadsheet-based cohort analysis.
```

### E_RES_017

**Claim:** Built an onboarding funnel covering account creation, first lesson start, lesson completion, and seven-day return behavior.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Product Analytics Intern, BrightPath Learning

**Grounding status:** VALIDATED

**Source Gold ID:** G017

**Source text:**

```text
- Built a funnel covering account creation, first lesson start, lesson completion, and seven-day return behavior.
```

### E_RES_018

**Claim:** Found a large drop-off between account creation and first lesson start and worked with the product team to define hypotheses for the decline.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Product Analytics Intern, BrightPath Learning

**Grounding status:** VALIDATED

**Source Gold ID:** G018

**Source text:**

```text
- Found a large drop-off between account creation and first lesson start and worked with the product team to define hypotheses for the decline.
```

### E_RES_019

**Claim:** Helped design an A/B test comparing two onboarding flows and documented the primary metric, guardrail metrics, and experiment assumptions.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Product Analytics Intern, BrightPath Learning

**Grounding status:** VALIDATED

**Source Gold ID:** G019

**Source text:**

```text
- Helped design an A/B test comparing two onboarding flows and documented the primary metric, guardrail metrics, and experiment assumptions.
```

### E_RES_020

**Claim:** Created a dashboard summarizing activation and retention metrics for weekly product reviews.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Product Analytics Intern, BrightPath Learning

**Grounding status:** VALIDATED

**Source Gold ID:** G020

**Source text:**

```text
- Created a dashboard summarizing activation and retention metrics for weekly product reviews.
```

### E_RES_021

**Claim:** Wrote product requirement notes for an onboarding checklist based on research findings and analytics.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Product Analytics Intern, BrightPath Learning

**Grounding status:** VALIDATED

**Source Gold ID:** G021

**Source text:**

```text
- Wrote product requirement notes for an onboarding checklist based on research findings and analytics.
```

### E_RES_022

**Claim:** Worked as a Graduate Research Assistant in the Human-AI Interaction Lab at Western Lakes University from Jan 2025–May 2026.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Graduate Research Assistant, Human-AI Interaction Lab

**Grounding status:** VALIDATED

**Source Gold ID:** G022

**Source text:**

```text
### Graduate Research Assistant — Human-AI Interaction Lab, Western Lakes University
**Jan 2025 – May 2026**
```

### E_RES_023

**Claim:** Supported a study on how users interpret confidence and uncertainty in AI-generated recommendations.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Graduate Research Assistant, Human-AI Interaction Lab

**Grounding status:** VALIDATED

**Source Gold ID:** G023

**Source text:**

```text
- Supported a study on how users interpret confidence and uncertainty in AI-generated recommendations.
```

### E_RES_024

**Claim:** Prepared study materials, helped run moderated usability sessions, and organized qualitative research notes.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Graduate Research Assistant, Human-AI Interaction Lab

**Grounding status:** VALIDATED

**Source Gold ID:** G024

**Source text:**

```text
- Prepared study materials, helped run moderated usability sessions, and organized qualitative research notes.
```

### E_RES_025

**Claim:** Coded participant feedback into recurring themes related to trust, explanation quality, and willingness to verify AI output.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Graduate Research Assistant, Human-AI Interaction Lab

**Grounding status:** VALIDATED

**Source Gold ID:** G025

**Source text:**

```text
- Coded participant feedback into recurring themes related to trust, explanation quality, and willingness to verify AI output.
```

### E_RES_026

**Claim:** Used Python to clean survey data and calculate descriptive statistics.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Graduate Research Assistant, Human-AI Interaction Lab

**Grounding status:** VALIDATED

**Source Gold ID:** G026

**Source text:**

```text
- Used Python to clean survey data and calculate descriptive statistics.
```

### E_RES_027

**Claim:** Contributed to a research summary comparing user behavior across two explanation designs.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Experience — Graduate Research Assistant, Human-AI Interaction Lab

**Grounding status:** VALIDATED

**Source Gold ID:** G027

**Source text:**

```text
- Contributed to a research summary comparing user behavior across two explanation designs.
```

### E_RES_028

**Claim:** Worked on an AI Feedback Triage Prototype as a course team project in 2025.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Selected Product Work — AI Feedback Triage Prototype

**Grounding status:** VALIDATED

**Source Gold ID:** G028

**Source text:**

```text
### AI Feedback Triage Prototype
**Course Team Project | 2025**
```

### E_RES_029

**Claim:** Helped define a prototype that grouped free-form customer feedback into product themes for faster review.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Selected Product Work — AI Feedback Triage Prototype

**Grounding status:** VALIDATED

**Source Gold ID:** G029

**Source text:**

```text
- Helped define a prototype that grouped free-form customer feedback into product themes for faster review.
```

### E_RES_030

**Claim:** Wrote user stories and acceptance criteria for feedback ingestion, theme assignment, and human correction.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Selected Product Work — AI Feedback Triage Prototype

**Grounding status:** VALIDATED

**Source Gold ID:** G030

**Source text:**

```text
- Wrote user stories and acceptance criteria for feedback ingestion, theme assignment, and human correction.
```

### E_RES_031

**Claim:** Used an LLM API to test structured classification outputs on a small manually labeled dataset.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Selected Product Work — AI Feedback Triage Prototype

**Grounding status:** VALIDATED

**Source Gold ID:** G031

**Source text:**

```text
- Used an LLM API to test structured classification outputs on a small manually labeled dataset.
```

### E_RES_032

**Claim:** Reviewed classification errors and grouped them into ambiguous feedback, multi-topic feedback, and unsupported category assignment.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Selected Product Work — AI Feedback Triage Prototype

**Grounding status:** VALIDATED

**Source Gold ID:** G032

**Source text:**

```text
- Reviewed classification errors and grouped them into ambiguous feedback, multi-topic feedback, and unsupported category assignment.
```

### E_RES_033

**Claim:** Proposed a human-review step for low-confidence classifications instead of automatically accepting every model output.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Selected Product Work — AI Feedback Triage Prototype

**Grounding status:** VALIDATED

**Source Gold ID:** G033

**Source text:**

```text
- Proposed a human-review step for low-confidence classifications instead of automatically accepting every model output.
```

### E_RES_034

**Claim:** Lists product skills including product requirements, user stories, prioritization, user research, usability testing, experiment design, metric definition, product analytics, and A/B testing.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Skills — Product

**Grounding status:** VALIDATED

**Source Gold ID:** G034

**Source text:**

```text
**Product:** Product requirements, user stories, prioritization, user research, usability testing, experiment design, metric definition, product analytics, A/B testing
```

### E_RES_035

**Claim:** Lists AI/data skills including LLM APIs, prompt evaluation, basic machine learning concepts, offline evaluation, error analysis, Python, SQL, and pandas.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Skills — AI / Data

**Grounding status:** VALIDATED

**Source Gold ID:** G035

**Source text:**

```text
**AI / Data:** LLM APIs, prompt evaluation, basic machine learning concepts, offline evaluation, error analysis, Python, SQL, pandas
```

### E_RES_036

**Claim:** Lists design/collaboration skills including Figma, journey mapping, wireframing, stakeholder communication, and cross-functional collaboration.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Skills — Design / Collaboration

**Grounding status:** VALIDATED

**Source Gold ID:** G036

**Source text:**

```text
**Design / Collaboration:** Figma, journey mapping, wireframing, stakeholder communication, cross-functional collaboration
```

### E_RES_037

**Claim:** Lists tools including Git, GitHub, Jupyter Notebook, Excel / Google Sheets, Tableau, and Postman.

**Evidence type:** NOT_SCORED_V1

**Source document:** Synthetic New Grad AI Product Resume

**Source section:** Skills — Tools

**Grounding status:** VALIDATED

**Source Gold ID:** G037

**Source text:**

```text
**Tools:** Git, GitHub, Jupyter Notebook, Excel / Google Sheets, Tableau, Postman
```

## Deep Learning Project

### E_DL_001

**Claim:** Implemented a classical regression and classification pipeline from scratch, including polynomial regression, ridge regression, cross-validation, logistic regression, and gradient descent.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — Classical ML Foundations

**Grounding status:** VALIDATED

**Source Gold ID:** G001

**Source text:**

```text
| 1. [Classical ML Foundations](notebooks/01-classical-ml-foundations/README.md) | Polynomial linear regression, ridge regression, k-fold cross-validation, logistic regression, gradient descent | poly_transform, lin_reg_obj, lin_reg_fit, get_rmse, ridge_reg_fit... | Regression and classification pipeline implemented from scratch; note: the uploaded notebook still contains one stale error output and should be rerun before public release. |
```

### E_DL_002

**Claim:** Implemented a neural network from scratch with ReLU, softmax cross-entropy, forward propagation, backpropagation, and parameter updates.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — Neural Network from Scratch

**Grounding status:** VALIDATED

**Source Gold ID:** G002

**Source text:**

```text
| 2. [Neural Network from Scratch](notebooks/02-neural-network-from-scratch/README.md) | ReLU, softmax cross-entropy, forward propagation, backpropagation, parameter updates, MNIST classification | relu, relu_der, linear, linear_der, softmax_cross_entropy_loss... | MNIST subset: cost decreased from 2.303 to around 0.158; training accuracy 97.25%; testing accuracy 90.80%. |
```

### E_DL_003

**Claim:** Achieved 97.25% training accuracy and 90.80% testing accuracy on an MNIST subset with the neural-network-from-scratch implementation.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — Neural Network from Scratch

**Grounding status:** VALIDATED

**Source Gold ID:** G003

**Source text:**

```text
| 2. [Neural Network from Scratch](notebooks/02-neural-network-from-scratch/README.md) | ReLU, softmax cross-entropy, forward propagation, backpropagation, parameter updates, MNIST classification | relu, relu_der, linear, linear_der, softmax_cross_entropy_loss... | MNIST subset: cost decreased from 2.303 to around 0.158; training accuracy 97.25%; testing accuracy 90.80%. |
```

### E_DL_004

**Claim:** Implemented neural-network optimization techniques including dropout, batch normalization, mini-batch training, momentum/Adam-style optimization, and learning-rate decay.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — Neural Network Optimization Techniques

**Grounding status:** VALIDATED

**Source Gold ID:** G004

**Source text:**

```text
| 3. [Neural Network Optimization Techniques](notebooks/03-neural-network-optimization/README.md) | Dropout, batch normalization, mini-batch training, momentum/Adam-style optimization, learning-rate decay | dropout, dropout_der, batchnorm, batchnorm_der, initialize_velocity... | MNIST full dataset: network reached 96.748% training accuracy and 96.170% testing accuracy. |
```

### E_DL_005

**Claim:** Reached 96.748% training accuracy and 96.170% testing accuracy on the full MNIST dataset after applying the optimization techniques.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — Neural Network Optimization Techniques

**Grounding status:** VALIDATED

**Source Gold ID:** G005

**Source text:**

```text
| 3. [Neural Network Optimization Techniques](notebooks/03-neural-network-optimization/README.md) | Dropout, batch normalization, mini-batch training, momentum/Adam-style optimization, learning-rate decay | dropout, dropout_der, batchnorm, batchnorm_der, initialize_velocity... | MNIST full dataset: network reached 96.748% training accuracy and 96.170% testing accuracy. |
```

### E_DL_006

**Claim:** Built a PyTorch CNN image-classification pipeline using convolutional layers, batch normalization, ReLU, pooling, fully connected layers, and training/evaluation loops.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — CNN Image Classification

**Grounding status:** VALIDATED

**Source Gold ID:** G006

**Source text:**

```text
| 4. [CNN Image Classification](notebooks/04-cnn-image-classification/README.md) | Convolutional layers, batch normalization, ReLU, pooling, fully connected layers, PyTorch training/evaluation loops | Model, train_model, evaluate_model | CNN achieved 94.506% train accuracy and 91.000% test accuracy. |
```

### E_DL_007

**Claim:** Achieved 94.506% training accuracy and 91.000% test accuracy with the CNN image-classification model.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — CNN Image Classification

**Grounding status:** VALIDATED

**Source Gold ID:** G007

**Source text:**

```text
| 4. [CNN Image Classification](notebooks/04-cnn-image-classification/README.md) | Convolutional layers, batch normalization, ReLU, pooling, fully connected layers, PyTorch training/evaluation loops | Model, train_model, evaluate_model | CNN achieved 94.506% train accuracy and 91.000% test accuracy. |
```

### E_DL_008

**Claim:** Implemented and trained a GAN with generator and discriminator architectures, binary cross-entropy loss, and adversarial training.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — GAN Image Generation

**Grounding status:** VALIDATED

**Source Gold ID:** G008

**Source text:**

```text
| 5. [GAN Image Generation](notebooks/05-gan-image-generation/README.md) | Generator, discriminator, binary cross-entropy loss, adversarial training, qualitative image generation | noise, Generator, Discriminator, DLoss, GLoss | Trained a GAN with adversarial generator/discriminator losses; generated samples were tracked qualitatively across epochs. |
```

### E_DL_009

**Claim:** Tracked generated GAN samples qualitatively across training epochs.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — GAN Image Generation

**Grounding status:** VALIDATED

**Source Gold ID:** G009

**Source text:**

```text
| 5. [GAN Image Generation](notebooks/05-gan-image-generation/README.md) | Generator, discriminator, binary cross-entropy loss, adversarial training, qualitative image generation | noise, Generator, Discriminator, DLoss, GLoss | Trained a GAN with adversarial generator/discriminator losses; generated samples were tracked qualitatively across epochs. |
```

### E_DL_010

**Claim:** Implemented a domain-adversarial neural network using a feature extractor, label classifier, domain classifier, and gradient reversal for source-to-target domain adaptation.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — Domain-Adversarial Neural Network

**Grounding status:** VALIDATED

**Source Gold ID:** G010

**Source text:**

```text
| 6. [Domain-Adversarial Neural Network](notebooks/06-domain-adversarial-learning/README.md) | Feature extractor, label classifier, domain classifier, gradient reversal, source-to-target transfer | FeatureExtractor, LabelClassifier, GradReverse, DomainClassifier, calc_clf_logits... | Source-only model: source test 94.11%, target test 57.17%. With DANN: source test 85.90%, target test 62.09%, improving target-domain generalization by 4.92 percentage points. |
```

### E_DL_011

**Claim:** Improved target-domain test performance from 57.17% with the source-only model to 62.09% with DANN, a 4.92 percentage-point improvement.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Module Overview — Domain-Adversarial Neural Network

**Grounding status:** VALIDATED

**Source Gold ID:** G011

**Source text:**

```text
| 6. [Domain-Adversarial Neural Network](notebooks/06-domain-adversarial-learning/README.md) | Feature extractor, label classifier, domain classifier, gradient reversal, source-to-target transfer | FeatureExtractor, LabelClassifier, GradReverse, DomainClassifier, calc_clf_logits... | Source-only model: source test 94.11%, target test 57.17%. With DANN: source test 85.90%, target test 62.09%, improving target-domain generalization by 4.92 percentage points. |
```

### E_DL_012

**Claim:** Used an engineering workflow involving reproducible notebooks, modular source extraction, model evaluation, and experiment documentation.

**Evidence type:** NOT_SCORED_V1

**Source document:** Deep Learning Portfolio Project

**Source section:** Key Technical Skills Demonstrated

**Grounding status:** VALIDATED

**Source Gold ID:** G012

**Source text:**

```text
- Engineering workflow: reproducible notebooks, modular source extraction, model evaluation, experiment documentation
```

## RAG Assistant Project

### E_RAG_001

**Claim:** Built an adaptive retrieval-augmented generation system that helps users evaluate how their projects and experience match dynamically provided job postings.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Overview

**Grounding status:** VALIDATED

**Source Gold ID:** G001

**Source text:**

```text
An adaptive retrieval-augmented generation system that helps users evaluate how their projects and experience match dynamically provided job postings.

Users can paste any job description, role requirements, or hiring criteria and ask questions such as:

- Which of my projects best match this role?
- What evidence supports my fit for this position?
- What gaps should I address?
- How should I position a project on my resume?
- How should I explain the project in an interview?

The system does not rely on predefined job titles. Job titles, job descriptions, and hiring requirements are treated as dynamic user-provided context.
```

### E_RAG_002

**Claim:** Implemented document ingestion and chunking with source metadata, embeddings, and ChromaDB semantic retrieval.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Key Capabilities — Document Ingestion and Chunking

**Grounding status:** VALIDATED

**Source Gold ID:** G002

**Source text:**

```text
### 1. Document Ingestion and Chunking

The system loads text documents from the local knowledge base, splits them into smaller chunks, and attaches metadata such as:

- Source file
- Chunk index
- Original text

These chunks are embedded and stored in ChromaDB for semantic retrieval.
```

### E_RAG_003

**Claim:** Implemented a Basic RAG workflow using query embeddings, ChromaDB retrieval, context construction, and grounded answer generation.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Key Capabilities — Basic RAG

**Grounding status:** VALIDATED

**Source Gold ID:** G003

**Source text:**

```text
### 2. Basic RAG

Basic RAG is designed for direct factual retrieval and single-project explanation.

Example questions:

```text
What technology stack does Project 2 use?
What does Project 1 demonstrate?
Does Project 4 include PyTorch?
```

Workflow:

```text
User question
→ Query embedding
→ ChromaDB retrieval
→ Context construction
→ Grounded answer generation
```

Basic RAG does not use the intent classifier, contextual rewriting, or multi-query planning when it is manually forced for testing.
```

### E_RAG_004

**Claim:** Implemented an Agentic RAG workflow with conversation-aware rewriting, multi-query planning, retrieval, candidate merging, chunk deduplication, Qwen global reranking, evidence selection, and grounded synthesis.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Key Capabilities — Agentic RAG

**Grounding status:** VALIDATED

**Source Gold ID:** G004

**Source text:**

```text
### 3. Agentic RAG

Agentic RAG is designed for questions that require broader evidence, comparison, interpretation, or positioning.

Example questions:

```text
Which of my projects best match this job posting?
Compare Project 2 and Project 4 for this role.
What is missing from my portfolio for this position?
How should I describe Project 2 in an interview?
```

Workflow:

```text
User question
→ Conversation-aware question rewriting
→ Multi-query planning
→ Retrieval for each query
→ Candidate merging
→ Chunk deduplication
→ Qwen global reranking
→ Top-evidence selection
→ Context construction
→ Grounded answer synthesis
```
```

### E_RAG_005

**Claim:** Implemented Adaptive RAG that classifies user intent and automatically routes simple factual requests to Basic RAG and complex analytical or positioning requests to Agentic RAG.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Key Capabilities — Adaptive RAG

**Grounding status:** VALIDATED

**Source Gold ID:** G005

**Source text:**

```text
### 4. Adaptive RAG

Adaptive RAG is the default end-user experience.

The system first classifies the user's intent, then automatically selects Basic or Agentic RAG.

```text
Simple factual intent
→ Basic RAG

Complex analytical or positioning intent
→ Agentic RAG
```

This removes the burden of retrieval-strategy selection from the user.
```

### E_RAG_006

**Claim:** Designed intent classification around the user's task rather than a fixed target job role, keeping job titles and job descriptions as dynamic input.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Intent Classification

**Grounding status:** VALIDATED

**Source Gold ID:** G006

**Source text:**

```text
## Intent Classification

The classifier identifies what the user is trying to accomplish. It does not classify the user into a fixed target role.

Current intent categories:

```python
QUESTION_TYPES = [
    "factual lookup",
    "project explanation",
    "project comparison",
    "job fit analysis",
    "gap analysis",
    "resume or interview positioning",
    "risk and limitations",
]
```

### Routing Policy

```text
factual lookup
project explanation
        ↓
    Basic RAG
```

```text
project comparison
job fit analysis
gap analysis
resume or interview positioning
risk and limitations
        ↓
    Agentic RAG
```

A role name or pasted job description remains part of the user's dynamic input rather than becoming a classifier category.
```

### E_RAG_007

**Claim:** Implemented conversation-aware question rewriting using recent session messages to resolve follow-up references while preserving intent and avoiding unsupported facts.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Conversation-Aware Question Rewriting

**Grounding status:** VALIDATED

**Source Gold ID:** G007

**Source text:**

```text
## Conversation-Aware Question Rewriting

The system stores recent messages in the current Streamlit session and uses them to resolve follow-up questions.

Example:

```text
User:
Tell me about Project 2.

User:
What is missing from this project for the job above?
```

The system can rewrite the follow-up into a standalone retrieval question such as:

```text
What is missing from Project 2 for the previously provided job posting?
```

The rewriting step is designed to:

- Resolve references such as “this project,” “it,” or “the previous role”
- Preserve the user's original intent
- Avoid introducing unsupported facts
- Produce a clearer query for downstream retrieval
```

### E_RAG_008

**Claim:** Implemented multi-query retrieval with up to four search queries and three chunks per query, then merged and deduplicated candidates using source file plus chunk index.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Multi-Query Retrieval

**Grounding status:** VALIDATED

**Source Gold ID:** G008

**Source text:**

```text
Agentic RAG generates multiple search queries and retrieves evidence for each one.

With the default configuration:

```text
Up to 4 search queries
×
Up to 3 chunks per query
=
Up to 12 initial candidates before deduplication
```

Candidates are merged and deduplicated using:

```text
source file + chunk index
```
```

### E_RAG_009

**Claim:** Preserved retrieval metadata on deduplicated chunks, including matched queries, rank, distance, query-hit count, and original candidate position for debugging and evaluation.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Multi-Query Retrieval

**Grounding status:** VALIDATED

**Source Gold ID:** G009

**Source text:**

```text
A deduplicated chunk can retain:

- Every search query that retrieved it
- Its retrieval rank for each query
- Its retrieval distance for each query
- The number of query hits
- Its original candidate position

This metadata supports debugging, evaluation, and retrieval transparency.
```

### E_RAG_010

**Claim:** Implemented global reranking of the complete deduplicated candidate pool with qwen3-rerank against the standalone user question, selecting the top eight evidence chunks.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Reranking and Evidence Selection

**Grounding status:** VALIDATED

**Source Gold ID:** G010

**Source text:**

```text
## Reranking and Evidence Selection

Vector retrieval is optimized for recall, but the first retrieved candidates are not always the best evidence for the user's complete analytical task.

For Agentic RAG, the complete deduplicated candidate pool is sent to a dedicated Qwen reranker.

```text
Standalone user question
+
All deduplicated candidate chunks
        ↓
qwen3-rerank
        ↓
Global relevance scores
        ↓
Top 8 evidence chunks
        ↓
Final answer generation
```

The reranker uses the standalone user question as the ranking query rather than ranking separately against each generated search query.

This separates two responsibilities:

```text
Generated search queries
→ Expand retrieval recall

Standalone user question
→ Determine final evidence relevance
```
```

### E_RAG_011

**Claim:** Designed a full-candidate fallback that sends all deduplicated candidates to generation when reranking is unavailable, avoiding first-seen truncation and preserving recall.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Reranking and Evidence Selection — Full-Candidate Fallback

**Grounding status:** VALIDATED

**Source Gold ID:** G011

**Source text:**

```text
### Full-Candidate Fallback

Reranking is useful, but the answer pipeline should not fail only because the reranker is temporarily unavailable.

If Qwen reranking is disabled or fails:

```text
All deduplicated candidates
→ No blind truncation
→ Full candidate set is passed to the generation model
```

The fallback intentionally does not return to first-seen truncation such as:

```python
unique_chunks[:8]
```

That older approach could favor earlier search queries and drop evidence retrieved by later queries.

With the current default settings, the fallback passes at most 12 candidates before deduplication, so preserving the complete candidate set is a practical way to protect recall.

Fallback metadata includes:

- `ranking_method = "all_candidates_fallback"`
- `rerank_used = False`
- `rerank_fallback_reason`
- Exact final evidence count
```

### E_RAG_012

**Claim:** Implemented a model-provider abstraction through shared text, JSON, embedding, and reranking interfaces so core RAG logic remains separated from provider-specific APIs.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Model Provider Abstraction

**Grounding status:** VALIDATED

**Source Gold ID:** G012

**Source text:**

```text
## Model Provider Abstraction

The core RAG pipeline does not directly call a model-specific SDK.

Instead, `rag_core.py` depends on a small provider interface:

```python
call_llm_text(...)
call_llm_json(...)
get_embedding(...)
rerank_documents(...)
```

These functions are implemented in `model_provider.py`.

Current configuration:

```text
Model provider: Qwen
Generation model: qwen3.7-plus
Embedding model: text-embedding-v4
Reranker model: qwen3-rerank
Generation API style: OpenAI-compatible Chat Completions
Rerank API style: Dedicated rerank endpoint
```

### Why This Abstraction Matters

The provider layer separates:

```text
RAG business logic
from
model-specific API implementation
```

If the project later moves to a provider that does not support the OpenAI-compatible API format, the main changes should remain inside `model_provider.py`, while the core retrieval and routing logic can stay unchanged.

The abstraction does not eliminate all provider differences. JSON output, embeddings, reranking, tool calling, error handling, and model parameters may still require provider-specific implementations.
```

### E_RAG_013

**Claim:** Implemented structured model-output validation with JSON parsing, allowed-enum validation, and a rule-based fallback when intent-classifier output is invalid or the model call fails.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Structured Model Output and Validation

**Grounding status:** VALIDATED

**Source Gold ID:** G013

**Source text:**

```text
## Structured Model Output and Validation

The intent classifier requests JSON-formatted output.

However, the system does not blindly trust the model response.

The process is:

```text
Model returns JSON text
→ Python parses it with json.loads()
→ The predicted type is validated against the allowed enum
→ A rule-based fallback is used when the output is invalid or the model call fails
```

This improves robustness and prevents unsupported category names from entering the routing pipeline.
```

### E_RAG_014

**Claim:** Designed the Streamlit experience with Adaptive RAG as the default, advanced forced-mode controls for testing, and user-friendly evidence-coverage controls instead of exposing top_k directly.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Streamlit User Experience

**Grounding status:** VALIDATED

**Source Gold ID:** G014

**Source text:**

```text
## Streamlit User Experience

The project includes a Streamlit interface designed for both normal users and internal testing.

### Default Experience

The default experience uses Auto / Adaptive RAG.

Users do not need to understand or select:

- Basic RAG
- Agentic RAG
- Adaptive RAG
- `top_k`

They only need to ask a question or paste a job description.

### Advanced Controls

Advanced controls are available for debugging, evaluation, and baseline comparison.

They allow forced selection of:

- Auto / Adaptive RAG
- Basic RAG
- Agentic RAG

The UI also replaces the engineering term `top_k` with a user-friendly evidence-coverage control:

- Focused
- Balanced
- Comprehensive

These options are internally mapped to different retrieval depths.
```

### E_RAG_015

**Claim:** Implemented retrieval and reranking transparency in the UI through collapsible details such as ranking method, reranker model, fallback usage, evidence counts, matched queries, and candidate/final positions.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Streamlit User Experience — Progressive Disclosure

**Grounding status:** VALIDATED

**Source Gold ID:** G015

**Source text:**

```text
### Progressive Disclosure

The final answer remains visible by default.

Technical and supporting information is placed in collapsible sections:

- Workflow Details
- Evidence Ranking
- Evidence Overview
- Source Details
- Conversation Memory

For Agentic responses, the interface can display:

- Ranking method
- Reranker model
- Whether fallback was used
- Final evidence count
- Rerank score summary
- Matched search queries
- Candidate and final evidence positions

This keeps the main experience simple while preserving transparency for users who want to inspect the workflow.
```

### E_RAG_016

**Claim:** Built an offline evaluation runner around a curated nine-question set that runs Basic, Agentic, and Adaptive modes and records answers plus internal workflow behavior.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Evaluation Framework

**Grounding status:** VALIDATED

**Source Gold ID:** G016

**Source text:**

```text
## Evaluation Framework

The project includes an internal offline evaluation runner built around a curated nine-question test set.

The runner can execute each question in:

- Basic RAG
- Agentic RAG
- Adaptive RAG

A full run can therefore produce up to 27 mode-level results.

Each result records the final answer as well as internal workflow behavior, including:

- Conversation history
- Interpreted standalone question
- Predicted question type
- Selected strategy
- Search queries
- Retrieved chunks
- Rerank and fallback metadata
- Latency
- Errors
```

### E_RAG_017

**Claim:** Defined evaluation as two complementary dimensions: verification of intended system behavior and validation of whether resulting evidence and answers appear useful for the user task.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Evaluation Framework

**Grounding status:** VALIDATED

**Source Gold ID:** G017

**Source text:**

```text
The evaluation framework covers two complementary dimensions:

```text
Verification
→ Did the system execute according to its intended design?

Validation
→ Did the resulting evidence and answer appear useful for the user's task?
```
```

### E_RAG_018

**Claim:** Combined automatic signals with manual semantic review for evidence quality, judging relevance, specificity, sufficiency, diversity, grounding, and support strength.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Evaluation Framework — Retrieval and Evidence Evaluation

**Grounding status:** VALIDATED

**Source Gold ID:** G018

**Source text:**

```text
Required-entity coverage is checked automatically with simple string matching.

This is a lightweight heuristic. It does not fully understand aliases, paraphrases, or semantic equivalents.

Evidence quality therefore remains semi-objective:

```text
Automatic signals
+
Manual semantic review
```

Manual review considers whether the evidence is:

- Relevant
- Specific
- Sufficient
- Diverse enough for the question
- Properly grounded in the correct project
- Strong enough to support the final conclusion
```

### E_RAG_019

**Claim:** Evaluated reranking and fallback behavior using model/configuration state, fallback status and reason, evidence counts, represented queries/sources, and rerank-score summaries.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Evaluation Framework — Rerank and Fallback Evaluation

**Grounding status:** VALIDATED

**Source Gold ID:** G019

**Source text:**

```text
### 3. Rerank and Fallback Evaluation

For Agentic results, the runner records:

- Reranker model
- Whether reranking was enabled
- Ranking method
- Whether the reranker was actually used
- Whether fallback was activated
- Fallback reason
- Final evidence count
- Represented query count
- Represented source count
- Minimum, maximum, and average rerank scores

When the all-candidate fallback is used, the returned evidence count is the exact deduplicated candidate-pool size.

When Qwen reranking succeeds, the current `rag_core.py` returns only the selected evidence. The evaluation output therefore avoids claiming an exact pre-rerank candidate count when that value is not available.
```

### E_RAG_020

**Claim:** Stored structured answer-quality rubrics for human review or future LLM-as-judge across grounding, completeness, product framing, actionability, role relevance, and risk awareness, while distinguishing offline validation from full real-world product validation.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Evaluation Framework — Offline Validation and Answer-Quality Review

**Grounding status:** VALIDATED

**Source Gold ID:** G020

**Source text:**

```text
### 4. Offline Validation and Answer-Quality Review

Final answer quality has no single ground-truth answer.

The runner stores structured rubrics for human review or a future LLM-as-judge.

Example dimensions include:

- Retrieval grounding
- Answer completeness
- Product framing
- Actionability
- Role relevance
- Risk awareness

This provides initial offline validation: it evaluates whether the system appears useful on representative scenarios.

It does not yet constitute complete real-world product validation.

Stronger product validation would require target-user testing and measurable outcomes such as:

- Task completion rate
- Time saved
- User confidence
- Expert or recruiter ratings
- Repeat usage
- Improvement over a no-assistant baseline
```

### E_RAG_021

**Claim:** Recorded model and run traceability including provider, generation model, embedding model, reranker model, rerank configuration, timestamp, evaluation version, elapsed time, and errors.

**Evidence type:** NOT_SCORED_V1

**Source document:** Adaptive RAG Assistant Project

**Source section:** Evaluation Framework — Model Run Traceability

**Grounding status:** VALIDATED

**Source Gold ID:** G021

**Source text:**

```text
### 5. Model Run Traceability

Each evaluation run records:

- Model provider
- Generation model
- Embedding model
- Reranker model
- Rerank configuration
- Timestamp
- Evaluation version
- Elapsed time
- Errors

This prevents results from different model configurations from being mixed together.
```

## AI Job Search Agent Project

### E_JOB_001

**Claim:** Built a local AI-assisted job-search product that turns job-alert emails into a durable, evidence-grounded human-review queue.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Project overview

**Grounding status:** VALIDATED

**Source text:**

```text
A local AI-assisted job-search product that turns noisy job-alert emails into a durable, evidence-grounded review queue.

The system connects to Gmail, identifies job-related messages, extracts one or more job leads, resolves each lead to a usable public job description, deduplicates already-seen postings, extracts structured job requirements, compares every requirement against a grounded candidate evidence base, calculates a deterministic fit signal, applies bounded preference logic, persists completed analyses, and lets the user decide whether to **Pass**, **Save for later**, or **Pursue**.

The product is intentionally designed as a **human-in-the-loop decision-support system**, not an autonomous application bot.
```

### E_JOB_002

**Claim:** Designed V1 as a human-in-the-loop decision-support system that stops at Pass / Save for later / Pursue and does not automatically tailor resumes, submit applications, contact recruiters, or make final career decisions.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Product Goal and Boundary

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_003

**Claim:** Implemented the local product in Python 3.11+ with Streamlit for the UI and SQLite for durable local state.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Technology Stack

**Grounding status:** VALIDATED

**Source text:**

```text
- **Python 3.11+**
- **Streamlit** for the local product UI
- **SQLite** for durable local product state
```

### E_JOB_004

**Claim:** Used the OpenAI Python SDK against an OpenAI-compatible Qwen endpoint and kept the application on direct SDK/application code without LangChain or LangGraph.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Technology Stack

**Grounding status:** VALIDATED

**Source text:**

```text
- **OpenAI Python SDK** against an OpenAI-compatible Qwen / Alibaba Model Studio endpoint
- **Qwen generation models** for structured semantic tasks
- **Qwen Responses API Web Search tool** for bounded public web search
- **Gmail API** with installed-app OAuth and read-only scope
- **pytest** for deterministic unit/integration-style tests
- direct SDK / application code; no LangChain or LangGraph dependency
```

### E_JOB_005

**Claim:** Integrated the Gmail API using installed-app OAuth with a read-only Gmail scope.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Gmail Integration / OAuth and privacy boundary

**Grounding status:** VALIDATED

**Source text:**

```text
### OAuth and privacy boundary

The local UI uses Google's installed-app OAuth flow with the read-only scope:

```text
https://www.googleapis.com/auth/gmail.readonly
```
```

### E_JOB_006

**Claim:** Kept Gmail credentials and tokens local, excluded them from Git and the application database, and did not send them to the LLM.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Gmail Integration / OAuth and privacy boundary

**Grounding status:** VALIDATED

**Source text:**

```text
Default local files:

```text
data/private/google_credentials.json
data/private/gmail_token.json
```

The credentials and token remain local, are excluded from Git, are not stored in the application database, and are not sent to the LLM.

The product does send the minimum application content required for semantic steps—such as email metadata for classification and relevant full email content for JobCandidate extraction—to the configured model service.
```

### E_JOB_007

**Claim:** Designed metadata-first Gmail ingestion so the system classifies message metadata before fetching full bodies and only sends relevant messages to JobCandidate extraction.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Gmail Integration / Metadata-first ingestion

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_008

**Claim:** Built email relevance classification and JobCandidate extraction that can return zero, one, or multiple leads from one job-related email, while keeping an email-derived lead distinct from a verified job posting.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Email Classification and JobCandidate Extraction

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_009

**Claim:** Implemented a provider-neutral web-search interface backed by Qwen's Responses API hosted `web_search` tool with required tool use.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** LLM and Search Provider Configuration

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_010

**Claim:** Kept hosted Web Search bounded and application-orchestrated: application code decides when search is needed, invokes one search operation, and deterministically processes returned URLs instead of running an open-ended autonomous ReAct loop.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** LLM and Search Provider Configuration

**Grounding status:** VALIDATED

**Source text:**

```text
The Qwen search adapter uses the Responses API with the provider-hosted Web Search tool:

```python
tools=[{"type": "web_search"}]
tool_choice="required"
```

This is a real tool-enabled LLM workflow. However, the overall application remains **bounded and application-orchestrated**: the program decides when JD resolution needs a search, invokes one search operation, then deterministically processes returned URLs. It is not an open-ended autonomous ReAct loop.
```

### E_JOB_011

**Claim:** Designed source-aware JD-resolution routing: LinkedIn/Indeed leads go directly to bounded Web Search, while other sources try the source URL once before falling back to the same search pipeline.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Source-aware routing

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_012

**Claim:** Built one deterministic search query from company, full title, and optional location, then calls the provider-neutral `search_web()` interface once for that search stage.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Search query

**Grounding status:** VALIDATED

**Source text:**

```text
### Search query

The application creates one deterministic query from the strongest available lead fields, primarily:

```text
company + full title + optional location
```

The application then calls the provider-neutral `search_web()` interface exactly once for that search stage.
```

### E_JOB_013

**Claim:** Added explicit search cost/reliability bounds: up to 30 ranked results, at most 15 page fetch attempts in batches of 5, structural validation, one semantic-verification call per usable batch, and early stopping on the first sufficiently matching and complete JD.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Bounded result processing

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_014

**Claim:** Separated deterministic URL filtering from semantic judgment: Python removes obvious generic/index/non-posting URLs and duplicates without performing title/company/location semantic matching.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Bounded result processing

**Grounding status:** VALIDATED

**Source text:**

```text
The deterministic URL filter removes obvious generic/index/non-posting URLs and duplicates. It deliberately avoids doing title/company/location semantic matching in Python.
```

### E_JOB_015

**Claim:** Implemented page-level fault isolation so individual stale, malformed, blocked, or unfetchable search results can be skipped, while a failure of the search operation itself remains a retryable workflow-level technical failure.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Page retrieval

**Grounding status:** VALIDATED

**Source text:**

```text
### Page retrieval

Pages are fetched with deterministic HTTP logic. Individual stale, malformed, blocked, or otherwise unfetchable search candidates can be skipped without discarding the entire search result set.

A failure of the search operation itself is different: it is treated as a workflow-level technical failure and remains retryable.
```

### E_JOB_016

**Claim:** Designed LLM semantic verification to judge both consistency with the email-derived job lead and completeness for downstream requirement extraction, while tolerating reasonable title/company/location wording variants.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Semantic verification boundary

**Grounding status:** VALIDATED

**Source text:**

```text
### Semantic verification boundary

The semantic verifier asks two questions for each fetched page:

1. Is this page sufficiently consistent with the email-derived job lead?
2. Is the page sufficiently complete for downstream requirement extraction and fit analysis?

The verifier can tolerate reasonable company/title/location wording variants. It does not require exact string equality, the same provider job ID, or proof of exact cross-site identity.
```

### E_JOB_017

**Claim:** Allowed a third-party specific job page to pass verification when it is semantically consistent and sufficiently complete instead of requiring an employer-official domain.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Semantic verification boundary

**Grounding status:** VALIDATED

**Source text:**

```text
A third-party specific job page can pass if it is a sufficiently consistent and complete public posting. The search-provider prompt may prefer employer/ATS pages, but the downstream acceptance boundary is **semantic consistency + sufficient JD completeness**, not “official domain or fail.”
```

### E_JOB_018

**Claim:** Modeled JD-resolution terminal outcomes separately as VERIFIED, UNVERIFIED, and TECHNICAL_FAILURE, treating UNVERIFIED as a normal business outcome and technical failures as retryable.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** JD Resolution / Terminal outcomes

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_019

**Claim:** Implemented exact resolved-posting-URL deduplication with deterministic internal opportunity IDs so retries do not duplicate already persisted opportunities.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Exact Posting-URL Deduplication

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_020

**Claim:** Designed candidate background around one active Resume plus append-only Supporting Materials, with replacement evidence extracted and validated before the active Resume is switched.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Candidate Background and Evidence Pipeline / Managed sources

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_021

**Claim:** Preserved historical evidence from inactive resumes through durable evidence IDs that are never reused while future matching uses only active managed sources.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Candidate Background and Evidence Pipeline / Managed sources

**Grounding status:** VALIDATED

**Source text:**

```text
Supporting Materials remain append-only and active in V1.

Future matching uses active managed sources. Historical Job Detail pages can still hydrate evidence that came from an older inactive resume because evidence IDs remain durable and are never reused.
```

### E_JOB_022

**Claim:** Built candidate evidence extraction into structured EvidenceUnit records containing a claim, source document/section/text, evidence type, ID, and grounding status.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Candidate Background and Evidence Pipeline / Candidate evidence extraction

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_023

**Claim:** Designed the candidate-evidence extraction prompt to use only explicit facts, avoid unsupported inference or exaggerated ownership/impact/complexity, and preserve source provenance.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Candidate Background and Evidence Pipeline / Candidate evidence extraction

**Grounding status:** VALIDATED

**Source text:**

```text
The extraction prompt is intentionally conservative:

- use only explicit facts from the document
- do not infer missing facts
- do not exaggerate ownership, responsibility, impact, or technical complexity
- preserve source provenance
```

### E_JOB_024

**Claim:** Implemented candidate-evidence validation with deterministic provenance validation plus semantic grounding validation, allowing only validated evidence into CandidateEvidenceBase.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Candidate Background and Evidence Pipeline / Evidence validation

**Grounding status:** VALIDATED

**Source text:**

```text
### Evidence validation

Evidence validation has two conceptual gates:

```text
1. deterministic provenance validation
2. semantic grounding validation
```

Only validated evidence enters `CandidateEvidenceBase` for future matching.
```

### E_JOB_025

**Claim:** Built atomic, grounded JobRequirement extraction from verified full job descriptions with structured IDs, category, requirement level, exact JD source text/section, and grounding status.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Job Requirement Extraction

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_026

**Claim:** Designed a requirement taxonomy covering responsibility, experience, skill, domain knowledge, education, license, certification, and other; normalized common category aliases and safely fell back unknown non-critical categories to OTHER.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Job Requirement Extraction / Categories

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_027

**Claim:** Defined EXPERIENCE semantically as prior demonstrated activity and SKILL as practical capability, rather than categorizing requirements solely from surface wording such as 'experience with X'.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Job Requirement Extraction / Categories

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_028

**Claim:** Used CORE, REQUIRED, and PREFERRED requirement levels and kept them strict because they affect downstream weighting.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Job Requirement Extraction / Requirement levels

**Grounding status:** VALIDATED

**Source text:**

```text
### Requirement levels

```text
CORE
REQUIRED
PREFERRED
```

Requirement level is kept strict because it affects downstream weighting.
```

### E_JOB_029

**Claim:** Designed requirement extraction to use only explicit JD content, avoid outside knowledge and strengthened wording, preserve DO-vs-HAVE semantics, avoid unrelated bundling, and attach exact source provenance.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Job Requirement Extraction / Extraction rules

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_030

**Claim:** Validated extracted requirements for structure, provenance, and semantic grounding before allowing them into matching and scoring.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Job Requirement Extraction / Requirement validation

**Grounding status:** VALIDATED

**Source text:**

```text
### Requirement validation

Extracted requirements are checked for valid structure, source provenance, and semantic grounding before matching.

Only validated requirements participate in matching and scoring.
```

### E_JOB_031

**Claim:** Designed requirement-level semantic matching where each validated requirement is evaluated against the complete validated CandidateEvidenceBase to produce one RequirementEvidenceMapping, without embedding Top-K prefiltering.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Requirement-Evidence Matching / Evaluation unit

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_032

**Claim:** Defined four requirement support levels—STRONG, PARTIAL, WEAK, and NOT_CLEARLY_SUPPORTED—with explicit semantics that distinguish full support, incomplete direct support, adjacent support, and insufficient evidence.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Requirement-Evidence Matching / Support levels

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_033

**Claim:** Modeled evidence relationships as DIRECT or ADJACENT and allowed DIRECT evidence to contribute to an overall PARTIAL result when another material condition is missing; NOT_CLEARLY_SUPPORTED carries no evidence matches.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Requirement-Evidence Matching / Evidence relationships

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_034

**Claim:** Allowed multiple atomic evidence units to jointly support one requirement while preventing unrelated projects from being combined to fabricate an end-to-end lifecycle that the evidence does not establish.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Requirement-Evidence Matching / Complementary evidence

**Grounding status:** VALIDATED

**Source text:**

```text
### Complementary evidence

Multiple atomic evidence units may jointly support one requirement when they establish complementary parts of the required capability.

The matcher must not, however, combine unrelated projects to pretend that one specific end-to-end lifecycle occurred when the evidence does not establish that lifecycle.
```

### E_JOB_035

**Claim:** Added deterministic validation of matcher output, including exactly one mapping per requirement, known requirement/evidence IDs, valid labels, no duplicates, required reasons, and evidence/support consistency.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Requirement-Evidence Matching / Structured output validation

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_036

**Claim:** Added a second semantic verification pass for negative or insufficient-support conclusions to search the complete evidence base for missed counter-evidence before finalizing requirement mappings.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Negative-Conclusion Verification and Reconciliation

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_037

**Claim:** Separated semantic matching from deterministic Requirement Fit scoring: code combines support scores with CORE/REQUIRED/PREFERRED weights and computes a normalized 0–100 fit score.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Deterministic Requirement Fit

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_038

**Claim:** Kept user preferences separate from Requirement Fit and used them only as a bounded Pursuit Priority modifier, where mismatches can downgrade priority by at most one tier without changing the fit score.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Preferences and Pursuit Priority

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_039

**Claim:** Derived job-level Strong Matches and Main Gaps deterministically from finalized requirement mappings rather than adding a second semantic LLM judgment.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Strong Matches and Main Gaps

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_040

**Claim:** Designed Agent Run orchestration to process JobCandidates sequentially, persist each completed new opportunity immediately, and mark the parent email processed only after all of its candidates reach terminal outcomes.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Agent Run Orchestration and Failure Semantics

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_041

**Claim:** Designed partial-progress durability and fault isolation so earlier completed opportunities survive later candidate failures, retries leave the email unprocessed, exact URL dedupe prevents duplicate saves, individual page failures can be skipped, and workflow-level failures remain visible/retryable.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Agent Run Orchestration and Failure Semantics

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_042

**Claim:** Persisted completed opportunity state atomically in SQLite as historical snapshots, including JobOpportunity, JobRequirements, RequirementEvidenceMappings, and EvidenceMatches, while preserving referenced historical candidate evidence.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Persistence and Durable Product State

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_043

**Claim:** Built an inspectable Streamlit review experience with Needs Review/Reviewed queues, requirement-level explanations, grounded evidence with original source text, and human Pass / Save for later / Pursue decisions.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Local Streamlit UI and Job Detail Evidence Contract

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_044

**Claim:** Simplified user-facing Agent Run progress to Checking recent emails, Processing opportunity X/Y, and Complete instead of displaying a fabricated semantic-work percentage.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Local Streamlit UI / User-facing Agent Run progress

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_045

**Claim:** Separated software testing, AI behavioral evaluation, and product validation, and designed offline semantic evaluation to isolate model components from Gmail, Web Search, network availability, and persistence.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Evaluation Strategy

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_046

**Claim:** Built a candidate-evidence extraction benchmark across four controlled documents and evaluated coverage/recall, selection/precision, semantic correctness, granularity/atomicity, grounding/source attribution, and duplication/redundancy; identified upstream recall as the largest product risk.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Evaluation Strategy / Candidate Evidence Extraction evaluation

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_047

**Claim:** Built and reviewed an eight-JD job-requirement extraction benchmark covering atomicity, strength language, alternatives, noise/negation, deduplication, taxonomy, and long-form prose; final v3 achieved 97.2% semantic recall, 98.1% semantic F1, 100% requirement-level accuracy, 96.0% category accuracy, and 102/102 grounding/source-fidelity passes.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Evaluation Strategy / Job Requirement Extraction evaluation

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_048

**Claim:** Designed matcher evaluation with fixed Gold JobRequirements plus fixed Gold Candidate Evidence so matcher behavior is isolated from upstream extraction errors, using one human-adjudicated Gold mapping per representative atomic requirement.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Evaluation Strategy / Requirement-Evidence Matching evaluation

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_049

**Claim:** Maintained a deterministic pytest suite; the documented packaging snapshot reported 40 passing tests, and database migration testing preserved existing candidate evidence, opportunities, and historical evidence matches.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Testing

**Grounding status:** VALIDATED

**Source text:**

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

### E_JOB_050

**Claim:** The current project is a local/single-user tool and does not claim cloud production deployment, production observability, or full production latency/cost monitoring.

**Evidence type:** PROJECT

**Source document:** README_AI_Job_Search_Agent_COMPLETE.md

**Source section:** Current Limitations

**Grounding status:** VALIDATED

**Source text:**

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

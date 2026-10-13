# AI Career Knowledge Assistant

An adaptive retrieval-augmented generation system that helps users evaluate how their projects and experience match dynamically provided job postings.

Users can paste any job description, role requirements, or hiring criteria and ask questions such as:

- Which of my projects best match this role?
- What evidence supports my fit for this position?
- What gaps should I address?
- How should I position a project on my resume?
- How should I explain the project in an interview?

The system does not rely on predefined job titles. Job titles, job descriptions, and hiring requirements are treated as dynamic user-provided context.

---

## Project Overview

Many RAG applications use the same retrieval workflow for every question. This project takes a different approach.

Simple factual questions may only require a direct semantic search over the knowledge base. More complex questions—such as job-fit analysis, project comparison, gap analysis, or resume positioning—benefit from contextual rewriting, multiple search queries, broader retrieval, and answer synthesis.

To support both cases, this project combines:

- Basic RAG
- Agentic multi-query retrieval
- Conversation-aware question rewriting
- Intent classification
- Adaptive routing
- Dedicated Qwen reranking
- Full-candidate fallback when reranking is unavailable
- Retrieval transparency
- Verification and offline validation
- Model-provider abstraction
- A Streamlit user interface

The result is an assistant that automatically selects the appropriate retrieval strategy based on the user's intent.

---

## Primary Use Case

The intended workflow is:

```text
The user finds a new job posting
        ↓
The user pastes the job description or requirements
        ↓
The system classifies the user's intent
        ↓
The system automatically selects Basic or Agentic RAG
        ↓
The system retrieves evidence from the user's project knowledge base
        ↓
Complex queries are globally reranked against the standalone user question
        ↓
The system provides grounded job-fit, gap, resume, or interview analysis
```

The assistant is job-posting-aware, but not job-title-dependent.

A newly discovered role such as AI Solutions Consultant, Technical Product Manager, Forward Deployed Engineer, or any other position can be analyzed without adding a new predefined category.

---

## Key Capabilities

### 1. Document Ingestion and Chunking

The system loads text documents from the local knowledge base, splits them into smaller chunks, and attaches metadata such as:

- Source file
- Chunk index
- Original text

These chunks are embedded and stored in ChromaDB for semantic retrieval.

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

---

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

---

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

---

## Multi-Query Retrieval

A single semantic query may not retrieve all evidence needed for complex career analysis.

For example, a job-fit question may require evidence about:

- Technical implementation
- Product thinking
- Evaluation
- User experience
- Stakeholder communication
- Business impact
- Risks and limitations

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

A deduplicated chunk can retain:

- Every search query that retrieved it
- Its retrieval rank for each query
- Its retrieval distance for each query
- The number of query hits
- Its original candidate position

This metadata supports debugging, evaluation, and retrieval transparency.

---

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

Each selected chunk can record:

- `rerank_score`
- `rerank_used`
- `ranking_method`
- `original_candidate_position`
- `reranked_position`
- `final_evidence_position`

A rerank score measures query-document relevance. It is not a confidence score for factual correctness.

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

---

## Knowledge Base and Vector Search

The project uses:

- Local text files as the knowledge base
- Embeddings for semantic representation
- ChromaDB for vector storage and retrieval
- Persistent local storage for the vector database

The ingestion pipeline is:

```text
Load documents
→ Split text into chunks
→ Generate embeddings
→ Store vectors and metadata in ChromaDB
```

Changing the embedding model requires rebuilding the vector database because different models may use different vector dimensions and semantic spaces.

---

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

---

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

---

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

---

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

The evaluation framework covers two complementary dimensions:

```text
Verification
→ Did the system execute according to its intended design?

Validation
→ Did the resulting evidence and answer appear useful for the user's task?
```

### 1. Verification

Verification focuses on system and workflow correctness.

The runner records:

- `expected_question_type`
- `predicted_question_type`
- `question_type_match`
- `expected_strategy`
- `selected_strategy`
- `strategy_match`
- `interpreted_question`
- `ranking_method`
- `rerank_used`
- `fallback_used`
- Errors and elapsed time

`expected_question_type` is human-labeled ground truth for the curated evaluation set.

`expected_strategy` is derived from the current routing policy.

A successful routing check proves that the implementation followed the current policy. It does not by itself prove that the policy is the best possible product design.

### 2. Retrieval and Evidence Evaluation

The evaluation runner records:

- Required entities
- Entity string-match checks
- Entity coverage ratio
- Desired evidence topics
- Matched queries
- Retrieved chunks
- Source metadata
- Retrieval distances
- Query-hit counts
- Rerank scores
- Candidate and final evidence positions

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

---

## Project Structure

```text
RAG-project/
├── app.py
├── rag_core.py
├── model_provider.py
├── eval_questions.py
├── eval_runner.py
├── data/
├── chroma_db/
├── eval_results/
├── .env
└── README.md
```

### Main Files

#### `app.py`

Streamlit user interface, session memory, adaptive-mode defaults, advanced controls, evidence display, and progressive disclosure.

#### `rag_core.py`

Document loading, chunking, ingestion, retrieval, question classification, routing, contextual rewriting, multi-query planning, candidate deduplication, reranking integration, fallback behavior, and answer generation.

#### `model_provider.py`

Provider configuration and shared interfaces for text generation, structured JSON output, embeddings, and Qwen reranking.

#### `eval_questions.py`

Evaluation scenarios, human-labeled expected question types, evidence expectations, and answer-quality rubrics.

#### `eval_runner.py`

Runs Basic, Agentic, and Adaptive workflows and saves structured verification, evidence, rerank, fallback, and answer-review results.

---

## Technology Stack

- Python
- Streamlit
- ChromaDB
- Qwen / Alibaba Model Studio
- OpenAI Python SDK for the OpenAI-compatible generation API
- HTTPX for the dedicated rerank endpoint
- python-dotenv
- JSON-based evaluation artifacts

---

## Setup

### 1. Create and Activate a Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install streamlit chromadb openai httpx python-dotenv
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
MODEL_PROVIDER=qwen
DASHSCOPE_API_KEY=your_api_key

DASHSCOPE_BASE_URL=your_openai_compatible_generation_endpoint
GENERATION_MODEL=qwen3.7-plus
EMBEDDING_MODEL=text-embedding-v4

RERANK_ENABLED=true
RERANK_MODEL=qwen3-rerank
DASHSCOPE_RERANK_URL=your_dedicated_rerank_endpoint
RERANK_TIMEOUT_SECONDS=60
RERANK_INSTRUCT=Given a career-analysis question or job description, rank project evidence by how directly it helps answer the user's main question.
```

Do not commit the real `.env` file or API key to GitHub.

### 4. Build the Vector Database

Run this after adding or changing documents, or after changing the embedding model:

```bash
rm -rf chroma_db
python -c "from rag_core import ingest_documents; count = ingest_documents(reset=True); print('Stored chunks:', count)"
```

### 5. Run the Streamlit Application

```bash
streamlit run app.py
```

### 6. Run the Evaluation Suite

```bash
python eval_runner.py
```

Evaluation results are saved as timestamped JSON files under `eval_results/`.

To test the full-candidate fallback, temporarily set:

```env
RERANK_ENABLED=false
```

Restart the Python or Streamlit process before rerunning the test so that the updated environment variables are loaded.

---

## Example Questions

### Factual Lookup

```text
What technology stack does Project 2 use?
```

### Project Explanation

```text
What does Project 1 demonstrate?
```

### Project Comparison

```text
Compare Project 2 and Project 4.
```

### Dynamic Job-Fit Analysis

```text
Here is a job posting. Which of my projects best match its requirements?
```

### Gap Analysis

```text
What is missing from my portfolio for this role?
```

### Resume Positioning

```text
How should I describe Project 2 on my resume for this job?
```

### Interview Positioning

```text
How should I explain this project in a one-minute interview answer?
```

### Risk and Limitations

```text
What limitations or guardrails should I mention when discussing this project?
```

---

## Key Product and Engineering Decisions

### Adaptive Routing Instead of User-Selected Routing

The first UI version exposed Basic, Agentic, and Adaptive RAG as equal user choices.

This created a product problem: a user could select Basic RAG and then ask a complex job-fit question, unintentionally limiting the system's capabilities.

The final design makes Adaptive RAG the default. Forced Basic and Agentic modes remain available only under advanced controls for debugging and evaluation.

### Dynamic Job Context Instead of Predefined Roles

Earlier classifier categories mixed user intent with target roles.

The final taxonomy separates them:

```text
User intent
≠
Target job title
```

Job titles and JD requirements are dynamic inputs. The classifier only determines whether the user wants factual retrieval, job-fit analysis, gap analysis, positioning, or another supported task.

### User-Friendly Controls

Engineering terms such as `top_k` are not shown to regular users.

The UI uses evidence-coverage labels instead, while the implementation still maps them to retrieval parameters internally.

### Retrieval Transparency Without UI Overload

Evidence, source details, search queries, routing decisions, and conversation memory remain inspectable, but are collapsed by default.

This supports both usability and trust.

### Global Reranking After Multi-Query Retrieval

The earlier Agentic implementation deduplicated retrieved chunks and then returned the first eight candidates.

That created query-order bias: chunks found by earlier queries were more likely to survive, while evidence from later queries could be dropped before any global relevance comparison.

The final design:

```text
Retrieves all candidates
→ Deduplicates them
→ Reranks the complete candidate pool
→ Selects the top evidence
```

This improves evidence selection without reducing retrieval recall.

### Recall-Preserving Fallback

The system does not use a second ranking algorithm when Qwen reranking fails.

Instead, it passes the complete deduplicated candidate pool to the generation model.

This decision favors:

- Simplicity
- Transparency
- Recall preservation
- Avoidance of first-seen truncation

### Evaluation as a Separate Internal Layer

Evaluation logic is not shown to the end user.

The app focuses on answering questions, while `eval_runner.py` produces internal artifacts for routing, retrieval, and answer-quality review.

---

## Current Limitations

- Final answer quality is not yet automatically scored.
- Entity coverage uses simple string matching.
- Topic coverage still requires manual review or an LLM-as-judge.
- The nine-question set is intentionally small and does not cover every real-world job-posting pattern.
- Multi-query output cleaning can be improved.
- The knowledge base currently depends on manually maintained text files.
- The system does not yet parse a pasted JD into a dedicated structured requirement schema.
- Reranking currently applies only to the Agentic retrieval path.
- Reranking optimizes semantic relevance but does not explicitly guarantee project or source diversity.
- The exact pre-rerank candidate count is not returned after successful top-evidence selection.
- Changing embedding models requires rebuilding ChromaDB.
- The generation provider uses an OpenAI-compatible API format, while reranking uses a dedicated endpoint.
- Streamlit session memory is local to the current browser session.
- The project currently provides offline validation, not full real-world product validation.

---

## Future Improvements

### Job Description Parsing

Extract structured fields from a pasted job posting, such as:

- Required skills
- Preferred skills
- Responsibilities
- Seniority
- Product expectations
- Technical expectations

### Explicit Job-to-Project Matching

Generate a structured match matrix:

```text
Job requirement
→ Matching project evidence
→ Strength of evidence
→ Missing evidence
→ Recommended positioning
```

### LLM-as-Judge Evaluation

Add rubric-based automated scoring for:

- Grounding
- Completeness
- Relevance
- Actionability
- Role alignment

### Retrieval Improvements

- Hybrid keyword and vector search
- Metadata filtering
- Improved query cleaning
- Evidence diversity controls
- Source- or project-aware selection constraints
- Exact candidate-pool observability
- Reranker A/B testing and threshold analysis

### Real-World Product Validation

Evaluate the assistant with target users and compare it against a no-assistant baseline using:

- Task completion rate
- Time to analyze a job posting
- User confidence
- Expert or recruiter review
- Output usefulness ratings
- Repeat usage

### Provider Expansion

Add non-OpenAI-compatible adapters while preserving the same provider interface.

### Tool-Calling Agent

Add tools for:

- Parsing job descriptions
- Comparing projects
- Identifying portfolio gaps
- Generating resume bullets
- Producing interview talking points

---

## What This Project Demonstrates

This project demonstrates the ability to:

- Build an end-to-end RAG application
- Design Basic, Agentic, and Adaptive retrieval workflows
- Use classification and routing to control system behavior
- Incorporate conversation context into retrieval
- Build multi-query search, evidence deduplication, and global reranking
- Design a recall-preserving fallback for reranker failure
- Create a verification and offline-validation framework instead of relying only on demos
- Separate model-provider implementation from core application logic
- Migrate a working system from OpenAI Responses API to Qwen generation, embedding, and reranking services
- Translate engineering controls into a clearer end-user experience
- Improve a technical prototype through product-oriented iteration

---

## Interview Summary

> I built an Adaptive RAG career assistant that matches a user's project portfolio against dynamically provided job postings. The system classifies user intent and routes simple factual questions to Basic RAG while sending job-fit analysis, project comparison, gap analysis, and resume or interview positioning through an Agentic multi-query workflow. The Agentic path retrieves a broad candidate pool, deduplicates the evidence, and uses a dedicated Qwen reranker to globally select the most relevant chunks against the standalone user question. If reranking is unavailable, the system preserves recall by sending the complete deduplicated candidate set to the generation model instead of truncating by query order. I also added conversation-aware rewriting, retrieval transparency, a Streamlit interface, and an evaluation framework that separates system verification from offline product validation.

---

## Status

The current version is a completed V1 prototype with:

- Working document ingestion
- Working ChromaDB retrieval
- Working Basic RAG
- Working Agentic RAG
- Working Adaptive routing
- Working conversation-aware rewriting
- Working Streamlit UI
- Working evaluation runner
- Working Qwen generation, embedding, and reranking integration
- Working full-candidate rerank fallback
- Rerank and fallback transparency in Streamlit
- Verification and offline-validation artifacts
- Provider and model traceability in evaluation outputs

The next phase focuses on packaging, portfolio presentation, stronger real-world validation, evidence-diversity controls, and structured job-description matching.

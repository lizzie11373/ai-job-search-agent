# Candidate Evidence Gold v2 — RAG Project

**Review status:** HUMAN_REVIEWED (author-confirmed for Portfolio V1; historical analysis preserved).

**Frozen input SHA-256:** `4220ed310c8143abb796b08fec64e36c9961fd7f1a374ff803fd88c15c111a74`

## Annotation policy

- Include implemented technical capabilities, product/architecture decisions, evaluation work, fallback behavior, and useful product-transparency decisions.
- Exclude setup instructions, repository structure, generic stack lists when stronger evidence exists, future improvements, and generic self-positioning.
- Prefer one reusable downstream-matching capability or decision per evidence unit.

## Draft evidence units (21)

### G001
**Claim:** Built an adaptive retrieval-augmented generation system that helps users evaluate how their projects and experience match dynamically provided job postings.

**Source section:** Overview
**Source lines:** 3–13

**Source text:**

> An adaptive retrieval-augmented generation system that helps users evaluate how their projects and experience match dynamically provided job postings.
> 
> Users can paste any job description, role requirements, or hiring criteria and ask questions such as:
> 
> - Which of my projects best match this role?
> - What evidence supports my fit for this position?
> - What gaps should I address?
> - How should I position a project on my resume?
> - How should I explain the project in an interview?
> 
> The system does not rely on predefined job titles. Job titles, job descriptions, and hiring requirements are treated as dynamic user-provided context.

### G002
**Claim:** Implemented document ingestion and chunking with source metadata, embeddings, and ChromaDB semantic retrieval.

**Source section:** Key Capabilities — Document Ingestion and Chunking
**Source lines:** 69–77

**Source text:**

> ### 1. Document Ingestion and Chunking
> 
> The system loads text documents from the local knowledge base, splits them into smaller chunks, and attaches metadata such as:
> 
> - Source file
> - Chunk index
> - Original text
> 
> These chunks are embedded and stored in ChromaDB for semantic retrieval.

### G003
**Claim:** Implemented a Basic RAG workflow using query embeddings, ChromaDB retrieval, context construction, and grounded answer generation.

**Source section:** Key Capabilities — Basic RAG
**Source lines:** 79–101

**Source text:**

> ### 2. Basic RAG
> 
> Basic RAG is designed for direct factual retrieval and single-project explanation.
> 
> Example questions:
> 
> ```text
> What technology stack does Project 2 use?
> What does Project 1 demonstrate?
> Does Project 4 include PyTorch?
> ```
> 
> Workflow:
> 
> ```text
> User question
> → Query embedding
> → ChromaDB retrieval
> → Context construction
> → Grounded answer generation
> ```
> 
> Basic RAG does not use the intent classifier, contextual rewriting, or multi-query planning when it is manually forced for testing.

### G004
**Claim:** Implemented an Agentic RAG workflow with conversation-aware rewriting, multi-query planning, retrieval, candidate merging, chunk deduplication, Qwen global reranking, evidence selection, and grounded synthesis.

**Source section:** Key Capabilities — Agentic RAG
**Source lines:** 103–129

**Source text:**

> ### 3. Agentic RAG
> 
> Agentic RAG is designed for questions that require broader evidence, comparison, interpretation, or positioning.
> 
> Example questions:
> 
> ```text
> Which of my projects best match this job posting?
> Compare Project 2 and Project 4 for this role.
> What is missing from my portfolio for this position?
> How should I describe Project 2 in an interview?
> ```
> 
> Workflow:
> 
> ```text
> User question
> → Conversation-aware question rewriting
> → Multi-query planning
> → Retrieval for each query
> → Candidate merging
> → Chunk deduplication
> → Qwen global reranking
> → Top-evidence selection
> → Context construction
> → Grounded answer synthesis
> ```

### G005
**Claim:** Implemented Adaptive RAG that classifies user intent and automatically routes simple factual requests to Basic RAG and complex analytical or positioning requests to Agentic RAG.

**Source section:** Key Capabilities — Adaptive RAG
**Source lines:** 131–145

**Source text:**

> ### 4. Adaptive RAG
> 
> Adaptive RAG is the default end-user experience.
> 
> The system first classifies the user's intent, then automatically selects Basic or Agentic RAG.
> 
> ```text
> Simple factual intent
> → Basic RAG
> 
> Complex analytical or positioning intent
> → Agentic RAG
> ```
> 
> This removes the burden of retrieval-strategy selection from the user.

### G006
**Claim:** Designed intent classification around the user's task rather than a fixed target job role, keeping job titles and job descriptions as dynamic input.

**Source section:** Intent Classification
**Source lines:** 149–186

**Source text:**

> ## Intent Classification
> 
> The classifier identifies what the user is trying to accomplish. It does not classify the user into a fixed target role.
> 
> Current intent categories:
> 
> ```python
> QUESTION_TYPES = [
>     "factual lookup",
>     "project explanation",
>     "project comparison",
>     "job fit analysis",
>     "gap analysis",
>     "resume or interview positioning",
>     "risk and limitations",
> ]
> ```
> 
> ### Routing Policy
> 
> ```text
> factual lookup
> project explanation
>         ↓
>     Basic RAG
> ```
> 
> ```text
> project comparison
> job fit analysis
> gap analysis
> resume or interview positioning
> risk and limitations
>         ↓
>     Agentic RAG
> ```
> 
> A role name or pasted job description remains part of the user's dynamic input rather than becoming a classifier category.

### G007
**Claim:** Implemented conversation-aware question rewriting using recent session messages to resolve follow-up references while preserving intent and avoiding unsupported facts.

**Source section:** Conversation-Aware Question Rewriting
**Source lines:** 190–215

**Source text:**

> ## Conversation-Aware Question Rewriting
> 
> The system stores recent messages in the current Streamlit session and uses them to resolve follow-up questions.
> 
> Example:
> 
> ```text
> User:
> Tell me about Project 2.
> 
> User:
> What is missing from this project for the job above?
> ```
> 
> The system can rewrite the follow-up into a standalone retrieval question such as:
> 
> ```text
> What is missing from Project 2 for the previously provided job posting?
> ```
> 
> The rewriting step is designed to:
> 
> - Resolve references such as “this project,” “it,” or “the previous role”
> - Preserve the user's original intent
> - Avoid introducing unsupported facts
> - Produce a clearer query for downstream retrieval

### G008
**Claim:** Implemented multi-query retrieval with up to four search queries and three chunks per query, then merged and deduplicated candidates using source file plus chunk index.

**Source section:** Multi-Query Retrieval
**Source lines:** 233–249

**Source text:**

> Agentic RAG generates multiple search queries and retrieves evidence for each one.
> 
> With the default configuration:
> 
> ```text
> Up to 4 search queries
> ×
> Up to 3 chunks per query
> =
> Up to 12 initial candidates before deduplication
> ```
> 
> Candidates are merged and deduplicated using:
> 
> ```text
> source file + chunk index
> ```

### G009
**Claim:** Preserved retrieval metadata on deduplicated chunks, including matched queries, rank, distance, query-hit count, and original candidate position for debugging and evaluation.

**Source section:** Multi-Query Retrieval
**Source lines:** 251–259

**Source text:**

> A deduplicated chunk can retain:
> 
> - Every search query that retrieved it
> - Its retrieval rank for each query
> - Its retrieval distance for each query
> - The number of query hits
> - Its original candidate position
> 
> This metadata supports debugging, evaluation, and retrieval transparency.

### G010
**Claim:** Implemented global reranking of the complete deduplicated candidate pool with qwen3-rerank against the standalone user question, selecting the top eight evidence chunks.

**Source section:** Reranking and Evidence Selection
**Source lines:** 263–293

**Source text:**

> ## Reranking and Evidence Selection
> 
> Vector retrieval is optimized for recall, but the first retrieved candidates are not always the best evidence for the user's complete analytical task.
> 
> For Agentic RAG, the complete deduplicated candidate pool is sent to a dedicated Qwen reranker.
> 
> ```text
> Standalone user question
> +
> All deduplicated candidate chunks
>         ↓
> qwen3-rerank
>         ↓
> Global relevance scores
>         ↓
> Top 8 evidence chunks
>         ↓
> Final answer generation
> ```
> 
> The reranker uses the standalone user question as the ranking query rather than ranking separately against each generated search query.
> 
> This separates two responsibilities:
> 
> ```text
> Generated search queries
> → Expand retrieval recall
> 
> Standalone user question
> → Determine final evidence relevance
> ```

### G011
**Claim:** Designed a full-candidate fallback that sends all deduplicated candidates to generation when reranking is unavailable, avoiding first-seen truncation and preserving recall.

**Source section:** Reranking and Evidence Selection — Full-Candidate Fallback
**Source lines:** 306–333

**Source text:**

> ### Full-Candidate Fallback
> 
> Reranking is useful, but the answer pipeline should not fail only because the reranker is temporarily unavailable.
> 
> If Qwen reranking is disabled or fails:
> 
> ```text
> All deduplicated candidates
> → No blind truncation
> → Full candidate set is passed to the generation model
> ```
> 
> The fallback intentionally does not return to first-seen truncation such as:
> 
> ```python
> unique_chunks[:8]
> ```
> 
> That older approach could favor earlier search queries and drop evidence retrieved by later queries.
> 
> With the current default settings, the fallback passes at most 12 candidates before deduplication, so preserving the complete candidate set is a practical way to protect recall.
> 
> Fallback metadata includes:
> 
> - `ranking_method = "all_candidates_fallback"`
> - `rerank_used = False`
> - `rerank_fallback_reason`
> - Exact final evidence count

### G012
**Claim:** Implemented a model-provider abstraction through shared text, JSON, embedding, and reranking interfaces so core RAG logic remains separated from provider-specific APIs.

**Source section:** Model Provider Abstraction
**Source lines:** 359–397

**Source text:**

> ## Model Provider Abstraction
> 
> The core RAG pipeline does not directly call a model-specific SDK.
> 
> Instead, `rag_core.py` depends on a small provider interface:
> 
> ```python
> call_llm_text(...)
> call_llm_json(...)
> get_embedding(...)
> rerank_documents(...)
> ```
> 
> These functions are implemented in `model_provider.py`.
> 
> Current configuration:
> 
> ```text
> Model provider: Qwen
> Generation model: qwen3.7-plus
> Embedding model: text-embedding-v4
> Reranker model: qwen3-rerank
> Generation API style: OpenAI-compatible Chat Completions
> Rerank API style: Dedicated rerank endpoint
> ```
> 
> ### Why This Abstraction Matters
> 
> The provider layer separates:
> 
> ```text
> RAG business logic
> from
> model-specific API implementation
> ```
> 
> If the project later moves to a provider that does not support the OpenAI-compatible API format, the main changes should remain inside `model_provider.py`, while the core retrieval and routing logic can stay unchanged.
> 
> The abstraction does not eliminate all provider differences. JSON output, embeddings, reranking, tool calling, error handling, and model parameters may still require provider-specific implementations.

### G013
**Claim:** Implemented structured model-output validation with JSON parsing, allowed-enum validation, and a rule-based fallback when intent-classifier output is invalid or the model call fails.

**Source section:** Structured Model Output and Validation
**Source lines:** 401–416

**Source text:**

> ## Structured Model Output and Validation
> 
> The intent classifier requests JSON-formatted output.
> 
> However, the system does not blindly trust the model response.
> 
> The process is:
> 
> ```text
> Model returns JSON text
> → Python parses it with json.loads()
> → The predicted type is validated against the allowed enum
> → A rule-based fallback is used when the output is invalid or the model call fails
> ```
> 
> This improves robustness and prevents unsupported category names from entering the routing pipeline.

### G014
**Claim:** Designed the Streamlit experience with Adaptive RAG as the default, advanced forced-mode controls for testing, and user-friendly evidence-coverage controls instead of exposing top_k directly.

**Source section:** Streamlit User Experience
**Source lines:** 420–453

**Source text:**

> ## Streamlit User Experience
> 
> The project includes a Streamlit interface designed for both normal users and internal testing.
> 
> ### Default Experience
> 
> The default experience uses Auto / Adaptive RAG.
> 
> Users do not need to understand or select:
> 
> - Basic RAG
> - Agentic RAG
> - Adaptive RAG
> - `top_k`
> 
> They only need to ask a question or paste a job description.
> 
> ### Advanced Controls
> 
> Advanced controls are available for debugging, evaluation, and baseline comparison.
> 
> They allow forced selection of:
> 
> - Auto / Adaptive RAG
> - Basic RAG
> - Agentic RAG
> 
> The UI also replaces the engineering term `top_k` with a user-friendly evidence-coverage control:
> 
> - Focused
> - Balanced
> - Comprehensive
> 
> These options are internally mapped to different retrieval depths.

### G015
**Claim:** Implemented retrieval and reranking transparency in the UI through collapsible details such as ranking method, reranker model, fallback usage, evidence counts, matched queries, and candidate/final positions.

**Source section:** Streamlit User Experience — Progressive Disclosure
**Source lines:** 455–477

**Source text:**

> ### Progressive Disclosure
> 
> The final answer remains visible by default.
> 
> Technical and supporting information is placed in collapsible sections:
> 
> - Workflow Details
> - Evidence Ranking
> - Evidence Overview
> - Source Details
> - Conversation Memory
> 
> For Agentic responses, the interface can display:
> 
> - Ranking method
> - Reranker model
> - Whether fallback was used
> - Final evidence count
> - Rerank score summary
> - Matched search queries
> - Candidate and final evidence positions
> 
> This keeps the main experience simple while preserving transparency for users who want to inspect the workflow.

### G016
**Claim:** Built an offline evaluation runner around a curated nine-question set that runs Basic, Agentic, and Adaptive modes and records answers plus internal workflow behavior.

**Source section:** Evaluation Framework
**Source lines:** 481–503

**Source text:**

> ## Evaluation Framework
> 
> The project includes an internal offline evaluation runner built around a curated nine-question test set.
> 
> The runner can execute each question in:
> 
> - Basic RAG
> - Agentic RAG
> - Adaptive RAG
> 
> A full run can therefore produce up to 27 mode-level results.
> 
> Each result records the final answer as well as internal workflow behavior, including:
> 
> - Conversation history
> - Interpreted standalone question
> - Predicted question type
> - Selected strategy
> - Search queries
> - Retrieved chunks
> - Rerank and fallback metadata
> - Latency
> - Errors

### G017
**Claim:** Defined evaluation as two complementary dimensions: verification of intended system behavior and validation of whether resulting evidence and answers appear useful for the user task.

**Source section:** Evaluation Framework
**Source lines:** 505–513

**Source text:**

> The evaluation framework covers two complementary dimensions:
> 
> ```text
> Verification
> → Did the system execute according to its intended design?
> 
> Validation
> → Did the resulting evidence and answer appear useful for the user's task?
> ```

### G018
**Claim:** Combined automatic signals with manual semantic review for evidence quality, judging relevance, specificity, sufficiency, diversity, grounding, and support strength.

**Source section:** Evaluation Framework — Retrieval and Evidence Evaluation
**Source lines:** 555–574

**Source text:**

> Required-entity coverage is checked automatically with simple string matching.
> 
> This is a lightweight heuristic. It does not fully understand aliases, paraphrases, or semantic equivalents.
> 
> Evidence quality therefore remains semi-objective:
> 
> ```text
> Automatic signals
> +
> Manual semantic review
> ```
> 
> Manual review considers whether the evidence is:
> 
> - Relevant
> - Specific
> - Sufficient
> - Diverse enough for the question
> - Properly grounded in the correct project
> - Strong enough to support the final conclusion

### G019
**Claim:** Evaluated reranking and fallback behavior using model/configuration state, fallback status and reason, evidence counts, represented queries/sources, and rerank-score summaries.

**Source section:** Evaluation Framework — Rerank and Fallback Evaluation
**Source lines:** 576–593

**Source text:**

> ### 3. Rerank and Fallback Evaluation
> 
> For Agentic results, the runner records:
> 
> - Reranker model
> - Whether reranking was enabled
> - Ranking method
> - Whether the reranker was actually used
> - Whether fallback was activated
> - Fallback reason
> - Final evidence count
> - Represented query count
> - Represented source count
> - Minimum, maximum, and average rerank scores
> 
> When the all-candidate fallback is used, the returned evidence count is the exact deduplicated candidate-pool size.
> 
> When Qwen reranking succeeds, the current `rag_core.py` returns only the selected evidence. The evaluation output therefore avoids claiming an exact pre-rerank candidate count when that value is not available.

### G020
**Claim:** Stored structured answer-quality rubrics for human review or future LLM-as-judge across grounding, completeness, product framing, actionability, role relevance, and risk awareness, while distinguishing offline validation from full real-world product validation.

**Source section:** Evaluation Framework — Offline Validation and Answer-Quality Review
**Source lines:** 595–621

**Source text:**

> ### 4. Offline Validation and Answer-Quality Review
> 
> Final answer quality has no single ground-truth answer.
> 
> The runner stores structured rubrics for human review or a future LLM-as-judge.
> 
> Example dimensions include:
> 
> - Retrieval grounding
> - Answer completeness
> - Product framing
> - Actionability
> - Role relevance
> - Risk awareness
> 
> This provides initial offline validation: it evaluates whether the system appears useful on representative scenarios.
> 
> It does not yet constitute complete real-world product validation.
> 
> Stronger product validation would require target-user testing and measurable outcomes such as:
> 
> - Task completion rate
> - Time saved
> - User confidence
> - Expert or recruiter ratings
> - Repeat usage
> - Improvement over a no-assistant baseline

### G021
**Claim:** Recorded model and run traceability including provider, generation model, embedding model, reranker model, rerank configuration, timestamp, evaluation version, elapsed time, and errors.

**Source section:** Evaluation Framework — Model Run Traceability
**Source lines:** 623–637

**Source text:**

> ### 5. Model Run Traceability
> 
> Each evaluation run records:
> 
> - Model provider
> - Generation model
> - Embedding model
> - Reranker model
> - Rerank configuration
> - Timestamp
> - Evaluation version
> - Elapsed time
> - Errors
> 
> This prevents results from different model configurations from being mixed together.

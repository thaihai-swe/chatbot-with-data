# Feature Specification: Multi-Hop Reasoning Chain & Real Reranking

## Metadata

- **Feature name:** Multi-Hop Reasoning Chain & Real Reranking
- **Feature slug:** 15.retrieval-optimization
- **Owner:** System Architect
- **Status:** Draft
- **Last updated:** 2026-05-19
- **Related artifacts:**
  - `analysis.md` - Current state analysis
  - `proposal.md` - High-level proposal

---

## Problem Statement

**What problem are we solving?**

The system has sophisticated query decomposition that breaks complex queries into sub-questions, but treats them as independent parallel queries. This misses the core value of multi-hop reasoning: using intermediate results to inform subsequent retrieval steps. Additionally, the reranking implementation is a dummy that just sorts by similarity score, wasting the potential of the advanced multi-query fusion pipeline.

**For whom?**

- **Primary users:** End users asking complex multi-hop questions that require reasoning chains (e.g., "What did the CEO say about the product mentioned in Q3 earnings?")
- **Secondary users:** System operators and developers who need visibility into reasoning chains for debugging and trust-building

**Why now?**

The retrieval foundation is 70% complete with query decomposition, multi-query fusion, and comprehensive tracing already implemented. The missing 30% (iterative reasoning and real reranking) are the highest-ROI enhancements that will differentiate this system as a true multi-hop RAG platform.

---

## Desired Outcomes

1. **True Multi-Hop Reasoning:** System executes sub-questions sequentially, where each sub-question's results inform the next retrieval step, enabling complex reasoning chains.

2. **Optimal Chunk Ranking:** Retrieved chunks are reranked using cross-encoder models or Cohere Rerank API, ensuring the top-k chunks used for grounding are the most relevant.

3. **Reasoning Transparency:** Users can see the reasoning chain (which sub-question led to which chunks, intermediate steps) in the API response for debugging and trust-building.

4. **Graceful Degradation:** Failed intermediate steps fall back to baseline retrieval without aborting the entire query.

---

## Minimum Release Slice

**What ships in the first useful release:**

1. Sequential iterative retrieval for multi-hop queries
2. Reasoning chain tracking and API exposure
3. Failure handling with fallback to original query + remaining sub-questions
4. Cross-encoder reranking integration (local model)
5. Comprehensive tracing for both features

**What can wait:**

- Cohere Rerank API support (can be added in follow-up)
- UI implementation for reasoning chain display (API contract first, UI later)
- Advanced reranking features (score calibration, ensemble reranking)
- Performance optimizations (caching, parallelization where possible)

---

## Success Criteria

- **SC-001:** System executes sub-questions sequentially, using intermediate results to inform subsequent retrieval
  - **Validation:** Manual test with multi-hop query; verify sub-questions execute in order and later sub-questions reference earlier results

- **SC-002:** Reasoning chain is exposed in API response with sub-questions, chunks, and intermediate steps
  - **Validation:** API response inspection; verify `reasoning_chain` field contains sub-questions, chunk IDs, and execution order

- **SC-003:** Failed intermediate sub-questions trigger fallback to original query + remaining sub-questions
  - **Validation:** Manual test with query that causes intermediate failure; verify system continues with fallback strategy

- **SC-004:** Multi-hop queries complete within 2-3x baseline latency (e.g., 3-6s for queries that normally take 2s)
  - **Validation:** Performance test; measure latency for multi-hop vs. baseline queries

- **SC-005:** Existing non-multi-hop queries are unaffected (no regression in latency or quality)
  - **Validation:** Regression test suite; verify simple queries maintain baseline performance

- **SC-006:** Cross-encoder model reranks retrieved chunks based on query-chunk relevance
  - **Validation:** Unit test; verify cross-encoder scores are computed and chunks are reordered

- **SC-007:** Reranking improves top-k chunk relevance (measurable via manual evaluation)
  - **Validation:** Manual evaluation; compare top-5 chunks before/after reranking for 10 test queries

- **SC-008:** Reranking adds <200ms latency for typical queries
  - **Validation:** Performance test; measure reranking latency in isolation

- **SC-009:** Reasoning chain is captured in `RetrievalTrace` with per-hop timing and chunk attribution
  - **Validation:** Trace inspection; verify `RetrievalTrace` contains hop-by-hop breakdown

- **SC-010:** Reranking scores and pre/post-rerank ordering are captured in `RerankingTrace`
  - **Validation:** Trace inspection; verify `RerankingTrace` contains before/after chunk ordering

- **SC-011:** Collection routing correctly identifies relevant collection(s) for single-collection queries with >80% accuracy
  - **Validation:** Manual evaluation; test 20 queries with known correct collections, measure routing accuracy

- **SC-012:** Collection routing falls back to all-collections for low-confidence queries (<0.7 threshold)
  - **Validation:** Manual test; verify ambiguous queries trigger fallback

- **SC-013:** Collection routing adds <500ms latency to query processing
  - **Validation:** Performance test; measure routing latency in isolation

- **SC-014:** Collection routing decisions are captured in trace with confidence scores and reasoning
  - **Validation:** Trace inspection; verify routing trace contains collections, confidence, reasoning

---

## In Scope

1. **Multi-Hop Reasoning Chain:**
   - Sequential iterative retrieval for decomposed sub-questions
   - Intermediate result usage to inform subsequent retrieval
   - Reasoning chain tracking (sub-question → chunks → intermediate reasoning)
   - API exposure of reasoning chain
   - Failure handling with fallback strategy

2. **Real Reranking:**
   - Cross-encoder model integration (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`)
   - Query-chunk relevance scoring
   - Chunk reordering based on cross-encoder scores
   - Score normalization to [0, 1] range
   - Threshold filtering for low-relevance chunks

3. **Collection Auto-Detection (Lightweight):**
   - LLM-based collection routing for single-collection queries
   - Confidence scoring (high/medium/low)
   - Fallback to all-collections for low confidence or ambiguous queries
   - Session-level collection routing (not per-hop in multi-hop chains)
   - Routing decision tracing

4. **Observability:**
   - Reasoning chain in `RetrievalTrace`
   - Per-hop timing and chunk attribution
   - Reranking scores in `RerankingTrace`
   - Pre/post-rerank ordering
   - Collection routing decisions in trace

5. **Configuration:**
   - Enable/disable multi-hop reasoning per request
   - Enable/disable reranking per request
   - Enable/disable collection auto-detection per request
   - Max hops limit (default: 3)
   - Timeout for multi-hop queries (default: 30s)
   - Reranking top-N candidates (default: 50)
   - Collection routing confidence threshold (default: 0.7)

---

## Out Of Scope

1. **Query/result caching** - Separate feature (performance optimization)
2. **Advanced filtering/metadata** - Separate feature (query capabilities)
3. **Retrieval quality metrics (MRR, NDCG)** - Separate feature (observability)
4. **UI implementation for reasoning chain display** - API contract only; UI is separate workstream
5. **Cohere Rerank API support** - Can be added in follow-up release
6. **Real-time streaming of reasoning steps** - Batch response only for MVP
7. **Multi-collection routing for complex queries** - Lightweight routing only; advanced multi-collection logic deferred
8. **Embedding-based collection similarity** - LLM-based routing only for MVP
9. **Per-hop collection routing in multi-hop chains** - Session-level routing only for MVP
10. **Collection recommendation UI** - API contract only

---

## Non-Goals

1. **Building a general-purpose reasoning engine** - Focus on retrieval-specific reasoning, not arbitrary logic
2. **Supporting arbitrary reasoning depths** - Limit to 3-5 hops for performance and complexity management
3. **Automatic query classification improvements** - Use existing classification; don't change routing logic
4. **Changing existing query decomposition logic** - Enhance what happens after decomposition, not decomposition itself
5. **Optimizing for sub-second latency** - 2-3x latency increase is acceptable for multi-hop queries
6. **Perfect collection routing** - Lightweight routing with fallback is acceptable; 100% accuracy not required
7. **Building a collection recommendation system** - Simple routing only, not a full recommendation engine

---

## Users And Stakeholders

**Primary users:**
- End users asking complex multi-hop questions requiring reasoning chains
- Example: "What did the CEO say about the product mentioned in Q3 earnings?"
- Example: "Compare the pricing strategy discussed in the 2024 plan with the actual pricing in the product docs"

**Secondary stakeholders:**
- System operators debugging retrieval quality issues
- Developers building on top of the RAG API
- Product managers evaluating retrieval effectiveness

---

## User Stories And Key Scenarios

### US-001: Multi-Hop Question Answering
**As a** user asking a complex multi-hop question  
**I want** the system to break down my question into steps and use intermediate results to inform subsequent retrieval  
**So that** I get accurate answers that require reasoning across multiple pieces of information

### US-002: Reasoning Transparency
**As a** user or developer  
**I want** to see the reasoning chain (which sub-questions were asked, which chunks were retrieved, how they connect)  
**So that** I can understand how the system arrived at the answer and debug issues

### US-003: Optimal Chunk Ranking
**As a** user  
**I want** the most relevant chunks to be used for grounding my answer  
**So that** the generated response is accurate and well-supported

### US-004: Graceful Failure Handling
**As a** user  
**I want** the system to still provide an answer even if some intermediate reasoning steps fail  
**So that** I get a useful response instead of a complete failure

### US-005: Automatic Collection Routing
**As a** user  
**I want** the system to automatically route my query to the most relevant collection(s)  
**So that** I don't need to manually select collections and get faster, more relevant results

---

## Detailed Scenarios

### Scenario 1: Multi-Hop Query (Happy Path)

**Given:**
- User asks: "What did the CEO say about the product mentioned in Q3 earnings?"
- System classifies query as `multi_hop`
- Documents exist for both Q3 earnings and CEO statements

**When:**
- System decomposes query into:
  1. "What product was mentioned in Q3 earnings?"
  2. "What did the CEO say about [product from step 1]?"
- System executes sub-question 1, retrieves chunks, generates intermediate answer: "Product X"
- System executes sub-question 2 with context "Product X", retrieves relevant CEO statement chunks
- System reranks all retrieved chunks using cross-encoder
- System generates final answer using top-k reranked chunks

**Then:**
- User receives accurate answer grounded in both Q3 earnings and CEO statements
- API response includes `reasoning_chain` with:
  - Sub-question 1, retrieved chunks, intermediate answer
  - Sub-question 2 (contextualized with "Product X"), retrieved chunks
  - Final reranked chunk ordering
- Total latency is 2-3x baseline (acceptable)

---

### Scenario 2: Intermediate Failure (Fallback)

**Given:**
- User asks: "Compare the pricing in the 2024 plan with actual product pricing"
- System classifies query as `multi_hop`
- 2024 plan document exists, but "actual product pricing" is ambiguous

**When:**
- System decomposes query into:
  1. "What is the pricing in the 2024 plan?"
  2. "What is the actual product pricing?"
- System executes sub-question 1, retrieves chunks successfully
- System executes sub-question 2, but retrieves no relevant chunks (failure)
- System triggers fallback: combine original query + remaining sub-questions
- System retrieves using original query "Compare the pricing in the 2024 plan with actual product pricing"
- System reranks retrieved chunks

**Then:**
- User receives answer based on fallback retrieval (not perfect, but useful)
- API response includes `reasoning_chain` with:
  - Sub-question 1 success
  - Sub-question 2 failure
  - Fallback strategy triggered
- System does not abort; graceful degradation occurs

---

### Scenario 3: Simple Query (No Multi-Hop)

**Given:**
- User asks: "What is the company's mission statement?"
- System classifies query as `simple`

**When:**
- System skips multi-hop reasoning (existing routing logic)
- System executes baseline retrieval
- System reranks retrieved chunks using cross-encoder
- System generates answer

**Then:**
- User receives answer quickly (no multi-hop overhead)
- Latency is baseline + reranking (<200ms extra)
- No regression in performance for simple queries

---

### Scenario 4: Reranking Improves Relevance

**Given:**
- User asks: "How does the authentication system work?"
- System retrieves 50 chunks via multi-query fusion (RRF)
- Top 10 chunks by similarity score include some tangentially related chunks

**When:**
- System applies cross-encoder reranking to top 50 chunks
- Cross-encoder computes query-chunk relevance scores
- System reorders chunks based on cross-encoder scores
- System selects top 10 reranked chunks for grounding

**Then:**
- Top 10 chunks are more relevant to "authentication system" than pre-reranking
- Generated answer is more accurate and focused
- `RerankingTrace` shows before/after ordering and score changes

---

### Scenario 5: Collection Auto-Detection (Happy Path)

**Given:**
- User creates session without specifying collections (empty list)
- Available collections:
  - "Product Documentation" (5,000 chunks)
  - "Internal Policies" (2,000 chunks)
  - "Q3 2024 Earnings" (1,000 chunks)
  - "Engineering Specs" (3,000 chunks)
- User asks: "What's our return policy?"

**When:**
- System detects no collections specified in session
- System invokes collection routing service
- LLM analyzes query intent: "return policy" → product/customer-facing
- LLM routes to "Product Documentation" with high confidence (0.9)
- System retrieves from "Product Documentation" only (5,000 chunks instead of 11,000)

**Then:**
- Query is faster (searches 5,000 chunks instead of 11,000)
- Results are more relevant (no noise from unrelated collections)
- API response includes `collection_routing` trace with:
  - Detected collections: ["Product Documentation"]
  - Confidence: 0.9
  - Reasoning: "Query about return policy is product documentation"
- User receives accurate answer grounded in product docs

---

### Scenario 6: Collection Auto-Detection (Low Confidence Fallback)

**Given:**
- User creates session without specifying collections
- User asks: "What happened last quarter?" (ambiguous query)

**When:**
- System invokes collection routing service
- LLM analyzes query but cannot confidently determine collection
- Confidence score: 0.4 (below threshold of 0.7)
- System falls back to searching all collections

**Then:**
- Query searches all collections (safe fallback)
- API response includes `collection_routing` trace with:
  - Detected collections: null (fallback to all)
  - Confidence: 0.4
  - Reasoning: "Query is ambiguous; could refer to earnings, policies, or engineering work"
  - Fallback triggered: true
- User receives answer from all available sources

---

## Current Context (Brownfield)

**Existing Behavior to Preserve:**

1. **Query Classification:** 5-category classification (simple/multi_hop/comparative/conversational/out_of_domain) must remain unchanged
2. **Query Decomposition:** Existing decomposition logic in `QueryIntelligenceService.decompose_query()` must remain unchanged
3. **RRF Merging:** Reciprocal Rank Fusion with k=60 for multi-query fusion must remain unchanged
4. **Parent-Child Expansion:** Existing parent-child retrieval logic must remain unchanged
5. **Hybrid Search:** Alpha parameter configuration must remain unchanged
6. **Safety Checks:** Query injection detection and chunk safety filtering must remain unchanged
7. **Tracing Infrastructure:** Existing `RetrievalTrace` and `RerankingTrace` schemas must be extended, not replaced

**Impacted Boundaries:**

- `backend/chat/retrieval.py:278-496` - `AdvancedRetrievalService` will be modified to add iterative retrieval
- `backend/chat/retrieval.py:250-276` - `RerankingService` will be replaced with real implementation
- `backend/schemas/chat.py` - `RetrievalTrace` and `RerankingTrace` will be extended with new fields
- `backend/chat/service.py:43-237` - Chat orchestration flow remains unchanged (calls retrieval service)

**Unchanged Behavior:**

- Query classification routing logic
- Multi-query fusion (expansion, rewriting, HyDE, synonyms)
- Parent-child expansion
- Grounding evaluation
- Context assembly
- Generation and citation extraction

---

## Dependencies And External Touchpoints

**DEP-001: Cross-Encoder Model**
- Dependency: Hugging Face `sentence-transformers` library
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2` (or similar)
- Risk: Model download/loading time on first use
- Mitigation: Pre-download model during deployment

**DEP-002: LLM Provider for Intermediate Answers**
- Dependency: Existing LLM provider (OpenAI, Anthropic, etc.)
- Used for: Generating intermediate answers in multi-hop chain
- Risk: Additional LLM API calls increase cost and latency
- Mitigation: Use fast, cheap model for intermediate answers (e.g., GPT-4o-mini)

**DEP-003: Existing Retrieval Infrastructure**
- Dependency: Weaviate vector database, embedding provider, chunk repository
- Risk: None (no changes to existing infrastructure)

**DEP-004: Tracing Infrastructure**
- Dependency: Existing `RetrievalTrace` and `RerankingTrace` schemas
- Risk: Schema changes may break existing consumers
- Mitigation: Extend schemas with new optional fields (backward compatible)

**DEP-005: LLM Provider for Collection Routing**
- Dependency: Existing LLM provider (OpenAI, Anthropic, etc.)
- Used for: Analyzing query intent and routing to collections
- Risk: Additional LLM API calls increase cost and latency
- Mitigation: Use fast, cheap model for routing (e.g., GPT-4o-mini); cache routing decisions where possible

**DEP-006: Collections Database**
- Dependency: `collections` table with `id`, `name`, `description` fields
- Used for: Retrieving collection metadata for routing decisions
- Risk: Missing or poor-quality descriptions reduce routing accuracy
- Mitigation: Validate collection descriptions exist; provide guidance for creating good descriptions

---

## Functional Requirements

### REQ-001: Sequential Sub-Question Execution

**Requirement:**  
When a query is classified as `multi_hop` and decomposed into sub-questions, the system must execute sub-questions sequentially (not in parallel), where each sub-question can reference results from previous sub-questions.

**Why it matters:**  
This is the core of multi-hop reasoning. Sequential execution allows the system to use intermediate results to refine subsequent queries, enabling true reasoning chains.

**Impacted users or scenarios:**  
US-001 (Multi-Hop Question Answering), Scenario 1 (Multi-Hop Query Happy Path)

**Related success criteria:**  
SC-001, SC-004

**Priority:** Must Have

**Acceptance notes:**  
- Sub-questions execute in order (1, 2, 3, ...)
- Each sub-question waits for previous sub-question to complete before starting
- Later sub-questions can reference intermediate results from earlier sub-questions

**Validation surface:**  
Manual test with multi-hop query; inspect `reasoning_chain` in API response to verify execution order and intermediate result usage

---

### REQ-002: Intermediate Answer Generation

**Requirement:**  
After retrieving chunks for each sub-question, the system must generate a concise intermediate answer that summarizes the retrieved information. This intermediate answer is used to contextualize subsequent sub-questions.

**Why it matters:**  
Intermediate answers provide the "glue" between reasoning steps, allowing the system to carry forward information from one hop to the next.

**Impacted users or scenarios:**  
US-001 (Multi-Hop Question Answering), Scenario 1 (Multi-Hop Query Happy Path)

**Related success criteria:**  
SC-001

**Priority:** Must Have

**Acceptance notes:**  
- Intermediate answer is generated using LLM (fast, cheap model preferred)
- Intermediate answer is concise (1-3 sentences)
- Intermediate answer is stored in reasoning chain
- Subsequent sub-questions are contextualized with intermediate answer

**Validation surface:**  
Manual test; inspect `reasoning_chain` to verify intermediate answers are present and used in subsequent sub-questions

---

### REQ-003: Reasoning Chain Tracking

**Requirement:**  
The system must track the complete reasoning chain, including: (1) sub-questions executed, (2) chunks retrieved per sub-question, (3) intermediate answers generated, (4) execution order, (5) per-hop timing.

**Why it matters:**  
Reasoning chain tracking enables transparency, debugging, and trust-building. Users and developers need to understand how the system arrived at an answer.

**Impacted users or scenarios:**  
US-002 (Reasoning Transparency), All scenarios

**Related success criteria:**  
SC-002, SC-009

**Priority:** Must Have

**Acceptance notes:**  
- Reasoning chain is stored in `RetrievalTrace.reasoning_chain` field
- Each hop includes: sub-question text, chunk IDs, intermediate answer, timing
- Execution order is preserved (hop 1, hop 2, hop 3, ...)

**Validation surface:**  
API response inspection; verify `reasoning_chain` field contains all required information

---

### REQ-004: Reasoning Chain API Exposure

**Requirement:**  
The reasoning chain must be included in the API response as a new field `reasoning_chain` in the chat response schema.

**Why it matters:**  
Users and developers need access to the reasoning chain for transparency and debugging.

**Impacted users or scenarios:**  
US-002 (Reasoning Transparency)

**Related success criteria:**  
SC-002

**Priority:** Must Have

**Acceptance notes:**  
- New field `reasoning_chain` added to chat response schema
- Field is optional (only present for multi-hop queries)
- Field contains array of hops with sub-question, chunks, intermediate answer, timing

**Validation surface:**  
API response inspection; verify `reasoning_chain` field is present and correctly formatted

---

### REQ-005: Failure Handling with Fallback

**Requirement:**  
If an intermediate sub-question fails to retrieve relevant chunks (e.g., no chunks above relevance threshold), the system must fall back to combining: (1) the original query without decomposition, and (2) remaining sub-questions that haven't been executed yet.

**Why it matters:**  
Graceful degradation ensures users get useful answers even when intermediate reasoning steps fail. Aborting the entire chain would result in poor user experience.

**Impacted users or scenarios:**  
US-004 (Graceful Failure Handling), Scenario 2 (Intermediate Failure)

**Related success criteria:**  
SC-003

**Priority:** Must Have

**Acceptance notes:**  
- Failure is detected when sub-question retrieves 0 chunks or all chunks below threshold
- Fallback strategy: retrieve using original query + execute remaining sub-questions
- Reasoning chain records failure and fallback strategy
- System does not abort; continues to generate answer

**Validation surface:**  
Manual test with query that causes intermediate failure; verify system continues with fallback and reasoning chain shows failure + fallback

---

### REQ-006: Multi-Hop Latency Constraint

**Requirement:**  
Multi-hop queries must complete within 2-3x baseline latency. For example, if a simple query takes 2 seconds, a multi-hop query should complete in 4-6 seconds.

**Why it matters:**  
Excessive latency degrades user experience. 2-3x is acceptable for complex reasoning, but beyond that users will perceive the system as slow.

**Impacted users or scenarios:**  
US-001 (Multi-Hop Question Answering), Scenario 1 (Multi-Hop Query Happy Path)

**Related success criteria:**  
SC-004

**Priority:** Must Have

**Acceptance notes:**  
- Measure baseline latency for simple queries (e.g., 2s)
- Measure multi-hop latency for complex queries (e.g., 4-6s)
- If latency exceeds 3x baseline, optimize or reduce max hops

**Validation surface:**  
Performance test; measure and compare latency for simple vs. multi-hop queries

---

### REQ-007: Max Hops Limit

**Requirement:**  
The system must enforce a maximum number of reasoning hops (default: 3, configurable up to 5) to prevent excessive latency and complexity.

**Why it matters:**  
Unbounded reasoning chains could lead to excessive latency, cost, and complexity. A reasonable limit balances capability with performance.

**Impacted users or scenarios:**  
All multi-hop scenarios

**Related success criteria:**  
SC-004

**Priority:** Must Have

**Acceptance notes:**  
- Default max hops: 3
- Configurable via `AdvancedRetrievalConfig.max_hops`
- If decomposition produces more sub-questions than max hops, truncate to max hops
- Reasoning chain records if truncation occurred

**Validation surface:**  
Unit test; verify system stops at max hops even if more sub-questions exist

---

### REQ-008: Multi-Hop Timeout

**Requirement:**  
Multi-hop queries must have a timeout (default: 30 seconds) to prevent indefinite execution. If timeout is reached, the system must return partial results or fall back to baseline retrieval.

**Why it matters:**  
Prevents system from hanging on complex or problematic queries. Users expect timely responses.

**Impacted users or scenarios:**  
All multi-hop scenarios

**Related success criteria:**  
SC-004

**Priority:** Must Have

**Acceptance notes:**  
- Default timeout: 30 seconds
- Configurable via `AdvancedRetrievalConfig.multi_hop_timeout_ms`
- If timeout reached, return partial results from completed hops
- Reasoning chain records timeout event

**Validation surface:**  
Manual test with artificially slow query; verify timeout triggers and partial results returned

---

### REQ-009: No Regression for Simple Queries

**Requirement:**  
Queries classified as `simple`, `conversational`, or `out_of_domain` must not experience latency or quality regression. Multi-hop logic must only apply to queries classified as `multi_hop`.

**Why it matters:**  
Most queries are simple and should not pay the cost of multi-hop reasoning. Existing performance must be preserved.

**Impacted users or scenarios:**  
Scenario 3 (Simple Query No Multi-Hop)

**Related success criteria:**  
SC-005

**Priority:** Must Have

**Acceptance notes:**  
- Simple queries skip multi-hop logic (existing routing behavior)
- Latency for simple queries remains baseline + reranking (<200ms extra)
- Quality for simple queries is unchanged or improved (due to reranking)

**Validation surface:**  
Regression test suite; measure latency and quality for simple queries before/after implementation

---

### REQ-010: Cross-Encoder Reranking

**Requirement:**  
The system must replace the dummy reranking implementation with a real cross-encoder model (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) that computes query-chunk relevance scores and reorders chunks accordingly.

**Why it matters:**  
Reranking improves the quality of top-k chunks used for grounding, leading to more accurate answers. The current dummy implementation wastes the potential of multi-query fusion.

**Impacted users or scenarios:**  
US-003 (Optimal Chunk Ranking), Scenario 4 (Reranking Improves Relevance)

**Related success criteria:**  
SC-006, SC-007

**Priority:** Must Have

**Acceptance notes:**  
- Cross-encoder model loaded on service initialization
- For each query, compute relevance scores for top-N candidates (default: 50)
- Reorder chunks by cross-encoder score (descending)
- Return top-k reranked chunks (default: 10)

**Validation surface:**  
Unit test; verify cross-encoder scores are computed and chunks are reordered. Manual evaluation; compare top-5 chunks before/after reranking for test queries.

---

### REQ-011: Reranking Score Normalization

**Requirement:**  
Cross-encoder scores must be normalized to [0, 1] range to enable consistent threshold filtering and score interpretation.

**Why it matters:**  
Raw cross-encoder scores vary by model and are not directly interpretable. Normalization enables consistent filtering and comparison.

**Impacted users or scenarios:**  
US-003 (Optimal Chunk Ranking)

**Related success criteria:**  
SC-006

**Priority:** Should Have

**Acceptance notes:**  
- Apply min-max normalization or sigmoid to cross-encoder scores
- Normalized scores in [0, 1] range
- Store both raw and normalized scores in `RerankingTrace`

**Validation surface:**  
Unit test; verify normalized scores are in [0, 1] range

---

### REQ-012: Reranking Threshold Filtering

**Requirement:**  
The system must support optional threshold filtering to remove chunks with reranking scores below a configurable threshold (default: 0.3).

**Why it matters:**  
Low-relevance chunks can degrade answer quality. Threshold filtering removes noise from the grounding context.

**Impacted users or scenarios:**  
US-003 (Optimal Chunk Ranking)

**Related success criteria:**  
SC-006

**Priority:** Should Have

**Acceptance notes:**  
- Configurable via `AdvancedRetrievalConfig.rerank_threshold`
- Default threshold: 0.3 (on normalized [0, 1] scale)
- Chunks below threshold are filtered out after reranking
- If all chunks filtered, fall back to top-k without filtering

**Validation surface:**  
Unit test; verify chunks below threshold are removed

---

### REQ-013: Reranking Latency Constraint

**Requirement:**  
Reranking must add less than 200ms latency for typical queries (50 candidates, 10 output chunks).

**Why it matters:**  
Reranking should improve quality without significantly degrading performance. 200ms is acceptable overhead for better results.

**Impacted users or scenarios:**  
All scenarios

**Related success criteria:**  
SC-008

**Priority:** Must Have

**Acceptance notes:**  
- Measure reranking latency in isolation (time to score 50 candidates)
- Target: <200ms on typical hardware
- If latency exceeds 200ms, reduce candidate count or optimize model

**Validation surface:**  
Performance test; measure reranking latency for 50 candidates

---

### REQ-014: Reranking Top-N Configuration

**Requirement:**  
The number of candidates to rerank (top-N) must be configurable (default: 50) to balance quality and performance.

**Why it matters:**  
Reranking all retrieved chunks (e.g., 100+) is expensive. Reranking top-N candidates balances quality (rerank enough to improve results) with performance (don't rerank everything).

**Impacted users or scenarios:**  
All scenarios

**Related success criteria:**  
SC-008

**Priority:** Must Have

**Acceptance notes:**  
- Configurable via `AdvancedRetrievalConfig.rerank_top_n`
- Default: 50 candidates
- Only top-N candidates by similarity score are reranked
- Remaining candidates are discarded

**Validation surface:**  
Unit test; verify only top-N candidates are passed to reranker

---

### REQ-015: Reranking Trace

**Requirement:**  
The system must capture reranking details in `RerankingTrace`, including: (1) pre-rerank chunk ordering, (2) post-rerank chunk ordering, (3) raw and normalized scores, (4) reranking latency.

**Why it matters:**  
Observability is critical for debugging and evaluating reranking effectiveness. Developers need to see how reranking changed chunk ordering.

**Impacted users or scenarios:**  
US-002 (Reasoning Transparency), Scenario 4 (Reranking Improves Relevance)

**Related success criteria:**  
SC-010

**Priority:** Must Have

**Acceptance notes:**  
- `RerankingTrace` extended with new fields:
  - `pre_rerank_order`: List of chunk IDs before reranking
  - `post_rerank_order`: List of chunk IDs after reranking
  - `scores`: Map of chunk ID to raw and normalized scores
  - `rerank_latency_ms`: Time spent reranking
- Trace included in API response

**Validation surface:**  
API response inspection; verify `RerankingTrace` contains all required fields

---

### REQ-016: Multi-Hop Configuration

**Requirement:**  
Multi-hop reasoning must be configurable per request via `AdvancedRetrievalConfig.enable_multi_hop` (default: true for multi_hop queries, false otherwise).

**Why it matters:**  
Users may want to disable multi-hop reasoning for specific queries (e.g., latency-sensitive use cases) or enable it for queries not classified as multi_hop.

**Impacted users or scenarios:**  
All scenarios

**Related success criteria:**  
SC-001, SC-005

**Priority:** Should Have

**Acceptance notes:**  
- `AdvancedRetrievalConfig.enable_multi_hop` flag
- Default: true if query classified as `multi_hop`, false otherwise
- If disabled, skip multi-hop logic even for multi_hop queries
- If enabled, apply multi-hop logic even for non-multi_hop queries (advanced use case)

**Validation surface:**  
Unit test; verify multi-hop logic is skipped when disabled

---

### REQ-017: Reranking Configuration

**Requirement:**  
Reranking must be configurable per request via `AdvancedRetrievalConfig.enable_reranking` (default: true).

**Why it matters:**  
Users may want to disable reranking for specific queries (e.g., latency-sensitive use cases) or compare results with/without reranking.

**Impacted users or scenarios:**  
All scenarios

**Related success criteria:**  
SC-006

**Priority:** Should Have

**Acceptance notes:**  
- `AdvancedRetrievalConfig.enable_reranking` flag
- Default: true
- If disabled, skip reranking and use similarity-based ordering
- If enabled, apply cross-encoder reranking

**Validation surface:**  
Unit test; verify reranking is skipped when disabled

---

### REQ-019: Collection Auto-Detection

**Requirement:**  
When a session has no collections specified (empty list), the system must automatically detect the most relevant collection(s) for the query using LLM-based routing before retrieval.

**Why it matters:**  
Searching all collections by default is slow and produces noisy results. Automatic routing improves performance and relevance without requiring users to manually select collections.

**Impacted users or scenarios:**  
US-005 (Automatic Collection Routing), Scenario 5 (Collection Auto-Detection Happy Path)

**Related success criteria:**  
SC-012, SC-014

**Priority:** Must Have

**Acceptance notes:**  
- Routing only applies when session has empty `collection_ids` list
- If session has explicit collections, skip routing (use session collections)
- LLM analyzes query intent and available collection descriptions
- Returns 1-3 most relevant collections with confidence scores
- Routing happens before retrieval, not during

**Validation surface:**  
Manual test with queries spanning different collections; verify correct collections are selected. Unit test; verify routing is skipped when session has explicit collections.

---

### REQ-020: Collection Routing Confidence Scoring

**Requirement:**  
The collection routing service must return a confidence score (0.0-1.0) for each routing decision. If the highest confidence is below a configurable threshold (default: 0.7), the system must fall back to searching all collections.

**Why it matters:**  
Low-confidence routing decisions could route queries to the wrong collection, resulting in no relevant results. Fallback ensures users always get results, even if routing is uncertain.

**Impacted users or scenarios:**  
US-005 (Automatic Collection Routing), Scenario 6 (Collection Auto-Detection Low Confidence Fallback)

**Related success criteria:**  
SC-013

**Priority:** Must Have

**Acceptance notes:**  
- Confidence score in [0.0, 1.0] range
- Default threshold: 0.7 (configurable via `AdvancedRetrievalConfig.collection_routing_threshold`)
- If confidence < threshold, fall back to all collections
- Fallback is recorded in routing trace

**Validation surface:**  
Manual test with ambiguous queries; verify fallback triggers for low confidence. Unit test; verify threshold logic.

---

### REQ-021: Collection Routing Trace

**Requirement:**  
The system must capture collection routing decisions in a new `CollectionRoutingTrace` including: (1) detected collections, (2) confidence scores, (3) LLM reasoning, (4) whether fallback was triggered, (5) routing latency.

**Why it matters:**  
Observability is critical for debugging routing decisions and evaluating routing effectiveness. Users and developers need to understand why a query was routed to specific collections.

**Impacted users or scenarios:**  
US-005 (Automatic Collection Routing), All collection routing scenarios

**Related success criteria:**  
SC-015

**Priority:** Must Have

**Acceptance notes:**  
- New `CollectionRoutingTrace` schema with fields:
  - `detected_collections`: List of collection IDs
  - `confidence_scores`: Map of collection ID to confidence score
  - `reasoning`: LLM explanation of routing decision
  - `fallback_triggered`: Boolean
  - `routing_latency_ms`: Time spent routing
- Trace included in `RetrievalTrace`

**Validation surface:**  
API response inspection; verify `CollectionRoutingTrace` contains all required fields

---

### REQ-022: Collection Routing Configuration

**Requirement:**  
Collection routing must be configurable per request via `AdvancedRetrievalConfig.enable_collection_routing` (default: true when session has no collections, false otherwise).

**Why it matters:**  
Users may want to disable routing for specific queries or force all-collections search even when routing is available.

**Impacted users or scenarios:**  
All collection routing scenarios

**Related success criteria:**  
SC-012

**Priority:** Should Have

**Acceptance notes:**  
- `AdvancedRetrievalConfig.enable_collection_routing` flag
- Default: true if session has empty `collection_ids`, false if session has explicit collections
- If disabled, skip routing and use session collections (or all collections if session is empty)
- If enabled, apply routing even if session has explicit collections (override mode)

**Validation surface:**  
Unit test; verify routing is skipped when disabled

---

### REQ-023: Collection Routing Latency Constraint

**Requirement:**  
Collection routing must add less than 500ms latency to query processing.

**Why it matters:**  
Routing should improve performance by reducing retrieval scope, not degrade it with excessive overhead. 500ms is acceptable for the benefit of targeted retrieval.

**Impacted users or scenarios:**  
All collection routing scenarios

**Related success criteria:**  
SC-014

**Priority:** Must Have

**Acceptance notes:**  
- Measure routing latency in isolation (time to call LLM and parse response)
- Target: <500ms on typical hardware
- If latency exceeds 500ms, optimize prompt or use faster model

**Validation surface:**  
Performance test; measure routing latency for typical queries

---

### REQ-024: Collection Descriptions for Routing

**Requirement:**  
The system must retrieve collection descriptions from the database and provide them to the LLM for routing decisions. If a collection has no description, use the collection name only.

**Why it matters:**  
LLM needs context about what each collection contains to make accurate routing decisions. Descriptions provide that context.

**Impacted users or scenarios:**  
US-005 (Automatic Collection Routing), All collection routing scenarios

**Related success criteria:**  
SC-012

**Priority:** Must Have

**Acceptance notes:**  
- Query `collections` table for all available collections
- Include `id`, `name`, and `description` fields
- If `description` is null or empty, use `name` only
- Pass collection metadata to LLM in routing prompt

**Validation surface:**  
Unit test; verify collection descriptions are retrieved and passed to LLM. Manual test; verify routing uses descriptions in reasoning.

---

### REQ-025: Backward Compatibility

**Requirement:**  
Existing API contracts, schemas, and behavior must remain unchanged for queries that do not use multi-hop reasoning or reranking. New fields must be optional and backward compatible.

**Why it matters:**  
Existing clients and integrations must continue to work without changes. Breaking changes are not acceptable for this enhancement.

**Impacted users or scenarios:**  
All existing users and integrations

**Related success criteria:**  
SC-005

**Priority:** Must Have

**Acceptance notes:**  
- New fields in response schemas are optional
- Existing fields unchanged
- Existing query behavior unchanged (routing, classification, etc.)
- No breaking changes to API contracts

**Validation surface:**  
Regression test suite; verify existing API calls continue to work unchanged

---

## Open Questions

**OQ-001: Intermediate Answer Model Selection**
- **Question:** Which LLM model should be used for generating intermediate answers in multi-hop chains?
- **Options:** (A) Same model as final generation, (B) Faster/cheaper model (e.g., GPT-4o-mini), (C) Configurable per request
- **Impact:** Cost and latency
- **Status:** Non-blocking; default to option B (faster/cheaper model) for MVP
- **Resolution:** Use GPT-4o-mini or equivalent for intermediate answers; make configurable in follow-up

**OQ-002: Cross-Encoder Model Selection**
- **Question:** Which cross-encoder model should be used for reranking?
- **Options:** (A) `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast, good quality), (B) `cross-encoder/ms-marco-MiniLM-L-12-v2` (slower, better quality), (C) Configurable
- **Impact:** Latency vs. quality tradeoff
- **Status:** Non-blocking; default to option A for MVP
- **Resolution:** Use `ms-marco-MiniLM-L-6-v2` for MVP; make model configurable in follow-up

**OQ-003: Cohere Rerank API Priority**
- **Question:** Should Cohere Rerank API support be included in MVP or deferred to follow-up?
- **Impact:** Scope and timeline
- **Status:** Non-blocking; defer to follow-up
- **Resolution:** MVP uses local cross-encoder only; Cohere API added in follow-up release

---

## Assumptions

**ASM-001:** Existing query classification accurately identifies multi-hop queries. If classification is inaccurate, multi-hop reasoning may be applied to wrong queries or missed for correct queries.

**ASM-002:** Intermediate answers can be generated in 1-3 sentences without losing critical information. If longer context is needed, may need to adjust approach.

**ASM-003:** Cross-encoder model `ms-marco-MiniLM-L-6-v2` provides sufficient quality improvement over similarity-based ranking. If not, may need larger model.

**ASM-004:** 2-3x latency increase is acceptable to users for multi-hop queries. If users are latency-sensitive, may need to optimize or make multi-hop opt-in only.

**ASM-005:** Existing tracing infrastructure can be extended without breaking changes. If schema changes break consumers, may need migration strategy.

**ASM-006:** Collection descriptions in the database are accurate and descriptive enough for LLM routing. If descriptions are missing or poor quality, routing accuracy may suffer.

**ASM-007:** LLM-based collection routing can achieve >80% accuracy for single-collection queries. If accuracy is lower, may need embedding-based or hybrid approach.

---

## Risk Mitigation

**RISK-001: Latency Regression**
- **Risk:** Multi-hop reasoning and reranking add latency that degrades user experience
- **Mitigation:** Enforce max hops limit, timeout, and latency constraints. Make multi-hop opt-in for latency-sensitive use cases.

**RISK-002: Cost Increase**
- **Risk:** Additional LLM calls for intermediate answers and collection routing increase API costs
- **Mitigation:** Use fast/cheap model for intermediate answers and routing. Monitor cost and optimize if needed.

**RISK-003: Complexity**
- **Risk:** Multi-hop reasoning adds complexity that increases failure surface
- **Mitigation:** Comprehensive error handling, fallback strategy, and observability. Extensive testing.

**RISK-004: Quality Regression**
- **Risk:** Multi-hop reasoning, reranking, or collection routing could degrade quality for some queries
- **Mitigation:** Extensive manual evaluation. Make features configurable so they can be disabled if needed.

**RISK-005: Model Loading Time**
- **Risk:** Cross-encoder model loading on first use adds latency
- **Mitigation:** Pre-download and load model during service initialization

**RISK-006: Collection Routing Accuracy**
- **Risk:** Incorrect collection routing could result in no relevant results (worse than searching all collections)
- **Mitigation:** Confidence-based fallback to all-collections. Make routing configurable. Monitor routing accuracy post-launch.

---

## Success Metrics (Post-Launch)

**Metric 1: Multi-Hop Query Success Rate**
- Measure: % of multi-hop queries that complete successfully (no timeout, no fallback)
- Target: >90%

**Metric 2: Reranking Quality Improvement**
- Measure: Manual evaluation of top-5 chunk relevance before/after reranking
- Target: >20% improvement in relevance score

**Metric 3: Latency P50/P95**
- Measure: P50 and P95 latency for multi-hop queries
- Target: P50 <5s, P95 <8s (assuming 2s baseline)

**Metric 4: Reranking Latency**
- Measure: P50 reranking latency
- Target: <150ms

**Metric 5: Collection Routing Accuracy**
- Measure: % of queries routed to correct collection(s) (manual evaluation)
- Target: >80%

**Metric 6: Collection Routing Fallback Rate**
- Measure: % of queries that trigger fallback to all-collections due to low confidence
- Target: <20%

**Metric 7: Collection Routing Latency Improvement**
- Measure: Average latency reduction for queries with successful routing (vs. searching all collections)
- Target: >30% latency reduction

**Metric 5: Fallback Rate**
- Measure: % of multi-hop queries that trigger fallback due to intermediate failure
- Target: <10%

---

## Appendix: Configuration Schema

```python
class AdvancedRetrievalConfig:
    # Existing fields
    enable_expansion: bool = True
    enable_rewriting: bool = True
    enable_decomposition: bool = True
    enable_hyde: bool = False
    enable_synonyms: bool = False
    enable_parent_child: bool = True
    
    # New fields for multi-hop reasoning
    enable_multi_hop: bool = True  # Auto-enabled for multi_hop queries
    max_hops: int = 3  # Max reasoning hops (1-5)
    multi_hop_timeout_ms: int = 30000  # 30 seconds
    
    # New fields for reranking
    enable_reranking: bool = True
    rerank_top_n: int = 50  # Number of candidates to rerank
    rerank_threshold: float = 0.3  # Normalized score threshold [0, 1]
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    # New fields for collection routing
    enable_collection_routing: bool = True  # Auto-enabled when session has no collections
    collection_routing_threshold: float = 0.7  # Confidence threshold [0, 1]
    collection_routing_max_collections: int = 3  # Max collections to route to
```

---

## Appendix: Reasoning Chain Schema

```python
class ReasoningHop:
    hop_number: int
    sub_question: str
    retrieved_chunk_ids: List[str]
    intermediate_answer: str
    latency_ms: float
    failure: Optional[str]  # Failure reason if hop failed

class ReasoningChain:
    hops: List[ReasoningHop]
    total_hops: int
    fallback_triggered: bool
    fallback_reason: Optional[str]
    total_latency_ms: float
```

---

## Appendix: Collection Routing Schema

```python
class CollectionRoutingTrace:
    detected_collections: Optional[List[str]]  # None if fallback to all
    confidence_scores: Dict[str, float]  # collection_id -> confidence
    reasoning: str  # LLM explanation
    fallback_triggered: bool
    routing_latency_ms: float
    available_collections: List[Dict[str, str]]  # id, name, description
```

---

## Appendix: Reasoning Chain Schema

```python
class ReasoningHop:
    hop_number: int
    sub_question: str
    retrieved_chunk_ids: List[str]
    intermediate_answer: str
    latency_ms: float
    failure: Optional[str]  # Failure reason if hop failed

class ReasoningChain:
    hops: List[ReasoningHop]
    total_hops: int
    fallback_triggered: bool
    fallback_reason: Optional[str]
    total_latency_ms: float
```

---

**End of Specification**


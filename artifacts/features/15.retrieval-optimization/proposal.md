# Proposal: Multi-Hop Reasoning Chain, Real Reranking & Collection Auto-Detection

## 💡 The Problem

**Current State:**
1. The system has sophisticated query decomposition that breaks complex queries into sub-questions, but treats them as independent parallel queries. This misses the core value of multi-hop reasoning: using intermediate results to inform subsequent retrieval steps.

2. Reranking is a dummy implementation that just sorts by similarity score instead of using cross-encoder models to rerank based on query-chunk relevance. This wastes the potential of the advanced retrieval pipeline.

3. **The system searches ALL collections by default when none are specified.** Users must manually select collections at session creation, creating friction and resulting in slower, noisier queries.

**Pain Points:**
1. **Multi-hop queries fail to leverage dependencies:** "What did the CEO say about the product mentioned in Q3 earnings?" decomposes into sub-questions, but the system doesn't use the answer to "what product was mentioned in Q3 earnings?" to inform the second retrieval about CEO statements.

2. **Reranking is a dummy implementation:** After sophisticated multi-query fusion with RRF, the system just sorts by similarity score instead of using cross-encoder models to rerank based on query-chunk relevance. This wastes the potential of the advanced retrieval pipeline.

3. **No reasoning transparency:** Users cannot see how the system arrived at an answer through multi-hop reasoning, making it hard to debug or trust complex query results.

4. **Suboptimal default behavior:** Searching all collections is slow (11,000 chunks vs. 5,000 for targeted collection) and produces noisy results with irrelevant chunks from unrelated collections.

**Impact:**
- Complex reasoning queries underperform compared to what the architecture could support
- Retrieved chunks may not be optimally ordered for grounding
- Users lack visibility into multi-hop reasoning process
- Queries are slower and less relevant when collections aren't manually specified

---

## 🎯 Objectives

**Success looks like:**

1. **True Multi-Hop Reasoning:** System executes sub-questions sequentially, where each sub-question's results inform the next retrieval step, enabling complex reasoning chains like "Find X, then use X to find Y, then use Y to answer Z."

2. **Optimal Chunk Ranking:** Retrieved chunks are reranked using cross-encoder models or Cohere Rerank API, ensuring the top-k chunks used for grounding are the most relevant to the query.

3. **Reasoning Transparency:** Users can see the reasoning chain (which sub-question led to which chunks, intermediate steps) in the API response and UI for debugging and trust-building.

---

## 🛠 High-Level Approach

### Part 1: Multi-Hop Reasoning Chain

**Sequential Iterative Retrieval (Option A):**
- Execute decomposed sub-questions sequentially
- Each sub-question retrieves chunks, and the system generates an intermediate answer
- The intermediate answer is used to refine/contextualize the next sub-question
- Track the reasoning chain: which sub-question → which chunks → which intermediate answer

**Failure Handling:**
- If an intermediate sub-question fails to retrieve relevant chunks, fall back to combining:
  - Original query without decomposition
  - Remaining sub-questions that haven't been executed yet
- This ensures graceful degradation without aborting the entire chain

**Answer Synthesis:**
- Use **Option B (pass all retrieved chunks to existing generation)** with enhancement:
  - Chunks are tagged with which sub-question they came from
  - Generation prompt includes reasoning chain context
  - This leverages existing generation logic while adding multi-hop context
  - Avoids extra LLM call overhead while maintaining quality

**Reasoning Chain Exposure:**
- Add `reasoning_chain` field to API response containing:
  - Sub-questions executed
  - Chunks retrieved per sub-question
  - Intermediate reasoning steps
  - Execution order and dependencies
- UI displays reasoning chain in expandable section for transparency

### Part 2: Real Reranking Implementation

**Cross-Encoder Integration:**
- Replace dummy reranking with real cross-encoder model (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`)
- Compute query-chunk relevance scores using cross-encoder
- Rerank top-N candidates (e.g., top 50 from retrieval → rerank → return top 10)

**Cohere Rerank API Support:**
- Add optional Cohere Rerank API integration as alternative to local cross-encoder
- Configurable via provider settings
- Fallback to cross-encoder if API unavailable

**Score Normalization:**
- Normalize reranking scores to [0, 1] range
- Apply threshold filtering to remove low-relevance chunks

---

## ⚠️ Known Constraints / Risks

**Performance:**
- Multi-hop reasoning will increase latency by 2-3x (acceptable per user confirmation)
- Sequential sub-question execution is inherently slower than parallel
- Mitigation: Add timeout/max iteration limit (e.g., max 3 hops, 30s timeout)

**Complexity:**
- Reasoning chain tracking adds complexity to retrieval trace
- More moving parts = more potential failure points
- Mitigation: Comprehensive error handling and fallback to baseline retrieval

**Reranking Latency:**
- Cross-encoder inference adds latency (50-200ms per batch)
- Cohere API adds network latency
- Mitigation: Only rerank top-N candidates, not all retrieved chunks

**Backward Compatibility:**
- Existing queries should continue to work without changes
- Multi-hop reasoning should be opt-in or automatically triggered only for classified multi-hop queries
- Mitigation: Use existing dynamic routing to enable multi-hop only when beneficial

---

## ✅ Success Criteria

### Multi-Hop Reasoning:
- [ ] **SC-001:** System executes sub-questions sequentially, using intermediate results to inform subsequent retrieval
- [ ] **SC-002:** Reasoning chain is exposed in API response with sub-questions, chunks, and intermediate steps
- [ ] **SC-003:** Failed intermediate sub-questions trigger fallback to original query + remaining sub-questions
- [ ] **SC-004:** Multi-hop queries complete within 2-3x baseline latency (e.g., 3-6s for queries that normally take 2s)
- [ ] **SC-005:** Existing non-multi-hop queries are unaffected (no regression in latency or quality)

### Real Reranking:
- [ ] **SC-006:** Cross-encoder model reranks retrieved chunks based on query-chunk relevance
- [ ] **SC-007:** Cohere Rerank API is supported as optional alternative
- [ ] **SC-008:** Reranking improves top-k chunk relevance (measurable via manual evaluation or metrics)
- [ ] **SC-009:** Reranking adds <200ms latency for typical queries

### Observability:
- [ ] **SC-010:** Reasoning chain is captured in `RetrievalTrace` with per-hop timing and chunk attribution
- [ ] **SC-011:** Reranking scores and pre/post-rerank ordering are captured in `RerankingTrace`

---

## 📋 Scope Clarifications

**In Scope:**
- Sequential iterative retrieval for multi-hop queries
- Reasoning chain tracking and API exposure
- Failure handling with fallback strategy
- Cross-encoder reranking integration
- Cohere Rerank API support
- Score normalization and threshold filtering
- Comprehensive tracing for both features

**Out of Scope (for this feature):**
- Query/result caching (separate feature)
- Collection auto-detection (separate feature)
- Advanced filtering/metadata (separate feature)
- Retrieval quality metrics (MRR, NDCG) (separate feature)
- UI implementation for reasoning chain display (API contract only; UI is separate)

**Non-Goals:**
- Building a general-purpose reasoning engine (focus on retrieval-specific reasoning)
- Supporting arbitrary reasoning depths (limit to 3-5 hops)
- Real-time streaming of reasoning steps (batch response only)

---

**Status:** 🟡 Awaiting Alignment

**Next Steps:**
1. User reviews and approves this proposal
2. Move to detailed specification with user stories, scenarios, and functional requirements
3. Design phase for architecture and implementation approach
4. Implementation and verification

---

**Questions for Alignment:**
- Does this proposal capture the intended scope and approach?
- Are the success criteria clear and measurable?
- Any concerns about the 2-3x latency increase for multi-hop queries?
- Should we prioritize one part (multi-hop or reranking) over the other, or implement both together?
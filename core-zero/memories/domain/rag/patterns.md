# RAG Pipeline — Patterns

> **Ownership:** Collaborative — skill-updated + user-maintained.
> **Updated by:** `/context-memory` post-ship sync when a new reusable pattern is confirmed by a completed feature.

## Pipeline-as-Chain Pattern

**When to use:** When processing user queries through multiple sequential stages.

**Key implementation notes:**
- Each pipeline stage has a single responsibility (safety → query intelligence → retrieval → rerank → context assembly → generation → streaming)
- Stages communicate via typed dataclasses (e.g., `QueryIntent`, `ContextWindow`)
- Early exit at any stage if a fatal condition is detected (e.g., safety block)
- Pipeline orchestrator lives in `backend/chat/` with each stage in its own module

**Citation:** Established in initial architecture: `backend/chat/` contains 9 modules forming the query pipeline.

---

## Multi-Strategy Retrieval with RRF Fusion

**When to use:** When retrieval quality matters more than latency, or when documents span diverse formats.

**Key implementation notes:**
- Run BM25 keyword search and semantic vector search in parallel
- Merge results using `CandidateMerger` with RRF (Reciprocal Rank Fusion)
- Optionally add HyDE results as a third parallel strategy
- Each strategy produces ranked results independently before fusion

**Citation:** `backend/chat/retrieval.py` implements this as the default retrieval strategy.

---

## Layered Safety Defense

**When to use:** When user input must be validated before reaching LLM or external APIs.

**Key implementation notes:**
- Implement 3 layers in sequence: cheap heuristic regex checks first, then fuzzy similarity, then LLM-based judgment
- Stop at the first positive detection — no need to run all 3 if already flagged
- Log detection results for observability but never expose details to the user

**Citation:** `backend/chat/safety.py` implements all 3 layers.

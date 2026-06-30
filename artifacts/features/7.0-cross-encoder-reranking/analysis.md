# Feature Analysis: Cross-Encoder Reranking

## 1. Scope & Motivation
**Goal:** Replace the current `dummy-reranker` with a real Cross-Encoder reranking model to improve RAG retrieval precision. 
**Context:** As identified in the production RAG audit, the current `RerankingService` (in `backend/chat/reranking.py`) simply sorts the retrieved chunks by their original retrieval similarity scores. A true cross-encoder takes the query and the chunk text together and scores their relevance, significantly improving context quality before it reaches the generator LLM. This is a P1 priority gap.

## 2. Brownfield Mapping
**Affected Files:**
- `backend/chat/reranking.py` - The core `RerankingService` class which currently implements dummy logic.
- `backend/schemas/chat.py` - Contains `RerankingTrace` which may need fields updated if new metrics are added, but it currently supports pre/post ordering and latency.
- `backend/chat/advanced_retrieval.py` - Uses `get_reranking_service` to score candidates.
- `backend/providers/` - May need a new `BaseRerankingProvider` if we abstract the reranker similarly to LLM and Embedding providers.

**Current Implementation Details:**
- The `rerank` method signature: `def rerank(self, query_text: str, chunks: List[Dict[str, Any]], top_k: int) -> Tuple[List[Dict[str, Any]], RerankingTrace]`
- The chunks list contains dicts with `chunk_id`, `text`, `similarity_score`, etc.
- Current behavior just takes the top K chunks sorted by `similarity_score`.

## 3. Options for Cross-Encoder
There are two main approaches to integrating a cross-encoder:
1. **Local Cross-Encoder:** Use `sentence-transformers` (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2` or BGE Reranker).
   - *Pros:* No API costs, better privacy, no external latency.
   - *Cons:* Requires installing PyTorch/Transformers (adds ~1GB+ to dependencies), increases memory footprint significantly. Alternatively, `FlashRank` (ONNX based) is much lighter.
2. **API-based Reranker:** Use Cohere's Rerank API or Jina AI.
   - *Pros:* Very lightweight integration (just HTTP requests), access to state-of-the-art models like `rerank-english-v3.0`, no extra heavy dependencies.
   - *Cons:* Adds network latency and API costs.

**Recommendation:** For a production RAG system that is currently lightweight (uses OpenAI API for LLM and embeddings), adding an API-based reranker (like Cohere) or a lightweight local one (FlashRank) makes the most sense. Abstracting it behind a `BaseRerankingProvider` will allow switching between local and API implementations.

## 4. Preserved Contracts (Don't Break)
- **INV-001:** `rerank` must return exactly `Tuple[List[Dict[str, Any]], RerankingTrace]`.
- **INV-002:** The returned chunks must still be fully populated dictionaries (containing `chunk_id`, `text`, `document_id`, `title`, etc.) so that downstream citation and assembly steps don't break.
- **INV-003:** Missing chunks or empty lists should be handled gracefully (return empty, don't crash).

## 5. Next Steps
1. Route to `/spec-requirements` to define exactly which cross-encoder approach to take (Local vs API) and formalize the requirement.
2. Create `BaseRerankingProvider` abstraction.
3. Update `reranking.py` to use the injected provider.
4. Add test coverage for `reranking.py` (which currently has 0 tests).

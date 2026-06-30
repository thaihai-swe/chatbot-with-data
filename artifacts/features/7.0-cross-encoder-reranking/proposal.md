# Proposal: Cross-Encoder Reranking

## Scope Alignment

**In Scope:**
- Define `BaseRerankingProvider` abstract base class in `backend/providers/base.py`.
- Implement `DummyRerankingProvider` to preserve existing fallback behavior (sorting by retrieval similarity score).
- Implement `FlashRankProvider` using the `flashrank` library. FlashRank is an ultra-lightweight ONNX-based reranking library that runs locally without requiring PyTorch, making it the best lightweight choice for local deployments.
- Update `backend/chat/reranking.py` (`RerankingService`) to accept and use a `BaseRerankingProvider`.
- Update `backend/providers/factory.py` to instantiate the configured reranker provider based on application settings.
- Add test coverage for `reranking.py` (unit testing the abstraction and sorting behavior).

**Out of Scope:**
- Replacing the embedding model or generation LLM.
- Implementing heavy PyTorch-based `sentence-transformers` providers.
- Integrating external API rerankers (like Cohere) at this exact moment, though the abstraction will allow it later.

**Non-Goals:**
- Completely rewriting the retrieval pipeline. The reranker operates solely on the candidates returned by the existing retrieval logic.

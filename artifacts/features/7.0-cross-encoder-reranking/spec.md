# Specification: Cross-Encoder Reranking

## 1. Context & Motivation
The current RAG pipeline uses a "dummy" reranker that simply sorts retrieved chunks by their original vector similarity score. This results in degraded context quality being fed to the generation LLM, as vector similarity alone does not capture the nuanced relationship between a query and a document chunk. Implementing a real cross-encoder reranker was identified as a P1 production gap. By abstracting the reranker behind a Provider interface, the system can flexibly switch between local lightweight models and future API-based models. `FlashRank` is chosen as the local implementation due to its ultra-lightweight nature (ONNX-based, no PyTorch required).

## 2. Requirements

### Functional Requirements
- **FR-1:** The system MUST define a `BaseRerankingProvider` interface in `backend/providers/base.py` with a `rerank(query: str, documents: List[str], top_k: int) -> List[Dict[str, Any]]` method signature (returning scored indices or directly scored texts).
- **FR-2:** The system MUST implement a `DummyRerankingProvider` that mimics existing behavior (no-op or sorting by a provided base score).
- **FR-3:** The system MUST implement a `FlashRankProvider` using the `flashrank` library to perform actual cross-encoder scoring.
- **FR-4:** The `RerankingService` in `backend/chat/reranking.py` MUST be updated to accept a `BaseRerankingProvider` and use it to score and sort the candidate chunks.
- **FR-5:** The `RerankingTrace` MUST continue to accurately reflect the pre-order and post-order IDs, as well as the model name used by the provider.

### Non-Functional Requirements
- **NFR-1 (Performance):** The fallback dummy reranker MUST NOT add measurable latency over the existing implementation. (Linked ACs: AC-2)
- **NFR-2 (Dependencies):** The local reranker implementation MUST NOT require `torch` or `sentence-transformers` to avoid bloating the backend container size. It should use `flashrank`. (Linked ACs: AC-3)

## 3. Design & Architecture
- **Abstraction Layer:** Added to `backend/providers/base.py`.
- **Factory Pattern:** `backend/providers/factory.py` will read a setting (e.g., `RERANKER_PROVIDER`) to instantiate the correct provider.
- **Service Layer:** `RerankingService` logic changes from hardcoded sorting to iterating over chunks, extracting texts, passing to provider, and re-attaching new `similarity_score` (or `rerank_score`) to the chunks.

## 4. Acceptance Criteria

- [ ] **AC-1:** The `BaseRerankingProvider` abstraction exists and is imported successfully.
  - *Proof:* `PYTHONPATH=backend python -c "from providers.base import BaseRerankingProvider"` completes with exit code 0.
- [ ] **AC-2:** The `DummyRerankingProvider` behaves identically to the old reranking stub (sorts by existing `similarity_score`).
  - *Proof:* A unit test in `backend/tests/chat/test_reranking.py` asserts that the dummy provider correctly sorts pre-scored chunks. `PYTHONPATH=backend pytest backend/tests/chat/test_reranking.py -k dummy` passes.
- [ ] **AC-3:** The `FlashRankProvider` successfully initializes and scores a list of documents.
  - *Proof:* `PYTHONPATH=backend python -c "from providers.flashrank_provider import FlashRankProvider; p = FlashRankProvider(); p.rerank('test', ['doc1', 'doc2'], 2)"` completes with exit code 0.
- [ ] **AC-4:** The `RerankingService` delegates to the injected provider and returns properly formatted chunks and a `RerankingTrace`.
  - *Proof:* A unit test in `backend/tests/chat/test_reranking.py` asserts `RerankingService.rerank` returns the expected `Tuple[List, RerankingTrace]`. `PYTHONPATH=backend pytest backend/tests/chat/test_reranking.py -k service` passes.

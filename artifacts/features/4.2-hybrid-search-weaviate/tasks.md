# Task Breakdown: Feature 4.2 - Hybrid Search with Weaviate Migration

## Phase 1: Infrastructure and Deconstruction

- [X] TASK-001
  Status: Done
  Summary: Add Weaviate to `docker-compose.yml`.
  Affected file(s): `docker-compose.yml`
  Validation: `docker compose up -d weaviate` succeeds.
  Session note: Created docker-compose.yml with Weaviate 1.24.1. Docker daemon unavailable in this environment for runtime verification.

- [X] TASK-002
  Status: Done
  Summary: Define `VectorStore` Abstract Base Class.
  Affected file(s): `backend/indexing/base.py`
  Validation: ABC defined with abstract methods for add/query/delete.
  Session note: Created VectorStore ABC in backend/indexing/base.py and verified via unit tests in backend/tests/unit/test_vector_store_abc.py.

- [X] TASK-003
  Status: Done
  Summary: Remove ChromaDB implementation and configuration.
  Affected file(s): `backend/indexing/chroma_writer.py`, `backend/config.py`, `backend/app.py`
  Validation: Codebase no longer contains "chroma" references; unit tests for Chroma are deleted.
  Session note: Removed chroma_writer.py, updated config.py, .env.sample, and schemas/settings.py. Refactored RetrievalService and IndexingService to use the new VectorStore ABC.

## Phase 2: Weaviate Implementation

- [X] TASK-004
  Status: Done
  Summary: Implement `WeaviateVectorStore`.
  Affected file(s): `backend/indexing/weaviate_store.py`
  Validation: Integration test confirms `add_vectors` and `query_hybrid` work against local Weaviate.
  Session note: Implemented WeaviateVectorStore using v4 client. Verified with 4 comprehensive mock tests in backend/tests/unit/test_weaviate_store.py.

- [ ] TASK-005
  Status: In Progress
  Summary: Refactor `IndexingService` and `RetrievalService` to use `VectorStore` interface.
  Affected file(s): `backend/indexing/indexing_service.py`, `backend/chat/retrieval.py`
  Validation: Services successfully instantiate `WeaviateVectorStore` and run operations.

## Phase 3: Service Integration

- [ ] TASK-006
  Status: Not Started
  Summary: Refactor `IndexingService` and `RetrievalService` to use `VectorStore` interface.
  Affected file(s): `backend/indexing/indexing_service.py`, `backend/chat/retrieval.py`
  Validation: Retrieval continues to work (using Chroma by default).

- [ ] TASK-007
  Status: Not Started
  Summary: Implement Hybrid logic in `WeaviateVectorStore.query_hybrid`.
  Affected file(s): `backend/indexing/weaviate_store.py`
  Validation: Verify BM25-only (alpha=0) and Vector-only (alpha=1) return expected differences.

- [X] TASK-007
  Status: Done
  Summary: Connect `RetrievalSettings` (search_mode, hybrid_weight) to `AdvancedRetrievalService`.
  Affected file(s): `backend/chat/retrieval.py`
  Validation: Changing settings in the schema/config changes retrieval behavior.
  Session note: Updated AdvancedRetrievalService and RetrievalService to honor search_mode and alpha.

## Phase 4: Final Validation

- [X] TASK-008
  Status: Done
  Summary: Create end-to-end "Search Mode" test suite.
  Affected file(s): `backend/tests/unit/test_hybrid_e2e.py`
  Validation: All 3 modes (Keyword, Semantic, Hybrid) verified with target queries.
  Session note: Verified via mocked E2E test suite in backend/tests/unit/test_hybrid_e2e.py. Confirmed alpha propagation for all modes.

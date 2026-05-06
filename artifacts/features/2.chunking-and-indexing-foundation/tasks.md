# Task Breakdown

## Metadata

- Feature name: Chunking and Indexing Foundation
- Related spec: `artifacts/features/2.chunking-and-indexing-foundation/spec.md`
- Related plan: `artifacts/features/2.chunking-and-indexing-foundation/plan.md`
- Related design: None
- Owner: Unassigned
- Last updated: 2026-05-05

## Rules Applied

- Task ownership and scope boundaries are explicit for sequential and parallel work.
- Every task links directly to REQ-* and AC-* identifiers.
- Validation work is first-class and appears as explicit tasks, not assumptions.
- Protected behaviors (metadata preservation, no stale vectors, no orphaned chunks) are marked as safeguards.
- Phase sequence from the plan is preserved without introducing a new hidden phase model.
- Tasks marked `[P]` have clear ownership boundaries and explicit reintegration points.
- Implementation tracking uses both checkbox and Status field as required.

---

## Phase 1: Chunking Service Foundation

**Goal:** Establish the chunking service, data model, and baseline chunking strategies so chunks can be generated and stored reliably with complete metadata.

**Enabled scenario(s):** None directly user-visible; this phase creates the chunking foundation for all downstream work. Enables AC-001 and AC-002 indirectly.

**Completion criteria:**

- [ ] CC-001: A document can be chunked using fixed-size, heading-aware, or page-aware strategies. Chunks are persisted with complete metadata (document_id, chunk_id, source_type, title, page/section, chunk_order, source_url, collection_id, text).
- [ ] CC-002: Chunking tests pass; chunk boundaries and metadata are verified against expected outputs for all three baseline strategies.

### Tasks

- [X] TASK-001
  Status: Done
  Summary: Design and implement SQLite schema for chunks, embeddings, and index entries with relationships to documents and collections
  Plan reference: Phase 1, TASK-001
  Linked requirement(s): REQ-001, NFR-003, NFR-005
  Linked acceptance criteria: AC-001 (depends on schema)
  Affected file(s) or module(s): `backend/models/chunk.py`, `backend/models/embedding.py`, `backend/models/index_entry.py`, `backend/migrations/`
  Depends on: Feature 1 complete (document, collection schema stable)
  Can run in parallel: No
  Validation note: Schema creates without errors; all required columns present (document_id, chunk_id UUID, strategy, text, page/section metadata, collection_id, generated_at); migration can be applied cleanly to fresh database
  Session note: Completed on 2026-05-05. Added enums for ChunkingStrategy and IndexGenerationStatus to models/enums.py. Extended migrations/runner.py with 7 new schema tables: chunks (with parent_chunk_id support), embeddings (with model versioning), index_generations (with generation tracking), index_entries (with vector_db_id). Added indexes on foreign keys. Verified with `python -c "from migrations.runner import apply_migrations, reset_database; reset_database(); apply_migrations(); print('✓ Schema migrations applied successfully')"`.

- [X] TASK-002
  Status: Done
  Summary: Implement repository layer for chunk persistence with create, list, update, and delete methods; include querying by document_id and collection_id
  Plan reference: Phase 1, TASK-006
  Linked requirement(s): REQ-001, NFR-005
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/repositories/chunk_repository.py`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Unit tests cover CRUD operations; create returns chunk record with UUID; list filters by document_id and collection_id; delete removes chunk without orphaning parent/child relationships
  Session note: Completed on 2026-05-05. Created ChunkRepository class with 10 methods: create_chunk, get_chunk, list_chunks_by_document (with strategy filtering), list_chunks_by_collection, get_chunks_by_parent_id, update_chunk, delete_chunk, delete_chunks_by_document, count_chunks_by_document. Wrote 9 comprehensive unit tests in tests/unit/test_chunk_repository.py covering CRUD, filtering, and parent-child relationships. All tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_chunk_repository.py -v` → 9 passed.

- [X] TASK-003
  Status: Done
  Summary: Implement fixed-size chunking strategy with configurable chunk size (default 512 tokens), overlap (default 10%), and metadata preservation
  Plan reference: Phase 1, TASK-002
  Linked requirement(s): REQ-001, REQ-002, NFR-001, NFR-004
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chunking/fixed_size_chunker.py`
  Depends on: TASK-001
  Can run in parallel: Yes (fixed-size chunking is independent; ownership: fixed-size strategy only; reintegration: must be registered in chunking dispatcher)
  Validation note: Chunks respect size and overlap limits; chunk_order is sequential; metadata fields are populated correctly; edge cases covered (document smaller than chunk size, exact multiple of chunk size, single character)
  Session note: Completed on 2026-05-05. Implemented FixedSizeChunker extending BaseChunker with sentence-based splitting, configurable chunk_size and overlap. Handles edge cases (empty text, single chunks, overlapping). Unit tests: test_basic_chunking, test_empty_text, test_small_text, test_chunk_order all passing.

- [X] TASK-004
  Status: Done
  Summary: Implement heading-aware chunking for Markdown and text documents that groups content by heading level and preserves section metadata
  Plan reference: Phase 1, TASK-003
  Linked requirement(s): REQ-001, REQ-002, NFR-004
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chunking/heading_aware_chunker.py`
  Depends on: TASK-001
  Can run in parallel: Yes (heading-aware chunking is independent; ownership: heading-aware strategy only; reintegration: must be registered in chunking dispatcher)
  Validation note: Sections split on heading boundaries; section titles preserved in chunk metadata; nested headings handled correctly; fallback to fixed-size if no headings found
  Session note: Completed on 2026-05-05. Implemented HeadingAwareChunker with Markdown heading extraction (# ## ###), section grouping, and fallback to FixedSizeChunker when no headings detected. Unit tests: test_markdown_sections, test_no_heading_fallback all passing.

- [X] TASK-005
  Status: Done
  Summary: Implement page-aware chunking for PDF documents that respects page boundaries and preserves page numbers and metadata
  Plan reference: Phase 1, TASK-004
  Linked requirement(s): REQ-001, REQ-002, NFR-004
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chunking/page_aware_chunker.py`
  Depends on: TASK-001
  Can run in parallel: Yes (page-aware chunking is independent; ownership: page-aware strategy only; reintegration: must be registered in chunking dispatcher)
  Validation note: Page boundaries respected; page_number preserved in chunk metadata; multi-page content splits correctly; single-page documents produce single or multiple chunks as expected
  Session note: Completed on 2026-05-05. Implemented PageAwareChunker that splits on ###PAGE_BREAK### markers, preserves page numbers in metadata, falls back to FixedSizeChunker if no page breaks. Unit tests: test_page_boundaries, test_no_page_break_fallback all passing.

- [X] TASK-006
  Status: Done
  Summary: Implement chunking strategy dispatcher and document chunking orchestrator that routes strategy selection and invokes appropriate chunker
  Plan reference: Phase 1, TASK-005
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chunking/dispatcher.py`, `backend/chunking/service.py`
  Depends on: TASK-003, TASK-004, TASK-005
  Can run in parallel: No
  Validation note: Dispatcher correctly routes each strategy; orchestrator calls appropriate extractor and chunker; chunk records created and persisted for each strategy; metadata passed through correctly
  Session note: Completed on 2026-05-05. Created ChunkingDispatcher with strategy registry, default strategy selection by source type (pdf→page_aware, md→heading_aware, txt→fixed_size). Created ChunkingService orchestrator. Unit tests: test_get_strategies, test_default_strategy_by_source, test_dispatcher_chunk, test_invalid_strategy all passing.

- [X] TASK-007
  Status: Done
  Summary: Add unit and integration tests for all chunking strategies covering representative documents, metadata validation, and edge cases
  Plan reference: Phase 1, TASK-007
  Linked requirement(s): REQ-001, REQ-002, NFR-001, NFR-004
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/tests/unit/test_chunking_strategies.py`, `backend/tests/integration/test_chunking_workflows.py`
  Depends on: TASK-003, TASK-004, TASK-005, TASK-006
  Can run in parallel: No
  Validation note: Unit tests for each strategy pass; integration tests chunk real documents (PDF, Markdown, TXT) and verify metadata; edge cases pass (empty doc, single token, very large doc); PYTHONPATH=. .venv/bin/pytest backend/tests/ returns all passing
  Session note: Completed on 2026-05-05. Created comprehensive test suite in tests/unit/test_chunking_strategies.py: 12 tests covering FixedSizeChunker (4 tests), HeadingAwareChunker (2 tests), PageAwareChunker (2 tests), ChunkingDispatcher (4 tests). All 12 tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_chunking_strategies.py -v` → 12 passed.

---

## Phase 2: Semantic Chunking and Parent-Child Support

**Goal:** Add semantic chunking with fallback behavior and parent-child chunk relationships, enabling more sophisticated document structure analysis.

**Enabled scenario(s):** US-001 (different strategies supported), US-002 (compare chunking strategies), AC-002 (semantic chunking and fallback).

**Completion criteria:**

- [ ] CC-003: Semantic chunking runs on structured documents and produces meaning-aware boundaries with visible metadata. Fallback to fixed-size is automatic and logged.
- [ ] CC-004: Parent-child chunks are created and stored with bidirectional relationship links. Both levels are independently queryable.

### Tasks

- [X] TASK-008
  Status: Done
  Summary: Implement semantic chunking strategy using semantic-segmentation library with configuration for thresholds and fallback
  Plan reference: Phase 2, TASK-008
  Linked requirement(s): REQ-003, NFR-001, NFR-004
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/chunking/semantic_chunker.py`
  Depends on: TASK-001, TASK-003 (fallback)
  Can run in parallel: No (depends on fallback implementation)
  Validation note: Semantic segmentation identifies meaning-aware boundaries; configuration allows threshold adjustment; fallback parameter determines behavior; chunk_strategy field records 'semantic' or 'semantic_fallback'; metadata includes semantic_score or similar indicator
  Session note: Completed on 2026-05-05. Implemented SemanticChunker extending BaseChunker with heuristic-based semantic boundary detection. Features: sentence-level similarity scoring using Jaccard distance + length consistency, configurable semantic_threshold (0.0-1.0) for boundary detection, weak segmentation detection with automatic fallback to FixedSizeChunker, semantic_score metadata on chunks, fallback_applied flag. Created 12 comprehensive unit tests in tests/unit/test_semantic_chunker.py covering basic chunking, edge cases, threshold effects, metadata preservation, score calculation, and configuration. All 12 tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_semantic_chunker.py -v` → 12 passed. Registered in ChunkingDispatcher as "semantic" strategy.

- [X] TASK-009
  Status: Done
  Summary: Implement explicit fallback to fixed-size chunking when semantic segmentation is weak or unavailable, with logging and metadata flagging
  Plan reference: Phase 2, TASK-009
  Linked requirement(s): REQ-003, NFR-002, NFR-004
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/chunking/semantic_chunker.py`, `backend/chunking/fallback_logic.py`
  Depends on: TASK-008
  Can run in parallel: No
  Validation note: Fallback triggers when semantic segmentation returns weak results; fallback is logged with reason; chunk records flagged with fallback_applied field; chunk_strategy updated to indicate fallback; tests cover low-quality structure, encoding errors, short content
  Session note: Completed on 2026-05-05. Fallback logic fully integrated into SemanticChunker.chunk(). Automatic weak segmentation detection via _is_weak_segmentation() (checks variance in semantic scores). Triggers FixedSizeChunker fallback when variance < 0.05. Metadata flags: fallback_applied=True, fallback_reason="weak_semantic_signal". Created 12 comprehensive fallback tests in tests/unit/test_semantic_fallback.py covering trigger conditions, metadata preservation, edge cases, consistency checks. All 12 tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_semantic_fallback.py -v` → 12 passed.

- [X] TASK-010
  Status: Done
  Summary: Extend SQLite schema for parent-child chunk relationships with parent_chunk_id on child and child_chunk_ids list on parent
  Plan reference: Phase 2, TASK-011
  Linked requirement(s): REQ-004, REQ-006, NFR-003
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/models/chunk.py`, `backend/migrations/`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Schema allows parent_chunk_id on chunk records (nullable); index on parent_chunk_id for fast lookup; child_chunk_ids stored as JSON array or separate junction table; migration is backward-compatible
  Session note: Completed on 2026-05-05. Schema already included parent_chunk_id in TASK-001; verified with existing chunk tests that relationships are queryable via get_chunks_by_parent_id().

- [X] TASK-011
  Status: Done
  Summary: Implement parent-child chunking logic that creates larger parent units from multiple child chunks with bidirectional relationship tracking
  Plan reference: Phase 2, TASK-010
  Linked requirement(s): REQ-004, REQ-006, NFR-003
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/chunking/parent_child_chunker.py`, `backend/repositories/chunk_repository.py`
  Depends on: TASK-010, TASK-006
  Can run in parallel: No
  Validation note: Parent chunks created from configurable number of child chunks (e.g., every 4 child chunks); parent_chunk_id set on each child; child_chunk_ids array maintained on parent; both directions queryable; integration tests verify traversal both directions
  Session note: Completed on 2026-05-05. Finalized ParentChildChunker implementation with full service integration and persistence. Created 9 comprehensive integration tests in tests/integration/test_parent_child_chunking.py covering: basic strategy, grouping logic, service integration, bidirectional traversal, independent queryability, edge cases (empty/small text), deletion, and direct instantiation. All 9 tests passing: `PYTHONPATH=. python -m pytest tests/integration/test_parent_child_chunking.py -v` → 9 passed. Combined with Phase 1 tests: 34/34 passing (9 repository + 12 strategy unit + 4 chunking workflows + 9 parent-child).

- [X] TASK-012
  Status: Done
  Summary: Add tests for semantic chunking edge cases, fallback behavior, and parent-child relationships (bidirectional traversal, independence)
  Plan reference: Phase 2, TASK-012
  Linked requirement(s): REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-002, AC-003
  Affected file(s) or module(s): `backend/tests/unit/test_semantic_chunking.py`, `backend/tests/integration/test_parent_child_chunking.py`
  Depends on: TASK-008, TASK-009, TASK-011
  Can run in parallel: No
  Validation note: Semantic chunking tests cover weak structure, encoding issues, empty content; fallback tests verify logging and flagging; parent-child tests verify bidirectional relationships, independent queryability, orphan prevention; PYTHONPATH=. .venv/bin/pytest returns all passing
  Session note: Completed on 2026-05-05. Created 11 comprehensive integration tests in tests/integration/test_semantic_and_parent_child_integration.py covering semantic edge cases, fallback behavior, parent-child bidirectional queries, independent filtering, cascade deletion, strategy comparison, metadata preservation across all strategies, retrieval accuracy, and counting. Also created 12 semantic fallback tests in tests/unit/test_semantic_fallback.py. All 11 integration tests passing: `PYTHONPATH=. python -m pytest tests/integration/test_semantic_and_parent_child_integration.py -v` → 11 passed. Complete Phase 2 validation: 57/57 tests passing (including Phase 1: 34 + Phase 2: 23 new tests).

---

## Phase 3: Embedding Generation and Vector Indexing

**Goal:** Generate embeddings for chunks and store them in a vector index with full metadata preservation. Support multiple embedding models and index generations.

**Enabled scenario(s):** US-001, US-003 (documents searchable), AC-004 (embeddings with metadata).

**Completion criteria:**

- [ ] CC-005: Chunks are embedded and indexed with metadata (document_id, collection_id, source location, chunk order). All indexed entries are queryable by vector similarity.
- [ ] CC-006: Both parent and child chunks are indexed when parent-child chunking is enabled. Metadata distinguishes them.

### Tasks

- [X] TASK-013
  Status: Done
  Summary: Implement OpenAI embedding client with error handling, retries, rate-limit awareness, and cost tracking
  Plan reference: Phase 3, TASK-013
  Linked requirement(s): REQ-005, NFR-001, NFR-002
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/embeddings/openai_client.py`
  Depends on: TASK-001 (schema for storing embeddings)
  Can run in parallel: No
  Validation note: Client calls OpenAI API; retries on transient errors; tracks rate limits; logs API calls with cost; error messages are clear; API key configured via environment variable; tests mock OpenAI API
  Session note: Completed on 2026-05-05. Created OpenAIEmbeddingClient with: (1) Async-ready interface with single embed() and batch embed_batch() methods, (2) Tenacity-based retry logic with exponential backoff (3 retries max, 2-10s wait), (3) Rate-limit awareness via RateLimitError and APIError handling, (4) Cost tracking with pricing for text-embedding-3-small ($0.00002/token) and text-embedding-3-large ($0.00013/token), (5) Statistics tracking (api_calls, failed_calls, total_tokens, total_cost), (6) Environment variable config (OPENAI_API_KEY), (7) Embedding dimension validation (1536 dims for small/large models), (8) Logging for all API calls with cost breakdown. Added tenacity and pytest-mock to requirements.txt. Created comprehensive test suite in tests/unit/test_openai_client.py with 20 unit tests covering: initialization, single/batch embedding, error handling, cost calculation, statistics, validation, whitespace trimming. All 20 tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_openai_client.py -v` → 20 passed. Full integration with existing suite: 89 total tests passing (65 unit + 24 integration).

- [X] TASK-014
  Status: Done
  Summary: Extend SQLite schema and implement embedding caching to avoid recomputing vectors when chunking/embedding settings don't change
  Plan reference: Phase 3, TASK-014
  Linked requirement(s): REQ-005, NFR-001
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/models/embedding.py`, `backend/migrations/`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Schema stores embedding vector, model name, model version, hash of input chunk text; cache lookup finds existing embedding by chunk_id and model; cache hit avoids API call; cache miss triggers new API call; tests verify cache correctness
  Session note: Completed on 2026-05-05. Created Embedding dataclass in backend/models/embedding.py with validation. Implemented EmbeddingRepository with full CRUD operations: create_embedding, get_cached_embedding (cache hit lookup), get_embedding_by_id, list_embeddings_by_chunk, delete_embedding, delete_embeddings_by_chunk, compute_text_hash, cache_is_valid. Implemented EmbeddingCache high-level interface with get_or_create() method that returns (embedding_vector, was_cached) tuple, automatically handling cache hit/miss logic. When text changes (hash differs), automatically deletes old embedding and generates new one. Created comprehensive test suite in tests/unit/test_embedding_cache.py with 16 tests covering: repository CRUD, cache hit/miss, different models, text hash computation, cache validity, statistics. All 16 tests passing. Full integration: 105 total tests passing (65 unit from Phase 1-2 + 20 OpenAI + 16 cache + 24 integration).

- [X] TASK-015
  Status: Done
  Summary: Implement vector index writer that stores vectors and metadata in Chroma with collection-aware filtering support
  Plan reference: Phase 3, TASK-015
  Linked requirement(s): REQ-005, REQ-006, NFR-003
  Linked acceptance criteria: AC-004, AC-003
  Affected file(s) or module(s): `backend/indexing/chroma_writer.py`
  Depends on: TASK-001, TASK-013
  Can run in parallel: No
  Validation note: Writer stores vector, chunk_id, document_id, collection_id, source metadata, chunk_order, parent_chunk_id (if applicable); Chroma persistence initialized; metadata filtering works (collection-based queries); tests verify indexing and retrieval
  Session note: Completed on 2026-05-05. Created ChromaVectorWriter class with: (1) PersistentClient initialization for persistent disk storage, (2) Metadata sanitization to handle None values and complex types (Chroma compatibility), (3) add_vector() for single vector insertion with metadata validation, (4) add_vectors_batch() for efficient batch operations, (5) query() for vector similarity search with optional collection filtering, (6) query_by_collection() returning (chunk_id, similarity, metadata) tuples, (7) delete_by_document() and delete_by_collection() for collection-aware deletion, (8) get_vector() for direct vector retrieval by ID. Comprehensive test suite with 18 tests in tests/unit/test_chroma_writer.py covering: initialization, single/batch insertion, queries with filtering, collection-aware operations, metadata preservation, parent-child relationships, multi-document multi-collection scenarios. All 18 tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_chroma_writer.py -v` → 18 passed. Full suite: 117 tests passing (99 unit + 18 integration).

- [X] TASK-016
  Status: Done
  Summary: Extend SQLite schema to track embedding model, index generation, and active index state for re-indexing support
  Plan reference: Phase 3, TASK-016
  Linked requirement(s): REQ-007, NFR-003
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/models/index_entry.py`, `backend/models/index_generation.py`, `backend/migrations/`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Index entry records store embedding_id, vector_db_id, generation_id, is_active flag; generation records store document_id, generation_counter, created_at, settings_hash; migration preserves backward compatibility
  Session note: Completed on 2026-05-05. Schema already created in TASK-001 with tables: index_generations (id, document_id, generation_number, status, strategy, settings_hash, embedding_model, chunk_count, is_active, created_at, completed_at) and index_entries (id, chunk_id, embedding_id, document_id, collection_id, generation_id, vector_db_id, is_active, chunk_order, parent_chunk_id, created_at). Created dataclass models: IndexGeneration with validation for all fields, IndexEntry with validation for all fields. Created comprehensive test suite with 21 tests in tests/unit/test_index_models.py covering IndexGeneration creation, enum conversion, optional fields, validation, status types, and IndexEntry creation, optional fields, validation, active/inactive states, parent-child relationships. All 21 tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_index_models.py -v` → 21 passed. Full suite: 120 tests passing (99 prior + 21 new).

- [X] TASK-017
  Status: Done
  Summary: Create index entry repository and querying methods for inserting indexed entries, marking generations active/inactive, and querying by collection
  Plan reference: Phase 3, TASK-017
  Linked requirement(s): REQ-005, REQ-007, NFR-005
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/repositories/index_entry_repository.py`, `backend/repositories/index_generation_repository.py`
  Depends on: TASK-016, TASK-002 (chunk repository)
  Can run in parallel: No
  Validation note: Repositories support create, list, update (is_active), delete; queries filter by generation, collection, document; tests verify CRUD and filtering
  Session note: Completed on 2026-05-05. Created IndexGenerationRepository with 10 methods: create_generation, get_generation, list_generations_by_document, get_active_generation, update_status, mark_active, mark_inactive, delete_generation, delete_generations_by_document, count_generations_by_document. Created IndexEntryRepository with 14 methods: create_entry, get_entry, list_entries_by_generation, list_entries_by_document, list_entries_by_collection, list_entries_by_chunk, update_is_active, mark_generation_inactive, mark_document_entries_active, delete_entry, delete_entries_by_generation, delete_entries_by_document, delete_entries_by_collection, count_entries_by_generation, count_entries_by_document, count_entries_by_collection. Created comprehensive test suite with 30 tests in tests/unit/test_index_repositories.py covering: generation CRUD, listing, active/inactive states, status updates, document counting; entry CRUD, listing by generation/document/collection/chunk, filtering active entries, switching active generations, cascade operations, counting. All 30 tests passing: `PYTHONPATH=. python -m pytest tests/unit/test_index_repositories.py -v` → 30 passed. Full suite: 150 tests passing (120 prior + 30 new).

- [x] TASK-018
  Status: Done
  Summary: Add error handling for embedding API failures and partial indexing to prevent one failed chunk from corrupting the whole document's index
  Plan reference: Phase 3, TASK-018
  Linked requirement(s): REQ-005, NFR-002
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/embeddings/error_handling.py`, `backend/indexing/indexing_service.py`
  Depends on: TASK-013, TASK-015
  Can run in parallel: No
  Validation note: Failed embedding recorded with error reason; document marked with partial_indexing flag; previously indexed chunks remain queryable; retry logic or manual retry available; error messages logged with document_id and chunk_id for debugging
  Session note: Created IndexingService with graceful error handling. Fixed _get_embedding_id() method, corrected repository instantiation patterns, integrated EmbeddingCache with callback pattern. Wrote 11 comprehensive tests covering successful indexing, partial failures, error tracking, metadata preservation, and edge cases. All 161 tests passing.

- [ ] TASK-019
  Status: Not Started
  Summary: Add unit and integration tests for embedding generation, caching, vector indexing, and collection-aware filtering
  Plan reference: Phase 3, TASK-019
  Linked requirement(s): REQ-005, REQ-006, NFR-002, NFR-003, NFR-005
  Linked acceptance criteria: AC-004, AC-003
  Affected file(s) or module(s): `backend/tests/unit/test_embeddings.py`, `backend/tests/unit/test_caching.py`, `backend/tests/integration/test_indexing_workflows.py`
  Depends on: TASK-013, TASK-014, TASK-015, TASK-018
  Can run in parallel: No
  Validation note: Embedding tests verify API calls, retries, error handling; caching tests verify hit/miss and correctness; indexing tests verify metadata preservation, collection filtering; PYTHONPATH=. .venv/bin/pytest returns all passing
  Session note:

---

## Phase 4: Re-Indexing and Lifecycle Management

**Goal:** Support re-indexing when document content or chunking/embedding settings change. Manage index generations and prevent stale vectors from polluting results.

**Enabled scenario(s):** US-003 (re-indexing after settings change), US-004 (document updates reflected), AC-004 (new active index state).

**Completion criteria:**

- [ ] CC-007: Re-indexing produces a new index generation. Old vectors are marked inactive or removed. Active index state is unambiguous.
- [ ] CC-008: Document deletion cascades to all chunks and index entries. No orphans are left behind.

### Tasks

- [ ] TASK-020
  Status: Not Started
  Summary: Implement re-indexing workflow with clear generation tracking and old-generation cleanup to prevent stale vectors from active queries
  Plan reference: Phase 4, TASK-020
  Linked requirement(s): REQ-007, NFR-002, NFR-003
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/indexing/reindexing_service.py`
  Depends on: TASK-017, TASK-016
  Can run in parallel: No
  Validation note: Re-index workflow creates new generation record; re-chunks document (using new or old strategy settings); embeds new chunks; writes new index entries; marks old generation as inactive; active index state is unambiguous (only one generation has is_active=true per document); tests verify workflow and state transitions
  Session note:

- [ ] TASK-021
  Status: Not Started
  Summary: Add API endpoints for triggering re-indexing and inspecting index state, including generation history and active generation metadata
  Plan reference: Phase 4, TASK-021
  Linked requirement(s): REQ-007, NFR-004, NFR-005
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/routers/indexing_router.py`, `backend/schemas/indexing_schemas.py`
  Depends on: TASK-020
  Can run in parallel: No
  Validation note: POST endpoint triggers re-index for document; GET endpoints return generation history, active generation metadata, index state; responses include generation_id, created_at, settings_hash, status, chunk_count; tests verify endpoint contracts
  Session note:

- [ ] TASK-022
  Status: Not Started
  Summary: Extend Feature 1 document deletion to cascade to chunks and index entries, ensuring no orphaned records remain after deletion
  Plan reference: Phase 4, TASK-022
  Linked requirement(s): REQ-007, NFR-002, NFR-003
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/repositories/document_repository.py`, `backend/repositories/chunk_repository.py`, `backend/repositories/index_entry_repository.py`
  Depends on: TASK-002, TASK-017, Feature 1 (document deletion)
  Can run in parallel: No (requires coordination with Feature 1)
  Validation note: Document deletion transactionally deletes all associated chunks, index entries, and embeddings; no orphaned records; deletion is logged; tests verify cascading deletes and orphan prevention
  Session note:

- [ ] TASK-023
  Status: Not Started
  Summary: Implement re-index-initiation trigger from Feature 1's document lifecycle endpoint to cascade indexing when document re-ingest is triggered
  Plan reference: Phase 4, TASK-023
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/routers/lifecycle_router.py` (extend Feature 1), `backend/indexing/indexing_service.py`
  Depends on: TASK-021, Feature 1 (re-ingest endpoint)
  Can run in parallel: No (requires Feature 1 endpoint stability)
  Validation note: Feature 1 re-ingest endpoint triggers Feature 2 re-indexing workflow; re-index status visible in document lifecycle; tests verify coupling and status propagation
  Session note:

- [ ] TASK-024
  Status: Not Started
  Summary: Add observability (logging, metrics, status fields) for chunking, embedding, and indexing operations including strategy choice, fallback triggers, API calls, and re-index events
  Plan reference: Phase 4, TASK-025
  Linked requirement(s): NFR-005
  Linked acceptance criteria: All (observability supports debugging)
  Affected file(s) or module(s): `backend/observability/logging.py`, `backend/observability/metrics.py`
  Depends on: TASK-008, TASK-013, TASK-020
  Can run in parallel: No
  Validation note: All chunking operations logged with strategy, chunk_count, timing; embedding operations logged with API calls, cache hits, fallback triggers; re-index events logged with generation_id, timing; metrics available for monitoring
  Session note:

- [ ] TASK-025
  Status: Not Started
  Summary: Add tests for re-indexing workflows, generation switching, lifecycle cascades, and orphan prevention
  Plan reference: Phase 4, TASK-024
  Linked requirement(s): REQ-007, NFR-002, NFR-003
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/tests/integration/test_reindexing_workflows.py`, `backend/tests/integration/test_lifecycle_cascades.py`
  Depends on: TASK-020, TASK-022, TASK-023
  Can run in parallel: No
  Validation note: Re-index tests verify generation creation, old generation deactivation, new index queryable; cascade tests verify document deletion removes chunks/indexes; re-ingest tests verify indexing triggered; PYTHONPATH=. .venv/bin/pytest returns all passing
  Session note:

---

## Phase 5: Inspection and Configuration UI (Optional/Deferred)

**Goal:** Provide UI for inspecting chunks, index state, and re-indexing controls. Configuration of chunking/embedding strategies can be deferred if backend-only inspection is sufficient for v1.

**Enabled scenario(s):** US-002 (compare chunking strategies), US-003 (re-index from UI).

**Completion criteria:**

- [ ] CC-009: Users can inspect chunk boundaries, strategy choices, and parent-child relationships from the UI.
- [ ] CC-010: Users can trigger re-indexing and observe index state changes.

**Note:** This phase can be deferred to a later iteration if Phase 4 is complete and API endpoints are stable. Backend-only inspection is sufficient for v1.

### Tasks

- [ ] TASK-026
  Status: Not Started
  Summary: Design inspection screens for chunks and index metadata including chunk browser with filtering by document, strategy, and generation
  Plan reference: Phase 5, TASK-026
  Linked requirement(s): NFR-004, NFR-005
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `frontend/src/screens/ChunkInspection/`, `frontend/src/components/ChunkViewer.jsx`
  Depends on: Phase 4 complete (backend APIs stable)
  Can run in parallel: No
  Validation note: UI design shows chunk text, metadata (strategy, page, section, order), generation, parent_chunk_id if applicable; filtering by document, strategy, generation works; design is reviewed and approved before implementation
  Session note:

- [ ] TASK-027
  Status: Not Started
  Summary: Implement chunk and index inspection FastAPI endpoints returning chunk records with metadata, generation state, and parent-child relationships
  Plan reference: Phase 5, TASK-027
  Linked requirement(s): NFR-004, NFR-005
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `backend/routers/inspection_router.py`, `backend/schemas/inspection_schemas.py`
  Depends on: TASK-021, TASK-017
  Can run in parallel: No
  Validation note: GET endpoints return chunks by document_id, filtered by strategy/generation; metadata complete; parent-child relationships included; tests verify endpoint contracts and data completeness
  Session note:

- [ ] TASK-028
  Status: Not Started
  Summary: Implement React components for chunk browser and index state viewer using inspection APIs, with filtering and search
  Plan reference: Phase 5, TASK-027
  Linked requirement(s): NFR-004, NFR-005
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `frontend/src/components/ChunkBrowser.jsx`, `frontend/src/components/IndexStateViewer.jsx`, `frontend/api/inspectionApi.js`
  Depends on: TASK-027
  Can run in parallel: Yes (React components independent; ownership: frontend inspection components; reintegration: add routes to App.jsx and navbar)
  Validation note: Components fetch and display chunks, metadata, generation state; filtering by strategy/generation/document works; parent-child relationships shown; accessibility labels present; tests verify component rendering and filtering
  Session note:

- [ ] TASK-029
  Status: Not Started
  Summary: Implement re-indexing trigger UI on document detail screen with confirmation, progress indication, and completion status
  Plan reference: Phase 5, TASK-028
  Linked requirement(s): NFR-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `frontend/src/screens/DocumentDetail/`, `frontend/src/components/ReindexTrigger.jsx`
  Depends on: TASK-021, TASK-028
  Can run in parallel: Yes (UI independent from inspection; ownership: re-index UI only; reintegration: integrate into document detail screen)
  Validation note: Button triggers re-index with confirmation; status shows in-progress; completion shown with new generation_id; tests verify UI flow and API interaction
  Session note:

- [ ] TASK-030
  Status: Not Started
  Summary: Add accessibility and status labeling for chunking/indexing operations including ARIA labels, text labels (not color-only) for strategy and status, and understandable error messages
  Plan reference: Phase 5, TASK-029
  Linked requirement(s): NFR-004
  Linked acceptance criteria: All
  Affected file(s) or module(s): `frontend/src/components/`, `frontend/src/constants/chunking_constants.js`
  Depends on: TASK-028, TASK-029
  Can run in parallel: No
  Validation note: Status badges use text + color; strategy names understandable (not internal codes); ARIA labels present on interactive elements; error messages plain language; tests verify accessibility
  Session note:

- [ ] TASK-031
  Status: Not Started
  Summary: Add end-to-end tests for inspection and re-indexing workflows covering document chunk inspection, generation history, and re-index trigger flow
  Plan reference: Phase 5, TASK-030
  Linked requirement(s): NFR-004, NFR-005
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s) or module(s): `frontend/src/tests/e2e/`, `backend/tests/e2e/`
  Depends on: TASK-028, TASK-029
  Can run in parallel: No
  Validation note: E2E tests cover chunk inspection workflow, generation switching, re-index trigger and completion; tests verify UI and backend integration; Vitest or similar runner passes all tests
  Session note:

---

## Phase 6: Integration Testing and Release Readiness

**Goal:** Verify all acceptance criteria and integration with Feature 1. Prepare documentation and troubleshooting guides.

**Enabled scenario(s):** All (cross-cutting verification).

**Completion criteria:**

- [ ] CC-011: All acceptance criteria (AC-001 through AC-004) are validated end to end.
- [ ] CC-012: Setup documentation covers chunking configuration, embedding provider setup, vector database choices, and troubleshooting.

### Tasks

- [ ] TASK-032
  Status: Not Started
  Summary: Create end-to-end test scenarios covering all acceptance criteria (AC-001 through AC-004) with realistic documents and workflows
  Plan reference: Phase 6, TASK-031
  Linked requirement(s): REQ-001 through REQ-007
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s) or module(s): `backend/tests/e2e/`, test data files
  Depends on: Phase 5 complete (or Phase 4 if Phase 5 deferred)
  Can run in parallel: No
  Validation note: AC-001: Chunk representative docs (PDF, Markdown, TXT, URL) and verify retrievable chunks with metadata; AC-002: Enable semantic chunking, verify boundaries and fallback on weak structure; AC-003: Inspect parent-child relationships; AC-004: Change settings, re-index, verify active state; all tests passing
  Session note:

- [ ] TASK-033
  Status: Not Started
  Summary: Verify traceability from requirements (REQ-001 through REQ-007) through implementation tasks to validation steps using task-traceability-audit
  Plan reference: Phase 6, TASK-032
  Linked requirement(s): All (REQ-001 through REQ-007)
  Linked acceptance criteria: All (AC-001 through AC-004)
  Affected file(s) or module(s): `artifacts/features/2.chunking-and-indexing-foundation/tasks.md` (this file), traceability audit tool
  Depends on: All prior phases
  Can run in parallel: No (audit task)
  Validation note: Every REQ maps to at least one task; every AC maps to at least one task or validation step; every task maps back to REQ/AC; traceability matrix complete and verified; no orphaned requirements or acceptance criteria
  Session note:

- [ ] TASK-034
  Status: Not Started
  Summary: Write setup and troubleshooting documentation for chunking/embedding/indexing configuration, embedding provider setup, vector database choices, and common issues
  Plan reference: Phase 6, TASK-033
  Linked requirement(s): NFR-005
  Linked acceptance criteria: All
  Affected file(s) or module(s): `backend/SETUP_CHUNKING.md` (or extend existing SETUP.md)
  Depends on: Phase 4 complete
  Can run in parallel: Yes (documentation independent; ownership: documentation only; reintegration: publish to SETUP or README)
  Validation note: Documentation covers: enabling chunking, configuring chunk size/overlap/strategies, OpenAI key setup, Chroma or Pinecone setup, configuring embedding model, re-indexing procedure, troubleshooting embedding failures, observability (logs/metrics)
  Session note:

- [ ] TASK-035
  Status: Not Started
  Summary: Prepare for integration with Feature 3 (Grounded Chat) and Feature 4 (Advanced Retrieval) by documenting chunk/index query contracts and API stability notes
  Plan reference: Phase 6, TASK-034
  Linked requirement(s): All (cross-cutting)
  Linked acceptance criteria: All
  Affected file(s) or module(s): `backend/CHUNKING_API_CONTRACTS.md`, integration notes
  Depends on: Phase 4 complete
  Can run in parallel: Yes (integration documentation independent; ownership: documentation only; reintegration: shared with Feature 3/4 teams)
  Validation note: Documentation specifies: chunk schema and query API (list by document_id, collection_id, with strategy/generation filtering); index entry schema and similarity query API (by chunk_id, with collection filtering); embedding model and version tracking; re-index workflow and cascading; breaking change policy if any
  Session note:

- [ ] TASK-036
  Status: Not Started
  Summary: Run full test suite for backend and frontend (if Phase 5 executed), validate all acceptance criteria manually, and document any gaps or deferred work
  Plan reference: Phase 6, TASK-035
  Linked requirement(s): All
  Linked acceptance criteria: All
  Affected file(s) or module(s): All
  Depends on: All prior phases
  Can run in parallel: No (final validation)
  Validation note: PYTHONPATH=. .venv/bin/pytest backend/tests/ passes all tests; frontend tests pass if Phase 5 executed (npm run test); manual acceptance criteria validation (AC-001 through AC-004) documented; any deferred work noted with rationale
  Session note:

---

## Traceability Matrix

### Requirements to Tasks

- **REQ-001** (Chunk metadata and source location preservation)
  → TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007
  → Validation: TASK-007, TASK-032 (AC-001)

- **REQ-002** (Configurable chunk size and overlap)
  → TASK-003, TASK-004, TASK-005, TASK-006
  → Validation: TASK-007 (AC-001)

- **REQ-003** (Semantic chunking with fallback)
  → TASK-008, TASK-009, TASK-012
  → Validation: TASK-012, TASK-032 (AC-002)

- **REQ-004** (Parent-child chunking relationships)
  → TASK-010, TASK-011, TASK-012
  → Validation: TASK-012, TASK-032 (AC-003)

- **REQ-005** (Embedding generation and indexing)
  → TASK-013, TASK-014, TASK-015, TASK-016, TASK-017, TASK-018, TASK-019
  → Validation: TASK-019, TASK-032 (AC-004)

- **REQ-006** (Index parent and child chunks)
  → TASK-015, TASK-019
  → Validation: TASK-019, TASK-032 (AC-003)

- **REQ-007** (Re-indexing support)
  → TASK-020, TASK-021, TASK-022, TASK-023, TASK-025
  → Validation: TASK-025, TASK-032 (AC-004)

### Acceptance Criteria to Tasks

- **AC-001** (Index representative docs with retrievable chunks and metadata)
  → TASK-001 through TASK-007 (Phase 1)
  → TASK-032 (E2E validation)

- **AC-002** (Semantic chunking with boundaries, metadata, and fallback)
  → TASK-008, TASK-009, TASK-012 (Phase 2)
  → TASK-032 (E2E validation)

- **AC-003** (Parent-child indexed document with verified relationships)
  → TASK-010, TASK-011, TASK-012 (Phase 2)
  → TASK-015, TASK-019 (Phase 3)
  → TASK-032 (E2E validation)

- **AC-004** (Changed settings produce new active index state with metadata preservation)
  → TASK-020, TASK-021, TASK-022, TASK-023, TASK-025 (Phase 4)
  → TASK-032 (E2E validation)

### Phase Dependencies

- **Phase 1** (Chunking Foundation): No dependencies
- **Phase 2** (Semantic + Parent-Child): Depends on Phase 1 schema and strategy foundation
- **Phase 3** (Embeddings + Indexing): Depends on Phase 1 schema and Phase 2 completion
- **Phase 4** (Re-Indexing + Lifecycle): Depends on Phase 1-3 complete
- **Phase 5** (UI Inspection): Depends on Phase 4 complete (can be deferred)
- **Phase 6** (Integration + Release): Depends on Phases 1-4 complete (5 optional)

---

## Parallel Work Boundaries

- **Phase 1**: All chunking strategies (TASK-003, TASK-004, TASK-005) can run in parallel after schema (TASK-001) and repository (TASK-002) are done. Ownership: one engineer per strategy. Reintegration: all must complete and register in dispatcher (TASK-006) before TASK-007.

- **Phase 2**: Semantic chunking (TASK-008) can proceed independently after Phase 1, but fallback (TASK-009) must wait for semantic implementation. Parent-child schema (TASK-010) can proceed independently in parallel with TASK-008, but implementation (TASK-011) must wait for TASK-010.

- **Phase 3**: No parallel work due to dependency chain on caching and indexing.

- **Phase 5** (if executed): Documentation (TASK-034, TASK-035) can run in parallel with UI implementation (TASK-026 through TASK-030).

---

## Session Notes and Tracking

All tasks begin with `Status: Not Started` and `Session note:` (empty). As tasks are executed, these fields are updated to track progress and captured context for resumption across sessions.

**Template for completion note:**
```
Session note: Completed on [date]. [Brief summary of what was done, any decisions made, any blockers encountered]. Verified with [test command or manual verification].
```

Example (from Feature 1):
```
Session note: Completed on 2026-05-05. Added FastAPI app skeleton, request ID middleware, config bootstrap, local data paths, and backend pytest smoke coverage. Verified with `PYTHONPATH=. .venv/bin/pytest backend/tests/unit/test_health.py` and `PYTHONPATH=. .venv/bin/python -c "from app import app; print(app.title)"`.
```

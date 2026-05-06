# Implementation Plan

## Metadata

- Feature name: Chunking and Indexing Foundation
- Related spec: `artifacts/features/2.chunking-and-indexing-foundation/spec.md`
- Related requirements review: None present
- Related design: None present
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-05

## Plan Summary

Implement this feature as a serverless indexing pipeline in Python FastAPI that consumes accepted documents from Feature 1, chunks them using configurable strategies (fixed-size, heading-aware, page-aware, semantic, parent-child), generates embeddings via OpenAI API, and stores vectors and metadata in a vector database (Chroma or similar). The delivery is phased so the chunking service and data model land first, embedding and vector indexing land second, re-indexing and lifecycle management land third, and a minimal inspection and configuration UI lands on top of stable APIs.

The feature preserves full provenance and citation metadata on every chunk and index entry. Re-indexing produces a clear active index state without mixing generations. Semantic chunking includes fallback to deterministic baseline behavior when semantic segmentation is weak. The system remains transparent and reviewable for later retrieval comparison work.

Rollout risk is moderate because the feature introduces vector storage and external API dependencies (embeddings), so validation and rollback guidance account for embedding provider failures and index corruption scenarios.

## Constitution Alignment

- Constitutional rule or principle: Frontend screens in this repo must be JavaScript clients under `frontend/` that call REST API endpoints.
  Planning implication: Any inspection or configuration UI for chunking strategies will be delivered as ReactJS screens that consume FastAPI endpoints; no backend-rendered views.
- Constitutional rule or principle: Python work in this repo must use a virtual environment, and frontend/backend concerns must stay separated.
  Planning implication: Chunking, embedding, and vector indexing logic live in `backend/` under the same FastAPI application and virtual environment used by Feature 1.

## Execution Context

- Design reference: No `design.md` exists for this feature, so the plan makes minimum architecture choices needed to start implementation safely (e.g., choice of embedding provider, vector database, chunking library defaults).
- Relevant repository patterns for execution: Feature 1 established FastAPI endpoints, SQLite persistence, and document/collection schemas. Feature 2 builds on top of those contracts and adds index tables, chunk records, and embedding storage.
- Brownfield execution constraints or greenfield assumptions: This is brownfield on top of Feature 1's foundation. Reuse the FastAPI app structure, SQLite database, and document identity model; add new tables and services for chunks and indexes without disturbing Feature 1's workflows.
- Unchanged behavior that must be preserved during delivery: Feature 1's ingestion, collection management, and duplicate detection workflows must remain unchanged. Do not trigger automatic chunking or re-indexing on document ingest; chunking is initiated explicitly via API.

## Technical Approach

- Chosen approach: Build a chunking service with pluggable chunking strategies, an embedding client that calls OpenAI API, and a vector index writer that stores vectors and metadata in a local vector database. Use asyncio for non-blocking embedding calls. Keep chunking and indexing as on-demand operations triggered by explicit API calls rather than automatic background jobs.
- Architectural or integration shape: The backend owns chunking logic, embedding generation, vector index writes, and chunk metadata persistence. The frontend (minimal UI) owns triggering re-indexing workflows and inspecting chunk/index state. The vector database is queried later by the retrieval feature (Feature 4).
- Key interfaces or contracts: Chunking strategy endpoints that accept a document and return chunk records; embedding and indexing endpoints that consume chunks and produce indexed entries; re-indexing endpoints that clear and regenerate vectors for a document; inspection endpoints that list chunks, index state, and strategy choices for a document.
- Operational considerations: Embeddings are cached in the SQLite database to avoid re-computing them on re-index unless embedding settings change. The vector index (Chroma, Pinecone, or similar) stores only the current active generation; older indexes are cleared on re-index. Chunk and embedding operations are isolated per document to prevent one failure from corrupting the whole index.

## Decision Rationale

- Why this approach was selected: Feature 1 established SQLite and FastAPI; extending that same pattern to chunking and embeddings keeps architecture consistent and implementation incremental. OpenAI embeddings are stable, widely available, and sufficient for the first version. A local vector database (Chroma) is simple to set up and test; vendor lock-in is deferred to future work.
- Existing patterns reused: The same FastAPI router, SQLite schema, and document identity model from Feature 1. The same REST API contract style (JSON request/response, standard HTTP codes, request IDs). The same validation and error handling patterns.
- Alternatives considered: Embedding-based duplicate detection in Feature 1 (deferred; requires embeddings); automatic chunking on document ingest (deferred; explicit control allows experiment comparison); distributed indexing (deferred; async within single process sufficient for first version); streaming embeddings to avoid in-memory accumulation (deferred; batch per document is acceptable).
- Why rejected: Those options add operational complexity or couple features that should remain independent. Explicit chunking/indexing control is valuable for experimentation and debugging. Batch processing per document is safe and simpler than streaming. Single-process async is sufficient; distributed work comes later if needed.

## Requirements And Constraints

- REQ-001:
  Implementation note: Implement fixed-size, heading-aware (for Markdown), and page-aware (for PDF) chunking strategies. Each chunk record must include `document_id`, `chunk_id` (UUID or sequential), `source_type`, `title`, `page`/`section` (when applicable), `chunk_order`, `source_url` (when applicable), `collection_id`, and `text` content.
  Planned validation: Unit tests for each chunking strategy on representative documents; integration tests that chunk a document and verify metadata and ordering.
  Linked scenario or outcome: US-001, SC-001
- REQ-002:
  Implementation note: Support configurable chunk size (e.g., 512-2048 tokens), overlap (e.g., 0-50% of chunk size), and strategy selection per collection or experiment.
  Planned validation: API tests that change chunking settings and re-chunk the same document, confirming that different strategies produce expected variations in chunk boundaries.
  Linked scenario or outcome: US-001, US-002
- REQ-003:
  Implementation note: Implement semantic chunking using a library like `semantic-chunking` or spaCy if feasible; provide clear fallback to fixed-size chunking when semantic segmentation fails or settings are not configured.
  Planned validation: Unit tests covering semantic segmentation success, fallback paths, and edge cases (weak structure, short content, encoding issues); reviewers can inspect semantic boundary metadata and fallback indicators.
  Linked scenario or outcome: US-002, SC-001
- REQ-004:
  Implementation note: Implement parent-child chunking by creating larger parent units from multiple child chunks. Store `parent_chunk_id` on child records and `child_chunk_ids` (list) on parent records. Both parent and child remain distinct and retrievable.
  Planned validation: Unit tests for parent-child relationship construction; integration tests that verify both directions of traversal.
  Linked scenario or outcome: US-004, SC-001
- REQ-005:
  Implementation note: Call OpenAI embedding API (or another provider configured via environment variable) for each chunk. Store embeddings in SQLite. Preserve collection, document, and citation metadata on every vector index entry.
  Planned validation: API tests that generate embeddings and verify they are stored; integration tests that confirm metadata is present on indexed entries.
  Linked scenario or outcome: US-001, US-002, SC-002
- REQ-006:
  Implementation note: Index both child and parent chunks when parent-child chunking is enabled. Keep their identities and relationships distinct in the index for later debugging.
  Planned validation: Integration tests that confirm both levels appear in the index with correct relationships.
  Linked scenario or outcome: US-004, SC-002
- REQ-007:
  Implementation note: Support re-indexing when document content or chunking/embedding settings change. Maintain a clear active index state (e.g., via a "generation" or "index_version" field). Clear or mark stale vectors when re-indexing starts; do not mix old and new generations.
  Planned validation: Integration tests for re-indexing workflow; manual inspection that active index state is unambiguous after settings change.
  Linked scenario or outcome: US-003, SC-003
- NFR-001:
  Implementation note: Chunk a representative document (10-50 pages) in under 5 seconds; embed a document (50-100 chunks) in under 30 seconds including API latency. Use async/await to avoid blocking on embedding calls.
- NFR-002:
  Implementation note: If embedding fails for one document, previous index entries remain queryable. If chunking fails, the document remains ingested but unchunked; error is logged with document ID.
- NFR-003:
  Implementation note: Preserve source URL, document ID, page number, and collection ID on every chunk and index entry. Do not synthesize or infer metadata; explicitly copy from ingestion records.
- NFR-004:
  Implementation note: Chunk strategy names and index state must be understandable text labels (e.g., "Fixed-size (512t, 10% overlap)", "Heading-aware", "Semantic with fallback").
- NFR-005:
  Implementation note: Log chunking strategy choice, chunk boundaries, embedding model, index generation, re-index events, and fallback triggers. Provide inspection endpoints to retrieve chunk records and index metadata for a document.

## Impacted Areas

- Services or modules: New `backend/chunking/` service with strategy implementations; new `backend/embeddings/` service for OpenAI integration; new `backend/indexing/` service for vector index writes; extensions to `backend/models/` for chunk and index records.
- APIs or interfaces: New FastAPI routers for document chunking, embedding generation, index state inspection, and re-indexing triggers.
- Data model or storage: New SQLite tables: `chunks` (document_id, chunk_id, strategy, text, metadata), `embeddings` (chunk_id, vector, model, generation), `index_entries` (chunk_id, vector_db_id, generation, metadata), `index_generations` (document_id, generation, strategy_settings, status). Vector database (Chroma or similar) for fast similarity search.
- UI or UX: Minimal inspection screens for reviewing chunks and index state; configuration screens for chunking/embedding settings (deferred to later phase or kept backend-only for v1).
- Infrastructure or deployment: OpenAI API key configuration; vector database setup (Chroma local or Pinecone cloud); async task handling within FastAPI (no separate job queue for v1).
- Documentation: Chunking strategy guide, embedding model choices, re-indexing procedure, troubleshooting index corruption.

## Affected Domains And Integration Boundaries

- Domain or subsystem: Document chunking and text segmentation
  Why it matters: Chunk boundaries directly affect retrieval precision and citation accuracy. Different strategies must be comparable and reversible.
- Domain or subsystem: Embedding generation and vector indexing
  Why it matters: Embeddings are the core of later similarity retrieval. Metadata preservation is essential for collection filtering and citations.
- Integration boundary or touchpoint: FastAPI backend to OpenAI API
  Why it matters: Embedding provider can fail; system must handle rate limits, API errors, and retries gracefully.
- Integration boundary or touchpoint: SQLite to vector database
  Why it matters: Chunk metadata lives in SQL; vectors live in vector DB. Reindexing must keep both in sync and avoid orphaned vectors.
- Integration boundary or touchpoint: Chunking/indexing service to Feature 1 (document ingestion)
  Why it matters: Feature 2 consumes documents from Feature 1. Document lifecycle (delete, update) may cascade to chunks and indexes.
- Integration boundary or touchpoint: Chunking/indexing service to Feature 4 (advanced retrieval)
  Why it matters: Feature 4 will query chunks and indexes. Index schema must be stable and queryable.

## Protected Behavior

- Behavior that must not regress: Chunk metadata (document_id, source location, collection) must be complete and queryable. Lost or altered metadata breaks later citations.
  Protection approach: Explicit schema for chunk records; validation tests that confirm metadata is present and correct after chunking.
- Behavior that must not regress: Re-indexing must not leave stale vectors in the active index. Old generations must be cleared or marked inactive.
  Protection approach: Explicit index generation tracking; integration tests for re-indexing that verify old vectors are no longer queryable.
- Behavior that must not regress: Document deletion (Feature 1) must cascade to chunks and index entries. Orphaned chunks must not be left behind.
  Protection approach: Transactional delete operations; tests that verify chunks are removed when document is deleted.
- Behavior that must not regress: Semantic chunking failures must fall back to deterministic chunking, not silently produce incorrect chunks.
  Protection approach: Explicit fallback logic; tests for edge cases where semantic segmentation might fail.

## Affected Files

- FILE-001 Path: `backend/chunking/`
  Reason for change: New module for chunking strategy implementations (fixed-size, heading-aware, page-aware, semantic, parent-child).
- FILE-002 Path: `backend/embeddings/`
  Reason for change: New module for embedding generation client and caching logic.
- FILE-003 Path: `backend/indexing/`
  Reason for change: New module for vector index writes and metadata storage.
- FILE-004 Path: `backend/models/`
  Reason for change: New SQLite models for chunks, embeddings, and index entries; relationships to documents and collections.
- FILE-005 Path: `backend/routers/`
  Reason for change: New FastAPI routers for chunking, embedding, and index management endpoints.
- FILE-006 Path: `backend/repositories/`
  Reason for change: New repository methods for chunk and embedding persistence.
- FILE-007 Path: `requirements.txt`
  Reason for change: Add dependencies for chunking (e.g., `sentence-transformers`, `semantic-chunking`), embeddings (OpenAI API), and vector DB (Chroma, Pinecone).
- FILE-008 Path: `backend/migrations/`
  Reason for change: New migrations for chunk and index tables.

## Dependencies

- DEP-001 Internal dependency: Feature 1 (Knowledge Ingestion and Collections) must be complete. Feature 2 consumes document records, collection memberships, and document metadata.
  Why it matters: Feature 2 has no documents to chunk without Feature 1.
- DEP-002 Internal dependency: Feature 1 status: Feature 1 is **COMPLETE** as of 2026-05-05. All ingestion, collection management, and duplicate detection are ready. Feature 2 can proceed.
- DEP-003 External dependency: OpenAI API key and account (or alternative embedding provider)
  Why it matters: Embeddings require external API calls. Cost and rate limits must be understood.
- DEP-004 External dependency: Vector database (Chroma for local, Pinecone for cloud, or equivalent)
  Why it matters: Vectors must be stored somewhere for later retrieval. Local development uses Chroma; production may differ.
- DEP-005 External dependency: Chunking and semantic-segmentation libraries (e.g., `sentence-transformers`, `semantic-chunking`, spaCy)
  Why it matters: Semantic chunking is a requirement; implementations vary in quality and performance.
- DEP-006 External dependency: Python HTTP client for OpenAI API (e.g., `openai` library)
  Why it matters: Official OpenAI client is preferred for stability and maintained support.

## Implementation Prerequisites

- PREREQ-001: Feature 1 (Knowledge Ingestion and Collections) is fully deployed and tested locally. Sample ingested documents exist in the database.
- PREREQ-002: OpenAI API key is available and configured (via `.env` or environment variable).
- PREREQ-003: Vector database choice (Chroma vs. Pinecone vs. other) is decided. Local Chroma is recommended for v1 simplicity.
- PREREQ-004: Python dependencies for chunking, embeddings, and vector indexing are added to `requirements.txt` and installed in `.venv`.
- PREREQ-005: SQLite schema is migrated to include chunk, embedding, and index entry tables.

## Implementation Phases

### Phase 1: Chunking Service Foundation

**Goal:** Establish the chunking service, data model, and baseline chunking strategies so chunks can be generated and stored reliably.

**Enabled user scenario(s) or outcome(s):** None directly user-visible; this phase creates the chunking foundation for all downstream work.

**Tasks:**

- TASK-001: Design and implement SQLite schema for chunks, embeddings, and index entries with relationships to documents and collections.
- TASK-002: Implement fixed-size chunking strategy with configurable chunk size, overlap, and metadata preservation.
- TASK-003: Implement heading-aware chunking for Markdown and text documents with section tracking.
- TASK-004: Implement page-aware chunking for PDF documents with page metadata preservation.
- TASK-005: Implement chunking strategy dispatcher and document chunking orchestrator.
- TASK-006: Create repository layer for chunk persistence and querying.
- TASK-007: Add unit and integration tests for all chunking strategies.

**Completion criteria:**

- CC-001: A document can be chunked using fixed-size, heading-aware, or page-aware strategies. Chunks are persisted with complete metadata.
- CC-002: Chunking tests pass; chunk boundaries and metadata are verified against expected outputs.

### Phase 2: Semantic Chunking and Parent-Child Support

**Goal:** Add semantic chunking with fallback behavior and parent-child chunk relationships, enabling more sophisticated document structure analysis.

**Enabled user scenario(s) or outcome(s):** US-001, US-002 (different chunking strategies can be compared).

**Tasks:**

- TASK-008: Implement semantic chunking using a semantic-segmentation library; include configuration for thresholds and fallback strategy.
- TASK-009: Add explicit fallback to fixed-size chunking when semantic segmentation is weak or unavailable.
- TASK-010: Implement parent-child chunking logic that creates parent units from multiple child chunks.
- TASK-011: Extend repository and schema to track parent-child relationships bidirectionally.
- TASK-012: Add tests for semantic chunking edge cases, fallback behavior, and parent-child relationships.

**Completion criteria:**

- CC-003: Semantic chunking runs on structured documents and produces meaning-aware boundaries with visible metadata. Fallback to fixed-size is automatic and logged.
- CC-004: Parent-child chunks are created and stored with bidirectional relationship links. Both levels are independently queryable.

### Phase 3: Embedding Generation and Vector Indexing

**Goal:** Generate embeddings for chunks and store them in a vector index with full metadata preservation. Support multiple embedding models and index generations.

**Enabled user scenario(s) or outcome(s):** US-001, US-003 (documents are searchable via vector similarity).

**Tasks:**

- TASK-013: Implement OpenAI embedding client with error handling, retries, and rate-limit awareness.
- TASK-014: Add embedding caching in SQLite to avoid recomputing vectors when settings don't change.
- TASK-015: Implement vector index writer that stores vectors and metadata in Chroma or equivalent.
- TASK-016: Extend schema to track embedding model, index generation, and active index state.
- TASK-017: Create index entry repository and querying methods.
- TASK-018: Add error handling for embedding API failures and partial indexing.
- TASK-019: Add unit and integration tests for embedding generation and index operations.

**Completion criteria:**

- CC-005: Chunks are embedded and indexed with metadata (document_id, collection_id, source location, chunk order). All indexed entries are queryable by vector similarity.
- CC-006: Both parent and child chunks are indexed when parent-child chunking is enabled. Metadata distinguishes them.

### Phase 4: Re-Indexing and Lifecycle Management

**Goal:** Support re-indexing when document content or chunking/embedding settings change. Manage index generations and prevent stale vectors from polluting results.

**Enabled user scenario(s) or outcome(s):** US-003 (re-indexing after settings change), US-004 (document updates are reflected in index).

**Tasks:**

- TASK-020: Implement re-indexing workflow with clear generation tracking and old-generation cleanup.
- TASK-021: Add API endpoints for triggering re-indexing and inspecting index state.
- TASK-022: Extend document deletion (Feature 1) to cascade to chunks and index entries.
- TASK-023: Implement re-index-initiation from Feature 1's document lifecycle endpoint.
- TASK-024: Add tests for re-indexing, generation switching, and lifecycle cascades.
- TASK-025: Add observability (logging, metrics) for chunking, embedding, and indexing operations.

**Completion criteria:**

- CC-007: Re-indexing produces a new index generation. Old vectors are marked inactive or removed. Active index state is unambiguous.
- CC-008: Document deletion cascades to all chunks and index entries. No orphans are left behind.

### Phase 5: Inspection and Configuration UI (Optional/Deferred)

**Goal:** Provide UI for inspecting chunks, index state, and re-indexing controls. Configuration of chunking/embedding strategies.

**Enabled user scenario(s) or outcome(s):** US-002 (compare chunking strategies), US-003 (re-index from UI).

**Tasks:**

- TASK-026: Design inspection screens for chunks and index metadata.
- TASK-027: Implement chunk/index inspection endpoints and React components.
- TASK-028: Implement re-indexing trigger UI and settings configuration screens.
- TASK-029: Add accessibility and status labeling for chunking/indexing operations.
- TASK-030: Add end-to-end tests for inspection and configuration workflows.

**Completion criteria:**

- CC-009: Users can inspect chunk boundaries, strategy choices, and parent-child relationships from the UI.
- CC-010: Users can trigger re-indexing and observe index state changes.

**Note:** This phase can be deferred to a later iteration if Phase 4 is complete and API endpoints are stable. Backend-only inspection is sufficient for v1.

### Phase 6: Integration Testing and Release Readiness

**Goal:** Verify all acceptance criteria and integration with Feature 1. Prepare documentation and troubleshooting guides.

**Tasks:**

- TASK-031: Create end-to-end test scenarios covering all acceptance criteria (AC-001 through AC-004).
- TASK-032: Verify traceability from requirements to implementation and testing.
- TASK-033: Write setup and troubleshooting documentation for chunking/embedding/indexing.
- TASK-034: Prepare for integration with Feature 3 (Grounded Chat) and Feature 4 (Advanced Retrieval).
- TASK-035: Run full test suite and validate acceptance criteria manually.

**Completion criteria:**

- CC-011: All acceptance criteria (AC-001 through AC-004) are validated end to end.
- CC-012: Setup documentation covers chunking configuration, embedding provider setup, vector database choices, and troubleshooting.

## Validation Strategy

- TEST-001 Unit tests: Chunking strategies on representative documents; embedding client error handling; parent-child relationship logic.
- TEST-002 Integration tests: End-to-end chunking and embedding of documents from Feature 1; re-indexing workflows; metadata preservation.
- TEST-003 API tests: Chunking, embedding, and inspection endpoints; re-indexing triggers; index state queries.
- TEST-004 Manual verification: Inspect chunks and index entries for representative documents; verify metadata completeness and traceability.
- TEST-005 Observability: Logs and metrics for chunking strategy choice, fallback triggers, embedding API calls, and re-index events.

## Traceability Matrix

- REQ-001 → Phase 1 (TASK-001 through TASK-007), Phase 2 (TASK-010); Validation: AC-001
- REQ-002 → Phase 1 (configurable settings in TASK-002, TASK-003, TASK-004); Validation: AC-001
- REQ-003 → Phase 2 (TASK-008, TASK-009); Validation: AC-002
- REQ-004 → Phase 2 (TASK-010, TASK-011); Validation: AC-003
- REQ-005 → Phase 3 (TASK-013 through TASK-019); Validation: AC-004
- REQ-006 → Phase 3 (TASK-015 indexes both parent and child); Validation: AC-003
- REQ-007 → Phase 4 (TASK-020, TASK-021); Validation: AC-004
- AC-001 → Phase 1, Phase 2, Phase 6 (TEST-001, TEST-002, TEST-004)
- AC-002 → Phase 2, Phase 6 (TEST-001, TEST-002, TEST-004)
- AC-003 → Phase 2, Phase 3, Phase 6 (TEST-002, TEST-003, TEST-004)
- AC-004 → Phase 3, Phase 4, Phase 6 (TEST-002, TEST-003, TEST-005)

## Rollout Plan

- Release approach: Land Phase 1 (chunking foundation), Phase 2 (semantic + parent-child), and Phase 3 (embeddings + indexing) before Phase 4 (re-indexing) to establish stable chunk and index contracts.
- Feature flags: None required if the feature remains local-only. If multiple chunking strategies are exposed to users, configuration flags for enabled strategies are recommended.
- Migration needs: SQLite schema migration for new chunk and index tables. Vector database initialization (Chroma local or cloud setup).
- Backward compatibility notes: Feature 1's document and collection records must remain unchanged. New chunking/indexing is purely additive.

## Rollback Plan

If a regression is found after Phase 3 lands:
1. Disable or revert chunking/embedding endpoints in FastAPI.
2. Clear the vector database (Chroma or equivalent) to remove bad vectors.
3. Revert SQLite schema if needed; preserve chunk records for audit if important.
4. Restore previous chunking and embedding logic from version control.

If Phase 4 (re-indexing) causes index corruption:
1. Stop all re-indexing operations.
2. Clear the active index state; mark all index entries as inactive.
3. Revert to a previous known-good index generation or rebuild from scratch.
4. Fix the re-indexing logic and validate with test data before re-enabling.

## Risks And Mitigations

- RISK-001: Embedding API rate limits or costs exceed expectations.
  Mitigation: Monitor API usage in logs; cache embeddings to avoid recomputation; consider a cheaper or local embedding model if needed.
- RISK-002: Semantic chunking produces poor boundaries on some document types (e.g., scanned PDFs, code).
  Mitigation: Test semantic chunking on representative examples early; provide explicit fallback configuration; log fallback triggers.
- RISK-003: Vector database choice (Chroma vs. Pinecone) affects later scalability.
  Mitigation: Use a thin abstraction layer for vector operations; avoid vendor-specific APIs; allow provider swapping later.
- RISK-004: Re-indexing could create orphaned vectors if old-generation cleanup fails.
  Mitigation: Use explicit generation tracking; test re-indexing on non-production data; validate that old vectors are marked inactive before new generation is active.
- RISK-005: Metadata loss if chunk or index schema is not complete.
  Mitigation: Explicit schema validation tests; preservation checks that verify document_id, collection_id, and source location on every chunk and index entry.

## Assumptions

- ASM-001: OpenAI embeddings are available and cost-effective for the project's expected volume.
  If false: Switch to a local embedding model (e.g., `sentence-transformers`) or a different provider.
- ASM-002: Semantic chunking libraries (e.g., `semantic-chunking`) are stable and work well on typical text documents.
  If false: Fall back to fixed-size + heading-aware chunking and defer semantic chunking to a later iteration.
- ASM-003: A local vector database (Chroma) is sufficient for initial development and testing.
  If false: Switch to Pinecone, Weaviate, or equivalent when scaling requires it.
- ASM-004: One embedding model per feature iteration is sufficient; multi-model comparison is deferred.
  If false: Add embedding model configuration and comparison logic later.

## Open Questions

- Q-001: Should parent-child chunking be enabled by default for all documents or only when explicitly configured per collection or experiment?
  Owner: Product/Design decision
  Impact: Affects default index size and query performance.
  Recommend: default enabled with easy disable per collection.
- Q-002: Should re-indexing be automatic when embedding settings change or manual via API trigger?
  Owner: Product/Design decision
  Impact: Affects index staleness and user experience.
  Recommend: manual trigger with clear status feedback.
- Q-003: Which vector database should be used for local development and v1 deployment?
  Owner: Architecture decision
  Impact: Affects dependency choices and later migration effort.
  Recommend: Chroma for simplicity; Pinecone for cloud later.
- Q-004: Should chunk inspection and strategy configuration be exposed in the UI in v1 or kept backend-only?
  Owner: Product/Design decision
  Impact: Affects Phase 5 scope and user experience.
  Next step: Confirm during Phase 1 completion. Recommend: defer full UI to Phase 5; provide backend-only inspection API for v1.

## Notes

- Delivery sequence: 2 of 7. Feature 2 is the indexing foundation that enables Feature 3 (Grounded Chat and Citations) and Feature 4 (Advanced Retrieval Strategies).
- Integration with Feature 1: Feature 2 assumes Feature 1 is complete. Document records, collection memberships, and document deletion workflows from Feature 1 must be stable before Feature 2 implementation begins.
- Integration with Feature 4: Feature 4 (Advanced Retrieval) will query chunks and index entries. The chunk and index schemas defined in Phase 1-3 must be stable and queryable by the time Feature 4 begins.
- Estimated implementation effort: Phases 1-4 (core functionality) are estimated at 3-4 weeks for a single full-time engineer. Phase 5 (UI) adds 1-2 weeks. Phase 6 (integration and release) adds 1 week.

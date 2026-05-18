# Technical Design

## Metadata

- Feature name: Document Lifecycle Fixes
- Feature slug: document-lifecycle-fixes
- Related spec: `spec.md`
- Related requirements review: `requirements-review.md`
- Owner: 
- Status: Draft
- Last updated: 2026-05-18

---

## Design Summary

This design fixes two critical data consistency issues in the document lifecycle:

1. **Delete Path:** Extend the existing delete route to call vector cleanup in Weaviate immediately after SQL deletion, ensuring orphaned vectors are removed. Use fail-open semantics: if vector deletion fails, log the error and return HTTP 500, but do not roll back the SQL deletion.

2. **Reindex Path:** Clear all existing chunks and vectors before re-chunking and re-indexing. Fix collection-scoping in the ingestion service to ensure chunks are indexed only under their assigned collection(s) without duplication.

Both changes are localized to existing routes and services with minimal architectural impact.

---

## Current State And Context

- **Existing system baseline:** Delete route exists at `backend/routers/documents.py:34` and calls `repository.delete_document()`. Reindex route exists at `backend/routers/documents.py:49` and calls `IngestionService`. Vector cleanup method exists at `backend/indexing/weaviate_store.py:110` but is never called on delete.

- **Relevant repository patterns:** 
  - Routes delegate to repositories and services.
  - Repositories handle SQL operations.
  - Weaviate store handles vector operations.
  - Ingestion service orchestrates chunking and indexing per collection.

- **Brownfield constraints:** 
  - Cannot change the delete/reindex endpoint URLs (REQ-A1).
  - Must preserve existing chunking and indexing strategies (REQ-B2).
  - Fail-open semantics required for vector deletion failures (REQ-D2).

- **Unchanged behavior that must be preserved:**
  - HTTP 404 on non-existent document (both delete and reindex).
  - HTTP 204 on successful delete.
  - HTTP 200 on successful reindex.
  - Existing chunking and indexing logic.

---

## Design Drivers

- **REQ-D1:** Delete must remove both SQL and Weaviate vectors.
  - Design implication: Call `weaviate_store.delete_by_document()` after SQL deletion in the delete route.

- **REQ-D2:** Vector deletion failure must not roll back SQL deletion.
  - Design implication: Use fail-open semantics; catch exceptions, log, and return HTTP 500.

- **REQ-D3:** Retrieval must not return deleted documents.
  - Design implication: Add validation in retrieval layer to check if returned documents still exist in SQL.

- **REQ-R1:** Reindex must clear old chunks and vectors before re-chunking.
  - Design implication: Call `chunk_repo.delete_chunks_by_document()` and `weaviate_store.delete_by_document()` before re-chunking in the reindex route.

- **REQ-R2:** Collection scoping must be preserved during reindexing.
  - Design implication: Fix `ingestion_service._chunk_and_index_document()` to clear chunks per collection and fix `indexing_service.index_document()` to load chunks for the current collection context only.

- **AC-D1, AC-R1:** Vectors must be cleanly removed and recreated.
  - Design implication: Use idempotent Weaviate delete operations.

- **AC-D3, AC-R4:** Failures must be logged with context.
  - Design implication: Log document_id, collection_id (if applicable), and error details.

---

## Proposed Architecture

### Delete Path

**Components:**
- `backend/routers/documents.py:delete_document()` — HTTP route handler
- `backend/repositories/core.py:delete_document()` — SQL deletion
- `backend/indexing/weaviate_store.py:delete_by_document()` — Vector deletion

**Responsibilities:**
- Route: Accept DELETE request, validate document exists, orchestrate deletion, return appropriate HTTP status.
- Repository: Delete SQL record, return success/failure.
- Weaviate store: Delete all vectors for the document, return count of deleted vectors.

**Interaction Model:**
1. Route receives DELETE request.
2. Route calls `repository.delete_document(document_id)`.
3. If SQL deletion fails, return HTTP 404.
4. If SQL deletion succeeds, call `weaviate_store.delete_by_document(document_id)`.
5. If vector deletion fails, log error with document_id and exception, return HTTP 500.
6. If vector deletion succeeds, return HTTP 204.

**Key Boundaries:**
- SQL deletion is atomic and reliable (assumption).
- Weaviate deletion is idempotent (assumption).
- No transaction coordination between SQL and Weaviate.

### Reindex Path

**Components:**
- `backend/routers/documents.py:reindex_document()` — HTTP route handler
- `backend/repositories/core.py:get_document()` — Fetch document metadata
- `backend/ingestion/service.py:_chunk_and_index_document()` — Orchestrate chunking and indexing per collection
- `backend/indexing/indexing_service.py:index_document()` — Index chunks for a collection
- `backend/indexing/weaviate_store.py:delete_by_document()` — Vector deletion
- `backend/repositories/chunk.py:delete_chunks_by_document()` — SQL chunk deletion

**Responsibilities:**
- Route: Accept POST request, validate document exists, orchestrate reindex, return status.
- Ingestion service: For each collection, clear old chunks/vectors, then re-chunk and re-index.
- Indexing service: Load chunks for the current collection context only (not all chunks for the document).
- Weaviate store: Delete vectors by document_id.
- Chunk repository: Delete chunks by document_id.

**Interaction Model:**
1. Route receives POST request.
2. Route calls `repository.get_document(document_id)`.
3. If document does not exist, return HTTP 404.
4. Route calls `ingestion_service.reindex_document(document_id)`.
5. For each collection assigned to the document:
   a. Call `chunk_repo.delete_chunks_by_document(document_id)` (clears all chunks for the document).
   b. Call `weaviate_store.delete_by_document(document_id)` (clears all vectors for the document).
   c. Call `chunking_service.chunk_document()` to re-chunk.
   d. Call `indexing_service.index_document()` to index chunks for this collection only.
6. If any step fails, log error with document_id, collection_id, and exception, return HTTP 500.
7. If all steps succeed, return HTTP 200 with status object.

**Key Boundaries:**
- Chunk deletion is per-document (not per-collection), so it happens once per reindex.
- Vector deletion is per-document (not per-collection), so it happens once per reindex.
- Re-chunking and re-indexing happen per-collection to ensure correct scoping.

---

## Data Flow And Interfaces

### Delete Path Data Flow

```
DELETE /documents/{document_id}
  ↓
repository.delete_document(document_id)
  ↓ (SQL DELETE)
  ↓ (success → continue, failure → return 404)
weaviate_store.delete_by_document(document_id)
  ↓ (Weaviate DELETE)
  ↓ (success → return 204, failure → log + return 500)
HTTP 204 or 500
```

### Reindex Path Data Flow

```
POST /documents/{document_id}/reindex
  ↓
repository.get_document(document_id)
  ↓ (success → continue, failure → return 404)
For each collection_id in document.collection_ids:
  ↓
  chunk_repo.delete_chunks_by_document(document_id)
    ↓ (SQL DELETE)
  weaviate_store.delete_by_document(document_id)
    ↓ (Weaviate DELETE)
  chunking_service.chunk_document(document_id, collection_id, ...)
    ↓ (SQL INSERT chunks)
  indexing_service.index_document(document_id, collection_id)
    ↓ (Weaviate INSERT vectors)
    ↓ (success → continue to next collection, failure → log + return 500)
HTTP 200 with status or 500
```

### Interfaces

**Delete Route:**
- Input: `document_id` (path parameter)
- Output: HTTP 204 (success) or HTTP 404 (not found) or HTTP 500 (vector deletion failed)

**Reindex Route:**
- Input: `document_id` (path parameter)
- Output: HTTP 200 with `{"status": "completed"}` (success) or HTTP 404 (not found) or HTTP 500 (reindex failed)

**Weaviate Store:**
- `delete_by_document(document_id: str) -> int` — Delete all vectors for a document, return count of deleted vectors.

**Chunk Repository:**
- `delete_chunks_by_document(document_id: str) -> int` — Delete all chunks for a document, return count of deleted chunks.

**Indexing Service:**
- `index_document(document_id: str, collection_id: str) -> None` — Index chunks for a document in a specific collection. Must load chunks for this collection context only.

---

## Design Decisions And Tradeoffs

### Decision 1: Fail-Open Semantics for Vector Deletion Failure

**Why chosen:** REQ-D2 explicitly requires fail-open. If vector deletion fails but SQL deletion succeeds, it's better to have an orphaned vector (which can be cleaned up later) than to have an orphaned SQL record (which blocks the document from being re-created).

**Tradeoff:** Orphaned vectors may accumulate if vector deletion fails repeatedly. Mitigation: Log all failures; add a separate maintenance task to clean up orphaned vectors.

### Decision 2: Clear Chunks and Vectors Once Per Reindex (Not Per Collection)

**Why chosen:** Chunks and vectors are document-level, not collection-level. Clearing them once per reindex is more efficient than clearing them per collection.

**Tradeoff:** If reindexing fails mid-process (e.g., after clearing but before re-chunking), the document will have no chunks/vectors until the client retries. Mitigation: This is acceptable per REQ-R3; client can retry.

### Decision 3: Fix Collection Scoping in Indexing Service

**Why chosen:** REQ-R2 requires chunks to be indexed only under their assigned collection(s). The current code loads all chunks for a document, not just the current collection's chunks. Fixing this at the indexing service level ensures correct scoping.

**Tradeoff:** Requires changes to `indexing_service.index_document()` to accept a collection_id parameter and filter chunks accordingly. This is a small, localized change.

### Decision 4: No Retry Logic for Failed Operations

**Why chosen:** REQ-D2 and REQ-R3 accept fail-open semantics. Automatic retry logic would complicate error handling and could mask underlying issues. Client can retry via the API.

**Tradeoff:** Clients must implement retry logic if needed. Mitigation: Document this behavior in API docs.

---

## Alternatives Considered

### Alternative 1: Background Job for Vector Cleanup

**Reason not chosen:** REQ-D2 requires inline deletion (fail-open). A background job would introduce asynchronous cleanup, which complicates error handling and violates the fail-open requirement. Inline deletion is simpler and meets the requirement.

### Alternative 2: Atomic Transactions Across SQL and Weaviate

**Reason not chosen:** REQ-D2 explicitly rejects atomic transactions. Weaviate does not support distributed transactions with SQL, so this would require complex coordination logic. Fail-open is simpler and acceptable.

### Alternative 3: Incremental Reindexing Without Clearing Old Vectors

**Reason not chosen:** REQ-R1 requires clearing old chunks/vectors before re-chunking. Incremental reindexing would risk duplication and inconsistency. Clean reindexing is safer and meets the requirement.

---

## Brownfield Integration Notes

- **Existing boundary to respect:** The delete and reindex routes are public APIs. Their signatures and HTTP status codes must not change (REQ-A1).

- **Migration or compatibility concern:** No migration needed. This fix applies only to new delete and reindex operations. Existing orphaned vectors are not retroactively cleaned up (REQ-B1).

- **Regression hotspot:** The delete route currently does not call vector cleanup. Adding this call could introduce new failure modes (e.g., Weaviate connection errors). Mitigation: Use fail-open semantics and log all failures.

---

## Non-Functional Design Considerations

- **Performance:** Deleting vectors from Weaviate is O(n) where n is the number of vectors for the document. For typical documents (10-100 chunks), this is negligible. Reindexing involves clearing and recreating vectors, which is also O(n) per collection. No performance regression expected.

- **Reliability:** Fail-open semantics ensure that SQL deletion always succeeds even if vector deletion fails. This prevents orphaned SQL records. Orphaned vectors are acceptable and can be cleaned up separately.

- **Security:** No security implications. Delete and reindex operations are already authenticated at the route level.

- **Observability:** All failures must be logged with document_id, collection_id (if applicable), and error details. This enables debugging and monitoring.

- **Accessibility or UX consistency:** No UI changes required for delete and reindex operations. If new query parameters are introduced in the future, the frontend must be updated (REQ-A2).

---

## Open Questions

- **Q-001:** Should we add a separate maintenance task to clean up orphaned vectors from past deletions?
  - **Next step:** Defer to post-launch. This is out of scope per REQ-B1.

- **Q-002:** Should we add retry logic for failed vector operations?
  - **Next step:** No. REQ-D2 and REQ-R3 accept fail-open semantics. Client can retry via the API.

- **Q-003:** Are there existing integration tests for delete and reindex paths?
  - **Next step:** Check during planning phase. If tests exist, they must be updated to verify vector cleanup.

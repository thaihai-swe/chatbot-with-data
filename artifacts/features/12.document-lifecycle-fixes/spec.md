# Specification: Document Lifecycle Fixes

## Metadata

- Feature name: Document Lifecycle Fixes
- Feature slug: document-lifecycle-fixes
- Related proposal: `proposal.md`
- Status: Draft
- Last updated: 2026-05-18

---

## Problem Statement

The document lifecycle has two critical gaps that cause data inconsistency and retrieval errors:

1. **Orphaned Vectors on Delete:** When a document is deleted, the SQL record is removed but Weaviate vectors remain. Retrieval queries still return metadata for deleted documents because the vector store is never cleaned up.

2. **Index Corruption on Reindex:** When a document is reindexed, old chunks and vectors are not cleared before new ones are created. For multi-collection documents, chunks can be indexed under the wrong collection and duplicated on every reindex because collection context is lost during indexing.

These issues violate data consistency guarantees and degrade retrieval quality.

---

## User Scenarios

### Scenario 1: User Deletes a Document
**Actor:** Administrator or end user  
**Goal:** Remove a document and ensure it no longer appears in chat results  
**Current Behavior:** Document is removed from SQL but vectors remain in Weaviate; retrieval still returns the deleted content  
**Desired Behavior:** Both SQL record and all associated vectors are removed; retrieval no longer returns the document

### Scenario 2: User Reindexes a Document
**Actor:** Administrator or developer  
**Goal:** Refresh the index for a document (e.g., after fixing chunking logic or updating embeddings)  
**Current Behavior:** Old chunks and vectors are not cleared; new chunks are added alongside old ones; multi-collection documents may have chunks indexed under wrong collections  
**Desired Behavior:** Old chunks and vectors are cleared first; new chunks are indexed cleanly under the correct collection(s); no duplication

### Scenario 3: Multi-Collection Document Lifecycle
**Actor:** Administrator managing documents across multiple collections  
**Goal:** Ensure a document assigned to multiple collections is indexed correctly in each  
**Current Behavior:** Chunks may be indexed under the wrong collection; reindexing duplicates chunks across collections  
**Desired Behavior:** Each chunk is indexed only under its assigned collection(s); reindexing produces a clean state

---

## Requirements

### Delete Path

**REQ-D1:** When a document is deleted via `DELETE /documents/{document_id}`, the system must:
- Remove the SQL record from the documents table
- Remove all Weaviate vectors associated with the document (via `delete_by_document`)
- Return HTTP 204 No Content on success
- Return HTTP 404 if the document does not exist

**REQ-D2:** Vector deletion must be called **after** SQL deletion to ensure consistency. If vector deletion fails, the operation must:
- Log the failure with document_id and error details
- Not roll back the SQL deletion (fail-open to avoid orphaned SQL records)
- Return HTTP 500 to the client to signal partial failure

**REQ-D3:** Retrieval queries must not return metadata for deleted documents. The retrieval layer must validate that returned vector metadata corresponds to a document that still exists in SQL.

### Reindex Path

**REQ-R1:** When a document is reindexed via `POST /documents/{document_id}/reindex`, the system must:
- Clear all existing chunks for the document from the SQL chunks table
- Clear all existing vectors for the document from Weaviate (via `delete_by_document`)
- Re-chunk the document content using the configured strategy
- Re-index the new chunks under the correct collection(s)
- Return a status response indicating success or failure

**REQ-R2:** Collection scoping must be preserved during reindexing:
- When reindexing a document assigned to multiple collections, chunks must be indexed only under their assigned collection(s)
- The indexing service must load chunks for the current collection context, not all chunks for the document
- No chunk should be duplicated across collections

**REQ-R3:** If reindexing fails mid-process (e.g., chunking succeeds but indexing fails), the system must:
- Log the failure with document_id, collection_id, and error details
- Leave the document in a partially reindexed state (acceptable; client can retry)
- Return HTTP 500 to the client

### API Changes

**REQ-A1:** The delete and reindex routes must remain at their current endpoints (`DELETE /documents/{document_id}` and `POST /documents/{document_id}/reindex`). No new query parameters are required for these operations.

**REQ-A2:** If future enhancements require new query parameters (e.g., `?force=true` for delete, `?strategy=heading_aware` for reindex), they must be documented and the frontend must be updated accordingly.

### Brownfield Constraints

**REQ-B1:** Existing documents and vectors in the system are not retroactively cleaned up. This fix applies only to new delete and reindex operations going forward.

**REQ-B2:** The chunking and indexing strategies remain unchanged. This fix only ensures they are applied cleanly without duplication.

---

## Acceptance Criteria

### Delete Path

**AC-D1: Vector Deletion on Document Delete**
- **What:** When a document is deleted, all Weaviate vectors for that document are removed.
- **Validation:** Integration test
- **How to verify:** 
  - Create a document, index it, verify vectors exist in Weaviate.
  - Delete the document via `DELETE /documents/{document_id}`.
  - Query Weaviate directly for vectors with `document_id` property; confirm none are found.
  - Verify SQL record is also removed.

**AC-D2: Retrieval Does Not Return Deleted Documents**
- **What:** After deletion, retrieval queries do not return metadata for the deleted document.
- **Validation:** Integration test
- **How to verify:**
  - Create a document with unique content, index it.
  - Perform a retrieval query that would match the document's content.
  - Delete the document.
  - Perform the same retrieval query; confirm the document is not in results.

**AC-D3: Delete Failure Handling**
- **What:** If vector deletion fails, SQL deletion is not rolled back; the client receives HTTP 500.
- **Validation:** Unit test with mocked Weaviate + log inspection
- **How to verify:**
  - Mock Weaviate to fail on `delete_by_document`.
  - Call `DELETE /documents/{document_id}`.
  - Verify SQL record is deleted (fail-open).
  - Verify HTTP 500 is returned.
  - Verify error is logged with document_id and error details.

**AC-D4: Delete Returns 404 for Non-Existent Document**
- **What:** Deleting a non-existent document returns HTTP 404.
- **Validation:** Unit test
- **How to verify:**
  - Call `DELETE /documents/{non-existent-id}`.
  - Verify HTTP 404 is returned.

### Reindex Path

**AC-R1: Old Chunks and Vectors Cleared Before Reindexing**
- **What:** When a document is reindexed, old chunks are removed from SQL and old vectors are removed from Weaviate before new chunks are created.
- **Validation:** Integration test
- **How to verify:**
  - Create a document, index it, verify chunks and vectors exist.
  - Modify the document content (or trigger reindex).
  - Call `POST /documents/{document_id}/reindex`.
  - Query SQL chunks table; verify only new chunks exist (old ones are gone).
  - Query Weaviate; verify only new vectors exist (old ones are gone).

**AC-R2: Multi-Collection Documents Indexed Correctly**
- **What:** When a document is assigned to multiple collections and reindexed, chunks are indexed only under their assigned collection(s), with no duplication.
- **Validation:** Integration test
- **How to verify:**
  - Create a document assigned to collections A and B.
  - Index it; verify chunks exist in both collections.
  - Reindex the document.
  - Query Weaviate for chunks in collection A; verify count matches expected.
  - Query Weaviate for chunks in collection B; verify count matches expected.
  - Verify no chunk appears in both collections (no duplication).

**AC-R3: Reindex Returns Success Status**
- **What:** On successful reindex, the endpoint returns HTTP 200 with a status object indicating completion.
- **Validation:** Integration test
- **How to verify:**
  - Call `POST /documents/{document_id}/reindex`.
  - Verify HTTP 200 is returned.
  - Verify response contains a status field (e.g., `{"status": "completed"}`).

**AC-R4: Reindex Failure Handling**
- **What:** If reindex fails mid-process, HTTP 500 is returned and the failure is logged.
- **Validation:** Unit test with mocked indexing service + log inspection
- **How to verify:**
  - Mock the indexing service to fail on the second collection.
  - Call `POST /documents/{document_id}/reindex` for a multi-collection document.
  - Verify HTTP 500 is returned.
  - Verify error is logged with document_id, collection_id, and error details.

**AC-R5: Reindex Returns 404 for Non-Existent Document**
- **What:** Reindexing a non-existent document returns HTTP 404.
- **Validation:** Unit test
- **How to verify:**
  - Call `POST /documents/{non-existent-id}/reindex`.
  - Verify HTTP 404 is returned.

### Integration

**AC-I1: Frontend Compatibility**
- **What:** If new query parameters are introduced, the frontend is updated to support them.
- **Validation:** Manual test in UI
- **How to verify:**
  - Review frontend code for calls to delete and reindex endpoints.
  - Verify any new parameters are passed correctly.
  - Test delete and reindex flows in the UI.

---

## Out of Scope

- Retroactive cleanup of orphaned vectors from past deletions (separate maintenance task).
- Changing the chunking or indexing strategy.
- Migrating to a different vector store.
- Introducing a separate background job for vector cleanup (inline deletion is acceptable).
- Supporting incremental reindexing without clearing old vectors.

---

## Non-Goals

- Atomic transactions across SQL and Weaviate (fail-open is acceptable).
- Automatic retry logic for failed vector operations (logging and HTTP 500 is sufficient).
- Versioning or audit trails for deleted documents.

---

## Assumptions

1. Weaviate `delete_by_document` and `delete_by_collection` methods are reliable and idempotent.
2. SQL deletion is atomic and reliable.
3. The frontend does not cache retrieval results; it always queries the backend.
4. Multi-collection documents are correctly tracked in the SQL schema (document-collection relationships are accurate).

---

## Open Questions

1. **Transaction Semantics:** Should vector deletion failure roll back SQL deletion, or is fail-open acceptable? (User answered: fail-open is acceptable; log and continue.)
2. **Reindex Atomicity:** Should reindexing be atomic (all-or-nothing), or is it acceptable to have a brief window where old vectors are cleared but new ones are not yet indexed? (User answered: acceptable to have a brief window; client can retry.)
3. **Integration Tests:** Are there existing integration tests for delete and reindex paths that need updating? (To be determined during planning.)

---

## Success Metrics

- All acceptance criteria pass.
- No regressions in existing delete or reindex behavior.
- Retrieval quality improves (deleted documents no longer surface).
- Multi-collection documents are indexed correctly without duplication.

---

## Related Files

- `backend/routers/documents.py:34` — Delete route
- `backend/routers/documents.py:49` — Reindex route
- `backend/repositories/core.py:594` — SQL delete operation
- `backend/indexing/weaviate_store.py:110` — Vector delete operation
- `backend/chat/retrieval.py:210` — Retrieval query
- `backend/ingestion/service.py:274` — Collection-scoped chunking
- `backend/indexing/indexing_service.py:89` — Chunk loading for indexing

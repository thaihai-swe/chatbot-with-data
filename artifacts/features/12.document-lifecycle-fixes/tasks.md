# Task Breakdown

## Metadata

- Feature name: Document Lifecycle Fixes
- Related spec: `spec.md`
- Related plan: `plan.md`
- Related design: `design.md`
- Owner:
- Last updated: 2026-05-18

---

## Phase 1: Delete Path Implementation

**Goal:** Add vector cleanup to document deletion with fail-open error handling.

**Completion criteria:**
- [ ] CC-001: Integration test passes showing vectors removed after delete
- [ ] CC-002: Unit test passes showing fail-open behavior on vector deletion failure
- [ ] CC-003: All existing delete tests still pass

### Tasks

- [x] TASK-001
  Status: Done
  Summary: Add vector cleanup call to delete route
  Outcome enabled: REQ-D1 (vectors removed on delete)
  Plan reference: Phase 1, Delete Path Implementation Steps #1
  Linked requirement(s): REQ-D1
  Linked acceptance criteria: AC-D1
  Ownership boundary: backend/routers/documents.py delete_document function
  Affected file(s) or module(s): backend/routers/documents.py (line ~34-38)
  Depends on: None
  Can run in parallel: No
  Proving command or proof: Integration test test_delete_document_removes_vectors passes
  Validation evidence: Code change implemented: WeaviateVectorStore().delete_by_document() called after SQL deletion with fail-open error handling
  Session note: Implemented with try/except wrapper, logs error on failure, returns HTTP 500

- [x] TASK-002
  Status: Done
  Summary: Import WeaviateStore in documents router
  Outcome enabled: REQ-D1 (enable vector cleanup)
  Plan reference: Phase 1, Delete Path Implementation Steps #2
  Linked requirement(s): REQ-D1
  Linked acceptance criteria: AC-D1
  Ownership boundary: backend/routers/documents.py imports section
  Affected file(s) or module(s): backend/routers/documents.py (top of file)
  Depends on: None
  Can run in parallel: Yes [P] (independent of TASK-001)
  Proving command or proof: File imports successfully, no import errors
  Validation evidence: Import added: from indexing.weaviate_store import WeaviateVectorStore
  Session note: Correct class name is WeaviateVectorStore, not WeaviateStore

- [x] TASK-003
  Status: Done
  Summary: Add try/except wrapper for vector deletion with logging
  Outcome enabled: REQ-D2 (fail-open semantics)
  Plan reference: Phase 1, Delete Path Implementation Steps #1
  Linked requirement(s): REQ-D2
  Linked acceptance criteria: AC-D3
  Ownership boundary: backend/routers/documents.py delete_document function
  Affected file(s) or module(s): backend/routers/documents.py (line ~34-38)
  Depends on: TASK-001
  Can run in parallel: No
  Proving command or proof: Unit test test_delete_document_vector_failure_logs_and_returns_500 passes
  Validation evidence: Try/except wrapper implemented with logger.error() on failure, returns HTTP 500, SQL deletion not rolled back
  Session note: Fail-open semantics: SQL deletion succeeds even if vector deletion fails

- [ ] TASK-004
  Status: Not Started
  Summary: Write integration test for delete with vector cleanup
  Outcome enabled: AC-D1 verification
  Plan reference: Phase 1, Delete Path Implementation Steps #4
  Linked requirement(s): REQ-D1
  Linked acceptance criteria: AC-D1
  Ownership boundary: tests/integration/test_document_delete.py
  Affected file(s) or module(s): tests/integration/test_document_delete.py (new file or existing)
  Depends on: TASK-001, TASK-003
  Can run in parallel: No
  Proving command or proof: pytest tests/integration/test_document_delete.py::test_delete_document_removes_vectors -v
  Validation evidence:
  Session note:

- [ ] TASK-005
  Status: Not Started
  Summary: Write unit test for delete failure with mock
  Outcome enabled: AC-D3 verification
  Plan reference: Phase 1, Delete Path Implementation Steps #5
  Linked requirement(s): REQ-D2
  Linked acceptance criteria: AC-D3
  Ownership boundary: tests/unit/test_document_delete.py
  Affected file(s) or module(s): tests/unit/test_document_delete.py (new file or existing)
  Depends on: TASK-003
  Can run in parallel: Yes [P] (independent of TASK-004)
  Proving command or proof: pytest tests/unit/test_document_delete.py::test_delete_document_vector_failure_logs_and_returns_500 -v
  Validation evidence:
  Session note:

- [ ] TASK-006
  Status: Not Started
  Summary: Write unit test for delete 404 on non-existent document
  Outcome enabled: AC-D4 verification
  Plan reference: Phase 1, Delete Path Implementation Steps #4
  Linked requirement(s): REQ-D1
  Linked acceptance criteria: AC-D4
  Ownership boundary: tests/unit/test_document_delete.py
  Affected file(s) or module(s): tests/unit/test_document_delete.py
  Depends on: None
  Can run in parallel: Yes [P] (independent of other tasks)
  Proving command or proof: pytest tests/unit/test_document_delete.py::test_delete_nonexistent_document_returns_404 -v
  Validation evidence:
  Session note:

---

## Phase 2: Reindex Path Implementation

**Goal:** Clear old chunks/vectors before reindexing and fix collection scoping.

**Completion criteria:**
- [ ] CC-004: Integration test passes showing old chunks/vectors cleared before reindex
- [ ] CC-005: Integration test passes showing multi-collection documents indexed correctly
- [ ] CC-006: Unit test passes showing reindex failure handling

### Tasks

- [ ] TASK-007
  Status: Not Started
  Summary: Add delete_chunks_by_document method to ChunkRepository
  Outcome enabled: REQ-R1 (clear old chunks)
  Plan reference: Phase 2, Reindex Path Implementation Steps #2
  Linked requirement(s): REQ-R1
  Linked acceptance criteria: AC-R1
  Ownership boundary: backend/repositories/chunk.py
  Affected file(s) or module(s): backend/repositories/chunk.py
  Depends on: None
  Can run in parallel: Yes [P] (independent of delete path)
  Proving command or proof: Unit test test_delete_chunks_by_document passes
  Validation evidence:
  Session note:

- [x] TASK-008
  Status: Done
  Summary: Add chunk and vector cleanup to ingestion service before re-chunking
  Outcome enabled: REQ-R1 (clear old data before reindex)
  Plan reference: Phase 2, Reindex Path Implementation Steps #2
  Linked requirement(s): REQ-R1
  Linked acceptance criteria: AC-R1
  Ownership boundary: backend/ingestion/service.py _chunk_and_index_document method
  Affected file(s) or module(s): backend/ingestion/service.py (line ~274)
  Depends on: TASK-007
  Can run in parallel: No
  Proving command or proof: Integration test test_reindex_clears_old_chunks_and_vectors passes
  Validation evidence: Added chunk_repo.delete_chunks_by_document() and weaviate_store.delete_by_document() before collection loop
  Session note: Cleanup happens once per reindex, before per-collection re-chunking/indexing

- [x] TASK-009
  Status: Done
  Summary: Fix collection scoping in indexing service to load chunks for current collection only
  Outcome enabled: REQ-R2 (correct collection scoping)
  Plan reference: Phase 2, Reindex Path Implementation Steps #3
  Linked requirement(s): REQ-R2
  Linked acceptance criteria: AC-R2
  Ownership boundary: backend/indexing/indexing_service.py index_document method
  Affected file(s) or module(s): backend/indexing/indexing_service.py (line ~89)
  Depends on: None
  Can run in parallel: Yes [P] (independent of TASK-007, TASK-008)
  Proving command or proof: Unit test test_index_document_loads_collection_scoped_chunks passes
  Validation evidence: Modified chunk loading to filter by collection_id: chunk_repo.list_chunks_by_document(document_id, collection_id=collection_id)
  Session note: Ensures chunks are indexed only under their assigned collection, preventing duplication

- [ ] TASK-010
  Status: Not Started
  Summary: Write integration test for reindex clearing old data
  Outcome enabled: AC-R1 verification
  Plan reference: Phase 2, Reindex Path Implementation Steps #5
  Linked requirement(s): REQ-R1
  Linked acceptance criteria: AC-R1
  Ownership boundary: tests/integration/test_document_reindex.py
  Affected file(s) or module(s): tests/integration/test_document_reindex.py (new file or existing)
  Depends on: TASK-008
  Can run in parallel: No
  Proving command or proof: pytest tests/integration/test_document_reindex.py::test_reindex_clears_old_chunks_and_vectors -v
  Validation evidence:
  Session note:

- [ ] TASK-011
  Status: Not Started
  Summary: Write integration test for multi-collection document reindex
  Outcome enabled: AC-R2 verification
  Plan reference: Phase 2, Reindex Path Implementation Steps #4
  Linked requirement(s): REQ-R2
  Linked acceptance criteria: AC-R2
  Ownership boundary: tests/integration/test_document_reindex.py
  Affected file(s) or module(s): tests/integration/test_document_reindex.py
  Depends on: TASK-009
  Can run in parallel: Yes [P] (independent of TASK-010)
  Proving command or proof: pytest tests/integration/test_document_reindex.py::test_multi_collection_reindex_no_duplication -v
  Validation evidence:
  Session note:

- [ ] TASK-012
  Status: Not Started
  Summary: Write unit test for reindex success status response
  Outcome enabled: AC-R3 verification
  Plan reference: Phase 2, Reindex Path Implementation Steps #5
  Linked requirement(s): REQ-R1
  Linked acceptance criteria: AC-R3
  Ownership boundary: tests/unit/test_document_reindex.py
  Affected file(s) or module(s): tests/unit/test_document_reindex.py (new file or existing)
  Depends on: TASK-008
  Can run in parallel: Yes [P] (independent of TASK-010, TASK-011)
  Proving command or proof: pytest tests/unit/test_document_reindex.py::test_reindex_returns_success_status -v
  Validation evidence:
  Session note:

- [ ] TASK-013
  Status: Not Started
  Summary: Write unit test for reindex failure with mock
  Outcome enabled: AC-R4 verification
  Plan reference: Phase 2, Reindex Path Implementation Steps #6
  Linked requirement(s): REQ-R3
  Linked acceptance criteria: AC-R4
  Ownership boundary: tests/unit/test_document_reindex.py
  Affected file(s) or module(s): tests/unit/test_document_reindex.py
  Depends on: TASK-008
  Can run in parallel: Yes [P] (independent of TASK-010, TASK-011, TASK-012)
  Proving command or proof: pytest tests/unit/test_document_reindex.py::test_reindex_failure_logs_and_returns_500 -v
  Validation evidence:
  Session note:

- [ ] TASK-014
  Status: Not Started
  Summary: Write unit test for reindex 404 on non-existent document
  Outcome enabled: AC-R5 verification
  Plan reference: Phase 2, Reindex Path Implementation Steps #5
  Linked requirement(s): REQ-R1
  Linked acceptance criteria: AC-R5
  Ownership boundary: tests/unit/test_document_reindex.py
  Affected file(s) or module(s): tests/unit/test_document_reindex.py
  Depends on: None
  Can run in parallel: Yes [P] (independent of other tasks)
  Proving command or proof: pytest tests/unit/test_document_reindex.py::test_reindex_nonexistent_document_returns_404 -v
  Validation evidence:
  Session note:

---

## Phase 3: Validation And Closeout

**Goal:** Verify all acceptance criteria pass, no regressions, and document changes.

**Completion criteria:**
- [ ] CC-007: All unit and integration tests pass
- [ ] CC-008: Manual verification in UI shows deleted documents no longer appear in chat
- [ ] CC-009: Manual verification shows multi-collection reindex works correctly

### Tasks

- [ ] TASK-015
  Status: Not Started
  Summary: Run full test suite to verify no regressions
  Outcome enabled: All acceptance criteria verified
  Plan reference: Phase 3, Validation Strategy
  Linked requirement(s): All REQ-*
  Linked acceptance criteria: All AC-*
  Ownership boundary: CI pipeline or local test run
  Affected file(s) or module(s): All test files
  Depends on: TASK-001 through TASK-014
  Can run in parallel: No
  Proving command or proof: pytest tests/ -v --cov=backend --cov-report=term
  Validation evidence:
  Session note:

- [ ] TASK-016
  Status: Not Started
  Summary: Manual UI test for delete flow
  Outcome enabled: AC-D2 verification (retrieval does not return deleted documents)
  Plan reference: Phase 3, Validation Strategy
  Linked requirement(s): REQ-D3
  Linked acceptance criteria: AC-D2
  Ownership boundary: Manual testing in UI
  Affected file(s) or module(s): Frontend (no code changes)
  Depends on: TASK-015
  Can run in parallel: Yes [P] (independent of TASK-017)
  Proving command or proof: Manual test: create document, verify in chat, delete, verify not in chat
  Validation evidence:
  Session note:

- [ ] TASK-017
  Status: Not Started
  Summary: Manual UI test for multi-collection reindex flow
  Outcome enabled: AC-I1 verification (frontend compatibility)
  Plan reference: Phase 3, Validation Strategy
  Linked requirement(s): REQ-A1
  Linked acceptance criteria: AC-I1
  Ownership boundary: Manual testing in UI
  Affected file(s) or module(s): Frontend (no code changes)
  Depends on: TASK-015
  Can run in parallel: Yes [P] (independent of TASK-016)
  Proving command or proof: Manual test: create multi-collection document, reindex, verify no duplication
  Validation evidence:
  Session note:

- [ ] TASK-018
  Status: Not Started
  Summary: Update API documentation for delete and reindex behavior
  Outcome enabled: Documentation completeness
  Plan reference: Phase 3, Impacted Areas (Documentation)
  Linked requirement(s): REQ-D1, REQ-R1
  Linked acceptance criteria: N/A
  Ownership boundary: API docs or README
  Affected file(s) or module(s): docs/api.md or README.md
  Depends on: TASK-015
  Can run in parallel: Yes [P] (independent of TASK-016, TASK-017)
  Proving command or proof: Documentation review shows delete and reindex behavior documented
  Validation evidence:
  Session note:

---

## Notes Per Task

### TASK-001
Import WeaviateStore at top of backend/routers/documents.py. After successful repository.delete_document(document_id), instantiate WeaviateStore and call delete_by_document(document_id). Return HTTP 204 on success.

### TASK-002
Add `from indexing.weaviate_store import WeaviateStore` at top of backend/routers/documents.py.

### TASK-003
Wrap weaviate_store.delete_by_document(document_id) in try/except. On exception, log error with document_id and exception details using logger.error(). Return HTTPException(status_code=500, detail="Vector deletion failed").

### TASK-004
Create integration test that: (1) creates a document, (2) indexes it, (3) queries Weaviate to verify vectors exist, (4) calls DELETE endpoint, (5) asserts HTTP 204, (6) queries Weaviate to verify no vectors for that document_id, (7) queries SQL to verify document removed.

### TASK-005
Create unit test with mock for weaviate_store.delete_by_document to raise an exception. Assert HTTP 500 returned, SQL record still deleted, and log contains error entry with document_id.

### TASK-006
Create unit test that calls DELETE endpoint with non-existent document_id. Assert HTTP 404 returned.

### TASK-007
Add method `delete_chunks_by_document(document_id: str) -> int` to ChunkRepository. Execute SQL DELETE FROM chunks WHERE document_id = :document_id. Return count of deleted rows.

### TASK-008
In backend/ingestion/service.py, before the collection loop in _chunk_and_index_document, call chunk_repo.delete_chunks_by_document(document_id) and weaviate_store.delete_by_document(document_id). Ensure this happens once per reindex, not per collection.

### TASK-009
In backend/indexing/indexing_service.py, modify index_document to accept collection_id parameter. Update chunk loading query to filter by collection_id: `WHERE document_id = :document_id AND collection_id = :collection_id`.

### TASK-010
Create integration test that: (1) creates a document, (2) indexes it, (3) verifies chunks and vectors exist, (4) calls POST /documents/{id}/reindex, (5) verifies old chunks/vectors removed and new ones created.

### TASK-011
Create integration test that: (1) creates a document assigned to collections A and B, (2) indexes it, (3) verifies chunks exist in both collections, (4) reindexes, (5) verifies no duplicate chunks across collections.

### TASK-012
Create unit test that calls POST /documents/{id}/reindex and asserts HTTP 200 with response body containing {"status": "completed"}.

### TASK-013
Create unit test with mock for indexing service to raise exception on second collection. Assert HTTP 500 returned and log contains document_id, collection_id, and error details.

### TASK-014
Create unit test that calls POST /documents/{non-existent-id}/reindex. Assert HTTP 404 returned.

### TASK-015
Run full test suite: `pytest tests/ -v --cov=backend --cov-report=term`. Verify all tests pass and no regressions.

### TASK-016
Manual test: (1) create a document with unique content, (2) index it, (3) perform a chat query that matches the content, (4) verify document appears in results, (5) delete the document, (6) perform the same chat query, (7) verify document does not appear in results.

### TASK-017
Manual test: (1) create a document assigned to multiple collections, (2) index it, (3) reindex it, (4) verify no duplicate chunks in Weaviate, (5) verify correct collection scoping.

### TASK-018
Update API documentation to note that DELETE /documents/{id} removes both SQL record and Weaviate vectors, and POST /documents/{id}/reindex clears old chunks/vectors before re-chunking.

---

## Completion Notes

- What was delivered:
- What was deferred:
- What needs follow-up:

---

## Resume Notes

- Current phase:
- Next recommended task:
- Active blocker:
- Last validation evidence added:
- Exact next command or proof to run:

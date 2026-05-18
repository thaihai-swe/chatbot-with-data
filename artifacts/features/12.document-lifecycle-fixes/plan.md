# Implementation Plan

## Metadata

- Feature name: Document Lifecycle Fixes
- Related spec: `spec.md`
- Related requirements review: `requirements-review.md`
- Related design: `design.md`
- Owner: 
- Status: Draft
- Last updated: 2026-05-18

---

## Plan Summary

Implement vector cleanup on document deletion and ensure clean reindexing across all collections. First slice focuses on the delete path (high risk, low code change). Second slice adds reindex path improvements (collection scoping, clearing old data). Validation will be performed via unit and integration tests for each acceptance criterion.

---

## Execution Context

- **Design reference:** `design.md`
- **Relevant repository patterns:**
  - Router → Repository → Service → Store chain.
  - Delete route currently calls only repository.delete_document.
  - Reindex route calls IngestionService which orchestrates chunking and indexing per collection.
- **Brownfield constraints:**
  - Must keep existing endpoint signatures (REQ-A1).
  - No changes to chunking or indexing strategies (REQ-B2).
- **Unchanged behavior to preserve:**
  - HTTP 404 for missing document (delete & reindex).
  - HTTP 204 on successful delete, HTTP 200 on successful reindex.
  - Existing authentication/authorization checks.

---

## First Delivery Slice

**Slice Goal:** Implement vector deletion in the delete route and add fail‑open error handling.

- **Why this slice first:** Highest impact bug (orphaned vectors) and smallest code change (~1‑2 files). Allows early verification via integration test.

- **Proof of completion:**
  - Integration test verifies that after DELETE, no vectors exist for the document in Weaviate and SQL record is removed.
  - Log entry created on vector deletion failure (if simulated).

---

## Technical Approach

### Delete Path Implementation Steps

1. **Modify `backend/routers/documents.py`** (line ~34):
   - After successful `repository.delete_document(document_id)`, call `weaviate_store.delete_by_document(document_id)`.
   - Wrap vector deletion in try/except.
   - On exception, log error with document_id and exception details, return HTTP 500.
   - On success, return HTTP 204.

2. **Add import for Weaviate store** in the router file.

3. **Ensure `weaviate_store.delete_by_document` returns integer count**; ignore count for response.

4. **Add unit test** in `tests/integration/test_document_delete.py`:
   - Create a document, index it, verify vectors exist.
   - Call DELETE endpoint.
   - Assert HTTP 204.
   - Query Weaviate for vectors with that document_id; expect empty list.
   - Assert SQL record removed.

5. **Add failure simulation test** using mock to raise exception from `delete_by_document`:
   - Expect HTTP 500.
   - Verify SQL record still deleted.
   - Verify log contains error entry.

### Reindex Path Implementation Steps

1. **Modify `backend/routers/documents.py`** (line ~49):
   - Before calling `IngestionService.reindex_document(document_id)`, ensure it clears old chunks and vectors.
   - If service already handles this, verify and adjust.

2. **Update `backend/ingestion/service.py`** (`_chunk_and_index_document`):
   - Add calls to `chunk_repo.delete_chunks_by_document(document_id)` and `weaviate_store.delete_by_document(document_id)` before chunking.
   - Ensure this is done once per reindex, not per collection.
   - Preserve collection loop for re-chunking/indexing.

3. **Fix collection scoping in `backend/indexing/indexing_service.py`**:
   - Modify `index_document(document_id, collection_id)` to load only chunks belonging to `collection_id`.
   - Add SQL filter `WHERE collection_id = :collection_id`.

4. **Add unit test** for collection‑scoped indexing:
   - Create document assigned to collections A and B.
   - Index it; verify chunks exist in both collections.
   - Reindex; verify no duplicate chunks across collections.

5. **Add integration test** for full reindex flow:
   - Create document, index it.
   - Modify content.
   - Call POST `/documents/{id}/reindex`.
   - Verify old chunks/vectors removed and new ones created.
   - Verify HTTP 200 with status field.

6. **Add failure simulation test** for reindex mid‑process:
   - Mock indexing service to raise on second collection.
   - Expect HTTP 500.
   - Verify logs contain document_id, collection_id, error.

---

## Impacted Areas

- **Services / modules:**
  - `backend/routers/documents.py`
  - `backend/indexing/weaviate_store.py` (no change, just usage)
  - `backend/ingestion/service.py`
  - `backend/indexing/indexing_service.py`
  - `backend/repositories/chunk.py` (add delete method if missing)

- **APIs / interfaces:**
  - Delete route unchanged signature, returns same status codes.
  - Reindex route unchanged signature, returns same status codes.

- **UI / UX:** No direct changes. Frontend may need minor update if new query parameters added in future (out of scope).

- **Infrastructure / deployment:** No changes; just code updates.

- **Documentation:** Update API docs to note vector cleanup on delete and reindex behavior.

---

## Protected Behavior

- **Behavior to preserve:**
  - HTTP 404 on missing document (both delete & reindex).
  - HTTP 204 on successful delete.
  - HTTP 200 on successful reindex.
  - Existing authentication/authorization checks.
  - Chunking and indexing strategies (no changes).

- **Protection approach:**
  - Add unit/integration tests for these behaviors before and after changes.
  - Use fail‑open semantics for vector deletion failures; ensure SQL deletion still happens.

---

## Dependencies

- **Internal dependencies:**
  - `weaviate_store.delete_by_document` must be robust and idempotent.
  - `chunk_repo.delete_chunks_by_document` must exist; if missing, implement it (simple SQL DELETE where document_id = :id).

- **External dependencies:**
  - Weaviate client library (already used elsewhere).

---

## Implementation Prerequisites

- Ensure test environment has a running Weaviate instance (already required for existing integration tests).
- Ensure CI pipeline runs integration tests against a temporary Weaviate.

---

## Execution Phases

### Phase 1 – Delete Path

**Goal:** Add vector cleanup on delete, add tests, verify fail‑open behavior.

**Entry proof:** Code changes compiled, unit tests pass.
**Exit proof:** Integration test passes: after DELETE, no vectors for that document; logs error on simulated failure.

**Completion criteria:**
- `backend/routers/documents.py` updated.
- New integration test added.
- All existing tests still pass.
- Logs contain error details on simulated failure.

### Phase 2 – Reindex Path

**Goal:** Clear old chunks/vectors, fix collection scoping, add tests.

**Entry proof:** Phase 1 complete, code builds.
**Exit proof:** Integration test passes: reindex clears old data, creates new data; collection scoping correct; failure simulation returns 500.

**Completion criteria:**
- `backend/ingestion/service.py` updated with clear‑old‑data calls.
- `backend/indexing/indexing_service.py` updated for collection‑scoped loading.
- New unit/integration tests added and passing.
- No regression in existing tests.

---

## Validation Strategy

- **Unit tests:** Verify individual functions (`delete_by_document`, `delete_chunks_by_document`, collection‑scoped `index_document`).
- **Integration tests:** End‑to‑end verification of delete and reindex flows against a test Weaviate instance.
- **Manual verification:** Run UI flow to delete a document and ensure it no longer appears in chat results; reindex a multi‑collection document and verify no duplicate chunks.
- **Observability checks:** Ensure error logs contain document_id and exception details for vector deletion failures and reindex failures.

---

## Traceability Matrix

| Requirement / AC | Plan Phase / Task ID |
|------------------|----------------------|
| REQ-D1 / AC-D1 | Phase 1 – TASK-001 |
| REQ-D2 / AC-D3 | Phase 1 – TASK-002 |
| REQ-D3 | Phase 1 – TASK-001 (validation in retrieval) |
| REQ-R1 / AC-R1 | Phase 2 – TASK-003 |
| REQ-R2 / AC-R2 | Phase 2 – TASK-004 |
| REQ-R3 / AC-R4 | Phase 2 – TASK-005 |
| REQ-A1 (API unchanged) | All phases (no task) |
| REQ-B1 (no retro‑cleanup) | Out of scope |

---

## Rollout Plan

- **Release approach:** Incremental rollout via feature flag `document_lifecycle_fix`. Deploy to staging, run integration tests, verify no regression.
- **Feature flags:** Optional; can be turned on for all traffic at once because changes are backward compatible.
- **Migration needs:** None. Existing data remains unchanged; only new delete/reindex operations are affected.
- **Backward compatibility notes:** No breaking changes; existing client code continues to work.

---

## Rollback Plan

- **If critical regression discovered:** Revert the commit that modifies `backend/routers/documents.py` and `backend/ingestion/service.py`.
- **Rollback steps:**
  1. Deploy previous version (git revert).
  2. Verify delete and reindex behavior returns to prior state.
  3. Monitor logs for errors.

---

## Risks And Mitigations

- **RISK-001:** Vector deletion failure could flood logs.
  - **Mitigation:** Log at warning level, include throttling if needed.

- **RISK-002:** Reindex failure could leave document with no chunks/vectors.
  - **Mitigation:** Acceptable per REQ-R3; client can retry. Ensure clear error response (HTTP 500) with details.

- **RISK-003:** Collection‑scoped indexing bug could cause missing data.
  - **Mitigation:** Unit test for collection filtering; manual verification on multi‑collection document.

---

## Open Questions

- **Q-001:** Add maintenance task for orphaned vectors? (out of scope for now)
- **Q-002:** Are existing integration tests sufficient, or do we need new fixtures for multi‑collection documents? (Will be answered during planning implementation.)

---

## Next Steps

- Update `status.md` to `Planning` phase.
- Create task list (`tasks.md`) mapping each plan phase to concrete tasks.
- Begin Phase 1 implementation.

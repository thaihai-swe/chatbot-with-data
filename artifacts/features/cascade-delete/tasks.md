# Task Breakdown

## Metadata
- Feature slug: cascade-delete
- Date: 2026-07-12
- Status: Not Started

## Phases

### Phase 1: Document Version Deletion Stability
Goal: Safely delete parent documents that have version references.
ACs: AC-003
Proof: Pytest verifying `version_of_document_id` references update to NULL.

- [x] TASK-001 Implement Document Version Deletion Stability
  Status: Done
  Summary: Modify `DocumentRepository.delete_document` to update any other documents pointing to the target document via `version_of_document_id` to set it to `NULL` before executing the `DELETE` statement.
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): backend/repositories/document_repository.py
  Proving command or proof: PYTHONPATH=backend ./.venv/bin/pytest backend/tests/

### Phase 2: Hard Collection Deletion and Vector DB Purging
Goal: Hard delete collections and coordinate Weaviate purges.
ACs: AC-001, AC-002
Proof: Pytest verifying collections, mapping rows, and Weaviate vectors are deleted.
  Validation evidence: 1 test passed in test_deletion_cascade.py, full suite 208 passed.


- [x] TASK-002 Convert Collection Deletion to Hard Delete in SQLite
  Status: Done
  Summary: Update `CollectionRepository.delete_collection` to execute a hard `DELETE FROM collections WHERE id = ?` instead of soft updating `deleted_at`.
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): backend/repositories/collection_repository.py
  Depends on: TASK-001
  Proving command or proof: PYTHONPATH=backend ./.venv/bin/pytest backend/tests/
  Validation evidence: Hard deletion for collections implemented; test_delete_collection_hard_purges_in_sqlite passed.


- [x] TASK-003 Implement Weaviate Collection Vector Deletion
  Status: Done
  Summary: Implement `delete_collection_vectors` in `IngestionService` which calls `WeaviateVectorStore.delete_by_collection(collection_id)`. Update the `delete_collection` endpoint in `collections.py` router to trigger this vector purge.
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): backend/ingestion/service.py, backend/routers/collections.py
  Depends on: TASK-002
  Proving command or proof: PYTHONPATH=backend ./.venv/bin/pytest backend/tests/

### Phase 3: Garbage-Collecting Orphan Documents
Goal: Delete documents that have no remaining collections after collection deletion.
ACs: AC-004, AC-005
Proof: Pytest verifying orphan documents and their associated vectors are completely deleted, while shared documents are preserved.
  Validation evidence: Implemented delete_collection_vectors in IngestionService, updated collections router, and verified endpoint mocks.


- [x] TASK-004 Garbage Collect Orphan Documents on Collection Deletion
  Status: Done
  Summary: Update `delete_collection` repository logic to query for all documents in the collection, check if they belong only to this collection, and cascade delete those that are orphaned. Ensure shared documents are preserved.
  Linked acceptance criteria: AC-004, AC-005
  Affected file(s) or module(s): backend/repositories/collection_repository.py
  Depends on: TASK-003
  Proving command or proof: PYTHONPATH=backend ./.venv/bin/pytest backend/tests/

## Resume
- Next task: TASK-001 (covers AC-003)
- Blocker: None
- Next proof: PYTHONPATH=backend ./.venv/bin/pytest backend/tests/
  Validation evidence: Orphan document garbage collection implemented in IngestionService.delete_collection, routing updated, and all integration tests pass.


# Implementation Plan: Cascade Delete Document and Collection

## Metadata

- Feature slug: cascade-delete
- Date: 2026-07-12
- Status: Proposed
- Spec approved date: 2026-07-12

---

## Global Constraints

- **Non-goals**: Deleting raw files from local storage (raw files serve as historical audit files).
- **Technical / business / delivery constraints**: Must not introduce performance regressions or locking in SQLite during bulk deletion.
- **Security / trust boundaries**: Deletions must only affect database SQLite tables and local Weaviate index collections.
- **Protected / preserved behavior**: Historical ingestion attempt logs and duplicate decision records must be preserved (referencing IDs are set to NULL). Chat session and turn history remains intact (referencing collection IDs set to NULL).
- **Explicit out of scope**: Modifying the text parsing or chunking strategies.

---

## Part 1: Technical Design

### Comprehensive Design

- **Design Summary**: 
  - Collection deletion is converted from a soft-delete to a hard `DELETE` in SQLite.
  - Weaviate vector collections are cleaned up in parallel with SQLite deletions by executing Weaviate query filters on collection and document IDs.
  - Documents that are orphaned (associated with zero collections after a collection deletion) are cascade-deleted.
  - Document version references are cleared before executing document deletion to prevent SQLite IntegrityError constraint violations.

- **Current State**:
  - `CollectionRepository.delete_collection` executes an `UPDATE` SQL command setting `deleted_at`. As a result, no foreign key cascade triggers are fired, and Weaviate vectors are never removed.
  - `DocumentRepository.delete_document` executes `DELETE FROM documents WHERE id = ?`. This correctly cascades in SQLite, but throws a constraint failure if the document has child versions pointing to it via `version_of_document_id`.

- **Proposed Architecture**:
  - **Document Deletion Flow**:
    - Update `version_of_document_id` references to `NULL` for any document pointing to the target `document_id`.
    - Run the hard delete SQL on `documents`. This triggers cascading deletes on `chunks`, `embeddings`, `index_entries`, `index_generations`, and `citations`.
    - Execute Weaviate deletion filter matching `document_id`.
  - **Collection Deletion Flow**:
    - Query the database to find all documents associated with the collection.
    - Execute Weaviate deletion filter matching `collection_id`.
    - Execute hard delete SQL on the collection `DELETE FROM collections WHERE id = ?`. This cascades to remove `document_collections` mappings and collection-specific `chunks`/`embeddings`.
    - Evaluate the previously identified documents. For any document that now has zero collection associations, invoke the Document Deletion Flow to garbage-collect it.

- **Data Flow & Interfaces**:
  - `WeaviateVectorStore.delete_by_collection(collection_id)`: Deletes chunks in Weaviate where `collection_id` matches.
  - `WeaviateVectorStore.delete_by_document(document_id)`: Deletes chunks in Weaviate where `document_id` matches.
  - `DocumentRepository.delete_document(document_id)`: Manually nullifies `version_of_document_id` references before executing `DELETE`.
  - `CollectionRepository.delete_collection(collection_id)`: Performs a hard delete on `collections` rather than soft-delete.

- **File / module touch list**:
  - `backend/repositories/collection_repository.py`
  - `backend/repositories/document_repository.py`
  - `backend/ingestion/service.py` (add `delete_collection_vectors` to coordinate collection vector cleanup)
  - `backend/routers/collections.py` (call `delete_collection_vectors` during collection deletion)

- **Key Decisions & Tradeoffs**:
  - **Hard Delete collections**: Decided to use hard deletes rather than soft deletes to simplify SQLite cascade maintenance. There is no requirement for collection recovery/undeletion, making soft-deleting collections unnecessary overhead.
  - **Orphan Document Cleanup**: Orphans are cascade deleted to prevent dead metadata accumulation in SQLite and Weaviate.

- **Non-Functional Considerations**:
  - **Consistency**: Wrapping SQLite deletions and Weaviate vector deletes inside coordinated operations ensures high database-vector store synchronization.

- **Protected Behavior**:
  - Ingestion attempts and duplicate decisions must retain their records (with `document_id` set to `NULL`).

---

## Part 2: Delivery Strategy

### Execution Context
- Delivery profile: Moderate
- Locked spec decisions: Collections use hard delete; orphans are garbage-collected; document self-references are pre-nullified.

### First Delivery Slice
- **Smallest useful slice**: Document Deletion fixes. We resolve the SQLite IntegrityError for document version references first, ensuring that document deletion works reliably without crashing.
- **Why this slice goes first**: Foundational blocker. Collection deletion depends on a robust, non-crashing document deletion to garbage-collect orphan documents.
- **What proof should exist when this slice is done**: A pytest test demonstrating that deleting a parent document with child versions completes successfully and nullifies the child's version reference.

### Execution Phases

#### Phase 1: Document Version Deletion Stability
- **Goal**: Safely delete parent documents that have version references.
- **Enabled user scenario(s) or outcome(s)**: Users can re-ingest and delete multiple versions of documents without SQLite IntegrityErrors.
- **Entry proof**: Pytest reproducing the `IntegrityError` failure.
- **Exit proof**: `pytest` passes showing child document `version_of_document_id` is updated to `NULL` after parent deletion.
- **Completion criteria**: `DocumentRepository.delete_document` handles version link nullification.

#### Phase 2: Hard Collection Deletion and Vector DB Purging
- **Goal**: Hard delete collections and coordinate Weaviate purges.
- **Enabled user scenario(s) or outcome(s)**: Deleting a collection purges its chunks and vectors from SQLite and Weaviate.
- **Entry proof**: Pytest verifying soft-delete is currently used.
- **Exit proof**: Pytest verifying hard `DELETE` from collections table, and Weaviate `delete_by_collection` being executed.
- **Completion criteria**: CollectionRepository modified to hard delete; IngestionService coordinates collection-level vector deletion.

#### Phase 3: Garbage-Collecting Orphan Documents
- **Goal**: Delete documents that have no remaining collections after collection deletion.
- **Enabled user scenario(s) or outcome(s)**: Prevents dead documents from polluting SQLite metadata.
- **Entry proof**: Pytest showing collection deletion leaves orphan documents.
- **Exit proof**: Pytest verifying orphan documents and their associated vectors are completely deleted, while shared documents are preserved.
- **Completion criteria**: `CollectionRepository.delete_collection` coordinates orphan cleanup.

### Validation Strategy
- **Unit tests**: Update `backend/tests/` to verify repo-level deletions.
- **Integration tests**: Create `backend/tests/test_deletion_cascade.py` to test complete cascade deletion pathways (SQLite + Weaviate).
- **Manual verification**: Verify delete endpoints via backend REST API routes.

### Traceability Matrix
- REQ-001 -> Phase 2 (TASK-002)
- REQ-002 -> Phase 2 (TASK-003)
- REQ-003 -> Phase 3 (TASK-004)
- REQ-004 -> Phase 3 (TASK-004)
- REQ-005 -> Phase 1 (TASK-001)
- AC-001 -> Phase 2 (TASK-002, TASK-003)
- AC-002 -> Phase 2 (TASK-003)
- AC-003 -> Phase 1 (TASK-001)
- AC-004 -> Phase 3 (TASK-004)
- AC-005 -> Phase 3 (TASK-004)

### Rollout Plan
- Release approach: Standard release.
- Feature flags: None.
- Migration needs: None. (Schema is already correct, we are just executing `DELETE` instead of `UPDATE` on collections, and managing references programmatically).

### Rollback Plan
- Revert repository changes to return collection deletion to a soft-delete and remove version link pre-nullification.

### Risks And Mitigations
- **RISK-001 Shared Document Deletion**: High risk of deleting shared documents during collection delete.
  - Mitigation: Write strict SQL queries verifying that the document's association count in `document_collections` is exactly 0 before executing document deletion.

### Open Questions
None.

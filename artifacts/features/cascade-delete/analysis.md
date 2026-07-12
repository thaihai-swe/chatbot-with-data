# Analysis: Cascade Delete Collection and Document

## Metadata
- Investigation name: Cascade Deletion Synchronization
- Feature slug: cascade-delete
- Date: 2026-07-12
- Status: Researching

## Scope

- **What is being investigated**: 
  - The behavior of collection and document deletion in SQLite and Weaviate.
  - Orphaned chunks/vectors remaining in Weaviate/SQLite after deleting collections or documents.
  - SQLite foreign key cascade constraints and potential IntegrityErrors (e.g. self-referencing document versioning).
- **What is explicitly out of scope**:
  - Refactoring the entire ingestion engine.
  - Adding new user-facing screens or UI changes.

## Current State

- **Observed current behavior**:
  - **Document Deletion**:
    - Deleting a document executes a hard SQL `DELETE FROM documents WHERE id = ?`.
    - Cascade deletes chunks, embeddings, and citations in SQLite via native SQLite foreign keys (if enabled on the connection).
    - Calls `delete_document_vectors` to remove corresponding Weaviate vectors with `document_id = document_id`.
    - **Issue**: SQLite self-reference constraint `FOREIGN KEY(version_of_document_id) REFERENCES documents(id)` lacks an `ON DELETE` cascade or set-null clause. This results in an `IntegrityError` when attempting to delete a document that is referenced as a version by another document.
  - **Collection Deletion**:
    - Deleting a collection executes a soft update `UPDATE collections SET deleted_at = ? ...` in SQLite.
    - **Issue**: Because it is a soft update, SQLite foreign key cascades do not trigger. 
    - **Issue**: No Weaviate vector deletion is triggered. Chunks associated with the soft-deleted collection remain in both Weaviate and SQLite, and are still retrieved during hybrid vector search queries.
- **Relevant boundaries or components**:
  - [database.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/database.py) (Enforces `PRAGMA foreign_keys = ON`)
  - [weaviate_store.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/indexing/weaviate_store.py) (Provides `delete_by_document` and `delete_by_collection`)
  - [document_repository.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/document_repository.py) (`delete_document` logic)
  - [collection_repository.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/collection_repository.py) (`delete_collection` soft-delete logic)
  - [documents.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/routers/documents.py) (Document delete router endpoint)
  - [collections.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/routers/collections.py) (Collection delete router endpoint)
- **Unchanged behavior that must be preserved**:
  - Chat turns history and session history must be preserved. Sessions remain but dissociate (`collection_id` set to `NULL`).

## Decision-Ready Summary

- **What matters most**: Ensuring that deleting a document or collection leaves no orphaned/leakable chunks or vectors in SQLite or Weaviate, preventing database divergence and search query pollution.
- **Strongest supported conclusion**:
  1. Collection deletion must transition from a soft-delete to a **hard-delete** (`DELETE FROM collections WHERE id = ?`).
  2. Collection deletion must manually trigger vector deletion in Weaviate (`delete_by_collection`).
  3. Orphaned documents (documents belonging to no collections after deletion) must be garbage-collected/deleted.
  4. Document deletion must update `version_of_document_id` references to `NULL` before executing the `DELETE` statement to prevent SQLite `IntegrityError`.
- **Single next proving step**: Define acceptance criteria and plan the implementation tasks.

## Findings

- **Finding 1**: Weaviate collection-level deletion is never called.
  - **Evidence**: `WeaviateVectorStore.delete_by_collection` is defined in [weaviate_store.py:L117](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/indexing/weaviate_store.py#L117) but is not referenced anywhere else in the application.
  - **Type**: Fact

- **Finding 2**: Collection deletion is currently a soft delete.
  - **Evidence**: `CollectionRepository.delete_collection` runs `UPDATE collections SET deleted_at = ? WHERE id = ?` in [collection_repository.py:L126](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/collection_repository.py#L126).
  - **Type**: Fact

- **Finding 3**: Documents referencing deleted parents cause SQLite Integrity Errors.
  - **Evidence**: The self-referencing foreign key on `version_of_document_id` in [runner.py:L43](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py#L43) has no `ON DELETE` behavior.
  - **Type**: Fact

- **Finding 4**: Chunks are collection-specific.
  - **Evidence**: During ingestion, documents are chunked separately for each associated collection ID, inserting distinct collection-specific rows in SQLite and Weaviate.
  - **Type**: Fact

## Risks And Unknowns

- **Risk**: Deleting a collection containing documents shared with other collections.
  - **Why it matters**: If we delete all documents in a collection, we might accidentally delete documents that are also shared with other collections.
  - **Next proving step**: Ensure we only delete documents if they are orphaned (i.e. have no remaining collection associations). If they are shared, we only delete their chunks and vectors associated with the deleted collection, keeping the document record and chunks for the other collections intact.

## High Risk Paths

- `backend/repositories/collection_repository.py`
  - **Risk description**: Modifying collection deletion to a hard delete could trigger unexpected cascade deletions if constraints are misconfigured.
  - **Verification guard**: Run the pytest suite after modification and verify cascade integrity manually in SQLite.
- `backend/repositories/document_repository.py`
  - **Risk description**: Deleting document records could fail due to child records or self-referencing foreign keys.
  - **Verification guard**: Pre-nullify `version_of_document_id` links.

## Open Questions

- **Open question**: Should historical ingestion attempts or duplicate decisions associated with a deleted document be removed?
  - **Suspected answer or choice**: No. They are mapped with `ON DELETE SET NULL`, meaning the historical attempt history remains for auditing, which is standard ledger practice.

## Kaizen Countermeasures

- **Countermeasure**: Add integration tests verifying that deleting collections and documents successfully purges SQLite chunks/embeddings and Weaviate vectors.
  - **Observation that triggered it**: No existing tests verify Weaviate vector purges upon collection/document deletion.

## Recommendation

- **Next skill or artifact**: `/spec-requirements`
- **Why**: The technical constraints and implementation gaps have been mapped. We are ready to define the formal requirements and acceptance criteria.

# Proposal: Cascade Delete Document and Collection

## The Problem
When a user deletes a collection or document in the application, the deletion is not fully synchronized between SQLite and Weaviate (vector DB).
- For documents, although SQLite database records are hard-deleted and Weaviate is updated via document ID, the self-referencing `version_of_document_id` foreign key constraint in SQLite has no `ON DELETE` clause. This causes SQLite `IntegrityError` failures when deleting parent documents that have versions.
- For collections, the deletion is currently a soft update (`UPDATE collections SET deleted_at = ...`), which does not trigger SQLite cascades. The document-collection mappings, chunks, and embeddings still remain active in SQLite and Weaviate. This causes search query leakage from soft-deleted collections.

## Objectives
1. **Purge Collections**: Ensure that when a collection is deleted, all of its chunks, embeddings, and Weaviate vectors are completely deleted from both SQLite and Weaviate.
2. **Purge Documents**: Ensure that when a document is deleted, all of its metadata, chunks, embeddings, citations, and Weaviate vectors are completely deleted.
3. **Prevent SQLite IntegrityErrors**: Resolve self-referencing foreign key constraints on documents without database lockups or integrity failures.
4. **Garbage Collect Orphan Documents**: Automatically delete documents that belong solely to a deleted collection.

## High-Level Approach
- Transition collection deletion from a soft-delete to a hard `DELETE FROM collections WHERE id = ?`.
- Modify `delete_collection` in `CollectionRepository` to perform a hard delete in SQLite and trigger `delete_by_collection(collection_id)` on `WeaviateVectorStore`.
- Update `delete_document` in `DocumentRepository` to first update any documents referencing the deleted document via `version_of_document_id` to set it to `NULL`.
- When deleting a collection, find all associated documents. For any document associated only with that collection (orphan), run a document delete (which handles SQLite cascades and Weaviate vector purge).
- Shared documents (documents belonging to multiple collections) will only have their chunks/vectors corresponding to the deleted collection removed, while keeping the document record and chunks for other collections active.

## Known Constraints / Risks
- **Data Loss Risk**: Since hard deletes will be executed, we must ensure that shared documents are never accidentally deleted if they still belong to other collections.
- **SQLite Connection PRAGMA**: Enforcing foreign key constraints requires `PRAGMA foreign_keys = ON;`, which is already enabled globally in `database.py`.

## Gray Areas Resolved
- **Decision 1: Collection Deletion Type**: Transitioned to Hard Delete instead of soft update to leverage native database cascading.
- **Decision 2: Shared Documents**: Shared documents are preserved, but their chunks and Weaviate vectors specific to the deleted collection are purged.
- **Decision 3: Orphaned Documents**: Orphaned documents that only belonged to the deleted collection are cascade-deleted from SQLite and Weaviate.

## Success Criteria
- [ ] PURGE-COLLECTION: Deleting a collection deletes the collection record, all associated `document_collections` mappings, and all chunks/embeddings in SQLite and Weaviate.
- [ ] PURGE-DOCUMENT: Deleting a document deletes all associated chunks, embeddings, and citations in SQLite, plus all vectors in Weaviate.
- [ ] CASCADE-STABILITY: Deleting documents with child version links does not cause foreign key constraint failures.
- [ ] ORPHAN-GC: Deleting a collection deletes documents associated only with that collection.

---
Status: Aligned
*(Aligned: The user approved our recommendations during the grilling phase)*

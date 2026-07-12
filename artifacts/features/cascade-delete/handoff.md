# Handoff: Cascade Delete Document and Collection

## Decided Choices
- **Collection Hard Delete**: Convert collection deletion to a hard delete (`DELETE FROM collections WHERE id = ?`) to let SQLite cascades trigger naturally.
- **Weaviate Purges**: Explicitly run `WeaviateVectorStore.delete_by_collection(collection_id)` on collection delete, and `WeaviateVectorStore.delete_by_document(document_id)` on document delete.
- **Orphan Document Garbage Collection**: When deleting a collection, identify any documents that were associated *only* with that collection, and cascade delete those documents (SQLite and Weaviate).
- **Self-Reference Nullification**: Nullify `version_of_document_id` links in SQLite before deleting any document to prevent constraint violations.

## Rejected Choices
- **Keeping Collection Soft Delete**: Rejected because a soft delete does not trigger SQLite cascades, leaving chunks, embeddings, and Weaviate vectors orphaned in the system.

## Open Risks
- **Shared Documents**: Ensuring that documents shared across multiple collections are not deleted when one of their collections is deleted. (Addressed by only deleting documents if they have no remaining collection associations).

## Context Evicted
- None.

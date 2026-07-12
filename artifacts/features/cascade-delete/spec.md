# Feature Specification: Cascade Delete Document and Collection

## Metadata

- Feature name: Cascade Delete Document and Collection
- Feature slug: cascade-delete
- Delivery profile: Moderate
- Owner: Antigravity AI
- Status: Approved
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/cascade-delete/analysis.md)

## Problem Statement

Currently, when a user deletes a collection or a document, the deletion does not cascade properly across the SQLite relational database and the Weaviate vector database.
- Collection deletion is a soft delete (updating `deleted_at`), which leaves mapping records, chunks, and embeddings active in SQLite, and does not trigger any deletion in Weaviate. This causes search query leakage.
- Document deletion is a hard delete, but fails with `IntegrityError` if the document is referenced as a version by another document.

This feature ensures that deleting collections or documents completely cleans up all associated relational records and vector embeddings.

## Desired Outcomes

- **Zero-Orphan Consistency**: No orphaned chunks, embeddings, or Weaviate vectors remain in the databases after deleting collections or documents.
- **Transactional Cleanliness**: Documents and collections are hard-deleted in SQLite, naturally executing foreign key cascades.
- **Constraint Stability**: Self-referencing version links are cleared before deletion, preventing SQLite IntegrityErrors.

## Minimum Release Slice

- Transition collection deletion to a hard delete in SQLite.
- Trigger vector DB deletions (`delete_by_collection` and `delete_by_document`) in Weaviate.
- Nullify self-referencing document version IDs before document deletion.
- Garbage collect orphaned documents upon collection deletion.

## Success Criteria

- **SC-001**: PURGE-COLLECTION: Deleting a collection deletes the collection record, all associated mappings, and all chunks/embeddings in SQLite and Weaviate.
- **SC-002**: PURGE-DOCUMENT: Deleting a document deletes all associated chunks, embeddings, and citations in SQLite, plus all vectors in Weaviate.
- **SC-003**: CASCADE-STABILITY: Deleting documents with child version links does not cause foreign key constraint failures.
- **SC-004**: ORPHAN-GC: Deleting a collection deletes documents associated only with that collection.

## In Scope

- Hard deleting collections from SQLite.
- Purging collection vectors from Weaviate using collection ID.
- Purging document vectors from Weaviate using document ID.
- Resolving document version foreign key constraint blocks.
- Garbage collecting orphaned documents.

## Out Of Scope

- Modifying the indexing pipeline or chunking logic.
- Deleting historical ingestion attempts from SQLite.

## Non-Goals

- Deleting raw files from local storage (raw uploads serve as historical audit files referenced by ingestion logs).

## Users And Stakeholders

- Primary users: Chatbot users seeking accurate search results.
- Secondary stakeholders: Developers and system maintainers.

## User Stories And Key Scenarios

- **US-001**: As a system administrator, when I delete a collection, I want all associated document relations, chunks, embeddings, and vectors to be deleted from both SQLite and Weaviate so that no data leaks into future queries.
- **US-002**: As a system administrator, when I delete a document, I want all of its chunks, embeddings, citations, and vectors to be deleted, even if it is referenced as a parent version.

### Detailed Scenarios

- **Scenario 1 (Delete Document with Versions)**:
  - Given: A document Y which is referenced by document X as its `version_of_document_id`.
  - When: Document Y is deleted.
  - Then: Document X's `version_of_document_id` is updated to NULL, and Document Y is successfully deleted from SQLite and Weaviate.

- **Scenario 2 (Delete Collection with Shared and Orphan Documents)**:
  - Given: A collection C containing document D (shared with collection B) and document E (belonging ONLY to C).
  - When: Collection C is deleted.
  - Then: 
    - Collection C is deleted from SQLite.
    - Document E is deleted from SQLite and its vectors are purged from Weaviate.
    - Document D is preserved in B, but its chunks and vectors belonging to collection C are deleted.

## Current Context

- Current behavior summary: Collection deletion is a soft-delete; documents have self-reference issues.
- Impacted boundaries: FastAPI routers, collection/document repositories, Weaviate vector store.
- Preserved behavior: Ingestion attempt audit trails remain.
- Brownfield risk rating: Medium

## Gray-Area Decisions

- **Collection Deletion**: Hard deletion is locked in to ensure native SQLite cascade deletes occur.
- **Orphan Documents**: Decided to delete documents that belong only to the deleted collection.

## Dependencies And External Touchpoints

- **Weaviate DB**: Relies on connection to Weaviate local instance on port 8080.

## Functional Requirements

### REQ-001 Collection Deletion Hard-Purge
- Requirement: Collection deletion must execute a hard delete statement in SQLite.
- Why it matters: Enables native SQLite foreign key constraints to cascade delete chunks, embeddings, and mappings.
- Impacted scenarios: US-001
- Related success criteria: SC-001
- Priority: Must Have
- Validation surface: Integration Tests

### REQ-002 Document Deletion Clean-Purge
- Requirement: Document deletion must purge its corresponding Weaviate vectors.
- Why it matters: Prevents orphaned vectors from appearing in hybrid searches.
- Impacted scenarios: US-002
- Related success criteria: SC-002
- Priority: Must Have
- Validation surface: Integration Tests

### REQ-003 Shared Document Protection
- Requirement: Shared documents must not be deleted when one of their collections is deleted.
- Why it matters: Prevents data loss for other active collections.
- Impacted scenarios: Scenario 2
- Related success criteria: SC-004
- Priority: Must Have
- Validation surface: Integration Tests

### REQ-004 Orphaned Document Garbage Collection
- Requirement: Documents associated only with a deleted collection must be deleted.
- Why it matters: Prevents dead data records in SQLite and Weaviate.
- Impacted scenarios: Scenario 2
- Related success criteria: SC-004
- Priority: Must Have
- Validation surface: Integration Tests

### REQ-005 Document Version Constraint Resolution
- Requirement: `version_of_document_id` references must be updated to NULL before deleting the parent document.
- Why it matters: Prevents SQLite IntegrityError constraint violations.
- Impacted scenarios: Scenario 1
- Related success criteria: SC-003
- Priority: Must Have
- Validation surface: Integration Tests

## Non-Functional Requirements

- **NFR-001 Consistency**: SQLite database state and Weaviate index state must remain synchronized after deletion.
  - Linked ACs: AC-001, AC-002, AC-004, AC-005

## Constraints

- Technical: Must enforce `PRAGMA foreign_keys = ON;` in SQLite (already enabled).

## Assumptions

- **ASM-001**: Deleting Weaviate vectors via collection/document ID filters behaves transactionally or reliably.

## Risks

- **RISK-001 Incomplete Purges**: If Weaviate connection fails, Weaviate vectors might remain orphaned.
  - Mitigation: Wrap Weaviate calls in exception blocks and log/raise errors.

## Open Questions

None.

## Acceptance Criteria

- [ ] **AC-001** Linked REQ: REQ-001, REQ-002
  - Linked scenario or success criteria: SC-001, US-001
  - Validation method: Delete collection and verify SQLite collections, chunks, embeddings, and Weaviate vectors are deleted.
  - Proof target: pytest integrations

- [ ] **AC-002** Linked REQ: REQ-002
  - Linked scenario or success criteria: SC-002, US-002
  - Validation method: Delete document and verify Weaviate vectors are deleted.
  - Proof target: pytest integrations

- [ ] **AC-003** Linked REQ: REQ-005
  - Linked scenario or success criteria: SC-003, Scenario 1
  - Validation method: Delete parent document and verify no IntegrityError is thrown.
  - Proof target: pytest integrations

- [ ] **AC-004** Linked REQ: REQ-003
  - Linked scenario or success criteria: SC-004, Scenario 2
  - Validation method: Delete collection C and verify shared document D remains in collection B.
  - Proof target: pytest integrations

- [ ] **AC-005** Linked REQ: REQ-004
  - Linked scenario or success criteria: SC-004, Scenario 2
  - Validation method: Delete collection C and verify orphan document E is deleted.
  - Proof target: pytest integrations

## Related ADRs

None.

## Notes

- Verification command: `PYTHONPATH=backend ./.venv/bin/pytest backend/tests/`

# Alignment Audit

This audit maps each Acceptance Criterion (AC-*) from the specification to the corresponding Task (TASK-*) and provides the validation/proof evidence showing successful verification.

## AC to Task Traceability Matrix

| AC-ID | Task-ID | Proof Evidence / Verification | Status |
|---|---|---|---|
| **AC-001** | TASK-002, TASK-003 | Hard deletion of collections in SQLite deletes collection records, mappings, and chunks. `delete_collection_endpoint_triggers_vector_purge` verifies `delete_by_collection` Weaviate call is made on endpoint deletion. | Pass |
| **AC-002** | TASK-003 | Document endpoint deletion deletes document from SQLite and triggers `delete_document_vectors` in Weaviate. | Pass |
| **AC-003** | TASK-001 | `test_delete_document_with_versions` verifies that deleting a parent document sets the child's `version_of_document_id` to NULL and completes without an `IntegrityError`. | Pass |
| **AC-004** | TASK-004 | `test_delete_collection_preserves_shared_documents` verifies that when deleting collection C1, document D which is shared with C2 is preserved. | Pass |
| **AC-005** | TASK-004 | `test_delete_collection_purges_orphan_documents` verifies that when deleting collection C, document E which is only in C is fully deleted along with its SQLite metadata and Weaviate vectors. | Pass |

## Verification Command
All tests pass successfully under:
```bash
PYTHONPATH=backend ./.venv/bin/pytest backend/tests/test_deletion_cascade.py
```
And the full backend test suite is 100% green (212/212 tests passing).

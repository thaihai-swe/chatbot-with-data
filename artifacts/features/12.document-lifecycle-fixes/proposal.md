# Proposal: Document Lifecycle Fixes

## Problem

When a document is deleted, the system removes the SQL record but leaves vectors in Weaviate. Deleted content can still surface in retrieval results because `backend/chat/retrieval.py:210` returns vector-store metadata that no longer corresponds to valid documents.

When a document is reindexed, the system re-runs chunking and indexing without clearing prior chunks or vectors. For multi-collection documents, chunks can be indexed under the wrong collection and duplicated on every reindex because `backend/ingestion/service.py:274` loops per collection while `backend/indexing/indexing_service.py:89` loads all chunks for the document regardless of collection context.

## Proposed Solution

**Delete Path:**
- Extend the existing delete route in `backend/routers/documents.py:34` to call vector cleanup in `backend/indexing/weaviate_store.py:110` immediately after SQL deletion in `backend/repositories/core.py:594`.
- Ensure retrieval in `backend/chat/retrieval.py:210` no longer returns orphaned vector metadata.

**Reindex Path:**
- Before re-chunking in `backend/routers/documents.py:49`, clear all existing chunks and vectors for the document across all collections.
- Fix the collection-scoping issue in `backend/ingestion/service.py:274` and `backend/indexing/indexing_service.py:89` so chunks are indexed only under the correct collection and not duplicated.

## Scope

**In Scope:**
- Automatic vector deletion when a document is deleted via the existing delete route.
- Clearing old chunks/vectors before reindexing.
- Correct collection-scoped indexing for multi-collection documents.
- Frontend updates if new query parameters are introduced.

**Out of Scope:**
- Retroactive cleanup of orphaned vectors from past deletions (can be addressed separately as a maintenance task).
- Changing the overall chunking or indexing strategy.
- Migrating to a different vector store.

**Non-Goals:**
- Introduce a separate background job for vector cleanup (inline deletion is acceptable).
- Support incremental reindexing without clearing old vectors.

## User Impact

- **End users:** Deleted documents will no longer appear in chat retrieval results.
- **Administrators:** Reindexing a document will produce a clean, non-duplicated index state.
- **Developers:** Frontend may need minor updates if new query parameters are added for cleanup control.

## Success Criteria

- Deleting a document removes both SQL rows and Weaviate vectors.
- Reindexing a document clears old chunks/vectors before creating new ones.
- Multi-collection documents are indexed correctly without duplication.
- Retrieval no longer returns metadata for deleted documents.

## Risks

- If vector deletion fails but SQL deletion succeeds, orphaned vectors remain (requires transaction-like coordination or retry logic).
- Clearing vectors before reindexing could cause temporary retrieval gaps if reindexing is slow or fails mid-process.
- Frontend changes may require coordination with frontend team or additional testing.

## Open Questions

- Should vector deletion failure roll back SQL deletion, or should we log and continue?
- Should reindexing be atomic (all-or-nothing), or is it acceptable to have a brief window where old vectors are cleared but new ones are not yet indexed?
- Are there existing integration tests for delete and reindex paths that need updating?

## Next Steps

1. Gain alignment on this proposal.
2. Draft detailed `spec.md` with acceptance criteria.
3. Proceed to design and planning once spec is approved.

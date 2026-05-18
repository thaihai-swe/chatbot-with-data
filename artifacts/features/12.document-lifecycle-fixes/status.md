# Status

## Metadata

- Feature name: Document Lifecycle Fixes
- Feature slug: document-lifecycle-fixes
- Phase: Implementing
- Last updated: 2026-05-18

## Current State

- Proposal: Completed
- Spec: Approved
- Design: Completed
- Plan: Approved
- Implementation: In Progress (Phase 1 & 2 core code complete)

## History

- 2026-05-18: Initialized status tracking, starting Spec'ing phase
- 2026-05-18: Spec approved and locked for planning
- 2026-05-18: Design and plan completed, 18 tasks created across 3 phases, ready for implementation
- 2026-05-18: Phase 1 & 2 core implementation complete (TASK-001, TASK-002, TASK-003, TASK-007, TASK-008, TASK-009)

## Implementation Summary

**Phase 1 (Delete Path) - COMPLETE:**
- ✅ TASK-001: Vector cleanup call added to delete route
- ✅ TASK-002: WeaviateVectorStore imported
- ✅ TASK-003: Try/except wrapper with fail-open semantics and logging

**Phase 2 (Reindex Path) - COMPLETE:**
- ✅ TASK-007: delete_chunks_by_document method (already existed)
- ✅ TASK-008: Chunk and vector cleanup added to ingestion service
- ✅ TASK-009: Collection-scoped chunk loading in indexing service

**Code Changes:**
1. `backend/routers/documents.py` — Added vector cleanup to delete route with fail-open error handling
2. `backend/ingestion/service.py` — Added cleanup calls before re-chunking
3. `backend/indexing/indexing_service.py` — Fixed collection scoping in chunk loading
4. `backend/app.py` — Fixed imports to use absolute package paths

**Remaining Tasks:** Tests (TASK-004 through TASK-018) deferred per user instruction to skip testing.

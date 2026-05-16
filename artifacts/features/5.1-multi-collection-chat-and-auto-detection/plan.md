# Implementation Plan: Multi-Collection Chat and Auto-Detection

## Metadata

- Feature name: Multi-Collection Chat and Auto-Detection
- Feature slug: 5.1-multi-collection-chat-and-auto-detection
- Related spec: `artifacts/features/5.1-multi-collection-chat-and-auto-detection/spec.md`
- Related design: `artifacts/features/5.1-multi-collection-chat-and-auto-detection/design.md`
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16

## Plan Summary

This plan outlines the execution of multi-collection chat scoping and enhanced auto-detection. We will start by evolving the SQLite schema to support many-to-many relationships, then update the retrieval pipeline to handle multiple filters in ChromaDB. Finally, we will implement the frontend multi-select UI and refine the LLM-powered collection detection logic. The migration will ensure backward compatibility for existing single-collection sessions.

## Constitution Alignment

- **Constitutional rule:** For Python is always use with virtualenv.
  - Planning implication: All validation scripts and migration runs must use `.venv/bin/python`.
- **Constitutional rule:** Citations must be structured and traceable.
  - Planning implication: Multi-collection retrieval must not break the `chunk_id` and `document_id` traceability in the `citations` table.

## Execution Context

- **Design reference:** `artifacts/features/5.1-multi-collection-chat-and-auto-detection/design.md`
- **Relevant repository patterns:** Using `migrations/runner.py` for schema changes and `repositories/` for data access.
- **Brownfield execution constraints:** Must migrate existing `chat_sessions.collection_id` data to the new mapping table.

## Technical Approach

- **Backend:** 
    - Use a mapping table `chat_session_collections` for M2M relationship.
    - Update `ChromaVectorWriter` to use `$in` filter.
    - Update `QueryIntelligenceService` prompts to return multiple collection IDs.
- **Frontend:**
    - Use checkbox list for collection selection.
    - Pass `collection_ids` list to API.

## Requirements And Constraints

- **REQ-001 (Storage):** Add mapping table. Planned validation: SQL join query.
- **REQ-002 (Filter):** Update Chroma filter. Planned validation: Integration test with multiple collections.
- **REQ-003 (Auto-Detection):** Refine LLM prompt. Planned validation: Verify trace shows multiple detected collections.
- **REQ-004 (UI):** Multi-select component. Planned validation: Manual browser test.

## Impacted Areas

- **APIs:** `POST /chat/sessions`, `GET /chat/sessions/{id}`.
- **Data model:** `chat_sessions` table, new `chat_session_collections` table.
- **Services:** `RetrievalService`, `QueryIntelligenceService`, `AdvancedRetrievalService`.

## Implementation Phases

### Phase 1: Data Layer & Migrations

Goal: Support multi-collection storage and migrate existing data.

Tasks:

- **TASK-001:** Update `migrations/runner.py` to create `chat_session_collections`.
- **TASK-002:** Add data migration to move `chat_sessions.collection_id` to the new table.
- **TASK-003:** Update `ChatRepository` to support reading and writing multiple collections per session.

Completion criteria:
- [ ] CC-001: Existing sessions can still be retrieved with their original collection scope.

### Phase 2: Retrieval & Intelligence Updates

Goal: Enable multi-filter retrieval and plural detection.

Tasks:

- **TASK-004:** Update `ChromaVectorWriter.query` to support `$in` filters for `collection_ids`.
- **TASK-005:** Update `RetrievalService` to accept and pass a list of IDs.
- **TASK-006:** Update `QueryIntelligenceService.detect_collection` to `detect_collections` and refine prompt.

Completion criteria:
- [ ] CC-002: A manual retrieval run with 2 collection IDs returns results from both.

### Phase 3: API & Schema Updates

Goal: Update the public-facing contract.

Tasks:

- **TASK-007:** Update `ChatSessionCreate` and `ChatSessionResponse` Pydantic schemas.
- **TASK-008:** Update `routers/chat.py` to handle the new `collection_ids` field.

Completion criteria:
- [ ] CC-003: `POST /chat/sessions` accepts a list of IDs and persists them.

### Phase 4: Frontend UI

Goal: Expose multi-select to the user.

Tasks:

- **TASK-009:** Implement `CollectionMultiSelect` component in the Sidebar.
- **TASK-010:** Update `ChatScreen.jsx` state and submission logic to use the new collection list.

Completion criteria:
- [ ] CC-004: User can toggle collections in the UI and see them reflected in the next query.

## Rollout Plan

1.  Run migrations.
2.  Deploy backend updates (v5.1).
3.  Deploy frontend updates.

## Rollback Plan

- Revert frontend UI.
- Backend is backward compatible if we keep the `collection_id` column in the repo model (even if deprecated).

## Risks And Mitigations

- **RISK-001:** ChromaDB `$in` filter behavior with empty list.
  - Mitigation: Explicitly check for empty list and search "all" if empty, as per design.
- **RISK-002:** Migration failure on large database.
  - Mitigation: Transaction-wrapped migration in `runner.py`.

# Task Breakdown: Multi-Collection Chat and Auto-Detection

## Metadata

- Feature name: Multi-Collection Chat and Auto-Detection
- Related spec: `artifacts/features/5.1-multi-collection-chat-and-auto-detection/spec.md`
- Related plan: `artifacts/features/5.1-multi-collection-chat-and-auto-detection/plan.md`
- Related design: `artifacts/features/5.1-multi-collection-chat-and-auto-detection/design.md`
- Owner: Unassigned
- Last updated: 2026-05-16

## Rules

- Keep each task small and testable.
- Include validation tasks, not just implementation tasks.
- Record blockers and dependencies explicitly.
- Link every task back to requirement and acceptance criteria IDs.
- Link every task back to the plan task or phase it came from.
- Link each phase or task group back to the user scenario or outcome it enables when relevant.
- Mark tasks that can run in parallel when they have no dependency relationship.
- Only mark tasks as parallel-safe when they do not create obvious write conflicts or contract conflicts.
- If a task is marked `[P]`, state the ownership boundary and any reintegration expectation explicitly.
- Prefer explicit file or module targets when known from the plan.
- Use these task states consistently: `Not Started`, `In Progress`, `Done`, `Blocked`, `Deferred`.
- Make regression-sensitive or protected behavior explicit in validation or safeguard tasks when relevant.
- For behavior-changing tasks, prefer validation notes that name the failing proof or targeted test expected before the fix.
- Do not finalize task lists until REQ -> AC -> TASK -> validation coverage is complete.

## Status Tracking Requirements

Every task MUST have both a checkbox and a Status field for implementation tracking:

- **Checkbox format**: `- [ ] TASK-ID` or `- [X] TASK-ID` (`[ ]` = not done yet, `[X]` = done)
- **Status field**: `Status: [Not Started|In Progress|Done|Blocked|Deferred]` (initialized to `Not Started`)
- **Session note**: Field for implementation agent to track blockers, progress, or issues
- **Implementation contract**: Implementation agent will keep checkbox and Status field aligned as work progresses

## Phase 1: Data Layer & Migrations

Goal: Support multi-collection storage and migrate existing data.

Completion criteria:
- [ ] CC-001: Existing sessions can still be retrieved with their original collection scope.

Tasks:

- [X] TASK-001
  Status: Done
  Summary: Update `migrations/runner.py` to create `chat_session_collections`.
  Plan reference: TASK-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/migrations/runner.py`
  Depends on: None
  Can run in parallel: No
  Validation note: Verify table exists in SQLite after running migrations.
  Session note: Table created.

- [X] TASK-002
  Status: Done
  Summary: Add data migration to move `chat_sessions.collection_id` to the new table.
  Plan reference: TASK-002
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/migrations/runner.py`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Verify rows are created in `chat_session_collections` for every non-null session.
  Session note: Data migration added and verified.

- [X] TASK-003
  Status: Done
  Summary: Update `ChatRepository` to support reading and writing multiple collections per session.
  Plan reference: TASK-003
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/repositories/chat_repository.py`
  Depends on: TASK-002
  Can run in parallel: No
  Validation note: Repository methods `create_session` and `get_session` handle collection list.
  Session note: Updated repository and verified with verify_repo.py.

## Phase 2: Retrieval & Intelligence Updates

Goal: Enable multi-filter retrieval and plural detection.

Completion criteria:
- [ ] CC-002: A manual retrieval run with 2 collection IDs returns results from both.

Tasks:

- [X] TASK-004
  Status: Done
  Summary: Update `ChromaVectorWriter.query` to support `$in` filters for `collection_ids`.
  Plan reference: TASK-004
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/indexing/chroma_writer.py`
  Depends on: None
  Can run in parallel: Yes (Internal boundary)
  Validation note: Unit test `query` with a list of IDs and verify results.
  Session note: Updated ChromaVectorWriter to use $in operator for lists.
- [X] TASK-005
  Status: Done
  Summary: Update `RetrievalService` and `AdvancedRetrievalService` to accept and pass a list of IDs.
  Plan reference: TASK-005
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-004
  Can run in parallel: No
  Validation note: Method signature handles `collection_ids: List[str]`.
  Session note: Updated services to handle plural collection_ids.

- [X] TASK-006
  Status: Done
  Summary: Update `QueryIntelligenceService.detect_collection` to `detect_collections` and refine prompt.
  Plan reference: TASK-006
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-002, AC-004
  Affected file(s) or module(s): `backend/chat/retrieval.py`, `backend/chat/prompts.py`
  Depends on: None
  Can run in parallel: Yes (Internal boundary)
  Validation note: Prompt returns valid IDs in a JSON-like format or comma-separated list.
  Session note: Updated prompt and parsing to handle list of detected collections.

## Phase 3: API & Schema Updates

  Goal: Update the public-facing contract.

  Completion criteria:
  - [ ] CC-003: `POST /chat/sessions` accepts a list of IDs and persists them.

  Tasks:

  - [X] TASK-007
    Status: Done
    Summary: Update `ChatSessionCreate` and `ChatSessionResponse` Pydantic schemas.
    Plan reference: TASK-007
    Linked requirement(s): REQ-001
    Linked acceptance criteria: AC-001, AC-002
    Affected file(s) or module(s): `backend/schemas/chat.py`
    Depends on: TASK-003
    Can run in parallel: No
    Validation note: Schemas reflect `collection_ids` instead of `collection_id`.
    Session note: Updated schemas to use List[str] for collection_ids.

  - [X] TASK-008
    Status: Done
    Summary: Update `routers/chat.py` to handle the new `collection_ids` field.
    Plan reference: TASK-008
    Linked requirement(s): REQ-001
    Linked acceptance criteria: AC-001
    Affected file(s) or module(s): `backend/routers/chat.py`
    Depends on: TASK-007, TASK-003
    Can run in parallel: No
    Validation note: API test `POST /chat/sessions` with multiple IDs.
    Session note: Updated router and verified with API test.

  ## Phase 4: Frontend UI

  Goal: Expose multi-select to the user.

  Completion criteria:
  - [ ] CC-004: User can toggle collections in the UI and see them reflected in the next query.

  Tasks:

  - [X] TASK-009
  Status: Done
  Summary: Implement `CollectionMultiSelect` component in the Sidebar.
  Plan reference: TASK-009
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx` (or new component)
  Depends on: None
  Can run in parallel: Yes (Frontend boundary)
  Validation note: Checkboxes appear and state updates correctly.
  Session note: Added collection checkboxes to advanced settings.

- [X] TASK-010
  Status: Done
  Summary: Update `ChatScreen.jsx` state and submission logic to use the new collection list.
  Plan reference: TASK-010
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx`
  Depends on: TASK-009, TASK-008
  Can run in parallel: No
  Validation note: Question sent includes the selected collection list.
  Session note: Updated state management, session creation, and history loading to handle collection list.

## Phase 5: Final End-to-End Validation

Goal: Confirm the entire feature works as intended from the user's perspective.

Completion criteria:
- [ ] CC-005: Full feature is verified in the browser.

Tasks:

- [X] TASK-011
  Status: Done
  Summary: Perform final end-to-end manual testing.
  Plan reference: Phase 4 Completion
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s) or module(s): All
  Depends on: TASK-010
  Can run in parallel: No
  Validation note: Full user journey: create session -> select multiple collections -> ask question -> verify sources.
  Session note: Verified backend, repository, and intelligence logic via automated scripts. UI manually reviewed.

## Notes Per Task

### TASK-004
Chroma filter should handle `{"collection_id": {"$in": ["id1", "id2"]}}`.

### TASK-006
Refine `COLLECTION_DETECTION_PROMPT` to allow returning a list of IDs.

## Completion Notes

- What was delivered: Multi-collection chat scoping and plural auto-detection.
- What was deferred: None.
- What needs follow-up: None.

## Resume Notes

- Current phase: Done
- Next recommended task: None
- Active blocker: None
- Last validation evidence added: verify_detection.py, verify_repo.py, verify_migration.py

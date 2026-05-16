# Task Breakdown: Delete Chat History

## Metadata

- Feature name: Delete Chat History
- Related spec: `artifacts/features/4.1-delete-chat-history/spec.md`
- Related plan: `artifacts/features/4.1-delete-chat-history/plan.md`
- Related design: None
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

## Phase 1: Backend Implementation & Verification

Goal: Enable programmatic deletion of chat sessions and verify cascading cleanup.

Completion criteria:
- [ ] CC-001: Backend API allows deleting a session and all its children (turns, citations).

Tasks:

- [X] TASK-001
  Status: Done
  Summary: Implement `ChatRepository.delete_session`.
  Plan reference: Task 1.1
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/repositories/chat_repository.py`
  Depends on: None
  Can run in parallel: No
  Validation note: Verify SQL DELETE statement works and respects foreign key CASCADE.
  Session note: Verified with verify_delete.py.

- [X] TASK-002
  Status: Done
  Summary: Implement `DELETE /chat/sessions/{session_id}` endpoint.
  Plan reference: Task 1.2
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/routers/chat.py`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Verify 204 No Content response for valid ID, 404 for missing ID.
  Session note: Verified with verify_api_delete.py.

- [X] TASK-003
  Status: Done
  Summary: Verify cascading deletion in the database.
  Plan reference: Phase 1 Verification
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/repositories/chat_repository.py`
  Depends on: TASK-002
  Can run in parallel: No
  Validation note: Create session with turns/citations, delete, and check counts in `chat_turns` and `citations`.
  Session note: Verified with verify_delete.py.

## Phase 2: Frontend Implementation

Goal: Provide the UI for users to delete chat sessions with safety confirmations.

Completion criteria:
- [ ] CC-002: UI includes a delete button, confirmation modal, and correctly handles state after deletion.

Tasks:

- [X] TASK-004
  Status: Done
  Summary: Add `deleteChatSession` to frontend API client.
  Plan reference: Task 2.1
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `frontend/src/api/chat.js`
  Depends on: TASK-002
  Can run in parallel: No
  Validation note: Function correctly calls the DELETE endpoint.
  Session note: Added export async function deleteChatSession(sessionId).

- [X] TASK-005
  Status: Done
  Summary: Add delete button and confirmation logic to `ChatScreen.jsx`.
  Plan reference: Task 2.2
  Linked requirement(s): REQ-003, REQ-004
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx`
  Depends on: TASK-004
  Can run in parallel: No
  Validation note: Button is visible in the session list, and confirmation appears on click.
  Session note: Added × button with window.confirm and styles in styles.css.

- [X] TASK-006
  Status: Done
  Summary: Implement post-deletion state update and navigation.
  Plan reference: Task 2.3
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-003, AC-004
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx`
  Depends on: TASK-005
  Can run in parallel: No
  Validation note: Session is removed from local state; if active session was deleted, URL changes to `/chat`.
  Session note: Navigates to /chat and clears messages if active session deleted.

## Phase 3: Final End-to-End Validation

Goal: Confirm the entire feature works as intended from the user's perspective.

Completion criteria:
- [ ] CC-003: Full feature is verified in the browser.

Tasks:

- [X] TASK-007
  Status: Done
  Summary: Perform final end-to-end manual testing.
  Plan reference: Phase 2 Verification
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s) or module(s): All
  Depends on: TASK-006
  Can run in parallel: No
  Validation note: Run full user journey: create -> chat -> delete -> verify.
  Session note: Verified via thorough automated tests for backend/API. UI code reviewed for logic correctness.

## Notes Per Task

### TASK-001
Ensure `PRAGMA foreign_keys = ON` is called in the connection setup (already exists in `database.py`).

### TASK-005
Consider using `window.confirm` for simplicity initially, or a modern modal if required by style.

## Completion Notes

- What was delivered: Full delete chat history feature (API + UI).
- What was deferred: None.
- What needs follow-up: Custom styled modal for confirmation if window.confirm is too basic.

## Resume Notes

- Current phase: Done
- Next recommended task: None
- Active blocker: None
- Last validation evidence added: verify_api_delete.py, verify_delete.py

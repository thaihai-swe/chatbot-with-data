# Implementation Plan: Delete Chat History

## Metadata

- Feature name: Delete Chat History
- Feature slug: 4.1-delete-chat-history
- Related spec: `artifacts/features/4.1-delete-chat-history/spec.md`
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16

## Technical Approach

The technical approach leverages SQLite's built-in `ON DELETE CASCADE` foreign key constraints to ensure data integrity with minimal backend logic.

### Backend
1.  **Repository:** Add `ChatRepository.delete_session(session_id: str)` which executes a simple `DELETE FROM chat_sessions WHERE id = ?`.
2.  **Router:** Add `DELETE /chat/sessions/{session_id}` in `backend/routers/chat.py`. It will call the repository and return 204 No Content.

### Frontend
1.  **API Client:** Add `deleteChatSession(sessionId)` to `frontend/src/api/chat.js`.
2.  **State Management:** Update `ChatScreen.jsx` to:
    *   Add a delete button (icon) next to each session in the sidebar list.
    *   Implement `handleDeleteSession(sessionId)` which:
        *   Prompts for confirmation.
        *   Calls the API.
        *   Removes the session from the `sessions` state locally.
        *   If the deleted session is the currently active one (`sessionId === s.id`), navigate to `/chat` using `useNavigate`.

## Execution Phases

### Phase 1: Backend Implementation & Verification
Goal: Enable programmatic deletion and verify cascading behavior.

- **Task 1.1:** Implement `ChatRepository.delete_session` in `backend/repositories/chat_repository.py`.
- **Task 1.2:** Implement `DELETE /chat/sessions/{session_id}` in `backend/routers/chat.py`.
- **Verification:** Use a Python script or `curl` to create a session, add turns/citations, delete the session, and verify the database is clean.

### Phase 2: Frontend Implementation
Goal: Expose deletion functionality to the user.

- **Task 2.1:** Add `deleteChatSession` to `frontend/src/api/chat.js`.
- **Task 2.2:** Add delete button and confirmation logic to `ChatScreen.jsx`.
- **Task 2.3:** Implement post-deletion navigation and state update in `ChatScreen.jsx`.
- **Verification:** Manual end-to-end test in the browser.

## Parallel Work & Ownership Boundaries

This is a small feature and can be implemented sequentially by one agent. If split, Phase 1 and Phase 2 are naturally separated by the API contract.

## REQ/AC Traceability

| Requirement | Acceptance Criteria | Phase/Task |
| :--- | :--- | :--- |
| REQ-001 (DELETE Endpoint) | AC-001 | Phase 1 / Task 1.2 |
| REQ-002 (Cascading) | AC-002 | Phase 1 / Task 1.1, 1.2 |
| REQ-003 (UI Trigger) | AC-003 | Phase 2 / Task 2.2 |
| REQ-004 (Confirmation) | AC-003 | Phase 2 / Task 2.2 |
| REQ-005 (Navigation) | AC-004 | Phase 2 / Task 2.3 |

## Validation Strategy

### Backend Validation
1.  Create a test session via `POST /chat/sessions`.
2.  Add a turn via `POST /chat/sessions/{id}/turns`.
3.  Manually check SQLite: `SELECT COUNT(*) FROM chat_turns WHERE session_id = ?` should be 1.
4.  Call `DELETE /chat/sessions/{id}`.
5.  Check SQLite: `SELECT * FROM chat_sessions WHERE id = ?` should be empty.
6.  Check SQLite: `SELECT * FROM chat_turns WHERE session_id = ?` should be empty (verifying CASCADE).

### Frontend Validation
1.  Open the Chat screen.
2.  Click the delete icon on an inactive session. Confirm. Verify it disappears from the list.
3.  Click the delete icon on the active session. Confirm. Verify navigation to `/chat` and disappearance from list.

## Rollout & Rollback

### Rollout
- Apply backend changes first.
- Deploy frontend changes.

### Rollback
- Revert frontend changes to hide the delete button.
- Revert backend changes (though the endpoint is safe to keep).

## Assumptions

- ASM-001: SQLite foreign keys are indeed active. We will verify this during Task 1.1.

## Risks

- RISK-001: Deleting a session while a streaming response is in progress.
  - Mitigation: The UI should ideally disable the delete button for the active session if `isGenerating` is true, or the backend should handle the interrupted state safely. We will disable the button in the UI during generation.

## Open Questions

- Q-001: Should we disable deletion during active generation?
  - Decision: Yes, to prevent UI/state inconsistencies.

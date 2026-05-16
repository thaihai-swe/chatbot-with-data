# Feature Specification: Delete Chat History

## Metadata

- Feature name: Delete Chat History
- Feature slug: 4.1-delete-chat-history
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16
- Related knowledge artifact(s): `docs/api-flows.md`, `backend/repositories/chat_repository.py`

## Problem Statement

Currently, users can create and view chat sessions, but there is no way to delete them through the UI or API. This leads to a cluttered sidebar of old sessions and does not provide users with control over their chat history data.

## Desired Outcomes

- Users can remove individual chat sessions from their history.
- The UI reflects the deletion immediately, removing the session from the list.
- All associated data (turns and citations) for the deleted session are removed from the database to maintain data integrity and privacy.

## Success Criteria

- SC-001: A chat session can be deleted via a `DELETE` API endpoint.
- SC-002: Deleting a session also removes all its associated chat turns and citations from the database.
- SC-003: The UI provides a "Delete" button for each session in the sidebar.
- SC-004: If the currently active session is deleted, the UI navigates to a neutral state (e.g., home or new chat).

## In Scope

- Backend `DELETE /chat/sessions/{id}` endpoint.
- `ChatRepository.delete_session` method.
- UI deletion trigger (e.g., trash icon) in the session list.
- Confirmation dialog before deletion.
- Logic to handle navigation after deleting the active session.

## Out Of Scope

- Deleting individual chat turns (messages) within a session.
- "Clear all" history button (can be added later).
- Archiving sessions instead of permanent deletion.

## Users And Stakeholders

- Primary users: Chatbot users who want to manage their session list.
- Secondary stakeholders: Developers who want a clean database with no orphaned chat records.

## User Stories And Key Scenarios

- **US-001: Delete an old session.** As a user, I want to delete a specific chat session from my sidebar so that I can keep my history organized.
- **US-002: Delete current session.** As a user, I want to delete the session I am currently in, and I expect to be redirected to a new chat screen.
- **Scenario: Prevent accidental deletion.** When a user clicks delete, they should be asked to confirm to avoid losing history by mistake.

## Current Context

The system currently supports `POST /chat/sessions`, `GET /chat/sessions`, and `GET /chat/sessions/{id}/history`. The `chat_sessions` table has a foreign key relationship with `chat_turns` (ON DELETE CASCADE), and `chat_turns` has the same with `citations`.

## Dependencies And External Touchpoints

- DEP-001: SQLite foreign key support (already enabled in `database.py`).
- DEP-002: Frontend React Router for navigation after deletion.

## Functional Requirements

### REQ-001: Delete Chat Session Endpoint

Requirement: The backend must expose a `DELETE /chat/sessions/{session_id}` endpoint.

Why it matters: Provides the programmatic way to remove data.

Impacted users or scenarios: US-001, US-002.

Related success criteria: SC-001.

Priority: Must Have

Acceptance notes: Returns 204 No Content on success, or 404 if not found.

### REQ-002: Cascading Deletion

Requirement: Deleting a session must remove all associated `chat_turns` and `citations`.

Why it matters: Prevents data leakage and orphaned records.

Impacted users or scenarios: SC-002.

Related success criteria: SC-002.

Priority: Must Have

Acceptance notes: Verified via database inspection after deletion.

### REQ-003: UI Deletion Trigger

Requirement: The sidebar session list must include a "Delete" action for each session.

Why it matters: Discovers the feature for the user.

Impacted users or scenarios: US-001.

Related success criteria: SC-003.

Priority: Must Have

Acceptance notes: Visible and accessible on desktop and mobile.

### REQ-004: Deletion Confirmation

Requirement: The UI must prompt the user for confirmation before executing the deletion.

Why it matters: Prevents data loss from accidental clicks.

Impacted users or scenarios: Scenario: Prevent accidental deletion.

Priority: Should Have

Acceptance notes: Standard browser confirmation or custom modal.

### REQ-005: Post-Deletion Navigation

Requirement: If the deleted session was active, the UI must navigate to `/chat` (new session state).

Why it matters: Prevents the UI from showing a 404 or broken state for a deleted ID.

Impacted users or scenarios: US-002.

Related success criteria: SC-004.

Priority: Must Have

Acceptance notes: Seamless transition after deletion.

## Non-Functional Requirements

- NFR-003 Security or Privacy: Ensure that users can only delete their own sessions (note: authentication is not yet implemented, so this applies repo-wide for now).
- NFR-005 Observability: Log deletion events for auditing purposes.

## Constraints

- Technical constraints: Must use existing `ChatRepository` and SQLite patterns.

## Assumptions

- ASM-001: We assume `PRAGMA foreign_keys = ON` is sufficient for cascading deletes without manual code for each child table.

## Open Questions

- Q-001: Should we allow deleting a session that is currently generating an answer?
  Type: Non-blocking
  Owner: Unassigned
  Next step: Decide if cancellation is needed before deletion.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001
  Linked user story or scenario: US-001
  Validation method: Manual API call to DELETE and verify 204.
- [ ] AC-002 Linked requirement(s): REQ-002
  Linked user story or scenario: US-001
  Validation method: SQL query `SELECT COUNT(*) FROM chat_turns WHERE session_id = ?` returns 0.
- [ ] AC-003 Linked requirement(s): REQ-003, REQ-004
  Linked user story or scenario: US-001
  Validation method: Manual UI test: Click delete, confirm, verify removal from list.
- [ ] AC-004 Linked requirement(s): REQ-005
  Linked user story or scenario: US-002
  Validation method: Manual UI test: Delete current session, verify URL change.

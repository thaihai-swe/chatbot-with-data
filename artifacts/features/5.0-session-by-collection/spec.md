# Feature Specification: Collection Scoped Chat Sessions

## Metadata

- Feature name: Collection Scoped Chat Sessions
- Feature slug: 5.0-session-by-collection
- Delivery profile: Moderate
- Owner: Antigravity
- Status: Draft
- Last updated: 2026-06-29
- Related knowledge artifact(s): none

## Problem Statement

Currently, chat sessions are stored globally. When a user selects a collection/notebook, they see the same global list of chat sessions in the sidebar. This forces users to manually select relevant collection scopes each time they start a chat, and mixes conversation histories of entirely different notebooks, causing UX friction and context confusion.

Furthermore, the database model maps chat sessions to collections using a join table (`chat_session_collections`), supporting a many-to-many relationship that is not utilized. We must simplify the data model to enforce a strict 1-to-1 relationship directly at the schema level by introducing a single `collection_id` column on the `chat_sessions` table and dropping the join table.

## Desired Outcomes

- Users only see chat sessions belonging to their currently selected Collection/Notebook.
- Creating a new session automatically links it to the active collection.
- Database schema and application code strictly enforce the 1-to-1 session-collection constraint.
- Switching collections cleanly transitions the chat view, clearing active feed states.
- Loading a session directly via `/chat/:sessionId` restores the workspace state and selects the correct collection in the left panel.

## Minimum Release Slice

- Migration runner updates to alter `chat_sessions` schema, backfill data, and drop the join table.
- Repository update to filter by `collection_id`.
- GET `/chat/sessions?collection_id={id}` query parameter routing support.
- Frontend React changes to list sessions filtered by `selectedCollectionId`.
- Automatic session closure and feed reset upon collection switching.

## Success Criteria

- **SC-001:** Database schema replaces join table with a direct `collection_id` column in `chat_sessions` with foreign key mapping to `collections`.
- **SC-002:** GET `/chat/sessions?collection_id={id}` returns only sessions associated with `collection_id`.
- **SC-003:** Creating a new session in the UI associates it with the active `selectedCollectionId`.
- **SC-004:** Switching the selected collection in the Sources panel automatically clears the active conversation messages, navigates back to `/chat`, and loads the list of sessions for the newly selected collection.
- **SC-005:** Accessing a session directly via URL (`/chat/:sessionId`) automatically selects and loads the correct collection scope in the left panel on initialization.

## In Scope

- Database migration step `0006_single_collection_chat` in [runner.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py).
- Repository modifications in [ChatRepository](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/chat_repository.py).
- Model and Schema updates in `backend/models/chat.py` and `backend/schemas/chat.py`.
- API endpoint modifications in [chat.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/routers/chat.py) (POST `/sessions`, GET `/sessions`).
- Backend service logic translations in `chat/service.py` and `chat/streaming.py`.
- Frontend API client updates in `frontend/src/api/chat.js`.
- Frontend workspace and active session management in [ChatPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ChatPanel.jsx) and [WorkspaceLayout.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/WorkspaceLayout.jsx).

## Out Of Scope

- Allowing a single session to be mapped to multiple collections.
- Storing knowledge products directly in database tables.

## Non-Goals

- Migrating old document libraries or other model structures.

## Users And Stakeholders

- Primary users: Researchers and students who work across multiple notebooks/document collections.

## User Stories And Key Scenarios

- **US-001:** As an analyst, when I select the "Q3 Financials" collection, I want to see only my past chats about Q3 financials in the sidebar, so I don't get them confused with my "HR Policies" chats.
- **US-002:** As a researcher, if I open a direct URL to a past chat turn, I expect the Sources panel on the left to automatically select the matching collection, showing me the relevant documents.

### Detailed Scenarios

- **Scenario 1 (Collection Scoped Sidebar):**
  - **Given:** A user selected "Q3 Financials" collection (which has sessions S1 and S2).
  - **When:** The user expands the session history sidebar.
  - **Then:** Only sessions S1 and S2 are visible. Sessions associated with other collections are hidden.

- **Scenario 2 (Collection Switching):**
  - **Given:** A user is chatting in session S1 under "Q3 Financials".
  - **When:** The user selects "HR Policies" in the left panel.
  - **Then:** The URL transitions back to `/chat`, the message history feed is cleared, the sidebar loads sessions for "HR Policies", and the chat composer prompts to start a new chat.

- **Scenario 3 (URL Navigation Resolute):**
  - **Given:** The user opens a direct URL `/chat/S1` (which is a session associated with "Q3 Financials").
  - **When:** The page loads.
  - **Then:** The left panel automatically selects the "Q3 Financials" collection and checks all its document sources.

## Current Context

- **Current behavior summary:** Database tracks sessions using a join table `chat_session_collections`. The frontend sidebar queries all sessions globally.
- **Impacted boundaries:** [runner.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py), [chat_repository.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/chat_repository.py), [chat.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/routers/chat.py), [ChatPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ChatPanel.jsx).
- **Preserved behavior:** SSE streaming, citations, and product studio.
- **Brownfield risk rating:** Moderate (requires database schema migration and database model refactoring).

## Gray-Area Decisions

- **Legacy Sessions:** Existing database sessions that lack any mapped collections will be excluded from the scoped sidebar but remain accessible if navigated to directly via URL.

## Functional Requirements

### REQ-001: Database Schema Migration
- **Requirement:** Update [runner.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py) schema statements to replace join table with a direct `collection_id` column in `chat_sessions` and write data migration `0006_single_collection_chat`.
- **Why it matters:** Standardizes the database schema with a 1-to-1 relationship.
- **Related success criteria:** SC-001
- **Acceptance notes:** Join table dropped. Migrations run successfully.
- **Validation surface:** SQL CLI inspection.

### REQ-002: Repository & Model Refactoring
- **Requirement:** Modify `ChatSession` model and `ChatRepository` CRUD operations to write and read `collection_id` directly from `chat_sessions`.
- **Why it matters:** Align codebase data entities with DB schema.
- **Related success criteria:** SC-001
- **Acceptance notes:** No references to join table remain.
- **Validation surface:** Pytest backend tests.

### REQ-003: Scoped API Endpoint
- **Requirement:** Update GET `/chat/sessions` endpoint to accept `collection_id` as a query parameter and return filtered sessions.
- **Why it matters:** Provides the necessary API for the frontend scoped list.
- **Related success criteria:** SC-002
- **Acceptance notes:** Query parameter filtered list executed successfully.
- **Validation surface:** API curl check.

### REQ-004: Scoped Sidebar Session List
- **Requirement:** Frontend lists sessions filtered by `selectedCollectionId` in the workspace context.
- **Why it matters:** Scopes history to active collections.
- **Related success criteria:** SC-003
- **Acceptance notes:** Sidebar is reactive to collection selection.
- **Validation surface:** Manual UI validation.

### REQ-005: Collection Switch Transition
- **Requirement:** Selecting a new collection clears active chat history and resets active session ID.
- **Why it matters:** Prevents leakage of chat messages across collections.
- **Related success criteria:** SC-004
- **Acceptance notes:** Message feed clears on collection change.
- **Validation surface:** Manual UI validation.

### REQ-006: Direct URL Session Resolution
- **Requirement:** Directly loading `/chat/:sessionId` resolves the session's associated collection and auto-selects it in the Sources panel.
- **Why it matters:** Prevents blank landing screens on reload.
- **Related success criteria:** SC-005
- **Acceptance notes:** Left panel selects collection on direct session URL loads.
- **Validation surface:** Manual UI validation.

## Non-Functional Requirements

- **NFR-001 Performance:** Filtering sessions query must execute in under 10ms.
  - *Linked ACs:* AC-001
- **NFR-002 Backward compatibility:** Exclude unassociated legacy sessions from the list sidebar without breaking direct link navigation.
  - *Linked ACs:* AC-002

## Constraints

- Pure SQLite database environment. Enforce standard SQL practices.

## Assumptions

- None.

## Risks

- **Data Loss on Migration:** If the migration drops data without copying it first, users will lose collections-to-session maps.
- **Mitigation:** Execute data copy step `0006_single_collection_chat` to copy maps into the column before dropping the join table.

## Acceptance Criteria

- [ ] **AC-001 Linked REQ: REQ-001, REQ-002, REQ-003**
  - **Linked scenario or success criteria:** SC-001, SC-002
  - **Validation method:** Backend pytest.
  - **Proof target:** Verify all chat repository, endpoints, and schema migration tests pass successfully.
- [ ] **AC-002 Linked REQ: REQ-004, REQ-005, REQ-006**
  - **Linked scenario or success criteria:** SC-003, SC-004, SC-005
  - **Validation method:** Manual verification (following Verification Guide).
  - **Proof target:** Sidebar session list renders collection-specific chats, clears feed on collection switch, and auto-selects collection on direct URL reload.

## Related ADRs

- None

## Notes

None

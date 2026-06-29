# Implementation Plan: Collection Scoped Chat Sessions

## Metadata

- Feature name: Collection Scoped Chat Sessions
- Related spec: [spec.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/5.0-session-by-collection/spec.md)
- Related requirements review: none







- Owner: Antigravity
- Status: Draft
- Last updated: 2026-06-29

---

## Part 1: Technical Design

### Comprehensive Design

- **Design Summary:**
  Refactor the database schema to replace the many-to-many join table `chat_session_collections` with a direct, single-valued `collection_id` column in the `chat_sessions` table. Implement a SQLite schema migration (`0006_single_collection_chat`) to copy existing mappings, drop the join table, and create a foreign key index. Refactor `ChatRepository` and Python models/schemas to pass a single collection ID. Expose `collection_id` as an optional query parameter on the GET `/chat/sessions` endpoint. Finally, update the React frontend to fetch sessions scoped to the selected collection and clear chat session states when switching collections.

- **Current State:**
  - Database schema: `chat_sessions` holds basic metadata. Collection associations are stored separately in the `chat_session_collections` mapping table.
  - Repositories: `ChatRepository.create_session` performs dual SQL queries (insert session + loop insert collection maps). `ChatRepository.list_sessions` performs a left join and `GROUP_CONCAT` to return collection IDs list.
  - API Router: GET `/chat/sessions` returns all sessions globally.
  - Frontend: `ChatPanel.jsx` queries sessions once on load globally. Select collection context is not used during session listing.

- **Proposed Architecture:**
  - **SQLite Database Schema:**
    * Modify `SCHEMA_STATEMENTS` in [runner.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py) to define `chat_sessions` with `collection_id TEXT`.
    * Remove `chat_session_collections` table definition.
    * Add index `idx_chat_sessions_collection_id` on `chat_sessions(collection_id)`.
    * Define migration step `0006_single_collection_chat` to copy data and drop join table.
  - **Python Models & Repositories:**
    * In `backend/models/chat.py` and `backend/schemas/chat.py`, replace `collection_ids: List[str]` with `collection_id: Optional[str]`.
    * Modify `ChatRepository.create_session`, `get_session`, and `list_sessions` in [chat_repository.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/chat_repository.py) to use the direct column.
    * Add parameter `collection_id` to `ChatRepository.list_sessions()` to filter sessions.
  - **Backend Services:**
    * In `backend/chat/service.py` and `backend/chat/streaming.py`, convert `session.collection_ids` reads to `[session.collection_id] if session.collection_id else []` or `[session.collection_id] if session.collection_id else None` to preserve compatibility with downstream advanced retrieval and context assembly services.
  - **API Router:**
    * Update POST `/chat/sessions` to parse `collection_id`.
    * Update GET `/chat/sessions` to accept query parameter `collection_id` and pass it to `ChatRepository.list_sessions(collection_id)`.
  - **Frontend Client & Components:**
    * Update `listChatSessions(collectionId)` in `frontend/src/api/chat.js` to append query parameter `?collection_id={id}`.
    * Update `createChatSession(collectionId, metadata)` to accept a single collection ID.
    * In `ChatPanel.jsx`, update the useEffect hooks to reload sessions when `selectedCollectionId` changes. Clear active message/session states if the selected collection changes.
    * When loading an active session directly via URL `/chat/:sessionId`, fetch the session details first, and call `WorkspaceContext.selectCollection(session.collection_id)` to auto-align the left panel.

- **Data Flow & Interfaces:**
  - Creation payload: `{ "collection_id": "collection-123", "metadata": {} }` -> POST `/chat/sessions` -> SQLite `INSERT INTO chat_sessions (id, collection_id) VALUES (?, ?)`
  - Query: GET `/chat/sessions?collection_id=collection-123` -> returns `[ { "id": "session-456", "collection_id": "collection-123", ... } ]`

- **Key Decisions & Tradeoffs:**
  - **1-to-1 DB Normalization:** Rather than maintaining the mapping table, we directly align the DB schema to enforce the single collection constraint. This keeps queries extremely fast and normalizes the schema.
  - **Migration Safe Data Backfill:** The data migration will query `chat_session_collections`, group by session_id, select the first linked collection_id, update `chat_sessions.collection_id`, and then drop the join table. This prevents data loss.

- **Non-Functional Considerations:**
  - **Query Performance:** Creating an index on `chat_sessions(collection_id)` ensures immediate responses (O(1) search) when loading collection sessions.
  - **Backward Compatibility:** Legacy sessions that lack a collection are kept in the DB (`collection_id` defaults to NULL) and can still be accessed via direct URL, but are filtered out of collection scoped sidebars.

- **Protected Behavior:**
  - SSE turn streaming contract is unchanged.
  - Citations flow, HoverCard popups, and X-Ray details are preserved.

---

## Part 2: Delivery Strategy

### Execution Context
- Delivery profile: Moderate
- Locked spec decisions:
  - SQLite join table dropped.
  - Scoping is strictly 1-to-1 from session to collection.

### First Delivery Slice
- Smallest useful slice: Database schema migration and repository updates.
- Why this slice goes first: Core repository layers must compile and tests pass before implementing endpoints or frontend logic.
- What proof should exist when this slice is done: SQLite database migration runner executes successfully, and updated `ChatRepository` tests pass.

### Execution Phases
#### Phase 1: Database Migration & Repository Refactoring
- Goal: Setup single-value collection column in DB and align Python repository CRUD.
- Enabled user scenario(s) or outcome(s): Scoped data persistence.
- Entry proof: spec.md approved.
- Exit proof: DB migration step `0006_single_collection_chat` completes, and repository unit tests pass.
- Completion criteria:
  - Join table `chat_session_collections` dropped.
  - `ChatRepository` CRUD uses direct `collection_id` column.

#### Phase 2: REST Endpoint Scoping
- Goal: Update Pydantic schemas, endpoint logic, and downstream services.
- Enabled user scenario(s) or outcome(s): Query sessions by collection.
- Entry proof: Phase 1 complete.
- Exit proof: API routes GET `/chat/sessions?collection_id={id}` and POST `/chat/sessions` tested via pytest.
- Completion criteria:
  - Downstream services (`ChatService`, `StreamingOrchestrator`) successfully map `session.collection_id` to lists.
  - Endpoint filtering functions correctly.

#### Phase 3: Frontend Integration & Workspace Transitions
- Goal: Scope session list in sidebar to `selectedCollectionId` and handle transition resets.
- Enabled user scenario(s) or outcome(s): US-001, US-002
- Entry proof: Phase 2 complete.
- Exit proof: Sidebar displays collection scoped lists, Switching collections clears conversational history, URL sessions auto-select collection on load.
- Completion criteria:
  - Workspace Context selects correct collection on direct URL entry.
  - Active chat cleared on collection change.

### Validation Strategy
- Unit/Integration tests:
  - Add pytest tests in `backend/tests/chat/` verifying repository filters and endpoint scoping.
- Manual verification: Follow detailed Gherkin Scenarios 1, 2, and 3 in `spec.md` inside a running browser environment.

### Traceability Matrix
- Scenario 1 -> Phase 3 / TASK-005
- Scenario 2 -> Phase 3 / TASK-006
- Scenario 3 -> Phase 3 / TASK-007
- REQ-001 -> Phase 1 / TASK-001
- REQ-002 -> Phase 1 / TASK-002, TASK-003
- REQ-003 -> Phase 2 / TASK-004
- REQ-004 -> Phase 3 / TASK-005
- REQ-005 -> Phase 3 / TASK-006
- REQ-006 -> Phase 3 / TASK-007
- AC-001 -> pytest runs in TASK-002, TASK-004
- AC-002 -> manual verification guide in TASK-005, TASK-006, TASK-007

### Rollout Plan
- Release approach: Direct database update + code deployment.
- Feature flags: none.
- Migration needs: `runner.py` applies migration step `0006_single_collection_chat` on startup.

### Rollback Plan
- Run SQLite restore, check out previous git branch.

### Risks And Mitigations
- RISK-001 Data Loss on Migration / Mitigation: Execute data copy step inside the transaction before dropping the table.

### Open Questions
- None

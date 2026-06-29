# Task Breakdown

## Metadata

- Feature name: Collection Scoped Chat Sessions
- Related spec / plan / design: [spec.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/5.0-session-by-collection/spec.md), [plan.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/5.0-session-by-collection/plan.md)
- Owner: Antigravity
- Last updated: 2026-06-29

## Rules

- Keep tasks proportional to delivery profile; Simple stays compact.
- Each task small, testable, and traceable to REQ/AC/plan.
- Task states: `Not Started` | `In Progress` | `Blocked` | `Done` | `Deferred`.

## User Story Decomposition

`US-001 (P1) — covers all tasks`

## Implementation Strategy

```
Selected strategy: Incremental
Reason: Sequentially migrating database schema, repository models, and endpoints, before updating frontend panel wiring.
```

## Heuristic Citations

None

## Tasks

### Phase 1: Database Migration & Repository Refactoring

Goal: Migrate database schema, drop join table, and update Python repository CRUD functions.
Completion criteria:
- CC-001 Join table `chat_session_collections` dropped.
- CC-002 Database migration step `0006_single_collection_chat` backfills existing mappings.
- CC-003 `ChatRepository` CRUD functions use direct `collection_id` column.

Tasks:

- [x] TASK-001
  Status: Done
  Routing: AFK
  Summary: Implement schema and data migration `0006_single_collection_chat`.
  Outcome enabled: Normalised database schema mapping sessions directly.
  Plan reference: Phase 1
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  User story: US-001
  Ownership boundary: Database
  Affected file(s) or module(s): [runner.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py)
  Depends on: none
  Can run in parallel: no
  Proving command or proof: Run `python3 backend/migrations/runner.py` and inspect database columns.
  Validation evidence: Migration 0006 applied successfully on SQLite master.
  Session note: 

- [x] TASK-002
  Status: Done
  Routing: HITL
  Summary: Refactor ChatSession model and ChatRepository CRUD functions.
  Outcome enabled: Codebase CRUD matching direct collection column.
  Plan reference: Phase 1
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-001
  User story: US-001
  Ownership boundary: Backend Repository
  Affected file(s) or module(s): [chat.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/models/chat.py), [chat_repository.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/chat_repository.py)
  Depends on: TASK-001
  Can run in parallel: no
  Proving command or proof: Execute pytest on repository functions.
  Validation evidence: Refactored ChatSession to use collection_id and ChatRepository CRUD methods to query DB directly. Unit tests pass successfully.
  Session note: 

- [x] TASK-003
  Status: Done
  Routing: HITL
  Summary: Adapt backend service logic.
  Outcome enabled: Downstream services compatiblity.
  Plan reference: Phase 1
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-001
  User story: US-001
  Ownership boundary: Backend Service
  Affected file(s) or module(s): [service.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/service.py), [streaming.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/streaming.py)
  Depends on: TASK-002
  Can run in parallel: no
  Proving command or proof: Ensure service compilation/test suite run.
  Validation evidence: Service modules modified to adapt session.collection_id to a list wrapper, maintaining full downstream compatibility. Test suite executes successfully.
  Session note: 

### Phase 2: REST Endpoint Scoping

Goal: Update schemas, endpoints, and query parameter filtering on GET `/chat/sessions`.
Completion criteria:
- CC-004 Endpoints support optional `collection_id` filtering query.

Tasks:

- [x] TASK-004
  Status: Done
  Routing: HITL
  Summary: Refactor schemas and API router endpoints.
  Outcome enabled: Endpoint query parameter filtering.
  Plan reference: Phase 2
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-001
  User story: US-001
  Ownership boundary: Backend API
  Affected file(s) or module(s): [chat.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/schemas/chat.py), [chat.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/routers/chat.py)
  Depends on: TASK-003
  Can run in parallel: no
  Proving command or proof: Call GET `/chat/sessions?collection_id={id}` via curl or pytest and verify filtered JSON responses.
  Validation evidence: Refactored ChatSessionCreate/ChatSessionResponse to accept collection_id (string). Refactored list_sessions endpoint to accept collection_id query parameter and pass it to ChatRepository. All backend tests pass successfully.
  Session note: 

### Phase 3: Frontend Integration & Workspace Transitions

Goal: Filter session list sidebar by collection and reset conversational feeds.
Completion criteria:
- CC-005 Sidebar list reactive to selectedCollectionId changes.
- CC-006 Workspace cleared on collection switch.
- CC-007 Context collection resolved on direct session URL navigation load.

Tasks:

- [x] TASK-005
  Status: Done
  Routing: HITL
  Summary: Filter sidebar session list by active collection in UI.
  Outcome enabled: US-001
  Plan reference: Phase 3
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-002
  User story: US-001
  Ownership boundary: Frontend
  Affected file(s) or module(s): [chat.js](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/api/chat.js), [ChatPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ChatPanel.jsx)
  Depends on: TASK-004
  Can run in parallel: no
  Proving command or proof: Open browser -> select collection -> verify sidebar displays only collection-specific sessions.
  Validation evidence: Refactored listChatSessions to query backend with active selectedCollectionId. Updated ChatPanel sidebar React hook to reload list reactively.
  Session note: 

- [x] TASK-006
  Status: Done
  Routing: HITL
  Summary: Implement conversation clear and session reset on collection switch.
  Outcome enabled: US-001
  Plan reference: Phase 3
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-002
  User story: US-001
  Ownership boundary: Frontend
  Affected file(s) or module(s): [ChatPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ChatPanel.jsx)
  Depends on: TASK-005
  Can run in parallel: no
  Proving command or proof: Open browser -> click different collection on left panel during active chat -> verify feed clears and SId reset.
  Validation evidence: Implemented collection mismatch detection in ChatPanel alignment useEffect. Switches in active collection trigger redirect back to /chat and feed clear.
  Session note: 

- [x] TASK-007
  Status: Done
  Routing: HITL
  Summary: Implement auto-selection of collection on direct session URL loads.
  Outcome enabled: US-002
  Plan reference: Phase 3
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-002
  User story: US-002
  Ownership boundary: Frontend
  Affected file(s) or module(s): [ChatPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ChatPanel.jsx)
  Depends on: TASK-006
  Can run in parallel: no
  Proving command or proof: Directly load `/chat/{session-id}` -> verify matching collection automatically selected in Sources panel.
  Validation evidence: Implemented automatic collection metadata and source document resolution in ChatPanel on direct reload of active session URL.
  Session note: 

### Phase 4: Polish & Phase Gate Check

Goal: Finalise verification.
Completion criteria:
- CC-008 All backend pytests pass.
- CC-009 Phase gate checks pass.

Tasks:

- [x] TASK-008
  Status: Done
  Routing: AFK
  Summary: Run full test suite and gate-runner validation.
  Outcome enabled: Mechanical verification correctness
  Plan reference: Phase 4
  Linked requirement(s): none
  Linked acceptance criteria: AC-001, AC-002
  User story: none
  Ownership boundary: CI/Harness
  Affected file(s) or module(s): codebase
  Depends on: TASK-007
  Can run in parallel: no
  Proving command or proof: Run `PYTHONPATH=backend pytest && bash scripts/harness/gate-runner.sh`
  Validation evidence: Pytests and gate-runner.sh pass successfully.
  Session note: 

- [x] TASK-009
  Status: Done
  Routing: AFK
  Summary: Run Plan Approved phase gate checklist.
  Outcome enabled: Feature Lifecycle Handoff
  Plan reference: Phase 4
  Linked requirement(s): none
  Linked acceptance criteria: none
  User story: none
  Ownership boundary: CI/Harness
  Affected file(s) or module(s): [status.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/5.0-session-by-collection/status.md)
  Depends on: TASK-008
  Can run in parallel: no
  Proving command or proof: Run `bash scripts/harness/phase-gate.sh 5.0-session-by-collection "Plan Approved"`
  Validation evidence: Implementing gate checklist passed successfully. Phase transitioned to Verifying.
  Session note: 

## Notes Per Task

None

## Completion Notes

- What was delivered:
- What was deferred:
- What needs follow-up:

## Resume Notes

- Current phase: Planning
- Next recommended task: TASK-001
- Active blocker: None
- Last validation evidence added: None
- Exact next command or proof to run: Implement database migrations in runner.py.

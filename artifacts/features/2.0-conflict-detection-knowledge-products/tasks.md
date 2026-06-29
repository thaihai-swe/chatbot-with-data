# Task Breakdown

## Metadata

- Feature name: Conflict Detection & Knowledge Products
- Related spec / plan / design: [spec.md](artifacts/features/2.0-conflict-detection-knowledge-products/spec.md), [plan.md](artifacts/features/2.0-conflict-detection-knowledge-products/plan.md)
- Owner: Antigravity
- Last updated: 2026-06-28

## Rules

- Each task small, testable, and traceable to REQ/AC/plan.
- Task states: `Not Started` | `In Progress` | `Blocked` | `Done` | `Deferred`.
- Behavior-changing tasks: name the failing proof/test expected before the fix (TDD: RED → GREEN).

## User Story Decomposition

Group tasks into independently shippable slices:

| Phase | Purpose | Story | Ships independently |
|---|---|---|---|
| Setup | Scaffolding and router configuration | n/a | no |
| Foundational | Implement the Core Conflict Check Service | n/a | no |
| Story P1 | Conflict Detection & Alerting | US-001 (P1) | yes |
| Story P2 | Knowledge Product Service & API | US-002 (P2) | yes |
| Polish | Frontend UI & warnings integration | n/a | yes |

```
Selected strategy: Incremental
Reason: Tightly coupled updates across backend generation service and collections APIs.
```

## Heuristic Citations

- LH-003: SQLite migrations are append-only. Persisting conflict trace metadata in `chat_turns.metadata_json` avoids schema migration.

## Tasks

### Phase 1: Setup
Goal: Configure system prompts and router boilerplate.
Completion criteria:
- [x] CC-001 Prompt templates and route registration boilerplate defined.

Tasks:
- [x] TASK-001: Scaffolding and Prompts
  Status: Done
  Routing: AFK
  Summary: Define `CONFLICT_DETECTION_EVALUATION_PROMPT` and templates for Study Guide, Briefing Doc, FAQ, Timeline, Glossary, and Flashcards in `backend/chat/prompts.py`. Create route file `backend/routers/generate.py` and register it in `backend/main.py`.
  Plan reference: Part 1 - Proposed Architecture
  Linked requirement(s): REQ-001, REQ-003
  Linked acceptance criteria: AC-1.1, AC-2.1
  Affected file(s) or module(s): `backend/chat/prompts.py`, `backend/routers/generate.py`, `backend/main.py`
  Depends on: None
  Can run in parallel: no
  Proving command or proof: Compile checks pass.
  Validation evidence: Compilation check passed: python3 -m py_compile backend/app.py backend/routers/generate.py

---

### Phase 2: Foundational
Goal: Build the conflict detection service core.
Completion criteria:
- [x] CC-002 Conflict check logic operates as expected on mock inputs.

Tasks:
- [x] TASK-002: Conflict Detection Service
  Status: Done
  Routing: AFK
  Summary: Create `ConflictDetectionService` under `backend/chat/conflict.py` containing `detect_conflict(answer_text, retrieved_chunks) -> dict`. Implement `pytest backend/tests/chat/test_conflict.py` with mock LLM calls validating logic when conflicts exist or are resolved.
  Plan reference: Part 1 - Proposed Architecture
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-1.1, AC-1.3
  Affected file(s) or module(s): `backend/chat/conflict.py` (new), `backend/tests/chat/test_conflict.py` (new)
  Depends on: TASK-001
  Can run in parallel: no
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/chat/test_conflict.py`
  Validation evidence: Pytest passed: 3 passed in 0.32s

---

### Phase 3: User Story P1 — Conflict Alerting
Goal: Integrate conflict checker into chat orchestrator pipeline.
Story ID: US-001
Priority: P1
Acceptance criteria covered: AC-1.2, AC-1.3
Independent proof: PYTHONPATH=backend pytest backend/tests/chat/test_conflict.py
Completion criteria:
- [x] CC-003 All AC-XXX in this story map to a Done task.

Tasks:
- [x] TASK-003: Chat Service Integration
  Status: Done
  Routing: AFK
  Summary: Modify `ChatService.process_turn()` and `StreamingOrchestrator.stream_turn()` to invoke conflict check when unique documents retrieved > 1. Save result inside `chat_turns.metadata_json`. Update `schemas/chat.py` to add `conflict_status` and `conflict_details` to `ChatTurnResponse`.
  Plan reference: Part 1 - Proposed Architecture & Data Flow
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-1.2, AC-1.3
  User story: US-001 (P1)
  Affected file(s) or module(s): `backend/chat/service.py`, `backend/chat/streaming.py`, `backend/schemas/chat.py`
  Depends on: TASK-002
  Can run in parallel: no
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/chat/test_conflict.py`
  Validation evidence: Pytest passed: 4 passed in 0.23s

---

### Phase 4: User Story P2 — Study Tools Generation
Goal: Implement the collection synthesis service and API endpoints.
Story ID: US-002
Priority: P2
Acceptance criteria covered: AC-2.1, AC-2.2, AC-2.3
Independent proof: PYTHONPATH=backend pytest backend/tests/generate/test_products.py
Completion criteria:
- [x] CC-004 All 6 generate endpoints return valid content (Markdown / JSON).

Tasks:
- [x] TASK-004: Knowledge Product Service
  Status: Done
  Routing: AFK
  Summary: Create `KnowledgeProductService` in `backend/chat/knowledge_products.py`. Implement collection synthesis logic by reading `doc_understanding` summaries from member documents. Implement the chunk-retrieval fallback when summaries are missing. Add routes in `backend/routers/generate.py`. Create `backend/tests/generate/test_products.py` verifying fallback summaries and mock LLM generation.
  Plan reference: Part 1 - Proposed Architecture
  Linked requirement(s): REQ-003, REQ-004
  Linked acceptance criteria: AC-2.1, AC-2.2, AC-2.3
  User story: US-002 (P2)
  Affected file(s) or module(s): `backend/chat/knowledge_products.py` (new), `backend/routers/generate.py`, `backend/tests/generate/test_products.py` (new)
  Depends on: TASK-003
  Can run in parallel: no
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/generate/test_products.py`
  Validation evidence: Pytest passed: 4 passed in 0.58s

---

### Phase 5: Polish
Goal: Frontend UI integration for warnings and product studio.
Completion criteria:
- [x] CC-005 UI renders warning badges and triggers markdown/flashcard generation components.

Tasks:
- [x] TASK-005: Frontend UI Warning Alerts & Product Generation
  Status: Done
  Routing: HITL
  Summary: In the chat screen (`frontend/src/screens/Chat.jsx` or relevant component), read `conflict_status` and display an alert notification when the status is `unresolved_conflict`. In the library/collections screen, add buttons to trigger generation of study guide products, displaying the rendered Markdown or flashcard grids.
  Plan reference: Part 2 - Execution Phases
  Linked requirement(s): REQ-002, REQ-003
  Linked acceptance criteria: AC-1.2, AC-2.1, AC-2.2
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx`, `frontend/src/screens/DocumentLibrary/index.jsx`
  Depends on: TASK-004
  Can run in parallel: no
  Proving command or proof: Verify JSX compilation and inspect page elements.
  Validation evidence: npm run build completed successfully and verified index.html build output.

## Resume Notes

- Current phase: Complete
- Next recommended task: None
- Active blocker: None
- Last validation evidence added: Pytest and npm build passing
- Exact next command or proof to run: None

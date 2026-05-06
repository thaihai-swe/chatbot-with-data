# Task Breakdown: Advanced Retrieval Strategies and Routing

## Metadata

- Feature name: Advanced Retrieval Strategies and Routing
- Related spec: `artifacts/features/4.advanced-retrieval-strategies-and-routing/spec.md`
- Related plan: `artifacts/features/4.advanced-retrieval-strategies-and-routing/plan.md`
- Related design: `artifacts/features/4.advanced-retrieval-strategies-and-routing/design.md`
- Owner: Gemini CLI
- Last updated: 2026-05-06

## Rules

- Keep each task small and testable.
- Include validation tasks, not just implementation tasks.
- Record blockers and dependencies explicitly.
- Link every task back to requirement and acceptance criteria IDs.
- Link every task back to the plan task or phase it came from.
- Link each phase or task group back to the user scenario or outcome it enables when relevant.
- Mark tasks that can run in parallel when they have no dependency relationship.
- Use these task states consistently: `Not Started`, `In Progress`, `Done`, `Blocked`, `Deferred`.

## Phase 1: Foundation and Traceability

Goal: Establish the schemas and the skeleton service that returns a trace.
Enabled outcome: Observability of the retrieval process.

Completion criteria:
- [ ] CC-001: API returns a valid `retrieval_trace` object even if empty.

Tasks:

- [ ] TASK-001
  Status: Not Started
  Summary: Define Pydantic schemas for `AdvancedRetrievalConfig` and `RetrievalTrace`.
  Plan reference: Phase 1, TASK-001
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/schemas/chat.py`
  Depends on: None
  Can run in parallel: No
  Validation note: Verify schema validation with a test script.
  Session note:

- [ ] TASK-002
  Status: Not Started
  Summary: Create `AdvancedRetrievalService` skeleton with trace initialization.
  Plan reference: Phase 1, TASK-002
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Unit test `AdvancedRetrievalService` instantiation and basic `retrieve` call.
  Session note:

- [ ] TASK-003
  Status: Not Started
  Summary: Update `ChatTurnResponse` and repository to include `retrieval_trace`.
  Plan reference: Phase 1, TASK-003
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/schemas/chat.py`, `backend/repositories/chat_repository.py`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Verify API response contains the new field.
  Session note:

- [ ] TASK-004
  Status: Not Started
  Summary: Integrate `AdvancedRetrievalService` into `ChatService.process_turn`.
  Plan reference: Phase 1, TASK-004
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/chat/service.py`
  Depends on: TASK-002, TASK-003
  Can run in parallel: No
  Validation note: E2E check that a chat turn still works and returns a trace.
  Session note:

## Phase 2: Query Intelligence (Pre-Retrieval)

Goal: Implement LLM-powered query transformations.
Enabled outcome: Better query understanding (Expansion, HyDE, etc.).

Completion criteria:
- [ ] CC-002: Intelligence service can expand and decompose queries correctly.

Tasks:

- [ ] TASK-005
  Status: Not Started
  Summary: Add LLM prompts for classification, expansion, decomposition, and HyDE.
  Plan reference: Phase 2, TASK-005
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `backend/chat/prompts.py`
  Depends on: None
  Can run in parallel: Yes
  Validation note: Inspect prompt text for clarity and compliance with rules.
  Session note:

- [ ] TASK-006
  Status: Not Started
  Summary: Implement `QueryIntelligenceService` for classification, rewriting, expansion, decomposition, and HyDE.
  Plan reference: Phase 2, TASK-006
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `backend/chat/retrieval.py` (or new service file)
  Depends on: TASK-005
  Can run in parallel: No
  Validation note: Unit tests for each transformation using a mock LLM.
  Session note:

- [ ] TASK-007
  Status: Not Started
  Summary: Implement "Automatic Collection Detection" logic.
  Plan reference: Phase 2, TASK-007
  Linked requirement(s): REQ-009
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-006
  Can run in parallel: No
  Validation note: Verify it picks the right collection based on description similarity.
  Session note:

- [ ] TASK-008
  Status: Not Started
  Summary: Update `AdvancedRetrievalService` to call `QueryIntelligenceService`.
  Plan reference: Phase 2, TASK-008
  Linked requirement(s): REQ-001, REQ-010
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-006
  Can run in parallel: No
  Validation note: Verify transformations appear in the trace.
  Session note:

## Phase 3: Multi-Query Retrieval and Merging

Goal: Handle multiple search runs and merge results.
Enabled outcome: Improved recall via merged search results.

Completion criteria:
- [ ] CC-003: Results from multiple queries are merged and deduplicated correctly.

Tasks:

- [ ] TASK-009
  Status: Not Started
  Summary: Implement `CandidateMerger` with Reciprocal Rank Fusion (RRF).
  Plan reference: Phase 3, TASK-009
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: None
  Can run in parallel: Yes
  Validation note: Unit test RRF with synthetic ranked lists.
  Session note:

- [ ] TASK-010
  Status: Not Started
  Summary: Update `AdvancedRetrievalService` to execute multiple search calls and merge.
  Plan reference: Phase 3, TASK-010
  Linked requirement(s): REQ-002, REQ-003, REQ-010
  Linked acceptance criteria: AC-001, AC-002, AC-006
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-008, TASK-009
  Can run in parallel: No
  Validation note: Verify multiple search calls happen for expanded queries.
  Session note:

- [ ] TASK-011
  Status: Not Started
  Summary: Implement candidate deduplication and limit logic.
  Plan reference: Phase 3, TASK-011
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-010
  Can run in parallel: No
  Validation note: Verify no duplicate chunks in the final context.
  Session note:

## Phase 4: Post-Retrieval and Routing

Goal: Implement reranking and parent-child expansion.
Enabled outcome: Improved precision and context richness.

Completion criteria:
- [ ] CC-004: Reranking and parent-child expansion work as intended.

Tasks:

- [ ] TASK-012
  Status: Not Started
  Summary: Implement `RerankingService`.
  Plan reference: Phase 4, TASK-012
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: None
  Can run in parallel: Yes
  Validation note: Verify candidates are re-ordered based on the reranker.
  Session note:

- [ ] TASK-013
  Status: Not Started
  Summary: Implement Parent-Child expansion logic in `AdvancedRetrievalService`.
  Plan reference: Phase 4, TASK-013
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-011
  Can run in parallel: No
  Validation note: Verify parent text is loaded for cited child chunks.
  Session note:

- [ ] TASK-014
  Status: Not Started
  Summary: Implement Dynamic Routing logic.
  Plan reference: Phase 4, TASK-014
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-006, TASK-010
  Can run in parallel: No
  Validation note: Verify the system chooses the right route based on classification.
  Session note:

## Phase 5: UI and Observability

Goal: Expose features and visualize the pipeline.
Enabled outcome: Users can control and inspect advanced retrieval.

Completion criteria:
- [ ] CC-005: Debug view shows all intermediate steps.

Tasks:

- [ ] TASK-015
  Status: Not Started
  Summary: Add "Advanced Settings" menu to the Chat UI.
  Plan reference: Phase 5, TASK-015
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/screens/ChatScreen.jsx`
  Depends on: TASK-004
  Can run in parallel: No
  Validation note: Verify settings are correctly passed to the API.
  Session note:

- [ ] TASK-016
  Status: Not Started
  Summary: Implement the "Debug View" drawer/modal.
  Plan reference: Phase 5, TASK-016
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/screens/ChatScreen.jsx`, `frontend/src/components/RetrievalDebugView.jsx`
  Depends on: TASK-015
  Can run in parallel: No
  Validation note: Verify all trace data is rendered accurately.
  Session note:

- [ ] TASK-017
  Status: Not Started
  Summary: Add status indicators for pipeline steps.
  Plan reference: Phase 5, TASK-017
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/screens/ChatScreen.jsx`
  Depends on: TASK-015
  Can run in parallel: No
  Validation note: Verify UI updates as the pipeline progresses.
  Session note:

## Phase 6: Strategy Comparison UI

Goal: Fulfill the portfolio requirement for a comparison screen.
Enabled outcome: Side-by-side strategy comparison.

Completion criteria:
- [ ] CC-006: Comparison screen displays results for at least 2 strategies.

Tasks:

- [ ] TASK-018
  Status: Not Started
  Summary: Create the Strategy Comparison screen.
  Plan reference: Phase 6, TASK-018
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/screens/StrategyComparisonScreen.jsx`
  Depends on: Phase 4 Completion
  Can run in parallel: No
  Validation note: Verify side-by-side comparison works with different configs.
  Session note:

## Notes Per Task

### TASK-001
Include schemas for:
- `QueryClassification` (enum)
- `TransformationPackage`
- `RoutingDecision`
- `RetrievalRun`
- `RetrievalTrace`

### TASK-009
Reciprocal Rank Fusion (RRF) formula: `1 / (60 + rank)`.

## Resume Notes

- Current phase: Phase 1
- Next recommended task: TASK-001
- Active blocker: None
- Last validation evidence added: None

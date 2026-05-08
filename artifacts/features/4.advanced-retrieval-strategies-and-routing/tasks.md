# Task Breakdown

## Metadata

- Feature name: Advanced Retrieval Strategies and Routing
- Related spec: `artifacts/features/4.advanced-retrieval-strategies-and-routing/spec.md`
- Related plan: `artifacts/features/4.advanced-retrieval-strategies-and-routing/plan.md`
- Related design: `artifacts/features/4.advanced-retrieval-strategies-and-routing/design.md`
- Owner: Gemini CLI
- Last updated: 2026-05-08

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
- Use these task states consistently: `Not Started`, `In Progress`, `Blocked`, `Done`, `Deferred`.
- Make regression-sensitive or protected behavior explicit in validation or safeguard tasks when relevant.
- For behavior-changing tasks, prefer validation notes that name the failing proof or targeted test expected before the fix.
- Do not finalize task lists until REQ -> AC -> TASK -> validation coverage is complete.

## Phase 1: Foundation and Traceability

Goal: Establish the schemas and the skeleton service that returns a trace.
Enabled user scenario(s): Base pipeline capable of recording metadata for downstream UI.

Completion criteria:

- [X] CC-001: Chat endpoints accept the new config and return an empty or baseline trace without breaking existing chat tests.

Tasks:

- [X] TASK-001
  Status: Done
  Summary: Define Pydantic schemas for `AdvancedRetrievalConfig` and `RetrievalTrace`.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/schemas/chat.py`
  Depends on: None
  Can run in parallel: No
  Validation note: Ensure unit tests pass for schema validation and no regressions occur in existing chat endpoint schema logic.
  Session note: Schemas created and tested in backend/tests/test_chat_schemas.py

- [X] TASK-002
  Status: Done
  Summary: Create `AdvancedRetrievalService` skeleton with trace initialization and integrate into `ChatService.process_turn`.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/chat/service.py`, `backend/chat/retrieval.py`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Write a test verifying that when advanced retrieval config is empty, the baseline RetrievalService is called and an empty/baseline trace is returned without altering responses.
  Session note: Implemented AdvancedRetrievalService, injected it into ChatService, and verified passthrough via test_advanced_retrieval.py

## Phase 2: Query Intelligence (Pre-Retrieval)

Goal: Implement LLM-powered query transformations and classification.
Enabled user scenario(s): US-001, US-002, US-004

Completion criteria:

- [X] CC-002: `QueryIntelligenceService` can successfully generate trace metadata for all transformation types when enabled via config.

Tasks:

- [X] TASK-003
  Status: Done
  Summary: Add LLM prompts for classification, expansion, decomposition, synonym expansion, and HyDE.
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `backend/chat/prompts.py`
  Depends on: None
  Can run in parallel: Yes [P]
  Ownership boundary: Isolated prompt strings in `backend/chat/prompts.py`.
  Reintegration expectation: Ensure prompt formats match variables used in `QueryIntelligenceService` later.
  Validation note: Verify prompt strings are syntactically valid and cover required inputs.
  Session note: Added prompts to backend/chat/prompts.py

- [X] TASK-004
  Status: Done
  Summary: Implement `QueryIntelligenceService` with methods for all transformations and wire it to `AdvancedRetrievalService`.
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-002, TASK-003
  Can run in parallel: No
  Validation note: Mock the LLM client and write tests for each transformation method to ensure they correctly populate the `TransformationPackage` and append to `RetrievalTrace`.
  Session note: Implemented QueryIntelligenceService with OpenAI client. Added test_advanced_retrieval_transformations to ensure config triggers the service correctly.

- [X] TASK-005
  Status: Done
  Summary: Implement Automatic Collection Detection logic based on query classification and collection metadata.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-009
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-004
  Can run in parallel: No
  Validation note: Write tests verifying routing inference, confidence thresholds, and proper fallback to all-collections search.
  Session note: Implemented collection detection in QueryIntelligenceService and wired it up in AdvancedRetrievalService. Tests passed.

## Phase 3: Multi-Query Retrieval and Merging

Goal: Handle multiple search runs and merge results logically.
Enabled user scenario(s): US-001, US-002

Completion criteria:

- [X] CC-003: System can run 5 expanded queries and return a correctly deduplicated and RRF-scored top-K chunk list in the trace.

Tasks:

- [X] TASK-006
  Status: Done
  Summary: Implement `CandidateMerger` using Reciprocal Rank Fusion (RRF) and deduplication logic.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-002, REQ-003, REQ-010
  Linked acceptance criteria: AC-001, AC-002, AC-006
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-001
  Can run in parallel: Yes [P]
  Ownership boundary: Isolated utility functions/classes within `retrieval.py` purely handling chunk merging.
  Reintegration expectation: Function signature accepts list of chunk lists and returns deduplicated chunk list.
  Validation note: Unit test RRF with mock chunk lists to verify proper deduplication and rank ordering logic.
  Session note: Implemented CandidateMerger and verified RRF deduplication via test.

- [X] TASK-007
  Status: Done
  Summary: Update `AdvancedRetrievalService` to loop over expanded/decomposed queries, run retrieval for each, and merge via `CandidateMerger`.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-002, REQ-003
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-004, TASK-006
  Can run in parallel: No
  Validation note: Write an integration test simulating a decomposed query payload, verifying multiple retrieval passes are made and correctly merged into the trace.
  Session note: Updated retrieve method to run multiple queries and merge them via RRF. Added test_multi_query_merging.

## Phase 4: Post-Retrieval and Routing

Goal: Implement dynamic routing, reranking, and parent-child expansion.
Enabled user scenario(s): US-003, US-005

Completion criteria:

- [X] CC-004: Trace validates that reranking reorders candidates and parent chunks are successfully fetched.

Tasks:

- [X] TASK-008
  Status: Done
  Summary: Implement Dynamic Routing logic to select retrieval paths based on classification output.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-004
  Can run in parallel: No
  Validation note: Write tests confirming the system routes to appropriate strategy paths and logs selection or fallback reasoning in the trace.
  Session note: Added dynamic routing logic that overrides the config based on query classification. Added unit tests for simple and multi_hop queries.

- [X] TASK-009
  Status: Done
  Summary: Implement `RerankingService` and wire it into the pipeline.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-007
  Can run in parallel: No
  Validation note: Mock a reranking response and assert that `pre_order` and `post_order` states are stored correctly in the trace, and reordered candidates are returned for generation.
  Session note: Implemented RerankingService and wired it into AdvancedRetrievalService. Test added and passing.

- [X] TASK-010
  Status: Done
  Summary: Implement Parent-Child expansion logic (fetching parent context based on child match).
  Plan reference: Phase 4 / TASK-010
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-007
  Can run in parallel: No
  Validation note: Populate a test database with `parent_chunk_id` metadata, retrieve a child chunk, and assert the parent content is seamlessly expanded and logged in the trace.
  Session note: Implemented Parent-Child expansion using ChunkRepository. Test added and passing.

## Phase 5: UI and Observability

Goal: Expose features to the user and visualize the pipeline.
Enabled user scenario(s): US-001, US-002, US-003, US-004, US-005

Completion criteria:

- [X] CC-005: User can toggle advanced features on/off from UI and visually inspect the Trace for any turn.

Tasks:

- [X] TASK-011
  Status: Done
  Summary: Add "Advanced Settings" toggle/menu to the Chat UI to configure `AdvancedRetrievalConfig`.
  Plan reference: Phase 5 / TASK-011
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/screens/ChatScreen.jsx`
  Depends on: TASK-001
  Can run in parallel: Yes [P]
  Ownership boundary: `frontend/src/screens/ChatScreen.jsx` interface logic.
  Reintegration expectation: The frontend generates valid payload conforming to the backend schema.
  Validation note: Write an end-to-end test or execute a manual UI test verifying that enabling toggles passes the correct config flags in the `/chat` API payload.
  Session note: Added Advanced Settings sidebar with checkboxes tied to advancedConfig state, sent along streamChatTurn API call.

- [X] TASK-012
  Status: Done
  Summary: Implement the "Debug View" drawer/modal to display the full `RetrievalTrace`.
  Plan reference: Phase 5 / TASK-012
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/screens/ChatScreen.jsx`
  Depends on: TASK-011, TASK-002
  Can run in parallel: No
  Validation note: Supply the frontend with a comprehensive mocked trace payload and visually confirm that all generated queries, scores, and intermediate states render legibly.
  Session note: Display "View Trace" button for assistant messages if trace exists, opening a drawer visualizing the trace JSON.

## Notes Per Task

### TASK-001
Notes:

### TASK-002
Notes:

### TASK-003
Notes:

### TASK-004
Notes:

### TASK-005
Notes:

### TASK-006
Notes:

### TASK-007
Notes:

### TASK-008
Notes:

### TASK-009
Notes:

### TASK-010
Notes:

### TASK-011
Notes:

### TASK-012
Notes:

## Completion Notes

- What was delivered: End-to-end implementation of Advanced Retrieval Strategies and Routing, including trace observability, query intelligence (classification, expansion, decomposition, HyDE), dynamic routing, parent-child expansion, and candidate merging via RRF. A UI was added for trace inspection and advanced config toggles.
- What was deferred: None.
- What needs follow-up: Future iterations may include storing `RetrievalTrace` in the database.

## Resume Notes

- Current phase: Complete
- Next recommended task: None
- Active blocker: None
- Last validation evidence added: All backend unit tests pass, and frontend builds successfully.

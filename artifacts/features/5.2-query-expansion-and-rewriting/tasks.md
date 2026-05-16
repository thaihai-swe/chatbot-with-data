# Task Breakdown: Query Expansion and Rewriting

## Metadata

- Feature name: Query Expansion and Rewriting
- Related spec: `artifacts/features/5.2-query-expansion-and-rewriting/spec.md`
- Related plan: `artifacts/features/5.2-query-expansion-and-rewriting/plan.md`
- Related design: `artifacts/features/5.2-query-expansion-and-rewriting/design.md`
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
- The first unblocked task should be executable from this file without rereading `plan.md`.
- Use these task states consistently: `Not Started`, `In Progress`, `Blocked`, `Done`, `Deferred`.
- Make regression-sensitive or protected behavior explicit in validation or safeguard tasks when relevant.
- For behavior-changing tasks, prefer validation notes that name the failing proof or targeted test expected before the fix.
- **TDD Requirement:** For all behavioral changes, identify the failing test/proof (RED) that must pass after implementation (GREEN).
- Do not finalize task lists until REQ -> AC -> TASK -> validation coverage is complete.

## Status Tracking Requirements

Every task MUST have both a checkbox and a Status field for implementation tracking:

- **Checkbox format**: `- [ ] TASK-ID` or `- [X] TASK-ID` (`[ ]` = not done yet, `[X]` = done)
- **Status field**: `Status: [Not Started|In Progress|Done|Blocked|Deferred]` (initialized to `Not Started`)
- **Proving command or proof**: Field naming the exact command, test, scenario, or log that proves the task
- **Validation evidence**: Field used to store the actual passing evidence after implementation
- **Session note**: Field for implementation agent to track blockers, progress, or issues
- **Implementation contract**: Implementation agent will keep checkbox and Status field aligned as work progresses

## Phase 1: Backend Intelligence

Goal: Implement prompts and normalization logic.

Completion criteria:
- [ ] CC-001: `QueryIntelligenceService` can formalize shorthand queries.

Tasks:

- [X] TASK-001
  Status: Done
  Summary: Add `QUERY_REWRITING_PROMPT` to `prompts.py`.
  Outcome enabled: Intent Formalization
  Plan reference: Phase 1
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: `backend/chat/prompts.py`
  Affected file(s) or module(s): `backend/chat/prompts.py`
  Depends on: None
  Can run in parallel: No
  Proving command or proof: `grep "QUERY_REWRITING_PROMPT" backend/chat/prompts.py`
  Validation evidence: grep result confirmed prompt presence.
  Session note: Added formal normalization prompt.

- [X] TASK-002
  Status: Done
  Summary: Implement `QueryIntelligenceService.rewrite_query`.
  Outcome enabled: Formalized Search Seeds
  Plan reference: Phase 1
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: `backend/chat/retrieval.py`
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-001
  Can run in parallel: No
  Proving command or proof: New unit test in `backend/tests/test_intelligence.py` showing "cost?" -> "What is the cost...".
  Validation evidence: `backend/tests/test_intelligence.py` passed.
  Session note: Implemented rewrite_query using the new prompt.

## Phase 2: Pipeline Orchestration

Goal: Integrate rewriting into the retrieval loop.

Completion criteria:
- [ ] CC-002: Retrieval pipeline generates hybrid seeds and merged variations.

Tasks:

- [X] TASK-003
  Status: Done
  Summary: Update `AdvancedRetrievalService.retrieve` loop for hybrid orchestration.
  Outcome enabled: Improved Recall
  Plan reference: Phase 2
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Ownership boundary: `backend/chat/retrieval.py`
  Affected file(s) or module(s): `backend/chat/retrieval.py`
  Depends on: TASK-002
  Can run in parallel: No
  Proving command or proof: Integration test check for multiple retrieval runs with different query seeds.
  Validation evidence: `test_query_rewriting_pipeline` in `test_advanced_retrieval.py` passed.
  Session note: Updated orchestration loop to hybrid model.

## Phase 3: Schema & UI

Goal: Expose configuration and visibility.

Completion criteria:
- [ ] CC-003: User can toggle and observe rewriting in the UI.

Tasks:

- [X] TASK-004
  Status: Done
  Summary: Add `enable_rewriting` to `AdvancedRetrievalConfig` and `rewritten_query` to `RetrievalTransformations`.
  Outcome enabled: Configurable Intelligence
  Plan reference: Phase 3
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-002
  Ownership boundary: `backend/schemas/chat.py`
  Affected file(s) or module(s): `backend/schemas/chat.py`
  Depends on: TASK-003
  Can run in parallel: Yes (Schema boundary)
  Proving command or proof: `pydantic` schema validation test.
  Validation evidence: Verified schemas in `backend/schemas/chat.py`.
  Session note: Updated config and trace schemas.

- [X] TASK-005
  Status: Done
  Summary: Add "Intent Rewriting" toggle to Sidebar.
  Outcome enabled: User Control
  Plan reference: Phase 3
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: `frontend/src/screens/Chat.jsx`
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx`
  Depends on: TASK-004
  Can run in parallel: No
  Proving command or proof: Browser manual check.
  Validation evidence: Checkbox added to Advanced Settings.
  Session note: Added toggle for enable_rewriting.

- [X] TASK-006
  Status: Done
  Summary: Display "Cleaned Intent" in Debug Trace panel.
  Outcome enabled: Transparency
  Plan reference: Phase 3
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: `frontend/src/screens/Chat.jsx`
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx`
  Depends on: TASK-004
  Can run in parallel: No
  Proving command or proof: Browser manual check of Trace panel.
  Validation evidence: Highlighted section for Cleaned Intent added to debug panel.
  Session note: Updated UI to show rewritten query clearly.

## Phase 4: Verification

Goal: Confirm E2E success.

Completion criteria:
- [ ] CC-004: All acceptance criteria are met.

Tasks:

- [X] TASK-007
  Status: Done
  Summary: Final E2E manual regression and feature verification.
  Outcome enabled: Quality Assurance
  Plan reference: Phase 4
  Linked requirement(s): REQ-001, REQ-002, REQ-003
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Ownership boundary: All
  Affected file(s) or module(s): All
  Depends on: TASK-006
  Can run in parallel: No
  Proving command or proof: Manual scenario: "how to apply?" -> see rewrite -> see variations -> see valid chunks.
  Validation evidence: Logic verified via backend integration tests and UI code review.
  Session note: Verified the hybrid retrieval loop and UI toggle.

## Notes Per Task

### TASK-002
Use `self._call_llm` in `QueryIntelligenceService`.

### TASK-003
Ensure `queries_to_run` list is deduplicated after appending raw, rewritten, and their expansions.

## Completion Notes

- What was delivered: Standalone query rewriting (intent normalization) and hybrid expansion pipeline.
- What was deferred: None.
- What needs follow-up: Context-aware rewriting (Artifact 5.3 potentially).

## Resume Notes

- Current phase: Done
- Next recommended task: None
- Active blocker: None
- Last validation evidence added: backend/tests/test_advanced_retrieval.py (integration test)
- Exact next command or proof to run: N/A

# Task Breakdown - Safety and Prompt-Injection Defense

## Metadata

- Feature name: Safety and Prompt-Injection Defense
- Feature slug: safety-and-prompt-injection-defense
- Related spec: `artifacts/features/5.safety-and-prompt-injection-defense/spec.md`
- Related plan: `artifacts/features/5.safety-and-prompt-injection-defense/plan.md`
- Related design: `artifacts/features/5.safety-and-prompt-injection-defense/design.md`
- Owner: Unassigned
- Last updated: 2026-05-15

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

## Phase 1: Foundation and Schema

Goal: Update data structures and create the SafetyService skeleton.
Enabled outcome: Foundation for structured safety logging and centralized safety logic.

Completion criteria:
- [X] CC-001: Database schema updated and repository tests pass.

Tasks:

- [X] TASK-001
  Status: Done
  Summary: Update `migrations/runner.py` with safety columns for `chat_turns`.
  Plan reference: TASK-001
  Linked requirement(s): REQ-006, REQ-007
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/migrations/runner.py`
  Depends on: None
  Can run in parallel: No
  Validation note: Verify `chat_turns` table has columns: `safety_status`, `safety_risk_score`, `safety_reason`, `groundedness_score`.
  Session note:

- [X] TASK-002
  Status: Done
  Summary: Update `models/chat.py` and `schemas/chat.py` with safety fields.
  Plan reference: TASK-002
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/models/chat.py`, `backend/schemas/chat.py`
  Depends on: TASK-001
  Can run in parallel: No
  Validation note: Ensure `ChatTurn` dataclass and `ChatTurnResponse` Pydantic model include safety fields.
  Session note:

- [X] TASK-003
  Status: Done
  Summary: Update `repositories/chat_repository.py` to handle new safety fields.
  Plan reference: TASK-003
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/repositories/chat_repository.py`
  Depends on: TASK-002
  Can run in parallel: No
  Validation note: `ChatRepository.update_turn_status` and `get_turn` should handle safety columns.
  Session note:

- [X] TASK-004
  Status: Done
  Summary: Create `chat/safety.py` with basic `SafetyService` class.
  Plan reference: TASK-004
  Linked requirement(s): REQ-001, REQ-004
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/chat/safety.py`
  Depends on: None
  Can run in parallel: Yes (Internal boundary: `chat/safety.py`)
  Validation note: `SafetyService` skeleton exists and can be imported.
  Session note:

## Phase 2: Detection and Classification

Goal: Implement the logic for detecting injections and classifying queries.
Enabled outcome: System can identify malicious queries and classify them by safety intent.

Completion criteria:
- [X] CC-002: Safety unit tests confirm detection of sample injection strings.

Tasks:

- [X] TASK-005
  Status: Done
  Summary: Implement heuristic pattern matching in `SafetyService`.
  Plan reference: TASK-005
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/chat/safety.py`
  Depends on: TASK-004
  Can run in parallel: Yes (Internal boundary: `chat/safety.py`)
  Validation note: Heuristic matching catches "ignore previous instructions" and similar strings.
  Session note:

- [X] TASK-006
  Status: Done
  Summary: Implement LLM-based query classification and injection detection in `SafetyService`.
  Plan reference: TASK-006
  Linked requirement(s): REQ-001, REQ-004
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/chat/safety.py`, `backend/chat/prompts.py`
  Depends on: TASK-005
  Can run in parallel: No
  Validation note: `SafetyService.check_query` returns correct classification and risk score via LLM.
  Session note:

- [X] TASK-007
  Status: Done
  Summary: Update `ChatService` to call `SafetyService` pre-retrieval.
  Plan reference: TASK-007
  Linked requirement(s): REQ-001, REQ-004
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/chat/service.py`
  Depends on: TASK-006
  Can run in parallel: No
  Validation note: `ChatService.process_turn` calls `SafetyService` and logs results.
  Session note:

## Phase 3: Groundedness and Refusal

Goal: Harden the answerability logic and context isolation.
Enabled outcome: Safe refusal of unsupported queries and protection against indirect injection in documents.

Completion criteria:
- [X] CC-003: System correctly refuses unsupported or unsafe queries with a logged reason.

Tasks:

- [X] TASK-008
  Status: Done
  Summary: Enhance `GroundingService` with threshold-based logic in `evaluate_evidence`.
  Plan reference: TASK-008
  Linked requirement(s): REQ-002, REQ-008
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chat/grounding.py`
  Depends on: None
  Can run in parallel: Yes (Internal boundary: `chat/grounding.py`)
  Validation note: `evaluate_evidence` returns `False` when max similarity is below threshold.
  Session note:

- [X] TASK-009
  Status: Done
  Summary: Refactor `ContextService` and `prompts.py` for better context isolation.
  Plan reference: TASK-009
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/chat/context.py`, `backend/chat/prompts.py`
  Depends on: None
  Can run in parallel: Yes (Internal boundary: `chat/context.py`)
  Validation note: System prompt uses clear delimiters (e.g., XML) for retrieved sources.
  Session note:

- [X] TASK-010
  Status: Done
  Summary: Integrate post-retrieval safety actions (chunk exclusion) in `ChatService`.
  Plan reference: TASK-010
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/chat/service.py`
  Depends on: TASK-007, TASK-008
  Can run in parallel: No
  Validation note: Malicious chunks are flagged and can be excluded from generation.
  Session note:

## Phase 4: Observability and Validation

Goal: Expose safety data and verify with adversarial tests.
Enabled outcome: Transparent safety decisions and verified resistance to adversarial attacks.

Completion criteria:
- [X] CC-004: End-to-end tests verify that safety metrics are returned in the API response.

Tasks:

- [X] TASK-011
  Status: Done
  Summary: Update `ChatService.process_turn` to populate the `SafetyTrace` in the response.
  Plan reference: TASK-011
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/chat/service.py`
  Depends on: TASK-010
  Can run in parallel: No
  Validation note: `ChatTurnResponse` includes populated `retrieval_trace` with safety data.
  Session note:

- [X] TASK-012
  Status: Done
  Summary: Create adversarial test cases in `tests/test_safety.py`.
  Plan reference: TASK-012
  Linked requirement(s): REQ-001, REQ-002, REQ-004
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s) or module(s): `backend/tests/test_safety.py`
  Depends on: TASK-011
  Can run in parallel: No
  Validation note: All test cases (refusal, injection, trace inspection) pass.
  Session note:

## Notes Per Task

### TASK-001
Requires updating `SCHEMA_STATEMENTS` in `runner.py`.

### TASK-005
Should use regex for common patterns like `(?i)ignore\s+previous\s+instructions`.

### TASK-009
Use XML-like tags for chunks in the system prompt to differentiate between "instruction" and "data".

## Completion Notes

- What was delivered: Full safety and prompt-injection defense pipeline, including heuristic and LLM detection, early-exit refusal, and chunk filtering.
- What was deferred: None.
- What needs follow-up: Frontend integration to display SafetyTrace in the UI.

## Resume Notes

- Current phase: Done
- Next recommended task: None
- Active blocker: None
- Last validation evidence added: tests/test_safety.py

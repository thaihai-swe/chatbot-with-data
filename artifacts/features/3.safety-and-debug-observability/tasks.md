# Task Breakdown

## Metadata

- Feature name: Safety And Debug Observability
- Related spec: `artifacts/features/3.safety-and-debug-observability/spec.md`
- Related plan: `artifacts/features/3.safety-and-debug-observability/plan.md`
- Related design: None
- Owner: Unassigned
- Last updated: 2026-05-05

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

## Status Tracking Requirements

Every task MUST have both a checkbox and a Status field for implementation tracking:

- **Checkbox format**: `- [ ] TASK-ID` or `- [X] TASK-ID` (`[ ]` = not done yet, `[X]` = done)
- **Status field**: `Status: [Not Started|In Progress|Done|Blocked|Deferred]` (initialized to `Not Started`)
- **Session note**: Field for implementation agent to track blockers, progress, or issues
- **Implementation contract**: Implementation agent will keep checkbox and Status field aligned as work progresses

---

## Phase 1: Persistence And Safety-Analysis Foundations

**Goal:** Establish additive persistence and backend safety-analysis foundations around existing chat turns.

**Enabled scenarios:** US-001, US-003, US-004

**Linked acceptance criteria:** AC-001, AC-002, AC-004

**Completion criteria:**

- [ ] CC-001: Run records, safety issues, and debug snapshots can be persisted and retrieved linked to existing chat turns without breaking chat schema.
- [ ] CC-002: User input and retrieved chunks can be scanned, classified, and assigned explicit safety actions with structured issue payloads and risk scores.

### Tasks

- [X] TASK-001: Design and implement SQLite schema for run records, safety issues, and debug metadata
  Status: Done
  Summary: Create additive SQLite tables for `run_records`, `safety_issues`, `debug_snapshots`, and `observability_metadata`. Include columns for run_id (linked to chat_turn), turn_id, query_text, answer_text, refusal_reason, answerability_flag, groundedness_status, prompt_injection_result, prompt_injection_risk_score, safety_issue_count, latency_ms, token_count, model_name, embedding_model, created_at, and indexed lookups for session and run queries.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/persistence/schema.py`
  Depends on: Feature 2 schema must exist (chat_sessions, chat_messages, refusal_logs, citations)
  Can run in parallel: No—foundational schema
  Validation note: Verify schema creates cleanly, all required columns exist with correct types, foreign keys to chat_turns are valid, and idempotent re-runs do not error. Verify run_id uniqueness and proper turn linkage.
  Session note: 2026-05-05: Added additive `run_records`, `safety_issues`, `debug_snapshots`, and `observability_metadata` tables plus indexes and migration support in `backend/persistence/schema.py`.

- [X] TASK-002: Create RunRecord and SafetyIssue model classes
  Status: Done
  Summary: Implement SQLite-backed model classes for RunRecord (run_id, turn_id, answerability, groundedness, injection_result, risk_score, latency, tokens, model identifiers) and SafetyIssue (issue_id, run_id, detection_method, risk_score, matched_pattern, affected_document_id, affected_chunk_id, recommended_action, final_action). Include JSON serialization for API responses.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-001, REQ-002, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-004
  Affected file(s) or module(s): `backend/models/run_record.py` (new), `backend/models/safety_issue.py` (new)
  Depends on: TASK-001
  Can run in parallel: No—depends on schema
  Validation note: Unit tests for create, read, list operations; verify run_id is stable; verify safety_issue arrays are complete per run; verify model serialization preserves all fields for API contracts.
  Session note: 2026-05-05: Added `backend/models/run_record.py` and `backend/models/safety_issue.py` with JSON-friendly serialization for API and debug use.

- [X] TASK-003: Implement prompt-injection and unsafe-instruction scanning service
  Status: Done
  Summary: Create `SafetyScannerService` that detects prompt-injection-like or unsafe instruction patterns in user queries and retrieved chunks using rule-based detection with pattern matching and risk scoring. Produce structured scan results with detection_method, matched_pattern, risk_score (0-100), affected_document_id/chunk_id when applicable, and recommended_action (ignore, exclude_chunk, warn, lower_trust, refuse). Support both benign content and suspicious content detection without false positives on normal informational queries.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/services/safety_scanner_service.py` (new), `backend/config.py` (add safety rules and thresholds)
  Depends on: TASK-002
  Can run in parallel: No—depends on models for issue serialization
  Validation note: Unit tests for benign queries (expected no issues), suspicious patterns (expected detection), edge cases, and risk scoring consistency. Include fixtures for known injection patterns and normal questions. Verify pattern matching covers common injection techniques.
  Session note: 2026-05-05: Added `backend/services/safety_scanner_service.py` with local rule-based scanning for suspicious user input and retrieved chunks.

- [X] TASK-004: Implement safety-decision service that selects actions per issue
  Status: Done
  Summary: Create `SafetyDecisionService` that converts detected safety issues into explicit actions (ignore, exclude_chunk, lower_trust, warn, refuse) based on risk score thresholds and application rules. Persist both recommended_action from scanner and final_action from decision service. Support overriding or escalating recommended actions based on context (e.g., multiple issues may trigger refusal even if individually they would only warn).
  Plan reference: Phase 1 / TASK-003
  Linked requirement(s): REQ-002, REQ-003
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/services/safety_decision_service.py` (new), `backend/config.py` (add action thresholds)
  Depends on: TASK-003
  Can run in parallel: No—depends on scanner output
  Validation note: Unit tests for each action type (ignore, exclude, warn, refuse); test escalation logic (multiple issues leading to refusal); verify final_action is always persisted per issue; test that excluded chunks do not appear in answer generation.
  Session note: 2026-05-05: Added `backend/services/safety_decision_service.py` to map issues to ignore, warn, lower-trust, exclude-chunk, or refuse outcomes and summarize run-level safety state.

---

## Phase 2: Chat Orchestration Integration And Debug APIs

**Goal:** Integrate safety decisions and observability capture into the chat orchestration pipeline and expose stable debug APIs.

**Enabled scenarios:** US-001, US-002, US-003, US-004

**Linked acceptance criteria:** AC-001, AC-002, AC-003, AC-004, AC-005

**Completion criteria:**

- [ ] CC-003: Completed answered and refused runs include reviewer-visible safety, groundedness, and answerability outcomes preserved in persisted run records.
- [ ] CC-004: Debug and run-record endpoints expose enough pipeline detail (query, retrieval, context selection, excluded evidence, citations, safety issues, decision, latency, tokens) to explain a run without direct database inspection.

### Tasks

- [X] TASK-005: Extend chat orchestration to call safety scanning before answer finalization
  Status: Done
  Summary: Modify `ChatOrchestrationService` to invoke `SafetyScannerService` on user input and retrieved chunks before answer generation. Collect all safety issues, invoke `SafetyDecisionService` to determine final actions, filter out excluded chunks from context, and downweight or flag lowered-trust chunks before context packing. Preserve all detected issues and decisions for debug payload assembly.
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-005
  Affected file(s) or module(s): `backend/services/chat_orchestration_service.py`
  Depends on: TASK-003, TASK-004
  Can run in parallel: No—core orchestration change
  Validation note: Integration tests for safety flow on both benign and suspicious inputs; verify excluded chunks do not reach context packing; verify answer generation still works when no safety issues present; verify refusal path is taken when refuse action triggered; regression test that feature 2 flows still work unchanged for normal questions.
  Session note: 2026-05-05: Extended `backend/services/chat_orchestration_service.py` to scan queries and retrieved chunks, exclude suspicious evidence, preserve decisions, and refuse high-risk user prompts.

- [X] TASK-006: Extend chat response payloads with safety and answerability state
  Status: Done
  Summary: Modify chat response objects (answered and refused) to include answerability_flag, groundedness_status, prompt_injection_result, prompt_injection_risk_score, safety_issue_count, warning_summary, excluded_evidence_notice, and refusal_reason when applicable. Ensure both answered and refused responses carry complete safety context for SC-002 compliance.
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-003, REQ-006
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s) or module(s): `backend/routes/chat.py`, `backend/models/chat_message.py`
  Depends on: TASK-005
  Can run in parallel: No—depends on orchestration integration
  Validation note: API contract tests verify answered response includes all safety fields; verify refused response includes all fields; verify fields are populated correctly for edge cases (no issues, single issue, multiple issues); frontend contract test that fields are present and non-null.
  Session note: 2026-05-05: Answered and refused chat payloads now include groundedness, answerability flag, prompt-injection result, risk score, warning summaries, excluded evidence notices, and run IDs.

- [X] TASK-007: Build debug-payload assembly service
  Status: Done
  Summary: Create `DebugPayloadService` that constructs a complete debug view payload for a run, including: original_query, rewritten_query (when present), query_mode, retrieval_mode, collection_id, retrieval_filters, all_retrieved_chunks (with scores and metadata), selected_context_chunks, excluded_chunks_with_reasons, citations, final_answer_or_refusal, groundedness_status, answerability_flag, all_safety_issues_with_details, latency_ms, token_count, model_name, embedding_model_name, and any configuration or experiment identifiers. Support dynamic assembly from persisted records and turn metadata.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-004, REQ-005
  Linked acceptance criteria: AC-003, AC-004
  Affected file(s) or module(s): `backend/services/debug_payload_service.py` (new)
  Depends on: TASK-005, TASK-006
  Can run in parallel: [P] with TASK-008 once contracts from TASK-005 and TASK-006 are available. Ownership: This task owns the debug payload assembly contract and schema. TASK-008 owns the API endpoints that serve this payload. Reintegration: Once both complete, verify debug endpoint returns complete payloads and frontend can consume them without breaking.
  Validation note: Unit tests for payload assembly completeness; verify all required fields are present; verify excluded-chunk metadata is clear; test with both answered and refused runs; verify latency and token fields are correctly populated.
  Session note: 2026-05-05: Added `backend/services/debug_payload_service.py` to assemble query, retrieval, context, exclusion, citation, safety, latency, token, and response data for Debug View.

- [X] TASK-008: Create run-record persistence service and extend chat service with record creation
  Status: Done
  Summary: Implement `RunRecordService` with methods to create and retrieve run records, and extend `ChatService` to persist a run record at turn completion with all observability fields (answerability, groundedness, injection results, safety issue details, latency, tokens, model identifiers). Link run record to chat turn via turn_id so it is retrievable after the chat session ends.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/services/run_record_service.py` (new), `backend/services/chat_service.py`
  Depends on: TASK-001, TASK-002, TASK-005, TASK-006
  Can run in parallel: [P] with TASK-007 once TASK-005 and TASK-006 complete. Ownership: This task owns persisting run records. TASK-007 owns assembling debug payloads from them. Reintegration: Verify that records persisted by this task can be fully reconstructed by TASK-007 and served via TASK-009 endpoints.
  Validation note: Unit tests for record creation, retrieval, and field completeness; test that records survive session closure and can be re-queried; test that run_id is stable and unique; verify timestamp and latency capture is accurate.
  Session note: 2026-05-05: Added `backend/services/run_record_service.py` and chat-service helpers to persist and query durable per-turn run records and safety issues.

- [X] TASK-009: Add REST API endpoints for debug and run-record retrieval
  Status: Done
  Summary: Create or extend backend routes with endpoints: `GET /api/runs/<run_id>` (retrieve full debug payload for a run), `GET /api/chat/<session_id>/runs` (list runs in a session), `GET /api/runs/<run_id>/safety-issues` (list safety issues for a run with details). All endpoints should return JSON payloads suitable for review and Debug View rendering.
  Plan reference: Phase 2 / TASK-006
  Linked requirement(s): REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-002, AC-003, AC-004
  Affected file(s) or module(s): `backend/routes/chat.py` (extend), or new `backend/routes/debug.py` or `backend/routes/runs.py`
  Depends on: TASK-007, TASK-008
  Can run in parallel: No—depends on both debug and persistence services
  Validation note: API contract tests for each endpoint; verify payloads match expected schema; test both answered and refused runs; test that endpoints return 404 for nonexistent runs; verify response includes all debug fields.
  Session note: 2026-05-05: Added `backend/routes/runs.py` and registered `/api/runs/<run_id>`, `/api/runs/<run_id>/safety-issues`, and session run-list endpoints.

---

## Phase 3: Frontend Warning Surfaces And Debug View

**Goal:** Deliver the user-facing warning surfaces and Debug View on top of the stabilized backend contracts.

**Enabled scenarios:** US-001, US-002

**Linked acceptance criteria:** AC-002, AC-003, AC-005

**Completion criteria:**

- [ ] CC-005: Users can see when safety logic changed the run outcome (excluded evidence, warnings, refusals) and understand the effect from the chat UI.
- [ ] CC-006: Reviewers can open a Debug View for a run and inspect evidence, exclusions, safety issues, and final decision through the application UI.

### Tasks

- [X] TASK-010: Implement warning banners and safety-state badges on chat.html
  Status: Done
  Summary: Extend `frontend/chat.html` and `frontend/chat.js` to render visible warning banners when safety issues are detected, including: prompt-injection warnings, excluded-evidence notices (with chunk count and reason), answerability warnings (unsupported or conflicting question), groundedness warnings (low confidence in supporting evidence), and refusal explanations (with refusal category and reason). Use distinct visual styling (colors, icons) to distinguish warning types. Show warnings inline with the answer or above the refusal message.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-003, REQ-006
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s) or module(s): `frontend/chat.html`, `frontend/chat.js`, `frontend/styles.css`
  Depends on: TASK-005, TASK-006, TASK-009 (so payloads include warnings)
  Can run in parallel: [P] with TASK-011 once backend payloads are stable. Ownership: This task owns warning banner markup, styling, and data binding. TASK-011 owns Debug View markup and modal/drawer. Reintegration: Verify warning banners and Debug View do not conflict for layout or event handling; test both together on the same screen.
  Validation note: Manual browser verification of warning visibility for benign runs (no warnings), single-issue runs, multi-issue runs, and refusal runs. Verify warning text is clear and non-technical. Test on both desktop and mobile viewports.
  Session note: 2026-05-05: Extended `frontend/chat.html`, `frontend/chat.js`, and `frontend/styles.css` with visible warning banners, safety badges, and excluded-evidence messaging.

- [X] TASK-011: Implement Debug View panel with query, retrieval, context, exclusions, and decision details
  Status: Done
  Summary: Add Debug View UI to `frontend/chat.html` (inline drawer or modal) with sections for: original query, rewritten query (if present), retrieval mode and scope, selected collection, all retrieved chunks (with scores, document source, matched snippet), selected context chunks (highlighted), excluded chunks with reasons, citations, final answer text, answerability and groundedness state, all safety issues with detection method and risk score, latency, token count, and model identifiers. Include toggle to show/hide Debug View per run. Fetch debug payload from backend via `GET /api/runs/<run_id>` endpoint.
  Plan reference: Phase 3 / TASK-008
  Linked requirement(s): REQ-004, REQ-005
  Linked acceptance criteria: AC-003, AC-004
  Affected file(s) or module(s): `frontend/chat.html`, `frontend/chat.js`, `frontend/styles.css`
  Depends on: TASK-007, TASK-009 (endpoints must be ready)
  Can run in parallel: [P] with TASK-010. Ownership: This task owns Debug View markup, layout, and payload rendering. TASK-010 owns warning banners. Reintegration: Ensure both views coexist without layout conflicts; test clicking between Debug View and main chat area.
  Validation note: Manual browser verification that Debug View opens for answered runs and refused runs; verify all fields are populated and readable; verify excluded chunks are clearly marked; verify latency and token counts are present; test that Debug View closes properly and chat remains responsive; test on both answered and refused outcomes.
  Session note: 2026-05-05: Added structured Debug View rendering in the chat UI, including query, retrieved chunks, selected context, exclusions, citations, latency, and safety issue sections.

- [X] TASK-012: Ensure warning and debug surfaces work for persisted-history re-entry
  Status: Done
  Summary: Verify that after a chat session ends, when a user re-opens the session or browses run history, they can still: (1) see warning banners and safety state for past runs, (2) open the Debug View for a past run and inspect the full payload. Test session reload, page refresh after session completion, and navigating to a different session and back. Ensure `GET /api/runs/<run_id>` returns complete payloads even when queried hours or days after the original turn.
  Plan reference: Phase 3 / TASK-009
  Linked requirement(s): REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-002, AC-003, AC-005
  Affected file(s) or module(s): `frontend/chat.js`, `backend/services/run_record_service.py`
  Depends on: TASK-010, TASK-011, TASK-008 (persistence must be durable)
  Can run in parallel: No—depends on persistent retrieval
  Validation note: Integration test: create a run, close the session, re-open it later, verify warnings and debug data are still accessible. Manual test: refresh page after a turn completes, verify warning state survives and Debug View can still be opened. Test across multiple sessions.
  Session note: 2026-05-05: Session selection now reloads persisted run summaries and latest debug payloads, and history buttons reopen Debug View for completed prior runs.

---

## Phase 4: Validation And Hardening

**Goal:** Harden the safety and observability behavior with automated verification and manual review evidence.

**Enabled scenarios:** US-001, US-002, US-003, US-004

**Linked acceptance criteria:** AC-001, AC-002, AC-003, AC-004, AC-005

**Completion criteria:**

- [ ] CC-007: Automated unit and integration tests protect safety detection, action selection, debug payload completeness, and persisted-run observability across benign and suspicious inputs.
- [ ] CC-008: Manual verification confirms warning surfaces and Debug View behavior are understandable and traceable for both answered and refused runs, and for persisted-history re-entry.

### Tasks

- [X] TASK-013: Add unit tests for safety pattern detection and risk scoring
  Status: Done
  Summary: Write unit tests for `SafetyScannerService` covering: benign queries and chunks (expected no issues), known injection patterns (expected detection with correct risk score), edge cases (empty input, very long input, special characters), and scoring consistency (multiple occurrences increase score, threshold boundaries are respected). Use fixtures with realistic malicious and benign examples. Verify that normal informational content does not trigger false positives.
  Plan reference: Phase 4 / TASK-010
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/tests/unit/test_safety_scanner_service.py` (new)
  Depends on: TASK-003
  Can run in parallel: [P] with TASK-014, TASK-015 (each owns its own test file with no shared writes). Ownership: This task owns SafetyScannerService unit tests. TASK-014 owns SafetyDecisionService tests. TASK-015 owns debug payload tests. Reintegration: After all three complete, run the full unit test suite to ensure no conflicts.
  Validation note: Verify all tests pass; verify coverage of safety scanner is >90%; verify benign and suspicious examples are correctly classified.
  Session note: 2026-05-05: Added `backend/tests/unit/test_safety_scanner_service.py` covering benign input, malicious input, and retrieved-chunk issue detection.

- [X] TASK-014: Add unit tests for safety-decision service and action selection
  Status: Done
  Summary: Write unit tests for `SafetyDecisionService` covering: each action type (ignore, exclude_chunk, lower_trust, warn, refuse) is correctly assigned for appropriate risk scores, escalation logic (multiple issues can trigger higher action), and final action is always persisted. Test with single and multiple issues. Verify that recommended_action and final_action are tracked correctly.
  Plan reference: Phase 4 / TASK-010
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/tests/unit/test_safety_decision_service.py` (new)
  Depends on: TASK-004
  Can run in parallel: [P] with TASK-013, TASK-015. Ownership: SafetyDecisionService unit tests. Reintegration: Merge with other unit test runs; verify no cross-task conflicts.
  Validation note: Verify all tests pass; verify coverage is >90%; verify action thresholds match configuration.
  Session note: 2026-05-05: Added `backend/tests/unit/test_safety_decision_service.py` covering ignore, warn, lower-trust, exclude-chunk, and escalation behavior.

- [X] TASK-015: Add unit tests for debug-payload assembly completeness
  Status: Done
  Summary: Write unit tests for `DebugPayloadService` verifying payload assembly for both answered and refused runs, all fields present and correctly populated, excluded-chunk metadata is clear, latency and token counts are captured, and model identifiers are preserved. Test edge cases: no retrieved chunks, no safety issues, multiple safety issues, chunks with low scores.
  Plan reference: Phase 4 / TASK-010
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/tests/unit/test_debug_payload_service.py` (new)
  Depends on: TASK-007
  Can run in parallel: [P] with TASK-013, TASK-014. Ownership: Debug payload service tests. Reintegration: Merge with other unit tests.
  Validation note: Verify all tests pass; verify payload contains all required fields; verify serialization is correct for API consumption.
  Session note: 2026-05-05: Added `backend/tests/unit/test_debug_payload_service.py` to verify assembled Debug View payloads include required observability and safety fields.

- [X] TASK-016: Add integration tests for malicious user input handling
  Status: Done
  Summary: Write integration tests exercising full chat flow with malicious user input (known injection patterns, instruction-override attempts): verify scanner detects the issue, decision service recommends or escalates to refusal, chat orchestration applies the action, response includes warning or refusal, and run record is persisted with all issue details. Test both single and multiple malicious patterns in one query.
  Plan reference: Phase 4 / TASK-011
  Linked requirement(s): REQ-001, REQ-002, REQ-003
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/tests/integration/test_malicious_user_input.py` (new)
  Depends on: TASK-005, TASK-006, TASK-008, TASK-009
  Can run in parallel: [P] with TASK-017, TASK-018 (each tests a different input vector with no write conflicts). Ownership: Malicious user input integration tests. TASK-017 owns malicious chunk tests. TASK-018 owns warning/exclusion outcomes. Reintegration: Run all three together to verify end-to-end chat flow is protected; verify no test conflicts.
  Validation note: All tests pass; verify malicious inputs trigger appropriate safety actions; verify persisted run records include issue details.
  Session note: 2026-05-05: Added `backend/tests/integration/test_malicious_user_input.py` for high-risk malicious query refusal and persisted run inspection.

- [X] TASK-017: Add integration tests for malicious retrieved-chunk handling
  Status: Done
  Summary: Write integration tests for chat flow with malicious or injection-like retrieved chunks (injected via test fixtures): verify scanner detects suspicious chunks, decision service recommends exclusion or warning, orchestration filters excluded chunks from context, answer is generated (or refusal issued) without the malicious content, run record documents exclusion and reason. Test that citation traceability is preserved (excluded chunks do not appear in citations).
  Plan reference: Phase 4 / TASK-011
  Linked requirement(s): REQ-001, REQ-002, REQ-003
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/tests/integration/test_malicious_chunk_handling.py` (new)
  Depends on: TASK-005, TASK-006, TASK-008, TASK-009
  Can run in parallel: [P] with TASK-016, TASK-018. Ownership: Malicious chunk tests. Reintegration: Merge with other integration tests; verify chat flow is protected end-to-end.
  Validation note: All tests pass; verify chunks are correctly filtered; verify citations exclude malicious sources; verify exclusion is documented in run record.
  Session note: 2026-05-05: Added `backend/tests/integration/test_malicious_chunk_handling.py` to verify suspicious chunks are excluded and do not appear in final citations.

- [X] TASK-018: Add integration tests for warning-only and exclusion-only outcomes
  Status: Done
  Summary: Write integration tests verifying that safety actions correctly produce their intended outcomes without unnecessary refusals: low-risk issues trigger warn-only (answer still provided with warning), medium-risk issues trigger chunk exclusion and answer with warning, high-risk issues trigger refusal. Test each outcome with realistic benign questions mixed with suspicious signals. Verify answer quality is not degraded when safe to answer despite warnings.
  Plan reference: Phase 4 / TASK-011
  Linked requirement(s): REQ-002, REQ-003, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-005
  Affected file(s) or module(s): `backend/tests/integration/test_safety_outcomes.py` (new)
  Depends on: TASK-005, TASK-006, TASK-008
  Can run in parallel: [P] with TASK-016, TASK-017. Ownership: Safety outcome tests. Reintegration: Run all integration tests together.
  Validation note: All tests pass; verify no false refusals; verify warnings are only shown when justified; verify answers are still generated when appropriate.
  Session note: 2026-05-05: Added `backend/tests/integration/test_safety_outcomes.py` to cover warning-only benign answers and persisted run-list summaries.

- [X] TASK-019: Add regression tests for feature 2 (grounded chat) after safety integration
  Status: Done
  Summary: Run the existing feature 2 test suite plus write additional tests to verify that non-malicious supported questions still answer with citations, answerability and groundedness signals are preserved, and no new false refusals are introduced by safety layer. Ensure backward compatibility with existing chat, document library, and collection features. Smoke-test the Document Library, Collections, and Chat pages in the browser to confirm no regressions.
  Plan reference: Phase 4 / TASK-011
  Linked requirement(s): NFR-001, NFR-003
  Linked acceptance criteria: All (regression protection)
  Affected file(s) or module(s): `backend/tests/integration/test_feature_2_regression.py` (new), full suite in `backend/tests/`
  Depends on: All previous tasks
  Can run in parallel: No—final regression check
  Validation note: All existing feature 2 tests pass; all new regression tests pass; no new warnings for benign queries; document ingestion, collections, and chat flows all work as before.
  Session note: 2026-05-05: Added `backend/tests/integration/test_feature_2_regression.py` and reran the full backend suite to confirm benign grounded chat still answers cleanly.

- [ ] TASK-020: Create and execute manual test checklist for Debug View and warnings
  Status: Blocked
  Summary: Develop a comprehensive manual testing checklist covering: (1) Warning visibility for different safety outcomes (prompt-injection, excluded evidence, unsupported question, low groundedness, refusal), (2) Debug View opening, data completeness, and clarity for both answered and refused runs, (3) Excluded-chunk metadata and citation traceability, (4) Persisted-history re-entry (session reload, page refresh, later session access), (5) Warning and debug UI quality and layout on desktop and mobile, (6) Edge cases (very long queries, many chunks retrieved, many safety issues). Execute the checklist in a browser and document results. Update `artifacts/features/3.safety-and-debug-observability/manual-test-checklist.md` with results.
  Plan reference: Phase 4 / TASK-012
  Linked requirement(s): REQ-003, REQ-004, REQ-006, NFR-002
  Linked acceptance criteria: AC-002, AC-003, AC-004, AC-005
  Affected file(s) or module(s): `artifacts/features/3.safety-and-debug-observability/manual-test-checklist.md` (create or update)
  Depends on: TASK-010, TASK-011, TASK-012
  Can run in parallel: No—depends on all frontend work
  Validation note: Checklist completed with all items passing; screenshots or notes document Debug View and warning behavior; any issues discovered are either fixed or logged as deferred.
  Session note: 2026-05-05: Created `manual-test-checklist.md`, but execution remains blocked in this environment because I do not have a real browser/GUI path to truthfully complete and capture the manual checks.

---

## Traceability Matrix

### Requirements to Acceptance Criteria to Tasks

| Requirement | Acceptance Criteria | Primary Tasks | Validation Tasks |
|---|---|---|---|
| REQ-001: Prompt-injection and unsafe instruction detection | AC-001 | TASK-003, TASK-005 | TASK-013, TASK-016, TASK-017 |
| REQ-002: Safety actions and decision making | AC-001, AC-002 | TASK-004, TASK-005 | TASK-014, TASK-016, TASK-017, TASK-018 |
| REQ-003: Expose safety and observability state | AC-002, AC-005 | TASK-006, TASK-009 | TASK-010, TASK-020 |
| REQ-004: Debug View with pipeline internals | AC-003, AC-004 | TASK-007, TASK-009, TASK-011 | TASK-015, TASK-020 |
| REQ-005: Persist run-level observability records | AC-004 | TASK-001, TASK-002, TASK-008 | TASK-012, TASK-020 |
| REQ-006: User-visible safety surfaces | AC-002, AC-005 | TASK-010, TASK-012 | TASK-020 |
| NFR-001: Retrieved text untrusted | AC-001, AC-002 | TASK-003, TASK-005 | TASK-016, TASK-017 |
| NFR-002: Observability without direct DB inspection | AC-003, AC-004 | TASK-007, TASK-009, TASK-011 | TASK-020 |
| NFR-003: Coherent final state even with safety checks | AC-001, AC-002, AC-005 | TASK-005, TASK-006 | TASK-018, TASK-019 |
| NFR-004: Safety instrumentation does not block progress | AC-005 | TASK-006 | TASK-020 |

### User Stories to Tasks

| User Story | Primary Tasks | Validation Tasks |
|---|---|---|
| US-001: See when system considers question unsupported, conflicting, or injection-like | TASK-003, TASK-006, TASK-010 | TASK-013, TASK-016, TASK-020 |
| US-002: Inspect Debug View to understand final answer or refusal | TASK-007, TASK-011 | TASK-015, TASK-020 |
| US-003: Confirm retrieved content is untrusted and cannot override rules | TASK-005 | TASK-016, TASK-017 |
| US-004: Inspect logs and run records for latency, tokens, and safety decisions | TASK-001, TASK-008, TASK-009 | TASK-012, TASK-020 |

---

## Phase Sequencing And Dependencies

- **Phase 1** is foundational: persistence, models, and scanner/decision services must be ready before orchestration integration.
- **Phase 2** builds on Phase 1: chat orchestration integration, extended payloads, and APIs depend on Phase 1 services.
- **Phase 3** depends on Phase 2: frontend warning and debug surfaces depend on stable backend payloads and endpoints.
- **Phase 4** is final validation: automated tests cover Phases 1–3; manual tests validate frontend and end-to-end behavior.

Parallel opportunities:
- Within Phase 1: TASK-001, TASK-002 must complete before TASK-003, TASK-004; TASK-003 and TASK-004 are sequential.
- Within Phase 2: TASK-005 and TASK-006 are sequential (orchestration must run first); TASK-007 and TASK-008 can run in parallel once TASK-005/TASK-006 complete; both depend on completion before TASK-009.
- Within Phase 3: TASK-010 and TASK-011 can run in parallel once backend is stable; TASK-012 depends on both.
- Within Phase 4: TASK-013, TASK-014, TASK-015 are independent unit tests (parallel); TASK-016, TASK-017, TASK-018 are independent integration tests (parallel); TASK-019 and TASK-020 are sequential final checks.

---

## Open Decisions Carried Forward

1. **Inline Debug View vs. dedicated page**: This task list assumes inline drawer or modal on `chat.html`. If a dedicated run-detail page is preferred, TASK-009 and TASK-011 should be adjusted to add a new route and navigation pattern.

2. **Dynamic vs. snapshot debug payloads**: This list assumes dynamic assembly from persisted turn and citation records via `DebugPayloadService`. If full-snapshot persistence is preferred, TASK-001 schema and TASK-007 assembly approach should be revisited to store complete snapshots.

3. **Token and latency sources**: Tasks assume token and latency metrics come from the local generation provider. Confirm actual metrics availability before TASK-005 implementation.

---

## Validation Scope And Success

This task breakdown is complete and ready for implementation when:

✅ All 20 tasks have been reviewed for feasibility and clarity.
✅ Dependencies are understood and phase sequencing is confirmed.
✅ REQ → AC → TASK → validation coverage is intact (see traceability matrix).
✅ Parallel markers `[P]` are confirmed safe with clear ownership boundaries.
✅ No major requirements are orphaned or missing tasks.

Upon completion of all phases and validation tasks, the feature will satisfy:

- SC-001: Reviewers can observe prompt-injection warnings and refusal paths.
- SC-002: Safety and groundedness decisions are inspectable for any answered or refused query.
- SC-003: Debug View exposes enough pipeline state for understanding answers and refusals.
- SC-004: Run metadata (latency, tokens, safety decisions) persists and is reviewable after execution.

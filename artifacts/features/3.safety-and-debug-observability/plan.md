# Implementation Plan

## Metadata

- Feature name: Safety And Debug Observability
- Related spec: `artifacts/features/3.safety-and-debug-observability/spec.md`
- Related requirements review: None present in workspace
- Related design: None
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-05

## Plan Summary

Implement a safety and debug-observability slice on top of the grounded chat flow that already exists in this repo. The backend will add prompt-injection scanning, explicit safety decisions, run-level observability records, and debug payload assembly around the existing retrieval and answer pipeline. The frontend will extend the current static HTML, CSS, and JavaScript chat client with visible safety warnings, answerability and groundedness state, and a Debug View that lets reviewers inspect the run without reading raw logs or the database directly.

## Constitution Alignment

- Constitutional rule or principle: Frontend screens in this repo should be JavaScript clients that call REST API endpoints; frontend and backend must stay separated.
  Planning implication: Safety warnings, debug state, and run inspection will be exposed through JSON APIs in `backend/` and rendered by static `frontend/` pages or panels. No server-rendered data views.
- Constitutional rule or principle: Touch only what the request requires.
  Planning implication: This plan covers prompt-injection handling, reviewer-visible safety decisions, persisted run records, and Debug View surfaces only. It does not pull forward evaluation dashboards, settings management, or advanced retrieval features beyond making them observable when present.
- Constitutional rule or principle: For Python, always use virtualenv.
  Planning implication: Backend implementation, migrations, and verification must run inside the project virtual environment.

## Execution Context

- Design reference: None
- Relevant repository patterns for execution: Existing Flask app with blueprint routes, service modules, SQLite-backed persistence, local Chroma usage for retrieval, and static frontend pages under `frontend/` served by Flask.
- Brownfield execution constraints or greenfield assumptions: Brownfield extension of feature 2. Chat sessions, turns, citations, and answerability already exist and must remain compatible while gaining safety and observability layers.
- Unchanged behavior that must be preserved during delivery: The current ingestion, collections, and grounded chat flows must continue to work. Safety instrumentation must not break non-malicious supported questions or remove citation traceability.

## Technical Approach

- Chosen approach: Add a safety-analysis layer around the chat orchestration pipeline that scans user input and retrieved chunks, produces structured issue records, applies explicit safety actions, and persists a run-level record with both user-facing and debug-facing fields. Extend the chat UI with visible safety notices and a Debug View panel fed by dedicated REST endpoints.
- Architectural or integration shape: The backend will separate safety scanning, safety decisioning, debug payload assembly, and run-record persistence into focused services. Existing chat orchestration will call those services before finalizing answers or refusals. SQLite will store run records, safety issues, and debug snapshots keyed to chat turns. The frontend will render the same backend-produced debug and safety payloads rather than reconstructing pipeline state in JavaScript.
- Key interfaces or contracts: Safety-scan result payloads, per-run safety issue records, final run-observability record payloads, debug-view endpoint(s), and chat response objects extended with groundedness state, answerability state, warning summaries, excluded-evidence notices, and persisted run identifiers.
- Operational considerations: The first pass should be local-first and deterministic, with rule-based prompt-injection detection as the baseline. The contracts must still preserve detection method, score, matched rule, recommended action, final action, and optional model-based signals so later features can extend the same schema.

## Decision Rationale

- Why this approach was selected: It matches the repo’s existing separation of backend logic and static frontend clients, keeps safety decisions centralized in Python where evidence and turn state already live, and gives the UI stable reviewer-facing payloads instead of leaking raw logs into the browser.
- Existing patterns reused: Flask blueprints, service-oriented backend modules, SQLite local persistence, chat session and turn records, and static HTML/CSS/JavaScript clients using `fetch`.
- Alternatives considered: Console-log-only observability, a separate admin-only debug app, storing debug state only in browser memory, or postponing persistence until the evaluation feature.
- Why rejected: Console logs do not satisfy the reviewer-facing requirement. A separate app would duplicate navigation and state. Browser-only debug state would disappear with the session and fail persisted-run requirements. Deferring persistence would block later comparison and audit features.

## Requirements And Constraints

- REQ-001:
  Implementation note: Add scanning for prompt-injection-like or unsafe instruction patterns across both user queries and retrieved chunks, and preserve structured detection details for review.
  Planned validation: Unit tests for benign versus suspicious inputs and integration tests that exercise malicious retrieved content and malicious user prompts.
  Linked scenario or outcome: US-001, US-003, SC-001, SC-002
- REQ-002:
  Implementation note: Add explicit safety actions such as ignore, exclude chunk, lower trust, continue with warning, and refuse, and persist both recommended and final system actions per issue.
  Planned validation: Integration tests covering exclusion, warning-only, and refusal outcomes with persisted issue payload inspection.
  Linked scenario or outcome: US-001, US-003, SC-001, SC-002
- REQ-003:
  Implementation note: Extend answered and refused run payloads with answerability state, groundedness state, prompt-injection result, risk score when available, refusal cause, and supporting safety signals.
  Planned validation: API contract tests for one answered run and one refused run plus frontend verification that those states are visible.
  Linked scenario or outcome: US-001, US-002, SC-002, SC-003
- REQ-004:
  Implementation note: Build a Debug View payload that includes query, scope, retrieval mode, retrieved chunks, selected context, exclusions, safety issues, answerability state, groundedness state, citations, final answer or refusal, latency, and token usage.
  Planned validation: Integration tests for debug payload completeness and manual inspection of the Debug View in the browser.
  Linked scenario or outcome: US-002, US-004, SC-003, SC-004
- REQ-005:
  Implementation note: Persist durable run records and safety records keyed to chat turn or run ID, including model and configuration identifiers needed for later explanation.
  Planned validation: Persistence tests that create a run, reload it after the session call completes, and verify latency, token, citation, and safety fields remain available.
  Linked scenario or outcome: US-004, SC-004
- REQ-006:
  Implementation note: Surface user-visible warnings and refusal explanations in the chat UI when excluded evidence, suspicious content, or high safety risk materially changes the run outcome.
  Planned validation: Manual browser verification of warning banners, refusal messaging, and outcome summaries plus frontend contract checks.
  Linked scenario or outcome: US-001, US-002, SC-001, SC-002, SC-003
- NFR-001:
  Implementation note: Retrieved text must remain untrusted throughout the pipeline and must never override application rules or suppress citations and refusals.
- NFR-002:
  Implementation note: Debug and safety records must be understandable through application screens and APIs without requiring direct SQLite inspection.
- NFR-003:
  Implementation note: Every run must still end in a coherent answer, refusal, cancellation, or error state even when safety exclusions or warnings trigger.
- NFR-004:
  Implementation note: Safety instrumentation must fit within the existing progress and chat-response flow rather than blocking all user feedback until raw logs are assembled.

## Impacted Areas

- Services or modules: New safety scanning service, safety decision service, debug payload builder, and run-record persistence helpers; existing chat orchestration service will be extended to call them.
- APIs or interfaces: Extended chat ask and streaming payloads, debug-run retrieval endpoints, run-record listing or detail endpoints, and any issue-detail endpoint if needed for deeper inspection.
- Data model or storage: SQLite additions for run records, safety issues, debug snapshots, exclusion metadata, latency and token counters, and model or config identifiers.
- UI or UX: Extend `frontend/chat.html` and `frontend/chat.js` with warning banners, answerability and groundedness badges, a debug toggle, and a Debug View or drawer for per-run inspection.
- Infrastructure or deployment: Local Flask runtime remains the host. Persistence remains local SQLite. No external observability stack is required in this slice.
- Documentation: Manual verification checklist and startup notes for safety-debug testing, including sample prompt-injection scenarios.

## Affected Domains And Integration Boundaries

- Domain or subsystem: Chat orchestration
  Why it matters: Safety decisions must plug into the same turn lifecycle that already owns retrieval, answerability, and final answer or refusal completion.
- Domain or subsystem: Retrieval and evidence handling
  Why it matters: Suspicious chunks may need to be excluded, down-ranked, or warned on before context packing and answer generation proceed.
- Domain or subsystem: Run persistence and observability
  Why it matters: Later features depend on durable run records with model, latency, token, and safety fields.
- Domain or subsystem: Frontend debug and warning surfaces
  Why it matters: Reviewer trust depends on making the pipeline state visible without leaking implementation-only internals or forcing direct DB inspection.
- Integration boundary or touchpoint: Existing chat session and turn records from feature 2
  Why it matters: Run records and debug views should attach to the same turn IDs rather than inventing a disconnected identity model.
- Integration boundary or touchpoint: Existing citation and answerability payloads
  Why it matters: Safety and debug layers should extend those payloads, not replace them, so feature 2 consumers remain compatible.
- Integration boundary or touchpoint: Future advanced retrieval features
  Why it matters: The debug schema must leave room for query rewrites, reranking traces, and routing decisions without requiring a second redesign later.

## Protected Behavior

- Behavior that must not regress: Supported grounded questions should still answer with citations when no meaningful safety issue is present.
  Protection approach: Keep safety scanning additive and verify benign runs still complete with the expected citations and answer payload shape.
- Behavior that must not regress: Refusals must remain explicit terminal outcomes rather than generic backend failures.
  Protection approach: Route safety-based refusal through persisted refusal categories and terminal-state handling already established in feature 2.
- Behavior that must not regress: Citation traceability must remain tied to stored chunks even when chunks are excluded or warned on.
  Protection approach: Preserve excluded-chunk metadata separately and keep final citations sourced only from accepted stored evidence.
- Behavior that must not regress: Existing ingestion and collections pages must continue to work.
  Protection approach: Keep new schema additive, avoid touching feature 1 routes unnecessarily, and rerun the backend suite after implementation.

## Affected Files

- FILE-001 Path: `backend/persistence/schema.py`
  Reason for change: Add additive schema for run records, safety issues, debug snapshots, and observability metadata.
- FILE-002 Path: `backend/services/`
  Reason for change: Add safety scanning, safety action selection, debug payload assembly, and run-record persistence services; extend chat orchestration to integrate them.
- FILE-003 Path: `backend/routes/`
  Reason for change: Extend chat-response payloads and add debug or run-observability endpoints.
- FILE-004 Path: `backend/models/`
  Reason for change: Add structured models for safety issue records and run-observability records when useful for JSON serialization and persistence clarity.
- FILE-005 Path: `frontend/chat.html`, `frontend/chat.js`, `frontend/styles.css`
  Reason for change: Add user-visible warnings, groundedness or answerability labels, debug toggle, and Debug View rendering.
- FILE-006 Path: `backend/tests/`
  Reason for change: Add unit and integration coverage for detection, decisions, persistence, and reviewer-visible debug payloads.
- FILE-007 Path: `backend/config.py`
  Reason for change: Add rule thresholds, safety action defaults, and any toggles needed for baseline safety instrumentation.

## Dependencies

- DEP-001 Internal dependency: Completed grounded chat flow from feature 2
  Why it matters: Safety and debug instrumentation depend on real turns, retrieval results, answerability decisions, and citations.
- DEP-002 Internal dependency: Existing Flask app and static frontend serving pattern
  Why it matters: The feature should extend the current app shape rather than invent a second UI delivery model.
- DEP-003 External dependency: SQLite local persistence
  Why it matters: Run records and safety issue payloads must persist after the chat response returns.
- DEP-004 Internal dependency: Existing retrieval and citation metadata
  Why it matters: Debug payloads and excluded-evidence warnings depend on stable chunk, citation, and score fields.
- DEP-005 Optional future dependency: Model-based safety classification
  Why it matters: The first implementation can be rule-first, but the schema must preserve detection method and score fields so model-based classification can be layered in later.

## Implementation Prerequisites

- PREREQ-001: Feature 2 backend and chat UI foundations must be in place and passing tests, because this feature instruments that flow rather than replacing it.
- PREREQ-002: The project virtual environment must be active before backend implementation or verification runs.
- PREREQ-003: Confirm the first-pass safety detector is rule-first and local, so the implementation does not guess at unavailable external classifiers.
- PREREQ-004: Confirm whether the Debug View should live inline on `chat.html` or as a dedicated run-detail page before task generation, because both are plausible and affect file scope.

## Implementation Phases

### Phase 1

Goal:
Establish additive persistence and backend safety-analysis foundations around existing chat turns.

Enabled user scenario(s) or outcome(s):
US-001, US-003, US-004, SC-001, SC-002, SC-004

Tasks:

- TASK-001:
  Description: Add SQLite tables and persistence helpers for run records, safety issues, debug snapshots, latency, token, and model metadata linked to existing chat turns.
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/persistence/schema.py`, `backend/models/`, `backend/services/`
- TASK-002:
  Description: Implement rule-based prompt-injection and unsafe-instruction scanning for user queries and retrieved chunks, with structured issue payloads and risk scoring.
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001
  Affected file(s): `backend/services/`, `backend/config.py`
- TASK-003:
  Description: Implement safety decisioning that converts detected issues into explicit actions such as ignore, exclude chunk, warn, lower trust, or refuse, and persists both recommended and final decisions.
  Linked requirement(s): REQ-002, REQ-003
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s): `backend/services/`

Completion criteria:

- CC-001: The backend can persist run-level safety and observability records linked to chat turns without breaking the existing chat schema.
- CC-002: User input and retrieved chunks can be scanned, classified, and assigned explicit safety actions with structured issue payloads.

### Phase 2

Goal:
Integrate safety decisions and observability capture into the chat orchestration pipeline and expose stable debug APIs.

Enabled user scenario(s) or outcome(s):
US-001, US-002, US-003, US-004, SC-001, SC-002, SC-003, SC-004

Tasks:

- TASK-004:
  Description: Extend chat orchestration so safety scanning runs before answer finalization, suspicious chunks can be excluded or down-weighted, and final answer or refusal payloads include safety, groundedness, and answerability state.
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-005
  Affected file(s): `backend/services/`
- TASK-005:
  Description: Build a debug-payload assembly layer that captures query context, retrieval details, selected context, excluded evidence, citations, refusal details, latency, token usage, and model identifiers for each run.
  Linked requirement(s): REQ-004, REQ-005
  Linked acceptance criteria: AC-003, AC-004
  Affected file(s): `backend/services/`, `backend/models/`
- TASK-006:
  Description: Extend chat endpoints and add debug or run-record endpoints so the frontend can fetch run details, safety issues, and persisted observability state after completion.
  Linked requirement(s): REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-002, AC-003, AC-004
  Affected file(s): `backend/routes/`

Completion criteria:

- CC-003: Completed answered and refused runs include reviewer-visible safety, groundedness, and answerability outcomes.
- CC-004: Debug and run-record endpoints expose enough pipeline detail to explain a run without direct database inspection.

### Phase 3

Goal:
Deliver the user-facing warning surfaces and Debug View on top of the stabilized backend contracts.

Enabled user scenario(s) or outcome(s):
US-001, US-002, US-003, SC-001, SC-002, SC-003

Tasks:

- TASK-007:
  Description: Extend the chat page UI with warning banners, answerability and groundedness badges, excluded-evidence notices, and refusal summaries that explain the effect on the answer flow.
  Linked requirement(s): REQ-003, REQ-006
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s): `frontend/chat.html`, `frontend/chat.js`, `frontend/styles.css`
- TASK-008:
  Description: Add Debug View UI and JavaScript data loading for query, retrieval, selected context, excluded chunks, safety issues, citations, final decision, latency, token usage, and model metadata.
  Linked requirement(s): REQ-004, REQ-005
  Linked acceptance criteria: AC-003, AC-004
  Affected file(s): `frontend/chat.html`, `frontend/chat.js`, `frontend/styles.css`
- TASK-009:
  Description: Ensure warning and debug surfaces work for both answered and refused runs, including persisted-history re-entry after the original turn completes.
  Linked requirement(s): REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-002, AC-003, AC-005
  Affected file(s): `frontend/chat.js`

Completion criteria:

- CC-005: Users can see when safety logic changed the run outcome and understand the effect on the answer flow from the chat UI.
- CC-006: Reviewers can open a Debug View for a run and inspect the evidence, exclusions, safety issues, and final decision through the app.

### Phase 4

Goal:
Harden the safety and observability behavior with automated verification and manual review evidence before closure.

Enabled user scenario(s) or outcome(s):
SC-001, SC-002, SC-003, SC-004

Tasks:

- TASK-010:
  Description: Add unit tests for safety pattern detection, risk scoring, action selection, and debug payload assembly.
  Linked requirement(s): REQ-001, REQ-002, REQ-004
  Linked acceptance criteria: AC-001, AC-003
  Affected file(s): `backend/tests/unit/`
- TASK-011:
  Description: Add integration tests for malicious user-input handling, malicious retrieved-chunk handling, warning-only outcomes, exclusion outcomes, safety-driven refusals, and persisted run-record retrieval.
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-004
  Affected file(s): `backend/tests/integration/`
- TASK-012:
  Description: Create and execute a manual browser checklist for Debug View, warning messaging, refused-run inspection, and post-session run-record review.
  Linked requirement(s): REQ-004, REQ-005, REQ-006
  Linked acceptance criteria: AC-003, AC-004, AC-005
  Affected file(s): `artifacts/features/3.safety-and-debug-observability/`

Completion criteria:

- CC-007: Automated checks protect safety detection, action selection, debug payload completeness, and persisted-run observability.
- CC-008: Manual verification confirms warning surfaces and Debug View behavior are understandable and traceable for both answered and refused runs.

## Validation Strategy

- Automated validation: Run the backend unit and integration suite in the project virtualenv, including new safety and debug tests plus the existing feature 1 and feature 2 regression coverage.
- Manual validation: Use a browser checklist to test malicious user prompts, malicious retrieved text, excluded-evidence warnings, Debug View inspection, and persisted run review after page reload or session switch.
- Regression validation: Re-run the full backend test suite and smoke-test the existing Document Library, Collections, and Grounded Chat pages after the safety-debug additions land.

## Rollout And Sequencing Notes

- Recommended implementation order: Start with persistence and scanner primitives, then integrate safety decisions into orchestration, then expose debug APIs, and only then wire the frontend warning and debug surfaces.
- Parallelization opportunities: Backend persistence and scanner work can proceed before frontend UI work. Frontend Debug View can begin once the debug payload contract is stable. Automated tests can be added incrementally per phase.
- Risk watch items during delivery: Avoid over-aggressive rules that convert normal questions into refusals; keep excluded-evidence details reviewable; do not let debug payload assembly drift from the actual executed pipeline state.

## Open Decisions To Carry Into Task Breakdown

- Decision needed: Inline Debug View on `chat.html` versus a dedicated run-detail page.
  Why it matters: It changes whether frontend work stays scoped to the existing chat screen or adds another route and navigation pattern.
- Decision needed: Whether the first pass should store full debug snapshots per run or assemble some debug fields dynamically from persisted turn and citation records.
  Why it matters: Snapshot persistence is simpler for review fidelity, but dynamic assembly reduces storage duplication.
- Decision needed: Exact token and latency field sources for the current local generation provider.
  Why it matters: The plan assumes those observability fields exist, but the first implementation may need fallback estimation for local deterministic generation.

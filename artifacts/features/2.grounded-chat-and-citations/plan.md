# Implementation Plan

## Metadata

- Feature name: Grounded Chat And Citations
- Related spec: `artifacts/features/2.grounded-chat-and-citations/spec.md`
- Related requirements review: None present in workspace
- Related design: None
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-04

## Plan Summary

Implement a local-first grounded chat slice on top of the completed ingestion and collection foundation using the existing Flask backend and static HTML, CSS, and JavaScript frontend pattern. The backend will add retrieval, answerability checks, citation assembly, chat session persistence, and streamed or non-streamed answer delivery. The frontend will add a dedicated chat screen that exposes scope, retrieval mode, visible generation states, cancellation, history, and citation inspection without leaving the app. Validation is phased so retrieval and refusal correctness are proven before the UI depends on them.

## Constitution Alignment

- Constitutional rule or principle: Frontend screens in this repo should be JavaScript clients that call REST API endpoints; frontend and backend must stay separated.
  Planning implication: The chat experience will live under `frontend/` as static HTML, CSS, and JavaScript that calls new backend REST endpoints. Retrieval, grounding, and chat-state logic stay in `backend/`.
- Constitutional rule or principle: Touch only what the request requires.
  Planning implication: This plan covers baseline grounded chat, retrieval-mode visibility, citations, refusals, conversation history, and progress or streaming controls only. It does not pull forward advanced routing, experiment dashboards, or later safety-debug features.
- Constitutional rule or principle: For Python, always use virtualenv.
  Planning implication: Backend implementation, local verification, and any model-provider setup must run inside the project virtual environment.

## Execution Context

- Design reference: None
- Relevant repository patterns for execution: Existing Flask app with blueprint-based routes, service modules, SQLite metadata persistence, local ChromaDB vector storage, and static frontend pages already served by Flask from `frontend/`.
- Brownfield execution constraints or greenfield assumptions: Brownfield extension of feature 1. Document, chunk, collection, and vector records already exist and must remain compatible. Chat behavior is new, but it must consume the existing ingestion data model instead of inventing a second storage path.
- Unchanged behavior that must be preserved during delivery: Ingestion, collections, duplicate handling, and document lifecycle APIs must continue to work unchanged. Citation records must always map to stored chunks and never to generated helper text.

## Technical Approach

- Chosen approach: Add a retrieval-and-answer pipeline in `backend/` that queries chunk and vector records by collection scope and retrieval mode, evaluates answerability, generates grounded answers with structured citation objects, and persists conversation turns. Expose both standard JSON answers and a streaming endpoint for chat progress. Build a dedicated chat UI in `frontend/` that consumes those APIs and renders message history, answer status, citations, and citation detail panels.
- Architectural or integration shape: The backend will separate chat-session persistence, retrieval orchestration, answerability evaluation, response generation, and citation formatting into focused services. SQLite will store chat sessions, messages, question parameters, answer status, and refusal metadata. Existing SQLite and ChromaDB document records remain the evidence source for retrieval and citation detail. The frontend will render chat state and citation detail from backend payloads rather than reconstructing them client-side.
- Key interfaces or contracts: Chat session CRUD endpoints, ask-question endpoint, streaming answer endpoint, cancel-generation endpoint, citation-detail payloads, retrieval-mode and scope selectors, and response objects that include answer status, refusal category when applicable, citation arrays, retrieval metadata, and visible progress states.
- Operational considerations: The first version should prefer a deterministic, local-friendly baseline that can run with the existing repo setup, but the API contracts must preserve explicit generation state, finalization, and cancellation boundaries so the implementation can evolve from synchronous generation to streaming without breaking the UI contract.

## Decision Rationale

- Why this approach was selected: It reuses the repo’s existing backend and frontend structure, consumes the evidence foundation already built in feature 1, and keeps grounding and citation correctness in the backend where evidence mapping can be controlled centrally.
- Existing patterns reused: Flask blueprint routes, service-oriented backend organization, SQLite-backed metadata, ChromaDB-backed vectors, frontend pages served by Flask, and static HTML, CSS, and JavaScript clients using `fetch`.
- Alternatives considered: A server-rendered chat UI; a frontend framework for streaming state; storing chat history only in browser memory; deferring streaming until later.
- Why rejected: Server-rendered UI conflicts with the repo pattern. A framework is unnecessary at the current repo scale. Browser-only history would not satisfy traceable chat-state requirements reliably. Deferring streaming entirely would leave REQ-006 under-specified for implementation and acceptance review.

## Requirements And Constraints

- REQ-001:
  Implementation note: Add chat session and message persistence plus a question workflow that records selected collection scope, selected retrieval mode, and conversation turn order before answer completion.
  Planned validation: Integration tests for session creation, follow-up turns, scope persistence, and retrieval-mode visibility; manual chat-history verification in the UI.
  Linked scenario or outcome: US-001, US-002, US-005, SC-001, SC-004
- REQ-002:
  Implementation note: Add baseline semantic, keyword or sparse, and hybrid retrieval modes over existing chunk records and preserve retrieval metadata per citation candidate.
  Planned validation: Retrieval-focused tests that compare returned evidence and verify mode visibility in API and UI payloads.
  Linked scenario or outcome: US-001, US-002, US-003, SC-001, SC-003
- REQ-003:
  Implementation note: Generate answers from retrieved evidence only and emit structured citation records with document title or ID, chunk ID, page or section, and source URL when available. Support inline citations and a reference-list payload even if the UI leads with one primary presentation.
  Planned validation: Answer and citation mapping tests plus manual citation-detail inspection.
  Linked scenario or outcome: US-001, US-003, SC-001, SC-003
- REQ-004:
  Implementation note: Implement explicit answerability evaluation before final answer completion, with refusal categories for no relevant evidence, low retrieval confidence, insufficient support, conflicting evidence, out of domain, and related groundedness causes supported by current signals.
  Planned validation: Tests for unsupported questions, weak-evidence questions, and conflict scenarios plus UI verification that refusal categories are visible.
  Linked scenario or outcome: US-004, SC-002
- REQ-005:
  Implementation note: Add citation detail retrieval that exposes source metadata, supporting snippet, retrieval mode, and scores available from the current retrieval pipeline.
  Planned validation: Citation-detail API tests and manual inspection from the chat UI.
  Linked scenario or outcome: US-003, SC-003
- REQ-006:
  Implementation note: Support non-streamed answers and a streamed-progress path with visible status states, cancellation, context packing, and final citation attachment only after answer finalization.
  Planned validation: Streaming and cancellation integration tests plus manual UI verification of progress states and final citation timing.
  Linked scenario or outcome: US-005, SC-004
- NFR-001:
  Implementation note: Every question path must end in a clear answer, refusal, cancellation, or error state stored in the session history.
- NFR-002:
  Implementation note: The UI must expose progress states from backend retrieval and generation rather than leaving the chat screen idle.
- NFR-003:
  Implementation note: Answer generation must treat retrieved evidence as the factual source of truth and never cite uncoupled model text.
- NFR-004:
  Implementation note: Citation details and refusal reasons must be rendered in readable UI panels, not hidden in logs or debug-only payloads.
- CON-001:
  Impact on plan: Automatic collection routing stays out of scope; collection selection remains explicit in the chat UI for this feature.
- CON-002:
  Impact on plan: Advanced query transformations and deep safety diagnostics remain deferred, so the baseline retrieval stack must be simple and inspectable.

## Impacted Areas

- Services or modules: New chat-session service, retrieval service, answerability service, response-generation service, citation-formatting service, and context-packing logic.
- APIs or interfaces: New chat session endpoints, ask-question endpoint, streaming answer endpoint, cancellation endpoint, citation-detail endpoint or embedded citation detail payload.
- Data model or storage: SQLite schema additions for chat sessions, chat messages, answer status, refusal category, retrieval metadata snapshots, and citation references. Existing `chunk_metadata`, `documents`, and collection records are read heavily by this feature.
- UI or UX: New chat page under `frontend/` with session history, question form, collection selector, retrieval-mode selector, status surface, answer panel, citations panel, and citation detail interaction.
- Infrastructure or deployment: Local runtime still served from Flask. Streaming transport should use a simple mechanism compatible with Flask in local development, such as line-delimited streamed HTTP or server-sent events if it fits the current stack.
- Documentation: Feature-specific startup notes, manual verification notes, and any environment assumptions for generation or model calls.

## Affected Domains And Integration Boundaries

- Domain or subsystem: Retrieval pipeline
  Why it matters: It determines which evidence is available to answerability and citation logic.
- Domain or subsystem: Answer generation and grounding
  Why it matters: It must bind answer text to retrieved evidence and avoid unsupported claims.
- Domain or subsystem: Chat session persistence
  Why it matters: It preserves conversation history, user selections, and terminal turn states.
- Domain or subsystem: Citation rendering and inspection
  Why it matters: It is the core reviewer-facing trust surface for this feature.
- Integration boundary or touchpoint: Existing chunk and collection storage from feature 1
  Why it matters: Retrieval and citations depend on chunk metadata quality and stable document identifiers.
- Integration boundary or touchpoint: Frontend-to-backend streamed answer contract
  Why it matters: The chat UI needs stable progress-state and completion semantics to avoid showing premature citations.
- Integration boundary or touchpoint: Generation provider abstraction
  Why it matters: The plan must keep the provider swappable without changing citation and refusal contracts, even if the first implementation uses a single configured provider.

## Protected Behavior

- Behavior that must not regress: Stored chunk and document metadata must remain the citation source of truth.
  Protection approach: Build citation records directly from stored chunk metadata and cover mapping in integration tests.
- Behavior that must not regress: Refusals must appear as explicit groundedness outcomes, not generic 500-like failures.
  Protection approach: Centralize answerability decisions in one backend layer and store a refusal category on each refused turn.
- Behavior that must not regress: Existing ingestion and collection screens must continue to function with the expanded backend schema.
  Protection approach: Keep new chat tables additive, preserve existing document and collection APIs, and run the existing backend test suite alongside new chat tests.
- Behavior that must not regress: Partial streamed output must not expose final citations before grounding checks complete.
  Protection approach: Separate progress events from final citation payload emission in the streaming contract and verify that citations appear only on final completion.

## Affected Files

- FILE-001 Path: `backend/persistence/schema.py`
  Reason for change: Add additive schema for chat sessions, chat messages, answer status, refusal category, and citation linkage.
- FILE-002 Path: `backend/services/`
  Reason for change: Add retrieval, answerability, generation, citation, and chat-session orchestration modules.
- FILE-003 Path: `backend/routes/`
  Reason for change: Add chat-facing REST and streaming endpoints plus cancellation handling.
- FILE-004 Path: `frontend/`
  Reason for change: Add a dedicated chat page and JavaScript client for asking questions, rendering progress, and inspecting citations.
- FILE-005 Path: `backend/tests/`
  Reason for change: Add unit, integration, and chat-flow validation coverage for retrieval, grounded answers, refusals, citations, streaming, and cancellation.
- FILE-006 Path: `backend/config.py`
  Reason for change: Add baseline retrieval and answerability defaults plus any generation-provider configuration the first implementation needs.

## Dependencies

- DEP-001 Internal dependency: Completed ingestion and collection foundation from feature 1
  Why it matters: Chat depends on stable document, collection, chunk, and vector records.
- DEP-002 Internal dependency: Existing Flask app and static-frontend serving pattern
  Why it matters: The feature must extend the current runtime shape rather than replace it.
- DEP-003 External dependency: ChromaDB local vector store
  Why it matters: Semantic and hybrid retrieval depend on vector lookups over ingested chunks.
- DEP-004 External dependency: SQLite local metadata store
  Why it matters: Chat sessions, turn state, and citation references require durable local persistence.
- DEP-005 External dependency: Generation-capable model provider
  Why it matters: Grounded answer generation and refusals need a provider interface, even if the first implementation uses a single configured model.

## Implementation Prerequisites

- PREREQ-001: Feature 1 backend and local persistence must be working, because chat depends on retrievable documents and chunks.
- PREREQ-002: The project virtual environment must be active before backend implementation or tests run.
- PREREQ-003: Decide the minimum first-pass generation provider contract before task generation so the service boundaries and tests do not guess.
- PREREQ-004: Confirm the streaming transport choice for local Flask delivery before implementation starts, because it shapes the frontend event-handling contract.

## Implementation Phases

### Phase 1

Goal:
Establish chat persistence, baseline retrieval contracts, and additive backend schema needed for grounded answer execution.

Enabled user scenario(s) or outcome(s):
US-001, US-002, US-005, SC-001, SC-004

Tasks:

- TASK-001:
  Description: Add SQLite tables and persistence helpers for chat sessions, chat messages, turn state, refusal category, retrieval metadata snapshots, and citation references.
  Linked requirement(s): REQ-001, REQ-006
  Linked acceptance criteria: AC-001, AC-006
  Affected file(s): `backend/persistence/schema.py`, new `backend/models/`, new `backend/services/`
- TASK-002:
  Description: Implement baseline retrieval modes over existing chunk records, including semantic, keyword or sparse, and hybrid retrieval outputs with collection-scope filtering and preserved chunk metadata.
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Affected file(s): `backend/services/`, `backend/config.py`

Completion criteria:

- CC-001: A chat session and its turns can be created and persisted with scope, retrieval mode, and terminal status metadata.
- CC-002: Retrieval returns ranked chunk candidates with the metadata required for answer generation and citations across single-collection and all-collections scopes.

### Phase 2

Goal:
Implement grounded answer generation, answerability or refusal logic, citation assembly, and cancellation-safe turn lifecycle behavior.

Enabled user scenario(s) or outcome(s):
US-001, US-003, US-004, US-005, SC-001, SC-002, SC-003, SC-004

Tasks:

- TASK-003:
  Description: Implement chat orchestration that runs retrieval, context packing, answerability checks, and grounded answer generation for a question turn.
  Linked requirement(s): REQ-001, REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-001, AC-003, AC-004, AC-006
  Affected file(s): `backend/services/`, `backend/config.py`
- TASK-004:
  Description: Implement refusal taxonomy, explicit refusal-state persistence, and final citation object generation that maps answer support to stored chunk metadata only.
  Linked requirement(s): REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-003, AC-004, AC-005
  Affected file(s): `backend/services/`, `backend/models/`
- TASK-005:
  Description: Expose non-streamed ask-question, streamed answer, cancel-generation, session-history, and citation-detail APIs with stable response contracts.
  Linked requirement(s): REQ-001, REQ-005, REQ-006
  Linked acceptance criteria: AC-001, AC-005, AC-006
  Affected file(s): `backend/routes/`

Completion criteria:

- CC-003: Supported questions can complete with grounded answers and structured citations.
- CC-004: Unsupported or weakly supported questions complete as refusals with visible reason categories rather than fabricated answers.
- CC-005: The backend exposes enough session, answer, citation, and progress metadata for the chat UI to render without reconstructing grounding logic client-side.

### Phase 3

Goal:
Deliver the chat UI and citation inspection workflow on top of the stabilized backend contracts.

Enabled user scenario(s) or outcome(s):
US-001, US-002, US-003, US-004, US-005, SC-001, SC-002, SC-003, SC-004

Tasks:

- TASK-006:
  Description: Build a dedicated grounded-chat page in HTML and CSS with question input, chat history, collection selector, retrieval-mode selector, streaming control, cancel action, status surface, answer panel, and citations panel.
  Linked requirement(s): REQ-001, REQ-006
  Linked acceptance criteria: AC-001, AC-006
  Affected file(s): `frontend/`
- TASK-007:
  Description: Implement frontend JavaScript for session creation, follow-up questions, streamed and non-streamed answer handling, cancellation, and history refresh from backend APIs.
  Linked requirement(s): REQ-001, REQ-006
  Linked acceptance criteria: AC-001, AC-006
  Affected file(s): `frontend/`
- TASK-008:
  Description: Implement citation rendering and citation-detail interaction that exposes source metadata, snippet, retrieval mode, and available scores without leaving the app.
  Linked requirement(s): REQ-003, REQ-005
  Linked acceptance criteria: AC-003, AC-005
  Affected file(s): `frontend/`

Completion criteria:

- CC-006: Reviewers can ask questions, inspect history, observe progress states, and cancel in-progress answers from the chat UI.
- CC-007: Citation presentation and citation-detail inspection expose the required source metadata and support traceability back to stored chunks.

### Phase 4

Goal:
Harden the retrieval or chat behavior with automated validation and manual review evidence before feature closure.

Enabled user scenario(s) or outcome(s):
SC-001, SC-002, SC-003, SC-004

Tasks:

- TASK-009:
  Description: Add unit and integration coverage for retrieval ranking, answerability decisions, citation mapping, session persistence, streamed completion, and cancellation behavior.
  Linked requirement(s): REQ-002, REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-002, AC-003, AC-004, AC-006
  Affected file(s): `backend/tests/`
- TASK-010:
  Description: Perform manual browser verification of scoped questioning, supported-answer citations, refusals, citation detail, streaming states, cancellation, and history preservation.
  Linked requirement(s): REQ-001, REQ-003, REQ-004, REQ-005, REQ-006
  Linked acceptance criteria: AC-001, AC-003, AC-004, AC-005, AC-006
  Affected file(s): `frontend/`, `backend/`

Completion criteria:

- CC-008: Automated checks cover the backend behavior that produces user-visible grounded answer, refusal, citation, and turn-state outcomes.
- CC-009: Manual verification confirms the chat UI meets the acceptance criteria and keeps citations and refusal reasons inspectable.

## Validation Strategy

- TEST-001 Unit tests: Retrieval helpers, keyword or sparse ranking helpers, answerability classification logic, citation formatting, context-packing helpers, and session-state helpers.
- TEST-002 Integration tests: Flask endpoints for session creation, asking questions, streaming or final answer completion, cancellation, citation detail, and retrieval-mode visibility using local SQLite and ChromaDB fixtures.
- TEST-003 End-to-end tests: Lightweight browser verification of supported questions, unsupported questions, citation inspection, history persistence, and cancellation if automation support is available later.
- TEST-004 Manual verification: Validate the chat screen, visible scope and retrieval strategy, progress states, refusal categories, citations, and citation detail against the acceptance criteria.
- TEST-005 Observability checks: Verify session and turn records preserve terminal state, refusal category, retrieval metadata, and citation references for inspection through backend responses.

## Traceability Matrix

- Scenario or outcome -> Plan phase(s): US-001 -> Phase 1, Phase 2, Phase 3; US-002 -> Phase 1, Phase 3; US-003 -> Phase 2, Phase 3; US-004 -> Phase 2, Phase 3, Phase 4; US-005 -> Phase 1, Phase 2, Phase 3, Phase 4
- REQ-001 -> Plan phase / task IDs: Phase 1 / TASK-001; Phase 2 / TASK-003, TASK-005; Phase 3 / TASK-006, TASK-007
- REQ-002 -> Plan phase / task IDs: Phase 1 / TASK-002; Phase 4 / TASK-009
- REQ-003 -> Plan phase / task IDs: Phase 2 / TASK-003, TASK-004; Phase 3 / TASK-008
- REQ-004 -> Plan phase / task IDs: Phase 2 / TASK-003, TASK-004; Phase 4 / TASK-009
- REQ-005 -> Plan phase / task IDs: Phase 2 / TASK-004, TASK-005; Phase 3 / TASK-008
- REQ-006 -> Plan phase / task IDs: Phase 1 / TASK-001; Phase 2 / TASK-003, TASK-005; Phase 3 / TASK-006, TASK-007; Phase 4 / TASK-009, TASK-010
- AC-001 -> Validation step(s): TEST-002, TEST-004
- AC-002 -> Validation step(s): TEST-001, TEST-002, TEST-005
- AC-003 -> Validation step(s): TEST-001, TEST-002, TEST-004
- AC-004 -> Validation step(s): TEST-001, TEST-002, TEST-004
- AC-005 -> Validation step(s): TEST-002, TEST-004
- AC-006 -> Validation step(s): TEST-002, TEST-004, TEST-005

## Rollout Plan

- Release approach: Deliver the backend chat pipeline and session APIs first, then wire the frontend chat page to the stabilized contracts in the same local environment.
- Feature flags: No formal runtime flag is required in this local-first repo, but incomplete chat controls should stay hidden until their corresponding backend contracts are functional.
- Migration needs: Additive SQLite schema changes for chat sessions and turn records must be idempotent and safe alongside the existing feature 1 schema. No destructive migration should be required.
- Backward compatibility notes: Existing ingestion and collection flows must remain functional. New chat storage should not require rewriting existing document or chunk records.

## Rollback Plan

If the feature proves unstable, roll back the new chat routes, services, and frontend page together so the existing ingestion and collection features remain intact. Keep schema rollback additive in practice: disabling chat behavior is safer than trying to remove newly added chat tables from a local DB automatically. If streaming causes instability, fall back to the non-streamed answer endpoint while preserving the same final answer and citation contract.

## Risks And Mitigations

- RISK-001 Risk: Retrieval mode behavior may be inconsistent across semantic, keyword or sparse, and hybrid paths, causing surprising citation quality.
  Mitigation: Keep retrieval-mode outputs explicit in payloads and add targeted validation for each mode before UI review.
- RISK-002 Risk: Answer generation may produce plausible text that outruns available evidence.
  Mitigation: Enforce answerability checks and citation mapping before finalizing a grounded answer, and refuse explicitly when support is insufficient.
- RISK-003 Risk: Streaming output can expose premature conclusions or unstable citation placeholders.
  Mitigation: Separate progress states from final answer and citation emission; do not emit final citation objects until grounding checks are complete.
- RISK-004 Risk: Brownfield schema or API changes could break the already-working ingestion and collection flows.
  Mitigation: Keep schema changes additive, preserve existing routes, and run the full backend suite alongside new chat tests.

## Open Questions

- Q-001 Question: Which generation provider should be treated as the default first-pass implementation target for this repo?
  Next step: Confirm before task generation so the backend service contract and setup notes stay grounded.
- Q-002 Question: Is the first review expected to show both inline citations and a separate reference-list rendering in the same UI, or is one primary rendering plus structured citation detail sufficient?
  Next step: Confirm before task generation so the frontend citation presentation scope is explicit.
- Q-003 Question: Should streaming use server-sent events or simple chunked HTTP responses in the first implementation?
  Next step: Decide before implementation because it shapes frontend event handling and cancellation semantics.

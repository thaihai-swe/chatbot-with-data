# Implementation Plan

## Metadata

- Feature name: Knowledge Ingestion and Collections
- Related spec: `artifacts/features/1.knowledge-ingestion-and-collections/spec.md`
- Related requirements review: None present
- Related design: None present
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-05

## Plan Summary

Implement this feature as a greenfield ReactJS frontend under `frontend/` backed by a Python FastAPI service under `backend/`, with SQLite storing document, collection, ingestion, and duplicate-decision metadata and local disk storing uploaded source files and fetched URL snapshots. The delivery should be phased so backend contracts and persistence land first, ingestion and duplicate handling land second, and the two user-facing screens land on top of stable REST APIs with validation embedded in each phase.

This plan keeps chunking, embeddings, and retrieval out of scope, but it preserves the identifiers, lifecycle records, and provenance needed by downstream indexing work. Rollout risk is moderate because the feature introduces new persisted state and asynchronous ingestion behavior, so validation and rollback guidance are included per phase rather than deferred to the end.

## Constitution Alignment

- Constitutional rule or principle: Frontend screens in this repo must be JavaScript clients under `frontend/` that call REST API endpoints.
  Planning implication: All user-facing ingestion and collection workflows will be delivered as ReactJS screens that consume FastAPI endpoints; no backend-rendered views are planned.
- Constitutional rule or principle: Python work in this repo must use a virtual environment, and frontend/backend concerns must stay separated.
  Planning implication: Backend setup, dependency management, tests, and runtime commands should assume `.venv`, while frontend scaffolding and build tooling remain isolated under `frontend/`.

## Execution Context

- Design reference: No `design.md` exists for this feature, so the plan makes only the minimum architecture choices needed to start implementation safely.
- Relevant repository patterns for execution: The repository currently contains the PRD, feature specs, `requirements.txt`, an empty `frontend/`, and an empty source-level `backend/`; there is no established application structure to preserve.
- Brownfield execution constraints or greenfield assumptions: Treat this as greenfield source implementation, but keep changes limited to the minimum app, storage, and UI surface needed for the specified workflows.
- Unchanged behavior that must be preserved during delivery: Do not introduce chat, chunking, embeddings, vector indexing, automatic collection routing, or evaluation behaviors in this feature slice.

## Technical Approach

- Chosen approach: Build a REST-first FastAPI backend for collections, documents, ingestion jobs, and duplicate decisions; build a ReactJS client that exposes a document library and collections management screens on top of those APIs.
- Architectural or integration shape: The backend owns file and URL ingestion, text extraction, duplicate classification, lifecycle tracking, and metadata persistence. The frontend owns upload, URL submission, duplicate-decision prompts, status polling or refresh, and collection CRUD workflows.
- Key interfaces or contracts: Collection CRUD endpoints; document listing and filtering endpoints; ingestion submission endpoints for file upload and URL ingestion; duplicate-decision and document lifecycle endpoints for delete, move, replace, and re-ingest actions.
- Operational considerations: Persist raw source artifacts outside git in a local data directory, keep ingestion work reversible through explicit status transitions and event logs, and prefer FastAPI background processing for v1 instead of introducing a separate job queue.

## Decision Rationale

- Why this approach was selected: The repo has no existing app structure, and the PRD explicitly calls for a ReactJS UI and FastAPI backend. A REST-first split keeps implementation aligned with project rules and makes later retrieval and evaluation features easier to layer on.
- Existing patterns reused: The plan reuses the repo's documented split between `frontend/` and `backend/`, the virtualenv requirement for Python, and the PRD direction to use SQLite for metadata.
- Alternatives considered: Introduce a richer async job system now; persist metadata in a different database; wait for chunking or embeddings before implementing duplicate detection.
- Why rejected: Those options add scope or coupling that this feature does not need. The current spec can be satisfied with SQLite metadata, local file storage, and heuristic duplicate detection that does not depend on downstream indexing.

## Requirements And Constraints

- REQ-001:
  Implementation note: Support PDF, TXT, Markdown, and URL ingestion with extractor-specific metadata capture, including filename or URL provenance, content type, and timestamps.
  Planned validation: Integration tests that ingest one sample from each supported source and verify metadata persistence and terminal status.
  Linked scenario or outcome: US-001, SC-001
- REQ-002:
  Implementation note: Model documents and ingestion runs separately so `document_id` remains stable while ingestion attempts and outcomes accumulate as lifecycle records.
  Planned validation: API and persistence tests covering submitted, processing, completed, failed, and skipped states with visible error payloads.
  Linked scenario or outcome: US-001, US-003, US-004, SC-001
- REQ-003:
  Implementation note: Represent collections as first-class records and document membership as explicit associations so collection CRUD and document moves remain traceable.
  Planned validation: CRUD and move-flow tests plus manual UI verification for collection management and membership display.
  Linked scenario or outcome: US-002, US-004, SC-002
- REQ-004:
  Implementation note: Expose delete, re-ingest, and re-index-initiation actions through explicit lifecycle endpoints that update active inventory without orphaning history.
  Planned validation: Integration tests for delete, move, and re-ingest flows and manual verification that inventory views reflect the latest active state.
  Linked scenario or outcome: US-004, SC-001, SC-002
- REQ-005:
  Implementation note: Implement duplicate classification using file hash, normalized text hash, canonical URL comparison, metadata comparison, and text-overlap heuristics; reserve embedding-based checks for later features.
  Planned validation: Backend tests for `unique`, `exact_duplicate`, `near_duplicate`, `same_url`, `same_title_different_content`, and `same_content_different_source` outcomes.
  Linked scenario or outcome: US-001, US-003, US-004, SC-003
- REQ-006:
  Implementation note: Store duplicate evidence and chosen action in dedicated duplicate-decision records linked to the matched document and ingestion attempt.
  Planned validation: Persistence and API tests verifying logged method, evidence, target document reference, and action.
  Linked scenario or outcome: US-003, US-004, SC-003
- REQ-007:
  Implementation note: The React ingestion workflow must show collection assignment, live or refreshable status, duplicate warnings, and decision prompts before a document is treated as usable.
  Planned validation: Frontend integration or end-to-end coverage for upload and duplicate flows plus manual UX verification.
  Linked scenario or outcome: US-001, US-002, US-003, SC-001, SC-003
- NFR-001:
  Implementation note: Use explicit submitted and processing states immediately after intake and expose status refresh or polling from the frontend.
- NFR-002:
  Implementation note: Keep ingestion attempts isolated from one another and make destructive lifecycle actions transactional at the metadata layer.
- NFR-003:
  Implementation note: Treat uploaded files and fetched URLs as untrusted input, limit parsing to supported types, and retain provenance for later safety features.
- NFR-004:
  Implementation note: Status and duplicate states must be labeled with text, not color alone, and destructive actions should have clear button text and confirmations.
- NFR-005:
  Implementation note: Persist audit-friendly records for documents, collections, ingestion attempts, duplicate events, and lifecycle transitions so operators can inspect system state.
- CON-001:
  Impact on plan: Chunking, vector storage, chat, and routing must stay out of this feature even if some schema fields are reserved for downstream compatibility.

## Impacted Areas

- Services or modules: `backend/` FastAPI application, ingestion pipeline, duplicate detection logic, persistence layer, and configuration.
- APIs or interfaces: REST endpoints for collections, documents, ingestion submission, duplicate decisions, and lifecycle actions.
- Data model or storage: SQLite schema for documents, collections, memberships, ingestion attempts, and duplicate events; local disk storage for uploaded files and URL snapshots.
- UI or UX: ReactJS document library and collections screens, upload and URL intake forms, status tables, duplicate warning flows, and collection management dialogs.
- Infrastructure or deployment: Local development setup for Python virtualenv and frontend Node tooling, plus runtime data directories ignored by git.
- Documentation: Feature plan traceability and implementation notes; follow-on API or setup docs may be needed during implementation but are not part of this planning artifact.

## Affected Domains And Integration Boundaries

- Domain or subsystem: Document ingestion lifecycle
  Why it matters: This is the core workflow that creates stable document identity, status visibility, and provenance for downstream features.
- Domain or subsystem: Collection management
  Why it matters: Collections are the organizing unit for later retrieval scoping and must be correct before chat features build on them.
- Integration boundary or touchpoint: Browser to FastAPI REST interface
  Why it matters: The frontend and backend can progress independently only if request and response contracts stabilize early.
- Integration boundary or touchpoint: Metadata store to future indexing pipeline
  Why it matters: This feature must preserve document and collection identities without prematurely implementing chunking or vector writes.

## Protected Behavior

- Behavior that must not regress: The feature must not imply that documents are indexed, retrievable, or chat-ready merely because ingestion metadata exists.
  Protection approach: Use status labels and UI wording that distinguish ingestion completion from downstream indexing or retrieval readiness.
- Behavior that must not regress: Collection changes must not silently drop document provenance or history.
  Protection approach: Model collection membership and lifecycle history explicitly and cover delete, move, and replace flows with integration tests.

## Affected Files

- FILE-001 Path: `backend/`
  Reason for change: New FastAPI application, persistence layer, ingestion services, duplicate logic, and tests are expected here.
- FILE-002 Path: `frontend/`
  Reason for change: New ReactJS client, document library screen, collections screen, and client-side API integration are expected here.
- FILE-003 Path: `requirements.txt`
  Reason for change: Backend dependencies will likely need to expand or normalize to support FastAPI runtime, SQLite access helpers, and testing.
- FILE-004 Path: `.gitignore`
  Reason for change: Review whether frontend build output or additional local data directories need ignore coverage during implementation.

## Dependencies

- DEP-001 Internal dependency: Feature spec `artifacts/features/1.knowledge-ingestion-and-collections/spec.md`
  Why it matters: It defines the required sources, lifecycle states, duplicate classes, and acceptance criteria this plan must trace.
- DEP-002 Internal dependency: Later chunking and indexing work
  Why it matters: This feature must preserve compatible document and collection metadata without implementing downstream retrieval behavior.
- DEP-003 External dependency: PDF and HTML parsing libraries available to the Python environment
  Why it matters: PDF extraction and URL text capture depend on stable parsing libraries inside the project virtualenv.
- DEP-004 External dependency: Node-based React toolchain for `frontend/`
  Why it matters: The repo currently has no frontend scaffold, so implementation will require selecting and installing a React build and test stack.

## Implementation Prerequisites

- PREREQ-001: Clean the working baseline enough to distinguish planned source changes from stale `__pycache__` artifacts in `backend/`.
- PREREQ-002: Confirm or create the Python virtualenv workflow and install backend dependencies through `.venv`.
- PREREQ-003: Decide the ReactJS scaffold and test runner for `frontend/`; if no existing preference is introduced, use a lightweight client scaffold consistent with a REST-only UI.

## Implementation Phases

### Phase 1

Goal: Establish the backend application skeleton, persistence model, and REST contracts that every later slice depends on.
Enabled user scenario(s) or outcome(s): None directly user-complete; this phase creates the stable contracts and storage foundation for US-001 through US-004.

Tasks:

- TASK-001:
  Description: Scaffold the FastAPI app, configuration, and development entrypoint under `backend/`, including health or smoke endpoints and test harness setup.
  Linked requirement(s): REQ-002, NFR-002, NFR-005
  Linked acceptance criteria: Supports AC-001 through AC-004 indirectly by creating the executable backend surface
  Affected file(s): `backend/`, `requirements.txt`
- TASK-002:
  Description: Define the SQLite schema and repository layer for collections, documents, document-collection membership, ingestion attempts, lifecycle events, and duplicate-decision records.
  Linked requirement(s): REQ-002, REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s): `backend/`
- TASK-003:
  Description: Define and implement initial REST contracts for collection CRUD, document listing, document detail, and lifecycle action endpoints, even if ingestion internals are stubbed at first.
  Linked requirement(s): REQ-002, REQ-003, REQ-004, REQ-007
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s): `backend/`

Completion criteria:

- CC-001: FastAPI app starts from the project virtualenv and exposes stable endpoint shapes for collections and documents.
- CC-002: SQLite persistence exists for all core entities needed by the spec with tests proving create, update, read, and lifecycle logging behavior.

### Phase 2

Goal: Deliver ingestion execution, extractor support, and duplicate classification with auditable lifecycle outcomes.
Enabled user scenario(s) or outcome(s): US-001, US-003, and the lifecycle portion of US-004.

Tasks:

- TASK-004:
  Description: Implement file upload and URL ingestion intake, supported-source extractors, raw artifact storage, and ingestion status transitions from submitted through terminal outcomes.
  Linked requirement(s): REQ-001, REQ-002, REQ-004
  Linked acceptance criteria: AC-001, AC-003
  Affected file(s): `backend/`
- TASK-005:
  Description: Implement duplicate and near-duplicate detection using hashes, canonicalized URLs, metadata comparison, and text-overlap heuristics, plus user-action pathways such as skip, replace, merge metadata, new version, and ingest anyway.
  Linked requirement(s): REQ-005, REQ-006, REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/`
- TASK-006:
  Description: Finalize lifecycle action endpoints for delete, re-ingest, re-index initiation, and document moves between collections, ensuring active inventory and history remain consistent.
  Linked requirement(s): REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-002, AC-003, AC-004
  Affected file(s): `backend/`

Completion criteria:

- CC-003: All supported source types ingest through the backend with visible terminal status and preserved provenance.
- CC-004: Duplicate outcomes and handling decisions are persisted and retrievable for audit and UI display.

### Phase 3

Goal: Deliver the ReactJS document library experience on top of stable backend APIs.
Enabled user scenario(s) or outcome(s): US-001, US-003, and document visibility for US-004.

Tasks:

- TASK-007:
  Description: Scaffold the ReactJS client and API integration layer under `frontend/`, including routing or screen structure needed for the document library and collections views.
  Linked requirement(s): REQ-007, NFR-004
  Linked acceptance criteria: Supports AC-001 through AC-004 indirectly by creating the UI surface
  Affected file(s): `frontend/`
- TASK-008:
  Description: Implement the document library screen with file upload, URL submission, collection selection, document table, metadata display, filters, search, and status visibility.
  Linked requirement(s): REQ-001, REQ-002, REQ-007
  Linked acceptance criteria: AC-001
  Affected file(s): `frontend/`
- TASK-009:
  Description: Implement duplicate warning and decision flows so users can inspect duplicate evidence and choose the allowed action before the document is treated as available.
  Linked requirement(s): REQ-005, REQ-006, REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `frontend/`

Completion criteria:

- CC-005: A user can submit supported sources from the browser and inspect document status, metadata, and duplicate state without using backend-only tools.
- CC-006: The UI does not rely only on color to communicate ingestion or duplicate status.

### Phase 4

Goal: Deliver collection management UI, end-to-end integration hardening, and release-readiness verification.
Enabled user scenario(s) or outcome(s): US-002 and the collection-management portion of US-004.

Tasks:

- TASK-010:
  Description: Implement the collections screen with create, rename, inspect, delete, document membership visibility, and move actions aligned to the current feature scope.
  Linked requirement(s): REQ-003, REQ-004, REQ-007
  Linked acceptance criteria: AC-002, AC-003
  Affected file(s): `frontend/`
- TASK-011:
  Description: Add cross-stack integration tests and manual verification coverage for end-to-end ingestion, duplicate handling, collection CRUD, and lifecycle actions.
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s): `backend/`, `frontend/`
- TASK-012:
  Description: Tighten release-readiness details such as empty-state UX, error messages, status wording, and any minimal setup or operator notes needed to run the feature locally.
  Linked requirement(s): NFR-001, NFR-003, NFR-004, NFR-005
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s): `frontend/`, `backend/`

Completion criteria:

- CC-007: Collection CRUD and document movement work from the UI with backend persistence and traceability intact.
- CC-008: Acceptance-criteria validation is executable end to end without relying on unstated manual backend intervention.


## Traceability Matrix

- Scenario or outcome -> Plan phase(s): US-001 -> Phases 2 and 3; US-002 -> Phase 4; US-003 -> Phases 2 and 3; US-004 -> Phases 2 and 4; SC-001 -> Phases 2 and 3; SC-002 -> Phase 4; SC-003 -> Phases 2 and 3
- REQ-001 -> Plan phase / task IDs: Phase 2 / TASK-004; Phase 3 / TASK-008
- REQ-002 -> Plan phase / task IDs: Phase 1 / TASK-001, TASK-002, TASK-003; Phase 2 / TASK-004
- REQ-003 -> Plan phase / task IDs: Phase 1 / TASK-002, TASK-003; Phase 2 / TASK-006; Phase 4 / TASK-010
- REQ-004 -> Plan phase / task IDs: Phase 1 / TASK-002, TASK-003; Phase 2 / TASK-004, TASK-006; Phase 4 / TASK-010
- REQ-005 -> Plan phase / task IDs: Phase 2 / TASK-005; Phase 3 / TASK-009
- REQ-006 -> Plan phase / task IDs: Phase 1 / TASK-002; Phase 2 / TASK-005, TASK-006; Phase 3 / TASK-009
- REQ-007 -> Plan phase / task IDs: Phase 1 / TASK-003; Phase 2 / TASK-005; Phase 3 / TASK-007, TASK-008, TASK-009; Phase 4 / TASK-010
- AC-001 -> Validation step(s): TEST-002 supported-source ingestion coverage; TEST-003 upload and URL ingestion flow; TEST-004 metadata and status review
- AC-002 -> Validation step(s): TEST-002 collection CRUD and membership tests; TEST-003 collections-screen workflow; TEST-004 traceability review
- AC-003 -> Validation step(s): TEST-002 delete, move, and re-ingest integration coverage; TEST-003 lifecycle actions flow; TEST-005 persisted state inspection
- AC-004 -> Validation step(s): TEST-001 duplicate classifier tests; TEST-002 duplicate-decision API coverage; TEST-003 duplicate-warning UX flow; TEST-004 reviewer walk-through

## Rollout Plan

- Release approach: Land the backend contracts and persistence first, then expose the React screens once ingestion and duplicate workflows are functional end to end.
- Feature flags: None required if the feature remains local-only during development; if this repo later hosts multiple screens, keep navigation entry points hidden until Phase 3 is complete.
- Migration needs: Introduce SQLite schema creation or migration logic for new metadata tables before enabling the feature locally.
- Backward compatibility notes: There is no existing source implementation to preserve, but document and collection IDs created here should remain stable for downstream indexing and chat features.

## Rollback Plan

Disable or remove the frontend navigation entry points first if a regression is found after the UI lands. Backend rollback should preserve stored raw files until metadata rollback is confirmed, then revert the new FastAPI routes and SQLite schema changes together so orphaned lifecycle records are not left behind. If a full code rollback is needed before dependent features land, remove the new tables and local data directory only after validating that no other feature has started consuming them.

## Risks And Mitigations

- RISK-001 Risk: Duplicate heuristics may over-classify or under-classify near-duplicate documents without embeddings.
  Mitigation: Keep classification evidence visible, log the detection method, require explicit handling choices for ambiguous cases, and cover representative edge cases in tests.
- RISK-002 Risk: Asynchronous ingestion can leave status records inconsistent if extraction or storage fails midway.
  Mitigation: Separate ingestion-attempt records from document records, use explicit terminal failure states, and test partial-failure paths.
- RISK-003 Risk: The frontend could outpace backend contract stability in a greenfield repo.
  Mitigation: Freeze core REST contracts in Phase 1 before substantial UI work and keep frontend API access isolated behind a small client layer.
- RISK-004 Risk: The PRD mentions collection-level statistics such as chunk counts, but chunking is out of scope for this feature.
  Mitigation: Limit the initial collections UI to statistics supported by current data, and label any deferred metrics clearly rather than fabricating values.

## Open Questions

- Q-001 Question: Should document membership remain many-to-many in the first implementation, or should v1 intentionally constrain each document to one primary collection even though the spec currently allows one or more?
  Next step: Confirm before implementation starts; the plan assumes explicit many-to-many membership because that best matches the current spec and PRD.
- Q-002 Question: Should re-index initiation be implemented as a recorded no-op placeholder until the chunking feature exists, or should the UI hide that action until downstream indexing work lands?
  Next step: Decide during implementation kickoff so the lifecycle API and UI wording do not imply unavailable behavior.
- Q-003 Question: Which React scaffold and test stack should the repo standardize on for greenfield frontend work?
  Next step: If no existing repo preference is introduced, select a lightweight scaffold during implementation and document the choice in the initial frontend setup commit.

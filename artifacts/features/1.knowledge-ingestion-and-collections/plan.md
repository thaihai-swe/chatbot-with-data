# Implementation Plan

## Metadata

- Feature name: Knowledge Ingestion And Collections
- Related spec: `artifacts/features/1.knowledge-ingestion-and-collections/spec.md`
- Related requirements review: None present in workspace
- Related design: None
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-04

## Plan Summary

Implement the first feature slice as a local-first document-ingestion and collection-management system with a Python API backend and a plain HTML, CSS, and JavaScript frontend that calls the API through AJAX or `fetch`. The backend will own ingestion orchestration, duplicate detection, chunk preparation, metadata persistence, vector indexing, and collection lifecycle operations. The frontend will expose the Document Library and Collections screens, document actions, and status visibility required by the spec. Validation is embedded phase by phase so ingestion correctness, duplicate handling, chunk metadata, and collection consistency are verified before the UI depends on them.

## Constitution Alignment

- Constitutional rule or principle: Touch only what the request requires.
  Planning implication: This plan covers only knowledge ingestion, duplicate handling, chunk and index preparation, collections, and the two required screens. It does not pull chat, advanced retrieval, or settings work forward.
- Constitutional rule or principle: Frontend screens in this repo should be JavaScript clients that call REST API endpoints; frontend and backend must stay separated.
  Planning implication: The UI work will live under `frontend/` as static HTML, CSS, and JavaScript that calls backend REST endpoints. All ingestion, persistence, and processing logic stays under `backend/`.
- Constitutional rule or principle: For Python, always use virtualenv.
  Planning implication: Backend setup, validation, and local scripts must run inside a project virtual environment before implementation starts.

## Execution Context

- Design reference: None
- Relevant repository patterns for execution: Greenfield repo with `frontend/` and `backend/` directories already split, plus Python dependencies for Flask, ChromaDB, PDF parsing, HTML parsing, and environment management in `requirements.txt`.
- Brownfield execution constraints or greenfield assumptions: Greenfield implementation; no existing API routes, storage schema, UI assets, or ingestion pipeline need backward compatibility.
- Unchanged behavior that must be preserved during delivery: Keep feature scope limited to ingestion and collection management. Do not introduce chat, retrieval answer generation, or experiment-dashboard behavior in this feature.

## Technical Approach

- Chosen approach: Build a Flask-based JSON API in `backend/` for document upload, URL ingestion, document lifecycle actions, duplicate inspection, chunk and index status, and collection management. Build a static frontend in `frontend/` using HTML, CSS, and JavaScript with AJAX or `fetch` calls to the API for the Document Library and Collections screens.
- Architectural or integration shape: The backend separates API routes, ingestion services, duplicate-detection logic, chunking and indexing services, and local persistence adapters. Metadata and operational state are stored locally in SQLite. Vector data is stored locally in ChromaDB. The frontend renders server-provided document and collection state and triggers backend actions through REST endpoints.
- Key interfaces or contracts: Multipart file-upload endpoint, URL-ingestion endpoint, document list/detail endpoints, duplicate-decision submission endpoint, re-index endpoint, delete endpoint, collection CRUD endpoints, document-to-collection move endpoint, and status payloads that include the metadata fields required by the spec.
- Operational considerations: All backend execution happens in a Python virtual environment. Long-running ingestion steps may execute synchronously at first if response times remain acceptable for small local datasets, but API and UI contracts should preserve explicit status fields so asynchronous execution can be introduced later without redesigning the screens.

## Decision Rationale

- Why this approach was selected: It matches the repo constraints, the PRD v1 direction, the dependency list already present, and the AGENTS rule that frontend screens should be JavaScript clients calling REST endpoints.
- Existing patterns reused: Existing repository separation of `frontend/` and `backend/`, Python dependency stack centered on Flask, ChromaDB, requests, BeautifulSoup, PyPDF2, and pdfplumber.
- Alternatives considered: Server-rendered frontend from Python templates; a heavier frontend framework; delaying vector indexing until chat work begins.
- Why rejected: Server-rendered UI conflicts with repo guidance. A heavier frontend framework adds setup and structure that the repo does not currently need. Delaying vector indexing would break the feature’s requirement to prepare retrievable chunk and index records now.

## Requirements And Constraints

- REQ-001:
  Implementation note: Support multipart file upload for PDF, TXT, and Markdown plus URL submission; create a stable document record immediately and track each ingestion attempt.
  Planned validation: API tests for each source type; manual upload and URL-ingestion verification in the Document Library screen.
  Linked scenario or outcome: US-001, US-002, SC-001
- REQ-002:
  Implementation note: Persist document metadata, ingestion state, errors, source identity, lifecycle history, and collection assignments in SQLite-backed metadata storage.
  Planned validation: Persistence-focused integration tests and UI verification of document detail fields.
  Linked scenario or outcome: US-001, US-005, SC-001, SC-003
- REQ-003:
  Implementation note: Implement duplicate checks before finalizing ingestion, preserve required duplicate classes and logging fields, and expose duplicate decisions through API and UI.
  Planned validation: Duplicate and near-duplicate tests plus manual duplicate-warning handling through the UI.
  Linked scenario or outcome: US-003, SC-002
- REQ-004:
  Implementation note: Implement baseline chunk preparation for fixed-size, heading-aware Markdown, and page-aware PDF flows, then create embeddings and ChromaDB index records with traceable metadata.
  Planned validation: Chunk metadata assertions, re-index tests, and inspection of prepared records.
  Linked scenario or outcome: US-005, SC-001, SC-004
- REQ-005:
  Implementation note: Implement collection CRUD, default-collection state, document assignment or move operations, and preservation of collection metadata across document, chunk, and index records.
  Planned validation: Collection CRUD and move integration tests plus manual UI verification.
  Linked scenario or outcome: US-004, SC-003, SC-004
- REQ-006:
  Implementation note: Build Document Library and Collections screens in plain HTML, CSS, and JavaScript, using AJAX or `fetch` for list, create, update, move, delete, duplicate-decision, and re-index flows.
  Planned validation: Browser-level manual flow verification against the acceptance criteria and API contract checks for returned fields.
  Linked scenario or outcome: US-001, US-003, US-004, US-005, SC-001, SC-002, SC-003, SC-004
- NFR-001:
  Implementation note: Model terminal ingestion states explicitly and avoid silent failures.
- NFR-002:
  Implementation note: Use stable identifiers and keep document, chunk, and collection references consistent across SQLite and ChromaDB.
- NFR-003:
  Implementation note: Treat uploaded and fetched content as user data; preserve only required metadata and content-derived records.
- NFR-004:
  Implementation note: Expose ingestion and duplicate decisions through API responses and UI state rather than hidden console logs only.
- CON-001:
  Impact on plan: Frontend and backend work must stay separated by directory and responsibility.
- CON-002:
  Impact on plan: Python setup and verification must assume a project virtual environment.

## Impacted Areas

- Services or modules: New ingestion service layer, duplicate-detection service, chunking service, indexing service, collection service, metadata persistence layer.
- APIs or interfaces: New REST API for upload, URL ingestion, documents, duplicate actions, re-index, delete, collections, and document movement.
- Data model or storage: SQLite schema for documents, ingestion attempts, collections, duplicate decisions, and chunk metadata; ChromaDB collections for vectors and collection-aware metadata.
- UI or UX: New Document Library screen and Collections screen under `frontend/`.
- Infrastructure or deployment: Local development only; project virtualenv plus local filesystem and local data directories for SQLite and ChromaDB persistence.
- Documentation: Feature-specific setup and manual verification notes once implementation starts.

## Affected Domains And Integration Boundaries

- Domain or subsystem: Backend ingestion pipeline
  Why it matters: It owns parsing, duplicate checks, chunk preparation, and indexing.
- Domain or subsystem: Metadata persistence
  Why it matters: It must keep document, chunk, duplicate, and collection records consistent and queryable.
- Domain or subsystem: Vector indexing
  Why it matters: It establishes retrieval-ready records required by later features.
- Domain or subsystem: Frontend library and collection management UI
  Why it matters: It is the only user-visible surface for this feature’s acceptance criteria.
- Integration boundary or touchpoint: Frontend-to-backend JSON contracts
  Why it matters: The UI depends on stable status, duplicate, and collection payload fields.
- Integration boundary or touchpoint: SQLite-to-Chroma consistency
  Why it matters: Re-index, delete, and collection-move actions must update both metadata and vector records safely.
- Integration boundary or touchpoint: URL fetch and parsing
  Why it matters: Network content extraction can fail in more ways than local file upload and must surface actionable errors.

## Protected Behavior

- Behavior that must not regress: Stable `document_id` assignment across ingestion retries and re-indexing.
  Protection approach: Persist canonical document records separately from transient ingestion attempt records and test repeated operations.
- Behavior that must not regress: Duplicate warnings must appear before duplicate content is silently accepted.
  Protection approach: Run duplicate checks before final record finalization and cover the decision path with API tests and UI verification.
- Behavior that must not regress: Collection membership consistency across document, chunk, and vector records.
  Protection approach: Centralize collection updates through one backend service and verify both metadata and index state after moves or deletes.

## Affected Files

- FILE-001 Path: `backend/`
  Reason for change: Add new API, service, and persistence modules for ingestion, duplicate handling, chunking, indexing, and collections.
- FILE-002 Path: `frontend/`
  Reason for change: Add static HTML, CSS, and JavaScript for the Document Library and Collections screens with AJAX-based API integration.
- FILE-003 Path: `requirements.txt`
  Reason for change: Likely unchanged for the first implementation because the required backend dependencies are already declared; verify before coding.
- FILE-004 Path: `artifacts/features/1.knowledge-ingestion-and-collections/`
  Reason for change: Source artifact location for planning, later tasks, and implementation traceability.

## Dependencies

- DEP-001 Internal dependency: Project virtual environment setup
  Why it matters: Backend work and validation must run in the required Python environment.
- DEP-002 Internal dependency: Local directory layout under `frontend/` and `backend/`
  Why it matters: The plan assumes frontend and backend remain separated by folder.
- DEP-003 External dependency: Local file system for uploaded files and persistent local data
  Why it matters: Ingestion, deletion, and re-index flows need stable local storage behavior.
- DEP-004 External dependency: ChromaDB and SQLite runtime behavior
  Why it matters: The feature depends on synchronized metadata and vector persistence.
- DEP-005 External dependency: Remote web URLs supplied by the user
  Why it matters: URL ingestion depends on fetch reliability and HTML parsing quality.

## Implementation Prerequisites

- PREREQ-001: Create and activate a project Python virtual environment before backend implementation or tests run.
- PREREQ-002: Decide where local uploaded-source files and persistent SQLite or ChromaDB data will live inside the workspace.
- PREREQ-003: Confirm the minimal backend package structure under `backend/` and static asset structure under `frontend/` before task breakdown.
- PREREQ-004: Confirm whether near-duplicate behavior beyond exact or canonical URL checks is required in the first implementation increment or can land as a staged follow-up within the same feature.

## Implementation Phases

### Phase 1

Goal:
Establish the backend data model, persistence contracts, and collection lifecycle foundation.

Enabled user scenario(s) or outcome(s):
US-004, US-005, SC-003, SC-004

Tasks:

- TASK-001:
  Description: Create backend metadata and persistence structure for documents, ingestion attempts, collections, duplicate records, chunk metadata, and index references.
  Linked requirement(s): REQ-002, REQ-005
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s): `backend/`
- TASK-002:
  Description: Implement collection CRUD, default-collection state, and document-to-collection assignment or move behavior in backend services and REST endpoints.
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Affected file(s): `backend/`

Completion criteria:

- CC-001: Collection and document metadata can be created, updated, queried, and deleted consistently through backend interfaces.
- CC-002: A document can be assigned to and moved between collections without breaking metadata integrity.

### Phase 2

Goal:
Implement ingestion, duplicate handling, chunk preparation, and index creation in the

Enabled user scenario(s) or outcome(s):
US-001, US-002, US-003, US-005, SC-001, SC-002, SC-004

Tasks:

- TASK-003:
  Description: Implement PDF, TXT, Markdown, and URL ingestion flows with explicit status and error handling.
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s): `backend/`
- TASK-004:
  Description: Implement duplicate-detection pipeline, duplicate classifications, duplicate logging fields, and duplicate-decision handling before ingestion finalization.
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Affected file(s): `backend/`
- TASK-005:
  Description: Implement baseline chunking, embedding generation, vector indexing, re-index behavior, and deletion cleanup across metadata and vectors.
  Linked requirement(s): REQ-004, REQ-005
  Linked acceptance criteria: AC-004, AC-005
  Affected file(s): `backend/`

Completion criteria:

- CC-003: Each supported source type can be ingested into a stable document record with explicit terminal state.
- CC-004: Duplicate and near-duplicate attempts trigger visible classification and decision flows.
- CC-005: Accepted documents produce chunk and index records with the required metadata and collection linkage.

### Phase 3

Goal:
Deliver the Document Library and Collections screens on top of the backend API contracts.

Enabled user scenario(s) or outcome(s):
US-001, US-003, US-004, US-005, SC-001, SC-002, SC-003, SC-004

Tasks:

- TASK-006:
  Description: Build the Document Library screen in HTML, CSS, and JavaScript with AJAX or `fetch` integration for upload, URL ingestion, listing, filtering, searching, duplicate handling, deletion, and re-index actions.
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-006
  Affected file(s): `frontend/`
- TASK-007:
  Description: Build the Collections screen in HTML, CSS, and JavaScript with AJAX or `fetch` integration for collection CRUD, default-collection selection, document moves, and collection statistics display.
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s): `frontend/`

Completion criteria:

- CC-006: Reviewers can manage documents and collections through the required screens without direct database access.
- CC-007: The frontend shows the required document-row and collection fields, plus long-running status visibility.

### Phase 4

Goal:
Harden validation, regression checks, and local operational safety for the completed feature.

Enabled user scenario(s) or outcome(s):
SC-001, SC-002, SC-003, SC-004

Tasks:

- TASK-008:
  Description: Add automated validation for supported source types, duplicate paths, chunk metadata, collection moves, deletion, and re-index flows.
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004, AC-005
  Affected file(s): `backend/`
- TASK-009:
  Description: Perform manual end-to-end browser verification for the Document Library and Collections workflows and record any residual risks or follow-up fixes.
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s): `frontend/`, `backend/`

Completion criteria:

- CC-008: Automated checks cover the backend behaviors that produce user-visible lifecycle state.
- CC-009: Manual verification confirms the UI meets the acceptance criteria and exposes actionable failures.

## Validation Strategy

- TEST-001 Unit tests: Parser helpers, duplicate-classification helpers, chunking helpers, and collection-state helpers.
- TEST-002 Integration tests: Flask API endpoints for upload, URL ingestion, duplicate handling, document lifecycle actions, collection CRUD, moves, and re-index behavior against local SQLite and ChromaDB test data.
- TEST-003 End-to-end tests: Lightweight browser flow verification for upload, URL ingest, duplicate warning, collection creation, document move, delete, and re-index behaviors.
- TEST-004 Manual verification: Validate document-row fields, collection fields, status transitions, duplicate prompts, and visible error handling in the two required screens.
- TEST-005 Observability checks: Verify ingestion status, duplicate decision fields, lifecycle state, and chunk metadata are inspectable through API responses and UI views without direct storage access.

## Traceability Matrix

- Scenario or outcome -> Plan phase(s): US-001 -> Phase 2, Phase 3; US-002 -> Phase 2, Phase 3; US-003 -> Phase 2, Phase 3; US-004 -> Phase 1, Phase 3; US-005 -> Phase 1, Phase 2, Phase 3, Phase 4
- REQ-001 -> Plan phase / task IDs: Phase 2 / TASK-003; Phase 3 / TASK-006
- REQ-002 -> Plan phase / task IDs: Phase 1 / TASK-001; Phase 2 / TASK-003; Phase 3 / TASK-006
- REQ-003 -> Plan phase / task IDs: Phase 2 / TASK-004; Phase 3 / TASK-006
- REQ-004 -> Plan phase / task IDs: Phase 2 / TASK-005
- REQ-005 -> Plan phase / task IDs: Phase 1 / TASK-001, TASK-002; Phase 2 / TASK-005; Phase 3 / TASK-007
- REQ-006 -> Plan phase / task IDs: Phase 3 / TASK-006, TASK-007; Phase 4 / TASK-009
- AC-001 -> Validation step(s): TEST-002, TEST-003, TEST-004
- AC-002 -> Validation step(s): TEST-002, TEST-004, TEST-005
- AC-003 -> Validation step(s): TEST-001, TEST-002, TEST-004
- AC-004 -> Validation step(s): TEST-001, TEST-002, TEST-005
- AC-005 -> Validation step(s): TEST-002, TEST-003, TEST-004
- AC-006 -> Validation step(s): TEST-003, TEST-004

## Rollout Plan

- Release approach: Deliver backend foundation first, then enable the frontend screens against the stable API contracts in the same local development environment.
- Feature flags: No runtime flags required for a greenfield local-first feature; keep incomplete UI actions hidden until their backend endpoints are functional.
- Migration needs: Initialize local SQLite schema and local ChromaDB collections before first use; plan implementation should include idempotent local setup.
- Backward compatibility notes: No existing user-facing feature needs compatibility support, but API and storage contracts created here should be stable enough for later chat and retrieval features.

## Rollback Plan

Because this is a greenfield feature, rollback is primarily code and local-data rollback. If a change proves unsafe during implementation, revert the feature branch changes, remove any newly created local SQLite or ChromaDB artifacts for this feature, and return the frontend to a no-op state with no exposed ingestion or collection actions. For partially completed work, disable the affected UI action and backend route together rather than leaving an interactive control wired to an unstable backend path.

## Risks And Mitigations

- RISK-001 Risk: Duplicate logic may be too aggressive or too weak for mixed local-file and URL content.
  Mitigation: Preserve the required duplicate classes and logs, keep decision handling explicit, and cover exact and near-duplicate cases in validation.
- RISK-002 Risk: Metadata and vector records can drift during delete, re-index, or collection-move actions.
  Mitigation: Centralize lifecycle operations through backend services and verify both SQLite and ChromaDB state after each lifecycle action.
- RISK-003 Risk: URL ingestion can fail unpredictably due to fetch or parsing issues.
  Mitigation: Surface actionable ingestion-error state and test representative URL failure modes.
- RISK-004 Risk: Frontend development may outrun backend contract stability in a greenfield repo.
  Mitigation: Complete and validate backend API payloads before wiring the UI screens deeply.

## Open Questions

- Q-001 Question: What minimum near-duplicate depth should be considered mandatory in the first implementation increment beyond exact hash and canonical URL checks?
  Next step: Confirm during the next requirements or design checkpoint before task generation if this materially changes scope.
- Q-002 Question: Should uploaded-source content be persisted as raw files in a dedicated workspace directory, or is normalized extracted content sufficient for this feature’s first implementation?
  Next step: Resolve before backend persistence work starts because it affects delete and re-index behavior.

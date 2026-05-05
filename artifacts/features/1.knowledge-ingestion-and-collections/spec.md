# Feature Specification

## Metadata

- Feature name: Knowledge Ingestion and Collections
- Feature slug: knowledge-ingestion-and-collections
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-05
- Related knowledge artifact(s): `prd-requirement.md`

## Problem Statement

The product cannot serve grounded answers until users can reliably add knowledge sources, organize them into meaningful collections, and manage document lifecycle events without creating duplicate or misleading data. The primary users are engineers and learners who need a clean, inspectable knowledge base before they can evaluate retrieval quality.

## Desired Outcomes

- Users can ingest supported sources into named collections with clear status, metadata, and error visibility.
- The knowledge base stays organized and low-noise through lifecycle controls and duplicate handling.

## Success Criteria

- SC-001: A user can ingest PDF, TXT, Markdown, and web URL sources into a selected collection and see a terminal status for every submitted item.
- SC-002: A user can create, rename, delete, and inspect collections without losing document-to-collection traceability.
- SC-003: Duplicate and near-duplicate documents are detected before they pollute retrieval, and the decision taken is visible to the user.

## In Scope

- Source ingestion for PDF, TXT, Markdown, and web URLs
- Stable document identity, source metadata, and ingestion status tracking
- Collection creation and document assignment workflows
- Re-ingestion, re-indexing initiation, document deletion, and document moves between collections
- Duplicate and near-duplicate detection with user-visible warnings and decision logging

## Out Of Scope

- Chunking strategy definition and embedding generation
- Chat answering, citations, or retrieval strategy comparison
- Evaluation dashboards and experiment reports

## Users And Stakeholders

- Primary users: Software engineers and learners building a document-backed assistant
- Secondary stakeholders: Reviewers assessing product completeness and AI engineering quality

## User Stories And Key Scenarios

- US-001: As a user, I can upload files or submit a URL so the system can ingest new knowledge.
- US-002: As a user, I can place documents into collections so retrieval can be scoped to a knowledge base.
- US-003: As a user, I can see whether ingestion succeeded, failed, or produced a duplicate warning before I rely on the content.
- US-004: As a user, I can remove, replace, or move documents so the knowledge base stays current.

## Current Context

The repository currently contains the PRD and environment scaffolding but no committed ingestion, collection-management, or UI implementation. This spec defines the first reviewable product slice and does not need to preserve an existing ingestion workflow.

## Dependencies And External Touchpoints

- DEP-001: User-provided local files and user-submitted web URLs
- DEP-002: A document storage layer that can retain source metadata and lifecycle state
- DEP-003: Downstream chunking and indexing flows that consume accepted documents

## Functional Requirements

### REQ-001

Requirement: The system must accept PDF, TXT, Markdown, and web URL sources for ingestion, extract textual content from each supported source type, and preserve source-specific metadata needed for later retrieval and citation.

Why it matters: Users cannot build a meaningful knowledge base if supported sources are inconsistent or lose provenance.

Impacted users or scenarios: US-001, US-003

Related success criteria: SC-001

Priority: Must Have

Acceptance notes: Reviewers must be able to confirm supported source coverage and retained source metadata for each ingested document.

### REQ-002

Requirement: The system must assign a stable `document_id` to each ingested document and record ingestion lifecycle state, including submitted, processing, completed, failed, and skipped outcomes with a user-visible error reason when ingestion does not complete.

Why it matters: Stable identity and status visibility are required for debugging, later re-indexing, and trustworthy collection management.

Impacted users or scenarios: US-001, US-003, US-004

Related success criteria: SC-001

Priority: Must Have

Acceptance notes: A reviewer must be able to inspect an item after ingestion and see both its stable identity and latest lifecycle outcome.

### REQ-003

Requirement: The system must allow users to create, rename, delete, and inspect collections, assign documents to one or more collections during ingestion when allowed by the product model, and move documents between collections while preserving document provenance.

Why it matters: Collections are the core unit for organizing knowledge bases and later scoping retrieval behavior.

Impacted users or scenarios: US-002, US-004

Related success criteria: SC-002

Priority: Must Have

Acceptance notes: Reviewers must be able to verify collection CRUD behavior and confirm that collection membership stays attached to the document record.

### REQ-004

Requirement: The system must support document deletion, re-ingestion, and re-indexing initiation without leaving orphaned lifecycle records or ambiguous collection membership.

Why it matters: Users need to correct bad uploads, refresh stale content, and keep the knowledge base accurate over time.

Impacted users or scenarios: US-004

Related success criteria: SC-001, SC-002

Priority: Must Have

Acceptance notes: A reviewer must be able to observe that a deleted or replaced document no longer appears as active content in the collection inventory.

### REQ-005

Requirement: The system must detect exact duplicates and near-duplicates during ingestion using source and content comparison signals such as file hash, normalized text hash, URL canonicalization, title and metadata matching, chunk-level similarity, embedding similarity, or near-duplicate text overlap; classify each submitted item as `unique`, `exact_duplicate`, `near_duplicate`, `same_url`, `same_title_different_content`, or `same_content_different_source`; and offer an explicit action path such as skip ingestion, replace an existing document, ingest as a new version, merge metadata, warn before continuing, or ingest anyway.

Why it matters: Duplicate data degrades retrieval quality, confuses evaluation, and makes the collection inventory harder to trust.

Impacted users or scenarios: US-001, US-003, US-004

Related success criteria: SC-003

Priority: Must Have

Acceptance notes: A reviewer must be able to trigger a duplicate case and see both the classification and the chosen handling outcome.

### REQ-006

Requirement: The system must log the detection method, matched document reference, similarity evidence when applicable, duplicate decision, and final user or system action for every duplicate or near-duplicate event.

Why it matters: Duplicate handling affects future retrieval and evaluation quality, so its reasoning must be auditable.

Impacted users or scenarios: US-003, US-004

Related success criteria: SC-003

Priority: Must Have

Acceptance notes: Reviewers must be able to inspect a duplicate-handling record without inferring hidden logic.

### REQ-007

Requirement: The ingestion experience must surface collection assignment, ingestion status, duplicate warnings, and any user decision needed for duplicate handling before the user assumes the document is available for chat or evaluation.

Why it matters: Silent failures or hidden warnings lead users to trust content that is not ready or not unique.

Impacted users or scenarios: US-001, US-002, US-003

Related success criteria: SC-001, SC-003

Priority: Must Have

Acceptance notes: A reviewer must be able to identify the readiness and duplicate state of each newly submitted source from the user-facing workflow.

## Non-Functional Requirements

- NFR-001 Performance: Status transitions for a submitted ingestion job must be visible quickly enough that users can distinguish active processing from a stalled workflow.
- NFR-002 Reliability: Failed ingestion of one source must not corrupt or silently alter unrelated document records or collections.
- NFR-003 Security or Privacy: The system must treat uploaded files and fetched web content as untrusted input and preserve provenance for later safety review.
- NFR-004 Accessibility: Collection management and ingestion status must be understandable through text labels and not rely only on color cues.
- NFR-005 Observability or Supportability: Operators and reviewers must be able to inspect document state, collection membership, duplicate-handling decisions, and the current document inventory within each collection.

## Constraints

- Technical constraints: The feature must stay compatible with a future chunking and indexing pipeline without prescribing storage internals here.
- Business constraints: The scope must remain understandable as a portfolio-quality artifact rather than a multi-tenant document platform.
- Delivery constraints: This feature should establish the content inventory model used by all later specs.

## Assumptions

- ASM-001: A document may belong to one or more collections when the product model benefits from reuse, but collection membership must remain explicit and reviewable.
- ASM-002: Web URL ingestion is limited to content that can be fetched and converted into readable text within the application’s allowed runtime environment.

## Risks

- RISK-001 Risk: Weak duplicate handling can create noisy retrieval results and misleading evaluation gains.
  Mitigation: Require explicit classification, logged evidence, and user-visible handling decisions.
- RISK-002 Risk: Collection lifecycle actions may leave stale references behind.
  Mitigation: Require lifecycle consistency checks in deletion, move, and re-ingestion flows.

## Open Questions

- Q-001 Question: Should a single document be attachable to multiple collections, or should collection membership be exactly one collection per document?
  Type: Non-blocking
  Owner: Product decision
  Next step: Confirm during requirements review; the current assumption allows one or more collections.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001, REQ-002
  Linked user story or scenario: US-001
  Linked success criteria: SC-001
  Validation method: Ingest one item of each supported source type and verify preserved source metadata, stable `document_id`, and terminal status visibility.
- [ ] AC-002 Linked requirement(s): REQ-003
  Linked user story or scenario: US-002
  Linked success criteria: SC-002
  Validation method: Create, rename, inspect, and delete collections, then verify that document membership updates stay traceable.
- [ ] AC-003 Linked requirement(s): REQ-004
  Linked user story or scenario: US-004
  Linked success criteria: SC-001, SC-002
  Validation method: Re-ingest, move, and delete a document, then confirm active inventory reflects the latest lifecycle state without orphaned references.
- [ ] AC-004 Linked requirement(s): REQ-005, REQ-006, REQ-007
  Linked user story or scenario: US-003
  Linked success criteria: SC-003
  Validation method: Submit an exact duplicate and a near-duplicate, verify duplicate status classification, detection evidence, warning visibility, action options, and recorded duplicate reasoning.

## Notes

Delivery sequence: 1 of 7. This feature establishes the document and collection inventory required by all downstream retrieval, safety, configuration, and evaluation features.

# Feature Specification

## Metadata

- Feature name: Knowledge Ingestion And Collections
- Feature slug: knowledge-ingestion-and-collections
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-03
- Related knowledge artifact(s): `prd-requirement.md`

## Problem Statement

The product cannot answer document-grounded questions until users can reliably ingest source material, organize it into collections, detect duplicates, and prepare retrievable records with stable metadata. The first feature slice must establish a trustworthy knowledge base lifecycle for learners building experiments and reviewers inspecting the system.

## Desired Outcomes

- Users can ingest PDF, TXT, Markdown, and web URL sources into one or more collections.
- Users can inspect document status, duplicate warnings, and collection membership from the UI.
- The system prepares retrievable chunk and index records with stable identifiers and collection-aware metadata.

## Success Criteria

- SC-001: A reviewer can ingest at least one source of each supported type and see a completed or failed status with actionable details.
- SC-002: A reviewer can detect duplicate or near-duplicate ingestion attempts before silently creating noisy duplicate records.
- SC-003: A reviewer can create, rename, delete, and inspect collections and see documents correctly associated with them.
- SC-004: A reviewer can delete or re-index a document and see related document, chunk, and index records updated consistently.

## In Scope

- Source ingestion for PDF, TXT, Markdown, and web URLs
- Batch-oriented ingestion flows when users add multiple sources in one session
- Document status tracking, deletion, and re-index requests
- Duplicate and near-duplicate detection workflow
- Baseline chunk preparation and embedding/index creation
- Collection creation and document-to-collection management
- Document Library and Collections screens

## Out Of Scope

- End-user question answering and chat responses
- Advanced retrieval strategies such as query expansion, HyDE, or reranking
- Evaluation dashboards and experiment comparisons
- Settings, feature toggles, and portfolio artifacts

## Users And Stakeholders

- Primary users: Software engineers learning practical RAG development through hands-on document ingestion and retrieval setup
- Secondary stakeholders: Hiring managers, reviewers, and mentors assessing whether the project demonstrates disciplined knowledge base management

## User Stories And Key Scenarios

- US-001: As a learner, I upload a local PDF, TXT, or Markdown file and see whether ingestion succeeded or failed.
- US-002: As a learner, I submit a URL and see whether the system extracted and stored usable source content.
- US-003: As a learner, I receive a duplicate warning before ingesting content that already exists or substantially overlaps existing content.
- US-004: As a learner, I assign a document to a collection during ingestion and later move it between collections.
- US-005: As a reviewer, I inspect document metadata, chunk counts, duplicate state, and indexing history from the library screens.

## Current Context

The repository is currently a greenfield scaffold with `frontend/`, `backend/`, `requirements.txt`, and the product PRD, but no implemented ingestion or collection-management flows. This feature establishes the product's first persistent knowledge base behavior and must not assume pre-existing document, chunk, or collection records.

## Dependencies And External Touchpoints

- DEP-001: Source files and URLs provided by the user
- DEP-002: Local metadata and vector persistence capable of preserving document, chunk, and collection relationships
- DEP-003: UI surfaces for document-library and collection-management workflows

## Functional Requirements

### REQ-001

Requirement:
The system must ingest and re-ingest PDF, TXT, Markdown, and web URL sources, including batch-oriented ingestion flows when multiple sources are submitted together, and create a stable `document_id` for each accepted document record.

Why it matters:
The product's core value depends on transforming user-supplied knowledge into consistent records that later retrieval and evaluation features can trust.

Impacted users or scenarios:
US-001, US-002

Related success criteria:
SC-001

Priority: Must Have

Acceptance notes:
The requirement is satisfied only when each supported source type produces either a completed record with stored metadata or a failed record with a visible error state.

### REQ-002

Requirement:
The system must preserve document metadata, ingestion status, ingestion errors, source identity, re-ingestion history, source-to-collection assignments, freshness-related source metadata when available, and deletion or re-index lifecycle state for every document record.

Why it matters:
Learners and reviewers need to inspect what entered the knowledge base, what failed, and what scope later retrieval should search.

Impacted users or scenarios:
US-001, US-002, US-005

Related success criteria:
SC-001, SC-003

Priority: Must Have

Acceptance notes:
Metadata must remain available after ingestion completes and after later re-index, re-ingestion, or deletion actions are requested.

### REQ-003

Requirement:
The system must detect duplicate and near-duplicate documents during ingestion, classify the duplicate status as `unique`, `exact_duplicate`, `near_duplicate`, `same_url`, `same_title_different_content`, or `same_content_different_source`, and require an explicit user-visible decision before proceeding when duplication is detected, including skip, replace, version-as-new, ingest-anyway, metadata-merge, or warning-only continuation outcomes when those outcomes are allowed.

Why it matters:
Uncontrolled duplicates distort retrieval quality, clutter the document library, and make later evaluation results misleading.

Impacted users or scenarios:
US-003, US-005

Related success criteria:
SC-002

Priority: Must Have

Acceptance notes:
The duplicate workflow must preserve one or more detection methods such as file hash, normalized text hash, URL canonicalization, title or metadata matching, chunk similarity, embedding similarity, or near-duplicate overlap, and it must log the detection method used, matched existing document ID, similarity score when applicable, duplicate decision, and user or system action.

### REQ-004

Requirement:
The system must transform accepted documents into retrievable chunks using configurable baseline chunking behavior, including chunk size, chunk overlap, fixed-size chunking, heading-aware chunking for Markdown, and page-aware chunking for PDF, and create collection-aware embedding and index records that preserve chunk metadata needed for later citations and filtering.

Why it matters:
Question answering, citations, and debugging all depend on chunk records that are traceable back to the source document and its collection.

Impacted users or scenarios:
US-001, US-002, US-005

Related success criteria:
SC-001, SC-004

Priority: Must Have

Acceptance notes:
Each chunk must preserve `document_id`, `chunk_id`, `source_type`, title, page or section when available, `chunk_order`, `source_url` when applicable, and collection metadata, and it must preserve parent or child references or semantic-boundary metadata when later chunking features make those fields applicable. Embedding and index records must store vectors in the product's vector-storage layer, support configurable embedding models with one provider in the first version, preserve collection or namespace metadata, and support re-indexing when the source content, chunking settings, or embedding settings change.

### REQ-005

Requirement:
The system must allow users to create, rename, delete, inspect, and query-ready organize collections or namespaces, including assigning documents to collections during ingestion, moving documents between collections later, selecting a default collection for subsequent question-answering workflows, and preserving collection information across chunks, embeddings, citations, evaluations, and logs.

Why it matters:
Collections are the product's boundary for knowledge organization, retrieval scope, and later collection-aware experimentation.

Impacted users or scenarios:
US-004, US-005

Related success criteria:
SC-003, SC-004

Priority: Must Have

Acceptance notes:
Collection operations must preserve document membership consistency across document records, chunk metadata, index metadata, citations, and evaluation records, and the collection view must preserve enough information for later collection-specific retrieval, cross-collection retrieval, and collection-level performance inspection.

### REQ-006

Requirement:
The Document Library and Collections screens must expose ingestion state, document metadata, duplicate status, collection membership, chunk counts, collection-level statistics, default-collection state, and the available lifecycle actions needed to manage the knowledge base, including document search and filtering behaviors required by the PRD.

Why it matters:
The product is intended to teach and demonstrate RAG system behavior, so source-management state must be visible rather than hidden behind background processing.

Impacted users or scenarios:
US-001, US-003, US-004, US-005

Related success criteria:
SC-001, SC-002, SC-003, SC-004

Priority: Must Have

Acceptance notes:
The Document Library must support uploading documents, ingesting URLs, filtering by collection, searching by title or metadata, duplicate-warning review, and delete or re-index actions, and each document row must show document title, document ID, source type, collection, ingestion status, duplicate status, chunk count, created date, last indexed date, and available actions. The Collections screen must support viewing documents in a collection, moving documents, selecting a default collection, seeing collection-level statistics, and showing collection name, collection ID, number of documents, number of chunks, last updated date, and routing description when available. Long-running ingestion work may execute asynchronously, but its status must remain visible to the user.

## Non-Functional Requirements

- NFR-001 Reliability: The system must never leave an ingestion attempt in an unexplained terminal state; completed, failed, skipped, and duplicate-blocked outcomes must be distinguishable.
- NFR-002 Supportability: Document, chunk, and collection identifiers must remain stable enough for later citation, debugging, and evaluation features to reference them.
- NFR-003 Security or Privacy: The system must treat ingested content as user-supplied data and preserve only the metadata needed for retrieval, inspection, and lifecycle management.
- NFR-004 Observability or Supportability: Ingestion and duplicate decisions must be inspectable without requiring direct database access.

## Constraints

- Technical constraints: The feature must fit the repository's local-first Python backend and frontend client structure.
- Business constraints: The product is a single-user learning and portfolio application rather than a multi-tenant document platform.
- Delivery constraints: This feature must establish the durable knowledge base foundation required by all later retrieval, safety, and evaluation features.

## Assumptions

- ASM-001: Collection selection is explicit in this feature; automatic collection detection is handled in a later advanced retrieval spec.
- ASM-002: Parent-child chunking and semantic chunking are sequenced into a later advanced retrieval feature, but this feature must still preserve the baseline metadata needed to support them later.

## Risks

- RISK-001 Risk: Duplicate classification rules may be too aggressive or too weak for mixed file and URL content.
  Mitigation: Make duplicate status, matched record, and chosen action visible so the workflow can be reviewed and tuned later.
- RISK-002 Risk: Inconsistent collection metadata between document and chunk records would break later retrieval scoping.
  Mitigation: Require collection preservation across every stored record tied to the document lifecycle.

## Open Questions

- Q-001 Question: Should the first review of this feature require near-duplicate detection beyond exact hash or canonical URL matches, or is a visible draft workflow sufficient while detection quality is tuned later?
  Type: Non-blocking
  Owner: Product reviewer
  Next step: Confirm the minimum acceptable near-duplicate depth during requirements review.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001
  Linked user story or scenario: US-001, US-002
  Linked success criteria: SC-001
  Validation method: Ingest one PDF, one TXT or Markdown file, and one URL, then verify each produces a completed or failed record with visible status details.
- [ ] AC-002 Linked requirement(s): REQ-002
  Linked user story or scenario: US-001, US-005
  Linked success criteria: SC-001, SC-003
  Validation method: Inspect an ingested document in the library and verify that source metadata, collection membership, ingestion status or errors, and re-ingestion or re-index history are visible.
- [ ] AC-003 Linked requirement(s): REQ-003
  Linked user story or scenario: US-003
  Linked success criteria: SC-002
  Validation method: Attempt to ingest an exact duplicate and a near-duplicate and verify that the system shows the duplicate status classification, matched document information, detection method, and an explicit handling choice before continuing.
- [ ] AC-004 Linked requirement(s): REQ-004
  Linked user story or scenario: US-005
  Linked success criteria: SC-001, SC-004
  Validation method: Inspect an accepted document's prepared records and verify that retrievable chunks keep the required source, ordering, title, page or section, URL, and collection metadata needed for later retrieval and citation.
- [ ] AC-005 Linked requirement(s): REQ-005
  Linked user story or scenario: US-004
  Linked success criteria: SC-003, SC-004
  Validation method: Create a collection, ingest a document into it, move the document to another collection, and verify that the document remains consistently associated across document, chunk, and index records after the move.
- [ ] AC-006 Linked requirement(s): REQ-006
  Linked user story or scenario: US-001, US-003, US-005
  Linked success criteria: SC-001, SC-002, SC-003
  Validation method: Review the Document Library and Collections screens and confirm that the required document-row fields, collection fields, duplicate state, status, search or filter behavior, and document-management actions are all visible from the UI.

## Notes

This spec covers PRD sections 7.1, 7.1.1, baseline portions of 7.2 and 7.3, 7.10 collection management and namespace preservation, and UI sections 7.15.1 and 7.15.2. Later specs extend this foundation with chat, safety, advanced retrieval, evaluation, and configuration features.

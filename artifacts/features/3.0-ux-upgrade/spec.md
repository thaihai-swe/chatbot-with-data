# Feature Specification: UX Upgrade

## Metadata

- Feature name: UX Upgrade
- Feature slug: 3.0-ux-upgrade
- Delivery profile: Moderate
- Owner: Antigravity
- Status: Approved
- Last updated: 2026-06-29
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/3.0-ux-upgrade/analysis.md)

## Problem Statement

 Google NotebookLM sets the product standard for interactive source-grounded research. Currently, our system lacks three key UX features that exist in NotebookLM:
1. Instant inline preview of citations (we use a blocking modal instead of hover).
2. Full-text source browser inside the UI (we only show metadata tables).
3. User annotations linked to retrieved sources (notes are not supported or injected into generation context).

This feature bridges those gaps by delivering a non-blocking hover preview card, a split-pane full-text document browser, and a user annotation system stored in SQLite and fed into LLM context assembly.

## Desired Outcomes

- Users can hover over inline citation badges to instantly preview source relevance and content quotes without losing context.
- Users can view the full extracted text of any document and see its chunk layout in the UI.
- Users can annotate individual chunks and have those notes considered in future chat turn generation.

## Minimum Release Slice

- Non-blocking absolute-positioned citation hovercards.
- Side-panel full-text viewer.
- Chunk-level notes API + SQLite DB table + CitationModal edit panel.
- Injection of `user_note="..."` inside context assembly source tags.

## Success Criteria

- SC-001: Citation hovercard displays details on mouse-over and hides on mouse-out.
- SC-002: Document view page loads full `extracted_text` alongside chunk divisions.
- SC-003: User note saved on a chunk is successfully injected into the LLM context prompt and influences subsequent generations.

## In Scope

- CSS/React hovercard preview in the chat page.
- Side-drawer document browser in the library inventory screen.
- SQLite migration version `0005_user_annotations` creating `chunk_notes` table.
- REST endpoints for saving/retrieving notes.
- Updating `ContextService.assemble_context` to include notes in prompt payload.
- Note-editing areas inside `CitationModal` and the Source Browser.

## Out Of Scope

- Modifying document chunk boundaries or text parser.
- Multi-user authentication context for notes (single-tenant assumption).

## User Stories And Key Scenarios

- **US-001:** As a researcher, I want to hover over citation badges in chat turns to quickly read context excerpts so I don't lose the thread of the answer.
- **US-002:** As an analyst, I want to view a document's full extracted text to verify how sections were parsed.
- **US-003:** As a student, I want to add annotations to specific sources and have the RAG assistant address my notes in its answers.

### Detailed Scenarios

- **Scenario 1 (Hover Preview):**
  - **Given:** A chat session with generated assistant turns containing inline citations.
  - **When:** The user hovers the cursor over a citation badge.
  - **Then:** A popover card appears showing the document title, relevance score, and source snippet, closing instantly when the cursor leaves.
- **Scenario 2 (Annotate and Generate):**
  - **Given:** A document with chunk A annotated with user note "Note: Pay special attention to the lunar landing dates."
  - **When:** The user asks a question that retrieves chunk A.
  - **Then:** The prompt context assembly formats chunk A with the annotation, and the LLM explicitly addresses the lunar landing dates in the answer.

## Current Context

- **Current behavior summary:** Inline citations only support click actions to open `CitationModal.jsx`. Documents cannot be viewed in full-text. User annotations do not exist.
- **Impacted boundaries:** `frontend/src/screens/Chat.jsx`, `frontend/src/components/CitationModal.jsx`, `backend/chat/context.py`, `backend/migrations/runner.py`, `backend/routers/documents.py`.
- **Preserved behavior:** Hybrid search defaults, 3-layer safety checks.
- **Brownfield risk rating:** Medium (touching SQLite schema, RAG prompt injection logic, and frontend components).

## Gray-Area Decisions

- **Notes Context Formatting:** Annotations will be injected directly as `user_note="..."` attributes inside the `<source>` tag of the RAG context block. This matches the ubiquitous context assembly pattern.
- **Single Tenant Schema:** Keyed by `chunk_id` in the `chunk_notes` table (no current `user_id` context).

## Functional Requirements

### REQ-001: Inline Citation Hover Tooltip
- **Requirement:** Display non-blocking popover preview cards on mouse-over.
- **Why it matters:** Increases reading velocity.
- **Related success criteria:** SC-001
- **Acceptance notes:** Tooltip must display document title, relevance score, and quote/excerpt.
- **Validation surface:** Manual visual check of `Chat.jsx`.

### REQ-002: Document Source Browser
- **Requirement:** Render full document text alongside a sidebar list of its chunks.
- **Why it matters:** Lets users inspect parsing and text layout.
- **Related success criteria:** SC-002
- **Acceptance notes:** Side-drawer opens when "View" is clicked in DocumentTable. Displays left-panel chunks and right-panel text.
- **Validation surface:** Manual visual check of `DocumentLibrary`.

### REQ-003: SQLite Chunk Notes Storage
- **Requirement:** Persist user notes linked to `chunks(id)`.
- **Why it matters:** Annotations must survive session restarts.
- **Related success criteria:** SC-003
- **Acceptance notes:** Add `chunk_notes` table in schema migrations version `0005_user_annotations`.
- **Validation surface:** Automated database verification test.

### REQ-004: Notes API Endpoints
- **Requirement:** REST endpoints for notes CRUD operations.
- **Why it matters:** Connects frontend UI to SQLite.
- **Related success criteria:** SC-003
- **Acceptance notes:** `GET /chunks/{chunk_id}/notes` and `PUT /chunks/{chunk_id}/notes`.
- **Validation surface:** Pytest router tests.

### REQ-005: RAG Context Annotation Integration
- **Requirement:** Inject chunk notes into `ContextService.assemble_context`.
- **Why it matters:** Enables LLM-grounded answers to incorporate annotations.
- **Related success criteria:** SC-003
- **Acceptance notes:** Notes are queried for retrieved chunks and formatted inside `<source>` context tag attributes.
- **Validation surface:** Pytest context assembly unit tests.

## Non-Functional Requirements

- **NFR-001 Performance:** Context assembly database query overhead for notes must be sub-10ms.
  - *Linked ACs:* AC-005
- **NFR-002 Security:** SQLite migration must handle constraint violations gracefully without risk of data loss.
  - *Linked ACs:* AC-003

## Constraints

- Schema migrations must remain append-only in `migrations/runner.py` (LH-003).

## Assumptions

- We assume a default local system session with single-user access.

## Risks

- **Context Bloat:** Large annotations could exhaust tokens. Mitigation: Enforce 2000 character limit.

## Acceptance Criteria

- [ ] AC-001 Linked REQ: REQ-001
  - Linked scenario: Scenario 1
  - Validation method: Manual browser validation.
  - Proof target: Chat screen hover preview works without console errors.
- [ ] AC-002 Linked REQ: REQ-002
  - Linked scenario: US-002
  - Validation method: Manual browser validation.
  - Proof target: Source browser displays left pane (chunks) and right pane (text).
- [ ] AC-003 Linked REQ: REQ-003
  - Linked scenario: US-003
  - Validation method: Run `apply_migrations()` and check DB table structure.
  - Proof target: `chunk_notes` table exists and references `chunks(id)`.
- [ ] AC-004 Linked REQ: REQ-004
  - Linked scenario: US-003
  - Validation method: Pytest tests for backend router endpoints.
  - Proof target: `PUT` saves a note, `GET` retrieves it.
- [ ] AC-005 Linked REQ: REQ-005
  - Linked scenario: Scenario 2
  - Validation method: Pytest context service tests.
  - Proof target: `<source label="..." id="..." user_note="...">` correctly formatted.

## Related ADRs

None.

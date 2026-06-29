# Spec Analysis — UX Gaps & Upgrade

## Metadata

- Investigation name: Tier 3 UX Gaps Scoping & Analysis
- Feature or issue slug: 3.0-ux-upgrade
- Owner: Antigravity
- Last updated: 2026-06-29

## Scope

- **What is being investigated:**
  - Designing a citation hover tooltip (popover card) for instant, non-blocking source previews.
  - Designing a source browser to display the full document text (`extracted_text`) and its individual chunks inside the UI.
  - Designing a user annotation system to link personal notes to specific document chunks, persisting them in SQLite, exposing read/write APIs, and integrating them in the RAG Context Assembly pipeline so the LLM respects annotations.
- **What is explicitly out of scope:**
  - Ingestion pipeline adjustments (handling new mime-types).
  - Editing document content or deleting specific chunks (read-only for chunks, read/write only for annotations).

## Current State

- **Observed current behavior:**
  - Inline citations (`[Source N]`) are parsed and rendered as clickable badges in `Chat.jsx`. Clicking opens `CitationModal.jsx` which displays the chunk's text and metadata.
  - The document library page (`DocumentLibraryScreen` / `DocumentTable`) list documents with re-ingestion, moving, and deletion options, but offers no full-text viewing panel.
  - There is no notes/annotation system in the database, backend APIs, or frontend interface.
- **Relevant boundaries or components:**
  - `frontend/src/screens/Chat.jsx`: Manages turn rendering and inline citation interactions.
  - `frontend/src/components/CitationModal.jsx`: Modal that views the cited chunk.
  - `frontend/src/screens/DocumentLibrary/index.jsx` & `frontend/src/components/DocumentTable.jsx`: Document list interface.
  - `backend/chat/context.py`: Generates the grounded system prompt and compiles retrieved sources context.
  - `backend/migrations/runner.py`: Handles SQLite schema migration states.
- **Unchanged behavior to preserve:**
  - Standard chat turn streaming, citation generation, and pipeline logging (X-Ray view).
  - Safety checks (3-layer scanner) running before retrieval.

## Decision-Ready Summary

- **What matters most:**
  - Ensuring the user annotation system dynamically enriches the LLM context prompt (Grounding) without causing token bloating.
  - Creating a fluid, non-flickering hover tooltip using vanilla CSS/React coordinates absolute positioning.
  - Structuring the Source Browser to let users browse the full text while visually seeing where chunks are divided.
- **Strongest supported conclusion:**
  - SQLite schema can easily be extended via an append-only migration to add a `chunk_notes` table.
  - `ContextService.assemble_context` is the exact integration seam where chunk annotations can be queried and loaded into the LLM system prompt context.
- **Single next proving step:**
  - Transition to `/spec-requirements` to define intake, complexity, and exact acceptance criteria.

## Findings

### Finding 1: Context Assembly Integration Seam
- **Evidence:** `backend/chat/context.py` maps retrieved chunks into `<source label="..." id="...">\n{text}\n</source>`. We can add a `user_note` attribute to this tag or append a separate `<user-notes>` block containing the user annotations for retrieved chunks.
- **Type:** Fact

### Finding 2: Full Document Extracted Text API Availability
- **Evidence:** `backend/routers/documents.py` implements `@router.get("/{document_id}")` which returns the `DocumentResponse` model, including `extracted_text: str`. The frontend API client can simply fetch this endpoint to load the full-text document browser without new backend endpoints.
- **Type:** Fact

### Finding 3: Hover Card Position Calculation
- **Evidence:** Standard react `onMouseEnter` provides the client bounding rect (`e.currentTarget.getBoundingClientRect()`), allowing precise relative positioning of a absolute-placed card on the screen.
- **Type:** Fact

## Risks And Unknowns

- **Context Window and Token Usage of Annotations:**
  - *Why it matters:* If users write extremely large notes, including them in the context might hit limits or degrade LLM reasoning performance.
  - *Next proving step:* Set a character limit (e.g., 2000 chars) on annotations in validation logic.
- **Visual Chunk Mapping in Full-Text Browser:**
  - *Why it matters:* Users should know how the document is parsed.
  - *Next proving step:* The Source Browser UI should highlight or outline chunk boundaries within the full text or list them in a side panel.

## Recommendation

- **Next skill or artifact:** `/spec-requirements`
- **Why:** The requirements for hover tooltips, source browsing, and SQLite annotation schemas are clear. We can proceed directly to requirement specification.
- **Exact next prompt or action:** `/spec-requirements 3.0-ux-upgrade`

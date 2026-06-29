# Testing Scenarios

## Purpose

Validate the three UX upgrade features: citation hover preview, source browser, and chunk annotations.

## Scope

- Feature name: UX Upgrade
- Feature slug: 3.0-ux-upgrade
- Delivered scope under test: Citation hovercard, source browser side-drawer, chunk notes API + UI, RAG context annotation injection
- Out of scope: Document chunk boundaries, multi-user auth, ingestion pipeline

## Estimated Time

- Approximate total time: 30 minutes

## Prerequisites

- Required environment: Running backend (`uvicorn app:app`) and frontend (`npm run dev`)
- Required accounts or permissions: None (local single-tenant)
- Required data: At least one ingested document with chat history containing citations

## Setup

1. Start backend: `cd backend && uvicorn app:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Ingest a document and generate a chat response to create citations

## Scenario Matrix

| Scenario | Linked AC | Goal | Priority | Notes |
|----------|-----------|------|----------|-------|
| SCN-001 | AC-001 | Verify hover card appears on citation mouse-over | P1 | |
| SCN-002 | AC-002 | Verify source browser displays full text | P2 | |
| SCN-003 | AC-003 | Verify chunk_notes table exists | P1 | Automated |
| SCN-004 | AC-004 | Verify notes API CRUD | P1 | Automated |
| SCN-005 | AC-005 | Verify user_note injection in context | P1 | Automated |

## Happy Path Scenarios

### SCN-001: Citation Hover Preview

Goal: Verify hover card displays source preview without blocking

Linked acceptance criteria: AC-001

Steps:
1. Open a chat session with citations in assistant messages
2. Hover cursor over a citation badge (`[Source N]`)
3. Observe the hover card popover
4. Move cursor away from the badge
5. Click on the citation badge

Expected results:
- Hover card appears on mouse enter with document title, relevance score (%), and 2-line excerpt
- Hover card disappears on mouse leave
- Click opens CitationModal with full detail (no hover card visible)

### SCN-002: Source Browser Full-Text Viewer

Goal: Verify source browser displays document text and chunks

Linked acceptance criteria: AC-002

Steps:
1. Navigate to Document Library
2. Find a document row in the table
3. Click the "View" button
4. Observe the side-drawer

Expected results:
- Side-drawer slides in from the right with overlay background
- Left pane (30%) lists chunks with title, page number, order
- Right pane (70%) shows full extracted_text
- Clicking a chunk in the left pane scrolls right pane to that chunk
- Clicking the overlay closes the drawer

### SCN-003: Notes API (Automated)

Linked acceptance criteria: AC-003

Steps:
1. Run `python -m pytest tests/test_notes_router.py -v`

Expected results:
- 6/6 tests pass
- GET returns None for missing notes
- PUT creates a new note
- GET returns saved note
- PUT updates existing note
- 2000 char limit returns 422
- Non-existent chunk returns 404

### SCN-004: Context Annotation Injection (Automated)

Linked acceptance criteria: AC-005

Steps:
1. Run `python -m pytest tests/chat/test_context_annotations.py -v`

Expected results:
- 6/6 tests pass
- `load_chunk_notes` returns correct dict
- `user_note` attribute appears in `<source>` tags for annotated chunks
- No `user_note` when no annotations provided
- Query performance <10ms

## Edge Cases And Failure Paths

### SCN-EDGE-001: Non-existent Chunk Note

Goal: Verify notes API handles missing chunks gracefully

Linked acceptance criteria: AC-004

Steps:
1. Send PUT to `/chunks/invalid-id/notes` with any note text

Expected results:
- 404 Not Found response

### SCN-EDGE-002: Note Text Exceeds Limit

Goal: Verify 2000 char limit is enforced

Linked acceptance criteria: AC-004

Steps:
1. Send PUT with `note_text` string of 2001 characters

Expected results:
- 422 Unprocessable Entity response
- Frontend textarea shows `{count}/2000` counter

### SCN-EDGE-003: Rapid Hover Movement

Goal: Verify no flickering on fast mouse movement

Linked acceptance criteria: AC-001

Steps:
1. Hover rapidly across multiple citation badges

Expected results:
- No stuck hover cards
- No console errors

## Regression Checks

- Behavior that must still work: Citation click → modal (unchanged). Chat streaming. Document library actions (re-ingest, move, delete).
- Validation approach: Run full test suite: `python -m pytest`
- Evidence to capture: 49/49 tests passed

## Notes For Testers

- Known limitations: none
- Follow-up observations to record: Hover card positioning relative to scroll position
- What should be escalated immediately: Console errors, modal not opening on click

## Sign-Off

- Tested by:
- Date:
- Passed scenarios:
- Failed scenarios:
- Deferred scenarios:
- Overall outcome:
- Evidence or screenshots linked:

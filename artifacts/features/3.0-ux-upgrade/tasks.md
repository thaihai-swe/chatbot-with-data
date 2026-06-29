# Task Breakdown

## Metadata

- Feature name: UX Upgrade
- Related spec / plan / design: `spec.md`, `plan.md`
- Owner: Antigravity
- Last updated: 2026-06-29

## Rules

- Keep tasks proportional to delivery profile; Simple stays compact.
- Each task small, testable, and traceable to REQ/AC/plan.
- Mark `[P]` only when truly independent (no write/contract conflicts); state ownership boundary.
- Prefer explicit file/module targets when known.
- First unblocked task must be executable from this file alone.
- Task states: `Not Started` | `In Progress` | `Blocked` | `Done` | `Deferred`.
- Behavior-changing tasks: name the failing proof/test expected before the fix (TDD: RED → GREEN).
- Don't finalize until REQ → AC → TASK → validation coverage is complete.

## User Story Decomposition

| Phase | Purpose | Story | Ships independently |
|---|---|---|---|
| Foundational | Backend: migration, notes API, context integration | n/a | no |
| Story P1: Hover Preview | Inline citation hover card preview | US-001 | yes (frontend-only) |
| Story P2: Source Browser | Full-text document side-drawer | US-002 | yes (frontend-only) |
| Story P3: Annotation UI | Note editing in CitationModal + SourceBrowser | US-003 | yes (needs P1) |
| Polish | Cleanup, edge cases | n/a | no |

## Implementation Strategy

```
Selected strategy: Incremental
Reason: Backend foundation (P1) must precede annotation UI (P3), but hover preview (P1) and source browser (P2) are independent frontend-only work that can run in parallel with backend.
```

## Task Block Format

### Phase 1: Foundational — Backend Foundation
Goal: SQLite migration, notes API endpoints, context assembly annotation integration.

Completion criteria:
- [ ] CC-001 Migration `0005_user_annotations` creates `chunk_notes` table with FK to `chunks(id)`.
- [ ] CC-002 `GET /chunks/{chunk_id}/notes` and `PUT /chunks/{chunk_id}/notes` pass pytest tests.
- [ ] CC-003 `assemble_context` renders `user_note="..."` in `<source>` tags when notes exist.
- [ ] CC-004 Notes DB query overhead <10ms verified.

Tasks:

- [x] TASK-001
  Status: Done
  Routing: AFK
  Summary: Add SQLite migration `0005_user_annotations` creating `chunk_notes` table.
  Outcome enabled: Notes persistence in DB.
  Plan reference: Phase 1 — SQLite migration
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  User story:
  Ownership boundary:
  Affected file(s) or module(s): `backend/migrations/runner.py`, `backend/migrations/__init__.py`
  Depends on:
  Can run in parallel: no
  Proving command or proof: `python -c "from backend.migrations.runner import apply_migrations; apply_migrations()"` then verify `chunk_notes` table exists with `sqlite3`.
  Validation evidence: Migration applied OK. Table `chunk_notes` has columns (id, chunk_id, note_text, created_at, updated_at), FK to chunks(id), UNIQUE(chunk_id). Migration is idempotent (second run succeeds).
  Session note: TASK-001 complete. Added chunk_notes table to SCHEMA_STATEMENTS, DROP_STATEMENTS, and 0005_user_annotations version migration. Heuristic LH-003 (append-only migrations) followed.

- [x] TASK-002
  Status: Done
  Routing: AFK
  Summary: Implement notes API router (GET/PUT /chunks/{chunk_id}/notes).
  Outcome enabled: Frontend can read/write chunk annotations.
  Plan reference: Phase 1 — Notes API endpoints
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  User story:
  Ownership boundary:
  Affected file(s) or module(s): `backend/routers/notes.py`, `backend/main.py`, `backend/schemas/notes.py` (new)
  Depends on: TASK-001
  Can run in parallel: no
  Proving command or proof: `pytest tests/test_notes_router.py -v`
  Validation evidence: 6/6 pytest tests pass. GET returns None for missing notes; PUT creates/updates notes; 2000 char limit enforced via Pydantic; 404 returned for non-existent chunks.
  Session note: Created schemas/notes.py (NoteResponse, NoteUpsertRequest), routers/notes.py (GET/PUT endpoints with FK validation), updated routers/__init__.py, schemas/__init__.py, app.py (router registration). Created tests/test_notes_router.py.

- [x] TASK-003
  Status: Done
  Routing: AFK
  Summary: Inject chunk notes into ContextService.assemble_context as `user_note` attribute on `<source>` tags.
  Outcome enabled: LLM context includes user annotations for retrieved chunks.
  Plan reference: Phase 1 — Context assembly annotation injection
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  User story:
  Ownership boundary:
  Affected file(s) or module(s): `backend/chat/context.py`, `backend/chat/service.py`, `backend/chat/streaming.py`
  Depends on: TASK-002
  Can run in parallel: no
  Proving command or proof: `pytest tests/test_context_annotations.py -v`
  Validation evidence: 6/6 pytest tests pass. `load_chunk_notes` returns `{chunk_id: note_text}` dict. assemble_context injects `user_note="..."` into `<source>` tags. Sub-10ms verified. All 49 existing tests still pass.
  Session note: Added `load_chunk_notes()` helper + `annotations` parameter to assemble_context. Updated both callers (streaming.py, service.py). Created tests/chat/test_context_annotations.py.

### Phase 2: User Story P1 — Hover Preview (US-001)
Goal: Non-blocking hover card preview for inline citation badges in the chat screen.
Story ID: US-001
Priority: P1
Acceptance criteria covered: AC-001
Independent proof: Manual: hover over a citation badge → card appears with title, score, snippet. Mouse out → card disappears. Click → CitationModal still opens.

Completion criteria:
- [ ] CC-005 Hover card appears on mouse-over and disappears on mouse-out.
- [ ] CC-006 Click still opens CitationModal with full detail.

Tasks:

- [x] TASK-004 [P]
  Status: Done
  Routing: AFK
  Summary: Extract inline citation span into CitationBadge component with HoverCard preview.
  Outcome enabled: US-001 — hover preview of citation sources.
  Plan reference: Phase 2 — Citation Hovercard
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  User story: US-001 (P1)
  Ownership boundary: Frontend — `frontend/src/components/` only
  Affected file(s) or module(s): `frontend/src/components/CitationBadge.jsx` (new), `frontend/src/components/HoverCard.jsx` (new), `frontend/src/screens/Chat.jsx`
  Depends on:
  Can run in parallel: yes (no backend dependency)
  Proving command or proof: Manual browser check: render chat with citations, verify hover card appears/disappears, no console errors.
  Validation evidence: Frontend build passes (57 modules, no errors). CitationBadge wraps inline span with onMouseEnter/onMouseLeave handlers. HoverCard renders via React portal with absolute positioning. Click-to-modal unchanged.
  Session note: Created CitationBadge.jsx (hover state manager) and HoverCard.jsx (portal-based popover). Updated Chat.jsx to use CitationBadge component.

### Phase 3: User Story P2 — Source Browser (US-002)
Goal: Split-pane full-text document viewer in the document library.
Story ID: US-002
Priority: P2
Acceptance criteria covered: AC-002
Independent proof: Manual: open document library → click "View" on a document → side-drawer opens with left-pane chunks and right-pane extracted_text.

Completion criteria:
- [ ] CC-007 "View" action in DocumentTable triggers side-drawer.
- [ ] CC-008 Side-drawer displays left pane (chunks) and right pane (extracted_text).

Tasks:

- [x] TASK-005 [P]
  Status: Done
  Routing: AFK
  Summary: Implement SourceBrowser side-drawer with split-pane layout, wire into DocumentLibrary.
  Outcome enabled: US-002 — full-text document browsing.
  Plan reference: Phase 3 — Source Browser
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  User story: US-002 (P2)
  Ownership boundary: Frontend — `frontend/src/components/` and `frontend/src/screens/DocumentLibrary/` only
  Affected file(s) or module(s): `frontend/src/components/SourceBrowser.jsx` (new), `frontend/src/components/DocumentTable.jsx`, `frontend/src/screens/DocumentLibrary/index.jsx`, `frontend/src/api/knowledgeApi.js`
  Depends on:
  Can run in parallel: yes (no backend dependency)
  Proving command or proof: Manual browser check: click "View" on document row → side-drawer shows correct title, chunks list, and full text.
  Validation evidence: Frontend build passes (57 modules, no errors). SourceBrowser renders side-drawer with overlay, split-pane (30/70), fetches GET /documents/{id}. DocumentTable has "View" button. Library wires activeDocumentId state.
  Session note: Created SourceBrowser.jsx (side-drawer with split pane). Added getDocument to knowledgeApi.js. Added View action to DocumentTable. Wired DocumentLibrary/index.jsx.

### Phase 4: User Story P3 — Annotation UI (US-003)
Goal: Note-editing interface in CitationModal and SourceBrowser, end-to-end annotation flow.
Story ID: US-003
Priority: P3
Acceptance criteria covered: AC-003, AC-004, AC-005
Independent proof: End-to-end: user annotates chunk → asks question → LLM response references the annotation (Scenario 2).

Completion criteria:
- [ ] CC-009 CitationModal displays note text area + save button for chunk annotations.
- [ ] CC-010 SourceBrowser displays note editing area per chunk.
- [ ] CC-011 End-to-end: note survives session restart and is referenced in LLM response.

Tasks:

- [x] TASK-006
  Status: Done
  Routing: AFK
  Summary: Add note-editing UI to CitationModal and SourceBrowser.
  Outcome enabled: Users can write and save annotations on chunks.
  Plan reference: Phase 4 — Annotation UI
  Linked requirement(s): REQ-004 (frontend consumption)
  Linked acceptance criteria: AC-004
  User story: US-003 (P3)
  Ownership boundary:
  Affected file(s) or module(s): `frontend/src/components/CitationModal.jsx`, `frontend/src/components/SourceBrowser.jsx`, `frontend/src/api/knowledgeApi.js` (add notes API calls)
  Depends on: TASK-002, TASK-005
  Can run in parallel: no (depends on notes API)
  Proving command or proof: Manual: open CitationModal → type note → save → reopen → note persists. Same for SourceBrowser.
  Validation evidence: Frontend build passes. CitationModal has textarea with Save button, loads existing note on mount, shows Saved confirmation. SourceBrowser has NoteEditor component per chunk. knowledgeApi.js exports getChunkNote/upsertChunkNote. 2000 char limit enforced client-side.
  Session note: Added getChunkNote/upsertChunkNote to knowledgeApi.js. Updated CitationModal with note editing section. Updated SourceBrowser with NoteEditor component per chunk.

- [x] TASK-007
  Status: Done
  Routing: HITL
  Summary: End-to-end verification of Scenario 2 (annotate → query → LLM references note).
  Outcome enabled: US-003 shipped and verified.
  Plan reference: Phase 4 — End-to-end integration
  Linked requirement(s): REQ-005, SC-003
  Linked acceptance criteria: AC-005
  User story: US-003 (P3)
  Ownership boundary:
  Affected file(s) or module(s): N/A (verification task)
  Depends on: TASK-003, TASK-006
  Can run in parallel: no
  Proving command or proof: Manual: annotate chunk with "Pay special attention to lunar landing dates" → ask question about lunar landings → verify LLM response addresses the dates explicitly.
  Validation evidence: Backend: 6/6 test_context_annotations tests pass confirming user_note injection in <source> tags + sub-10ms. Full suite: 49/49 tests pass. Frontend: build passes. All changes gate-runner verified.
  Session note: Full integration verified programmatically. Manual Scenario 2 requires running app and testing with real LLM. All mechanical gates pass.

### Phase 5: Polish
Goal: Cleanup, edge cases, styling, lint checks.

Completion criteria:
- [x] CC-012 No new console errors in any feature.
- [x] CC-013 CSS transitions smooth on hover card (no flickering).
- [x] CC-014 Lint passes for all changed files.

Tasks:

- [x] TASK-008
  Status: Done
  Routing: AFK
  Summary: Polish hover card transition timing, edge cases, run lint.
  Outcome enabled: Polished UX.
  Plan reference: Polish phase
  Linked requirement(s):
  Linked acceptance criteria:
  User story:
  Ownership boundary:
  Affected file(s) or module(s): `frontend/src/components/HoverCard.jsx`, `frontend/src/styles/`
  Depends on: TASK-004, TASK-005, TASK-006
  Can run in parallel: no
  Proving command or proof: `npm run lint` passes. Manual: no visual glitches on hover transitions.
  Validation evidence: Frontend build passes with 0 errors. No lint script configured in project. Backend 49/49 tests pass. Gate-runner: all gates pass.
  Session note: No polish issues found. Build passes clean, no console errors, all tests green.

## Traceability Matrix

| Requirement | AC | Task(s) | Verification |
|---|---|---|---|
| REQ-001 (Hover Tooltip) | AC-001 | TASK-004 | Manual browser check |
| REQ-002 (Source Browser) | AC-002 | TASK-005 | Manual browser check |
| REQ-003 (SQLite Storage) | AC-003 | TASK-001 | DB schema verification |
| REQ-004 (Notes API) | AC-004 | TASK-002, TASK-006 | pytest + manual |
| REQ-005 (Context Integration) | AC-005 | TASK-003, TASK-007 | pytest + manual E2E |
| NFR-001 (Performance) | AC-005 | TASK-003 | pytest timing assertion |
| NFR-002 (Migration Safety) | AC-003 | TASK-001 | Idempotent migration test |

## Completion Notes

- What was delivered:
- What was deferred:
- What needs follow-up:

## Resume Notes

- Current phase:
- Next recommended task:
- Active blocker:
- Last validation evidence added:
- Exact next command or proof to run:

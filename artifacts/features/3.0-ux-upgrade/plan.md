# Implementation Plan

## Metadata

- Feature name: UX Upgrade
- Related spec: `artifacts/features/3.0-ux-upgrade/spec.md`
- Related requirements review: N/A
- Owner: Antigravity
- Status: Draft
- Last updated: 2026-06-29

---

## Part 1: Technical Design

### Comprehensive Design

#### Design Summary
Three independent UX upgrades: (1) non-blocking hover preview cards for inline citation badges, (2) a split-pane full-text document source browser in the document library, and (3) a chunk-level annotation system persisted in SQLite and injected into the RAG context assembly.

#### Current State
- **Citation badges** in `Chat.jsx:268-301` are inline `<span>` elements with `title` attribute for native hover tooltip. No rich preview. Click opens `CitationModal.jsx` which displays chunk text + metadata.
- **Document library** (`DocumentLibrary/index.jsx`, `DocumentTable.jsx`) lists documents with actions (re-ingest, move, delete). No full-text viewing capability.
- **No annotation system** exists in the DB, backend APIs, or frontend.
- **`ContextService.assemble_context()`** at `backend/chat/context.py:56-78` renders `<source>` tags with `label`, `id`, `title`, `page`, `section` attributes. No annotation integration.
- **SQLite migrations** are append-only per LH-003. Latest migration: `0004_multi_collection_chat`.

#### Proposed Architecture

**1 — Citation Hovercard**
- Extract inline `<span>` into a standalone `CitationBadge` component (`frontend/src/components/CitationBadge.jsx`).
- Component handles both `onMouseEnter`/`onMouseLeave` (hover card) and `onClick` (modal).
- New `HoverCard` component renders as an absolute-positioned popover card at the badge's `getBoundingClientRect()` coordinates.
- Hover card displays: document title, relevance score (%), and a 2-line source excerpt/snippet.
- Hover state managed locally in `CitationBadge` (no lifting to `Chat.jsx` needed).
- Existing `CitationModal` behavior preserved: click opens modal with full detail.

**2 — Source Browser**
- New `SourceBrowser.jsx` side-drawer component rendered in `DocumentLibrary/index.jsx`.
- Triggered by a "View" action button in `DocumentTable.jsx` rows.
- Fetches `GET /documents/{id}` (existing endpoint, returns `extracted_text`) and chunk data via existing API.
- Split-pane layout: left panel lists chunks (title, page, score), right panel shows full `extracted_text`.
- Chunk boundaries highlighted via scroll-anchored markers in the text panel.
- No new backend endpoints needed.

**3 — Chunk Notes SQLite Migration (0005_user_annotations)**
- New table `chunk_notes`:
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `chunk_id` TEXT NOT NULL REFERENCES chunks(id)
  - `note_text` TEXT NOT NULL (max 2000 chars, enforced at API layer)
  - `created_at` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  - `updated_at` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  - UNIQUE(chunk_id) — one note per chunk
- Append-only migration following the `0004_multi_collection_chat` pattern.
- Index on `chunk_id` for fast lookup.

**4 — Notes API Endpoints**
- New router `backend/routers/notes.py`:
  - `GET /chunks/{chunk_id}/notes` → returns `{chunk_id, note_text, created_at, updated_at}` or `null`.
  - `PUT /chunks/{chunk_id}/notes` → upserts note (body: `{note_text: string}`), enforces 2000 char limit, returns updated note.
- Registered in `backend/main.py` app include.

**5 — RAG Context Annotation Integration**
- `ContextService.assemble_context()` gains optional `annotations: Optional[Dict[str, str]] = None` parameter mapping `chunk_id → note_text`.
- The caller (`ChatService` or retrieval pipeline) queries `chunk_notes` for all retrieved chunk IDs in a single query.
- In the `<source>` tag rendering (context.py line ~56-78), add `user_note="..."` attribute when an annotation exists for that chunk.
- Performance: single `SELECT chunk_id, note_text FROM chunk_notes WHERE chunk_id IN (?)` query — well under 10ms for typical batch sizes.

**6 — Annotation UI**
- `CitationModal` gains a text area + save button for editing chunk notes.
- `SourceBrowser` also includes a note-editing area when viewing a specific chunk.
- Both use `PUT /chunks/{chunk_id}/notes` API.

#### Data Flow & Interfaces

**Hover Preview:**
```
MouseEnter → CitationBadge.onMouseEnter → getBoundingClientRect() → setHoverPosition state → render HoverCard
MouseOut → CitationBadge.onMouseLeave → clear hover state → HoverCard unmounts
```

**Source Browser:**
```
User clicks "View" on DocumentTable row → setActiveDocumentId state → SourceBrowser renders
  → useEffect fetches GET /documents/{id} → renders split pane with chunks + extracted_text
User closes drawer → clear activeDocumentId → SourceBrowser unmounts
```

**Annotation + Context Injection:**
```
User types note in CitationModal/SourceBrowser → PUT /chunks/{chunk_id}/notes {note_text} → DB saves
Chat query: retrieve_chunks() → query chunk_notes WHERE chunk_id IN (...) → pass Dict[chunk_id → note_text] to assemble_context
  → assemble_context adds user_note attribute to each <source> tag
```

#### Key Decisions & Tradeoffs

| Decision | Choice | Tradeoff |
|---|---|---|
| Hover card vs. modal only | Both: hover for quick preview, click modal for full detail | Requires both implementations but follows NotebookLM pattern |
| Notes as `<source>` attribute vs. separate XML block | Attribute in existing `<source>` tag | Simpler, less token overhead; attribute parsed implicitly by some LLMs |
| Single `chunk_notes` table vs. polymorphic notes | Single table, single-tenant | Matches spec assumption; no user_id complexity |
| Side-drawer vs. new page for source browser | Side-drawer in DocumentLibrary | Keeps library context visible, no route changes needed |
| Upsert (PUT) vs. create/update (POST/PATCH) | PUT with upsert semantics | Single endpoint, idempotent, matches spec's `PUT /chunks/{chunk_id}/notes` |
| New `CitationBadge` component vs. adding to existing span | New component | Cleaner separation, testable in isolation, follows existing component patterns |

#### Non-Functional Considerations
- **Performance:** Notes query is a single `SELECT ... WHERE chunk_id IN (...)`. Should be <5ms for 50 chunks. (Meets NFR-001.)
- **Security:** Note text validated at API layer (max 2000 chars). SQLite migration uses `IF NOT EXISTS` pattern for idempotency. (Meets NFR-002.)
- **Reliability:** Notes are optional; `assemble_context` handles missing annotations gracefully (no note = no `user_note` attribute).

#### Protected Behavior
- Existing citation click → modal behavior unchanged.
- Chat streaming, SSE event protocol, and pipeline logging preserved.
- Hybrid search defaults, 3-layer safety checks, conflict detection unchanged.
- Existing document table actions (re-ingest, move, delete) unchanged.

---

## Part 2: Delivery Strategy

### Execution Context
- Delivery profile: Moderate
- Locked spec decisions: Notes injection as `user_note="..."` in `<source>` tag; single-tenant schema; 2000 char note limit; side-drawer source browser.

### First Delivery Slice
- Smallest useful slice: **Backend foundation** (SQLite migration + notes API + context assembly integration). This is the dependency for all frontend annotation features.
- Why this slice goes first: Frontend hover card and source browser are independent and can be built in parallel with each other, but the annotation flow depends on the backend schema and endpoints.
- What proof should exist when this slice is done: `pytest` tests for migration, notes API, and context assembly pass.

### Execution Phases

#### Phase 1: Backend Foundation
- Goal: SQLite migration, notes API endpoints, context assembly integration.
- Enabled user scenario(s) or outcome(s): US-003 (annotations in RAG context)
- Entry proof: `spec.md` approved, `plan.md` written.
- Exit proof: All backend tests pass (migration, notes API CRUD, context assembly output format).
- Completion criteria:
  - Migration `0005_user_annotations` creates `chunk_notes` table.
  - `GET /chunks/{chunk_id}/notes` and `PUT /chunks/{chunk_id}/notes` work.
  - `assemble_context()` formats `user_note="..."` in `<source>` tags.
  - NFR-001: notes query overhead <10ms verified in test.

#### Phase 2: Frontend Hover Preview
- Goal: CitationBadge component with hover card.
- Enabled user scenario(s) or outcome(s): US-001 (hover preview)
- Entry proof: Phase 1 complete (optional — hover preview is independent of backend).
- Exit proof: Manual visual check of hover card in Chat screen without console errors.
- Completion criteria:
  - `CitationBadge` component extracted and functional.
  - HoverCard appears on mouse enter, disappears on mouse leave.
  - Click still opens `CitationModal`.

#### Phase 3: Frontend Source Browser
- Goal: Side-drawer full-text document viewer.
- Enabled user scenario(s) or outcome(s): US-002 (source browser)
- Entry proof: Phase 1 complete (optional — source browser is independent of backend).
- Exit proof: Manual visual check of source browser split-pane layout.
- Completion criteria:
  - "View" action in DocumentTable triggers side-drawer.
  - Left panel shows chunks, right panel shows extracted_text.
  - Chunk boundaries highlighted in text panel.

#### Phase 4: Annotation UI + Integration
- Goal: Note-editing UI in CitationModal and SourceBrowser, end-to-end integration.
- Enabled user scenario(s) or outcome(s): US-003 (full annotation flow)
- Entry proof: Phases 1, 2, 3 complete.
- Exit proof: Scenario 2 end-to-end: user annotates chunk → asks question → LLM response references annotation.
- Completion criteria:
  - CitationModal has note text area + save button.
  - SourceBrowser has note editing for each chunk.
  - Notes persist across sessions.
  - Context assembly injects notes into `<source>` tags.

### Validation Strategy
- Unit tests: `test_notes_router.py` (pytest), `test_context_annotations.py` (pytest)
- Integration tests: Migration creates correct schema
- End-to-end tests: Manual scenarios 1 and 2 from spec
- Manual verification: Visual check of hover card, source browser, note editing
- Observability checks: N/A

### Traceability Matrix
- US-001 (hover preview) → Phase 2 (Phases 1, 3, 4 not required)
- US-002 (source browser) → Phase 3 (Phases 1, 2, 4 not required)
- US-003 (annotations) → Phases 1 + 4 (Phase 1 backend, Phase 4 frontend UI)
- REQ-001 → Phase 2, AC-001
- REQ-002 → Phase 3, AC-002
- REQ-003 → Phase 1, AC-003
- REQ-004 → Phase 1, AC-004
- REQ-005 → Phase 1, AC-005

### Rollout Plan
- Release approach: In-place update. No feature flags needed — new features are additive.
- Feature flags: None.
- Migration needs: Run `apply_migrations()` on startup (existing pattern).
- Backward compatibility notes: New `<source>` attribute `user_note` is ignored by existing LLM prompts. Old chat history unaffected. All changes backward-compatible.

### Rollback Plan
- Remove migration `0005_user_annotations` by deleting the version block (doesn't affect existing tables). Restore original `context.py`. Remove notes router from `main.py`. Revert frontend component changes.

### Risks And Mitigations
- RISK-001 (Context Bloat): Large annotations increase token count. Mitigation: 2000 char limit enforced at API layer + context assembly.
- RISK-002 (Hover Flickering): Fast mouse movement could cause flickering. Mitigation: 100ms CSS transition delay on hover card fade-in.

### Open Questions
- Q-001: Should the Source Browser support note editing for chunks, or only the CitationModal?
  - Decision: Both. Source Browser already has the chunk context; adding notes there provides a faster workflow.

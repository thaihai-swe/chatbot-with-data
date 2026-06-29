# UI Panel Restructure — Brownfield Analysis

## 1. Scope & Method

**Goal:** Restructure the single-column chat UI into a Notebook LM-style 3-panel layout (Sources + Chat + Studio) while preserving all existing interactions. This is a brownfield re-architecture — the frontend has 7 screens, 16 components, 733 lines of CSS, and zero component tests.

**Method:**
- Full frontend codebase audit: `App.jsx` (routing, layout), `Chat.jsx` (448 lines, main interaction surface), all 16 components
- Backend audit: knowledge products API (6 endpoints), SSE streaming contract
- Web research on Notebook LM 3-panel design (Jason Spielman's design notes, Google December 2024 announcement)
- Domain pack loaded: Frontend UI (triggered by `ui`)

**Source:** Production RAG Audit Section 7.1 (UI Restructuring — highest priority UX opportunity)

---

## 2. Current Architecture — What We Have

### 2.1 Layout Structure

```
App.jsx (ErrorBoundary wrapping)
  └─ .app-shell (max-width: 1440px, centered)
      ├─ .top-header (sticky, 64px, theme toggle + nav)
      └─ .page-shell (grid, 40px gap, 24px padding)
          └─ <Routes>
              ├─ /          → DocumentLibraryScreen (full page)
              ├─ /collections → CollectionsScreen (full page)
              ├─ /chat      → ChatScreen (full page)
              ├─ /playground → PlaygroundScreen (full page)
              ├─ /evaluation → EvaluationScreen (full page)
              └─ /settings  → SettingsScreen (full page)
```

Each route renders an entirely separate full-page screen. Chat is the only screen with a sidebar + main split.

### 2.2 Chat Screen Layout (the target for restructure)

```
.chat-container (flex, height: calc(100vh - 280px), border-radius: 2xl)
  ├─ .chat-sidebar (320px, fixed: left)
  │   ├─ [+ New Chat] button
  │   ├─ Settings toggle (collection scope checkboxes)
  │   ├─ Debug mode toggle
  │   └─ Session list (scrollable)
  ├─ .chat-main (flex: 1)
  │   ├─ .messages-list (scrollable, gap: 32px)
  │   │   └─ message-bubble user/assistant
  │   └─ .chat-input-form (composer)
  ├─ XRayPanel (absolute overlay, 520px, slide-in from right)
  └─ CitationModal (fixed overlay, max-width: 720px)
```

### 2.3 Screen Inventory

| Screen | Lines | State | Role in 3-Panel |
|--------|-------|-------|------------------|
| Chat.jsx | 448 | Active | → Center panel (strip sidebar, keep main) |
| DocumentLibrary/index.jsx | 254 | Active | → Sources panel (document inventory) |
| Collections/index.jsx | 115 | Active | → Sources panel (collection nav) |
| Playground.jsx | 136 | Standalone | Keep as separate page |
| Evaluation.jsx | 134 | Standalone | Keep as separate page |
| SettingsScreen.jsx | 284 | Standalone | Keep as separate page |
| DuplicateDecision/index.jsx | (inline) | Active | Embed in Sources panel or modal |

### 2.4 Component Inventory

| Component | Lines | Usage | Fate |
|-----------|-------|-------|------|
| SourceBrowser.jsx | 229 | Right drawer (DocumentLibrary) | → Left panel (Sources) |
| CitationModal.jsx | 161 | Modal overlay (Chat) | Keep |
| CitationBadge.jsx | 40 | Inline in chat messages | Keep |
| HoverCard.jsx | 71 | Portal to body | Keep |
| XRayPanel.jsx | 111 | Slide-in overlay (Chat) | Keep |
| ErrorBoundary.jsx | - | App wrapper | Keep |
| DocumentTable.jsx | - | Table in DocumentLibrary | → Sources panel |
| CollectionCard.jsx | - | Card in Collections | → Sources panel |
| CollectionForm.jsx | - | Form in Collections | → Sources panel |
| UploadForm.jsx | - | Upload in DocumentLibrary | → Sources panel |
| PlaygroundPanel.jsx | - | Side-by-side panels | Keep (standalone) |
| RunDetail.jsx | - | Detail view | Keep |
| SettingsField.jsx | - | Settings form | Keep (standalone) |
| StatusBadge.jsx | - | Status indicator | Keep |
| DuplicateWarning.jsx | - | Duplicate alert | Keep |

### 2.5 API Surface Consumed by Frontend

| Endpoint | Module | Used By | Type |
|----------|--------|---------|------|
| `GET /chat/sessions` | chat.js | ChatScreen | REST |
| `POST /chat/sessions` | chat.js | ChatScreen | REST |
| `GET /chat/sessions/:id/history` | chat.js | ChatScreen | REST |
| `DELETE /chat/sessions/:id` | chat.js | ChatScreen | REST |
| `POST /chat/sessions/:id/turns/stream` | chat.js | ChatScreen | SSE |
| `POST /chat/turns/:id/cancel` | chat.js | ChatScreen | REST |
| `GET /collections` | knowledgeApi.js | ChatScreen, DocLib, Collections | REST |
| `POST /collections` | knowledgeApi.js | Collections | REST |
| `PATCH /collections/:id` | knowledgeApi.js | Collections | REST |
| `DELETE /collections/:id` | knowledgeApi.js | Collections | REST |
| `GET /documents` | knowledgeApi.js | DocumentLibrary | REST |
| `GET /documents/:id` | knowledgeApi.js | SourceBrowser, DocumentLibrary | REST |
| `DELETE /documents/:id` | knowledgeApi.js | DocumentLibrary | REST |
| `POST /documents/:id/move` | knowledgeApi.js | DocumentLibrary, Collections | REST |
| `POST /documents/:id/reingest` | knowledgeApi.js | DocumentLibrary | REST |
| `POST /ingestion/file-upload` | knowledgeApi.js | DocumentLibrary | REST |
| `POST /ingestion/url` | knowledgeApi.js | DocumentLibrary | REST |
| `GET /ingestion/attempts` | knowledgeApi.js | DocumentLibrary | REST |
| `GET /ingestion/attempts/:id` | knowledgeApi.js | DocumentLibrary | REST |
| `POST /ingestion/attempts/:id/duplicate-decision` | knowledgeApi.js | DocumentLibrary | REST |
| `GET /chunks/:id/notes` | knowledgeApi.js | SourceBrowser, CitationModal | REST |
| `PUT /chunks/:id/notes` | knowledgeApi.js | SourceBrowser, CitationModal | REST |
| `POST /collections/:id/generate/study-guide` | (none yet) | **Studio target** | REST (sync) |
| `POST /collections/:id/generate/briefing-doc` | (none yet) | **Studio target** | REST (sync) |
| `POST /collections/:id/generate/faq` | (none yet) | **Studio target** | REST (sync) |
| `POST /collections/:id/generate/timeline` | (none yet) | **Studio target** | REST (sync) |
| `POST /collections/:id/generate/glossary` | (none yet) | **Studio target** | REST (sync) |
| `POST /collections/:id/generate/flashcards` | (none yet) | **Studio target** | REST (sync) |

### 2.6 SSE Streaming Contract

```
event: status   → { message, turn_id? }
event: token    → { content }
event: citations → { citations, retrieved_chunks, conflict_status, conflict_details,
                     retrieval_trace?, safety_trace?, evaluation_metrics? }
event: trace    → { retrieval?, safety?, evaluation? }
event: error    → { message }
event: done     → {}
```

**Invariant (INV-003):** SSE events are append-only. Frontend renders incrementally.

---

## 3. Notebook LM Reference Architecture

Based on Jason Spielman's design notes and Google's December 2024 announcement:

### 3.1 Mental Model

```
Inputs (Sources) → Conversation (Chat) → Outputs (Studio)
```

Three stages of a research workflow, represented as three persistent panels.

### 3.2 Panel Responsibilities

**Sources Panel (left):**
- Document inventory — all uploaded sources in the current notebook
- Per-source select/deselect for query scope
- Notebook switcher (if multiple notebooks)
- Source summaries and key topic extraction
- Upload button (drag-and-drop)

**Chat Panel (center):**
- Persistent chat — remains at core, size adjusts dynamically
- Citations with inline hover and deep-dive modal
- Conflict warnings
- Session history (collapsible)

**Studio Panel (right):**
- One-click knowledge products: Study Guide, Briefing Doc, FAQ, Timeline, Glossary, Flashcards
- Audio Overviews, Video Overviews, Mind Maps, Infographics, Slide Decks
- Note-taking space
- Export tools

### 3.3 Responsive Behavior

Three panel modes:
- **Standard:** Balanced 3-panel view
- **Reading+Chat:** Expanded left panel for source browsing, chat shrinks
- **Minimal:** Panels collapse to icons at smallest sizes

---

## 4. Brownfield Mapping

### 4.1 Target Files

| File | Lines | Role | Change Type |
|------|-------|------|-------------|
| `frontend/src/App.jsx` | 113 | Routing + layout shell | **Rewrite** — replace `<Routes>`-only rendering with 3-panel layout |
| `frontend/src/screens/Chat.jsx` | 448 | Chat screen (sidebar + main) | **Major surgery** — strip sidebar, keep main panel |
| `frontend/src/screens/DocumentLibrary/index.jsx` | 254 | Document inventory | **Migrate** — extract content into Sources panel |
| `frontend/src/screens/Collections/index.jsx` | 115 | Collection management | **Migrate** — embed into Sources panel |
| `frontend/src/screens/Evaluation.jsx` | 134 | Standalone eval | **Preserve** — keep as separate route |
| `frontend/src/screens/Playground.jsx` | 136 | A/B testing | **Preserve** — keep as separate route |
| `frontend/src/screens/SettingsScreen.jsx` | 284 | Settings | **Preserve** — keep as separate route |
| `frontend/src/styles.css` | 733 | All styles | **Extend** — add panel layout CSS, responsive rules |
| `frontend/src/components/SourceBrowser.jsx` | 229 | Document viewer | **Adapt** — convert from drawer to inline panel |
| `frontend/src/api/knowledgeApi.js` | 103 | API client | **Extend** — add knowledge product API calls if needed |

### 4.2 Dependency Graph (Current)

```
App.jsx
  ├── ErrorBoundary
  └── Routes
      ├── / → DocumentLibraryScreen
      │      ├── DocumentTable
      │      ├── SourceBrowser (right drawer)
      │      └── UploadForm
      ├── /collections → CollectionsScreen
      │      ├── CollectionCard
      │      └── CollectionForm
      ├── /chat → ChatScreen
      │      ├── XRayPanel (right slide-in)
      │      ├── CitationModal (overlay)
      │      ├── CitationBadge
      │      │      └── HoverCard
      │      └── API: chat.js, knowledgeApi.js
      ├── /playground → PlaygroundScreen
      │      └── PlaygroundPanel
      ├── /evaluation → EvaluationScreen
      └── /settings → SettingsScreen
             └── SettingsField
```

### 4.3 Target Dependency Graph

```
App.jsx
  ├── ErrorBoundary
  ├── TopHeader (preserved, simplified nav)
  └── Routes
      ├── / → WorkspaceLayout (NEW — 3-panel container)
      │      ├── SourcesPanel (NEW — left)
      │      │      ├── SourceBrowser (adapted)
      │      │      ├── DocumentTable (migrated)
      │      │      ├── CollectionCard (migrated)
      │      │      ├── UploadForm (migrated)
      │      │      └── API: knowledgeApi.js
      │      ├── ChatPanel (CENTER — adapted from ChatScreen)
      │      │      ├── CitationModal (preserved)
      │      │      ├── CitationBadge (preserved)
      │      │      │      └── HoverCard (preserved)
      │      │      └── API: chat.js
      │      └── StudioPanel (NEW — right)
      │             ├── KnowledgeProductList (NEW)
      │             ├── KnowledgeProductViewer (NEW)
      │             └── API: generate.py endpoints
      ├── /playground → PlaygroundScreen (preserved)
      ├── /evaluation → EvaluationScreen (preserved)
      └── /settings → SettingsScreen (preserved)
```

### 4.4 Shared State Requirements

Currently no external state management (no Redux, Zustand, Context). 3-panel layout introduces shared state:

| State | Producers | Consumers | Current Location |
|-------|-----------|-----------|-----------------|
| Selected collection(s) | SourcesPanel (collection picker) | ChatPanel (query scope) | `ChatScreen` local state |
| Active document for browsing | SourcesPanel / ChatPanel (citation click) | SourcesPanel (SourceBrowser) | `DocumentLibraryScreen` + `ChatScreen` local state |
| Active knowledge product result | StudioPanel (generate button) | StudioPanel (viewer) | N/A (no Studio yet) |
| Session list / active session | ChatPanel | ChatPanel | `ChatScreen` local state |
| Chat messages | ChatPanel | ChatPanel | `ChatScreen` local state |

**Recommendation:** Start with a React Context for collection scope + active document. Keep session/message state local to ChatPanel. Evaluate Zustand if cross-panel state grows beyond 3-4 values.

### 4.5 CSS Architecture Impact

Current CSS is a single 733-line file with:
- CSS custom properties for theming (83 lines)
- Component styles (chat, modals, tables, forms)
- Layout classes (`.app-shell`, `.page-shell`, `.grid`, `.stack`)
- Chat-specific layout (`.chat-container`, `.chat-sidebar`, `.chat-main`)
- Responsive breakpoints at 1024px and 768px

**New CSS needed:**
- `.workspace-layout` — the 3-panel flex container
- `.sources-panel`, `.chat-panel`, `.studio-panel` — panel styles
- `.panel-collapsed`, `.panel-expanded` — responsive states
- `.panel-resize-handle` — optional drag-to-resize

---

## 5. Preserved Behaviors (Don't Break)

| ID | Invariant | Rationale | Test Evidence |
|----|-----------|-----------|---------------|
| INV-001 | SSE streams are append-only | Frontend renders incrementally in Chat | Stream handlers in chat.js |
| INV-002 | Citation flow: badge → hover → modal | Users rely on instant source preview | CitationBadge + HoverCard + CitationModal |
| INV-003 | Screen-Component separation | Components are screen-agnostic | SourceBrowser used in both Chat and DocLib |
| INV-004 | API calls at screen/panel level | Not in reusable components | Current pattern across all screens |
| INV-005 | Theme toggle works globally | Light/dark switchable at any time | App.jsx state + CSS custom properties |
| INV-006 | Error boundary wraps entire app | Catch-all error handling | ErrorBoundary in App.jsx |
| INV-007 | Session CRUD works identically | Create, list, history, delete | chat.js API layer |
| INV-008 | X-Ray panel remains accessible | Debug transparency | XRayPanel slide-in |
| INV-009 | Knowledge products are REST POST (sync) | Current generate.py contract | `POST /collections/{id}/generate/*` |

---

## 6. Preserved Contracts

| Produces | Consumed By | Current Contract | Change Needed? |
|----------|-------------|------------------|----------------|
| Chat response (SSE) | ChatPanel | `status → token → citations → trace → done` | None |
| Citations | CitationBadge / Modal | `{chunk_id, document_id, title, quote_text, ...}` | None |
| Knowledge products | StudioPanel | REST POST `/collections/{id}/generate/*` | Add frontend API wrapper to knowledgeApi.js |
| Document list | SourcesPanel | `GET /documents` (unchanged) | None |
| Chunk notes | SourceBrowser / Modal | `GET/PUT /chunks/{id}/notes` | None |
| Collections list | SourcesPanel / Chat | `GET /collections` (unchanged) | None |

---

## 7. Boundaries & Integration Seams

### 7.1 Routing Strategy

Two viable approaches:

**Option A: Nested Routes under `/chat`**
```
/chat            → WorkspaceLayout (3-panel)
/chat/:sessionId → WorkspaceLayout (3-panel with active session)
/collections     → CollectionsScreen (standalone — redirect or embed)
/library         → DocumentLibraryScreen (standalone — redirect or embed)
```
*Pro:* Clean URL mapping for the 3-panel workspace. Non-chat screens stay standalone.
*Con:* Navigation between "workspace mode" and "settings/eval" requires full page transition.

**Option B: Always-on Workspace Layout**
```
/              → WorkspaceLayout (default, sources + chat)
/*             → WorkspaceLayout with overlay routes for settings/eval/playground
```
*Pro:* Persistent panels even when visiting settings.
*Con:* Forces all screens into the 3-panel context. Over-complicates routing.

**Recommendation:** Option A. The workspace layout is the core experience. Settings, Evaluation, and Playground are admin tools that work fine as standalone pages.

### 7.2 Panel Data Flow

```
SourcesPanel                     ChatPanel                     StudioPanel
  │                                │                              │
  ├─ Select collection ───────────►│                              │
  │                                │  (query scope)               │
  ├─ Select document for view ────►│                              │
  │  (opens SourceBrowser)         │                              │
  │                                │  (citation click) ──────────►│
  │                                │  (opens in SourceBrowser)    │
  │                                │                              │
  │                                │  Generate product ──────────►│
  │                                │  POST /collections/{id}/     │
  │                                │       generate/study-guide   │
  │                                │                              │
  │                                │  (streaming support TBD)     │
```

### 7.3 Knowledge Product Streaming Gap

Current `generate.py` endpoints are synchronous REST POST. For large collections, generation can take 10-30 seconds. Notebook LM generates products instantly or with progress indication. Two options:

1. **Add SSE streaming** to knowledge products (same pattern as chat turns)
2. **Keep sync** but add loading spinner + optimistic UI

**Recommendation:** Option 1 (SSE streaming) for study guides, briefing docs. Option 2 is acceptable for flashcards and glossary (fast to generate).

---

## 8. Risks & Unknowns

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Routing complexity:** 3-panel layout coexisting with 5 standalone screens | MEDIUM | Option A (nested routes) keeps isolation clean |
| **State management:** No existing external state, 3-panel introduces cross-panel dependencies | MEDIUM | React Context for collection scope; keep chat local |
| **CSS bloat:** 733-line single file grows significantly with panel layout | LOW | Extract panel CSS into a separate `workspace.css` or CSS modules |
| **SourceBrowser refactor:** Currently a right-side drawer, needs to become a left-side inline panel | MEDIUM | Extract content into a new `SourcesPanel` that renders SourceBrowser content inline |
| **Knowledge product API is synchronous:** No streaming, slow for large collections | MEDIUM | Either add SSE or accept sync with loading states |
| **Mobile responsiveness:** 3 panels on mobile is challenging | HIGH | Collapsible panels with icon triggers (Notebook LM pattern) |
| **No component tests for frontend:** 0 tests, refactoring is blind | CRITICAL | Add smoke tests before refactoring (see Section 9) |
| **Duplicate decision screen:** Currently inline in DocumentLibrary, needs a home | LOW | Modal overlay or SourcesPanel notification area |

---

## 9. Test Coverage Gap

| Module | Lines | Tests | Status |
|--------|-------|-------|--------|
| App.jsx (routing + layout) | 113 | 0 | **NEEDED** |
| Chat.jsx | 448 | 0 | **NEEDED** |
| DocumentLibrary/index.jsx | 254 | 0 | **NEEDED** |
| SourceBrowser.jsx | 229 | 0 | **NEEDED** |
| CitationModal.jsx | 161 | 0 | **NEEDED** |
| All other components | 500+ | 0 | **NEEDED** |

**Recommendation:** Add smoke tests for critical user flows before refactoring:
1. Chat: send message → receive SSE stream → render citations
2. SourceBrowser: open document → view chunks → edit note
3. Citation flow: click badge → open modal → view quote
4. Session CRUD: create → list → view history → delete

---

## 10. Implementation Sizing

| Task | Est. Effort | Risk | Dependencies |
|------|-------------|------|-------------|
| Create WorkspaceLayout component with 3-panel CSS | 2-3 days | LOW | None |
| Strip ChatScreen.sidebar, keep ChatPanel | 1 day | LOW | WorkspaceLayout |
| Build SourcesPanel from DocumentLibrary content | 2-3 days | MEDIUM | WorkspaceLayout |
| Adapt SourceBrowser from drawer to inline left panel | 1 day | MEDIUM | SourcesPanel |
| Build StudioPanel with knowledge product buttons | 2 days | LOW | WorkspaceLayout |
| Add knowledge product API wrapper to knowledgeApi.js | 0.5 day | LOW | None |
| Implement SSE streaming for knowledge products (optional) | 2 days | MEDIUM | Backend changes |
| Routing restructure (App.jsx) | 1 day | MEDIUM | WorkspaceLayout |
| Responsive panel collapse behavior | 1 day | MEDIUM | WorkspaceLayout |
| Add smoke tests before refactoring | 1 day | LOW | None |
| **Total** | **12-15 days** | | |

---

## 11. Conclusion

> The UI restructure from single-column to 3-panel layout is feasible but requires careful brownfield surgery. The key insight is that **most of the code already exists** — SourceBrowser (229 lines), DocumentLibrary (254 lines), CitationModal (161 lines), and the knowledge product APIs (6 endpoints in generate.py) just need to be re-parented into a persistent 3-panel container.
>
> **Critical blockers to resolve first:** (1) zero frontend tests make the refactoring blind — add smoke tests before touching layout. (2) Routing strategy must be decided (Option A recommended). (3) Knowledge product streaming vs sync tradeoff needs a decision.
>
> The biggest unknown is **state management** — currently all state is local to `useState` in each screen. The 3-panel layout introduces cross-panel dependencies (collection scope, active document) that need a lightweight shared context.

**Route to:** `/spec-adr` — the routing strategy decision (Option A vs B) is a contested technical choice that affects the entire architecture. Run an ADR first, then proceed to `/spec-requirements` for the implementation details.

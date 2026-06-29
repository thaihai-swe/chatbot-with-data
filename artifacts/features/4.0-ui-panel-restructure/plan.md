# Implementation Plan: UI Panel Restructure

## Metadata

- Feature name: UI Panel Restructure
- Related spec: `artifacts/features/4.0-ui-panel-restructure/spec.md`
- Owner: TBD
- Status: Draft
- Last updated: 2026-06-29

---

## Part 1: Technical Design

### Comprehensive Design

#### Design Summary
Restructure from single-column chat to a 3-panel workspace (Sources | Chat | Studio) with collapsible panels, collection-scoped document selection, and in-chat knowledge product generation. No new backend endpoints — pure frontend re-architecture.

#### Current State

| Module | Lines | Role |
|--------|-------|------|
| `App.jsx` | 113 | Routing + layout shell (7 routes, top nav) |
| `Chat.jsx` | 448 | Chat: sidebar (sessions, settings) + main (messages, composer) + modals |
| `DocumentLibrary/index.jsx` | 254 | Full document management: upload, table, filters |
| `Collections/index.jsx` | 115 | Collection CRUD with document membership |
| `SourceBrowser.jsx` | 229 | Right-side drawer: chunks + text + notes |
| `styles.css` | 733 | All styles: theme, layout, chat, modals |

**Key observations:**
- ChatScreen bundles sidebar + main in one component
- SourceBrowser is a fixed right-drawer overlay, not inline
- DocumentLibrary and Collections are full-page routes
- No cross-panel state (all `useState` per screen)
- Knowledge products have no frontend

#### Proposed Architecture

```
App.jsx
  +-- ErrorBoundary
  +-- WorkspaceProvider (NEW - React Context)
  +-- TopHeader (preserved, simplified nav)
  +-- Routes
      +-- /chat, /chat/:sessionId -> WorkspaceLayout (NEW)
      |   +-- SourcesPanel (NEW) - collapsible left
      |   +-- ChatPanel (EXTRACTED) - center
      |   +-- StudioPanel (NEW) - collapsible right
      +-- /playground, /evaluation, /settings -> preserved standalone
      +-- /, /collections -> redirect to /chat
```

#### Component Architecture

**1 - WorkspaceProvider (React Context)**

Shared state for cross-panel communication:

```
interface WorkspaceState {
  selectedCollectionId: string | null;
  collectionName: string | null;
  selectedDocumentIds: string[];
  documents: Document[];
  activeDocumentId: string | null;
  generatedProducts: Product[];
  sourcesCollapsed: boolean;
  studioCollapsed: boolean;
}
```

Actions: `selectCollection`, `toggleDocument`, `setActiveDocument`, `addGeneratedProduct`, `toggleSourcesPanel`, `toggleStudioPanel`

ChatPanel keeps session/messages state local (not shared in context).

**2 - WorkspaceLayout**

- CSS flex container: `display: flex; height: calc(100vh - 64px);`
- Three children: SourcesPanel (`flex: 0 0 auto, width: 320px`), ChatPanel (`flex: 1`), StudioPanel (`flex: 0 0 auto, width: 300px`)
- Collapsed: panels reduce to 48px icon strips. CSS `transition: width var(--motion-slow) ease`
- Responsive: at <=768px, bottom tab bar (3 tabs) replaces side panels
- Collapse/expand controlled by WorkspaceContext state + click handlers on icon strips

**3 - SourcesPanel (left)**

- **Collapsed:** 48px strip with icon. Click toggles `sourcesCollapsed` in context.
- **Expanded (~320px):**
  - Header: collection dropdown selector
  - On collection select: fetch documents via `listDocuments({collectionId})`, store in context
  - Document list with checkboxes (all checked default). Toggle calls `toggleDocument`
  - "View" action on a document: sets `activeDocumentId` in context -> SourceBrowser renders inline
  - SourceBrowser adapted: renders inside SourcesPanel width, not as overlay drawer
  - Upload button at top (simplified: file upload only, not the full DocLib form)
- **No collection:** prompt "Select a collection to begin"

**4 - ChatPanel (center)**

- Extracted from `Chat.jsx` lines 366-445 (the `.chat-main` div contents)
- Strips: `.chat-sidebar` (session list), scope settings, collection toggles
- Preserves: message list, streaming, citations, hover, conflict warnings, X-Ray toggle
- Composer toolbar: existing input + send/cancel + NEW `[+ Generate]` dropdown
- Generate dropdown appears only when `selectedCollectionId` is set
- Reads `selectedCollectionId` + `selectedDocumentIds` from WorkspaceContext
- Passes `document_ids: selectedDocumentIds` to chat API calls
- Session list: remains accessible via a compact collapsible header or moved to top nav

**5 - StudioPanel (right)**

- **Collapsed:** 48px strip with icon. Click toggles `studioCollapsed` in context.
- **Expanded (~300px):**
  - 6 generate buttons (Study Guide, Briefing Doc, FAQ, Timeline, Glossary, Flashcards)
  - Buttons enabled only when `selectedCollectionId` is set
  - Click calls `POST /collections/{id}/generate/{type}` via `knowledgeApi.js`
  - Loading spinner on active button, other buttons disabled during generation
  - On success: content added to `generatedProducts` in context, viewer renders product
  - Product history list (scrollable, newest first). Click item to view in viewer pane

**6 - Chat Inline Generation**

- `[+ Generate]` dropdown in ChatPanel composer toolbar
- 6 product types, same as StudioPanel
- On select: inserts assistant message `{ role: "assistant", content: "", isGenerating: true }`
- Calls knowledge product API in parallel
- On completion: updates message with formatted content, calls `addGeneratedProduct` in context
- Text products: rendered as formatted markdown
- Flashcards: rendered as Q&A list with expandable answers

**7 - Routing Changes in App.jsx**

```
Current:                        Target:
/ -> DocumentLibraryScreen      / -> redirect to /chat
/collections -> Collections     /collections -> redirect to /chat
/chat -> ChatScreen             /chat, /chat/:sessionId -> WorkspaceLayout
/chat/:sessionId -> ChatScreen  /playground -> PlaygroundScreen (same)
/playground -> PlaygroundScreen /evaluation -> EvaluationScreen (same)
/evaluation -> EvaluationScreen /settings -> SettingsScreen (same)
/settings -> SettingsScreen
```

Top nav: keep Library and Collections links or replace with a single "Sources" link that expands SourcesPanel.

#### Data Flow

```
Collection selected:
  SourcesPanel.selectCollection(id)
    -> WorkspaceContext.selectCollection(id)
    -> fetch documents
    -> WorkspaceContext set {selectedCollectionId, documents, selectedDocumentIds: all}

Document toggle:
  SourcesPanel.toggleDocument(id)
    -> WorkspaceContext.toggleDocument(id)
    -> ChatPanel reads selectedDocumentIds for next query

Chat query:
  ChatPanel.handleSendMessage
    -> reads selectedDocumentIds from context
    -> passes document_ids to SSE stream endpoint
    -> existing streaming flow resumes unchanged

Knowledge product generate (Studio or Chat):
  GenerateButton.onClick
    -> calls POST /collections/{id}/generate/{type}
    -> on success: WorkspaceContext.addGeneratedProduct(product)
    -> StudioPanel viewer updates
    -> if triggered from chat: insert assistant message with content

Panel collapse:
  Icon click -> WorkspaceContext.toggleSourcesPanel() / toggleStudioPanel()
    -> CSS width transitions 48px <-> 320px
```

#### Key Decisions & Tradeoffs

| Decision | Choice | Tradeoff |
|---|---|---|
| State management | React Context | Simple, no deps. Risk: re-renders on every state change. Mitigation: split into separate contexts or use useMemo for consumers. |
| Panel collapsible | CSS width transition + state | Simple animation. No drag-to-resize (Notebook LM supports it). Deferred as future enhancement. |
| SourceBrowser inline vs drawer | Inline in SourcesPanel | No overlay. Content constrained to panel width. |
| Generate in chat | Assistant message | Consistent with chat metaphor. History remains in session. |
| Knowledge product streaming | Sync REST (no SSE) | Acceptable for text-only. Loading states handle UX. |
| DocumentLibrary fate | Simplified upload + doc picker in SourcesPanel. Full management stays at /library route. | Two entry points for doc management. But avoids bloating SourcesPanel. |
| Chat session list | Compact header in ChatPanel | Not full sidebar. Drawer or dropdown to keep UI clean. |

#### Non-Functional Considerations

- **Performance:** Context provides stable references with `useMemo`. WorkspaceLayout render time must not exceed ChatScreen + 100ms (NFR-001).
- **Responsiveness:** Panel transitions use `--motion-slow` (240ms). At <=768px, single-panel mode via bottom tab bar (NFR-003).
- **Regression:** All existing chat interactions pass through unchanged code paths. ChatPanel reuses CitationModal, CitationBadge, HoverCard, XRayPanel without modification (NFR-004).
- **State consistency:** All mutations go through WorkspaceContext dispatch. ChatPanel reads context fresh before each SSE stream (NFR-002).

#### Protected Behavior

- SSE streaming append-only (INV-003)
- Citation flow: badge -> hover -> modal (INV-002)
- Screen-component separation (INV-005)
- X-Ray slide-in panel (INV-008)
- Theme toggle (INV-005)
- Error boundary wrapping (INV-006)
- Session CRUD (INV-007)
- Knowledge product REST contract (INV-009)

---

## Part 2: Delivery Strategy

### Execution Context
- Delivery profile: Complex
- Locked spec decisions: Option A routing, React Context state, sync knowledge products, inline SourceBrowser, collapsible panels default collapsed.

### First Delivery Slice
- Smallest useful slice: **WorkspaceLayout shell + WorkspaceContext**. This is the foundation everything else depends on.
- Why this goes first: All three panels need the layout container and shared context to function. Getting the CSS flex + collapse/expand working early validates the core UX hypothesis.
- Proof when done: Empty 3-panel layout renders at `/chat` with collapsible Sources/Studio icon strips.

### Execution Phases

#### Phase 1: Foundation
- Goal: WorkspaceLayout shell, WorkspaceContext, CSS panel layout, routing.
- Enabled outcomes: Core layout renders. Panels collapse/expand. Context flows between panels.
- Entry proof: Spec approved, plan written.
- Exit proof: `/chat` renders empty workspace with collapsible icon strips. `/settings` still works standalone.
- Tasks: TASK-001, TASK-002, TASK-003

#### Phase 2: SourcesPanel
- Goal: Collection picker + document list + inline SourceBrowser.
- Enabled outcomes: US-001, SC-001, SC-002.
- Entry proof: Phase 1 complete.
- Exit proof: Select collection -> documents load with checkboxes. Toggle docs. View opens inline SourceBrowser.
- Tasks: TASK-004, TASK-005

#### Phase 3: ChatPanel
- Goal: Extract ChatScreen main area into ChatPanel, strip sidebar, wire to context.
- Enabled outcomes: SC-003 (chat cycle preserved).
- Entry proof: Phase 1 complete.
- Exit proof: Full chat cycle works in new layout (stream, citations, hover, X-Ray).
- Tasks: TASK-006

#### Phase 4: StudioPanel + Chat Inline Generation
- Goal: Studio generate buttons, product history, viewer. [+ Generate] in chat composer.
- Enabled outcomes: US-003, SC-004, SC-005, SC-006.
- Entry proof: Phases 2 + 3 complete (need collection selection + chat panel).
- Exit proof: Generate from Studio panel -> viewer shows content. Generate from chat composer -> assistant message rendered.
- Tasks: TASK-007, TASK-008

#### Phase 5: Responsive + Polish
- Goal: Mobile single-panel mode, edge cases, lint.
- Enabled outcomes: SC-003 (responsive).
- Entry proof: All prior phases complete.
- Exit proof: <=768px bottom tab bar works. No console errors. Build passes.
- Tasks: TASK-009

### Validation Strategy
- Manual: All ACs verified via browser testing across 3 viewports
- Build: `npm run build` passes (0 errors)
- Regression: Existing chat screens work unchanged at original routes until routing phase

### Traceability Matrix

| Spec Item | Phase | Tasks |
|---|---|---|
| REQ-001 (Workspace) | P1 | TASK-001, TASK-002 |
| REQ-002 (Selection) | P2 | TASK-004 |
| REQ-003 (Chat) | P3 | TASK-006 |
| REQ-004 (Studio) | P4 | TASK-007 |
| REQ-008 (Chat Gen) | P4 | TASK-008 |
| REQ-005 (SourceBrowser) | P2 | TASK-005 |
| REQ-006 (Routing) | P1 | TASK-003 |
| REQ-007 (Collapse) | P1, P5 | TASK-002, TASK-009 |
| NFR-001 (Perf) | P1 | TASK-001 |
| NFR-002 (State) | P1 | TASK-001 |
| NFR-003 (Responsive) | P5 | TASK-009 |
| NFR-004 (Regression) | P3 | TASK-006 |

### Rollout Plan
- Release approach: In-place. No feature flags.
- Migration: None (frontend-only).
- Backward compatibility: Old chat sessions load correctly. Created before restructure still accessible.
- Rollback: Revert App.jsx routing, keep WorkspaceLayout component unused.

### Risks And Mitigations
- RISK-001 (Zero frontend tests): No safety net for refactoring 3 large screens. Mitigation: Add smoke test for core chat cycle before refactoring.
- RISK-002 (Context re-renders): Single context with 8+ values causes cascading re-renders. Mitigation: Split into Provider with `useMemo` on exposed values. Consider `useContextSelector` pattern.
- RISK-003 (Knowledge product slow): Sync REST can take 10-15s for large collections. Mitigation: Loading spinner + disabled buttons during generation. Acceptable for initial release.

### Open Questions
- Q-001: Should the session list be a dropdown in ChatPanel header or a collapsible drawer?
  - Decision: Compact collapsible header in ChatPanel. Shows current session name + expand arrow. Dropdown lists recent sessions.

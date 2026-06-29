# Task Breakdown: UI Panel Restructure

## Metadata

- Feature name: UI Panel Restructure
- Related spec / plan: `spec.md`, `plan.md`
- Owner: TBD
- Last updated: 2026-06-29

## Rules

- Each task small, testable, traceable to REQ/AC/plan.
- Mark `[P]` only when truly independent (no write/contract conflicts).
- Task states: `Not Started` | `In Progress` | `Blocked` | `Done` | `Deferred`.

## Implementation Strategy

```
Selected strategy: Incremental
Reason: Phased approach where each phase depends on the prior foundation
(WorkspaceLayout -> SourcesPanel -> ChatPanel -> StudioPanel -> Polish)
```

## User Story Decomposition

| Phase | Purpose | Ships independently |
|---|---|---|
| P1: Foundation | WorkspaceLayout, context, CSS, routing | no |
| P2: SourcesPanel | Collection picker, doc selection, inline SourceBrowser | no (needs P1) |
| P3: ChatPanel | Extract chat, strip sidebar, wire to context | no (needs P1) |
| P4: Studio + Chat Gen | Generate buttons, history, inline chat generation | no (needs P2+P3) |
| P5: Polish | Responsive mobile, edge cases | no |

## Task Block Format

### Phase 1: Foundation
Goal: WorkspaceLayout shell, WorkspaceContext, CSS panel layout, routing restructure.

Completion criteria:
- [ ] CC-001 `/chat` renders 3-panel WorkspaceLayout with collapsed Sources/Studio icon strips.
- [ ] CC-002 WorkspaceContext provides `selectedCollectionId`, `selectedDocumentIds`, `sourcesCollapsed`, `studioCollapsed`.
- [ ] CC-003 Sources/Studio icon strips expand/collapse on click with CSS transition.
- [ ] CC-004 `/settings`, `/playground`, `/evaluation` remain accessible as standalone routes.
- [ ] CC-005 `/` and `/collections` redirect to `/chat`.

Tasks:

- [x] TASK-001
  Status: Done
  Summary: Create WorkspaceProvider (React Context) with all shared state and actions.
  Covers: REQ-001, NFR-001, NFR-002
  Outcome enabled: Cross-panel state sharing foundation.
  Plan reference: Phase 1 - WorkspaceProvider
  Affected file(s): `frontend/src/context/WorkspaceContext.jsx` (new)
  Depends on:
  Can run in parallel: yes (independent of layout)
  Proving command or proof: `npm run build` passes. Import context in App.jsx and verify default state with React DevTools.
  Validation evidence: Context wraps app. Default state: `{selectedCollectionId: null, selectedDocumentIds: [], sourcesCollapsed: true, studioCollapsed: true}`. Actions dispatch correctly (console.log in reducer).

- [x] TASK-002
  Status: Done
  Summary: Build WorkspaceLayout component with 3-panel flex layout and collapsible icon strips. Add CSS.
  Covers: REQ-001, REQ-007
  Outcome enabled: 3-panel workspace renders and panels collapse/expand.
  Plan reference: Phase 1 - WorkspaceLayout
  Affected file(s): `frontend/src/components/WorkspaceLayout.jsx` (new), `frontend/src/styles.css` (append panel CSS)
  Depends on: TASK-001
  Can run in parallel: no (needs context for collapse state)
  Proving command or proof: `/chat` renders 3 empty panels. Click Sources icon -> expands. Click again -> collapses. Same for Studio.
  Validation evidence: Sources panel collapses from 320px to 48px with transition. Studio panel same. Chat panel fills remaining width.

- [ ] TASK-003 [P]
  Status: Not Started
  Summary: Restructure App.jsx routing: add WorkspaceLayout at `/chat` and `/chat/:sessionId`, redirect `/` and `/collections` to `/chat`, preserve standalone routes.
  Covers: REQ-006
  Outcome enabled: Routing matches spec Option A.
  Plan reference: Phase 1 - Routing
  Affected file(s): `frontend/src/App.jsx`
  Depends on: TASK-002
  Can run in parallel: yes (once WorkspaceLayout exists, routing is pure config)
  Proving command or proof: Navigate `/chat` -> workspace renders. Navigate `/settings` -> SettingsScreen renders. Navigate `/` -> redirects to `/chat`.
  Validation evidence: All 3 navigation paths verified.

### Phase 2: SourcesPanel
Goal: Collection picker, document list with checkboxes, inline SourceBrowser.

Completion criteria:
- [ ] CC-006 Collection dropdown shows available collections. Selecting one loads its documents.
- [ ] CC-007 Documents listed with checkboxes, all checked by default. Unchecking updates context.
- [ ] CC-008 "View" action opens SourceBrowser inline (not drawer).
- [ ] CC-009 Upload button opens simplified UploadForm.

Tasks:

- [ ] TASK-004
  Status: Not Started
  Summary: Build SourcesPanel with collection picker dropdown and document list with checkboxes.
  Covers: REQ-002, SC-001, SC-002, AC-001, AC-002
  Outcome enabled: US-001 - collection and document selection.
  Plan reference: Phase 2 - SourcesPanel
  Affected file(s): `frontend/src/components/SourcesPanel.jsx` (new)
  Depends on: TASK-002
  Can run in parallel: yes (independent of ChatPanel)
  Proving command or proof: Select collection -> documents load with checkboxes all checked. Uncheck 3 -> context `selectedDocumentIds` reflects change.
  Validation evidence: Collection dropdown fetches `listCollections()`. On select, fetches documents. Checkboxes render and toggle correctly.

- [ ] TASK-005
  Status: Not Started
  Summary: Adapt SourceBrowser from right-drawer to inline panel. Wire into SourcesPanel.
  Covers: REQ-005, AC-005
  Outcome enabled: US-002 - source browsing in left panel.
  Plan reference: Phase 2 - SourceBrowser inline
  Affected file(s): `frontend/src/components/SourceBrowser.jsx` (modify), `frontend/src/components/SourcesPanel.jsx` (wire)
  Depends on: TASK-004
  Can run in parallel: no (needs SourcesPanel for parent container)
  Proving command or proof: Click "View" on a document -> SourceBrowser renders inside SourcesPanel (not as overlay drawer). Chunks and notes editor work.
  Validation evidence: SourceBrowser no longer uses `position: fixed` drawer. Renders as child of SourcesPanel. Chunk selection, note editing preserved.

### Phase 3: ChatPanel
Goal: Extract ChatScreen main area into ChatPanel, strip sidebar, wire to context.

Completion criteria:
- [ ] CC-010 ChatPanel renders messages, composer, streaming, citations, X-Ray. No sidebar.
- [ ] CC-011 ChatPanel reads `selectedCollectionId` + `selectedDocumentIds` from context for API calls.
- [ ] CC-012 Chat input and generate buttons disabled when no collection selected.

Tasks:

- [ ] TASK-006
  Status: Not Started
  Summary: Extract ChatPanel from ChatScreen. Strip sidebar. Wire SSE streaming and citations to WorkspaceContext collection scope.
  Covers: REQ-003, SC-003, AC-003, NFR-004
  Outcome enabled: Full chat cycle works in new layout.
  Plan reference: Phase 3 - ChatPanel
  Affected file(s): `frontend/src/components/ChatPanel.jsx` (new, extract from `Chat.jsx` lines 366-445), `frontend/src/screens/Chat.jsx` (simplify to load WorkspaceLayout or redirect)
  Depends on: TASK-002
  Can run in parallel: yes (independent of SourcesPanel)
  Proving command or proof: Full chat cycle: create session -> send message -> SSE stream renders -> click citation -> modal opens -> X-Ray opens. No sidebar visible.
  Validation evidence: ChatPanel reuses CitationModal, CitationBadge, HoverCard, XRayPanel unchanged. SSE events flow identically. No console errors.

### Phase 4: StudioPanel + Chat Inline Generation
Goal: Studio generate buttons, product history, viewer. [+ Generate] in chat composer.

Completion criteria:
- [ ] CC-013 StudioPanel shows 6 generate buttons. Clicking one calls API and renders result in viewer.
- [ ] CC-014 Product history list shows generated products for current session.
- [ ] CC-015 Chat composer has [+ Generate] dropdown. Selecting inserts assistant message with product content.
- [ ] CC-016 Generated products from chat appear in Studio history, and vice versa.

Tasks:

- [ ] TASK-007
  Status: Not Started
  Summary: Build StudioPanel with 6 generate buttons, product history list, and content viewer. Add knowledge product API calls to frontend.
  Covers: REQ-004, SC-004, SC-006, AC-004
  Outcome enabled: US-003 - knowledge products accessible from Studio panel.
  Plan reference: Phase 4 - StudioPanel
  Affected file(s): `frontend/src/components/StudioPanel.jsx` (new), `frontend/src/api/knowledgeApi.js` (add product API calls)
  Depends on: TASK-004 (needs collection selection)
  Can run in parallel: no
  Proving command or proof: Select collection -> open Studio panel -> click each generate button -> viewer shows content. History list shows entries.
  Validation evidence: 6 buttons call POST endpoints. Loading spinner shows during generation. Text products render as formatted content. Flashcards render as Q&A list.

- [ ] TASK-008
  Status: Not Started
  Summary: Add [+ Generate] dropdown to ChatPanel composer toolbar. Handle insert as assistant message. Sync with WorkspaceContext generatedProducts.
  Covers: REQ-008, SC-005, AC-008
  Outcome enabled: Knowledge products can be generated directly from chat.
  Plan reference: Phase 4 - Chat Inline Generation
  Affected file(s): `frontend/src/components/ChatPanel.jsx` (modify), `frontend/src/components/GenerateButton.jsx` (new, shared with StudioPanel)
  Depends on: TASK-006, TASK-007
  Can run in parallel: no
  Proving command or proof: Click [+ Generate] -> Study Guide in composer -> assistant message appears with loading -> content renders. Studio history shows product.
  Validation evidence: GenerateButton component shared between StudioPanel and ChatPanel. Assistant message rendered with formatted content. Studio history updated via context.

### Phase 5: Responsive + Polish
Goal: Mobile single-panel mode, edge cases, build verification.

Completion criteria:
- [ ] CC-017 At <=768px, bottom tab bar replaces side panels. One panel visible at a time.
- [ ] CC-018 `npm run build` passes with 0 errors.
- [ ] CC-019 No console errors in any interaction.

Tasks:

- [ ] TASK-009
  Status: Not Started
  Summary: Add responsive mobile layout with bottom tab bar. Final build verification.
  Covers: REQ-007, NFR-003, AC-006
  Outcome enabled: Usable on mobile viewports.
  Plan reference: Phase 5 - Responsive
  Affected file(s): `frontend/src/components/WorkspaceLayout.jsx` (modify), `frontend/src/styles.css` (append mobile CSS)
  Depends on: TASK-002, TASK-004, TASK-006, TASK-007
  Can run in parallel: no
  Proving command or proof: Resize to 768px -> panels collapse to bottom tab bar with 3 tabs (Sources, Chat, Studio). Click each tab -> corresponding panel renders. Full-screen desktop restored above 768px.
  Validation evidence: CSS media query triggers at 768px. Bottom tab bar rendered. Panel visibility toggled by active tab. Build passes 0 errors.

## Traceability Matrix

| Requirement | AC | Tasks | Verification |
|---|---|---|---|
| REQ-001 (Workspace) | AC-007 | TASK-001, TASK-002 | npm run build, visual check |
| REQ-002 (Selection) | AC-001, AC-002 | TASK-004 | Manual: collection/doc select |
| REQ-003 (Chat) | AC-003 | TASK-006 | Manual: full chat cycle |
| REQ-004 (Studio) | AC-004 | TASK-007 | Manual: generate 6 products |
| REQ-005 (SourceBrowser) | AC-005 | TASK-005 | Manual: inline view |
| REQ-006 (Routing) | AC-009 | TASK-003 | Manual: navigate routes |
| REQ-007 (Collapse) | AC-006 | TASK-002, TASK-009 | Manual: collapse/expand |
| REQ-008 (Chat Gen) | AC-008 | TASK-008 | Manual: generate in chat |
| NFR-001 (Performance) | AC-007 | TASK-001 | performance.mark check |
| NFR-002 (State) | AC-001, AC-002 | TASK-001 | Visual: scope updates |
| NFR-003 (Responsive) | AC-006 | TASK-009 | Resize test |
| NFR-004 (Regression) | AC-003 | TASK-006 | Full chat cycle test |

# Feature Specification: UI Panel Restructure

## Metadata

- Feature name: UI Panel Restructure
- Feature slug: 4.0-ui-panel-restructure
- Delivery profile: Complex
- Owner: TBD
- Status: Proposed
- Last updated: 2026-06-29
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/4.0-ui-panel-restructure/analysis.md)

## Problem Statement

Our system uses a single-column, full-page navigation pattern where Chat, Document Library, and Collections are separate screens. This forces users to context-switch between managing sources and having a conversation. Google Notebook LM's 3-panel layout (Sources + Chat + Studio) has set the UX standard for AI-powered research — sources, conversation, and outputs coexist in a single workspace.

Users currently cannot:
1. See their document inventory while chatting.
2. Select which specific documents to query from within the chat workspace.
3. Generate knowledge products (study guides, flashcards) without leaving the chat context.

## Desired Outcomes

- Users can start a chat by selecting a collection (notebook), defaulting to all documents, with per-document toggle granularity.
- Users can browse sources, chat, and generate knowledge products in a single workspace without full-page navigation.
- All existing chat interactions (SSE streaming, citations, hover cards, X-Ray) work identically in the new layout.

## Minimum Release Slice

- WorkspaceLayout shell with 3 collapsible panels (Sources, Chat, Studio).
- Collection picker in Sources panel with per-document toggle (default: all).
- Chat panel extracted from ChatScreen (strip sidebar to Sources panel).
- Generate buttons in both Studio panel and Chat panel composer toolbar.
- Generated products render as chat messages.
- Studio panel shows generated product history.
- Routing: `/chat` → workspace, standalone routes for Settings/Playground/Evaluation.

## Success Criteria

- SC-001: User can select a collection in Sources panel; Chat panel routes queries to that collection.
- SC-002: User can toggle individual documents on/off within a selected collection; Chat respects the subset.
- SC-003: All existing chat features (streaming, citations, hover, X-Ray, conflict warnings) work in the new layout.
- SC-004: Generate buttons appear in both Studio panel and Chat panel composer toolbar.
- SC-005: Generated products render as chat messages in the Chat panel.
- SC-006: Studio panel shows history of generated products for the current session.

## In Scope

- WorkspaceLayout React component with 3-panel flex layout. Sources/Studio panels default collapsed (icon strips), Chat centered full-width.
- SourcesPanel (left): collection picker, document inventory with per-doc toggle, upload button, SourceBrowser inline.
- ChatPanel (center): extracted from ChatScreen main area (strip sidebar, keep message list + composer + citation modal + X-Ray).
- StudioPanel (right): generate buttons for 6 knowledge products, product history list, viewer for selected product.
- ChatPanel composer toolbar: generate buttons (duplicated from Studio panel).
- Generated products render as chat messages (formatted markdown/Q&A).
- Shared React Context for cross-panel state: `selectedCollectionId`, `selectedDocumentIds`, `activeDocumentId`, `generatedProducts`.
- Routing restructure: `/chat` → WorkspaceLayout, `/chat/:sessionId` → WorkspaceLayout with active session.
- CSS for workspace layout, panel collapse/responsive behavior.
- DocumentLibrary and Collections screen content migrated into SourcesPanel.

## Out Of Scope

- SSE streaming for knowledge products (keep synchronous REST with loading states).
- Backend changes to chat, retrieval, or knowledge product APIs.
- Authentication, auth, or multi-tenancy.
- Native mobile app (responsive web only).
- New knowledge product types beyond the existing 6.

## User Stories And Key Scenarios

- **US-001:** As a researcher, I want to pick a collection and see all its documents, then toggle specific ones on/off before asking a question.
- **US-002:** As an analyst, I want to browse documents in the left panel while chatting in the center panel without losing context.
- **US-003:** As a power user, I want to generate a study guide or flashcards from the current document set and view the result in the right panel.

### Detailed Scenarios

- **Scenario 1 (Collection + Document Selection):**
  - **Given:** The user opens `/chat` and sees the 3-panel workspace. Chat input and generate buttons are disabled/hidden.
  - **When:** The user selects "Q3 Reports" collection in the Sources panel.
  - **Then:** Only documents in "Q3 Reports" appear in the Sources panel with checkboxes checked by default. Chat panel enables: "Chatting with Q3 Reports (12 documents)."
  - **When:** The user unchecks 3 documents.
  - **Then:** The chat scope updates to "Chatting with Q3 Reports (9 documents)."
  - **When:** The user asks a question.
  - **Then:** The SSE stream routes only to the 9 selected documents.

- **Scenario 2 (Knowledge Product Generation):**
  - **Given:** A collection with 5 documents is selected.
  - **When:** The user clicks "Generate Study Guide" in the Studio panel.
  - **Then:** A loading state appears, the backend returns the product, and the content renders in the Studio viewer.

- **Scenario 4 (Chat Inline Generation):**
  - **Given:** A collection is selected and the user is in the Chat panel.
  - **When:** The user clicks "Study Guide" in the composer toolbar.
  - **Then:** A new assistant message appears in the chat with a loading indicator, the generation streams (or loads synchronously), and the final product renders as a formatted chat message.
  - **When:** The user opens the Studio panel.
  - **Then:** The generated product appears in the product history list.

- **Scenario 3 (Legacy Chat Session):**
  - **Given:** An existing session from a previous chat with `collection_ids` stored.
  - **When:** Navigating to `/chat/{sessionId}`.
  - **Then:** The WorkspaceLayout loads, Sources panel shows the session's collections/documents pre-selected, and chat history renders in the Chat panel.

## Current Context

- **Current behavior summary:** Chat is a full-screen route with its own sidebar. Document management is in separate routes (`/`, `/collections`). Knowledge products have no frontend.
- **Impacted boundaries:** `frontend/src/App.jsx` (routing + layout shell), `frontend/src/screens/Chat.jsx` (extract panel), `frontend/src/screens/DocumentLibrary/index.jsx` (migrate to panel), `frontend/src/screens/Collections/index.jsx` (migrate to panel), `frontend/src/styles.css` (add panel layout), `frontend/src/components/SourceBrowser.jsx` (adapt to inline panel).
- **Preserved behavior:** SSE streaming append-only (INV-003), citation flow (badge → hover → modal, INV-002), screen-component separation (INV-005), X-Ray slide-in (INV-008), theme toggle (INV-005), error boundary (INV-006).
- **Brownfield risk rating:** High (zero frontend tests, routing redesign, state extraction from 3 existing screens).

## Gray-Area Decisions

- **Routing Strategy:** Option A (nested — `/chat` workspace, standalone pages for admin screens). Rationale: clean isolation, non-chat screens don't need 3-panel context.
- **State Management:** React Context for cross-panel state. Keep chat messages/session local to ChatPanel. Rationale: only 3-4 shared values (collectionId, documentIds, activeDocId). No need for Zustand/Redux at this scale.
- **Knowledge Product Generation:** Sync REST POST with loading spinner. Rationale: avoids backend changes; acceptable UX for text-only products (5-15s generation).
- **CSS:** Append panel layout to existing `styles.css`. Rationale: single-file consistency, no import restructuring.
- **Non-Chat Screens Fate:** Full document management (upload, bulk operations, duplicate resolution) stays accessible from standalone `/library` route. Sources panel provides simplified document picker + browser.

## Functional Requirements

### REQ-001: Workspace Layout
- **Requirement:** Persistent 3-panel layout (Sources | Chat | Studio) that renders at `/chat` and `/chat/:sessionId`.
- **Why it matters:** Core UX transformation — eliminates screen-to-screen navigation for the primary workflow.
- **Related success criteria:** SC-003
- **Acceptance notes:** Panels are resizable via CSS flex. Each panel can collapse to a narrow strip (icon-only) at breakpoints.
- **Validation surface:** Manual visual check across 3 viewport sizes (1440px, 1024px, 768px).

### REQ-002: Collection + Document Selection
- **Requirement:** Sources panel shows a collection picker. Selecting a collection loads ONLY its documents (no cross-collection browsing). All documents checked by default. User can toggle individual documents.
- **Why it matters:** Core requirement — user must scope chat to a collection before interacting. Sources panel shows only documents under the selected collection/notebook.
- **Related success criteria:** SC-001, SC-002
- **Acceptance notes:** Selection state lives in shared React Context. ChatPanel reads context to pass `document_ids` to the SSE stream endpoint. Chat composer and Studio generate buttons remain disabled/hidden until a collection is selected.
- **Validation surface:** Manual test: empty state before selection → select collection → verify documents load → toggle 3 off → verify chat scope reflects change.

### REQ-003: Chat Panel Continuity
- **Requirement:** All existing chat functionality (SSE streaming, citations, hover cards, X-Ray, conflict warnings, session CRUD) works identically in the ChatPanel.
- **Why it matters:** No regression on existing interactions.
- **Related success criteria:** SC-003
- **Acceptance notes:** ChatPanel reuses CitationModal, CitationBadge, HoverCard, XRayPanel without modification.
- **Validation surface:** Manual test of full chat cycle: create session → send message → receive stream → click citation → view X-Ray.

### REQ-004: Studio Panel
- **Requirement:** Right panel displays 6 generate buttons (study guide, briefing doc, FAQ, timeline, glossary, flashcards), a product history list, and a viewer for the selected product. Generation targets the selected collection.
- **Why it matters:** Unlocks knowledge products with a frontend for the first time.
- **Related success criteria:** SC-004, SC-006
- **Acceptance notes:** Each button calls the existing `POST /collections/{id}/generate/*` endpoint. Loading spinner during generation. Flashcards render as Q&A list; text products render as formatted markdown.
- **Validation surface:** Manual test: generate each product type → verify content renders.

### REQ-008: Chat Inline Generation
- **Requirement:** Generate buttons (study guide, briefing doc, FAQ, timeline, glossary, flashcards) appear in the Chat panel composer toolbar ONLY after a collection is selected. Generated products render as chat messages (assistant role) with formatted output.
- **Why it matters:** Users must scope to a collection/notebook before generating study products.
- **Related success criteria:** SC-004, SC-005
- **Acceptance notes:** Generate buttons and chat input are disabled/hidden until `selectedCollectionId` is set. Clicking a generate button inserts a new assistant message with loading state. On completion, the product renders in the message. The product is also added to the Studio panel history via shared context.
- **Validation surface:** Manual test: verify empty state before selection → select collection → verify generate buttons appear → click generate → verify chat message renders → verify product appears in Studio history.

### REQ-005: SourceBrowser Inline Adaptation
- **Requirement:** SourceBrowser renders inline in the Sources panel (not as a right-side drawer) when a user clicks a document.
- **Why it matters:** Source browsing should not overlay the chat or studio panels.
- **Related success criteria:** SC-003
- **Acceptance notes:** SourceBrowser content fills the Sources panel width. Chunk notes editor preserved.
- **Validation surface:** Manual test: click document in Sources panel → verify inline view.

### REQ-006: Routing Restructure
- **Requirement:** `/chat` → WorkspaceLayout, `/chat/:sessionId` → WorkspaceLayout with pre-selected session. `/`, `/collections` → redirect to `/chat` or show simplified standalone page. `/playground`, `/evaluation`, `/settings` remain standalone.
- **Why it matters:** Enables both the workspace experience and admin tool access.
- **Related success criteria:** SC-003
- **Acceptance notes:** Navigation to a non-workspace route collapses/removes panels cleanly. Navigation back to `/chat` restores the workspace.
- **Validation surface:** Manual test: navigate chat → settings → back to chat → verify panel state.

### REQ-007: Collapsible Panels
- **Requirement:** Sources panel (left) and Studio panel (right) are collapsible at all viewport sizes. Default: both collapsed to icon strips, Chat panel centered full-width. Clicking a panel icon expands it; clicking again collapses it. At ≤768px, only one panel visible at a time with tab switcher.
- **Why it matters:** Gives users full focus on chat when needed while keeping sources and studio one click away.
- **Related success criteria:** SC-003
- **Acceptance notes:** Icons remain visible for Sources and Studio in collapsed state. Clicking an icon slides the panel open. Panels can be independently collapsed/expanded. At ≤768px, panels enter single-panel mode with bottom tab bar.
- **Validation surface:** Manual test: verify default collapsed → click Sources icon → panel opens → click again → collapses → repeat for Studio → resize to 768px → verify single-panel mode.

## Non-Functional Requirements

- **NFR-001 Performance:** WorkspaceLayout must render with no additional layout shift beyond existing page load. Initial render time must not exceed current `/chat` render time by more than 100ms.
  - *Linked ACs:* AC-007
- **NFR-002 State Consistency:** Shared React Context updates must propagate to all panels within a single render cycle. No stale collection scope after toggle.
  - *Linked ACs:* AC-001, AC-002
- **NFR-003 Responsiveness:** Panel collapse/expand transitions must complete within 240ms (matching `--motion-slow` CSS variable).
  - *Linked ACs:* AC-006
- **NFR-004 Regression Risk:** Zero regression on existing SSE streaming, citation, and X-Ray interactions.
  - *Linked ACs:* AC-003

## Constraints

- All existing components are reused, not rewritten.
- SSE streaming contract (`status → token → citations → trace → done`) is immutable.
- No new backend endpoints — only frontend re-architecture.

## Assumptions

- Single-tenant, single-user (no auth context).
- Knowledge products generate within 15s (backends are local).
- User has at least 1280px horizontal resolution for comfortable 3-panel use.

## Risks

- **Zero frontend tests** — refactoring 3 large screens (Chat 448 LOC, DocLib 254 LOC, Collections 115 LOC) with no test safety net is high risk. *Mitigation:* Add smoke tests for critical user flows (chat cycle, source browse, session CRUD) before refactoring.
- **State drift** — shared React Context could become stale if panels update asynchronously. *Mitigation:* All state mutations go through a single context dispatch. ChatPanel re-reads context before each SSE stream.
- **CSS bloat** — adding panel layout to 733-line styles.css without extraction. *Mitigation:* Append only layout classes; no refactoring of existing styles.

## Acceptance Criteria

- [ ] AC-001 (REQ-002, SC-001): Selecting a collection in SourcesPanel updates ChatPanel scope.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-001`
  - *Proof:* Cypress test: select collection → verify ChatPanel header shows collection name.

- [ ] AC-002 (REQ-002, SC-002): Toggling documents on/off changes chat scope.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-002`
  - *Proof:* Cypress test: default all checked → uncheck 3 docs → verify scope counter updates.

- [ ] AC-003 (REQ-003, SC-003): Full chat cycle works in WorkspaceLayout.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-003`
  - *Proof:* Cypress test: create session → send query → verify SSE stream renders → click citation → modal opens → X-Ray opens.

- [ ] AC-004 (REQ-004, SC-004): Generate buttons appear in both StudioPanel and ChatPanel composer toolbar.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-004`
  - *Proof:* Cypress test: verify 6 generate buttons in StudioPanel → verify same 6 buttons in ChatPanel composer toolbar.

- [ ] AC-005 (REQ-005): SourceBrowser renders inline in SourcesPanel.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-005`
  - *Proof:* Cypress test: click document in SourcesPanel → verify SourceBrowser renders inside left panel (not as overlay drawer).

- [ ] AC-006 (REQ-007, NFR-003): Panels collapse at breakpoints.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-006`
  - *Proof:* Cypress test: resize to 1024px → verify panels collapse to icons → resize to 768px → verify single-panel mode.

- [ ] AC-007 (REQ-001, NFR-001): WorkspaceLayout render time ≤ current ChatScreen render time + 100ms.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-007`
  - *Proof:* Performance measurement: `performance.mark()` before/after mount in WorkspaceLayout vs ChatScreen.

- [ ] AC-008 (REQ-008, SC-005): Generated products render as chat messages.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-008`
  - *Proof:* Cypress test: click generate in ChatPanel composer → verify assistant message appears with formatted product content → verify same product in StudioPanel history.

- [ ] AC-009 (REQ-006): Routing works: `/chat` → workspace, `/settings` → standalone, back navigation restores workspace.
  - *Verification:* `bash scripts/harness/gate-runner.sh 4.0-ui-panel-restructure --ac AC-009`
  - *Proof:* Cypress test: navigate `/chat` → `/settings` → `/chat` → verify panels render.

## Related ADRs

- ADR-001 (Proposed): Routing strategy — Option A (nested routes). Artifact: `core-zero/project/adr/001-routing-strategy.md`.

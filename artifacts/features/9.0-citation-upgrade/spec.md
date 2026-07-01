# Feature Specification: 9.0 Citation Upgrade

## Metadata

- Feature name: Citation Upgrade & UI Anchoring
- Feature slug: 9.0-citation-upgrade
- Delivery profile: Complex
- Owner: Antigravity
- Status: Approved
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/9.0-citation-upgrade/analysis.md)

## Problem Statement

The current RAG pipeline uses post-hoc regex citation extraction, which is less reliable than generation-time enforcement. Inline citation badges in the chat interface display long document titles directly inline, cluttering the reading flow. Additionally, clicking these badges opens a modal overlay rather than anchoring (visually highlighting and scrolling to) the source context directly in the left Sources panel (`SourceBrowser`).

## Desired Outcomes

- High-precision, generation-time citation enforcement.
- Clean inline reading flow using short, uniform citation labels (`[Source N]`).
- Visual citation anchoring: clicking a badge highlights and scrolls to the exact chunk in the left Sources panel.
- Backward compatibility with legacy `[Source N]` citations.

## Minimum Release Slice

- **What ships in the first useful release:**
  - Upgraded prompt instructions forcing inline citations.
  - Regex changes in backend and frontend to parse both `[Source N]` and `[N]`.
  - Normalizing inline badges to short labels.
  - State tracking in `WorkspaceContext` for `activeChunkId` and panel expansion.
  - visual highlight and automatic scroll-to-chunk in `SourceBrowser`.
  - Highlight cleanup on panel collapse or browser closure.
  - Disabled state for invalid/mismatched citation labels.
- **What can wait:**
  - Interactive multi-hop graph visualization of citations.
  - Page-level PDF highlights (we currently highlight chunk blocks).

## Success Criteria

- **SC-001**: 100% of generated facts match corresponding chunks via citation numbers.
- **SC-002**: Regular expressions parse both legacy `[Source 1]` and new `[1]` formats.
- **SC-003**: Clicking an inline citation badge expands the left panel and scrolls the correct chunk item into view in the document browser.
- **SC-004**: Citation badges render only the short label (e.g. `[Source 1]`) inline, moving long titles to tooltips/HoverCards.

## In Scope

- Prompt updates in `backend/chat/prompts.py`.
- Regex extraction updates in `backend/chat/citations.py`.
- Inline parsing updates in `frontend/src/components/ChatPanel.jsx`.
- Context state updates in `frontend/src/context/WorkspaceContext.jsx`.
- Highlight and scroll logic in `frontend/src/components/SourceBrowser.jsx`.
- Styles in `frontend/src/styles.css` for visual highlight classes.

## Out Of Scope

- Backend reranking logic modifications.
- Vector search or chunking strategy enhancements.
- Authentication or JWT integrations.
- Multi-modal citations (audio, image).

## Non-Goals

- Replacing Weaviate as the vector database.
- Modifying SQLite schemas.

## Users And Stakeholders

- **Primary users**: Researchers, analysts, and students using the document chatbot who need to verify claims quickly by looking at source documents in context.

## User Stories And Key Scenarios

- **US-001**: As a researcher, I want to read clean, uncluttered chat responses with short citation badges, so that I can maintain reading flow.
- **US-002**: As an analyst, I want to click a citation badge and see the exact source passage highlighted on the left sources panel, so that I can verify facts instantly.

### Detailed Scenarios

- **Scenario 1 (Happy Path - Visual Anchoring)**:
  - **Given**: A chat response is displayed with an inline badge `[Source 1]`. The left Sources panel is currently collapsed.
  - **When**: The user clicks the `[Source 1]` badge.
  - **Then**: The left Sources panel expands (`sourcesCollapsed: false`), the matching document opens in the `SourceBrowser` panel, and the corresponding chunk is styled with an active border highlight and scrolled smoothly into view.
- **Scenario 2 (Edge Case - Mixed/Alternate Format)**:
  - **Given**: The LLM output contains both legacy format `[Source 2]` and short format `[3]`.
  - **When**: The backend extracts citations and the frontend renders the turn.
  - **Then**: Both are parsed correctly and rendered uniformly as clickable badges `[Source 2]` and `[Source 3]` matching their respective context chunks.
- **Scenario 3 (Edge Case - Mismatched Citation)**:
  - **Given**: The LLM output refers to `[Source 9]` but only 2 chunks are in context.
  - **When**: The frontend renders the chat turn.
  - **Then**: The badge `[Source 9]` is displayed in a disabled (muted) state, cannot be clicked, does not trigger a HoverCard, and logs a warning.
- **Scenario 4 (Cleanup Path - Panel Collapse)**:
  - **Given**: An active chunk is currently highlighted and focused in `SourceBrowser`.
  - **When**: The user manually collapses the left panel or closes the `SourceBrowser`.
  - **Then**: The `activeChunkId` state is reset to `null` to clear any stale highlights.

## Current Context

- **Current behavior summary**: Parses `[Source N]` regex post-hoc, displays `[Document Title]` inline which creates long clunky badges, and clicking opens a modal overlay (`CitationModal`) that duplicates note-taking features found in the browser.
- **Impacted boundaries**: `backend/chat`, `frontend/src/components`, `frontend/src/context`.
- **Preserved behavior**: Streaming SSE tokens must remain untouched; citation extraction and DB save happens post-generation.
- **Brownfield risk rating**: Medium (requires modifying shared React context state and regex patterns in both backend/frontend).

## Gray-Area Decisions

- **Locked decisions**:
  - We discard the `CitationModal` for inline badge clicks in favor of direct left Sources panel highlighting/scrolling.
  - Badges render as `[Source N]` inline rather than resolving document titles.
- **Remaining decisions**:
  - None.

## Dependencies And External Touchpoints

- **DEP-001**: React `WorkspaceContext` manages side-panel collapse and document states.

## Functional Requirements

### REQ-001: Generation-Time Prompt Enforcement
- **Requirement**: Update prompts in `prompts.py` to instruct the model to always append citation markers in brackets after factual claims and ensure every sentence is grounded.
- **Why it matters**: Crucial for citation completeness.
- **Linked ACs**: `AC-001`
- **Priority**: Must Have

### REQ-002: Backward-Compatible Citation Parser
- **Requirement**: Update the regular expression in `citations.py` and `ChatPanel.jsx` to parse both `[Source N]` and `[N]` syntax.
- **Why it matters**: Supports legacy database rows while accepting updated formats.
- **Linked ACs**: `AC-002`
- **Priority**: Must Have

### REQ-003: Short Badge Rendering
- **Requirement**: Update `ChatPanel.jsx` inline rendering so that badges display the uniform short format `[Source N]` (or `[N]`) instead of the resolved document title.
- **Why it matters**: Stops long titles from cluttering chat text.
- **Linked ACs**: `AC-003`
- **Priority**: Must Have

### REQ-004: Workspace Anchoring State Actions
- **Requirement**: Extend `WorkspaceContext.jsx` with an `activeChunkId` state and functions to set it and expand the sources panel.
- **Why it matters**: Coordinates click events between panels.
- **Linked ACs**: `AC-004`
- **Priority**: Must Have

### REQ-005: Visual Highlight & Scroll
- **Requirement**: Update `SourceBrowser.jsx` to select, highlight, and scroll to the chunk matching `activeChunkId`.
- **Why it matters**: Completes the anchoring UX loop.
- **Linked ACs**: `AC-005`
- **Priority**: Must Have

### REQ-006: Highlight State Reset
- **Requirement**: Clear `activeChunkId` when the sources panel is manually collapsed or the document browser is closed.
- **Why it matters**: Prevents stale focus states.
- **Linked ACs**: `AC-006`
- **Priority**: Must Have

### REQ-007: Invalid Citation Handling
- **Requirement**: Muted styling and disabled interactions for badges with invalid indices/IDs.
- **Why it matters**: Gracefully handles hallucinations.
- **Linked ACs**: `AC-007`
- **Priority**: Must Have

## Non-Functional Requirements

- **NFR-001 Performance**: Citation parsing must run in `< 10ms` on the frontend.
- **NFR-002 Reliability**: Regex matching must not trigger infinite backtracking.
- **NFR-003 Security**: Citation parsing must not execute code injections embedded in source text.
- **NFR-004 Accessibility**: Focused chunks must have clear focus states for keyboard users.
- **NFR-005 Observability**: Invalid citations must be logged and visible in the `XRayPanel` traces.

- **Linked ACs**: `AC-002`, `AC-005`, `AC-007`

## Constraints

- **Technical**: All React components must follow existing styles and separate screens from modular sub-components.

## Assumptions

- **ASM-001**: The model has retrieved chunks with valid IDs that match frontend-loaded documents.

## Risks

- **RISK-001**: Smooth-scroll alignment fails if target elements are not yet mounted.
  - *Mitigation*: Ensure scrolling is triggered after document is loaded or use brief timeout/useEffect triggers.

## Acceptance Criteria

- [ ] **AC-001 Linked REQ**: REQ-001
  - **Linked scenario**: Scenario 2 (Happy Path)
  - **Validation method**: System prompts contain explicit instructions forcing citation identifiers.
  - **Proof target**: Manual code audit.

- [ ] **AC-002 Linked REQ**: REQ-002
  - **Linked scenario**: Scenario 2
  - **Validation method**: Run tests asserting parsing of `[Source 1]`, `[2]`, and mixed labels.
  - **Proof target**: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_citations.py`

- [ ] **AC-003 Linked REQ**: REQ-003
  - **Linked scenario**: Scenario 1
  - **Validation method**: Inline badge renders only the short text `[Source 1]`.
  - **Proof target**: Manual UI check.

- [ ] **AC-004 Linked REQ**: REQ-004
  - **Linked scenario**: Scenario 1
  - **Validation method**: Context dispatches actions to set `activeChunkId` and toggle side panel.
  - **Proof target**: Unit/Manual context state validation.

- [ ] **AC-005 Linked REQ**: REQ-005
  - **Linked scenario**: Scenario 1
  - **Validation method**: Active chunk styled with `2px solid var(--accent-strong)` and scrolled into view.
  - **Proof target**: Manual visual alignment validation.

- [ ] **AC-006 Linked REQ**: REQ-006
  - **Linked scenario**: Scenario 4
  - **Validation method**: Context `activeChunkId` is `null` when panel is collapsed.
  - **Proof target**: State audit.

- [ ] **AC-007 Linked REQ**: REQ-007
  - **Linked scenario**: Scenario 3
  - **Validation method**: Unmatched badge styled with muted colors, no hovercard portal, and cursor set to default.
  - **Proof target**: Manual test with fabricated citation values.

## Related ADRs

- None.

## Notes
- None.

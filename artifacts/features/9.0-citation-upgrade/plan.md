# Implementation Plan: 9.0 Citation Upgrade

## Metadata

- Feature slug: 9.0-citation-upgrade
- Date: 2026-07-01
- Status: Approved

---

## Part 1: Technical Design

### Comprehensive Design

- **Design Summary**:
  This solution upgrades the citation system by implementing strict generation-time citation enforcement, a flexible regex parser supporting both `[Source N]` and `[N]` syntax, and a visual anchoring UX. Clicking an inline badge expands the left Sources panel, loads the correct document in the browser, and highlights/scrolls to the target chunk block in the DOM instead of opening a modal overlay. Badges are simplified to display only their short labels (`[Source N]`) inline.

- **Current State**:
  - The backend parses `[Source N]` post-hoc and maps to chunk index/UUID.
  - Badges render with full document titles inline, disrupting message readability.
  - Chat panel click events are isolated and render an overlay `CitationModal`.
  - `SourceBrowser` maintains `selectedChunk` as local state initialized to `null`. It does not support scroll-to-chunk or external focus targeting.

- **Proposed Architecture**:
  - **Prompt Upgrades**: Revise `BASE_GROUNDED_CHAT_SYSTEM_PROMPT` in `backend/chat/prompts.py` to enforce that the LLM *must* append citation markers immediately after factual claims.
  - **Regex Normalization**: Update `CitationService` (`backend/chat/citations.py`) and `ChatPanel.jsx` to parse `\[(?:Source\s+)?([^\]]+)\]`.
  - **Workspace State Management**: Extend `WorkspaceContext.jsx` to maintain `activeChunkId`. Triggering `setActiveChunkId` will:
    - Automatically expand the left Sources panel (`sourcesCollapsed: false`).
    - Load the corresponding document in `SourceBrowser` by setting `activeDocumentId`.
  - **Anchoring & Auto-Scroll**: Update `SourceBrowser.jsx` to:
    - Listen for `activeChunkId`.
    - Auto-select the corresponding chunk index.
    - Scroll the highlighted element into view using `element.scrollIntoView({ behavior: "smooth", block: "nearest" })`.
    - Apply a custom visual highlight border and soft background in `frontend/src/styles.css`.
  - **Highlight Reset**: Clear `activeChunkId` when `SourceBrowser` is closed or the left Sources panel is manually collapsed.

- **Data Flow & Interfaces**:
  ```
  [User Clicks Badge] ──> Dispatch activeChunkId & activeDocumentId to WorkspaceContext
                              │
                              ├──> Expands SourcesPanel (sourcesCollapsed: false)
                              └──> Loads SourceBrowser (activeDocumentId set)
                                        │
                                        └──> SourceBrowser selects & scrolls to chunk
  ```

- **Key Decisions & Tradeoffs**:
  - *Decision 1*: Transition from `CitationModal` overlay to left Sources panel anchoring. Tradeoff: Avoids screen overlay clutter and reuses the existing NoteEditor in `SourceBrowser`, preventing duplicate code.
  - *Decision 2*: Inline badges show short label format `[Source N]` instead of full document titles. Tradeoff: Text is cleaner, while document titles remain discoverable via HoverCard and SourceBrowser.
  - *Decision 3*: Flexible regex `\[(?:Source\s+)?([^\]]+)\]` to support both `[Source N]` and `[N]`. Tradeoff: Retains full backward compatibility with legacy database entries.

- **Non-Functional Considerations**:
  - *Performance*: Highlight-and-scroll trigger must execute after `SourceBrowser` data fetching/rendering completes (handled via React `useEffect` hook).
  - *Reliability*: Backend regex avoids backtracking.
  - *Observability*: Invalid/unmatched citation indices render in a disabled state and log mismatch details to the `XRayPanel`.

- **Protected Behavior**:
  - Streaming SSE output pipeline remains untouched (INV-003, INV-007).
  - Layered safety filters are unchanged (INV-001).

---

## Part 2: Delivery Strategy

### Execution Context
- **Delivery profile**: Complex
- **Locked spec decisions**:
  - Inline badges show `[Source N]` short name only.
  - Badge click focuses, scrolls, and highlights in the left panel instead of opening a modal.
  - Supports both `[Source N]` and `[N]` syntax.

### First Delivery Slice
- **Smallest useful slice**: Setup backend prompt reinforcement and regex changes to parse both `[Source N]` and `[N]` formats, verified with backend unit tests.
- **Why this slice goes first**: Establishes data contract correctness before modifying frontend rendering or workspace states.
- **What proof should exist when this slice is done**: `test_citations.py` unit tests pass successfully.

### Execution Phases

#### Phase 1: Backend Prompt & Parser Upgrades
- **Goal**: Implement generation-time citation instructions and flexible backend citation parsing.
- **Enabled user scenario(s) or outcome(s)**: Precise, flexible backend parsing of `[Source N]` and `[N]` citation tokens.
- **Entry proof**: Baseline `pytest` runs cleanly.
- **Exit proof**: `pytest` passes with new tests verifying updated matching.
- **Completion criteria**:
  - `prompts.py` updated.
  - `citations.py` regex modified to `\[(?:Source\s+)?([^\]]+)\]` and matching logic updated.
  - New test cases added in `test_citations.py`.

#### Phase 2: Frontend Regex & Context State
- **Goal**: Normalize frontend badge parsing and extend workspace state with active chunk tracking.
- **Enabled user scenario(s) or outcome(s)**: Clean inline badges showing short labels, and unified click dispatching.
- **Entry proof**: Phase 1 tests pass.
- **Exit proof**: Context state update compiles and dispatches correctly.
- **Completion criteria**:
  - `ChatPanel.jsx` parses both formats and renders normalized `[Source N]` short badges.
  - `WorkspaceContext.jsx` updated with `activeChunkId` state, action, and auto-expand logic.
  - Clicking a badge sets `activeChunkId` and `activeDocumentId` in the context.

#### Phase 3: Anchoring & Visual Highlight in SourceBrowser
- **Goal**: Auto-select, highlight, and scroll target chunk into view inside the browser.
- **Enabled user scenario(s) or outcome(s)**: End-to-end visual citation anchoring in the sources panel.
- **Entry proof**: Phase 2 state actions working.
- **Exit proof**: Clicking badge successfully expands sources panel, opens browser, and scrolls to target chunk.
- **Completion criteria**:
  - `SourceBrowser.jsx` updated to select active chunk from props/context, and apply scroll-into-view.
  - CSS styles added in `styles.css` for visual highlight.
  - Reset action wired to manually collapsing the left panel or closing the browser.
  - Disabled state styled and applied for invalid citation badges.

### Validation Strategy
- **Unit tests**: `backend/tests/chat/test_citations.py` covering standard/short citation inputs.
- **Manual verification**: Traceability scenarios outlined in `spec.md` (Scenario 1, Scenario 3, Scenario 4).

### Traceability Matrix
- Scenario 1 (Happy Path) -> Phase 2 & Phase 3 (TASK-003, TASK-004, TASK-005)
- Scenario 2 (Alternate Format) -> Phase 1 & Phase 2 (TASK-001, TASK-002, TASK-003)
- Scenario 3 (Mismatched Citation) -> Phase 3 (TASK-006)
- Scenario 4 (Cleanup Path) -> Phase 3 (TASK-007)
- REQ-001 -> TASK-001
- REQ-002 -> TASK-002
- REQ-003 -> TASK-003
- REQ-004 -> TASK-004
- REQ-005 -> TASK-005
- REQ-006 -> TASK-007
- REQ-007 -> TASK-006

### Rollout Plan
- **Release approach**: Atomic deployment of frontend + backend updates.
- **Feature flags**: None.
- **Migration needs**: None.
- **Backward compatibility notes**: Supports matching `[Source N]` for old chat turns.

### Rollback Plan
Revert changes using Git checkout on modified files.

### Risks And Mitigations
- **RISK-001**: Scrolling fails if DOM is not yet rendered.
  - *Mitigation*: Trigger scroll inside a `useEffect` layout block with `activeChunkId` as dependency, utilizing a short timeout/requestAnimationFrame if necessary to ensure mounting.

### Open Questions
- None.

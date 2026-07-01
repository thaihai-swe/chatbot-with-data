# Proposal: 9.0 Citation Upgrade

## The Problem
The current RAG pipeline uses post-hoc regex citation extraction, which is less reliable than generation-time enforcement. Additionally, clicked citations in the chat interface display a modal overlay rather than visually highlighting the source context in the left Sources panel, creating a disconnected user experience compared to Google Notebook LM. Badges also display long document titles inline, cluttering the reading flow.

## Objectives
1. **High-Accuracy Citations**: Shift to strict generation-time prompt instructions to guarantee that the LLM references correct sources.
2. **Normalized Citation Formats**: Support both `[Source N]` and `[N]` citation formats inline and parse them robustly.
3. **Visual Citation Anchoring**: Click inline badges to open/highlight the target document chunk directly in the left Sources panel (`SourceBrowser`).
4. **Readable Inline Badges**: Restrict inline badges to short labels (e.g. `[Source 1]`) rather than rendering full document titles.

## High-Level Approach
- Update system prompt templates to enforce citation placement.
- Revise citation extraction regexes in `CitationService` and `ChatPanel.jsx` to match both legacy and updated formats.
- Update `WorkspaceContext` to track `activeChunkId` and toggle pane collapse state.
- Update `SourceBrowser` to highlight and auto-scroll the chunk matching `activeChunkId`.
- Simplify badge rendering to display short labels, moving full context/titles to HoverCard and SourceBrowser.

## Known Constraints / Risks
- **Backward Compatibility**: Existing database entries using `[Source N]` must remain parseable and valid.
- **Scroll Alignment**: Smooth scrolling long document chunk lists to the active chunk.

## Gray Areas To Resolve
- **UX Overlay vs. Left Pane**: Confirmed that clicking a citation will focus the left Sources panel/document viewer instead of opening the `CitationModal` overlay.
- **Badge Labels**: Confirmed that inline badges will render only the short label (e.g. `[Source N]`).

## Success Criteria
- [ ] LLM generated turns consistently produce citations matching retrieved chunk indices.
- [ ] Parser correctly handles both `[Source N]` and `[N]` syntax.
- [ ] Clicking a citation badge expands the left Sources panel, opens the document browser, and scrolls the chunk into view with a visual highlight.
- [ ] Inline citation badges show the short label (e.g., `[Source 1]`) regardless of how long the document title is.

---
Status: Aligned

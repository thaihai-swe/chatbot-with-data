# Research Analysis: 9.0 Citation Upgrade

## Metadata
- Investigation name: Citation Feature Upgrade & Parity Mapping
- Feature slug: 9.0-citation-upgrade
- Date: 2026-07-01
- Status: Research Complete

## Scope

- **What is being investigated:**
  - Upgrading the citation feature to enforce generation-time citations.
  - Displaying only the short source label (e.g., `[Source N]`) inline in the message text, rather than resolving and rendering the full document title inside the badge.
  - Anchoring citations in the UI: Clicking an inline citation badge should expand the left Sources panel, open the corresponding document in `SourceBrowser`, select the specific chunk, and scroll it into view with a visual highlight.
  - Streamlining quote extraction to avoid costly LLM fallbacks.
- **What is explicitly out of scope:**
  - Authentication (which is a separate production-gate requirement).
  - Docker deployment configuration.
  - Reranker model integration (such as BGE-Reranker-v2).
  - Multi-modal (image/audio) citation mapping.

## Current State

- **Observed current behavior:**
  - The model receives sources wrapped in `<source label="Source N" id="...">` tags.
  - Prompt instructions request the model to place `[Source N]` after factual claims.
  - Citations are parsed post-hoc from the generated answer via regex `\[Source\s+([^\]]+)\]`.
  - Sentence-level Jaccard word-overlap (threshold 0.5) is used to find the exact quote. If it fails, the system falls back to an LLM-based `QUOTE_EXTRACTION_PROMPT` call, introducing latency.
  - Clicking a citation in the frontend UI opens a local `CitationModal` overlay but doesn't interact with the left panel or scroll to the source document.
- **Relevant boundaries or components:**
  - **Backend:**
    - [citations.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/citations.py) (`CitationService`): Extracts citations, calculates Jaccard sentence overlap, runs LLM fallback.
    - [prompts.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/prompts.py): System prompts and instructions.
    - [service.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/service.py) & [streaming.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/streaming.py): Orchestration of RAG pipeline steps and SSE updates.
  - **Frontend:**
    - [ChatPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ChatPanel.jsx): Parses response text for citation labels and handles badge click actions.
    - [WorkspaceContext.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/context/WorkspaceContext.jsx): Stores active document, selected collections, and panel collapse state.
    - [SourceBrowser.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/SourceBrowser.jsx): Renders chunk items and notes in the document viewer.
- **Unchanged behavior that must be preserved:**
  - Streaming answers must remain incremental and append-only; citations and metadata are resolved at the end of the generation step to avoid interrupting token flow.
  - Existing database records containing `[Source N]` must continue to parse correctly in the frontend.
  - The X-Ray panel trace information must not be broken.

## Decision-Ready Summary

- **What matters most:** Achieving Notebook LM citation alignment requires linking frontend context states. Clicking a citation must dispatch the target document ID and chunk ID to `WorkspaceContext.jsx`, expand the Sources panel, and scroll the highlighted chunk element into view. In the frontend, the citation badge must render only the short source label (e.g., `[Source N]`) inline rather than the full document title to keep the reading flow clean. On the backend, we must update the prompts to strictly enforce citations per claim and extend the citation regexes to support both `[Source N]` and `[N]` syntax.
- **Strongest supported conclusion:** The visual anchoring upgrade can be implemented cleanly by extending `WorkspaceContext` to track `activeChunkId`, having `SourceBrowser.jsx` accept this ID to auto-select and scroll the chunk, and using a relaxed regex `\[(?:Source\s+)?([^\]]+)\]` to support both citation formats and resolve short labels.
- **Single next proving step:** Transition to `/spec-requirements` to draft a requirements spec defining the updated prompt instructions, regex patterns, short badge inline rendering, context actions, and scroll-into-view behavior.

## Findings

- **Finding 1: Below-threshold quote mapping incurs blocking LLM calls.**
  - *Evidence:* [citations.py:97-115](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/citations.py#L97-L115) shows that if Jaccard similarity is below 0.5, it makes an LLM call to extract the quote. This adds latency to response finalization.
  - *Type:* Fact.
- **Finding 2: The panels operate in silos.**
  - *Evidence:* Clicking a citation only updates local state `activeCitation` inside `ChatPanel.jsx` to render the modal overlay. The left `SourcesPanel` is not notified of the selected source.
  - *Type:* Fact.
- **Finding 3: `SourceBrowser` does not support external selection of chunks.**
  - *Evidence:* In [SourceBrowser.jsx:230](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/SourceBrowser.jsx#L230), `selectedChunk` is internal state initialized to `null`. It does not react to any external property to focus or scroll.
  - *Type:* Fact.
- **Finding 4: The parser is hardcoded to `[Source N]`.**
  - *Evidence:* Both [citations.py:19](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/citations.py#L19) and [ChatPanel.jsx:377](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ChatPanel.jsx#L377) enforce the literal prefix `Source` in their regexes, ignoring `[N]` tokens.
  - *Type:* Fact.

## Risks And Unknowns

- **Risk: Scroll Alignment and DOM Reference.**
  - *Why it matters:* Scrolling to the specific chunk requires `SourceBrowser` to have references to the individual chunk elements or use selectors. If elements are not rendered or the list is long, it might scroll incorrectly.
  - *Next proving step:* Use React `useRef` or dynamic `id`/`data-chunk-id` attributes and `element.scrollIntoView({ behavior: 'smooth', block: 'nearest' })`.
- **Risk: Backward compatibility of database references.**
  - *Why it matters:* If we change the citation pattern representation, we must ensure existing database turns load correctly and their citations match the regex.
  - *Next proving step:* Implement and test the regex `\[(?:Source\s+)?([^\]]+)\]` which matches both legacy and upgraded formats.

## Recommendation

- **Next skill or artifact:** `/spec-requirements`
- **Why:** The requirements for regex changes, prompt tuning, state transitions, and frontend styling should be fully documented before drafting the execution plan.
- **Exact next prompt or action:** Proceed to `/spec-requirements` to define requirements for the citation upgrade.

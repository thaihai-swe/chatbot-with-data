# Proposal: UX Upgrade

## Overview
This proposal defines the scope for addressing the Tier 3 UX gaps identified in the comparison against Google NotebookLM. The feature introduces non-blocking source previews, full-text document browsing with chunk mapping, and user annotations persisted per chunk and injected into RAG context.

## In Scope
1. **Citation Hover Tooltip:**
   * Instant, non-blocking preview of chunk details (title, page, relevance, excerpt) when hovering over inline citation tags in the chat bubble.
2. **Full-Text Source Browser:**
   * UI feature in the Document Library screen to view the complete text of any document alongside its parsed chunks.
3. **User Annotation System (Notes linked to chunks):**
   * SQLite schema to save notes per chunk.
   * Backend APIs to save, update, and retrieve chunk notes.
   * Inline notes editing textareas in both `CitationModal` (chat) and the new `Source Browser` (document library).
   * Context Assembly enrichment: dynamically inject user notes as a `user_note="..."` attribute inside `<source>` context elements sent to the LLM during grounded answer generation.

## Out Of Scope
* Real-time audio overviews or slide generation.
* Editing document text or changing partition boundaries (read-only for chunks, read/write for notes).
* Authentication middleware (LH-004 baseline assumes single-tenant).

## Non-Goals
* Upgrading Weaviate vector databases or modifying hybrid reranking calculations.
* Live synchronization of Google Docs or other third-party services.

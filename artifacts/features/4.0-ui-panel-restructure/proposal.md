# Proposal: UI Panel Restructure

## Overview
Restructure the single-column chat UI into a Notebook LM-style 3-panel layout: Sources (left) + Chat (center) + Studio (right). The chat panel anchors the experience — users begin by selecting a collection/notebook, which defaults to all documents, with the ability to choose specific documents before querying.

## In Scope
1. **Workspace Layout (3-Panel):**
   * Persistent left panel for document sources and collection navigation.
   * Persistent center panel for chat (extracted from current `ChatScreen`, preserving all interactions).
   * Persistent right panel for knowledge products (Studio) — study guides, flashcards, timelines, etc.
   * Collapsible responsive behavior on smaller screens.

2. **Collection/Document Selection Flow:**
   * User selects a collection (notebook) to scope the chat.
   * Default: all documents in that collection are selected.
   * User can toggle individual documents on/off within the selection.
   * Selection scope is reflected in chat query routing.

3. **Routing Restructure:**
   * `/chat` serves as the 3-panel workspace route (optionally with `:sessionId`).
   * Standalone screens (Settings, Evaluation, Playground) remain as separate routes.
   * `/library` and `/collections` content migrates into the Sources panel.

4. **State Management:**
   * Lightweight shared context for cross-panel state: selected collection(s), selected document(s), active document for browsing.
   * Chat session/message state stays local to ChatPanel.

5. **Knowledge Product Generation in Chat:**
   * Generate buttons accessible from both the Studio panel (right) and the Chat panel (inline in composer toolbar).
   * Generated products render as chat messages in the Chat panel (formatted markdown for text products, structured Q&A for flashcards).
   * Studio panel shows a history of generated products for the current session.

6. **CSS Panel Layout:**
   * Workspace layout CSS for the 3-panel flex container.
   * Responsive breakpoints for collapsible panels.

## Out Of Scope
* Adding SSE streaming to knowledge product endpoints (keep sync with loading states).
* Backend changes to the RAG pipeline (routing, retrieval, generation).
* Authentication, multi-tenancy, or permission-aware retrieval.
* Mobile-native app (responsive web only).
* New knowledge product types beyond the existing 6.

## Non-Goals
* Rewriting components from scratch — all existing components are reused or adapted.
* Full-screen X-Ray panel changes (remains as slide-in overlay).
* Replacing the CSS architecture with CSS modules or styled-components.

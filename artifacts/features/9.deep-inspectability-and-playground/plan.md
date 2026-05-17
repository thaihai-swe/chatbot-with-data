# Implementation Plan: Deep Inspectability and Playground

## Phase 1: Data Flow & Backend Enhancements
- **Goal:** Ensure the frontend has all the data needed for deep inspection.
- **Tasks:**
    - Update `StreamingOrchestrator` in `backend/chat/streaming.py` to include `retrieved_chunks` in the `citations` SSE event.
    - Verify `getChatHistory` and `createChatSession` API responses in the frontend include `retrieved_chunks`.

## Phase 2: Citation Detail View
- **Goal:** Allow users to inspect individual chunks.
- **Tasks:**
    - Create `frontend/src/components/CitationModal.jsx`.
    - Update `frontend/src/screens/Chat.jsx` to handle citation clicks and store chunk data.
    - Add necessary CSS for the modal.

## Phase 3: Playground Foundation
- **Goal:** Setup the side-by-side infrastructure.
- **Tasks:**
    - Create `frontend/src/components/PlaygroundPanel.jsx`.
    - Create `frontend/src/screens/Playground.jsx` with basic dual-panel layout.
    - Update `frontend/src/App.jsx` with the new route and navigation link.

## Phase 4: Comparative Logic & Polishing
- **Goal:** Implement diffing and final UX refinements.
- **Tasks:**
    - Implement parallel execution logic in `Playground.jsx`.
    - Implement `chunk_id` diffing and visual highlighting.
    - Responsive design pass for the side-by-side view.

## Validation Strategy
- **Manual Verification:** 
    - Click a citation in chat -> verify modal shows correct text and score.
    - Open Playground -> run query -> verify two independent panels load correctly.
    - Verify green/neutral highlighting for overlapping chunks.
- **Automated Tests:**
    - Add a unit test for the diffing logic (can be a small utility function).

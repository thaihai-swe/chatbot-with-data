# Tasks: Deep Inspectability and Playground

## Phase 1: Data Flow & Backend Enhancements

- [x] **TSK-001:** Update `StreamingOrchestrator` to include `retrieved_chunks` in SSE.
    - **Target:** `backend/chat/streaming.py`
    - **Proving:** Verified code change includes `safe_chunks` in `citations` event.
- [x] **TSK-002:** Verify `retrieved_chunks` availability in chat history.
    - **Target:** `frontend/src/screens/Chat.jsx`
    - **Proving:** Updated `ChatScreen` to parse `retrieved_chunks_json` and store it in messages state.

## Phase 2: Citation Detail View

- [x] **TSK-003:** Create `CitationModal.jsx` component.
    - **Target:** `frontend/src/components/CitationModal.jsx`
    - **Proving:** Created component with full chunk details and metadata display.
- [x] **TSK-004:** Integrate CitationModal into ChatScreen.
    - **Target:** `frontend/src/screens/Chat.jsx`
    - **Proving:** Added click handler and modal rendering to `ChatScreen`.
- [x] **TSK-005:** Add modal styles.
    - **Target:** `frontend/src/styles.css`
    - **Proving:** Appended modern glassmorphism styles for the modal.

## Phase 3: Playground Foundation

- [x] **TSK-006:** Create `PlaygroundPanel.jsx` component.
    - **Target:** `frontend/src/components/PlaygroundPanel.jsx`
    - **Proving:** Created panel with mode selector, config toggles, and results area.
- [x] **TSK-007:** Create `Playground.jsx` screen and navigation.
    - **Target:** `frontend/src/screens/Playground.jsx`, `frontend/src/App.jsx`
    - **Proving:** Integrated Playground into main app with dual-panel layout.

## Phase 4: Comparative Logic & Polishing

- [x] **TSK-008:** Implement parallel chat execution in Playground.
    - **Target:** `frontend/src/screens/Playground.jsx`
    - **Proving:** Used `Promise.all` to trigger simultaneous strategy executions.
- [x] **TSK-009:** Implement visual diffing logic.
    - **Target:** `frontend/src/screens/Playground.jsx`
    - **Proving:** Chunks are compared by `chunk_id` across panels and highlighted when matched.
- [x] **TSK-010:** Final UI/UX polish and responsiveness.
    - **Target:** `frontend/src/styles.css`, `frontend/src/screens/Playground.jsx`
    - **Proving:** Added glassmorphism styles and media queries for mobile-friendly vertical stacking.

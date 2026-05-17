# Design: Deep Inspectability and Playground

## Overview
This feature enhances the educational value of the RAG Knowledge Base Lab by providing granular visibility into retrieved chunks and allowing side-by-side strategy comparison.

## Architecture

### 1. Data Flow Enhancements
- **Backend:** Update `StreamingOrchestrator` to include the full `retrieved_chunks` data in the `citations` SSE event. Currently, it only includes citation mapping metadata.
- **Frontend:** Update `ChatScreen` and the new `Playground` screen to store the full `retrieved_chunks` array for each chat turn.

### 2. UI Components

#### `CitationModal.jsx` (New)
- A reusable glassmorphism modal component.
- **Props:** `chunk`, `onClose`.
- **Displays:**
    - Document Title (linked if URL available).
    - Retrieval Score.
    - Full Chunk Text.
    - Metadata (Page, Section).
    - Parent Context (if available in chunk metadata).

#### `PlaygroundPanel.jsx` (New)
- Represents one side of the comparison.
- Manages its own `retrievalConfig`, `answer`, `chunks`, and `isLoading` state.
- Highlights chunks based on a `isMatched` prop passed from the parent.

#### `Playground.jsx` (New Screen)
- **State:**
    - `query`: Shared across both panels.
    - `panelAConfig`, `panelBConfig`: Independent `AdvancedRetrievalConfig` objects.
    - `panelAResult`, `panelBResult`: Results from the API.
- **Logic:**
    - Triggers two parallel `streamChatTurn` (or equivalent) calls.
    - Computes `isMatched` for each chunk by checking if its `chunk_id` exists in the other panel's result.

### 3. Styling
- Use existing Vanilla CSS patterns for glassmorphism and modern aesthetics.
- Add specific styles for "Matched" vs "Unique" chunks (e.g., subtle green vs neutral border).

## Technical Trade-offs
- **Frontend Dual Execution:** We reuse the existing `POST /chat` endpoint. This avoids new backend complexity but doubles the request load. Given the lab scale, this is acceptable.
- **Transient Playground:** Results are not persisted to the DB to keep the playground focused on "quick experimentation" rather than long-term history.

## Impacted Boundaries
- `frontend/src/screens/Chat.jsx`: Addition of citation click handlers.
- `frontend/src/App.jsx`: Addition of `/playground` route.
- `backend/chat/streaming.py`: Update to SSE event payload.

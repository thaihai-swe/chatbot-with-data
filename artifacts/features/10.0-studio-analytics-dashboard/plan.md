# Implementation Plan: 10.0 Studio Analytics Dashboard

## Metadata

- Feature slug: 10.0-studio-analytics-dashboard
- Date: 2026-07-02
- Status: Approved

---

## Part 1: Technical Design

### Comprehensive Design

- **Design Summary**:
  This solution eliminates frontend mock states in the Studio Analytics Dashboard by synchronizing frontend components directly with backend settings and actual dynamic data from RAG traces and evaluations. The Hybrid Search Alpha Slider connects to the global `/settings` API using a debounced write cycle. The Vector Chunk Relevance histogram groups retrieval scores from the active session into density bins. The quality metrics cards cache and display real LLM-as-a-judge evaluation results. Finally, the document filter passes the target `document_id` into the generation API.

- **Current State**:
  - Alpha Slider: Local React state only; modifying it does not update the backend or influence retrieval.
  - Vector Chunk Histogram: SVG heights and values are hardcoded inline inside `StudioPanel.jsx`.
  - Quality Metrics: Cards display hardcoded strings (`98.2%`, `450ms`, etc.).
  - Document Selector: Local state `activeDocumentId` is selected, but not utilized during generation API calls in `knowledgeApi.js`.

- **Proposed Architecture**:
  - **Alpha Slider API Binding**: 
    - `StudioPanel.jsx` fetches `getSettings()` on mount to set the initial `alpha` state.
    - Implement a throttled `updateSettings` call or a slider `onChangeEnd` event that dispatches `{ retrieval: { hybrid_weight: alpha } }` to the backend.
    - Prevent the user from updating the slider when `settings.retrieval.retrieval_mode` is not `"hybrid"`.
  - **Real-Time Histogram Bins**: 
    - When a turn completes, `ChatScreen` or `WorkspaceContext` provides the latest `trace` object.
    - `StudioPanel` extracts `trace.retrieval.top_scores` (or calculates scores from `retrieved_chunks`).
    - Define five bins: `[0.0-0.2]`, `[0.2-0.4]`, `[0.4-0.6]`, `[0.6-0.8]`, `[0.8-1.0]`. Count occurrences per bin and scale SVG heights programmatically.
  - **Evaluation Data Sync**: 
    - Execute Sanity Check in `Evaluation.jsx`. 
    - Store the results (Groundedness, Recall, Latency, Relevancy) in `localStorage` or `WorkspaceContext`.
    - Both `Evaluation.jsx` and `StudioPanel.jsx` subscribe to this shared object and map the values to the UI cards.
  - **Document Bound Generation**: 
    - Update backend `routers/generate.py` to add `document_id: Optional[str] = Query(None)` to `/summary`, `/faq`, etc.
    - Update `/backend/chat/generation.py` services to filter chunk retrievals to match the specific `document_id` if provided.
    - Update `frontend/src/api/knowledgeApi.js` `generateProduct` to append `?document_id=XYZ`.

- **Data Flow & Interfaces**:
  ```
  [Studio Panel Slider] ──(debounced)──> PUT /settings (hybrid_weight)
  
  [Chat Turn Complete] ──> returns trace ──> StudioPanel maps chunk scores ──> Render Histogram SVG
  
  [Run Sanity Check] ──> Stores result in localStorage ──> StudioPanel & Evaluation charts read from cache
  
  [Knowledge Product Trigger] ──> POST /collections/{c_id}/generate/{type}?document_id={id} ──> Backend filters DB chunks
  ```

- **Key Decisions & Tradeoffs**:
  - *Decision 1*: Store Evaluation summary metrics in `localStorage` instead of building a new SQL database table. Tradeoff: Saves massive schema refactoring and limits state to the latest run only (which matches current UI requirements).
  - *Decision 2*: Slider debounce logic. Tradeoff: Preferring `onMouseUp` or `onChangeEnd` over continuous updating prevents API limits and file-locking collisions on the backend config JSON.
  - *Decision 3*: Histogram depends on the last chat query. Tradeoff: More accurate reflection of runtime relevance rather than collection-wide averages, making the metrics dynamic to user prompts.

- **Non-Functional Considerations**:
  - *Performance*: Updating Settings config file synchronously blocking could be slow; ensuring it is fully async.
  - *Reliability*: If no chat trace exists yet, the histogram should fall back gracefully to empty or zero-height states.

---

## Part 2: Delivery Strategy

### Execution Context
- **Delivery profile**: Moderate
- **Locked spec decisions**:
  - Settings page interactions must not conflict with Studio Panel `hybrid_weight`.
  - Document ID is isolated correctly via query parameters.

### First Delivery Slice
- **Smallest useful slice**: Wire the Alpha Slider to the `/settings` API and handle the locked state logic. 
- **Why this slice goes first**: Fastest to build, isolates the settings boundary risk identified during research.

### Execution Phases

#### Phase 1: Settings Sync & Alpha Slider Lockout
- **Goal**: Bind the UI slider to the backend RAG hybrid weight config.
- **Completion criteria**:
  - `StudioPanel.jsx` fetches and sets initial `hybrid_weight`.
  - Changing slider calls `updateSettings()`.
  - Slider is disabled if `retrieval_mode` != `"hybrid"`.

#### Phase 2: Dynamic Histogram Binning
- **Goal**: Render real-time relevance distributions.
- **Completion criteria**:
  - Read `trace.retrieved_chunks` from active chat turn context.
  - Calculate bin counts and heights.
  - Update SVG `<div height="...">` logic in `StudioPanel.jsx`.

#### Phase 3: Evaluation Summary Metrics Binding
- **Goal**: Hydrate quality cards with real LLM-as-a-judge scores.
- **Completion criteria**:
  - Sanity check runs store payload in `localStorage` or shared context.
  - Metric cards in `StudioPanel` and `Evaluation` pull the values safely.

#### Phase 4: Document Generation API Target Parameter
- **Goal**: Restrict knowledge summarization to a single focused document.
- **Completion criteria**:
  - Backend endpoints in `generate.py` support `document_id` query param.
  - Knowledge Service filters chunk vector queries by `document_id`.
  - Frontend `knowledgeApi.js` dispatches the query parameter safely.

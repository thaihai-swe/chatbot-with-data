# Feature Specification: 10.0 Studio Analytics Dashboard

## Metadata

- Feature name: Studio Analytics Dashboard Integration
- Feature slug: 10.0-studio-analytics-dashboard
- Delivery profile: Moderate
- Owner: Antigravity
- Status: Approved
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/10.0-studio-analytics-dashboard/analysis.md), [proposal.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/10.0-studio-analytics-dashboard/proposal.md)

## Problem Statement

The Studio Panel and Analytics Dashboard components in the frontend are heavily mocked. Currently, adjusting the "Hybrid Search Alpha" slider changes local React state but does not sync with the backend `retrieval.hybrid_weight` settings, rendering the UI control inert. Similarly, the "Vector Chunk Retrieval" histogram chart consists of static SVG columns, and quality metrics like Groundedness and Latency display hardcoded strings. Furthermore, the Knowledge Studio generation menu lets the user focus on a specific document, but fails to dispatch the `document_id` to the backend endpoint, resulting in full-collection generation.

## Desired Outcomes

- The Hybrid Search Alpha slider persists changes dynamically to the global backend configuration without spamming the network, and reacts intelligently to locked retrieval modes.
- The Vector Chunk Relevance histogram graphs real-time similarity distributions for the most recent chat query retrieval trace.
- The Studio Analytics quality metric cards display authentic test scores generated from the Evaluation validation suite.
- The Knowledge Studio can execute products bounded exclusively to a single focused document's chunks.

## Minimum Release Slice

- **What ships in the first useful release:**
  - `StudioPanel.jsx` component binding to `getSettings` and throttled `updateSettings` calls.
  - Disabled slider state when `retrieval_mode` != `hybrid`.
  - SVG histogram bars dynamically calculating array heights based on `retrieved_chunks` from the active chat turn's `retrieval_trace`.
  - Local caching (or React Context sharing) of evaluation sanity check metrics mapped to the metric cards.
  - Adding optional `document_id` path/query parameters to `/collections/{collection_id}/generate/{productType}` inside `generate.py` and wiring it to the chunk extraction pipeline.
- **What can wait:**
  - Persisting comprehensive evaluation history timelines into a SQL database.

## Success Criteria

- **SC-001**: Adjusting the Hybrid Alpha Slider successfully invokes a `PUT` request to the backend `/settings` API and updates `hybrid_weight`.
- **SC-002**: The Alpha Slider is visually disabled when the `retrieval_mode` setting is set to `semantic` or `keyword`.
- **SC-003**: The Vector Chunk Histogram computes and renders variable bar heights across 5 score distributions directly proportionate to the most recent chat query's similarity traces.
- **SC-004**: The Studio quality cards display the overall groundedness and relevancy values generated from an evaluation test run, replacing static mock text.
- **SC-005**: Triggering a Knowledge Product generation while a document is selected passes the `document_id` to the API, and the backend isolates chunk retrieval to only that document.

## Functional Requirements

### REQ-001: Hybrid Search Alpha State Sync
- **Requirement**: The `StudioPanel` must load `settings.retrieval.hybrid_weight` on mount and set it as the initial slider state. When the user slides the control, it must use a throttled/debounced API call (or trigger on mouse-up) to `updateSettings` to persist the change.
- **Why it matters**: Required to connect the UX to actual RAG retrieval logic.
- **Linked ACs**: `SC-001`
- **Priority**: Must Have
- **Verification Command**: `cat backend/config/settings.json` (Verify the file updates with the slider).

### REQ-002: Retrieval Mode UX Interaction Boundary
- **Requirement**: If the global `retrieval_mode` is `"semantic"` or `"keyword"`, the Studio Panel Alpha Slider must be disabled and visually indicate that Hybrid weighting is inactive.
- **Why it matters**: In `advanced_retrieval.py`, alpha is locked out if not in hybrid mode.
- **Linked ACs**: `SC-002`
- **Priority**: Must Have

### REQ-003: Dynamic Relevance Histogram
- **Requirement**: Replace the static `<div height="55%">` map in `StudioPanel.jsx` with a reducer that groups `retrieval_trace` chunk `similarity_score` floats into `[0.0-0.2]`, `[0.2-0.4]`, `[0.4-0.6]`, `[0.6-0.8]`, `[0.8-1.0]` bins, scaling bar heights dynamically based on bin frequency.
- **Why it matters**: Grants actual visibility into chunk density.
- **Linked ACs**: `SC-003`
- **Priority**: Must Have

### REQ-004: Live Evaluation Metrics Binding
- **Requirement**: Bind the Groundedness, Relevancy, Latency, and Recall value elements in `StudioPanel` and `Evaluation.jsx` to local context/storage state. Update this state cleanly when a new `sanity-check` evaluation run completes.
- **Why it matters**: Removes mock data strings and exposes active system health.
- **Linked ACs**: `SC-004`
- **Priority**: Must Have

### REQ-005: Document-Bounded Generation Routing
- **Requirement**: Update `backend/routers/generate.py` to optionally accept `document_id` via Query params for all generator endpoints (`/summary`, `/podcast`, `/faq`, `/timeline`). Update `frontend/src/api/knowledgeApi.js` to dispatch `documentId` if present.
- **Why it matters**: Allows targeted extraction workflows from a single document.
- **Linked ACs**: `SC-005`
- **Priority**: Must Have
- **Verification Command**: Unit test for bounded retrieval API payload.

## Acceptance Criteria Checklist
- [ ] `SC-001`: Alpha slider `onChangeComplete` invokes `updateSettings({ retrieval: { hybrid_weight: val }})`.
- [ ] `SC-002`: Alpha slider `<input disabled={...}>` correctly binds to `retrieval_mode !== 'hybrid'`.
- [ ] `SC-003`: SVG Histogram component iterates over dynamic trace chunk scores.
- [ ] `SC-004`: Sanity check results sync successfully across UI panes.
- [ ] `SC-005`: Knowledge Product API passes `document_id` and restricts Vector DB filtering correctly.

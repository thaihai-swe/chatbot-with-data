# Proposal: 10.0 Studio Analytics Dashboard

## The Problem
The current Studio Panel and Analytics Dashboard components inside the frontend are heavily mocked. The "Hybrid Search Alpha" slider is purely local component state and does not sync with backend global configuration `retrieval.hybrid_weight`, rendering it useless for actual RAG pipeline changes. Furthermore, the "Vector Chunk Retrieval" relevance score histogram chart is populated with static SVG geometries, and the evaluation metrics (Groundedness, Recall, etc.) are hardcoded text strings rather than actual test metrics. Lastly, when a user selects a specific document in the Knowledge Studio generation panel, the UI does not transmit the document ID to the backend, causing generation summaries to process the entire collection instead of the focused document.

## Objectives
1. **Dynamic Alpha Slider**: Bind the Hybrid Search Alpha slider to the global `/settings` API to instantly apply RAG weight changes, handling debounce to prevent network spam. Add UX protections to disable the slider if `retrieval_mode` is locked to Keyword or Semantic-only.
2. **Real-time Chunk Relevance Histogram**: Map the static SVG bar chart to use actual retrieval trace top scores from the latest chat query execution, distributed dynamically across five scalar bins.
3. **Evaluation Metrics Integration**: Bind the Evaluation dashboard validation history and the Studio panel quality cards to the results returned by the `/chat/evaluate/sanity-check` runs.
4. **Document-Level Generation**: Add a `document_id` query parameter boundary to backend generation API endpoints, and pass the selected `activeDocumentId` from the frontend to isolate generation contexts.

## High-Level Approach
- Update `StudioPanel.jsx` to fetch `getSettings` and use throttled `updateSettings` calls on the Alpha slider's change/release event.
- Extract `retrieval_trace` from the active chat context (via `WorkspaceContext` or `ChatScreen`) and group the `similarity_score` values from the `retrieved_chunks` array into histogram heights.
- Establish a localStorage cache or global context for the latest Evaluation Service results to display `overall_groundedness`, `overall_recall`, and average latency on the metric cards.
- Add `document_id: Optional[str] = None` to `/collections/{collection_id}/generate/{productType}` inside `backend/routers/generate.py`.

## In Scope
- Linking the StudioPanel slider to the existing `/settings` endpoints.
- Dynamically parsing trace relevance scores for the Studio SVG histogram.
- Binding validation metrics (e.g., groundedness, recall) from the most recent test to the analytics panel and evaluation screen metrics.
- Modifying the frontend `knowledgeApi.js` `generateProduct` wrapper to pass `documentId` up to the Python FastAPI router.

## Out Of Scope
- Creating new historical evaluation database schemas or migration files. We will only reflect the *latest* run via caching/local state.
- Adding complex authorization/permissions checks for who is allowed to change settings.

## Non-Goals
- Refactoring the entire `SettingsScreen.jsx` layout.
- Upgrading or changing the internal prompt logic of the evaluation agent itself.

## Success Criteria
- [ ] Changing the Alpha slider in the Studio tab updates `hybrid_weight` in `backend/config/settings.json`.
- [ ] If `retrieval_mode` is set to Keyword or Semantic Only, the Alpha slider is visibly disabled or warns the user.
- [ ] Vector chunk histogram bars accurately reflect the count of chunks inside score distributions derived from the active chat trace.
- [ ] Evaluation summary cards correctly update after triggering a Sanity Check run.
- [ ] Selecting a specific document in the Knowledge Studio restricts backend summarization extraction to that document's chunks.

---
Status: Aligned

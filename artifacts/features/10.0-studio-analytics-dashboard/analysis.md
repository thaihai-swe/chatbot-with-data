# Research Analysis: 10.0 Studio Analytics Dashboard

## Metadata
- Investigation name: Studio Analytics & Dashboard Integration
- Feature slug: 10.0-studio-analytics-dashboard
- Date: 2026-07-02
- Status: Research Complete

## Scope

- **What is being investigated:**
  - Connecting the Hybrid Search Alpha slider in the Studio Panel to the global settings API, ensuring that updating the slider updates `retrieval.hybrid_weight` in the backend database and updates retrieval behavior.
  - Replacing the static Vector Chunk Retrieval bar chart in the Studio panel with a dynamic histogram mapping actual query similarity scores aggregated from retrieval traces.
  - Syncing the evaluation summary cards on the Studio Analytics panel and the main Evaluation Dashboard to display actual groundedness, recall, latency, and correctness metrics pulled from sanity check runs.
  - Mapping the document selector dropdown filter inside the Knowledge Studio generation panel to document-level generation parameters on the backend, preventing collection-wide fallback if a single document is focused.
- **What is explicitly out of scope:**
  - Storing run history archives in the database (which would require database schema changes and migrations).
  - User authorization controls on settings adjustments.

## Current State

- **Observed current behavior:**
  - **Alpha Slider:** The slider operates strictly in local component memory using a local `useState(0.75)` call. It has no bindings to `getSettings` or `updateSettings` APIs, meaning changes do not affect the RAG search pipeline's hybrid weight weight.
  - **Vector Chunk Histogram:** Renders static SVG height bars that represent hardcoded counts (e.g. `4.5k`, `3.5k`). It remains static regardless of the current document or collection state.
  - **Evaluation Cards:** Summary metric stats are hardcoded text nodes (`98.2%`, `95.1%`, `450ms`, `96.5%`) on both the Studio sidebar and the main dashboard view.
  - **Document Generation Filter:** The document select dropdown changes the local `activeDocumentId` state but does not pass this variable during API invocations. The backend endpoints `/collections/{collection_id}/generate/{productType}` only accept collection IDs and generate summaries from all documents.
- **Relevant boundaries or components:**
  - **Backend:**
    - [settings.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/routers/settings.py) & [settings.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/schemas/settings.py): Global configurations including `retrieval.hybrid_weight`.
    - [generate.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/routers/generate.py): Post handlers for Knowledge product generation.
    - [advanced_retrieval.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/advanced_retrieval.py) & [retrieval.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/chat/retrieval.py): Retrieval execution and execution time tracing.
  - **Frontend:**
    - [StudioPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/StudioPanel.jsx): Hosts the analytics dashboard metrics, alpha selector slider, and product generation triggers.
    - [Evaluation.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/screens/Evaluation.jsx): Dashboard screen rendering benchmark history logs and run results.
    - [knowledgeApi.js](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/api/knowledgeApi.js): Client-side methods mapping to backend endpoints.

## Decision-Ready Summary

- **What matters most:** To move past frontend mock logic, we must bridge the state gap. The Studio Panel's Alpha slider should read its initial value from `/settings` and dispatch updates via throttled `updateSettings` requests. The Vector Chunk Retrieval chart should dynamically classify similarity scores from the active session's query retrieval trace (mapping scores into five frequency bins). The quality metric cards must be bound to actual results from the latest local storage cache of `/chat/evaluate/sanity-check`. Finally, document-level generation needs to be enabled by supporting an optional `document_id` query/body parameter in the backend product endpoints.
- **Strongest supported conclusion:** Settings updates can be bound immediately by utilizing the settings API client. Real-time histogram generation can be achieved by feeding the active chat message's `trace.retrieval.top_scores` array (from the pipeline trace) directly into the rendering method.
- **Single next proving step:** Transition to `/spec-requirements` to define requirements for alpha state binding, retrieval score classification, evaluation storage, and document-level generation APIs.

## Findings

- **Finding 1: Hybrid Search Alpha is component-local state.**
  - *Evidence:* In [StudioPanel.jsx:27](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/StudioPanel.jsx#L27), `alpha` is initialized as a simple `useState(0.75)` component hook and never synced with `/settings` endpoints.
  - *Type:* Fact.
- **Finding 2: Vector Chunk Retrieval bar chart is fully hardcoded.**
  - *Evidence:* In [StudioPanel.jsx:193-200](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/StudioPanel.jsx#L193-L200), the rendering function loops over a hardcoded array of bars containing static heights and relevance counts.
  - *Type:* Fact.
- **Finding 3: Studio Analytics quality metrics card are static mock text.**
  - *Evidence:* In [StudioPanel.jsx:238-283](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/StudioPanel.jsx#L238-L283), groundedness (`98.2%`), relevancy (`95.1%`), latency (`450ms`), and recall (`96.5%`) are rendered directly from hardcoded markup strings.
  - *Type:* Fact.
- **Finding 4: Document selector in Knowledge Studio generates products for the whole collection.**
  - *Evidence:* In [StudioPanel.jsx:35-43](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/StudioPanel.jsx#L35-L43) and [knowledgeApi.js:111-115](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/api/knowledgeApi.js#L111-L115), calls to `generateProduct` only pass `collectionId` and `productType`, ignoring the focused `activeDocumentId` select dropdown element.
  - *Type:* Fact.
- **Finding 5: Evaluation dashboard trends and recent runs table are hardcoded.**
  - *Evidence:* In [Evaluation.jsx:234-239](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/screens/Evaluation.jsx#L234-L239), the runs table parses static local arrays, and accuracy trends are modeled via hardcoded SVG path coordinates.
  - *Type:* Fact.

## Risks And Unknowns

- **Risk: Settings Concurrency and Overrides.**
  - *Why it matters:* If the Alpha slider triggers a PUT request to settings on every drag change event, it will spam the backend filesystem writer and slow down UI interaction.
  - *Next proving step:* Implement a debounce wrapper (e.g. 300ms) or update settings only on the slider's `onChangeEnd`/mouse-up event.
- **Risk: Document-level Summary context window limitations.**
  - *Why it matters:* If a user focuses generation on a very large document, the prompt must handle parsing it securely.
  - *Next proving step:* Ensure the backend retrieval queries restrict chunk fetching to the focused `document_id` if supplied.
- **Risk: Retrieval Mode Locks Alpha Effect.**
  - *Why it matters:* In `advanced_retrieval.py`, if `retrieval_mode` is set to `"keyword"` or `"semantic"`, the `effective_alpha` is locked to `0.0` or `1.0`, ignoring `hybrid_weight`. The Alpha slider on the Studio page will have no effect on RAG searches unless Retrieval Mode is set to `"hybrid"`.
  - *Next proving step:* The frontend StudioPanel should fetch the current `retrieval_mode` from settings and disable/warn the user if it is not in `"hybrid"` mode.

## Recommendation

- **Next skill or artifact:** `/spec-requirements`
- **Why:** The requirements for settings synchronization, trace score grouping, evaluation data caching, and document generation arguments must be established before planning.
- **Exact next prompt or action:** Proceed to `/spec-requirements` to draft specifications.

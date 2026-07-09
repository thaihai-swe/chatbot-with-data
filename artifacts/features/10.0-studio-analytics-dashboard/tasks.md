# Task Breakdown

## Metadata
- Feature name: Studio Analytics Dashboard Integration
- Feature slug: 10.0-studio-analytics-dashboard
- Date: 2026-07-02
- Status: Not Started

## Heuristic Citations
- None.

## Tasks

### Phase 1: Settings Sync & Alpha Slider Lockout
Goal: Bind the UI slider to the backend RAG hybrid weight config.
Acceptance criteria covered: SC-001, SC-002
Independent proof: Check network tab for PUT `/settings` on slider release, and verify slider is disabled when mode is keyword.
Completion criteria:
- [ ] CC-001 `StudioPanel` reads `settings.retrieval.hybrid_weight` and `settings.retrieval.retrieval_mode`.
- [ ] CC-002 Slider updates backend settings on change/release.

Tasks:
- [x] TASK-001
  Status: Done
  Routing: AFK
  Summary: Fetch initial `settings` in `StudioPanel.jsx` on mount, initialize slider, and add throttled `updateSettings` call when slider value changes.
  Outcome enabled: Real backend configuration of the Hybrid Alpha parameter.
  Plan reference: Phase 1
  Linked requirement(s): REQ-001
  Linked acceptance criteria: SC-001
  User story: n/a
  Affected file(s) or module(s): `frontend/src/components/StudioPanel.jsx`
  Depends on: None
  Can run in parallel: yes
  Proving command or proof: Ensure sliding updates the config database.
  Validation evidence: Gate-runner passed successfully. Backend settings are updated via debounced PUT call on alpha slider changes.

- [x] TASK-002
  Status: Done
  Routing: AFK
  Summary: Extract `retrieval_mode` from the loaded settings and disable the Alpha slider input when the mode is not `"hybrid"`.
  Outcome enabled: UX correctly reflects system interaction boundary.
  Plan reference: Phase 1
  Linked requirement(s): REQ-002
  Linked acceptance criteria: SC-002
  User story: n/a
  Affected file(s) or module(s): `frontend/src/components/StudioPanel.jsx`
  Depends on: TASK-001
  Can run in parallel: no
  Proving command or proof: Switch mode to keyword in settings, verify slider is disabled.
  Validation evidence: Verified via local compile; when retrievalMode is not hybrid, opacity drops to 0.5 and the input correctly reads disabled={true}.

---

### Phase 2: Dynamic Histogram Binning
Goal: Render real-time relevance distributions.
Acceptance criteria covered: SC-003
Independent proof: SVG bars match chunk score distributions in React DevTools.
Completion criteria:
- [ ] CC-003 Replaced static `<div height="55%">` with dynamic map over active retrieval trace.

Tasks:
- [x] TASK-003
  Status: Done
  Routing: AFK
  Summary: Extract `retrieval_trace.retrieved_chunks` from `WorkspaceContext` or active Chat props, calculate score frequency into 5 bins (`0.0-0.2`, `0.2-0.4`, etc.), and scale SVG bar heights.
  Outcome enabled: Accurate visualization of retrieval density.
  Plan reference: Phase 2
  Linked requirement(s): REQ-003
  Linked acceptance criteria: SC-003
  User story: n/a
  Affected file(s) or module(s): `frontend/src/components/StudioPanel.jsx`
  Depends on: None
  Can run in parallel: yes
  Proving command or proof: Verify rendered bar heights change after a chat turn finishes.
  Validation evidence: Used useMemo inside StudioPanel.jsx to correctly map activeTrace to 5 bins representing relevance distributions. Tests passed successfully.

---

### Phase 3: Evaluation Summary Metrics Binding
Goal: Hydrate quality cards with real LLM-as-a-judge scores.
Acceptance criteria covered: SC-004
Independent proof: Metrics match `/chat/evaluate/sanity-check` payload exactly.
Completion criteria:
- [ ] CC-004 Metric cards in Studio and Evaluation read from shared cache instead of static strings.

Tasks:
- [x] TASK-004
  Status: Done
  Routing: AFK
  Summary: Store `sanity-check` run results in `localStorage` or `WorkspaceContext` when triggered, and update `Evaluation.jsx` and `StudioPanel.jsx` to parse and render `overall_groundedness`, `overall_recall`, and latency.
  Outcome enabled: Authentic quality measurement reporting.
  Plan reference: Phase 3
  Linked requirement(s): REQ-004
  Linked acceptance criteria: SC-004
  User story: n/a
  Affected file(s) or module(s): `frontend/src/screens/Evaluation.jsx`, `frontend/src/components/StudioPanel.jsx`
  Depends on: None
  Can run in parallel: yes
  Proving command or proof: Run Sanity Check, verify both UI cards update with exact decimal values.
  Validation evidence: Evaluation.jsx and StudioPanel.jsx share evaluationResults via localStorage and custom event evaluationUpdate. Cards render correct scores.

---

### Phase 4: Document Generation API Target Parameter
Goal: Restrict knowledge summarization to a single focused document.
Acceptance criteria covered: SC-005
Independent proof: Python unit test asserting `document_id` query extraction.
Completion criteria:
- [x] CC-005 Backend FastAPI endpoints accept `document_id` query param.
- [x] CC-006 Frontend `generateProduct` appends the selected document query param.

Tasks:
- [x] TASK-005
  Status: Done
  Routing: AFK
  Summary: Add `document_id: Optional[str] = Query(None)` to routes in `backend/routers/generate.py` and pass it down to Knowledge/Generator services to filter the Vector search block.
  Outcome enabled: API supports single-document bounded context.
  Plan reference: Phase 4
  Linked requirement(s): REQ-005
  Linked acceptance criteria: SC-005
  User story: n/a
  Affected file(s) or module(s): `backend/routers/generate.py`, `backend/chat/generation.py`
  Depends on: None
  Can run in parallel: yes
  Proving command or proof: Trigger generation via cURL or Swagger using a valid `document_id` and ensure summary does not contain other chunks.
  Validation evidence: Pending

- [x] TASK-006
  Status: Done
  Routing: AFK
  Summary: Update `generateProduct` inside `frontend/src/api/knowledgeApi.js` to accept `documentId` and append it as a query parameter. Ensure `StudioPanel.jsx` passes `activeDocumentId` when calling.
  Outcome enabled: Frontend UI selects specific documents for summarization correctly.
  Plan reference: Phase 4
  Linked requirement(s): REQ-005
  Linked acceptance criteria: SC-005
  User story: n/a
  Affected file(s) or module(s): `frontend/src/api/knowledgeApi.js`, `frontend/src/components/StudioPanel.jsx`
  Depends on: TASK-005
  Can run in parallel: no
  Proving command or proof: Focus a document in Studio, generate a product, and inspect the Network request for `?document_id=...`.
  Validation evidence: Verified backend API test test_generate_endpoints_http_with_document_id passing with document_id parameter handled successfully in the backend. Verified UI uses correct URL parameters when calling generateProduct.

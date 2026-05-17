# Tasks: Evaluation and Observability

## Phase 1: Infrastructure & Backend Foundations

- [ ] **Task T-001: Create Evaluation Dataset**
  - **Target:** `backend/test_data/eval_dataset.json`
  - **Description:** Create a sample dataset with 10-20 "golden" questions and expected document IDs.
  - **Proof:** `cat backend/test_data/eval_dataset.json` shows valid JSON.

- [ ] **Task T-002: Define Evaluation Schemas**
  - **Target:** `backend/schemas/chat.py`
  - **Description:** Add `EvalResult` and `SanityCheckResponse` schemas.
  - **Proof:** Schemas are importable and pass Pydantic validation.

- [ ] **Task T-003: LLM-based Groundedness Scorer**
  - **Target:** `backend/chat/grounding.py`
  - **Description:** Implement `check_groundedness(answer, chunks)` using LLM as a judge.
  - **Proof:** Run a small script to verify the scorer returns 0-1 for a known grounded/ungrounded pair.

## Phase 2: Evaluation Service & API

- [ ] **Task T-004: Implement Evaluation Service**
  - **Target:** `backend/chat/evaluation.py`
  - **Description:** Create `EvaluationService` to run the sanity check loop. Parallelize LLM calls for speed.
  - **Proof:** Unit test calling `run_sanity_check()` with a mock LLM.

- [ ] **Task T-005: Add Sanity Check Endpoint**
  - **Target:** `backend/routers/chat.py`
  - **Description:** Add `POST /evaluate/sanity-check` to trigger the evaluation.
  - **Proof:** `curl -X POST .../evaluate/sanity-check` returns results.

## Phase 3: Frontend Deep Observability (X-Ray)

- [ ] **Task T-006: Add Debug Toggle to Chat UI**
  - **Target:** `frontend/src/screens/ChatScreen.jsx`
  - **Description:** Add a "Debug Mode" toggle in the header or sidebar. Use local state to manage.
  - **Proof:** Toggle state is visible and changes on click.

- [ ] **Task T-007: Implement X-Ray Panel**
  - **Target:** `frontend/src/components/XRayPanel.jsx` (New)
  - **Description:** Create a component to render `retrieval_trace` and `safety_trace` metadata.
  - **Proof:** Debug mode ON shows the panel for messages that have trace data.

## Phase 4: Frontend Evaluation UI

- [ ] **Task T-008: Create Evaluation Screen**
  - **Target:** `frontend/src/screens/EvaluationScreen.jsx`
  - **Description:** New screen with a "Run Sanity Check" button and a results table.
  - **Proof:** Navigating to `/evaluation` shows the button and table.

- [ ] **Task T-009: Connect Evaluation UI to Backend**
  - **Target:** `frontend/src/api/chat.js`
  - **Description:** Add `runSanityCheck` API call. Update UI to handle loading and display results.
  - **Proof:** Clicking the button triggers the run and populates the table with real scores.

# Plan: Evaluation and Observability

## 1. Execution Order

### Phase 1: Judge Service & Evaluation Schemas
- Define Pydantic schemas for `EvaluationCase`, `EvaluationDataset`, `EvaluationResult`, and `EvaluationRun`.
- Implement `JudgeService` with prompts for Groundedness and Relevance (LLM-as-a-judge).
- **Verification:** Unit tests for `JudgeService` using mocked LLM responses.

### Phase 2: Evaluation Runner & Storage
- Implement `EvaluationService` to run batch jobs.
- Setup filesystem storage in `backend/data/eval/`.
- Add background task support for running evaluations.
- **Verification:** CLI script to trigger a small evaluation run and verify the JSON output.

### Phase 3: Evaluation API
- Implement FastAPI routes for listing/updating datasets and runs.
- Add endpoint to trigger a new evaluation run with a specific configuration.
- **Verification:** REST API tests using `httpx`.

### Phase 4: Frontend Dataset & Run Management
- Create `EvaluationDashboard` screen in React.
- Implement JSON editor for datasets.
- Implement table view for past runs with summary metrics.
- **Verification:** Manual UI test - create a dataset, run it, and see it in the list.

### Phase 5: Detailed Analysis & Comparison UI
- Build the "Run Detail" view showing per-case results and judge reasoning.
- Implement the "Comparison" view for side-by-side metric visualization.
- **Verification:** Manual UI test - compare two runs with different retrieval configs.

### Phase 6: Live Chat Evaluation
- Add "Live Evaluation" toggle to Chat settings.
- Update `ChatService` to optionally call `JudgeService` for real-time feedback.
- Display judge scores and reasoning in the Chat UI (or Trace panel).
- **Verification:** Chat with "Live Evaluation" enabled and see the judge results.

## 2. Impacted Boundaries
- `backend/chat/service.py`: Add optional evaluation logic.
- `backend/chat/prompts.py`: Add judge prompts.
- `backend/schemas/chat.py`: Add evaluation schemas.
- `frontend/src/screens/`: Add `EvaluationDashboard.jsx`.
- `frontend/src/api/`: Add `eval.js`.

## 3. Proving Strategy
- **Unit Tests:** For `JudgeService` and `EvaluationService`.
- **Integration Tests:** For the Evaluation API.
- **Manual Verification:** UI walk-through for dataset management and experiment comparison.
- **Baseline Run:** Establish a "baseline" evaluation run to verify system stability.

## 4. Rollback Posture
- Evaluation logic is additive; if it fails, it doesn't break core chat (unless "Live Evaluation" is on).
- `JSON-per-run` storage is easy to clean up; just delete the folder.
- Frontend changes are isolated to a new screen.

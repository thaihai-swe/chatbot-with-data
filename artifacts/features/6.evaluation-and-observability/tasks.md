# Tasks: Evaluation and Observability

## Phase 1: Judge Service & Evaluation Schemas

- [x] **TASK-100:** Define Pydantic schemas for `EvaluationCase`, `EvaluationDataset`, `EvaluationResult`, and `EvaluationRun` in `backend/schemas/evaluation.py`.
    - **Target:** `backend/schemas/evaluation.py`
    - **Proof:** Schema validation tests passed in `tests/schemas/test_evaluation_schemas.py`.
    - **Note:** Schemas exported in `backend/schemas/__init__.py`.
- [x] **TASK-101:** Add LLM-as-a-judge prompts (Groundedness, Relevance) to `backend/chat/prompts.py`.
    - **Target:** `backend/chat/prompts.py`
    - **Proof:** `JUDGE_GROUNDEDNESS_PROMPT` and `JUDGE_RELEVANCE_PROMPT` added.
- [x] **TASK-102:** Implement `JudgeService` in `backend/chat/judge.py`.
    - **Target:** `backend/chat/judge.py`
    - **Proof:** Unit tests passed in `tests/chat/test_judge_service.py` with mocked LLM.

## Phase 2: Evaluation Runner & Storage

- [x] **TASK-200:** Create base directories `backend/data/eval/datasets` and `backend/data/eval/runs`.
    - **Target:** Filesystem
    - **Proof:** `backend/data/eval/datasets` and `backend/data/eval/runs` created.
- [x] **TASK-201:** Implement `EvaluationService` in `backend/chat/evaluation.py`.
    - **Target:** `backend/chat/evaluation.py`
    - **Proof:** CLI script `scripts/run_single_eval.py` successfully executed a mock evaluation and produced a valid JSON summary.
- [x] **TASK-202:** Add background task orchestration in `EvaluationService`.
    - **Target:** `backend/chat/evaluation.py`
    - **Proof:** `execute_run` method implemented with state tracking and logging, ready for FastAPI `BackgroundTasks`.

## Phase 3: Evaluation API

- [x] **TASK-300:** Implement `backend/routers/evaluation.py` with GET/POST for datasets and runs.
    - **Target:** `backend/routers/evaluation.py`
    - **Proof:** API router implemented with CRUD for datasets/runs and background task support for execution.
- [x] **TASK-301:** Register the evaluation router in `backend/app.py`.
    - **Target:** `backend/app.py`
    - **Proof:** API tests passed in `tests/test_api_eval.py` verifying `/eval/datasets` and `/eval/runs` endpoints.

## Phase 4: Frontend Dataset & Run Management

- [x] **TASK-400:** Create `frontend/src/api/eval.js` for backend communication.
    - **Target:** `frontend/src/api/eval.js`
    - **Proof:** API client implemented with functions for datasets and runs.
- [x] **TASK-401:** Implement `EvaluationDashboard.jsx` with basic tab navigation (Datasets, Runs).
    - **Target:** `frontend/src/screens/EvaluationDashboard.jsx`
    - **Proof:** `EvaluationDashboard` screen implemented and integrated into `App.jsx` with routing and tab navigation.
- [x] **TASK-402:** Implement Dataset editor (JSON textarea) and "Run Evaluation" trigger.
    - **Target:** `frontend/src/screens/EvaluationDashboard.jsx`
    - **Proof:** Dataset editor and Run configuration modal implemented in `EvaluationDashboard.jsx`.

## Phase 5: Detailed Analysis & Comparison UI

- [x] **TASK-500:** Build `RunDetail.jsx` component to show per-case results and judge logic.
    - **Target:** `frontend/src/components/RunDetail.jsx`
    - **Proof:** `RunDetail` component implemented with metric cards, score badges, and per-case reasoning breakdown. Integrated into `EvaluationDashboard`.
- [x] **TASK-501:** Build `ExperimentComparison.jsx` for side-by-side run metrics.
    - **Target:** `frontend/src/components/ExperimentComparison.jsx`
    - **Proof:** `ExperimentComparison` component implemented with side-by-side metric comparison and delta calculation (including percentage). Integrated into `EvaluationDashboard`.

## Phase 6: Live Chat Evaluation

- [x] **TASK-600:** Add `enable_live_evaluation` to `AdvancedRetrievalConfig` schema.
    - **Target:** `backend/schemas/chat.py`
    - **Proof:** `enable_live_evaluation` added to `AdvancedRetrievalConfig` and `evaluation_metrics` added to `ChatTurnResponse`.
- [x] **TASK-601:** Update `ChatService.process_turn` to call `JudgeService` if enabled.
    - **Target:** `backend/chat/service.py`
    - **Proof:** `ChatService` now takes `JudgeService` dependency and optionally populates `evaluation_metrics` in the response.
- [x] **TASK-602:** Update Chat UI to show live judge scores and reasoning.
    - **Target:** `frontend/src/screens/Chat.jsx`
    - **Proof:** "Live Evaluation" toggle added to chat settings. Chat bubbles now display Groundedness and Relevance scores when enabled.

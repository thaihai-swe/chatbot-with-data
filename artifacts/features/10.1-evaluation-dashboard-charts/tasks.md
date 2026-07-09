# Implementation Tasks: 10.1 Evaluation Dashboard Charts

## Setup Phase
N/A

## Foundational Phase
- [x] TASK-001
  Status: Done
  Summary: Add `evaluation_runs` table to `backend/migrations/runner.py` and create `backend/repositories/evaluation_repository.py` with `save_run` and `list_recent_runs` methods.
  Outcome enabled: Database schema exists and logic is ready for persisting evaluation results.
  Covers: AC-001
  Can run in parallel: yes
  Proving command: `sqlite3 backend/data.db "SELECT * FROM evaluation_runs;"` (should succeed with 0 rows)

## Story P1: Backend Logic & API
- [x] TASK-002
  Status: Done
  Summary: Update `backend/chat/evaluation.py` (`run_sanity_check`) to instantiate `EvaluationRepository` and save the final benchmark metrics into the database before returning the response.
  Outcome enabled: Executing the sanity check creates a permanent log in the DB.
  Covers: AC-001
  Depends on: TASK-001
  Can run in parallel: no
  Proving command: `curl -X POST http://localhost:8000/chat/evaluate/sanity-check` followed by `sqlite3 backend/data.db "SELECT count(*) FROM evaluation_runs;"` (count should be 1).

- [x] TASK-003
  Status: Done
  Summary: Define the response schema `EvaluationRunResponse` in `backend/schemas/chat.py`. Add the endpoint `GET /evaluate/history` inside `backend/routers/chat.py` (or wherever the `evaluate` route resides) that calls `list_recent_runs()`.
  Outcome enabled: Frontend can pull historical data.
  Covers: AC-002
  Depends on: TASK-001
  Can run in parallel: yes
  Proving command: `curl -s http://localhost:8000/chat/evaluate/history`

## Story P2: Frontend Integration
- [x] TASK-004
  Status: Done
  Summary: Add `recharts` to `frontend/package.json` (`npm install recharts`). Export `getEvaluationHistory` in the appropriate API client file (e.g. `frontend/src/api/chatApi.js`).
  Outcome enabled: Dependencies installed and API fetcher ready.
  Covers: AC-003
  Depends on: TASK-003
  Can run in parallel: no
  Proving command: `cat frontend/package.json | grep recharts`

- [x] TASK-005
  Status: Done
  Summary: Update `frontend/src/screens/Evaluation.jsx`. Use `useEffect` to call `getEvaluationHistory()`. Replace the static SVG with an `<AreaChart>` from `recharts`. Replace the static mock runs array with the dynamic fetched state.
  Outcome enabled: Fully dynamic Evaluation Dashboard.
  Covers: AC-003, AC-004
  Depends on: TASK-004
  Can run in parallel: no
  Proving command: Start frontend, verify Recharts elements render and match the latest backend payload visually. `cd frontend && npm test -- --passWithNoTests`

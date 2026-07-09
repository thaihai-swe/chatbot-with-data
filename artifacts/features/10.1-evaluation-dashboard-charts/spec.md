# Specification: 10.1 Evaluation Dashboard Charts

## What
This feature brings the Evaluation Dashboard to life by connecting it to a backend historical database. 
- It introduces an `evaluation_runs` database table that persists the results of every Sanity Check execution.
- It provides a historical API endpoint (`GET /chat/evaluate/history`) to retrieve the last 10 runs.
- It replaces the static SVG line chart in the React frontend with a dynamic `recharts` component that plots the real Relevancy and Groundedness metrics over time.
- It replaces the mocked "Recent Evaluation Runs" array with actual historical entries fetched from the backend.

## Why
Users currently rely on a static, hardcoded dashboard representation that does not accurately reflect the system's performance over time. While the Evaluation tab can trigger a live Sanity Check, the inability to track changes in accuracy, hallucination rates, or latency across multiple tuning sessions severely limits the dashboard's usefulness. By persisting these runs and visualizing them dynamically, users can concretely prove whether their adjustments to prompts, retrieval parameters, or models are causing regressions or improvements.

## Acceptance Criteria

- [ ] **AC-001**: A database migration creates the `evaluation_runs` table, and `EvaluationService.run_sanity_check()` inserts a new record into it upon completion.
  - *Proving Command*: `sqlite3 backend/data.db "SELECT count(*) FROM evaluation_runs;"`
- [ ] **AC-002**: A new `GET /chat/evaluate/history` endpoint exists and returns an array of the latest evaluation runs sorted by newest first, limited to 10 entries.
  - *Proving Command*: `curl -s http://localhost:8000/chat/evaluate/history | grep -q "overall_groundedness"`
- [ ] **AC-003**: The frontend `package.json` includes `recharts`, and `Evaluation.jsx` renders a dynamic line chart spreading available data points across the x-axis, using data fetched from the history endpoint.
  - *Proving Command*: `cd frontend && npm test -- --passWithNoTests` (and manual UI inspection).
- [ ] **AC-004**: The "Recent Evaluation Runs" table on the frontend dynamically iterates over the fetched history array, displaying the correct `id`, `created_at`, `dataset`, and `overall_recall` score for each row instead of mock data.
  - *Proving Command*: Manual UI inspection verifying dynamic data matches API response.

## Non-Functional Requirements
- **Performance**: The frontend must gracefully handle missing or empty evaluation history arrays without crashing (e.g., displaying an empty state or just flat lines).
  - Linked ACs: AC-003, AC-004

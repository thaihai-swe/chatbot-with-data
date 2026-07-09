# Plan: 10.1 Evaluation Dashboard Charts

## Part 1: Technical Design

### Component Modifications
1. **Database Schema (`backend/migrations/runner.py`)**: 
   - Add a `CREATE TABLE IF NOT EXISTS evaluation_runs` statement.
   - Columns: `id` (TEXT, PK), `dataset_name` (TEXT), `model_name` (TEXT), `total_cases` (INTEGER), `passed_cases` (INTEGER), `overall_recall` (REAL), `overall_groundedness` (REAL), `created_at` (TIMESTAMP).
2. **Backend Repository (`backend/repositories/evaluation_repository.py`)**:
   - Create `EvaluationRepository` inheriting from `BaseRepository`.
   - Add `save_run(...)` to insert a new run.
   - Add `list_recent_runs(limit=10)` to fetch runs ordered by `created_at` DESC.
3. **Evaluation Service (`backend/chat/evaluation.py`)**:
   - In `run_sanity_check`, after results are compiled, call `EvaluationRepository.save_run(...)`.
4. **Backend Routes (`backend/routers/chat.py` or `evaluate.py`)**:
   - The evaluation route is in `chat.py`. Add `GET /evaluate/history` returning `List[EvaluationRunResponse]`.
5. **Frontend API (`frontend/src/api/evaluationApi.js` or `chatApi.js`)**:
   - Check where the `sanity-check` API call is made. Add the new `getEvaluationHistory()` API wrapper.
6. **Frontend UI (`frontend/src/screens/Evaluation.jsx`)**:
   - Install `recharts`.
   - Use `useEffect` to fetch history via `getEvaluationHistory()`.
   - Replace the SVG with `Recharts` `<ResponsiveContainer>` containing an `<AreaChart>` mapping `overall_recall` (Relevancy) and `overall_groundedness`. Recharts handles dynamic scaling and points.
   - Replace the static mock runs array with a mapping of the fetched history data to populate the "Recent Evaluation Runs" table.

### Design Trade-offs
- **Custom SVG vs Chart Library**: We choose `recharts` because calculating responsive SVG bezier curves natively with variable data sizes is brittle. Adding the `recharts` dependency is lightweight enough and standard for React dashboards.

---

## Part 2: Delivery Strategy

### User Story Decomposition
- **Story P1: Foundation & Backend**: Database migration, repository logic, and the HTTP endpoint to fetch the history.
- **Story P2: Frontend UI & Charts**: Installation of `recharts`, fetching data from the API, and updating the Visuals (Line chart and Logs table).

### Implementation Strategy
**Incremental**: We will build the backend persistence first, prove it works via tests or API calls, and then integrate the frontend. This avoids mocking the frontend endpoints.

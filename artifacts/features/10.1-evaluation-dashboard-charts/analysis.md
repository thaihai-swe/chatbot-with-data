# Brownfield Analysis: 10.1 Evaluation Dashboard Charts

## 1. Goal
Investigate the current implementation of the Evaluation dashboard charts and the "Recent Runs" history. Identify the gaps between the current hardcoded frontend state and what is required to make the validation trend chart and recent runs log dynamic and backed by a historical database.

## 2. Current State Mapping

### Frontend State
**File**: `frontend/src/screens/Evaluation.jsx`
- **Validation Trend Chart**: Uses an inline SVG element (`<svg viewBox="0 0 400 180">`) with hardcoded `<path>` data drawing the trend lines for Relevancy and Groundedness. The x-axis labels ("Run 1", "Run 4", etc.) are statically rendered text nodes.
- **Recent Runs Log**: Uses a static array of mock data mapped inside the JSX:
  ```javascript
  [
    { id: "#EV-2026-894", time: "Today, 10:14 AM", dataset: "Q3_Financials_Set", model: "Hyperion Pro v4.2", score: "96.2%" },
    // ...
  ]
  ```

### Backend State
**Evaluation Logic**: `backend/chat/evaluation.py` and `backend/routers/chat.py`
- The API route `POST /chat/evaluate/sanity-check` calls `EvaluationService.run_sanity_check()`.
- `run_sanity_check` loads the `eval_dataset.json` dataset, runs the queries against the LLM provider, calculates metrics (recall, groundedness, accuracy), and returns a `SanityCheckResponse`.
- **Finding**: It does not save the results or history to any database. The data is entirely ephemeral and lost after the response completes.

**Database Schema**: `backend/migrations/runner.py`
- There are no tables for `evaluation_runs`, `evaluation_history`, or similar concepts.
- The existing tables only cover standard Chat operations (`chat_sessions`, `chat_turns`, `citations`, `documents`, etc.).

## 3. Risks & Constraints
- **SVG Complexity**: The current SVG chart contains complex hardcoded paths (`d="M 30 110 Q 70 90..."`) to represent smooth quadratic/bezier curves for the mock data. Making this dynamic using pure SVG paths mathematically will require calculating bezier control points for the data arrays, or adopting a lightweight charting library (e.g. Recharts or Chart.js) if manual SVG manipulation proves too brittle. Given the prompt's preference for vanilla implementations without heavy dependencies, manual SVG coordinate calculation is likely required but carries the risk of visual layout overflow if scores are extreme.
- **Backend Schema Changes Required**: A new migration must be written to introduce an `evaluation_runs` table. It needs to store:
  - Timestamp
  - Dataset Name
  - Overall Metrics (Recall, Groundedness, Passed Cases out of Total)
  - LLM Model used
- **Endpoint Additions**: New FastAPI endpoints are needed:
  - `GET /chat/evaluate/history` to return the historical list of runs.

## 4. Proposed Seams & Handoff
To make this feature operational, the following implementations are recommended for the subsequent `/spec-plan` phase:
1. **Database Update**: Create a new table `evaluation_runs` via an updated migration script.
2. **Backend Persistence**: Modify `EvaluationService.run_sanity_check()` to insert the calculated metrics into the database before returning the payload.
3. **Historical Data API**: Add an endpoint to fetch the list of historical runs (e.g., limit 10).
4. **Frontend Integration**: Update `Evaluation.jsx` to fetch the recent runs. Replace the hardcoded mock array with state mapped from the API.
5. **Dynamic SVG Calculation**: Implement a helper function in the frontend that takes the array of historical scores and linearly maps them to `(x, y)` coordinate paths for the Relevancy and Groundedness SVG lines, keeping the bounds within the `viewBox="0 0 400 180"`.

## Handoff Next Step
Requirements are sufficiently clear. Handoff to `/spec-requirements` to document user acceptance criteria.

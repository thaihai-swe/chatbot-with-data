# Proposal: 10.1 Evaluation Dashboard Charts

## Overview
Currently, the Evaluation dashboard in `StudioPanel.jsx` contains a hardcoded SVG line chart representing "Validation history" and a hardcoded list of "Recent Evaluation Runs". The backend runs the evaluation suite on the fly but does not persist the results. This proposal defines the scope for making both the Validation Trend chart and the Recent Runs log fully dynamic and backed by a historical database.

## In Scope
- Creating a new database table `evaluation_runs` to store the historical results of Sanity Checks.
- Updating the backend `run_sanity_check` to persist the evaluated metrics (Groundedness, Relevancy, Latency, Recall) before returning them to the client.
- Creating a new endpoint `GET /chat/evaluate/history` to retrieve the historical evaluation runs (limited to the last 10).
- Replacing the hardcoded frontend SVG chart with a dynamic chart built using `recharts` (a lightweight React charting library). The chart will dynamically spread available runs across its width if fewer than 10 exist.
- Replacing the mock "Recent Evaluation Runs" array with live data fetched from the backend history endpoint.

## Out Of Scope
- Allowing users to delete individual historical evaluation runs from the UI.
- Running historical benchmarks against multiple distinct datasets concurrently (currently assumes a single global "Sanity Check").
- Real-time websockets updates for the evaluation history (standard HTTP polling/refresh is sufficient).

## Non-Goals
- Replicating the precise exact pixel shape of the hardcoded SVG chart. `recharts` will be styled to match the aesthetic as closely as possible (gradients and colors), but it will use standard bezier interpolation.

# Proposal: 10.3 Ablation Evaluation Framework

## Problem
The README documents expected ablation results (e.g., BM25-only → Full Pipeline improves context precision from 52% to 87%), but the system can only evaluate against whatever pipeline configuration is currently active. There is no way to run the golden test suite against multiple configs, compare results side-by-side, or prove which pipeline stages actually contribute measurable gains.

## Solution
Add an ablation mode to the evaluation service that accepts a list of pre-defined config variants, runs the full test dataset against each sequentially, and returns a comparison response. The frontend Evaluation Dashboard adds an ablation comparison table showing per-variant metrics with delta highlighting.

## In Scope
- 3-4 pre-defined config variants (Baseline BM25-only, +Semantic Search, +Full Pipeline with reranking/expansion/intelligence, Full Pipeline minus reranking)
- Backend: `POST /evaluate/ablation` endpoint accepting variant list, running each, returning comparison
- Backend: Schema migration adding `config_variant_name` and `config_snapshot_json` to `evaluation_runs`
- Backend: Reuse `SettingsManager.save_run_snapshot()` to persist variant config per evaluation run
- Backend: Config variant definitions as a JSON file (`config/ablation-variants.json`)
- Data: Create `eval_dataset.json` with ~20 golden test cases (reverse-engineered from `_evaluate_case()`)
- Frontend: Ablation comparison table component showing metric deltas between variants
- Tests: Unit tests for `EvaluationService` with mocked `ChatService`; integration test for ablation endpoint

## Out of Scope
- Running ablation across multiple datasets (single dataset only)
- User-defined custom variants from the frontend (variants defined in config file only)
- SSE streaming progress for multi-variant runs (simple polling/sync response)
- Historical ablation comparison (only shows current run, not historic cross-run comparisons)
- Pipeline component changes (no new retrieval strategies, no new rerankers)

## Success
Users can run the ablation suite from the Evaluation Dashboard and see a comparison table showing which pipeline configuration produces the best metrics, replacing the purely aspirational ablation table in the README with real measurements.

## Complexity
Moderate (backend schema + API + frontend table + golden dataset creation)

## Next
`/spec-plan` after Spec Approved.

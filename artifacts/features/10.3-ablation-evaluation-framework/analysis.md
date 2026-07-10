# Analysis: 10.3 Ablation Evaluation Framework

## Metadata
- Investigation name: Ablation Evaluation Framework — brownfield mapping and feasibility
- Feature slug: `10.3-ablation-evaluation-framework`
- Date: 2026-07-09
- Status: Research Complete

## Scope

- **What is being investigated:** The existing evaluation pipeline, pipeline configuration system, persistence layer, and frontend visualization to determine the surface area for an A/B evaluation framework that runs golden datasets against multiple pipeline configurations and compares results.
- **What is explicitly out of scope:** Designing new pipeline components, changing the pipeline execution model, implementing constrained decoding, or building a new UI framework.

## Decision-Ready Summary

- **What matters most:** The pipeline config (`RetrievalSettings` in `backend/schemas/settings.py`) already has ~20 boolean toggles for individual stages. The evaluation service (`backend/chat/evaluation.py`) runs queries against the *current* live config. There is no mechanism to parameterize config per evaluation run, no dataset file exists, and no comparison/delta logic exists on frontend or backend.
- **Strongest supported conclusion:** Safe to proceed. The brownfield surface is well-bounded: extend the evaluation repository schema, add a config-override seam to `EvaluationService`, and add one API endpoint + UI component for multi-run comparison. No pipeline internals need changing.
- **Single next proving step:** Draft `spec.md` defining the config variant format, API contract, and UI changes.

---

## Findings

### F-001: Pipeline Configuration Surface

**Evidence:**
- `backend/schemas/settings.py:40-61` — `RetrievalSettings` has 21 fields:
  - Mode toggles: `retrieval_mode` (semantic|keyword|hybrid), `hybrid_weight`
  - Intelligence toggles: `intelligence_enabled`, `query_expansion_enabled`, `query_decomposition_enabled`, `hyde_enabled`, `synonym_expansion_enabled`, `dynamic_routing_enabled`
  - Retrieval toggles: `reranker_enabled`, `parent_child_enabled`, `multi_hop_enabled`, `collection_routing_enabled`
  - Numeric params: `top_k`, `reranker_top_n`, `max_hops`, `multi_hop_timeout_ms`, `collection_routing_threshold`
- `backend/config/settings.json` — current active config values
- `backend/config.py:77-134` — `SettingsManager.load/update` reads/writes `settings.json`; `save_run_snapshot` already persists config per turn
- `backend/chat/advanced_retrieval.py:36-241` — `AdvancedRetrievalService.retrieve()` consumes `RetrievalSettings` config object; modifies it in-place for dynamic routing

**Type:** Fact

**Implication:** Config variants can be defined as partial `RetrievalSettings` overrides. The config object is already passed through the retrieval pipeline as a parameter — no refactoring needed.

---

### F-002: Evaluation Service — Single-Config Only

**Evidence:**
- `backend/chat/evaluation.py:33-99` — `EvaluationService.run_sanity_check()` loads `eval_dataset.json`, runs all cases, persists result to `evaluation_runs` table. Uses whatever config is currently active in `settings.json`.
- No config parameter is accepted by `run_sanity_check()`; no config override mechanism exists.
- The method saves to `evaluation_runs` table but does **not** link to a config variant or to `SettingsManager.save_run_snapshot()`.
- `backend/chat/evaluation.py:80-89` → `EvaluationRepository.save_run()` stores: `dataset_name`, `model_name`, `total_cases`, `passed_cases`, `overall_recall`, `overall_groundedness`. No `config_variant` column.

**Type:** Fact

**Implication:** Three schema changes needed:
1. Add `config_variant_name` column to `evaluation_runs` table
2. Optionally store the full config snapshot (JSON blob) per run
3. Accept an optional `config_override` parameter in `run_sanity_check()`

---

### F-003: No eval_dataset.json Exists

**Evidence:**
- `backend/chat/evaluation.py:37-52` — searches 4 paths; none exist
- Full glob search confirmed file does not exist in repo

**Type:** Fact

**Implication:** The golden test dataset must be created as part of this feature. 20-30 cases with `question`, `expected_document_id` (or expected answer), and expected source document. Without it the evaluation service is non-functional.

---

### F-004: EvaluationRepository Schema — No Variant Support

**Evidence:**
- `backend/repositories/evaluation_repository.py:10-53` — `save_run()` inserts into `evaluation_runs` with columns: `id`, `dataset_name`, `model_name`, `total_cases`, `passed_cases`, `overall_recall`, `overall_groundedness`
- `list_recent_runs()` returns last 10 with no variant filtering
- No `created_at` column in the insert (but `SELECT *` would return it if defined in schema — likely auto-populated)

**Type:** Fact

**Implication:** Schema migration needed to add `config_variant_name`, `overall_groundedness→groundedness`, and potentially `config_snapshot_json`. The repo needs a new `list_runs_by_variant()` query.

---

### F-005: Frontend Evaluation.jsx — No Comparison UI

**Evidence:**
- `frontend/src/screens/Evaluation.jsx` — Renders metric cards, recharts history chart, recent runs list, and case verdict table
- Metric cards show hardcoded deltas ("+1.2% vs last run") that are purely cosmetic strings
- No mechanism to select two runs for side-by-side comparison
- History chart (`AreaChart`) plots all runs as a continuous line — no variant grouping or color coding
- "Recent Evaluation Runs" list (lines 238-275) shows runs without variant labels

**Type:** Fact

**Implication:** Frontend additions needed:
1. Variant picker / multi-run selector
2. Side-by-side comparison table (ablation matrix — one row per variant, one column per metric)
3. Delta highlighting in metric cards (feeding real comparison data instead of hardcoded strings)
4. Color-coded variant groups in the trend chart

---

### F-006: No Test Coverage for EvaluationService

**Evidence:**
- Full scan of `backend/tests/` — no test file exercises `EvaluationService` or `EvaluationRepository`
- No `conftest.py` exists in the project
- Closest test is `test_streaming_groundedness.py` which mocks services but does not test evaluation

**Type:** Fact

**Implication:** Tests must be written from scratch. The test seam is `EvaluationService.run_sanity_check()` with a mocked `ChatService` and a test `eval_dataset.json`.

---

### F-007: SettingsManager Can Already Persist Config Snapshots

**Evidence:**
- `backend/config.py:123-134` — `SettingsManager.save_run_snapshot()` writes the full `GlobalSettings` to `data/knowledge_ingestion/runs/run_chat_{timestamp}_{turn_id}.json`
- This is called in `ChatService.process_turn()` at line 76

**Type:** Fact

**Implication:** Reuse `save_run_snapshot()` for evaluation runs. Link the snapshot filename to the `evaluation_runs` row so the exact config is auditable per run.

---

### F-008: AdvancedRetrievalService Accepts Config as Parameter

**Evidence:**
- `backend/chat/advanced_retrieval.py:36-41` — `retrieve(query_text, config, collection_ids, k)` accepts a `RetrievalSettings` config
- The config object is passed through the entire pipeline; it's mutated by dynamic routing but the original input config is not preserved

**Type:** Fact

**Implication:** To run with a specific variant, construct a `RetrievalSettings` with overrides and pass it to `process_turn()`. The `EvaluationService` needs a seam to inject config per case run.

---

## Risks and Unknowns

### R-001: Config Mutation by Dynamic Routing
- **What:** `AdvancedRetrievalService.retrieve()` mutates the config object in-place when `dynamic_routing_enabled=True` (lines 59-62 of `advanced_retrieval.py`)
- **Why it matters:** If the same config object is reused across multiple evaluation cases, it will be polluted by the first case's routing decisions
- **Mitigation:** Create a deep copy of the config before each `process_turn()` call in the evaluation loop

### R-002: eval_dataset.json Format Unknown
- **What:** The exact JSON schema expected by `EvaluationService._load_dataset()` and `_evaluate_case()` is not documented
- **Why it matters:** The dataset must be authored before the feature can be verified
- **Mitigation:** Inspect `_evaluate_case()` to reverse-engineer the expected fields, then document in spec

### R-003: EvaluationService Runs Synchronous `process_turn` in Thread Pool
- **What:** `_evaluate_case()` at line 122 uses `loop.run_in_executor(None, self.chat_service.process_turn, ...)` because `process_turn` is synchronous
- **Why it matters:** Running 10-30 cases × N config variants multiplies execution time linearly. There's no progress reporting.
- **Mitigation:** Keep sequential variant execution; add SSE or polling for progress. Consider `asyncio.gather` within a variant.

### R-004: No Existing DB Migration System
- **What:** No migration files or Alembic setup found. The `evaluation_runs` table schema is created somewhere (likely in `database.py`).
- **Why it matters:** Adding columns requires a schema change without migration tooling
- **Mitigation:** Use `ALTER TABLE IF NOT EXISTS` or SQLite additive column approach. Document as known limit.

---

## Preserved Behavior Inventory

| Behavior | Where It Lives | Why Preserve | Verification |
|---|---|---|---|
| Single "Run Sanity Check" button still works as before | `Evaluation.jsx` + `POST /chat/evaluate/sanity-check` | Existing users expect single-click eval | E2E test: click button → results appear |
| Evaluation history endpoint continues returning last 10 runs | `GET /chat/evaluate/history` | Frontend trend chart depends on it | Existing frontend load test |
| `process_turn()` pipeline unchanged | `ChatService.process_turn()` | Load-bearing business logic; must not regress | Existing test suite |
| Config persistence format | `settings.json` | Other services read it | Manual check |

---

## Existing Patterns to Reuse

| Pattern | Location | When to Use |
|---|---|---|
| Config snapshot | `config.py:save_run_snapshot()` | Persist variant config per evaluation run |
| `RetrievalSettings` model | `schemas/settings.py` | Define variants as partial overrides |
| SSE streaming pattern | `chat/streaming.py` | Progress reporting for long multi-variant runs |
| `recharts` AreaChart | `Evaluation.jsx` | Extend with variant-colored series |
| `SanityCheckResponse` schema | `schemas/chat.py` | Reuse shape for single-variant result |

---

## Recommendation

- **Next skill:** `/spec-requirements`
- **Why:** Scope and requirements are clear based on this analysis. The brownfield surface is well-bounded, no contested technical choices remain.
- **Exact next action:** Draft `spec.md` defining:
  1. Config variant format (partial `RetrievalSettings` overrides with human-readable labels)
  2. New API endpoints: `POST /evaluate/ablation` (accepts list of variants, returns comparison) and `GET /evaluate/variants` (lists available variants)
  3. Schema migration: add `config_variant_name` + `config_snapshot_json` to `evaluation_runs`
  4. Frontend: comparison table component + variant picker + delta visualization
  5. Golden dataset: `eval_dataset.json` with 20 cases (reverse-engineer expected format from `_evaluate_case()`)
  6. Test plan: unit tests for `EvaluationService` with mocked `ChatService`, integration test for ablation endpoint

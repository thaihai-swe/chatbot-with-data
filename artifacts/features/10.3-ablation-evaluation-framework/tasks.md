# Task Breakdown

## Metadata
- Feature slug: `10.3-ablation-evaluation-framework`
- Date: 2026-07-09
- Status: Draft

---

## Foundational

### Phase 1: Foundational Data + Schema
Goal: Create evaluation dataset, variant definitions, and database schema. · ACs: AC-003, AC-004 · Proof: `cat backend/test_data/eval_dataset.json | jq 'length >= 15'`

- [x] TASK-001 Create golden evaluation dataset
  Status: Done
  Summary: Create `backend/test_data/eval_dataset.json` with ~20 test cases. Each case needs `id`, `question`, and `expected_document_id`. Use `_evaluate_case()` format from `backend/chat/evaluation.py` as reference.
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/test_data/eval_dataset.json` (CREATE)
  Proving command or proof: `cat backend/test_data/eval_dataset.json | jq 'length >= 15'`

- [x] TASK-002 Create config variant definitions
  Status: Done
  Summary: Create `backend/config/ablation-variants.json` with 4 variants: `baseline`, `semantic`, `full_pipeline`, `full_minus_reranker`. Each variant has `name`, `label`, `description`, and `overrides` (partial RetrievalSettings dict).
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/config/ablation-variants.json` (CREATE)
  Proving command or proof: `cat backend/config/ablation-variants.json | jq 'length == 4'`

- [x] TASK-003 Add schema migration 0008_ablation_variants + update repository
  Status: Done
  Summary: Add `0008_ablation_variants` migration block to `backend/migrations/runner.py` that adds `config_variant_name TEXT` and `config_snapshot_json TEXT` columns to `evaluation_runs`. Update `EvaluationRepository.save_run()` to accept and persist both new fields. Add optional `config_variant_name` and `config_snapshot_json` params.
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/migrations/runner.py` (MODIFY), `backend/repositories/evaluation_repository.py` (MODIFY)
  Proving command or proof: Run migration, then verify columns exist: `sqlite3 backend/data/knowledge_ingestion/app.db "PRAGMA table_info(evaluation_runs)" | grep -E "config_variant_name|config_snapshot_json"`

---

## User Story P1: Backend Ablation API (US-001)

### Phase 2: Backend Ablation API
Goal: Config override in EvaluationService, new schemas, ablation router. · ACs: AC-001, AC-002, AC-005, AC-007 · Proof: `curl -X POST /evaluate/ablation -d '{"variants":["baseline","full_pipeline"]}' | jq '.comparisons | length == 2'`

- [x] TASK-004 Add config override seam to EvaluationService
  Status: Done
  Summary: Modify `EvaluationService.run_sanity_check()` to accept optional `config_override: Optional[RetrievalSettings] = None` and `config_variant_name: Optional[str] = None`. When `config_override` is set, use `copy.deepcopy(config_override)` before each `process_turn()` call to prevent mutation. Persist `config_variant_name` and snapshot path to `EvaluationRepository.save_run()`. Add `import copy`.
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `backend/chat/evaluation.py` (MODIFY)
  Depends on: TASK-001, TASK-002
  Proving command or proof: Unit test asserting config immutability after evaluation loop with `dynamic_routing_enabled=True`

- [x] TASK-005 Add ablation schemas and router endpoint
  Status: Done
  Summary: Add `VariantResult`, `VariantDelta`, and `AblationComparisonResponse` models to `backend/schemas/chat.py`. Create `backend/routers/ablation.py` with `POST /evaluate/ablation` endpoint that: validates variant names against `ablation-variants.json`, loads variant configs, runs them sequentially via `EvaluationService`, computes deltas from first variant, returns `AblationComparisonResponse`. Register router in `backend/routers/__init__.py` or `backend/main.py`.
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-001, AC-002, AC-007
  Affected file(s) or module(s): `backend/schemas/chat.py` (MODIFY), `backend/routers/ablation.py` (CREATE), `backend/routers/__init__.py` (MODIFY)
  Depends on: TASK-003, TASK-004
  Proving command or proof: `curl -s -X POST http://localhost:8000/evaluate/ablation -H 'Content-Type: application/json' -d '{"variants": ["baseline", "full_pipeline"]}' | jq '.comparisons | length == 2'`

- [x] TASK-006 Write backend tests for ablation + evaluation
  Status: Done
  Summary: Created `backend/tests/chat/test_ablation.py` with 9 tests: config deep-copy immutability (AC-005), EvaluationService unit tests (happy path, empty dataset, config override persistence), ablation router integration tests (happy path 2 variants, happy path 1 variant, unknown variant, empty variants list, existing sanity-check unaffected). All pre-existing 115 backend tests unaffected.
  Linked acceptance criteria: AC-008
  Affected file(s) or module(s): `backend/tests/chat/test_ablation.py` (CREATE), `backend/chat/evaluation.py` (bugfix: pass session_id to _evaluate_case, fix expected_doc_id name)
  Depends on: TASK-005
  Proving command or proof: `cd backend && python -m pytest tests/chat/test_ablation.py -x -q 2>&1 | tail -3` — 9 passed

---

## User Story P2: Frontend Comparison Table (US-002)

### Phase 3: Frontend Comparison Table
Goal: Ablation table component in Evaluation Dashboard. · ACs: AC-006 · Proof: Ablation comparison table visible in UI after ablation run

- [x] TASK-007 Add frontend ablation comparison table
  Status: Done
  Summary: Added `<AblationTable>` component inline in `Evaluation.jsx`. Table shows one row per variant with columns: Recall, Groundedness, Citation, Latency, Pass Rate. Delta arrows (▲ green / ▼ red) display improvement/regression relative to first variant. Added `runAblation()` API function in `chat.js`. "Run Ablation" button in header row calls `POST /evaluate/ablation` with all 4 hardcoded variants. State management for ablation data, loading, and error included. Frontend builds clean (`npm run build`).
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/screens/Evaluation.jsx` (MODIFY), `frontend/src/api/chat.js` (MODIFY)
  Depends on: TASK-005
  Proving command or proof: `cd frontend && npm run build` — builds clean; Manual UI inspection after backend+frontend start completes

---

## Resume Notes

- **Next recommended task:** TASK-001, TASK-002, or TASK-003 (all zero deps, can run in parallel)
- **Blocker:** None
- **Next proof:** `cat backend/test_data/eval_dataset.json | jq 'length >= 15'`

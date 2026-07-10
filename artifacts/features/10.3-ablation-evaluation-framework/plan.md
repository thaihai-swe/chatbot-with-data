# Implementation Plan

## Metadata

- Feature slug: `10.3-ablation-evaluation-framework`
- Date: 2026-07-10
- Status: Approved
- Spec approved date: 2026-07-09

---

## Global Constraints

- **Non-goals (from spec):** No experiment management system, no automatic regression detection, no production A/B testing, no new evaluation metrics.
- **Technical constraints:** SQLite only (use ALTER TABLE ADD COLUMN, no Alembic). Config mutation by dynamic routing requires `copy.deepcopy`. Pipeline `process_turn()` unchanged.
- **Protected behavior:** Single "Run Sanity Check" must still work. `GET /chat/evaluate/history` unchanged. `settings.json` format unchanged.
- **Explicit out of scope:** User-defined variants from UI, SSE streaming, historical cross-run comparison, multiple datasets.

---

## Part 1: Technical Design

### Comprehensive Design

**Design Summary:**

Add an ablation evaluation mode that runs the golden test dataset against multiple pre-defined pipeline config variants sequentially and returns a side-by-side comparison. The design is additive: new files + new endpoint + new frontend component. Zero changes to the existing pipeline execution path.

**Current State:**

- `EvaluationService.run_sanity_check()` loads `eval_dataset.json` (which doesn't exist), runs all cases against whichever config is active in `settings.json`, persists one row in `evaluation_runs`, returns `SanityCheckResponse`.
- `RetrievalSettings` has ~20 toggle fields; `AdvancedRetrievalService.retrieve()` accepts a `RetrievalSettings` config parameter.
- `SettingsManager.save_run_snapshot()` persists full config to disk per turn.
- No variant tracking exists in `evaluation_runs` table.
- Frontend `Evaluation.jsx` renders metric cards, history chart, runs list, and case verdict table — all from existing backend data.

**Proposed Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                     POST /evaluate/ablation                  │
│  Router: ablation.py                                         │
│    │                                                         │
│    ├─ 1. Load variant defs from config/ablation-variants.json│
│    ├─ 2. Validate variant names                              │
│    ├─ 3. For each variant:                                   │
│    │    ├─ Build RetrievalSettings (base + variant overrides)│
│    │    ├─ Run EvaluationService.run_sanity_check(config_override=variant_config)
│    │    │    └─ deepcopy(config) per case → process_turn()   │
│    │    ├─ Persist run with config_variant_name + snapshot   │
│    │    └─ Collect per-variant result                        │
│    ├─ 4. Compute deltas from first variant (baseline)        │
│    └─ 5. Return AblationComparisonResponse                   │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow & Interfaces:**

1. **Config override seam:** `EvaluationService.run_sanity_check()` gains optional parameters: `config_override: Optional[RetrievalSettings] = None` and `config_variant_name: Optional[str] = None`. When `config_override` is set, it deep-copies the config per case and passes it to `process_turn()` via the chat service — no pipeline changes needed.

2. **Variant definition file** (`backend/config/ablation-variants.json`):
```json
[
  {
    "name": "baseline",
    "label": "BM25 Baseline",
    "description": "Keyword-only retrieval, all enhancements disabled",
    "overrides": {
      "retrieval_mode": "keyword",
      "intelligence_enabled": false,
      "query_expansion_enabled": false,
      "query_decomposition_enabled": false,
      "hyde_enabled": false,
      "synonym_expansion_enabled": false,
      "dynamic_routing_enabled": false,
      "reranker_enabled": false,
      "parent_child_enabled": false,
      "multi_hop_enabled": false,
      "collection_routing_enabled": false
    }
  },
  {
    "name": "semantic",
    "label": "Semantic Search",
    "description": "Semantic vector search, all enhancements disabled",
    "overrides": {
      "retrieval_mode": "semantic",
      "intelligence_enabled": false,
      "query_expansion_enabled": false,
      "query_decomposition_enabled": false,
      "hyde_enabled": false,
      "synonym_expansion_enabled": false,
      "dynamic_routing_enabled": false,
      "reranker_enabled": false,
      "parent_child_enabled": false,
      "multi_hop_enabled": false,
      "collection_routing_enabled": false
    }
  },
  {
    "name": "full_pipeline",
    "label": "Full Pipeline",
    "description": "All enhancements enabled (as configured in settings.json)",
    "overrides": {}
  },
  {
    "name": "full_minus_reranker",
    "label": "Full Pipeline (no reranker)",
    "description": "Full pipeline with reranker disabled",
    "overrides": {
      "reranker_enabled": false
    }
  }
]
```

3. **New schemas** (`backend/schemas/chat.py`):
```python
class VariantResult(BaseModel):
    variant_name: str
    label: str
    result: SanityCheckResponse

class VariantDelta(BaseModel):
    variant_name: str
    recall_delta: Optional[float] = None
    groundedness_delta: Optional[float] = None
    citation_coverage_delta: Optional[float] = None
    pass_rate_delta: Optional[float] = None

class AblationComparisonResponse(BaseModel):
    variants: List[str]
    comparisons: List[VariantResult]
    deltas: List[VariantDelta]
```

4. **Migration** (`0008_ablation_variants`): Add `config_variant_name TEXT` and `config_snapshot_json TEXT` to `evaluation_runs`. Follow existing ALTER TABLE pattern from `migrations/runner.py`.

5. **`EvaluationRepository.update`:** Add `config_variant_name` and `config_snapshot_json` params to `save_run()`. No new query methods needed.

6. **Frontend** (`Evaluation.jsx`): New `<AblationTable>` component rendered below existing evaluation results when `ablationData` state is set. Reuses existing `recharts` (already installed) if chart visualization is desired. Table columns: variant name, overall_recall, overall_groundedness, overall_citation_coverage, mean latency, pass rate. Delta column per metric colored green/red.

**File / module touch list:**

| File | Change |
|---|---|
| `backend/test_data/eval_dataset.json` | CREATE — golden dataset |
| `backend/config/ablation-variants.json` | CREATE — variant definitions |
| `backend/migrations/runner.py` | ADD — 0008_ablation_variants migration block |
| `backend/schemas/chat.py` | ADD — `VariantResult`, `VariantDelta`, `AblationComparisonResponse` |
| `backend/repositories/evaluation_repository.py` | MODIFY — `save_run()` params, add config_variant fields |
| `backend/chat/evaluation.py` | MODIFY — `run_sanity_check()` accepts `config_override`, `config_variant_name`; add deep-copy logic |
| `backend/routers/ablation.py` | CREATE — new router with `POST /evaluate/ablation` |
| `backend/main.py` or `backend/routers/__init__.py` | MODIFY — register new router |
| `frontend/src/screens/Evaluation.jsx` | MODIFY — add AblationTable component + ablation button + state |
| `backend/tests/chat/test_ablation.py` | CREATE — unit + integration tests |

**Key Decisions & Tradeoffs:**

| Decision | Choice | Rationale |
|---|---|---|
| Variant storage | JSON file (not DB, not code) | Config variants are static and rarely change; JSON is editable without code deployment |
| Config override mechanism | Parameter on `run_sanity_check()` | Minimal surface change — no new service abstraction needed |
| Deep-copy per case | `copy.deepcopy(config)` per `process_turn()` | Prevents mutation leakage; confirmed necessary from R-001 analysis |
| Ablation endpoint location | New `routers/ablation.py` | Keeps concerns separated; chat.py already 216 lines |
| Frontend table component | Inline in `Evaluation.jsx` as `<AblationTable>` | One file change, no new component file needed for a single-use component |
| Deltas from first variant | First variant is treated as baseline; deltas computed relative to it | Simple contract; user controls which variant is baseline by ordering |

**Non-Functional Considerations:**

- Performance: 4 variants × 20 cases = 80 process_turn calls. Expected ~3-5 min total. Sync response.
- Reliability: Errors in one case don't crash other cases (existing try/except in `_evaluate_case`). Errors in one variant don't crash others (new try/except per variant in ablation endpoint).
- Maintainability: New variants addable by editing JSON file — no code change.

**Protected Behavior:**

- `POST /chat/evaluate/sanity-check` unchanged (no config_override → existing behavior)
- `GET /chat/evaluate/history` unchanged
- `evaluation_runs` table: existing rows have NULL for new columns (backward compatible)
- Pipeline `process_turn()` unchanged

---

## Part 2: Delivery Strategy

### Execution Context

- Delivery profile: Moderate
- Locked spec decisions: Variant format = JSON file, 4 pre-defined variants, sync response, single dataset, table-style frontend comparison

### Implementation Strategy

**Strategy: MVP-first** — Complete and verify P1 (backend API) including its tests before any P2 (frontend) work begins. P1 is independently testable via curl.

### User Story Decomposition

| Phase | Story | Description | Ships independently |
|---|---|---|---|
| Foundational | n/a | Data files and schema | No |
| P1: Backend Ablation API | US-001 | Run ablation via API, get comparison response | Yes |
| P2: Frontend Comparison Table | US-002 | See ablation results in Evaluation Dashboard | Yes (with P1 deployed) |

### First Delivery Slice

- **Smallest useful slice:** `POST /evaluate/ablation` returns comparison for 2+ variants, verifiable via curl.
- **Why this slice goes first:** Core value — enables data-driven config comparison. Frontend is enhancement.
- **What proof should exist:** `curl -X POST /evaluate/ablation -d '{"variants":["baseline","full_pipeline"]}' | jq '.comparisons | length == 2'`

### Execution Phases

#### Phase 1: Foundational Data + Schema
- Goal: Create the evaluation dataset, variant definitions, and database schema for ablation tracking.
- Entry proof: No files exist yet.
- Exit proof: `eval_dataset.json` has >= 15 entries, `ablation-variants.json` has 4 variants, migration `0008_ablation_variants` is applied.
- Tasks: TASK-001, TASK-002, TASK-003

#### Phase 2: Backend Ablation API (User Story P1 — US-001)
- Goal: Config override + deep-copy in EvaluationService, new schemas, ablation router endpoint.
- Entry proof: Phase 1 complete.
- Exit proof: `curl -X POST /evaluate/ablation` returns valid `AblationComparisonResponse` with per-variant metrics.
- Tasks: TASK-004, TASK-005, TASK-006

#### Phase 3: Frontend Comparison Table (User Story P2 — US-002)
- Goal: AblationTable component in Evaluation.jsx.
- Entry proof: Phase 2 complete.
- Exit proof: Ablation comparison table visible in Evaluation Dashboard after ablation run.
- Tasks: TASK-007

### Validation Strategy

- **Unit tests:** Config deep-copy immutability (TASK-004), `EvaluationService` with mocked `ChatService` (TASK-006)
- **Integration tests:** `POST /evaluate/ablation` returns correct response shape, unknown variant returns 400, existing sanity-check still works (TASK-006)
- **Manual verification:** Frontend ablation table rendering (TASK-007)
- **Observability checks:** Verify `config_variant_name` is non-null in DB after ablation run

### Traceability Matrix

| REQ | AC | Phase | Task ID |
|---|---|---|---|
| REQ-001 (Config variants) | AC-001, AC-002 | Phase 1 | TASK-002 |
| REQ-002 (Ablation API) | AC-001, AC-007 | Phase 2 | TASK-005 |
| REQ-003 (Config isolation) | AC-005 | Phase 2 | TASK-004 |
| REQ-004 (Schema migration) | AC-003 | Phase 1 | TASK-003 |
| REQ-005 (Golden dataset) | AC-004 | Phase 1 | TASK-001 |
| REQ-006 (Frontend table) | AC-006 | Phase 3 | TASK-007 |
| — | AC-008 (all tests pass) | Phase 2 | TASK-006 |

### Rollout Plan

- **Release approach:** Direct merge (no feature flags). Changes are additive and backward compatible.
- **Migration needs:** `0008_ablation_variants` runs automatically on next backend startup via `migrations/runner.py`.
- **Backward compatibility:** Existing `evaluation_runs` rows have NULL `config_variant_name`. Existing API endpoints unchanged.

### Rollback Plan

Revert the merge commit. The migration is additive (ALTER TABLE ADD COLUMN) — no data loss. Re-run `apply_migrations()` on the previous version (it skips already-recorded migrations).

### Risks And Mitigations

- **RISK-001 Config Mutation:** Dynamic routing mutates config in-place. Mitigation: `copy.deepcopy(config)` before each `process_turn()` call. Verified by AC-005.
- **RISK-002 Sequential Runtime:** 4 variants × 20 cases × ~3s/case = ~4 min. Mitigation: Acceptable for a development tool; document in UI.

### Open Questions

None — all resolved during spec phase.

---

## Plan Self-Review (before Plan Approved)

- [x] Global Constraints filled from spec
- [x] Every REQ/AC maps to a phase or task ID in the Traceability Matrix
- [x] No placeholder prose
- [x] First unblocked task is executable from `tasks.md` alone (TASK-001 is creating a JSON file)
- [x] File/module targets named
- [x] Proof commands are exact
- [ ] Dependency edges in `tasks.md` will be checked: `python3 scripts/core/task_graph.py --feature 10.3-ablation-evaluation-framework --check`

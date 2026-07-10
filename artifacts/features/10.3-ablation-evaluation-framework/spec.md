# Feature Specification: 10.3 Ablation Evaluation Framework

## Metadata

- Feature name: Ablation Evaluation Framework
- Feature slug: `10.3-ablation-evaluation-framework`
- Delivery profile: Moderate
- Owner: Antigravity
- Status: Draft
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/10.3-ablation-evaluation-framework/analysis.md), [proposal.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/10.3-ablation-evaluation-framework/proposal.md)

## Problem Statement

The RAG system's README documents an ablation study table showing expected metric gains per pipeline stage (BM25-only → +Semantic → +Query Expansion → +Reranking → +Multi-Hop → Full Pipeline), but the evaluation service (`EvaluationService.run_sanity_check()`) can only run against whatever pipeline configuration is currently active in `settings.json`. There is no mechanism to:

- Run the golden test dataset against multiple pipeline configurations
- Compare metrics across configurations side-by-side
- Prove which pipeline stages actually contribute measurable gains
- Detect regressions when pipeline parameters change

This means the ablation table in the README remains aspirational — the system cannot produce real measurements to validate the claimed improvements.

## Desired Outcomes

- **Backend:** A new endpoint accepts a list of pre-defined config variants, runs the full evaluation dataset against each sequentially, and returns a comparison response with per-variant metrics and deltas.
- **Data:** A golden `eval_dataset.json` exists with ~20 test cases, enabling the evaluation service to function.
- **Persistence:** Each evaluation run stores its variant name and a snapshot of the config used, enabling traceability.
- **Frontend:** The Evaluation Dashboard shows an ablation comparison table that lets users see which pipeline configuration performs best on which metric.
- **Verification:** Tests exist for the ablation endpoint and for `EvaluationService` with mocked dependencies.

## Minimum Release Slice

- **What ships in the first useful release:**
  - `eval_dataset.json` with ~20 golden test cases
  - Config variant definitions in `config/ablation-variants.json` (4 variants: Baseline, +Semantic, Full Pipeline, Full minus Reranker)
  - Schema migration `0008_ablation_variants`: add `config_variant_name` and `config_snapshot_json` columns to `evaluation_runs`
  - `POST /evaluate/ablation` endpoint that accepts a list of variant names, runs them sequentially, returns a comparison response
  - Update `EvaluationService.run_sanity_check()` to accept optional `config_override` and `config_variant_name`
  - Deep-copy config before each case run to prevent mutation pollution (mitigation for R-001)
  - Frontend ablation comparison table in `Evaluation.jsx` showing per-variant metrics with delta highlighting
  - Unit tests for `EvaluationService` with mocked `ChatService`
  - Integration test for `POST /evaluate/ablation`

- **What can wait:**
  - User-defined custom variants from the UI
  - SSE progress streaming for long runs
  - Historical cross-run ablation comparison (only current run is compared)
  - Multiple dataset support (single dataset only)

## Success Criteria

- **SC-001:** `POST /evaluate/ablation` returns a comparison response with metrics for each variant, including overall_recall, overall_groundedness, and per-case results.
  - Proving command: `curl -s -X POST http://localhost:8000/evaluate/ablation -H 'Content-Type: application/json' -d '{"variants": ["baseline", "full_pipeline"]}' | jq '.comparisons | length == 2'`
- **SC-002:** Each evaluation run persisted after ablation has a non-null `config_variant_name` and a `config_snapshot_json` linking to the snapshot file.
  - Proving command: `sqlite3 backend/data/knowledge_ingestion/app.db "SELECT config_variant_name, config_snapshot_json FROM evaluation_runs WHERE config_variant_name IS NOT NULL LIMIT 1" | wc -l`
- **SC-003:** The ablation comparison table appears on the Evaluation Dashboard after an ablation run, showing per-variant metric rows with delta columns.
  - Validation method: Manual UI inspection
- **SC-004:** The existing single "Run Sanity Check" button still functions identically — it runs with the live config and returns a `SanityCheckResponse`.
  - Proving command: `curl -s -X POST http://localhost:8000/chat/evaluate/sanity-check | jq '.total_cases > 0'`
- **SC-005:** `eval_dataset.json` exists at `backend/test_data/eval_dataset.json` with at least 15 test cases, each containing `id`, `question`, and `expected_document_id`.
  - Proving command: `cat backend/test_data/eval_dataset.json | jq 'length >= 15'`
- **SC-006:** Config is deep-copied per case run — a variant with `dynamic_routing_enabled` does not leak mutation to the next variant.
  - Validation method: Unit test asserting config immutability after evaluation loop
- **SC-007:** All backend tests pass, including new ablation and evaluation tests.
  - Proving command: `cd backend && python -m pytest tests/ -x -q 2>&1 | tail -5`

## In Scope

- Creating `backend/test_data/eval_dataset.json` with ~20 test cases reverse-engineered from `EvaluationService._evaluate_case()` expected format
- Creating `backend/config/ablation-variants.json` defining 4 config variants as partial `RetrievalSettings` overrides
- Schema migration `0008_ablation_variants` adding columns to `evaluation_runs`
- `POST /evaluate/ablation` endpoint in `backend/routers/ablation.py` (new router)
- `AblationComparisonResponse` schema in `backend/schemas/chat.py`
- Config override seam in `EvaluationService.run_sanity_check()` + deep-copy per case
- Updating `EvaluationRepository.save_run()` to accept and persist `config_variant_name` and `config_snapshot_json`
- Frontend ablation comparison table component in `Evaluation.jsx`
- Unit tests for `EvaluationService` with mocked `ChatService`
- Integration test for ablation endpoint

## Out Of Scope

- User-defined custom variants from the frontend (variants defined in config file only)
- SSE progress streaming for multi-variant runs (sync response only)
- Historical cross-run ablation comparison (one-run comparison only)
- Multiple evaluation datasets
- Changing the pipeline execution model or adding new pipeline components
- Refactoring the Evaluation.jsx layout beyond the comparison table addition

## Non-Goals

- Building a full experiment management system with persistence of ablation runs
- Automatic regression detection or alerting
- A/B testing in production (offline evaluation only)
- Changing the underlying evaluation metrics or adding new ones

## Users And Stakeholders

- Primary users: Developers and operators tuning the RAG pipeline
- Secondary stakeholders: Anyone reading the README ablation study table who wants real numbers

## User Stories And Key Scenarios

- **US-001:** As a developer, I want to run the ablation suite with a single API call and see which pipeline config produces the best metrics, so I can make data-driven decisions about which features to enable.
- **US-002:** As a reviewer, I want to see a comparison table in the Evaluation Dashboard showing metric deltas between variants, so I can quickly assess the impact of pipeline changes.

### Detailed Scenarios

- Scenario 1 (Happy Path — Full Ablation):
  - Given: `eval_dataset.json` exists with 20 cases, `ablation-variants.json` defines 4 variants
  - When: User triggers ablation via frontend button or `POST /evaluate/ablation`
  - Then: All 4 variants run sequentially, comparison response is returned, frontend renders the comparison table
- Scenario 2 (Edge Case — Single Variant):
  - Given: User requests ablation with only 1 variant
  - When: `POST /evaluate/ablation` with `{"variants": ["baseline"]}`
  - Then: Single variant runs, comparison has 1 entry, no deltas computed
- Scenario 3 (Error State — Unknown Variant):
  - Given: `ablation-variants.json` defines 4 variants
  - When: User requests unknown variant name
  - Then: HTTP 400 with error message listing valid variant names
- Scenario 4 (Error State — Empty Dataset):
  - Given: `eval_dataset.json` has 0 cases
  - When: Ablation runs
  - Then: Response shows 0 total_cases for each variant, frontend shows empty state

## Current Context

- **Current behavior summary:** `EvaluationService.run_sanity_check()` loads `eval_dataset.json` (which doesn't exist yet), runs all cases against the live config, persists one result row. No multi-config support exists.
- **Impacted boundaries:** Backend schemas (new response model), backend routers (new endpoint), backend evaluation (config override), backend migrations (schema change), frontend (comparison table), backend config (new variants file).
- **Preserved behavior:** Single "Run Sanity Check" remains unchanged. `GET /chat/evaluate/history` unchanged. Pipeline `process_turn()` unchanged. `settings.json` format unchanged.
- **Brownfield risk rating:** Low — mostly additive changes (new endpoint, new schema, new file, new component). The only mutation risk is config object pollution (R-001), mitigated by deep-copy.

## Gray-Area Decisions

| Decision | Resolution | Status |
|---|---|---|
| Variant definition format | JSON file (`config/ablation-variants.json`) with partial `RetrievalSettings` overrides | Locked |
| Number of pre-defined variants | 4: `baseline`, `semantic`, `full_pipeline`, `full_minus_reranker` | Locked — expandable later |
| Ablation progress | Sync response (no SSE) — acceptable for 4 variants × 20 cases | Locked |
| eval_dataset.json location | `backend/test_data/eval_dataset.json` | Locked |
| Comparison UI | Side-by-side table in Evaluation.jsx with delta columns | Locked |

## Dependencies And External Touchpoints

- **DEP-001:** Golden dataset `eval_dataset.json` must be created with ~20 cases matching `_evaluate_case()` expected format
- **DEP-002:** No external API dependencies — fully self-contained
- **DEP-003:** No new Python or npm packages required

## Functional Requirements

### REQ-001: Ablation Config Variants

- **Requirement:** The system MUST define at least 4 pre-configured ablation variants as partial `RetrievalSettings` overrides in `backend/config/ablation-variants.json`:
  - `baseline`: `retrieval_mode=keyword`, all intelligence/reranking/multi-hop disabled
  - `semantic`: `retrieval_mode=semantic`, all intelligence/reranking/multi-hop disabled
  - `full_pipeline`: full active config as-is from `settings.json`
  - `full_minus_reranker`: full pipeline with `reranker_enabled=false`
- **Why it matters:** Without standard variants, comparison results are not reproducible or shareable.
- **Linked SC:** SC-001, SC-006
- **Priority:** Must Have

### REQ-002: Ablation API Endpoint

- **Requirement:** `POST /evaluate/ablation` MUST accept `{"variants": ["name1", "name2"]}` and return an `AblationComparisonResponse` containing per-variant `SanityCheckResponse` results and inter-variant deltas.
- **Why it matters:** Provides the primary backend capability for running multi-config evaluation.
- **Linked SC:** SC-001, SC-004
- **Priority:** Must Have
- **Validation surface:** Integration test

### REQ-003: Config Isolation Per Case

- **Requirement:** When running ablation, each evaluation case MUST receive a deep copy of the variant's `RetrievalSettings` config to prevent mutation leakage across cases and variants.
- **Why it matters:** Dynamic routing mutates the config object in-place (R-001). Without deep-copy, successive cases would have different configs than intended.
- **Linked SC:** SC-006
- **Priority:** Must Have
- **Validation surface:** Unit test asserting config immutability

### REQ-004: Schema Migration for Variant Columns

- **Requirement:** A migration `0008_ablation_variants` MUST add `config_variant_name TEXT` and `config_snapshot_json TEXT` columns to the `evaluation_runs` table.
- **Why it matters:** Enables linking each evaluation run to the variant definition and config snapshot used.
- **Linked SC:** SC-002
- **Priority:** Must Have

### REQ-005: Golden Evaluation Dataset

- **Requirement:** `backend/test_data/eval_dataset.json` MUST exist with at least 15 test cases. Each case MUST have `id` (string), `question` (string), and `expected_document_id` (string). Additional optional fields (`expected_answer`, `category`, `difficulty`) MAY be present.
- **Why it matters:** Without a dataset, the evaluation service returns empty results.
- **Linked SC:** SC-005
- **Priority:** Must Have

### REQ-006: Frontend Ablation Comparison Table

- **Requirement:** The Evaluation Dashboard (`Evaluation.jsx`) MUST display an ablation comparison table after an ablation run completes. The table MUST show one row per variant and columns for: variant name, overall_recall, overall_groundedness, overall_citation_coverage, mean latency, and pass rate. Deltas from the baseline variant MUST be highlighted (green for improvement, red for regression).
- **Why it matters:** Makes ablation results immediately visible and actionable.
- **Linked SC:** SC-003
- **Priority:** Should Have

## Non-Functional Requirements

- **NFR-001 Performance:** A full ablation run (4 variants × 20 cases) MUST complete within 5 minutes on a development machine with a working LLM provider.
  - Linked ACs: AC-001
- **NFR-002 Reliability:** If the LLM provider returns errors for specific cases, those cases MUST be reported as failures, not crash the entire ablation run.
  - Linked ACs: AC-007
- **NFR-003 Maintainability:** New config variants MUST be addable by editing `ablation-variants.json` without code changes.
  - Linked ACs: AC-001, AC-002

## Constraints

- **Technical:** SQLite database — use `ALTER TABLE ADD COLUMN` for migration (no Alembic)
- **Technical:** Config mutation by dynamic routing requires deep-copy (use `copy.deepcopy`)
- **Delivery:** Must not break existing single-run sanity check behavior or evaluation history endpoint

## Assumptions

- **ASM-001:** Golden test dataset cases query documents indexed in a running Weaviate instance — tests will mock the retrieval layer
- **ASM-002:** The `_evaluate_case()` method's expected format for dataset entries is stable (reviewed in analysis F-003)

## Risks

- **RISK-001 Config Mutation:** `AdvancedRetrievalService.retrieve()` mutates config in-place. Mitigation: `copy.deepcopy(config)` before each `process_turn()` call.
- **RISK-002 Sequential Runtime:** 4 variants × 20 cases = 80 sequential LLM calls. Mitigation: Document expected runtime in UI status text.
- **RISK-003 Missing Golden Data:** Without `eval_dataset.json` the feature cannot be verified. Mitigation: Include dataset creation as committed deliverable.

## Open Questions

None — all decisions resolved during grilling and analysis.

## Acceptance Criteria

- [ ] **AC-001 Linked REQ:** REQ-001, REQ-002
  - Linked success criteria: SC-001
  - Validation method: Integration test
  - Proof target: `POST /evaluate/ablation` with `["baseline", "full_pipeline"]` returns 2 comparison entries

- [ ] **AC-002 Linked REQ:** REQ-001
  - Linked success criteria: SC-001
  - Validation method: Integration test
  - Proof target: Unknown variant returns HTTP 400 with error message

- [ ] **AC-003 Linked REQ:** REQ-004
  - Linked success criteria: SC-002
  - Validation method: Automated check
  - Proof target: Run ablation, verify `config_variant_name` is non-null in DB

- [ ] **AC-004 Linked REQ:** REQ-005
  - Linked success criteria: SC-005
  - Validation method: File existence + JSON schema check
  - Proof target: `backend/test_data/eval_dataset.json` has >= 15 entries

- [ ] **AC-005 Linked REQ:** REQ-003
  - Linked success criteria: SC-006
  - Validation method: Unit test
  - Proof target: Config object remains unchanged after evaluation loop with `dynamic_routing_enabled=True`

- [ ] **AC-006 Linked REQ:** REQ-006
  - Linked success criteria: SC-003
  - Validation method: Manual UI inspection
  - Proof target: Ablation comparison table visible in Evaluation Dashboard after ablation run

- [ ] **AC-007 Linked REQ:** REQ-002
  - Linked success criteria: SC-004
  - Validation method: Integration test
  - Proof target: Existing `POST /chat/evaluate/sanity-check` still returns valid response

- [ ] **AC-008** Linked REQ: REQ-002
  - Linked success criteria: SC-007
  - Validation method: Automated test run
  - Proof target: `python -m pytest tests/ -x -q` passes with new tests

## Related ADRs

- ADR-001: Source-to-Answer Provenance Mode — no conflict; this feature is additive and does not constrain citation or provenance design.

## Notes

- Config variants file format (`config/ablation-variants.json`) will contain an array of objects with `name`, `label`, `description`, and `overrides` (partial `RetrievalSettings` dict).
- The `AblationComparisonResponse` schema: `{"variants": [...], "comparisons": [{"variant_name": str, "result": SanityCheckResponse, "delta_from_baseline": {...}}]}`
- Frontend comparison table will be a new component `<AblationTable>` rendered below the existing evaluation results when ablation data is present.

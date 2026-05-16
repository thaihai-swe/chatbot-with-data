# Implementation Plan: Query Expansion and Rewriting

## Metadata

- Feature name: Query Expansion and Rewriting
- Feature slug: 5.2-query-expansion-and-rewriting
- Related spec: `artifacts/features/5.2-query-expansion-and-rewriting/spec.md`
- Related design: `artifacts/features/5.2-query-expansion-and-rewriting/design.md`
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16

## Plan Summary

We will implement a standalone query rewriting component to normalize intent and a hybrid expansion pipeline that leverages both raw and rewritten queries. The plan starts with backend prompt engineering and service logic, moves to retrieval pipeline orchestration, and concludes with schema updates and UI visibility. This phased approach ensures the "intelligence" is verified before the UI is exposed.

## Execution Context

- **Design reference:** `artifacts/features/5.2-query-expansion-and-rewriting/design.md`
- **Patterns:** Using `QueryIntelligenceService` for LLM transformations and `AdvancedRetrievalService` for RAG orchestration.
- **Constraints:** Python virtualenv, OpenAI API compatibility.

## First Delivery Slice

- **Smallest useful slice:** Implementation of `rewrite_query` and the updated hybrid loop in `AdvancedRetrievalService` (verified via logs/integration tests).
- **Why this slice goes first:** It delivers the actual retrieval improvement (the core value) without needing UI changes.
- **Proof:** Integration test showing multiple queries being executed in the retrieval loop.

## Technical Approach

- **Prompts:** Add `QUERY_REWRITING_PROMPT` to normalize shorthand into formal questions.
- **Services:** Update `QueryIntelligenceService` to expose the rewrite method and `AdvancedRetrievalService` to orchestrate the "Rewrite -> Hybrid Expand -> Merge" flow.
- **Merge Logic:** Utilize existing RRF merging in `AdvancedRetrievalService`.
- **UI:** Add checkbox to Sidebar and display `rewritten_query` in the debug panel.

## Requirements And Constraints

- **REQ-001 (Normalization):** Handled via new LLM prompt. Validated via unit test.
- **REQ-002 (Hybrid Pipeline):** Handled via list-based query orchestration. Validated via integration test.
- **REQ-003 (Traceability):** Schema update in `chat.py`. Validated via UI check.

## Impacted Areas

- **Services:** `QueryIntelligenceService`, `AdvancedRetrievalService`.
- **Schemas:** `AdvancedRetrievalConfig`, `RetrievalTransformations`.
- **UI:** `ChatScreen.jsx`, `AdvancedConfigPanel.jsx`.

## Execution Phases

### Phase 1: Backend Intelligence

Goal: Implement prompts and normalization logic.
Enabled outcome: Intent Formalization.
Entry proof: `prompts.py` does not contain `QUERY_REWRITING_PROMPT`.
Exit proof: `rewrite_query("cost?")` returns a formal question string.

### Phase 2: Pipeline Orchestration

Goal: Integrate rewriting into the retrieval flow.
Enabled outcome: Higher Quality Variations.
Entry proof: `AdvancedRetrievalService` uses only raw query as expansion seed.
Exit proof: Integration test shows variations generated for both raw and rewritten inputs.

### Phase 3: Schema & UI

Goal: Expose configuration and trace data.
Enabled outcome: Transparent Transformation.
Entry proof: `AdvancedRetrievalConfig` lacks `enable_rewriting`.
Exit proof: User can toggle rewriting and see the result in the Debug panel.

## Validation Strategy

- **TEST-001 (Unit):** `QueryIntelligenceService.rewrite_query` accuracy.
- **TEST-002 (Integration):** `AdvancedRetrievalService.retrieve` with hybrid loop logic.
- **TEST-003 (Manual):** UI verification of Debug panel and toggle behavior.

## Rollout Plan

- **Backend first:** Deploy logic and schemas.
- **Frontend second:** Enable UI toggle.

## Rollback Plan

- Set `enable_rewriting=False` by default; logic can be disabled without a code revert.

## Risks And Mitigations

- **RISK-001 Semantic Drift:** LLM might change intent.
  - Mitigation: The "Hybrid" strategy ensures the raw user keywords are always included in the final retrieval set.

## Open Questions

- Q-001: Should we limit the number of variations per seed?
  - Next step: Default to 2 variations per seed (Raw and Rewritten) to avoid overwhelming the vector DB.

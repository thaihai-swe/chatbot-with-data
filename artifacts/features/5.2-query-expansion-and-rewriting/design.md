# Technical Design: Query Expansion and Rewriting

## Metadata

- Feature name: Query Expansion and Rewriting
- Feature slug: 5.2-query-expansion-and-rewriting
- Related spec: `artifacts/features/5.2-query-expansion-and-rewriting/spec.md`
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16

## Design Summary

We will introduce a "Rewriting" step into the `AdvancedRetrievalService` pipeline. This step uses a standalone LLM prompt to normalize messy user queries into formal search questions. The rewritten query will then serve as an additional "seed" for expansion variations. Both the raw query and the rewritten query (plus their respective expansions) will be merged into a single retrieval candidate set using the existing Reciprocal Rank Fusion (RRF) logic.

## Current State And Context

- **Baseline:** `AdvancedRetrievalService` currently runs `raw_query`, `expanded_queries` (from raw), and `decomposition`.
- **Retrieval Loop:** It iterates through a list of query strings, retrieves chunks for each, and merges them.
- **Intelligence:** `QueryIntelligenceService` provides `expand_query`.

## Design Drivers

- **REQ-001 (Normalization):** 
  - Design implication: Create `QUERY_REWRITING_PROMPT` that ignores history.
- **REQ-002 (Hybrid Pipeline):**
  - Design implication: Modify the `retrieve` loop to generate variations for both raw and rewritten strings.
- **REQ-003 (Traceability):**
  - Design implication: Update `RetrievalTransformations` schema to store `rewritten_query`.

## Proposed Architecture

- **Prompts:** Add `QUERY_REWRITING_PROMPT` to `backend/chat/prompts.py`.
- **Services:**
  - `QueryIntelligenceService`: Add `rewrite_query(query_text)` method.
  - `AdvancedRetrievalService`: Update `retrieve` to call `rewrite_query` first if enabled.
- **Logic:**
  1. If `enable_rewriting`: `rewritten = rewrite_query(raw)`
  2. `queries_to_run = [raw, rewritten]`
  3. For each `q` in `queries_to_run`:
     - If `enable_expansion`: `queries_to_run.extend(expand_query(q))`
  4. Deduplicate `queries_to_run`.
  5. Execute retrieval for all.

## Data Flow And Interfaces

- **Config Update:** `AdvancedRetrievalConfig` adds `enable_rewriting: bool`.
- **Trace Update:** `RetrievalTransformations` adds `rewritten_query: Optional[str]`.
- **Internal Interface:** `rewrite_query` accepts a string and returns a string.

## Design Decisions And Tradeoffs

- **Decision: Sequential vs. Parallel Intelligence**
  - Why chosen: Sequential (Rewrite then Expand) ensures expansion benefits from the formalization of the rewrite.
  - Tradeoff: Adds latency. We will mitigate this by ensuring the Rewrite prompt is extremely concise.

- **Decision: Augmentation (Hybrid)**
  - Why chosen: Searching for both raw and rewritten queries prevents "over-formalization" from losing specific user keywords (like acronyms or product names) that the LLM might "clean away".
  - Tradeoff: More queries in the loop (RRF handles this well).

## Alternatives Considered

- **Alternative: Replace Raw with Rewritten**
  - Reason not chosen: Too risky; a bad rewrite could break retrieval entirely. Augmentation is a safer "no-regret" strategy.

## Non-Functional Design Considerations

- **Observability:** `RetrievalTrace` must reflect which variations came from which seed (Raw vs. Rewritten).
- **Performance:** Limit total variations to 5-7 to keep ChromaDB query time within bounds.

## Open Questions

- Q-001: Should we limit the number of variations per seed?
  - Next step: Yes, default to 2 per seed if both raw and rewritten are used.

# Technical Design: Advanced Retrieval Strategies and Routing

## Metadata

- Feature name: Advanced Retrieval Strategies and Routing
- Feature slug: advanced-retrieval-strategies-and-routing
- Related spec: `artifacts/features/4.advanced-retrieval-strategies-and-routing/spec.md`
- Related requirements review: `artifacts/features/4.advanced-retrieval-strategies-and-routing/requirements-review.md`
- Owner: Gemini CLI
- Status: Approved
- Last updated: 2026-05-06

## Design Summary

The design introduces a sophisticated retrieval orchestration layer that transforms a single user query into a series of strategic search operations. It leverages LLMs for pre-retrieval query intelligence (classification, expansion, decomposition, HyDE) and post-retrieval enhancement (reranking, parent-child expansion). A unified `RetrievalPipeline` coordinates these steps, ensuring all transformations are captured in a `RetrievalTrace` for observability.

## Current State And Context

- **Existing system baseline**: `RetrievalService` performs single-query embedding and vector search via ChromaDB.
- **Relevant repository patterns**: Service-based architecture with explicit dependency injection. Repositories handle persistence.
- **Brownfield constraints**: Must integrate with `ChatService` and respect the existing `document_collections` mapping.
- **Unchanged behavior**: Baseline grounded chat (Feature 3) remains the fallback path.

## Design Drivers

- **REQ-001 (Query Intelligence)**: Needs a classification and rewriting stage that preserves the original query.
- **REQ-002/003 (Expansion/Decomposition)**: Requires merging results from multiple retrieval calls.
- **REQ-007 (Reranking)**: Needs a pluggable reranker interface.
- **REQ-010 (Observability)**: Requires a structured "Trace" object to flow through the pipeline.
- **NFR-001 (Performance)**: Latency for each stage must be measured and reported.

## Proposed Architecture

### Major Components

1.  **`QueryIntelligenceService`**: Dedicated to LLM-powered query understanding and transformation.
2.  **`AdvancedRetrievalService`**: The entry point for Feature 4, orchestrating the pipeline.
3.  **`CandidateMerger`**: Handles result fusion (e.g., RRF) when multiple queries are executed.
4.  **`RerankingService`**: Interface for re-scoring candidates before generation.
5.  **`RetrievalTrace` (Data Model)**: Captures every decision, transformation, and score for the Debug View.

### Interaction Model

`ChatService` -> `AdvancedRetrievalService` -> [`QueryIntelligenceService`, `RetrievalService`, `RerankingService`, `CandidateMerger`]

## Data Flow And Interfaces

### Inputs and Entry Points

- **`AdvancedRetrievalService.retrieve(...)`**:
    - `query_text: str`
    - `config: AdvancedRetrievalConfig` (Enables/disables specific strategies)
    - `session_id: str` (For context)

### Internal Interfaces

- **`QueryIntelligenceService`**:
    - `generate_transformations(query, config) -> TransformationPackage`
- **`CandidateMerger`**:
    - `merge(results_list: List[List[Chunk]]) -> List[Chunk]` (Uses Reciprocal Rank Fusion)

### Retrieval Trace Structure

```json
{
  "original_query": "...",
  "classification": "multi-hop",
  "transformations": {
    "rewritten_query": "...",
    "expanded_queries": ["...", "..."],
    "sub_questions": ["...", "..."],
    "hyde_doc": "..."
  },
  "routing": {
    "selected_strategy": "hybrid",
    "reason": "..."
  },
  "retrieval_runs": [
    {"query": "...", "raw_count": 10, "top_scores": [...]}
  ],
  "merged_candidates_count": 25,
  "reranking": {
    "model": "cross-encoder-...",
    "pre_order": [...],
    "post_order": [...]
  }
}
```

## Design Decisions And Tradeoffs

- **Decision: Reciprocal Rank Fusion (RRF) for merging.**
  - **Why chosen**: RRF is effective at merging results from different search types (keyword vs. semantic) and multiple queries without needing calibrated scores.
  - **Tradeoff**: Slightly more complex to implement than simple score averaging, but much more robust.

- **Decision: Strategy Toggles via Config Object.**
  - **Why chosen**: Allows the UI to explicitly enable/disable features for comparison (HyDE vs. Expansion).
  - **Tradeoff**: Increases the number of parameters passed through services.

- **Decision: Automatic Collection Detection via Summary Matching.**
  - **Why chosen**: Matching query embeddings against collection descriptions/summaries is faster and cheaper than full LLM routing for every turn.
  - **Tradeoff**: May be less precise than a multi-step LLM reasoning agent.

## Alternatives Considered

- **Alternative: Sequential Agentic Retrieval.**
  - **Reason not chosen**: While powerful, a full "ReAct" style agent for retrieval might be too slow for a standard chat UI and harder to make perfectly observable in a teaching context. A structured pipeline is easier to visualize.

## Brownfield Integration Notes

- **Existing boundary to respect**: `RetrievalService` should remain as the low-level vector-search executor. `AdvancedRetrievalService` will call it.
- **Regression hotspot**: Merging logic could accidentally drop high-confidence candidates if not carefully tested.

## Non-Functional Design Considerations

- **Performance**: Each LLM transformation adds ~500ms-2s latency. The UI must support streaming or granular status updates.
- **Observability**: The `RetrievalTrace` is a first-class citizen, not just a log file.
- **Reliability**: If an LLM transformation fails, the pipeline MUST fall back to the original query.

## Open Questions

- **Q-001 Question**: Should we store the `RetrievalTrace` in SQLite for historical evaluation?
  - **Next step**: Yes, add a `retrieval_traces` table in Feature 6 (Evaluation), but keep it as a transient response field for now.

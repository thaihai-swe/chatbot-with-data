# Implementation Plan: Advanced Retrieval Strategies and Routing

## Metadata

- Feature name: Advanced Retrieval Strategies and Routing
- Feature slug: advanced-retrieval-strategies-and-routing
- Related spec: `artifacts/features/4.advanced-retrieval-strategies-and-routing/spec.md`
- Related requirements review: `artifacts/features/4.advanced-retrieval-strategies-and-routing/requirements-review.md`
- Related design: `artifacts/features/4.advanced-retrieval-strategies-and-routing/design.md`
- Owner: Gemini CLI
- Status: Draft
- Last updated: 2026-05-06

## Plan Summary

The implementation follows a phased approach to transform the current linear retrieval path into a modular, observable, and multi-stage pipeline. We will first establish the observability foundation (`RetrievalTrace`), then build out the LLM-powered query intelligence services, followed by multi-query merging logic, and finally the post-retrieval enhancements (reranking, parent-child expansion). The UI will be updated to expose these advanced features and provide a detailed debug view for inspection.

## Constitution Alignment

- **Grounded in evidence**: Every query transformation must remain a retrieval aid and never become evidence itself.
  - Planning implication: `RetrievalTrace` must clearly separate "transformed queries" from "retrieved source text."
- **Observability first**: Intermediate steps must be inspectable to fulfill the educational goal.
  - Planning implication: The `RetrievalTrace` object is passed through all services and returned to the UI.

## Execution Context

- **Design reference**: `artifacts/features/4.advanced-retrieval-strategies-and-routing/design.md`
- **Relevant repository patterns**: Python services with Pydantic schemas, FastAPI routers, and ChromaDB vector indexing.
- **Brownfield execution constraints**: Must maintain compatibility with the existing `ChatService` turn orchestration.
- **Unchanged behavior**: The baseline `RetrievalService` and `GenerationService` will continue to function as the core search and response components.

## Technical Approach

- **Chosen approach**: Modular Pipeline with a unified Trace object.
- **Architectural shape**: A wrapper service (`AdvancedRetrievalService`) that orchestrates multiple specialized services (`QueryIntelligence`, `CandidateMerger`, `Reranker`).
- **Key interfaces**:
    - `AdvancedRetrievalService.retrieve(...) -> (List[Chunk], RetrievalTrace)`
    - `QueryIntelligenceService.transform(query, config) -> TransformationPackage`
- **Operational considerations**: Increased token usage and latency due to multiple LLM calls.

## Decision Rationale

- **Why this approach**: It allows for a clean separation between "understanding the user" and "searching the data," while making every step inspectable for the "experimentation platform" requirement.
- **Existing patterns reused**: Service-oriented structure, dependency injection.
- **Alternatives considered**: Agentic loops (e.g., ReAct).
- **Why rejected**: Too unpredictable and harder to visualize in a structured debug view compared to a pipeline.

## Requirements And Constraints

- **REQ-001 (Intelligence)**: Implementation includes classification, rewriting, expansion, and decomposition.
- **REQ-007 (Reranking)**: Interface created for pluggable rerankers.
- **REQ-010 (Visibility)**: Success depends on the `RetrievalTrace` capturing all intermediate states.
- **NFR-001 (Latency)**: Each phase of the pipeline will log its execution time in the trace.

## Impacted Areas

- **Services**: `ChatService`, `RetrievalService` (as a caller), New `AdvancedRetrievalService`, `QueryIntelligenceService`, `RerankingService`.
- **APIs**: `POST /chat` and `POST /chat/sessions/{id}/turns` will need to accept `AdvancedRetrievalConfig`.
- **UI**: Chat Screen (Settings toggle, Debug View), New Strategy Comparison UI.

## Protected Behavior

- **Baseline grounded chat**: Must continue to work if all advanced features are disabled.
  - Protection approach: `AdvancedRetrievalService` will default to a passthrough to `RetrievalService` if config is empty.

## Affected Files

- `backend/chat/service.py`: To call the advanced retrieval pipeline.
- `backend/chat/retrieval.py`: To add the new pipeline and services.
- `backend/chat/prompts.py`: To add transformation prompts.
- `backend/schemas/chat.py`: To add `AdvancedRetrievalConfig` and `RetrievalTrace` schemas.
- `frontend/src/screens/ChatScreen.jsx`: To add settings and debug view.

## Dependencies

- **Feature 2**: Requires `parent_chunk_id` metadata to be present in index.
- **Feature 3**: Requires a working chat loop to integrate into.

## Implementation Phases

### Phase 1: Foundation and Traceability

Goal: Establish the schemas and the skeleton service that returns a trace.

Tasks:
- TASK-001: Define Pydantic schemas for `AdvancedRetrievalConfig` and `RetrievalTrace`.
- TASK-002: Create `AdvancedRetrievalService` skeleton with trace initialization.
- TASK-003: Update `ChatTurnResponse` to include the `retrieval_trace`.
- TASK-004: Integrate `AdvancedRetrievalService` into `ChatService.process_turn`.

### Phase 2: Query Intelligence (Pre-Retrieval)

Goal: Implement LLM-powered query transformations.

Tasks:
- TASK-005: Add LLM prompts for classification, expansion, decomposition, and HyDE to `prompts.py`.
- TASK-006: Implement `QueryIntelligenceService` with methods for all transformations.
- TASK-007: Implement "Automatic Collection Detection" by matching query to collection descriptions.
- TASK-008: Update `AdvancedRetrievalService` to call `QueryIntelligenceService` based on config.

### Phase 3: Multi-Query Retrieval and Merging

Goal: Handle multiple search runs and merge results.

Tasks:
- TASK-009: Implement `CandidateMerger` with Reciprocal Rank Fusion (RRF).
- TASK-010: Update `AdvancedRetrievalService` to iterate over expanded/decomposed queries and merge results.
- TASK-011: Implement deduplication and limit logic for merged candidates.

### Phase 4: Post-Retrieval and Routing

Goal: Implement reranking and parent-child expansion.

Tasks:
- TASK-012: Implement `RerankingService` (starting with a simple embedding-similarity reranker or placeholder for cross-encoder).
- TASK-013: Implement Parent-Child expansion logic (retrieve parent text if child chunk is selected).
- TASK-014: Implement Dynamic Routing logic to choose strategies based on classification.

### Phase 5: UI and Observability

Goal: Expose features to the user and visualize the pipeline.

Tasks:
- TASK-015: Add "Advanced Settings" toggle/menu to the Chat UI.
- TASK-016: Implement the "Debug View" drawer/modal to display the `RetrievalTrace`.
- TASK-017: (Optional but recommended) Add status indicators for pipeline steps (e.g., "Expanding query...", "Reranking...").

### Phase 6: Strategy Comparison UI

Goal: Fulfill the portfolio requirement for a comparison screen.

Tasks:
- TASK-018: Create the Strategy Comparison screen that runs the same query through multiple configurations and displays results side-by-side.

## Traceability Matrix

- **US-001 (Expansion/HyDE)** -> Phases 2 & 3
- **US-002 (Decomposition)** -> Phases 2 & 3
- **US-003 (Compare Routing/Reranking)** -> Phases 4 & 6
- **US-005 (Parent-Child)** -> Phase 4
- **REQ-010 (Visibility)** -> All phases via `RetrievalTrace`

## Rollout Plan

- **Release approach**: Internal feature toggle or explicitly requested via API payload.
- **Backward compatibility**: `AdvancedRetrievalConfig` will be optional in API schemas, defaulting to "baseline" behavior.

## Rollback Plan

Revert `ChatService` to call `RetrievalService` directly instead of `AdvancedRetrievalService`.

## Risks And Mitigations

- **RISK-001 (High Latency)**: Multiple LLM calls can make the UI feel slow.
  - Mitigation: Inform the user of progress via status updates; ensure each transformation has a reasonable timeout.
- **RISK-002 (Increased Cost)**: More tokens used for intelligence.
  - Mitigation: Allow users to selectively enable features; provide a "Token Usage" summary in the trace.

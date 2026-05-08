# Implementation Plan: Advanced Retrieval Strategies and Routing

## Metadata

- Feature name: Advanced Retrieval Strategies and Routing
- Related spec: `artifacts/features/4.advanced-retrieval-strategies-and-routing/spec.md`
- Related requirements review: `artifacts/features/4.advanced-retrieval-strategies-and-routing/requirements-review.md`
- Related design: `artifacts/features/4.advanced-retrieval-strategies-and-routing/design.md`
- Owner: Gemini CLI
- Status: Approved
- Last updated: 2026-05-08

## Plan Summary

The implementation follows a phased approach to transform the current linear retrieval path into a modular, observable, and multi-stage pipeline. We will first establish the observability foundation (`RetrievalTrace`), then build out the LLM-powered query intelligence services, followed by multi-query merging logic, and finally the post-retrieval enhancements (reranking, parent-child expansion). The UI will be updated to expose these advanced features and provide a detailed debug view for inspection.

## Constitution Alignment

- Constitutional rule or principle: Grounded in evidence
  Planning implication: Every query transformation must remain a retrieval aid and never become evidence itself. `RetrievalTrace` must clearly separate "transformed queries" from "retrieved source text."
- Constitutional rule or principle: Observability first
  Planning implication: Intermediate steps must be inspectable to fulfill the educational goal. The `RetrievalTrace` object is passed through all services and returned to the UI.

## Execution Context

- Design reference: `artifacts/features/4.advanced-retrieval-strategies-and-routing/design.md`
- Relevant repository patterns for execution: Python services with Pydantic schemas, FastAPI routers, and ChromaDB vector indexing. Service-oriented architecture with dependency injection.
- Brownfield execution constraints or greenfield assumptions: Must maintain compatibility with the existing `ChatService` turn orchestration and use existing `document_collections` mapping.
- Unchanged behavior that must be preserved during delivery: The baseline `RetrievalService` and `GenerationService` will continue to function as the core search and response components when advanced strategies are not explicitly enabled.

## Technical Approach

- Chosen approach: Modular Pipeline with a unified Trace object.
- Architectural or integration shape: A wrapper service (`AdvancedRetrievalService`) that orchestrates multiple specialized services (`QueryIntelligenceService`, `CandidateMerger`, `RerankingService`).
- Key interfaces or contracts: 
  - `AdvancedRetrievalService.retrieve(query, config) -> (List[Chunk], RetrievalTrace)`
  - `QueryIntelligenceService.generate_transformations(query, config) -> TransformationPackage`
- Operational considerations: Increased token usage and latency due to multiple LLM calls per turn. Needs appropriate timeout handling and user feedback.

## Decision Rationale

- Why this approach was selected: Allows clean separation between user understanding and data searching while making every step inspectable. A structured pipeline is easier to trace and visualize than agentic loops.
- Existing patterns reused: Service-oriented structure, Pydantic data models for configuration.
- Alternatives considered: Sequential Agentic Retrieval (e.g., ReAct).
- Why rejected: Agentic loops are too unpredictable and harder to visualize in a structured debug view compared to a defined pipeline.

## Requirements And Constraints

- REQ-001: Pre-retrieval query intelligence
  Implementation note: Requires prompt engineering for classification and query rewriting.
  Planned validation: Inspect trace for generated query variants and routing signals.
  Linked scenario or outcome: US-001, US-002, US-003, US-004
- REQ-002: LLM-based query expansion
  Implementation note: Will generate 3-5 variations and requires candidate merging (RRF).
  Planned validation: Trace shows multiple queries and deduplicated merged results.
  Linked scenario or outcome: US-001, US-003
- REQ-003: Query decomposition
  Implementation note: Track sub-questions and their respective retrieved chunks.
  Planned validation: Trace details sub-questions and mapped evidence.
  Linked scenario or outcome: US-002, US-003
- REQ-004: HyDE
  Implementation note: Generate hypothetical document and embed it for retrieval.
  Planned validation: Verify hypothetical text is in trace but never in final cited context.
  Linked scenario or outcome: US-001, US-003
- REQ-005: Synonym expansion
  Implementation note: Map synonyms before retrieval.
  Planned validation: Trace logs applied synonym changes.
  Linked scenario or outcome: US-001, US-003
- REQ-006: Dynamic routing
  Implementation note: Route based on query characteristics or configured policy.
  Planned validation: Check route, reason, and fallback in trace.
  Linked scenario or outcome: US-003, US-004
- REQ-007: Configurable rerankers
  Implementation note: Start with cross-encoder or embedding-similarity reranker.
  Planned validation: Compare pre-rerank and post-rerank ordering in trace.
  Linked scenario or outcome: US-003
- REQ-008: Parent-child retrieval modes
  Implementation note: Retrieve parent chunk if child is matched. Needs `parent_chunk_id`.
  Planned validation: Validate child evidence with parent expansion in trace.
  Linked scenario or outcome: US-005
- REQ-009: Automatic collection detection
  Implementation note: Infer scope via embeddings or metadata if not user-selected.
  Planned validation: Verify collection selection reason and confidence in trace.
  Linked scenario or outcome: US-004
- REQ-010: Advanced retrieval pipeline observability
  Implementation note: The `RetrievalTrace` object must capture all states.
  Planned validation: End-to-end debug view inspection in UI.
  Linked scenario or outcome: US-001, US-002, US-003, US-004, US-005
- NFR-001:
  Implementation note: Expose added latency per stage in trace.
- CON-001:
  Impact on plan: Feature behavior and components must not alter core RAG fallback if omitted.

## Impacted Areas

- Services or modules: `ChatService`, `RetrievalService`, new `AdvancedRetrievalService`, `QueryIntelligenceService`, `RerankingService`.
- APIs or interfaces: `/chat` endpoints need `AdvancedRetrievalConfig` payload and response updates.
- Data model or storage: Pydantic schemas for Config and Trace.
- UI or UX: Chat screen settings toggle, Debug View drawer.
- Infrastructure or deployment: Potential new ML model dependencies for reranking.
- Documentation: Update API docs for new config parameters.

## Affected Domains And Integration Boundaries

- Domain or subsystem: Chat Turn Orchestration
  Why it matters: Must weave advanced retrieval seamlessly into the existing grounded chat turn without breaking streaming or citations.
- Integration boundary or touchpoint: Vector Database (ChromaDB)
  Why it matters: Multiple queries and parent-child expansion mean more complex query patterns against the index.

## Protected Behavior

- Behavior that must not regress: Baseline grounded chat
  Protection approach: `AdvancedRetrievalService` acts as a passthrough to `RetrievalService` if advanced features are disabled or config is empty.

## Affected Files

- FILE-001 Path: `backend/chat/service.py`
  Reason for change: To route to `AdvancedRetrievalService` instead of `RetrievalService` when config is present.
- FILE-002 Path: `backend/chat/retrieval.py`
  Reason for change: To implement the new pipeline and services.
- FILE-003 Path: `backend/chat/prompts.py`
  Reason for change: To add transformation and intelligence prompts.
- FILE-004 Path: `backend/schemas/chat.py`
  Reason for change: To add `AdvancedRetrievalConfig` and `RetrievalTrace` schemas.
- FILE-005 Path: `frontend/src/screens/ChatScreen.jsx`
  Reason for change: To add settings and debug view.

## Dependencies

- DEP-001 Internal dependency: Chunking and Indexing Foundation (Feature 2)
  Why it matters: Parent-child expansion requires `parent_chunk_id` metadata to be present in the index.
- DEP-002 Internal dependency: Grounded Chat and Citations (Feature 3)
  Why it matters: Needs a working chat loop and citation mechanism to integrate into and augment.

## Implementation Prerequisites

- PREREQ-001: Features 2 and 3 must be merged and stable.
- PREREQ-002: Parent-child chunking metadata must exist in test collections.

## Implementation Phases

### Phase 1

Goal: Establish the schemas and the skeleton service that returns a trace.
Enabled user scenario(s) or outcome(s): Base pipeline capable of recording metadata for downstream UI.

Tasks:

- TASK-001:
  Description: Define Pydantic schemas for `AdvancedRetrievalConfig` and `RetrievalTrace`.
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s): `backend/schemas/chat.py`
- TASK-002:
  Description: Create `AdvancedRetrievalService` skeleton with trace initialization and integrate into `ChatService.process_turn`.
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s): `backend/chat/service.py`, `backend/chat/retrieval.py`

Completion criteria:

- CC-001: Chat endpoints accept the new config and return an empty or baseline trace without breaking existing chat tests.

### Phase 2

Goal: Implement LLM-powered query transformations and classification.
Enabled user scenario(s) or outcome(s): US-001, US-002, US-004

Tasks:

- TASK-003:
  Description: Add LLM prompts for classification, expansion, decomposition, synonym expansion, and HyDE.
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s): `backend/chat/prompts.py`
- TASK-004:
  Description: Implement `QueryIntelligenceService` with methods for all transformations and wire it to `AdvancedRetrievalService`.
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-003
  Affected file(s): `backend/chat/retrieval.py`
- TASK-005:
  Description: Implement Automatic Collection Detection logic based on query classification and collection metadata.
  Linked requirement(s): REQ-009
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/chat/retrieval.py`

Completion criteria:

- CC-002: `QueryIntelligenceService` can successfully generate trace metadata for all transformation types when enabled via config.

### Phase 3

Goal: Handle multiple search runs and merge results logically.
Enabled user scenario(s) or outcome(s): US-001, US-002

Tasks:

- TASK-006:
  Description: Implement `CandidateMerger` using Reciprocal Rank Fusion (RRF) and deduplication logic.
  Linked requirement(s): REQ-002, REQ-003, REQ-010
  Linked acceptance criteria: AC-001, AC-002, AC-006
  Affected file(s): `backend/chat/retrieval.py`
- TASK-007:
  Description: Update `AdvancedRetrievalService` to loop over expanded/decomposed queries, run retrieval for each, and merge via `CandidateMerger`.
  Linked requirement(s): REQ-002, REQ-003
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s): `backend/chat/retrieval.py`

Completion criteria:

- CC-003: System can run 5 expanded queries and return a correctly deduplicated and RRF-scored top-K chunk list in the trace.

### Phase 4

Goal: Implement dynamic routing, reranking, and parent-child expansion.
Enabled user scenario(s) or outcome(s): US-003, US-005

Tasks:

- TASK-008:
  Description: Implement Dynamic Routing logic to select retrieval paths based on classification output.
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/chat/retrieval.py`
- TASK-009:
  Description: Implement `RerankingService` and wire it into the pipeline.
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-003
  Affected file(s): `backend/chat/retrieval.py`
- TASK-010:
  Description: Implement Parent-Child expansion logic (fetching parent context based on child match).
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-005
  Affected file(s): `backend/chat/retrieval.py`

Completion criteria:

- CC-004: Trace validates that reranking reorders candidates and parent chunks are successfully fetched.

### Phase 5

Goal: Expose features to the user and visualize the pipeline.
Enabled user scenario(s) or outcome(s): US-001, US-002, US-003, US-004, US-005

Tasks:

- TASK-011:
  Description: Add "Advanced Settings" toggle/menu to the Chat UI to configure `AdvancedRetrievalConfig`.
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s): `frontend/src/screens/ChatScreen.jsx`
- TASK-012:
  Description: Implement the "Debug View" drawer/modal to display the full `RetrievalTrace`.
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-006
  Affected file(s): `frontend/src/screens/ChatScreen.jsx`

Completion criteria:

- CC-005: User can toggle advanced features on/off from UI and visually inspect the Trace for any turn.

## Traceability Matrix

- Scenario or outcome -> Plan phase(s):
  - US-001 -> Phase 2, 3, 5
  - US-002 -> Phase 2, 3, 5
  - US-003 -> Phase 4, 5
  - US-004 -> Phase 2, 4, 5
  - US-005 -> Phase 4, 5
- REQ-001 -> Phase 2 / TASK-003, TASK-004
- REQ-002 -> Phase 3 / TASK-006, TASK-007
- REQ-003 -> Phase 3 / TASK-006, TASK-007
- REQ-004 -> Phase 2 / TASK-003, TASK-004
- REQ-005 -> Phase 2 / TASK-003, TASK-004
- REQ-006 -> Phase 4 / TASK-008
- REQ-007 -> Phase 4 / TASK-009
- REQ-008 -> Phase 4 / TASK-010
- REQ-009 -> Phase 2 / TASK-005
- REQ-010 -> Phase 1, Phase 5 / TASK-001, TASK-002, TASK-011, TASK-012
- AC-001 -> Phase 2, Phase 3 validation steps
- AC-002 -> Phase 3 validation steps
- AC-003 -> Phase 2, Phase 4 validation steps
- AC-004 -> Phase 2, Phase 4 validation steps
- AC-005 -> Phase 4 validation steps
- AC-006 -> Phase 1, Phase 5 validation steps

## Rollout Plan

- Release approach: Internal feature toggle or configured explicitly per chat session.
- Feature flags: Add an explicit "Enable Advanced Retrieval" toggle in the environment or UI.
- Migration needs: None. `AdvancedRetrievalConfig` will be optional in existing endpoints.
- Backward compatibility notes: Existing chat flows will use an empty config and bypass the advanced pipeline.

## Rollback Plan

Describe how to revert or disable the change safely.
Revert `ChatService` to call the baseline `RetrievalService` directly instead of `AdvancedRetrievalService`, ignoring any `AdvancedRetrievalConfig` passed in.

## Risks And Mitigations

- RISK-001 Risk: Multiple LLM calls for intelligence/transformations make the UI feel slow.
  Mitigation: Stream status updates to the UI, allow parallel LLM calls where possible, and provide configurable timeouts.
- RISK-002 Risk: Automatic collection routing may hide relevant evidence if confidence is overstated.
  Mitigation: Implement a strict confidence threshold and low-confidence fallback behavior. Ensure routing decisions are highly visible in the Debug View.

## Open Questions

- Q-001 Question: Should dynamic routing be automatic by default once available, or default-off until users explicitly opt into strategy automation?
  Next step: Default to off (opt-in via config) for initial rollout to prevent surprising legacy users, and resolve product decision during beta.

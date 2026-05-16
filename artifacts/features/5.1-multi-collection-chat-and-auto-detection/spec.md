# Feature Specification: Multi-Collection Chat and Auto-Detection

## Metadata

- Feature name: Multi-Collection Chat and Auto-Detection
- Feature slug: 5.1-multi-collection-chat-and-auto-detection
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16
- Related knowledge artifact(s): `prd-requirement.md`, `artifacts/features/4.advanced-retrieval-strategies-and-routing/spec.md`

## Problem Statement

Currently, a chat session is restricted to either a single collection or all collections. Users often need to scope their questions to a specific subset of documents (e.g., "Legal" AND "Compliance") without searching the entire knowledge base. Additionally, when a user is unsure which collection to pick, the system should intelligently route the query to the most relevant collections automatically.

## Desired Outcomes

- Users can select multiple collections when starting or configuring a chat session.
- Retrieval is accurately scoped to the union of selected collections.
- If no collections are selected, the system can automatically detect and use the most relevant collections based on the query.

## Success Criteria

- SC-001: Chat UI allows multi-selecting collections from the available list.
- SC-002: Backend correctly filters retrieval results to only include chunks from any of the selected collections.
- SC-003: When "Auto Collection Detection" is enabled and no collections are manually selected, the system identifies the relevant collections via LLM and uses them for retrieval.
- SC-004: The selected or auto-detected collections are visible in the chat metadata/trace.

## In Scope

- Frontend UI update for multi-collection selection in the sidebar.
- Backend database schema update to support multiple collections per session.
- Backend API update for session creation and update to accept a list of collection IDs.
- Retrieval logic update to handle a list of collection IDs in the filter.
- Refinement of auto-detection logic to potentially return multiple collections.
- Traceability: Showing which collections were used in the retrieval trace.

## Out Of Scope

- Cross-collection deduplication beyond existing RRF merging.
- User-defined collection groups (named sets of collections).

## Users And Stakeholders

- Primary users: Analysts and researchers managing large, diverse document sets.
- Secondary stakeholders: Developers testing routing accuracy and retrieval recall.

## User Stories And Key Scenarios

- **US-001: Manual Multi-Selection.** As a user, I want to select 'Project A' and 'Project B' collections so that my answer only uses those specific sources.
- **US-002: Auto-Detection.** As a user, I want to ask a question without picking a collection, and have the system find the right one for me.
- **US-003: Overriding Auto-Detection.** As a user, I want to see which collections were auto-detected and be able to manually override them if they are wrong.

## Current Context

- `ChatSession` model currently has an optional `collection_id` (string).
- `RetrievalService` accepts `collection_id: Optional[str]`.
- `ChromaVectorWriter` uses a `where` filter with `$eq` for single collection IDs.
- `AdvancedRetrievalService` has a stub for `auto_collection_detection` that uses `QueryIntelligenceService.detect_collection`.

## Dependencies And External Touchpoints

- DEP-001: `AdvancedRetrievalService` (Feature 4) which provides the hook for `auto_collection_detection`.
- DEP-002: `ChromaVectorWriter` which must be updated to support `$in` filters for metadata.

## Functional Requirements

### REQ-001: Multi-Collection Session Storage
Requirement: The system must support associating a chat session with zero, one, or multiple collections.
Why it matters: Enables flexible scoping of RAG context.
Impacted users or scenarios: US-001.
Priority: Must Have.
Acceptance notes: Database must store a list of IDs for each session, likely via a new mapping table.

### REQ-002: Multi-Collection Retrieval Filter
Requirement: The retrieval pipeline must support filtering by multiple collection IDs simultaneously.
Why it matters: Ensures answers are grounded only in the user-selected scope.
Impacted users or scenarios: US-001, US-002.
Priority: Must Have.
Acceptance notes: Chunks retrieved must belong to one of the selected collections.

### REQ-003: Enhanced Auto-Detection
Requirement: If `auto_collection_detection` is enabled and no collections are selected, the system must use LLM intelligence to select the most relevant collection(s).
Why it matters: Improves user experience by removing the need for manual routing.
Impacted users or scenarios: US-002.
Priority: Must Have.
Acceptance notes: Trace must show "auto-detected" status and the reasoning.

### REQ-004: UI Multi-Select
Requirement: The Chat sidebar/settings must provide a multi-select interface for collections.
Why it matters: Essential for user control.
Impacted users or scenarios: US-001, US-003.
Priority: Must Have.
Acceptance notes: User can toggle collections on/off.

## Non-Functional Requirements

- NFR-001 Performance: Auto-detection should add minimal latency (target < 500ms for detection step).
- NFR-005 Observability: The retrieval trace must clearly list all collection IDs used in the filter.

## Constraints

- Technical constraints: Must use existing SQLite and ChromaDB backend.
- Backwards compatibility: Existing single-collection sessions should be migrated or handled gracefully.

## Assumptions

- ASM-001: ChromaDB supports `$in` for metadata filtering.

## Open Questions

- Q-001: Should auto-detection pick multiple collections or just the "best" one?
  - Decision: For initial implementation, we will allow picking multiple if the prompt supports it, but the current logic picks one. We will design the data structure for a list.

## Acceptance Criteria

- [ ] AC-001: Start a new chat, select two specific collections, ask a question, and verify citations only come from those two collections.
- [ ] AC-002: Start a new chat with NO collections selected but "Auto-Detection" ON. Verify the system picks the correct collection for a specific query.
- [ ] AC-003: Verify that existing single-collection sessions still work correctly after the migration.
- [ ] AC-004: Retrieval trace shows the list of collections searched.

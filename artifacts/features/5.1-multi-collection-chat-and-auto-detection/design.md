# Technical Design: Multi-Collection Chat and Auto-Detection

## Metadata

- Feature name: Multi-Collection Chat and Auto-Detection
- Feature slug: 5.1-multi-collection-chat-and-auto-detection
- Related spec: `artifacts/features/5.1-multi-collection-chat-and-auto-detection/spec.md`
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16

## Design Summary

This design introduces the ability for users to scope chat sessions to multiple document collections. We will evolve the database schema to support a many-to-many relationship between sessions and collections, update the retrieval pipeline to use multi-value metadata filters in ChromaDB, and enhance the frontend UI with a multi-select interface. Additionally, we will refine the LLM-powered collection detection to return a list of relevant collections when no manual choice is made.

## Current State And Context

- **Existing system baseline:** `ChatSession` stores a single optional `collection_id`. Retrieval filters for exactly one ID (or none).
- **Relevant repository patterns:** Many-to-many relationships are managed via mapping tables (e.g., `document_collections`, `ingestion_attempt_collections`).
- **Brownfield constraints:** We must maintain compatibility with existing sessions that only have a single `collection_id` or `None`.
- **Unchanged behavior:** Baseline retrieval performance and safety checks must be preserved.

## Design Drivers

- **REQ-001 (Multi-Collection Storage):** 
  - Design implication: Add `chat_session_collections` table to SQLite.
- **REQ-002 (Multi-Collection Filter):**
  - Design implication: Update `ChromaVectorWriter.query` to use the `$in` operator for metadata filtering.
- **REQ-003 (Enhanced Auto-Detection):**
  - Design implication: Update `QueryIntelligenceService` to prompt for a list of relevant IDs and parse them into a list.
- **REQ-004 (UI Multi-Select):**
  - Design implication: Use a checkbox-based list or multi-select dropdown in the chat sidebar.

## Proposed Architecture

- **SQLite Schema:** Add `chat_session_collections (session_id, collection_id)` table.
- **Backend Services:**
    - `ChatRepository`: Methods to associate/list collections for a session.
    - `RetrievalService`: Update `retrieve_relevant_chunks` to accept `collection_ids: List[str]`.
    - `QueryIntelligenceService`: Refined `detect_collections` (plural) logic.
- **Interaction Model:**
    - Session Creation: User picks 0..N collections.
    - Retrieval: If 0 picked and "Auto" is ON -> Detect -> Filter by detected.
    - Retrieval: If N picked -> Filter by the N IDs.
    - Retrieval: If 0 picked and "Auto" is OFF -> Search across all collections.

## Data Flow And Interfaces

- **API Change:** `POST /chat/sessions` payload `collection_id` (str) -> `collection_ids` (List[str]).
- **Internal Interface:** `AdvancedRetrievalService.retrieve` signature update to handle list of IDs.
- **ChromaDB:** `where` filter becomes `{"collection_id": {"$in": [...]}}`.

## Design Decisions And Tradeoffs

- **Decision: Mapping Table vs. JSON String in `chat_sessions`**
  - Why chosen: Mapping table (`chat_session_collections`) follows the existing project pattern for collections and allows for SQL-native joins and constraints.
  - Tradeoff: Slightly more complex migrations and repository code compared to a JSON field.

- **Decision: ChromaDB `$in` Filter**
  - Why chosen: It's the native way to perform set-based filtering in Chroma and avoids multiple sequential queries.
  - Tradeoff: If the list is extremely large (e.g., hundreds of collections), performance might dip, but for typical use (2-5 collections), it is optimal.

## Alternatives Considered

- **Alternative: Comma-separated string in `collection_id`**
  - Reason not chosen: Brittle, hard to query, and breaks foreign key integrity.
- **Alternative: Multiple sequential retrieval runs (one per collection)**
  - Reason not chosen: High latency and complex merging logic (RRF would need to handle vastly different score distributions).

## Brownfield Integration Notes

- **Migration:**
    - Create `chat_session_collections`.
    - Data migration: For every `chat_session` where `collection_id` is NOT NULL, insert a row into the new mapping table.
    - Keep `collection_id` column in `chat_sessions` temporarily (marked as deprecated) or drop it after migration.
- **Backward Compatibility:** `ChatSessionResponse` should likely return `collection_ids` as a list, even if it only contains one item.

## Non-Functional Design Considerations

- **Observability:** Update `RetrievalRouting` schema to include `selected_collections: List[str]` and `detection_reason`.
- **UX Consistency:** The multi-select UI should match the "modern glassmorphism" aesthetic of the existing app.

## Open Questions

- **Q-001: Should we allow "All Collections" to be a special flag or just an empty list?**
  - Next step: Plan to treat empty list as "Search All" unless auto-detection is enabled.
- **Q-002: How to handle auto-detection when the user HAS selected some collections?**
  - Next step: Spec says auto-detection triggers when *no* collections are selected. We will stick to this for simplicity.

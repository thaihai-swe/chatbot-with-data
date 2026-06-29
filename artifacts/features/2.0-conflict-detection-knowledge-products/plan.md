# Implementation Plan: Conflict Detection & Knowledge Products

## Metadata

- Feature name: Conflict Detection & Knowledge Products
- Related spec: [spec.md](artifacts/features/2.0-conflict-detection-knowledge-products/spec.md)
- Related requirements review: None
- Owner: Antigravity
- Status: Draft
- Last updated: 2026-06-28

---

## Part 1: Technical Design

### Comprehensive Design

#### Design Summary
This feature introduces two key capabilities:
1. **Conflict Verification:** A post-processing check inside the chat generation pipeline that evaluates whether retrieved sources contradict each other, and if so, whether the generated answer correctly surfaced that contradiction.
2. **Studio Knowledge Products:** An API endpoint interface to generate synthesized research materials (Study Guides, Briefing Docs, FAQs, Timelines, Glossaries, and Flashcards) for any document collection, using pre-computed summaries with dynamic chunk summaries as fallbacks.

#### Current State
- The chat turn orchestrator (`backend/chat/service.py`) coordinates safety, retrieval, generation, and citation.
- System prompt templates contain optional slots for conflict instructions, but no verification runs on the response.
- `documents.metadata_json` optionally stores `doc_understanding` summaries generated during ingestion.
- The `collections` API router has no routes for document synthesis or study aids.

#### Proposed Architecture
- **`ConflictDetectionService` (`backend/chat/conflict.py`):**
  - Evaluates the generated answer against the retrieved chunks when unique document count > 1.
  - Sends a specialized prompt to the LLM to identify contradictions and check if the answer addressed them.
  - Returns `{"has_conflict": bool, "surfaced_correctly": bool, "details": str}`.
- **`KnowledgeProductService` (`backend/chat/knowledge_products.py`):**
  - Coordinates synthesis requests for Study Guide, Briefing Doc, FAQ, Timeline, Glossary, and Flashcards.
  - Fetches collection documents and extracts `doc_understanding` metadata.
  - If a document lacks `doc_understanding`, it queries Weaviate/SQLite for the first 3 chunks and generates a summary on the fly.
  - Compiles summaries and topics, sending them to the target product prompt template.
- **Router `/collections/{collection_id}/generate/...` (`backend/routers/generate.py`):**
  - Mounts collection-specific POST endpoints for generating products.
  - Registered in `backend/main.py` or imported in `backend/routers/__init__.py`.

#### Data Flow & Interfaces
- **Conflict Checking flow:**
  ```
  LLM generates answer_text → Check unique doc IDs retrieved →
  If > 1, call ConflictDetectionService.detect_conflict() →
  Store results in chat_turns.metadata_json under 'conflict_trace' →
  Map result to 'conflict_status' ("no_conflict", "resolved_conflict", "unresolved_conflict") →
  Return in ChatTurnResponse
  ```
- **Knowledge Product flow:**
  ```
  POST /collections/{id}/generate/study-guide →
  Get collection member documents → Extract summaries (or generate fallsback) →
  Format prompt → LLM synthesis → Return Markdown response
  ```

#### Key Decisions & Tradeoffs
- **Metadata Persistence:** Storing conflict detection results inside the `chat_turns.metadata_json` field prevents database migrations and maintains complete schema stability.
- **On-the-Fly Summarization Fallback:** Building summaries dynamically from the first 3 chunks of un-summarized documents prevents execution crashes while avoiding loading the entire document text (saving tokens).

#### Non-Functional Considerations
- **LLM Latency:** Executing the conflict check sequentially after answer generation adds 500-800ms of latency. We mitigate this by bypassing the check entirely when retrieved chunks originate from a single document.
- **Token Budget:** Knowledge products synthesize all documents in a collection. By using summaries rather than raw chunks, we keep the prompt context well within typical GPT-4o window limits.

#### Protected Behavior
- The 3-layer safety pipeline in `backend/chat/safety.py` must run first for all queries.
- Existing citation formats (`[Source N]`) and citation quote extraction logic must remain functional.

---

## Part 2: Delivery Strategy

### Execution Context
- Delivery profile: Moderate
- Locked spec decisions:
  - Generate study materials on-demand without database storage.
  - Return Flashcards as a JSON array of Q/A pairs.
  - Expose unresolved conflicts in UI via warnings instead of regenerating.

### First Delivery Slice
- **Smallest useful slice:** The Conflict Detection Service and its validation prompt.
- **Why this slice goes first:** Post-processing verification is a critical quality layer that can be implemented and unit-tested without any changes to API routes or frontend screens.
- **What proof should exist when this slice is done:** A passing unit test suite `pytest backend/tests/chat/test_conflict.py`.

### Execution Phases

#### Phase 1: Conflict Detection
- **Goal:** Implement the conflict detection service and integrate it into the chat turn workflow.
- **Enabled outcomes:** Turns identify source disagreements.
- **Entry proof:** spec.md exists and is approved.
- **Exit proof:** Unit tests pass for conflict check with mock LLM responses.
- **Completion criteria:** `backend/chat/conflict.py` exists, `ChatService` and `StreamingOrchestrator` call it, and `ChatTurnResponse` includes `conflict_status`.

#### Phase 2: Knowledge Products Generator
- **Goal:** Create the `KnowledgeProductService` and add API endpoints.
- **Enabled outcomes:** Study tools generated for collections.
- **Entry proof:** Phase 1 complete.
- **Exit proof:** Endpoints return well-formatted Markdown documents and parseable Flashcard JSON arrays.
- **Completion criteria:** `backend/chat/knowledge_products.py` and `backend/routers/generate.py` implemented.

#### Phase 3: Frontend Integration
- **Goal:** Wire up the frontend to show conflict warnings and render study guide generation UI.
- **Enabled outcomes:** User gets warning badges and triggers study tool generation.
- **Entry proof:** Phase 2 complete.
- **Exit proof:** UI renders warning messages for turns with `unresolved_conflict` status.

### Validation Strategy
- **Unit tests:** `backend/tests/chat/test_conflict.py` (mock LLM conflict evaluations) and `backend/tests/generate/test_products.py` (mock LLM product generation).
- **Manual verification:** Ingest conflicting documents, ask query, verify UI alert triggers. Generate FAQ for collection and review markdown structure.

### Traceability Matrix
- Scenario 1 (surfaced conflict) -> Phase 1
- Scenario 2 (ignored conflict warning) -> Phase 1 & 3
- Scenario 3 (flashcard generation) -> Phase 2
- Scenario 4 (incomplete metadata fallback) -> Phase 2
- REQ-001 -> Phase 1, task TASK-001
- REQ-002 -> Phase 1, task TASK-002
- REQ-003 -> Phase 2, task TASK-003
- REQ-004 -> Phase 2, task TASK-004

### Rollout Plan
- **Release approach:** Additive API changes. Backwards compatible.
- **Migration needs:** None.

### Rollback Plan
- Revert router registration and delete services.

### Risks And Mitigations
- **RISK-001 Prompt Injection:** Untrusted source text in collections. Mitigated by prompt constraints in the generator system prompts.

### Open Questions
None.

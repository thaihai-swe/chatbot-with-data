# Spec: Conflict Detection & Knowledge Products

## Metadata

- Feature name: Conflict Detection & Knowledge Products
- Feature slug: 2.0-conflict-detection-knowledge-products
- Delivery profile: Moderate
- Owner: Antigravity
- Status: Draft
- Last updated: 2026-06-28
- Related knowledge artifact(s): [analysis.md](artifacts/features/2.0-conflict-detection-knowledge-products/analysis.md)

## Problem Statement

Users of RAG systems can be misled when retrieved documents contain conflicting facts (e.g., Document A says revenue is $10M, Document B says it is $12M). If the LLM silently chooses one document or blends them, the user remains unaware of the source contradiction. Additionally, synthesizing multiple documents into study aids (Study Guides, Briefings, FAQs, Timelines, Glossaries, Flashcards) currently requires the user to execute complex, multi-turn chat prompts. Automating this synthesis at the collection level makes the system a full-featured research assistant.

## Desired Outcomes

- **Outcome 1:** Programmatically identify when sources contain conflicting claims.
- **Outcome 2:** Flag instances where the chat response failed to surface an active source conflict.
- **Outcome 3:** Generate study materials (markdown products and interactive JSON flashcards) directly from a collection's document metadata on-demand.

## Minimum Release Slice

- **What ships in the first useful release:**
  - Conflict checking post-processing step during chat turn processing.
  - Endpoints to generate Study Guides, Briefing Docs, FAQs, Timelines, Glossaries, and Flashcards for a collection.
  - Display of an "Unresolved Conflict" warning badge in the Chat UI when conflicts are missed.
- **What can wait:**
  - Persistent storage of generated knowledge products in SQLite.
  - In-place editing of generated study products.

## Success Criteria

- **SC-001:** The system successfully detects contradictions in retrieved documents and flags them when the generated answer ignores them.
- **SC-002:** The system generates study products for any collection, degrading gracefully if some documents lack pre-computed summaries.

## In Scope

- Post-generation conflict check inside the backend chat pipeline.
- 6 new API endpoints under the `/collections/{collection_id}/generate/...` route.
- Warnings rendered on the frontend chat screen for turns with unresolved conflicts.
- SSE token streaming is unaffected (conflict check runs synchronously at the end of the stream).

## Out Of Scope

- Audio/podcast generation, slideshow exports, and video briefing features.
- Multi-collection synthesis (products are scoped to a single collection).

## Non-Goals

- Attempting to resolve the conflict (e.g., deciding which source is "correct").
- Automatically regenerating the answer when a conflict is missed (to avoid infinite loops and high latency).

## Users And Stakeholders

- **Primary users:** Researchers, students, and analysts synthesizing multiple long sources.

## User Stories And Key Scenarios

### US-001: Source Conflict Alerting
As a researcher, I want to be alerted if my sources contain conflicting claims and the chatbot failed to mention this disagreement in its answer.

#### Detailed Scenarios

- **Scenario 1: Conflict correctly surfaced by LLM (Happy Path)**
  - **Given:** A collection contains two documents containing opposing claims.
  - **When:** The user asks a question about that claim and the LLM response explains both viewpoints.
  - **Then:** The post-processing check returns `has_conflict: true` and `surfaced_correctly: true`.
  - **And:** No warning badge is shown in the UI.

- **Scenario 2: Conflict ignored by LLM (Edge Case)**
  - **Given:** A collection contains two documents containing opposing claims.
  - **When:** The user asks a question about that claim and the LLM response silently asserts one claim as fact.
  - **Then:** The post-processing check returns `has_conflict: true` and `surfaced_correctly: false`.
  - **And:** The turn response includes `conflict_status: "unresolved_conflict"`.
  - **And:** The frontend renders a warning notice: "Warning: Sources contain conflicting claims on this topic that were not fully addressed."

### US-002: Study Tools Generation
As a student, I want to generate a study guide or flashcard set for my active document collection.

#### Detailed Scenarios

- **Scenario 3: Flashcard generation**
  - **Given:** A collection has 3 documents with pre-computed summaries.
  - **When:** The user calls the flashcard generation endpoint for that collection.
  - **Then:** The response is a JSON array of objects with `question` and `answer` fields.

- **Scenario 4: Summary degradation fallback**
  - **Given:** A collection contains a document that has no `doc_understanding` summary.
  - **When:** The user generates a briefing doc for that collection.
  - **Then:** The generation service creates an on-the-fly summary of that document from its first few chunks.
  - **And:** The briefing doc is generated successfully.

## Current Context

- **Current behavior summary:**
  - `ChatService` retrieves, generates, and returns the response. `CONFLICT_INSTRUCTION` is passed in the prompt, but no validation runs on the answer.
  - No generation routes or study services exist.
- **Impacted boundaries:**
  - `backend/chat/service.py` (chat turn processing)
  - `backend/routers/collections.py` (new endpoints added or routed)
- **Preserved behavior:**
  - Standard safety checks and hybrid retrieval configurations.
- **Brownfield risk rating:** Medium (touches the main chat turn orchestrator and adds new API surfaces).

## Gray-Area Decisions

- **Locked decisions that shape this spec:**
  - We do not save generated products to the SQLite database (on-demand generation only).
  - Unresolved conflicts trigger warning flags rather than regenerations to control latency.
  - Scope is strictly collection-bound.

## Dependencies And External Touchpoints

- **DEP-001:** LLM Provider (requires valid API credentials for OpenAI/Gemini to run evaluation and product prompts).

## Functional Requirements

### REQ-001: Conflict Detection Service
- **Requirement:** A service to judge if retrieved chunks contradict each other, and if the contradiction is represented in the generated text.
- **Why it matters:** Essential for preventing the system from presenting disputed facts as settled truth.
- **Related success criteria:** SC-001
- **Priority:** Must Have
- **Acceptance notes:** Uses a `CONFLICT_DETECTION_EVALUATION_PROMPT` to analyze context and response.
- **Validation surface:** `pytest backend/tests/chat/test_conflict.py`

### REQ-002: Turn Schema Enrichment
- **Requirement:** Store conflict verification results in `chat_turns.metadata_json` and return it in `ChatTurnResponse`.
- **Why it matters:** Allows the frontend to read conflict status and display appropriate warnings.
- **Related success criteria:** SC-001
- **Priority:** Must Have
- **Acceptance notes:** Includes `has_conflict`, `surfaced_correctly`, and `conflict_details`.
- **Validation surface:** `pytest backend/tests/chat/test_conflict.py`

### REQ-003: Studio Endpoints
- **Requirement:** 6 REST endpoints: `/collections/{id}/generate/{study-guide, briefing-doc, faq, timeline, glossary, flashcards}`.
- **Why it matters:** Enables users to trigger specific study materials generation.
- **Related success criteria:** SC-002
- **Priority:** Must Have
- **Acceptance notes:** Returns raw Markdown for documents, and JSON array for flashcards.
- **Validation surface:** `pytest backend/tests/generate/test_products.py`

### REQ-004: Summary Fallback Resolver
- **Requirement:** Gracefully fall back to generating summaries dynamically if documents lack pre-computed understanding metadata.
- **Why it matters:** Prevents generation failures for older documents.
- **Related success criteria:** SC-002
- **Priority:** Must Have
- **Acceptance notes:** Pulls first 3 chunks from Weaviate/SQLite to summarize on the fly.
- **Validation surface:** `pytest backend/tests/generate/test_products.py`

## Non-Functional Requirements

- **NFR-001 Performance:** Conflict check evaluation must take < 800ms on average when active.
  - *Linked ACs:* AC-1.3
- **NFR-002 Reliability:** Ingestion or study generation must never fail due to a single document missing summaries.
  - *Linked ACs:* AC-2.3
- **NFR-003 Security or Privacy:** Generated products must strictly respect collection boundaries (cannot read documents outside the collection).
  - *Linked ACs:* AC-2.1, AC-2.2

## Constraints

- **Technical:** Must reuse the existing `BaseLLMProvider` factory.
- **Delivery:** Must run successfully under the `phase-gate.sh` and `gate-runner.sh` validation scripts.

## Assumptions

- **ASM-001:** Users want standard Study Guides in Markdown and Flashcards in parseable JSON.

## Risks

- **RISK-001 Prompt Injection in Summaries:**
  - *Mitigation:* Ensure LLM instructions for products treat document summaries as untrusted context.

## Open Questions

None. All gray areas have been aligned.

## Acceptance Criteria

- [ ] **AC-1.1: Conflict Checker logic**
  - *Linked scenario or success criteria:* US-001 Scenario 1
  - *Validation method:* Automated pytest suite
  - *Proof target:* `PYTHONPATH=backend pytest backend/tests/chat/test_conflict.py`

- [ ] **AC-1.2: Response integration and serialization**
  - *Linked scenario or success criteria:* US-001 Scenario 2
  - *Validation method:* Automated pytest suite
  - *Proof target:* Verify `conflict_status` is returned in `ChatTurnResponse` payload.

- [ ] **AC-1.3: Latency constraint verification**
  - *Linked scenario or success criteria:* NFR-001
  - *Validation method:* Profile the conflict LLM judge execution time
  - *Proof target:* Logged latency must be < 800ms.

- [ ] **AC-2.1: Document synthesis endpoints**
  - *Linked scenario or success criteria:* US-002 Scenario 4
  - *Validation method:* Call routes via HTTP and verify Markdown output
  - *Proof target:* `PYTHONPATH=backend pytest backend/tests/generate/test_products.py`

- [ ] **AC-2.2: Flashcard format validation**
  - *Linked scenario or success criteria:* US-002 Scenario 3
  - *Validation method:* Parse HTTP response as JSON array
  - *Proof target:* Verify array elements contain keys `question` and `answer`.

- [ ] **AC-2.3: Incomplete metadata fallback**
  - *Linked scenario or success criteria:* US-002 Scenario 4
  - *Validation method:* Mock missing summaries in tests and call generator
  - *Proof target:* Verify generation succeeds and uses chunk fallbacks.

## Related ADRs

None.

## Notes

None.

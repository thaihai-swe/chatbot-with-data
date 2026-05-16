# Feature Specification: Query Expansion and Rewriting

## Metadata

- Feature name: Query Expansion and Rewriting
- Feature slug: 5.2-query-expansion-and-rewriting
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16
- Related knowledge artifact(s): `artifacts/features/4.advanced-retrieval-strategies-and-routing/spec.md`

## Problem Statement

User queries are often shorthand, informal, or noisy (e.g., "cost?", "eligibility requirements"). While we currently support "Query Expansion" to generate variations, expanding a noisy query often leads to noisy variations. We need a "Rewriting" step to normalize the user's intent into a clean, formal search string *before* expansion. This ensures that the variations generated are based on a high-quality "intent-clear" seed, significantly improving retrieval precision and recall.

## Desired Outcomes

- **Intent Formalization:** Transform messy user input into clear, standalone search questions.
- **Higher Quality Variations:** Generate expansion variations from both the raw input and the cleaned intent.
- **Transparent Transformation:** Show users exactly how their input was "cleaned" and "expanded" in the retrieval trace.

## Minimum Release Slice

- **First release:** Standalone rewriting prompt (non-contextual), `rewrite_query` method, and updated retrieval loop that combines raw and rewritten expansion.
- **Wait:** History-aware rewriting (contextual), user-editable rewriting rules.

## Success Criteria

- SC-001: Shorthand queries (e.g., "how to join?") are rewritten into formal questions (e.g., "What are the procedures and requirements for joining?").
- SC-002: The retrieval pipeline executes search runs for the raw query, the rewritten query, and variations derived from both.
- SC-003: The "Rewritten Query" is visible in the UI Retrieval Trace.

## In Scope

- New LLM prompt for standalone query rewriting (normalization).
- Implementation of `QueryIntelligenceService.rewrite_query`.
- Integration into `AdvancedRetrievalService` pipeline: Raw -> Rewrite -> [Expand Raw + Expand Rewritten].
- Traceability: Adding `rewritten_query` to the `RetrievalTrace` schema.
- UI: Displaying the rewritten query in the debug panel.

## Out Of Scope

- Conversation history awareness (this feature is explicitly non-contextual).
- Real-time synonym lookup from external APIs (handled via LLM expansion).

## Non-Goals

- Replacing the user's original message in the chat display.

## Users And Stakeholders

- Primary users: Chatbot users looking for accurate answers from short queries.
- Secondary stakeholders: Developers debugging retrieval quality and recall.

## User Stories And Key Scenarios

- **US-001: Normalize shorthand.** As a user, I want to ask short questions and have the system understand the underlying formal intent for searching.
- **US-002: Observe transformations.** As a developer, I want to see the "Clean Intent" version of a query to verify the LLM isn't hallucinating terms.

### Detailed Scenarios

- **Scenario 1 (Normalization):**
  - **Given:** User input "pricing?".
  - **When:** Rewriting is enabled.
  - **Then:** The system produces "What is the complete pricing structure, fees, and cost information?".
- **Scenario 2 (Expansion Pipeline):**
  - **Given:** A rewritten query from Scenario 1.
  - **When:** Expansion is enabled.
  - **Then:** Variations are generated for "pricing?" AND "What is the complete pricing structure...".

## Current Context

- `QueryIntelligenceService` handles expansion.
- `AdvancedRetrievalService` orchestrates the multi-query retrieval loop.
- Current loop: `[raw] + expansion(raw) + decomposition(raw)`.

## Dependencies And External Touchpoints

- DEP-001: OpenAI API for the rewriting call.

## Functional Requirements

### REQ-001: Intent Rewriting (Normalization)

Requirement: The system must provide a prompt that instructs the LLM to rewrite a potentially informal or shorthand user query into a single, formal, and standalone search question.

Why it matters: Improves the quality of the "seed" used for retrieval and expansion.

Impacted users or scenarios: US-001.

Priority: Must Have.

Validation surface: Unit test for `QueryIntelligenceService.rewrite_query`.

### REQ-002: Hybrid Expansion Pipeline

Requirement: The retrieval pipeline must be updated to generate expansion variations for BOTH the original user query and the newly generated rewritten query.

Why it matters: Ensures that no specific keywords from the raw input are lost while benefiting from the formalization of the rewrite.

Impacted users or scenarios: SC-002.

Priority: Must Have.

Validation surface: Integration test for `AdvancedRetrievalService`.

### REQ-003: Traceability Update

Requirement: The `RetrievalTrace` data structure and UI must be updated to include the "Rewritten Query" as a distinct step in the transformation log.

Why it matters: Essential for transparency and debugging.

Impacted users or scenarios: US-002.

Priority: Must Have.

Validation surface: Manual UI inspection of the Debug panel.

## Non-Functional Requirements

- NFR-001 Performance: The rewriting step should add < 800ms to the retrieval latency.
- NFR-005 Observability: Both original and rewritten queries must be stored in the turn metadata.

## Constraints

- **No Context:** The rewriter MUST NOT use chat history (this is a standalone intent normalization).

## Assumptions

- ASM-001: LLM-based formalization is more effective for vector search than raw slang/shorthand.

## Risks

- RISK-001 Semantic Drift: The LLM might rewrite "cost?" as something too specific like "subscription fees" when the user meant "hardware cost".
  Mitigation: Augmentation strategy (keep raw query in the search set).

## Open Questions

- Q-001: Should we allow users to toggle "Rewriting" separately from "Expansion"?
  Decision: Yes, via `AdvancedRetrievalConfig`.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001
  Linked user story or scenario: US-001
  Validation method: Unit test: "how to apply?" -> Produces a formal variant.
  Proof target: `backend/tests/test_intelligence.py` (new tests).
- [ ] AC-002 Linked requirement(s): REQ-002
  Linked user story or scenario: SC-002
  Validation method: Log verification: Check that retrieval runs for > 2 unique query strings.
- [ ] AC-003 Linked requirement(s): REQ-003
  Linked user story or scenario: US-002
  Validation method: UI Check: See "Rewritten Query" in the Trace panel.

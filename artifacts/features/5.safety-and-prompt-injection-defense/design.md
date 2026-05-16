# Technical Design - Safety and Prompt-Injection Defense

## Metadata

- Feature name: Safety and Prompt-Injection Defense
- Feature slug: safety-and-prompt-injection-defense
- Related spec: `artifacts/features/5.safety-and-prompt-injection-defense/spec.md`
- Related requirements review: N/A
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-15

## Design Summary

The safety and prompt-injection defense feature introduces a dedicated `SafetyService` into the chat orchestration pipeline. It provides a multi-layer defense: heuristic pattern matching for immediate detection of known injection strings and LLM-based classification for semantic safety and groundedness evaluation. The design hardens the context isolation in `ContextService` and introduces structured safety logging in the `chat_turns` table to enable evaluation and reviewability.

## Current State And Context

- **Existing system baseline**: A grounded chat pipeline that retrieves chunks, evaluates evidence (simple similarity check), and generates a response.
- **Relevant repository patterns**: Service-based architecture with orchestration in `ChatService`. Repository pattern for data persistence.
- **Brownfield constraints**: Must integrate seamlessly with the existing `process_turn` flow and the `AdvancedRetrievalService`.
- **Unchanged behavior**: The core retrieval logic (ChromaDB) and the final generation model call remain the same, but their inputs and orchestration are now guarded.

## Design Drivers

- **REQ-001 (Classification)**:
  Design implication: Need an LLM-based classifier that can categorize queries into safety-relevant buckets (safe, adversarial, out-of-domain).
- **REQ-002 (Groundedness)**:
  Design implication: The `GroundingService` must move beyond simple similarity scores to evaluate semantic support for an answer.
- **REQ-003 (Untrusted content)**:
  Design implication: `ContextService` must use strict delimiters (e.g., XML tags or clear headers) and system instructions that explicitly warn against following instructions in the retrieved text.
- **REQ-004 (Injection Detection)**:
  Design implication: Multi-layer detection (Heuristics + LLM) to balance latency and robustness.
- **REQ-007 (Safety Outputs)**:
  Design implication: `ChatTurnResponse` and the database schema must be extended to include a `SafetyTrace`.

## Proposed Architecture

- **SafetyService (New)**:
  - **Responsibilities**: Query classification, prompt-injection detection (heuristics & LLM), safety risk scoring.
  - **Interaction model**: Called by `ChatService` at the start of a turn (pre-retrieval) and potentially post-retrieval.
- **Enhanced GroundingService**:
  - **Responsibilities**: Evaluating evidence sufficiency, determining answerability, and refusal reasoning.
- **Hardened ContextService**:
  - **Responsibilities**: Assembling the prompt with strict isolation of untrusted data.
- **Persistence Layer**:
  - **Responsibilities**: Storing safety decisions, risk scores, and matched patterns in `chat_turns`.

## Data Flow And Interfaces

- **Inputs**: User query, retrieved chunks.
- **Internal Interfaces**:
  - `SafetyService.check_query(query: str) -> SafetyDecision`
  - `SafetyService.check_chunks(chunks: List[Chunk]) -> List[SafetyDecision]`
  - `GroundingService.evaluate_answerability(chunks: List[Chunk], query: str) -> AnswerabilityResult`
- **Storage Changes**:
  - `chat_turns` table added columns: `safety_status`, `safety_risk_score`, `safety_reason`, `groundedness_score`.
- **SafetyTrace structure**:
  ```json
  {
    "query_classification": "simple",
    "injection_risk": "low",
    "matched_patterns": [],
    "classifier_reason": "Safe factual query.",
    "groundedness": {
      "score": 0.95,
      "status": "grounded"
    },
    "answerability": {
      "is_answerable": true,
      "refusal_reason": null
    }
  }
  ```

## Design Decisions And Tradeoffs

- **Decision**: Use a dedicated `SafetyService` rather than putting safety logic inside `AdvancedRetrievalService`.
  - **Why chosen**: Separation of concerns. Safety is a cross-cutting concern that applies to both user input and retrieved data.
  - **Tradeoff**: One additional service to manage and coordinate in `ChatService`.

- **Decision**: Multi-layer detection (Heuristics + LLM).
  - **Why chosen**: Heuristics provide low-latency protection against common "ignore previous instructions" attacks. LLMs provide deep semantic understanding.
  - **Tradeoff**: Increased complexity in the detection pipeline.

- **Decision**: Refuse at the orchestration level (`ChatService`) rather than the generation level.
  - **Why chosen**: Saves LLM generation costs and provides a cleaner, reviewable refusal path.
  - **Tradeoff**: Requires orchestration logic to handle early exits gracefully (especially for streaming).

## Alternatives Considered

- **Alternative**: Relying solely on system prompts for safety.
  - **Reason not chosen**: System prompts are vulnerable to injection and don't provide reviewable safety metrics or structured refusal reasons.
- **Alternative**: External safety APIs (e.g., OpenAI Moderation API).
  - **Reason not chosen**: While useful, they don't handle RAG-specific "groundedness" or "retrieval as instructions" risks well enough for a portfolio project.

## Brownfield Integration Notes

- **Existing boundary**: `ChatService.process_turn` is the main entry point. Safety checks will be injected before and after retrieval.
- **Migration**: The `chat_turns` table needs a migration to add safety-related columns. Existing turns will have null safety data.
- **Regression hotspot**: Citations. Ensuring that safety-filtered chunks don't break the citation indices.

## Non-Functional Design Considerations

- **Performance**: Heuristic checks are fast. LLM safety calls will be made in parallel with retrieval where possible (for query classification).
- **Reliability**: If the safety LLM fails, the system should default to a "high risk" state or a safe refusal rather than skipping safety.
- **Security**: Strict separation of instructions and data is the primary defense against indirect prompt injection.
- **Observability**: The `SafetyTrace` in the API response makes every safety decision transparent to the user and reviewer.

## Open Questions

- **Q-001**: Should we use a cheaper/faster model (like GPT-4o-mini) for safety classification?
  - **Next step**: Benchmark latency vs. accuracy during Phase 2.
- **Q-002**: How to handle safety in streaming mode for early refusals?
  - **Next step**: Ensure the streaming response can emit a structured "refusal" event before the text stream starts.

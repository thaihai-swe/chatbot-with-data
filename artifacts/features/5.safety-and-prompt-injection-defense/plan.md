# Implementation Plan - Safety and Prompt-Injection Defense

## Metadata

- Feature name: Safety and Prompt-Injection Defense
- Related spec: `artifacts/features/5.safety-and-prompt-injection-defense/spec.md`
- Related requirements review: N/A
- Related design: N/A
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-15

## Plan Summary

This plan outlines the integration of safety controls and prompt-injection defense into the grounded chat pipeline. The approach is to introduce a `SafetyService` that performs pre-retrieval query classification and post-retrieval/post-generation safety checks. We will harden the chat orchestration to treat retrieved content as untrusted data, detect injection attempts, and enforce answerability thresholds. Success will be verified through adversarial test cases and structured safety logging.

## Constitution Alignment

- **Groundedness First**: Ensure all claims are traceable to sources.
  - Planning implication: Refuse answers when evidence support is below the threshold.
- **Treat Retrieval as Untrusted**: Document content must not override system policy.
  - Planning implication: Explicit instruction-override detection and strict prompt separation.

## Execution Context

- **Design reference**: Grounded chat architecture in `backend/chat/`.
- **Relevant repository patterns**: Service-based orchestration in `ChatService`.
- **Brownfield execution constraints**: Must maintain compatibility with `AdvancedRetrievalService` and existing streaming logic.
- **Unchanged behavior**: Baseline retrieval and generation logic for safe queries remains unchanged.

## Technical Approach

- **SafetyService**: A new service to centralize classification and detection logic.
- **Multi-layer Detection**: 
  - Layer 1: Heuristic/Pattern-based detection for common injection strings.
  - Layer 2: LLM-based classification for intent and groundedness.
- **Safe Context Assembling**: Update `ContextService` to use clear delimiters and instructions that isolate retrieved text.
- **Answerability Logic**: Enhance `GroundingService` with configurable thresholds for retrieval scores and support levels.
- **Safety Trace**: Extend `ChatTurnResponse` and the database schema to record safety metrics and detection reasons.

## Decision Rationale

- **Why a separate SafetyService?** To ensure safety logic is reusable and doesn't clutter retrieval or generation services.
- **Why dual detection (Patterns + LLM)?** Patterns are fast and catch simple attacks; LLM classification handles semantic evasion.
- **Why update schema?** Structured logging is a core requirement for evaluation and reviewability.

## Requirements And Constraints

- **REQ-001 (Classification)**: Implement query classification in `SafetyService`.
- **REQ-002 (Groundedness)**: Enhance `GroundingService` with scoring logic.
- **REQ-003 (Untrusted content)**: Refactor prompt templates in `chat/prompts.py` and assembly in `ContextService`.
- **REQ-004 (Injection Detection)**: Implement pattern and LLM-based detectors in `SafetyService`.
- **REQ-005 (Safety Actions)**: Implement logic to exclude chunks or refuse turns based on safety scores.
- **REQ-006 & REQ-007 (Logging/Exposing)**: Update `ChatRepository`, models, and schemas to include safety fields.
- **REQ-008 (Answerability Thresholds)**: Use configurable settings for refusal logic.

## Impacted Areas

- **Services**: `ChatService`, `GroundingService`, `ContextService`, `SafetyService` (new).
- **Models/Schemas**: `ChatTurn`, `ChatTurnResponse`, `RetrievalTrace`.
- **Storage**: `chat_turns` table in SQLite.
- **Prompts**: `GROUNDED_CHAT_SYSTEM_PROMPT`.

## Affected Domains And Integration Boundaries

- **Chat Domain**: Primary location for implementation.
- **LLM Boundary**: Increased LLM calls for classification and detection.
- **Persistence Boundary**: Extended schema for safety metrics.

## Protected Behavior

- **Citation Accuracy**: Safety checks must not break the mapping between answer text and source chunks.
- **Streaming UI**: Safety refusal must still return valid stream-compatible responses or errors.

## Affected Files

- `backend/chat/service.py`: Orchestrate safety checks.
- `backend/chat/safety.py`: (New) Core safety logic.
- `backend/chat/grounding.py`: Enhance evidence evaluation.
- `backend/chat/context.py`: Improve context isolation.
- `backend/chat/prompts.py`: Update safety instructions.
- `backend/models/chat.py`: Add safety fields to `ChatTurn`.
- `backend/schemas/chat.py`: Add safety fields to responses.
- `backend/repositories/chat_repository.py`: Persist safety data.
- `backend/migrations/runner.py`: Update database schema.

## Dependencies

- **DEP-001**: `llm/client.py` for safety classification calls.
- **DEP-002**: `config.py` for safety thresholds.

## Implementation Prerequisites

- Approval of the implementation plan.
- Baseline grounded chat functional.

## Implementation Phases

### Phase 1: Foundation and Schema

Goal: Update data structures and create the SafetyService skeleton.

Tasks:
- TASK-001: Update `migrations/runner.py` with safety columns for `chat_turns`.
- TASK-002: Update `models/chat.py` and `schemas/chat.py`.
- TASK-003: Update `repositories/chat_repository.py` to handle new fields.
- TASK-004: Create `chat/safety.py` with basic `SafetyService` class.

Completion criteria:
- CC-001: Database schema updated and repository tests pass.

### Phase 2: Detection and Classification

Goal: Implement the logic for detecting injections and classifying queries.

Tasks:
- TASK-005: Implement heuristic pattern matching in `SafetyService`.
- TASK-006: Implement LLM-based query classification and injection detection.
- TASK-007: Update `ChatService` to call `SafetyService` pre-retrieval.

Completion criteria:
- CC-002: Safety unit tests confirm detection of sample injection strings.

### Phase 3: Groundedness and Refusal

Goal: Harden the answerability logic and context isolation.

Tasks:
- TASK-008: Enhance `GroundingService` with threshold-based logic.
- TASK-009: Refactor `ContextService` and `prompts.py` for better context isolation.
- TASK-010: Integrate post-retrieval safety actions (chunk exclusion) in `ChatService`.

Completion criteria:
- CC-003: System correctly refuses unsupported or unsafe queries with a logged reason.

### Phase 4: Observability and Validation

Goal: Expose safety data and verify with adversarial tests.

Tasks:
- TASK-011: Update `ChatService.process_turn` to populate the `SafetyTrace`.
- TASK-012: Add adversarial test cases to `tests/test_safety.py`.

Completion criteria:
- CC-004: End-to-end tests verify that safety metrics are returned in the API response.

## Traceability Matrix

- Scenario: US-001 (Refusal) -> Phase 3
- Scenario: US-002 (Injection Defense) -> Phase 2
- Scenario: US-003 (Safety Review) -> Phase 4
- REQ-001 (Classification) -> Phase 2 (TASK-006)
- REQ-004 (Injection Detection) -> Phase 2 (TASK-005, TASK-006)
- AC-001 -> TASK-008, TASK-012
- AC-002 -> TASK-005, TASK-012

## Rollout Plan

- Released as a core update to the backend.
- Feature toggle `enable_safety` in `AdvancedRetrievalConfig`.

## Rollback Plan

- Revert `ChatService` changes to bypass `SafetyService`.
- Database schema changes are additive and backward compatible.

## Risks And Mitigations

- **RISK-001: Latency**: Safety LLM calls increase response time.
  - Mitigation: Use smaller/faster models or combine safety checks with retrieval intelligence where possible.
- **RISK-002: False Positives**: Legitimate chunks flagged as malicious.
  - Mitigation: Provide "recommended action" and allow configuration of sensitivity.

## Open Questions

- Should we use a separate model for safety classification to avoid bias? (Phase 2 decision)

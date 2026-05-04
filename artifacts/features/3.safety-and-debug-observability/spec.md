# Feature Specification

## Metadata

- Feature name: Safety And Debug Observability
- Feature slug: safety-and-debug-observability
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-03
- Related knowledge artifact(s): `prd-requirement.md`, `artifacts/features/2.grounded-chat-and-citations/spec.md`

## Problem Statement

Grounded answers alone are not enough for a learning-focused RAG application. Users and reviewers must also see when the system detected prompt-injection risk, weak grounding, or unsafe instruction patterns, and they must be able to inspect the internal evidence trail that led to a refusal or answer. Without explicit safety handling and debug observability, the product cannot demonstrate trustworthy AI behavior.

## Desired Outcomes

- The system treats retrieved content as untrusted and handles prompt-injection attempts without allowing document text to override application rules.
- Users can inspect answerability, groundedness, refusal, and prompt-injection signals for each run.
- The Debug View exposes enough pipeline state for learners and reviewers to understand how the answer was produced.

## Success Criteria

- SC-001: A reviewer can observe a prompt-injection warning or refusal path when malicious retrieved content or malicious user instructions are introduced.
- SC-002: A reviewer can inspect the system's safety and groundedness decision for any answered or refused query.
- SC-003: A reviewer can open the Debug View for a run and understand the evidence, route, filters, and final decision without reading raw logs.
- SC-004: A reviewer can inspect persisted run metadata for latency, token use, and safety-related decisions after execution completes.

## In Scope

- Prompt-injection detection and handling for user input and retrieved content
- Safety decisioning around groundedness, refusal, and suspicious chunks
- Run logging for query, retrieval, answer, citation, and safety metadata
- Debug View for pipeline internals and answerability state
- User-visible safety warnings and refusal reasoning

## Out Of Scope

- Query expansion, HyDE, reranking, or other advanced retrieval features beyond making them observable when later enabled
- Evaluation dashboards and regression reporting
- Settings management and named configurations

## Users And Stakeholders

- Primary users: Engineers learning how to make RAG systems robust against unsupported answers and prompt injection
- Secondary stakeholders: Reviewers assessing whether the application demonstrates trustworthy and inspectable AI behavior

## User Stories And Key Scenarios

- US-001: As a learner, I see when the system considers a question unsupported, conflicting, or injection-like.
- US-002: As a learner, I inspect the Debug View for a completed run to understand how the system reached its final answer or refusal.
- US-003: As a reviewer, I confirm that retrieved content is treated as untrusted and cannot override application rules.
- US-004: As a reviewer, I inspect logs and run records for latency, token usage, and safety decisions after a query completes.

## Current Context

The repository currently has no implemented debug, safety, or observability behavior. This feature depends on the baseline chat flow because it needs concrete query, retrieval, answer, and citation events to observe and explain.

## Dependencies And External Touchpoints

- DEP-001: Question-answering workflow from `grounded-chat-and-citations`
- DEP-002: Access to query, retrieval, answer, and citation events generated during each run
- DEP-003: UI surfaces for debug inspection and safety messaging

## Functional Requirements

### REQ-001

Requirement:
The system must treat both user queries and retrieved document content as untrusted input and classify prompt-injection-like or unsafe instruction patterns before finalizing an answer, using reviewable detection methods such as pattern rules, allow or block rules, instruction-intent signals, risk scoring, and when enabled model-based classification.

Why it matters:
Retrieved documents must never become a hidden control channel that overrides the application's own rules or disables citations and refusals.

Impacted users or scenarios:
US-001, US-003

Related success criteria:
SC-001, SC-002

Priority: Must Have

Acceptance notes:
The safety workflow must distinguish suspicious inputs from normal informational content, support document-level or retrieval-time scanning when applicable, and carry a visible system decision forward.

### REQ-002

Requirement:
The system must support safety actions that can ignore malicious instructions, exclude suspicious chunks, lower trust in risky evidence, continue with warnings when safe, or refuse when the risk is too high, and it must preserve the specific action chosen for each detected issue.

Why it matters:
Prompt-injection defense is not only about detection; the system needs explicit, reviewable behavior for how it responds once risk is identified.

Impacted users or scenarios:
US-001, US-003

Related success criteria:
SC-001, SC-002

Priority: Must Have

Acceptance notes:
Every detected prompt-injection issue must preserve detection method, risk score, matched pattern or classifier reason, affected document ID when applicable, affected chunk ID when applicable, recommended action, and final system decision.

### REQ-003

Requirement:
The system must expose answerability, groundedness status, refusal reason, prompt-injection result, prompt-injection risk score when available, retrieval support or confidence signals, and supporting safety signals for every completed question-answering run.

Why it matters:
Learners need to know why the system answered, warned, or refused, not just that it did.

Impacted users or scenarios:
US-001, US-002

Related success criteria:
SC-002, SC-003

Priority: Must Have

Acceptance notes:
Safety outcomes must be available for both answered and refused runs and must preserve the safety decision, answerability flag, groundedness status, and refusal cause in a reviewer-visible form.

### REQ-004

Requirement:
The Debug View must show the pipeline internals needed to understand a run, including original query, rewritten query when applicable, selected query mode, retrieval mode, routing decision and reason when applicable, collection or namespace used, metadata filters, retrieved chunks, retrieval scores, selected context, final answer or refusal, citations, groundedness status, answerability flag, prompt-injection result, refusal reason, and the safety decision.

Why it matters:
The product is designed for learning and portfolio review, so the internal reasoning trail must be inspectable through the application itself.

Impacted users or scenarios:
US-002, US-004

Related success criteria:
SC-003, SC-004

Priority: Must Have

Acceptance notes:
The Debug View must remain useful even when the final result is a refusal rather than an answer, and it must preserve later advanced fields such as expanded queries, HyDE output, synonym expansions, reranking traces, parent-child expansion results, prompt template used, latency, and token usage when those features are enabled elsewhere.

### REQ-005

Requirement:
The system must persist run-level observability records that include query context, retrieval metadata, answer output, citations, refusal outcomes, latency, token usage, safety-related decisions, and the model or configuration identifiers needed to explain the run later.

Why it matters:
Later experiment comparison and regression tracking depend on durable run records rather than transient console output.

Impacted users or scenarios:
US-004

Related success criteria:
SC-004

Priority: Must Have

Acceptance notes:
Persisted records must be inspectable after the original chat session has ended and must preserve model name, embedding model, reranker model when applicable, and experiment configuration when later evaluation features depend on those fields.

### REQ-006

Requirement:
The user interface must surface prompt-injection warnings, refusal reasoning, answerability state, groundedness state, and any excluded-evidence warnings when they materially affected the run outcome, including whether the system answered safely with warnings or refused outright.

Why it matters:
Safety decisions hidden only in logs would reduce the product's educational and review value.

Impacted users or scenarios:
US-001, US-002

Related success criteria:
SC-001, SC-002, SC-003

Priority: Must Have

Acceptance notes:
Warnings must explain the effect on the answer flow, not just that a warning exists.

## Non-Functional Requirements

- NFR-001 Security or Privacy: Retrieved text must never be treated as trusted instructions that can override system, developer, or application rules.
- NFR-002 Observability or Supportability: Safety and debug records must be understandable through the product UI without requiring direct database or log inspection.
- NFR-003 Reliability: Every run must produce a coherent final state even when safety checks trigger warnings, chunk exclusion, or refusal.
- NFR-004 Performance: Safety and debug instrumentation must not prevent the user from seeing progress or final state in the chat flow.

## Constraints

- Technical constraints: The feature depends on baseline retrieval and answer generation events already being available to observe.
- Business constraints: Safety explanations must support learning and reviewer trust without requiring expert familiarity with hidden backend logic.
- Delivery constraints: This slice covers observability and safety behavior, not offline evaluation or feature configuration management.

## Assumptions

- ASM-001: The first version can mix rule-based and model-based safety signals as long as the resulting decision is visible and reviewable.
- ASM-002: Advanced retrieval features introduced later must appear in the Debug View when enabled, but they are not required to land in the same implementation increment as this spec.

## Risks

- RISK-001 Risk: Safety warnings that are too opaque may look arbitrary and reduce user trust.
  Mitigation: Require visible reason categories and effect summaries in both the UI and persisted records.
- RISK-002 Risk: Overly aggressive chunk exclusion may increase false refusals.
  Mitigation: Preserve enough debug context for reviewers to inspect which chunks were excluded and why.

## Open Questions

- Q-001 Question: Should the first review require model-based prompt-injection classification in addition to rules, or is a reviewable rule-first defense acceptable if the decision trace is visible?
  Type: Non-blocking
  Owner: Product reviewer
  Next step: Confirm the minimum safety-detection depth during requirements review.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001, REQ-002
  Linked user story or scenario: US-001, US-003
  Linked success criteria: SC-001
  Validation method: Submit or retrieve content containing prompt-injection-like instructions and verify that the system flags the risk, records the issue payload, and applies an explicit safety action.
- [ ] AC-002 Linked requirement(s): REQ-003
  Linked user story or scenario: US-001
  Linked success criteria: SC-002
  Validation method: Review one answered run and one refused run and confirm that answerability, groundedness, refusal reason, safety status, and prompt-injection result are visible.
- [ ] AC-003 Linked requirement(s): REQ-004
  Linked user story or scenario: US-002
  Linked success criteria: SC-003
  Validation method: Open the Debug View for a completed run and verify that the query, retrieval details, selected context, final output, answerability state, and safety decision are inspectable.
- [ ] AC-004 Linked requirement(s): REQ-005
  Linked user story or scenario: US-004
  Linked success criteria: SC-004
  Validation method: Inspect persisted run records after a chat session and verify that latency, token usage, citations, safety decisions, and model or experiment identifiers remain available.
- [ ] AC-005 Linked requirement(s): REQ-006
  Linked user story or scenario: US-001, US-002
  Linked success criteria: SC-001, SC-002, SC-003
  Validation method: Trigger a run where safety warnings affect the outcome and verify that the UI explains the warning and its effect on the answer flow.

## Notes

This spec covers PRD sections 7.7, 7.7.1, 7.9, 7.12, the safety-heavy portions of 7.13, and UI section 7.15.5. It provides the observability foundation that later advanced retrieval and evaluation features will build on, including the concrete safety-issue and run-record payloads those later features depend on.

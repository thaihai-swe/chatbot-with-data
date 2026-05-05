# Feature Specification

## Metadata

- Feature name: Safety and Prompt-Injection Defense
- Feature slug: safety-and-prompt-injection-defense
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-05
- Related knowledge artifact(s): `prd-requirement.md`

## Problem Statement

The product is explicitly intended to demonstrate grounded, production-style RAG behavior. That goal fails if the assistant answers unsupported questions confidently, follows malicious instructions hidden in retrieved content, or hides the safety reasoning behind refusals and warnings.

## Desired Outcomes

- The assistant makes explicit safety decisions for unsupported, adversarial, or weakly grounded requests.
- Retrieved content is treated as untrusted data, and prompt-injection signals are detected, logged, and handled in a reviewable way.

## Success Criteria

- SC-001: The system refuses or constrains unsafe, unsupported, or out-of-domain requests in a reviewable way.
- SC-002: Prompt-injection-like content in documents or queries is detected and handled without silently changing assistant policy.
- SC-003: Safety outputs such as groundedness, support, refusal reason, and injection risk are visible for later review and evaluation.

## In Scope

- Safety decisioning for answerability and groundedness
- Prompt-injection detection on retrieved content and user queries
- Safe handling actions for suspicious chunks or requests
- Safety-related logs and user-visible outputs

## Out Of Scope

- Full evaluation datasets and dashboards
- Collection and ingestion CRUD mechanics
- Advanced retrieval feature design except where safety must constrain their outputs

## Users And Stakeholders

- Primary users: Engineers and learners validating whether the assistant behaves safely under weak evidence or adversarial input
- Secondary stakeholders: Reviewers assessing whether the project demonstrates realistic RAG safety controls

## User Stories And Key Scenarios

- US-001: As a user, I can see when the assistant refuses an unsupported or out-of-domain question.
- US-002: As a user, I can trust that malicious instructions inside a retrieved document are not followed.
- US-003: As a reviewer, I can inspect the system’s safety decision, support level, and prompt-injection handling after a response.

## Current Context

The repository has no committed safety pipeline or prompt-injection controls yet. This spec hardens the grounded chat flow and defines the reviewable safety outputs needed before evaluation work is credible.

## Dependencies And External Touchpoints

- DEP-001: Grounded answer generation and retrieval context from `grounded-chat-and-citations`
- DEP-002: Indexed document and chunk provenance from upstream ingestion and indexing features
- DEP-003: Optional model-assisted or rules-based classification signals for safety and prompt-injection detection

## Functional Requirements

### REQ-001

Requirement: The system must classify incoming requests and response candidates for answerability and safety-relevant categories, including supported, unsupported, ambiguous, out-of-domain, multi-hop where applicable, and adversarial or prompt-injection-like behavior.

Why it matters: Reviewable safety starts with explicit classification rather than ad hoc refusal wording.

Impacted users or scenarios: US-001, US-003

Related success criteria: SC-001, SC-003

Priority: Must Have

Acceptance notes: Reviewers must be able to inspect the final safety category used for a turn.

### REQ-002

Requirement: The system must compute and expose groundedness and retrieval-support signals for answers, refuse when support is insufficient, and distinguish unsupported refusal from partial-evidence uncertainty.

Why it matters: Users need to know whether the assistant is refusing because the question is unsupported, outside scope, or only partially grounded.

Impacted users or scenarios: US-001, US-003

Related success criteria: SC-001, SC-003

Priority: Must Have

Acceptance notes: A reviewer must be able to inspect both the support signal and the final refusal or uncertainty decision.

### REQ-003

Requirement: The system must treat all retrieved content as untrusted data rather than instructions and must ensure document text cannot disable citations, override system policy, reveal hidden prompts, or authorize actions outside the assistant’s product role.

Why it matters: This is the core safety boundary for any RAG system that reads user-provided or web-fetched content.

Impacted users or scenarios: US-002, US-003

Related success criteria: SC-001, SC-002

Priority: Must Have

Acceptance notes: Reviewers must be able to test instruction-like retrieved content and confirm it is not executed as policy.

### REQ-004

Requirement: The system must support advanced prompt-injection detection on user queries and retrieved content using one or more detection signals such as pattern matching, allowlist or blocklist rules, classifier-based scoring, document-level ingestion scanning, and chunk-level retrieval scanning, produce a risk score or equivalent severity output, and record the matched reason or pattern behind the detection.

Why it matters: The PRD explicitly calls for advanced prompt-injection detection as a first-class feature and evaluation target.

Impacted users or scenarios: US-002, US-003

Related success criteria: SC-002, SC-003

Priority: Must Have

Acceptance notes: A reviewer must be able to inspect how a suspicious query or chunk was flagged and why.

### REQ-005

Requirement: For suspicious chunks or requests, the system must support explicit safety actions such as ignoring malicious instructions, excluding a chunk from answer generation, lowering its trust score, warning the user, or refusing the answer when risk remains unacceptable.

Why it matters: Detection alone is not enough; the system needs reviewable mitigation behavior.

Impacted users or scenarios: US-001, US-002, US-003

Related success criteria: SC-001, SC-002, SC-003

Priority: Must Have

Acceptance notes: Reviewers must be able to see both the detection result and the handling action.

### REQ-006

Requirement: The system must log refusals, weak support, hallucination risk indicators, conflicting evidence, prompt-injection warnings, safety classifier outputs or matched patterns, affected documents or chunks, and the final safety decision for each relevant turn.

Why it matters: Safety claims are not credible if they cannot be inspected after the fact.

Impacted users or scenarios: US-003

Related success criteria: SC-003

Priority: Must Have

Acceptance notes: A reviewer must be able to retrieve a safety record for a turn without guessing at hidden classifier outputs.

### REQ-007

Requirement: The system must expose safety outputs for each relevant turn, including retrieval support score, groundedness status, answerability flag, refusal reason when refused, prompt-injection risk score when applicable, and the final safety decision.

Why it matters: The PRD asks for transparent refusal and groundedness behavior, so reviewers need the actual safety outputs rather than only a final answer state.

Impacted users or scenarios: US-001, US-003

Related success criteria: SC-001, SC-003

Priority: Must Have

Acceptance notes: Reviewers must be able to inspect the safety output set for a turn without reconstructing it from logs.

### REQ-008

Requirement: The system must determine answerability using configurable threshold logic that can consider retrieval score thresholds, number of supporting chunks, groundedness confidence, citation coverage, evidence consistency, collection scope, reranker confidence, prompt-injection risk, and dynamic routing confidence, and it must log, expose in debug output, and include in evaluation output both the final answerability decision and the refusal category when a refusal occurs.

Why it matters: The PRD requires answerability to be a reviewable product decision rather than a hidden model guess.

Impacted users or scenarios: US-001, US-003

Related success criteria: SC-001, SC-003

Priority: Must Have

Acceptance notes: Reviewers must be able to inspect the threshold-driven answerability decision and see why a refusal category was chosen.

## Non-Functional Requirements

- NFR-001 Performance: Safety checks must not silently disappear under latency pressure; fallback behavior must still produce a clear safety outcome.
- NFR-002 Reliability: Failure of one detector must not default the system into unsafe confident answering.
- NFR-003 Security or Privacy: Safety logs must preserve enough provenance for review without leaking secrets or treating hidden prompt content as trusted instructions.
- NFR-004 Accessibility: Refusal reasons and warning states must be understandable through clear text, not just risk colors or badges.
- NFR-005 Observability or Supportability: Reviewers must be able to inspect detection method, matched pattern or classifier reason, risk score, affected source references, recommended action, and final action for flagged cases.
- NFR-006 Configurability: Safety thresholds and refusal logic must be adjustable without rewriting the feature’s core requirement definitions.

## Constraints

- Technical constraints: This spec defines required safety behavior without requiring one specific classifier implementation.
- Business constraints: The feature must show realistic safety posture for a portfolio-quality RAG system, not only superficial refusal copy.
- Delivery constraints: Safety outputs must integrate with grounded chat before evaluation metrics can be trusted.

## Assumptions

- ASM-001: Safety decisions may combine rule-based and model-based signals as long as the final outcome remains inspectable.
- ASM-002: Some suspicious content may still contribute factual evidence if malicious instructions are isolated and ignored.

## Risks

- RISK-001 Risk: Overly aggressive detection could suppress useful evidence and make the assistant appear broken.
  Mitigation: Require explicit handling actions and distinguish warning, exclusion, and refusal paths.
- RISK-002 Risk: Safety failures may be hard to diagnose if logs omit the affected chunk or document.
  Mitigation: Require source-level provenance in safety records.

## Open Questions

- Q-001 Question: Should ingestion-time prompt-injection scanning block document availability immediately, or should flagged documents remain available with warnings until retrieval-time handling decides?
  Type: Non-blocking
  Owner: Product decision
  Next step: Resolve during review; current requirements allow either path as long as the safety action is explicit and reviewable.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001, REQ-002, REQ-008
  Linked user story or scenario: US-001
  Linked success criteria: SC-001, SC-003
  Validation method: Submit unsupported and partially supported questions and verify distinct classification, support signals, threshold-based answerability decisions, and refusal or uncertainty behavior.
- [ ] AC-002 Linked requirement(s): REQ-003, REQ-004, REQ-005
  Linked user story or scenario: US-002
  Linked success criteria: SC-001, SC-002, SC-003
  Validation method: Use injection-like content in a query or retrieved document and verify detection reasoning plus safe handling action.
- [ ] AC-003 Linked requirement(s): REQ-006, REQ-007
  Linked user story or scenario: US-003
  Linked success criteria: SC-003
  Validation method: Inspect safety records for a flagged turn and verify provenance, decision, action details, and explicit safety outputs are present.

## Notes

Delivery sequence: 5 of 7. This feature hardens the assistant behavior before the project claims evaluable quality or resistance to adversarial content.

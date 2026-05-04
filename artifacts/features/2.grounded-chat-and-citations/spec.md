# Feature Specification

## Metadata

- Feature name: Grounded Chat And Citations
- Feature slug: grounded-chat-and-citations
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-03
- Related knowledge artifact(s): `prd-requirement.md`, `artifacts/features/1.knowledge-ingestion-and-collections/spec.md`

## Problem Statement

After documents are ingested, users still need a question-answering experience that turns stored knowledge into usable answers. Without grounded answer generation, collection scoping, citation traceability, and clear refusal behavior, the product cannot demonstrate that retrieval actually helps the model answer from evidence instead of improvisation.

## Desired Outcomes

- Users can ask questions against a selected collection or across all collections and receive answers grounded in retrieved evidence.
- Every factual answer includes structured citations that point back to real stored chunks.
- The system refuses unsupported questions instead of fabricating answers and can stream answer progress in the chat UI.

## Success Criteria

- SC-001: A reviewer can ask a supported question and receive an answer that cites real retrieved chunks.
- SC-002: A reviewer can ask an unsupported or weakly supported question and receive a refusal with a visible reason rather than a fabricated answer.
- SC-003: A reviewer can inspect citation details and trace them back to document, section or page, and chunk metadata.
- SC-004: A reviewer can use the chat UI with preserved conversation history and visible answer-generation status.

## In Scope

- Baseline chat workflow for asking questions against ingested collections
- Retrieval mode selection and collection scoping for question answering
- Grounded answer generation with structured citations
- Answerability and refusal behavior for weak evidence
- Streaming and non-streaming answer delivery
- Chat screen and citation detail experience

## Out Of Scope

- Query expansion, query decomposition, HyDE, synonym expansion, or dynamic routing
- Advanced prompt-injection handling and deep debug observability
- Evaluation datasets, dashboards, and regression reporting
- Settings and reusable experiment configurations

## Users And Stakeholders

- Primary users: Engineers learning how retrieved evidence changes answer quality and refusal behavior
- Secondary stakeholders: Reviewers who need to verify that answers are grounded, cited, and traceable

## User Stories And Key Scenarios

- US-001: As a learner, I ask a question against a chosen collection and receive a document-grounded answer.
- US-002: As a learner, I switch between a single collection and all collections when asking a question.
- US-003: As a learner, I inspect inline and reference-style citations to see where each claim came from.
- US-004: As a learner, I receive a refusal when the available evidence is too weak, conflicting, or missing.
- US-005: As a learner, I watch answer generation progress in the chat screen and can continue a conversation with preserved history.

## Current Context

This repository does not yet implement retrieval or chat behavior. It also depends on the ingestion and collection foundation defined in `knowledge-ingestion-and-collections`, because this feature assumes retrievable document, chunk, and collection records already exist.

## Dependencies And External Touchpoints

- DEP-001: Collection-scoped document and chunk records from `knowledge-ingestion-and-collections`
- DEP-002: A retrieval layer that can select evidence from stored chunks
- DEP-003: A generation layer capable of producing cited answers and refusals from retrieved context

## Functional Requirements

### REQ-001

Requirement:
The system must provide a chat workflow where users can submit a question against a selected collection or across all collections, preserve chat history within the conversation, and expose the chosen search scope and retrieval strategy before the answer is finalized.

Why it matters:
The primary user journey is asking questions against the knowledge base and learning how retrieval affects answers over time.

Impacted users or scenarios:
US-001, US-002, US-005

Related success criteria:
SC-001, SC-004

Priority: Must Have

Acceptance notes:
The question workflow must make the selected search scope visible before the answer is generated.

### REQ-002

Requirement:
The system must retrieve supporting evidence for a question using configured baseline retrieval modes, including semantic, keyword or sparse, and hybrid retrieval support, and carry forward the retrieved chunk metadata needed for answer generation and citations.

Why it matters:
Answer quality and citation validity depend on retrieval that selects real source evidence rather than relying on the model's prior knowledge alone.

Impacted users or scenarios:
US-001, US-002, US-003

Related success criteria:
SC-001, SC-003

Priority: Must Have

Acceptance notes:
The chosen retrieval mode must be visible in the user experience or output metadata for later inspection.

### REQ-003

Requirement:
The system must generate answers that use retrieved evidence for factual claims, avoid unsupported claims, explicitly state uncertainty when evidence is partial, and preserve enough citation structure to distinguish document title or ID, page or section when available, chunk ID, and source URL when applicable.

Why it matters:
The product is valuable only if answers are inspectable and grounded in the ingested knowledge base.

Impacted users or scenarios:
US-001, US-003

Related success criteria:
SC-001, SC-003

Priority: Must Have

Acceptance notes:
Expanded queries, synthetic helper text, or non-retrieved content must never appear as citations in this feature, and the product must support both inline citations and reference-list citations for factual claims.

### REQ-004

Requirement:
The system must decide whether a question is answerable from the available evidence and refuse when retrieval confidence, support coverage, evidence consistency, citation coverage, collection scope, or other required answerability signals are insufficient for a reliable answer.

Why it matters:
A RAG system that answers unsupported questions confidently undermines both learning value and reviewer trust.

Impacted users or scenarios:
US-004

Related success criteria:
SC-002

Priority: Must Have

Acceptance notes:
Refusals must expose a user-visible reason category rather than returning a generic failure state, and the refusal taxonomy must preserve categories such as no relevant evidence, low retrieval confidence, insufficient support, conflicting evidence, out of domain, and equivalent collection- or safety-related refusal causes when later features supply those signals. The answerability thresholds behind those outcomes must remain configurable through the later configuration feature.

### REQ-005

Requirement:
The system must provide a citation detail experience that lets users inspect the evidence behind an answer, including the cited source metadata, the supporting text snippet, the retrieval strategy used, and the retrieval or reranking scores available for that citation.

Why it matters:
Reviewers need to verify that citations support the actual answer claims and map back to stored knowledge records.

Impacted users or scenarios:
US-003

Related success criteria:
SC-003

Priority: Must Have

Acceptance notes:
Users must be able to inspect citation evidence without leaving the application to search raw storage manually, and the detail view must show cited document title, document ID, chunk ID, page or section, source URL when applicable, and parent chunk ID or reranking score when later features make those fields available.

### REQ-006

Requirement:
The chat experience must support streamed or non-streamed answer delivery, show answer-generation status, support cancellation of in-progress generation, manage the context window by trimming, ranking, and packing retrieved context, and preserve citation correctness when the final answer is completed.

Why it matters:
Streaming and visible progress make the product feel responsive while still preserving trust in the final evidence-backed answer.

Impacted users or scenarios:
US-005

Related success criteria:
SC-004

Priority: Must Have

Acceptance notes:
Partial streamed output must not present fabricated final citations before evidence mapping is complete, the status flow should preserve interpretable states such as understanding the query, retrieving evidence, generating the answer, checking groundedness, and finalizing citations, and the chat screen must preserve the question input, answer panel, citation panel, collection selector, retrieval strategy selector, streaming control, optional debug toggle, and chat-history surface required by the PRD.

## Non-Functional Requirements

- NFR-001 Reliability: Each question must end in an answer, refusal, cancellation, or error state that is clear to the user.
- NFR-002 Performance: The chat experience must provide visible progress during retrieval and generation rather than leaving the interface idle without feedback, including streamed response support that does not bypass safety checks.
- NFR-003 Security or Privacy: Factual claims in answers must be grounded in retrieved knowledge-base evidence rather than hidden model assumptions.
- NFR-004 Accessibility: Citation details and refusal messages must be readable through the same interface used to ask the question.

## Constraints

- Technical constraints: The feature depends on the collection-scoped document foundation established earlier in the sequence.
- Business constraints: The first chat experience must prioritize groundedness and traceability over broad conversational freedom.
- Delivery constraints: Advanced retrieval transformations are explicitly deferred so the baseline cited chat flow can be reviewed on its own.

## Assumptions

- ASM-001: Explicit collection selection is the primary scoping control in this feature; automatic collection detection is handled later.
- ASM-002: Baseline retrieval modes are sufficient for this slice as long as the chosen mode is visible and citations remain correct.

## Risks

- RISK-001 Risk: Users may mistake a retrieval miss for a model failure if refusal reasoning is too vague.
  Mitigation: Require explicit refusal reasons tied to answerability rather than generic fallback copy.
- RISK-002 Risk: Streaming output can create trust issues if provisional text implies unsupported claims before citations are finalized.
  Mitigation: Require status visibility and final citation correctness before the answer is treated as complete.

## Open Questions

- Q-001 Question: Should the first review require both inline citations and a separate reference list in the same answer, or is support for either presentation enough if the structured citation data is intact?
  Type: Non-blocking
  Owner: Product reviewer
  Next step: Confirm the minimum acceptable citation presentation during requirements review.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001
  Linked user story or scenario: US-001, US-002, US-005
  Linked success criteria: SC-001, SC-004
  Validation method: Ask a question against a selected collection, then repeat across all collections and verify that the chosen search scope, retrieval strategy, and conversation history are visible.
- [ ] AC-002 Linked requirement(s): REQ-002
  Linked user story or scenario: US-001, US-002
  Linked success criteria: SC-001
  Validation method: Submit a supported question and verify that the answer output identifies the retrieval mode used and is based on retrieved evidence.
- [ ] AC-003 Linked requirement(s): REQ-003
  Linked user story or scenario: US-001, US-003
  Linked success criteria: SC-001, SC-003
  Validation method: Review an answer with citations and confirm that each citation maps to a real stored chunk with document title or ID, chunk ID, and page, section, or URL metadata when available, using inline or reference-list presentation without fabricated references.
- [ ] AC-004 Linked requirement(s): REQ-004
  Linked user story or scenario: US-004
  Linked success criteria: SC-002
  Validation method: Ask a question outside the available evidence and verify that the system refuses with a visible reason category instead of generating a confident answer, using explicit answerability logic rather than a generic error state.
- [ ] AC-005 Linked requirement(s): REQ-005
  Linked user story or scenario: US-003
  Linked success criteria: SC-003
  Validation method: Open a citation detail view from an answer and verify that the supporting snippet, source metadata, retrieval strategy, and available scores are inspectable.
- [ ] AC-006 Linked requirement(s): REQ-006
  Linked user story or scenario: US-005
  Linked success criteria: SC-004
  Validation method: Start a streamed answer, observe visible generation states, cancel one in-progress response, and verify that completed answers show final citations only after the answer is finalized and the system has managed context and groundedness checks.

## Notes

This spec covers the core portions of PRD sections 7.4, 7.5, 7.6, 7.6.1, 7.11, 7.13, and UI sections 7.15.3 and 7.15.4. Advanced routing, query transformation, deep safety diagnostics, and experiment features are intentionally sequenced into later specs, but the core answer flow still preserves citation structure, answerability behavior, and context-packing responsibilities from the PRD.

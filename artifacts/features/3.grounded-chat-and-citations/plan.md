# Implementation Plan

## Metadata

- Feature name: Grounded Chat and Citations
- Related spec: `artifacts/features/3.grounded-chat-and-citations/spec.md`
- Related requirements review: None present
- Related design: None present
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-06

## Plan Summary

Implement this feature as a chat service in Python FastAPI that consumes indexed chunks from Feature 2, executes collection-scoped retrieval to find relevant evidence, generates grounded answers with citations via OpenAI API, manages chat history across turns while protecting evidence-backed claims from context inflation, and streams generation progress to the frontend. The delivery is phased so the chat query and retrieval layer land first, answer generation with grounding and citations land second, streaming and cancellation land third, and the React chat UI lands on top of stable REST APIs.

Grounded chat is the core product value moment. The system must refuse unsupported claims, preserve citation correctness through streaming, and keep retrieved content treated as data rather than instructions. Rollout risk is moderate because the feature introduces external LLM API dependencies and complex state management (chat history, streaming, citation correctness), so validation and rollback guidance account for generation failures, incomplete citations, and streaming state loss.

## Constitution Alignment

- Constitutional rule or principle: Frontend screens in this repo must be JavaScript clients under `frontend/` that call REST API endpoints; do not use backend-rendered data views.
  Planning implication: All user-facing chat workflows will be delivered as ReactJS screens that consume FastAPI chat endpoints; no backend-rendered chat or template-based responses.
- Constitutional rule or principle: Python work in this repo must use a virtual environment, and frontend/backend concerns must stay separated.
  Planning implication: Chat service logic lives in `backend/` under the same FastAPI application and virtual environment; the chat UI remains isolated under `frontend/`.

## Execution Context

- Design reference: No `design.md` exists for this feature; the plan makes minimum architecture choices needed for safe implementation (e.g., LLM provider defaults to OpenAI per PRD, vector retrieval is baseline, context window strategy for history).
- Relevant repository patterns for execution: Features 1 and 2 established FastAPI endpoints, SQLite persistence (documents, chunks, embeddings), and vector indexing (Chroma). Feature 3 builds on top of these contracts and adds chat sessions, turns, citations, and grounded generation logic.
- Brownfield execution constraints or greenfield assumptions: This is brownfield on top of Features 1 and 2. Reuse FastAPI app structure, SQLite database, indexed chunks from Feature 2, and document/collection identity; add new tables for chat sessions, turns, and citation metadata without disturbing prior workflows.
- Unchanged behavior that must be preserved during delivery: Features 1 and 2 (ingestion, chunking, indexing) remain unchanged. Do not trigger automatic chat responses or change chunk/index behavior. Chat is a new capability layered on top, not a modification of prior features.

## Technical Approach

- Chosen approach: Build a chat service that accepts queries scoped to collection(s), executes vector similarity search on indexed chunks, assembles retrieved context, prompts an LLM (OpenAI) to generate grounded answers with citations, validates that citations map back to retrieved chunks, manages multi-turn chat history with context-window awareness, and streams generation progress with in-progress status and cancellation support.
- Architectural or integration shape: The backend owns query parsing, collection-scoped retrieval (via vector DB query), context assembly, LLM prompting, citation extraction and validation, chat history management, and streaming orchestration. The frontend owns chat UI (message list, input form, citation rendering, streaming status, cancellation button), collection selection, and turn display. Chat state is persisted in SQLite; vectors are queried from Chroma (Feature 2's vector DB).
- Key interfaces or contracts: Chat session creation endpoint (select collection scope); chat turn submission endpoint (query text, session ID); streaming response endpoint (Server-Sent Events or chunked HTTP response); chat history endpoint (retrieve prior turns with citations); turn cancellation endpoint. Response contract includes answer text, citations (chunk ID, document ID, document title, page/section, source URL), generation status, and streaming markers.
- Operational considerations: Chat history is trimmed to respect LLM context windows; retrieved context and prior turns are ranked by relevance and inclusion priority so evidence-backed claims remain grounded even with deep history. Streaming endpoints keep generation in progress visible but do not emit fabricated citations until final evidence mapping is complete. Chat sessions are ephemeral by default but can optionally be persisted.

## Decision Rationale

- Why this approach was selected: Feature 2 provides a stable, queryable vector index with full citation metadata. Building chat on top of it as a separate service layer keeps concerns decoupled and allows chat behavior to evolve without modifying chunking. OpenAI is specified in the PRD as the LLM provider. Streaming improves UX and allows reviewers to observe generation progress and in-progress status.
- Existing patterns reused: Same FastAPI router structure and REST API contract style (JSON, standard HTTP codes) from Features 1 and 2. Same SQLite persistence for chat metadata. Same Chroma vector query interface from Feature 2.
- Alternatives considered: Direct LLM generation without retrieval (rejected: defeats grounding requirement); always include all history in context (rejected: inflates window, loses evidence focus); fabricate citations mid-stream (rejected: violates SC-003 correctness requirement); store all chat sessions by default (rejected: out of scope for v1, can defer to later feature).
- Why rejected: Those options either violate core requirements (grounding, citation correctness) or add scope (session persistence, advanced history management). The current approach is minimal and sufficient for reviewers to validate grounded generation.

## Requirements And Constraints

- REQ-001:
  Implementation note: Accept chat queries with explicit collection selection (single collection or all collections); preserve the selected scope throughout retrieval and generation.
  Planned validation: API tests that specify collection scope and verify retrieved chunks and final answer metadata include collection filtering; manual reviewer walkthrough showing scope in UI.
  Linked scenario or outcome: US-001
- REQ-002:
  Implementation note: Execute baseline retrieval using vector similarity search on indexed chunks from Feature 2. Support configurable k (top-k results). Return ranked retrieved chunks with full metadata (document ID, title, page, section, chunk ID, source URL, collection).
  Planned validation: API tests that confirm retrieved chunks are ranked by similarity; integration tests that verify all required metadata is returned; manual inspection of retrieval results against hand-chosen queries.
  Linked scenario or outcome: US-001, US-002
- REQ-003:
  Implementation note: Build context from retrieved chunks and prior chat turns, aware of context-window limits. Trim or rank history so evidence-backed claims remain at the top; do not allow low-relevance history to displace source evidence. Return the final context used for generation so reviewers can see what was included.
  Planned validation: Integration tests verifying context assembly with multi-turn history; manual inspection that evidence remains accessible with deep conversation.
  Linked scenario or outcome: US-001
- REQ-004:
  Implementation note: Extract citations from LLM output by matching factual claims to retrieved chunks. Preserve for each citation: chunk ID, document ID, document title, page or section (when available), and source URL (when available). Do not emit citations that do not correspond to retrieved chunks or that reference synthetic retrieval artifacts.
  Planned validation: Unit tests for citation extraction and validation logic; integration tests that verify citation metadata is complete and traceable; manual inspection showing citations map back to real retrieved chunks.
  Linked scenario or outcome: US-002
- REQ-005:
  Implementation note: Refuse or qualify answers when retrieval support is insufficient (e.g., fewer than k results, low max similarity, or ambiguous evidence). Communicate uncertainty explicitly (e.g., "I don't have enough information" instead of confident unsupported claims). Make refusal and uncertainty visible in UI.
  Planned validation: Test cases with deliberately weak or absent evidence; manual reviewer walkthrough observing refusal messaging.
  Linked scenario or outcome: US-003
- REQ-006:
  Implementation note: Treat retrieved document content as untrusted data, not instructions. System prompts and response rules must not be overrideable by retrieved text. Do not follow directives in retrieved content that attempt to change assistant behavior or suppress citations.
  Planned validation: Security-focused test cases with adversarial retrieved text (e.g., "ignore your instructions"); manual reviewer verification that retrieved instructions are not followed.
  Linked scenario or outcome: US-001, US-003
- REQ-007:
  Implementation note: Support streaming answer delivery with visible in-progress status (understanding query, retrieving evidence, generating answer, checking groundedness, finalizing citations). Allow cancellation mid-stream. Emit only complete, final citations once evidence mapping is done; do not emit provisional or fabricated citations during streaming. Provide non-streaming fallback path with identical grounding and citation correctness.
  Planned validation: Streaming response tests comparing streamed vs. non-streamed answers for correctness; cancellation tests verifying no partial state is left; manual UI verification of status labels and cancellation UX.
  Linked scenario or outcome: US-004
- NFR-001:
  Implementation note: Chat flow should return visible retrieval progress within 2-3 seconds (query understanding and retrieval) and generation progress within 5-10 seconds (answer generation and citation finalization). Use async/await for non-blocking retrieval and LLM calls.
- NFR-002:
  Implementation note: If retrieval fails, present a clear error state (e.g., "Retrieval failed, please try again") without a stalled or truncated answer. If generation fails mid-stream, cancel the stream and show error state. Do not silently drop turns from history or leave inconsistent state.
- NFR-003:
  Implementation note: Keep retrieved content bounded to selected collection scope. Do not mix collections in retrieval without explicit user consent. Do not treat retrieved content as privileged or exempt from citation requirements.
- NFR-004:
  Implementation note: Citations, refusal states, and streaming statuses must be understandable through text labels (not color alone); UI must be keyboard-navigable and include ARIA labels where appropriate.
- NFR-005:
  Implementation note: Log query, retrieved chunks, context used for generation, final answer, and citations. Provide inspection endpoints so reviewers can trace how an answer was produced from start to finish.
- CON-001:
  Impact on plan: Do not add advanced retrieval (query expansion, HyDE, reranking, dynamic routing, semantic caching) in this feature. Keep baseline retrieval simple so Feature 4 can layer advanced strategies on top. Do not add evaluation or safety instrumentation beyond grounding checks; Features 5 and 6 handle those.

## Impacted Areas

- Services or modules: New `backend/chat/` service with query parser, retrieval orchestrator, context assembly, answer generation, citation extraction/validation, and streaming handler.
- APIs or interfaces: New FastAPI routers for chat session creation, turn submission, streaming responses, history retrieval, and turn cancellation.
- Data model or storage: New SQLite tables: `chat_sessions` (session_id, created_at, collection_scope), `chat_turns` (turn_id, session_id, query_text, retrieved_chunks, context_used, answer_text, citations, status, timestamps).
- UI or UX: New React chat screen with message list, input form, streaming status indicator, citation rendering (inline and reference list), refusal/uncertainty messaging, and cancellation button. Collection selector for query scope.
- Infrastructure or deployment: OpenAI API key configuration (extends Feature 2's embedding setup); async streaming support in FastAPI; chat session management (ephemeral for v1).
- Documentation: Chat API guide, prompt design notes, context-window management, streaming protocol, citation validation logic, troubleshooting generation failures.

## Affected Domains And Integration Boundaries

- Domain or subsystem: Query understanding and retrieval scoping
  Why it matters: Collection-scoped retrieval is the core control point for preventing out-of-scope answers and ensuring reviewers can reproduce results.
- Domain or subsystem: Context assembly and history management
  Why it matters: Multi-turn context must preserve evidence focus; incorrect history trimming can lose supporting evidence.
- Integration boundary or touchpoint: FastAPI backend to Chroma vector DB (Feature 2)
  Why it matters: Retrieval depends on vector search correctness. Index corruption or stale indexes break answer quality.
- Integration boundary or touchpoint: FastAPI backend to OpenAI LLM API
  Why it matters: LLM provider can fail. Rate limits, token limits, and API errors must be handled gracefully.
- Integration boundary or touchpoint: React frontend to FastAPI chat endpoints
  Why it matters: Streaming protocol and session state must align between frontend and backend; cancellation must be bidirectional.
- Integration boundary or touchpoint: Chat service to Feature 1 & 2 (ingestion, chunking, indexing)
  Why it matters: Retrieved chunks must be valid, indexed, and mapped correctly. Collection and document IDs must match Feature 1's model.

## Protected Behavior

- Behavior that must not regress: Retrieved content must not be treated as instructions or directives. LLM must refuse adversarial retrieved text attempting to override system behavior.
  Protection approach: System prompts that explicitly treat retrieved content as data, not instructions. Adversarial test cases covering prompt injection patterns.
- Behavior that must not regress: Citations must map back to real retrieved chunks. Fabricated or synthetic citations must never appear in final output.
  Protection approach: Citation extraction and validation logic that cross-checks claim text against retrieved chunks. Tests for all citation paths (streaming, non-streaming, partial evidence).
- Behavior that must not regress: Evidence-backed factual claims must remain grounded even with deep multi-turn history.
  Protection approach: Context assembly logic that ranks retrieved context higher than history; integration tests with 5+ turn conversations verifying evidence remains present.
- Behavior that must not regress: Streaming must not bypass grounding or citation checks. Final streamed answer must equal non-streamed answer for the same query.
  Protection approach: Integration tests comparing streaming and non-streaming outputs side by side; assertion that citations are identical.

## Affected Files

- FILE-001 Path: `backend/chat/`
  Reason for change: New module for query parsing, retrieval, context assembly, answer generation, citation extraction, and streaming logic.
- FILE-002 Path: `backend/routers/`
  Reason for change: New FastAPI router for chat endpoints (session creation, turn submission, streaming, history, cancellation).
- FILE-003 Path: `backend/models/`
  Reason for change: New SQLite models for chat sessions, turns, citations, and context metadata; relationships to collections, documents, and chunks.
- FILE-004 Path: `backend/repositories/`
  Reason for change: New repository methods for chat session and turn persistence, history retrieval, and citation storage.
- FILE-005 Path: `frontend/src/screens/`
  Reason for change: New React chat screen component with message list, input form, citation rendering, streaming status, and collection selector.
- FILE-006 Path: `frontend/src/api/`
  Reason for change: New API client methods for chat endpoints (submit turn, stream response, get history, cancel turn).
- FILE-007 Path: `frontend/src/components/`
  Reason for change: New React components for rendering citations (inline and reference list), streaming status, refusal messaging, and message bubbles.
- FILE-008 Path: `requirements.txt`
  Reason for change: Add LLM client library if not already present (e.g., `openai`), and any streaming or async utilities.

## Dependencies

- DEP-001 Internal dependency: Feature 1 (Knowledge Ingestion and Collections) must be complete and stable. Chat queries are scoped to collections; document and collection metadata must be accessible.
  Why it matters: Without stable collections, chat cannot scope queries reliably.
- DEP-002 Internal dependency: Feature 2 (Chunking and Indexing Foundation) must be complete and indexed chunks queryable via vector DB. Chat retrieves from Feature 2's vector index.
  Why it matters: Chat has no evidence source without Feature 2's indexed chunks.
- DEP-003 Internal dependency: Status: Feature 1 is **COMPLETE** (2026-05-05); Feature 2 is **COMPLETE** (2026-05-05). Feature 3 can proceed.
- DEP-004 External dependency: OpenAI API key and account (or alternative LLM provider)
  Why it matters: Answer generation requires external LLM calls. Cost and rate limits must be understood.
- DEP-005 External dependency: Stable Chroma vector DB instance (or equivalent) with Feature 2's indexed chunks populated
  Why it matters: Retrieval depends on vector search. Missing or corrupted indexes will break all answers.
- DEP-006 External dependency: OpenAI Python client library (if not already installed)
  Why it matters: Official client preferred for stability and maintained support.

## Implementation Prerequisites

- PREREQ-001: Features 1 and 2 are fully deployed and tested locally. Sample indexed documents exist with retrievable chunks in Chroma.
- PREREQ-002: OpenAI API key is available and configured (extends Feature 2 setup).
- PREREQ-003: Vector DB (Chroma) is running and queryable with Feature 2's indexed chunks.
- PREREQ-004: FastAPI app from Feature 2 is running and prior routers are stable (collections, documents, ingestion, chunking, indexing).
- PREREQ-005: SQLite schema includes documents, collections, chunks, and embeddings tables from Features 1 and 2.

## Implementation Phases

### Phase 1

Goal: Establish the chat service foundation, retrieval layer, and data model so queries can be submitted and relevant evidence retrieved reliably.
Enabled user scenario(s) or outcome(s): None directly user-visible; this phase creates the retrieval and persistence foundation for chat.

Tasks:

- TASK-001:
  Description: Design and implement SQLite schema for chat sessions, chat turns, citations, and context metadata.
  Linked requirement(s): REQ-003
  Linked acceptance criteria: Supports AC-001, AC-002, AC-003 indirectly by creating persistence layer
  Affected file(s): `backend/models/`, `backend/repositories/`

- TASK-002:
  Description: Implement chat session creation endpoint with collection scope selection and session lifecycle management.
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s): `backend/routers/`, `backend/models/`

- TASK-003:
  Description: Implement query parser and collection-scoped retrieval service that queries Chroma vector DB (Feature 2) and returns top-k ranked chunks with full metadata.
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001
  Affected file(s): `backend/chat/`

- TASK-004:
  Description: Implement context assembly service that builds LLM prompt context from retrieved chunks and prior chat turns, respecting context-window limits and prioritizing evidence.
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-001
  Affected file(s): `backend/chat/`

- TASK-005:
  Description: Implement chat turn submission endpoint that accepts a query, triggers retrieval, assembles context, and stores the turn with retrieved chunks and context used.
  Linked requirement(s): REQ-001, REQ-002, REQ-003
  Linked acceptance criteria: AC-001
  Affected file(s): `backend/routers/`

- TASK-006:
  Description: Implement chat history retrieval endpoint and in-memory turn caching to avoid redundant DB queries.
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-001
  Affected file(s): `backend/chat/`, `backend/repositories/`

Completion criteria:

- CC-001: FastAPI chat endpoints accept and store chat turns with retrieved context. Retrieval returns top-k chunks ranked by similarity.
- CC-002: SQLite persistence exists for chat sessions and turns with relationships to collections, documents, and chunks. History retrieval works correctly.

### Phase 2

Goal: Deliver answer generation with grounding checks, citation extraction and validation, and refusal behavior for weak evidence.
Enabled user scenario(s) or outcome(s): US-001, US-003 (user receives grounded answer with citations or refusal).

Tasks:

- TASK-007:
  Description: Implement LLM prompt template that treats retrieved content as data, explicitly prevents instruction-following from retrieved text, and requests citations.
  Linked requirement(s): REQ-004, REQ-006
  Linked acceptance criteria: AC-002, AC-003
  Affected file(s): `backend/chat/`

- TASK-008:
  Description: Implement answer generation service that calls OpenAI API (or configured LLM provider) with assembled context and system/user prompts.
  Linked requirement(s): REQ-004, REQ-006
  Linked acceptance criteria: AC-002
  Affected file(s): `backend/chat/`

- TASK-009:
  Description: Implement citation extraction logic that parses LLM output, identifies factual claims, and maps them to retrieved chunks.
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-002
  Affected file(s): `backend/chat/`

- TASK-010:
  Description: Implement citation validation that cross-checks extracted citations against retrieved chunks. Reject fabricated or synthetic citations.
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-002
  Affected file(s): `backend/chat/`

- TASK-011:
  Description: Implement refusal and uncertainty detection. Detect weak evidence patterns (too few results, low similarity, ambiguous claim match) and emit explicit refusal or qualification messaging.
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-003
  Affected file(s): `backend/chat/`

- TASK-012:
  Description: Implement turn persistence that stores answer, citations, context used, and generation status. Enable end-to-end inspection by reviewers.
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-002
  Affected file(s): `backend/repositories/`, `backend/routers/`

Completion criteria:

- CC-003: LLM generates answers on top of retrieved context. Citations are extracted, validated, and persisted.
- CC-004: Weak evidence triggers explicit refusal or uncertainty messaging without fabricated answers.

### Phase 3

Goal: Deliver streaming answer delivery with visible generation status, cancellation support, and final citation correctness.
Enabled user scenario(s) or outcome(s): US-004 (user watches answer stream with status; can cancel in progress).

Tasks:

- TASK-013:
  Description: Implement streaming orchestration that breaks answer generation into observable stages (understanding query, retrieving evidence, generating answer, checking groundedness, finalizing citations).
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/chat/`

- TASK-014:
  Description: Implement Server-Sent Events (SSE) or chunked HTTP streaming endpoint that emits answer text tokens and status updates as they become available.
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/routers/`

- TASK-015:
  Description: Implement citation finalization logic that waits until evidence mapping is complete before emitting final citations. Do not emit provisional citations during streaming.
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/chat/`

- TASK-016:
  Description: Implement turn cancellation endpoint and client-side cancellation signal propagation to stop in-progress generation cleanly.
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/routers/`, `backend/chat/`

- TASK-017:
  Description: Implement non-streaming fallback path with identical grounding and citation logic. Verify streaming and non-streaming produce identical final answers and citations.
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/chat/`

- TASK-018:
  Description: Add comprehensive tests for streaming vs. non-streaming path parity, cancellation behavior, and edge cases (network interruption, LLM timeout).
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `backend/tests/`

Completion criteria:

- CC-005: Streaming responses emit visible status and answer text incrementally. Cancellation works cleanly without partial state.
- CC-006: Streamed and non-streamed answers are identical for the same query. Citations are complete and correct in both paths.

### Phase 4

Goal: Deliver the React chat UI on top of stable chat APIs.
Enabled user scenario(s) or outcome(s): US-001, US-002, US-003, US-004 (user-facing chat experience).

Tasks:

- TASK-019:
  Description: Scaffold ReactJS chat client and routing under `frontend/`, including chat screen component structure.
  Linked requirement(s): REQ-001
  Linked acceptance criteria: Supports AC-001 through AC-004 indirectly by creating UI surface
  Affected file(s): `frontend/src/screens/`, `frontend/src/api/`

- TASK-020:
  Description: Implement chat message list component with message bubbles for user and assistant, supporting text, citations (inline and reference list), streaming status, and refusal messaging.
  Linked requirement(s): REQ-004, REQ-005, REQ-007
  Linked acceptance criteria: AC-002, AC-003, AC-004
  Affected file(s): `frontend/src/components/`

- TASK-021:
  Description: Implement chat input form with query text field, collection selector (single or all collections), submit button, and cancellation button visible during streaming.
  Linked requirement(s): REQ-001, REQ-007
  Linked acceptance criteria: AC-001, AC-004
  Affected file(s): `frontend/src/components/`

- TASK-022:
  Description: Implement citation rendering components (inline badges and reference list) that link citations back to document metadata and allow inspection.
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-002
  Affected file(s): `frontend/src/components/`

- TASK-023:
  Description: Implement streaming response handler that consumes SSE stream, displays answer text incrementally, shows status labels (not color alone), and handles cancellation.
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-004
  Affected file(s): `frontend/src/api/`

- TASK-024:
  Description: Implement collection selection UI and session management (create new chat, load prior conversation if sessions are persisted).
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s): `frontend/src/components/`, `frontend/src/screens/`

- TASK-025:
  Description: Add accessibility and keyboard navigation for citation links, message navigation, collection selector, and cancellation button. Use ARIA labels and semantic HTML.
  Linked requirement(s): NFR-004
  Linked acceptance criteria: AC-001 through AC-004 (accessibility cross-cutting)
  Affected file(s): `frontend/src/`

Completion criteria:

- CC-007: Users can submit queries, see streamed answers with citations, refusal messaging, and generation status from the React UI.
- CC-008: UI is keyboard-navigable and text labels make status clear without relying on color alone.

### Phase 5

Goal: End-to-end integration testing, validation of acceptance criteria, and release-readiness verification.
Enabled user scenario(s) or outcome(s): None; integration and validation phase.

Tasks:

- TASK-026:
  Description: Create end-to-end test scenarios covering all acceptance criteria (AC-001 through AC-004) across frontend and backend.
  Linked requirement(s): REQ-001 through REQ-007
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s): `backend/tests/`, `frontend/`

- TASK-027:
  Description: Verify traceability from requirements to implementation and testing. Ensure all REQ-* and AC-* are covered.
  Linked requirement(s): All
  Linked acceptance criteria: All
  Affected file(s): `artifacts/features/3.grounded-chat-and-citations/`

- TASK-028:
  Description: Manual reviewer walkthrough covering grounded answers, citation inspection, refusal behavior, and streaming correctness. Sign-off on acceptance criteria.
  Linked requirement(s): REQ-001 through REQ-007
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004
  Affected file(s): All chat service files

- TASK-029:
  Description: Write setup and troubleshooting documentation for chat service (LLM API configuration, Chroma vector DB setup, context-window tuning, streaming protocol).
  Linked requirement(s): NFR-001 through NFR-005
  Linked acceptance criteria: Supports all AC
  Affected file(s): Documentation

- TASK-030:
  Description: Verify performance benchmarks (retrieval <3s, generation <10s, streaming latency), error handling, and logging. Prepare for downstream Feature 4 (Advanced Retrieval) integration.
  Linked requirement(s): NFR-001, NFR-002
  Linked acceptance criteria: All AC
  Affected file(s): `backend/chat/`, `backend/config.py`

Completion criteria:

- CC-009: All acceptance criteria (AC-001 through AC-004) are validated end to end from the user-facing chat UI.
- CC-010: Setup documentation covers chat API configuration, streaming protocol, context-window management, and troubleshooting.

## Traceability Matrix

- Scenario or outcome -> Plan phase(s): US-001 -> Phases 1, 2, 4; US-002 -> Phases 2, 4; US-003 -> Phases 2, 4; US-004 -> Phases 3, 4; SC-001 -> Phases 1, 2; SC-002 -> Phase 2; SC-003 -> Phase 3
- REQ-001 -> Plan phase / task IDs: Phase 1 / TASK-002, TASK-003, TASK-005; Phase 4 / TASK-021, TASK-024
- REQ-002 -> Plan phase / task IDs: Phase 1 / TASK-003; Phase 2 / TASK-012
- REQ-003 -> Plan phase / task IDs: Phase 1 / TASK-004, TASK-005, TASK-006; Phase 2 / TASK-012
- REQ-004 -> Plan phase / task IDs: Phase 2 / TASK-007, TASK-008, TASK-009, TASK-010, TASK-012; Phase 3 / TASK-015; Phase 4 / TASK-022
- REQ-005 -> Plan phase / task IDs: Phase 2 / TASK-011; Phase 4 / TASK-020
- REQ-006 -> Plan phase / task IDs: Phase 2 / TASK-007, TASK-008
- REQ-007 -> Plan phase / task IDs: Phase 3 / TASK-013, TASK-014, TASK-015, TASK-016, TASK-017, TASK-018; Phase 4 / TASK-023
- AC-001 -> Validation step(s): Phase 1 / TASK-005; Phase 4 / TASK-021, TASK-024; Phase 5 / TASK-026, TASK-028
- AC-002 -> Validation step(s): Phase 2 / TASK-008, TASK-009, TASK-010, TASK-012; Phase 4 / TASK-022; Phase 5 / TASK-026, TASK-028
- AC-003 -> Validation step(s): Phase 2 / TASK-011; Phase 4 / TASK-020; Phase 5 / TASK-026, TASK-028
- AC-004 -> Validation step(s): Phase 3 / TASK-013, TASK-014, TASK-015, TASK-016, TASK-017, TASK-018; Phase 4 / TASK-023; Phase 5 / TASK-026, TASK-028

## Validation Strategy

- TEST-001 Unit tests: Query parsing and collection scoping; retrieval ranking; context assembly with multi-turn history; citation extraction and validation; refusal detection; streaming stage transitions.
- TEST-002 Integration tests: End-to-end query submission through answer generation; chat turn persistence and history retrieval; streaming vs. non-streaming parity; cancellation behavior; adversarial retrieved text handling (prompt injection tests).
- TEST-003 API tests: All chat endpoints (session creation, turn submission, streaming, history, cancellation); error responses; context-window limit handling; invalid collection scope handling.
- TEST-004 Manual verification: Reviewer walkthrough with hand-chosen queries across collections; inspect retrieved chunks and generated citations; verify refusal behavior on weak evidence; test streaming cancellation in UI; side-by-side comparison of streaming and non-streaming answers.
- TEST-005 Observability: Logs and metrics for query, retrieval, context assembly, LLM latency, citation validation, and streaming events. Traceability endpoints so reviewers can inspect answer provenance.

## Rollout Plan

- Release approach: Land the chat retrieval and generation backend (Phases 1 and 2) first, then streaming support (Phase 3), then the React UI (Phase 4). Validate end to end before enabling chat navigation in the frontend.
- Feature flags: Keep chat screen hidden in frontend navigation until Phase 4 is complete and end-to-end testing passes. If chat is added as a new section or modal, gate it behind a simple boolean flag until release.
- Migration needs: No schema migration needed; chat tables are new and additive. Ensure Chroma vector DB is populated with Feature 2's indexed chunks before enabling chat.
- Backward compatibility notes: Chat is a new feature; no prior chat state to preserve. Chat sessions are ephemeral for v1 unless persisted in a future feature.

## Rollback Plan

If a regression is found after the chat UI lands, disable chat navigation entry points first. Backend rollback should preserve chat session and turn records until completion is confirmed, then revert FastAPI routes and SQLite schema changes together. If full code rollback is needed before dependent features land, remove chat tables and routers only after validating no other feature depends on them. LLM API failures during rollback are acceptable (external dependency); fall back to retrieval-only endpoints if needed.

## Risks And Mitigations

- RISK-001 Risk: LLM can fabricate citations to chunks that don't exist or misrepresent retrieved evidence.
  Mitigation: Citation validation logic that cross-checks all citations against retrieved chunks; reject fabricated citations. Tests with adversarial LLM outputs. Reviewers inspect citation metadata for correctness.
- RISK-002 Risk: Streaming can emit partial or incomplete citations if generation is truncated.
  Mitigation: Delay citation finalization until generation is complete. Tests for cancellation during citation generation. Non-streaming path as fallback.
- RISK-003 Risk: Context window inflation with deep multi-turn history can displace evidence and reduce answer quality.
  Mitigation: Context assembly logic that ranks retrieved evidence higher than history. Tests with 5+ turn conversations. Observable context tokens in logs for debugging.
- RISK-004 Risk: Collection-scope filtering could be incorrect, allowing cross-collection answer leakage.
  Mitigation: Explicit scope preservation in retrieval query. Tests that verify retrieved chunks belong to selected collection(s). Reviewer walkthrough showing scope in UI.
- RISK-005 Risk: OpenAI API failures (rate limits, outages, quota exhaustion) can block all chat.
  Mitigation: Graceful error handling with user-facing messages. Rate-limit retry logic. Fallback to retrieval-only responses if generation fails. Monitoring and alerting on API health.
- RISK-006 Risk: Adversarial retrieved text (prompt injection) could override system behavior or suppress citations.
  Mitigation: System prompts that explicitly treat retrieved content as data, not instructions. Unit tests with adversarial payloads. Manual security review by stakeholder.

## Assumptions And Open Questions

- ASM-001 Assumption: Baseline vector similarity retrieval is sufficient for answer quality. Advanced retrieval (HyDE, reranking, query expansion, dynamic routing) is deferred to Feature 4.
  Rationale: Feature 3 focuses on grounded generation; retrieval quality improvements are separate.
- ASM-002 Assumption: Chat sessions are ephemeral (in-memory or short-lived) for v1. Persistent cross-session history is deferred to a later feature.
  Rationale: Session persistence adds scope; v1 focuses on single-conversation demonstration.
- ASM-003 Assumption: Context-window management uses a simple strategy (truncate old history, prioritize recent and retrieved). Sophisticated context ranking comes later.
  Rationale: Simple approach is sufficient for reviewers to see grounded behavior; complex ranking can be tuned later.
- Q-001 Question: Should the refusal threshold be configurable (e.g., minimum similarity score, minimum result count) for experimentation?
  Next step: Defer to Feature 7 (configuration controls) for now; hardcode conservative thresholds in v1.
- Q-002 Question: Should citation format be customizable (inline vs. reference list vs. footnote)?
  Next step: Support both inline and reference list in v1 UI; defer other formats to later UX refinement.


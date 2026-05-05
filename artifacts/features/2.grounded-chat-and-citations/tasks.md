# Task Breakdown

## Metadata

- Feature name: Grounded Chat And Citations
- Related spec: `artifacts/features/2.grounded-chat-and-citations/spec.md`
- Related plan: `artifacts/features/2.grounded-chat-and-citations/plan.md`
- Related design: None
- Owner: Unassigned
- Last updated: 2026-05-05

## Rules

- Keep each task small and testable.
- Include validation tasks, not just implementation tasks.
- Record blockers and dependencies explicitly.
- Link every task back to requirement and acceptance criteria IDs.
- Link every task back to the plan task or phase it came from.
- Link each phase or task group back to the user scenario or outcome it enables when relevant.
- Mark tasks that can run in parallel when they have no dependency relationship.
- Only mark tasks as parallel-safe when they do not create obvious write conflicts or contract conflicts.
- If a task is marked `[P]`, state the ownership boundary and any reintegration expectation explicitly.
- Prefer explicit file or module targets when known from the plan.
- Use these task states consistently: `Not Started`, `In Progress`, `Blocked`, `Done`, `Deferred`.
- Make regression-sensitive or protected behavior explicit in validation or safeguard tasks when relevant.
- For behavior-changing tasks, prefer validation notes that name the failing proof or targeted test expected before the fix.
- Do not finalize task lists until REQ -> AC -> TASK -> validation coverage is complete.

## Status Tracking Requirements

Every task MUST have both a checkbox and a Status field for implementation tracking:

- **Checkbox format**: `- [ ] TASK-ID` or `- [X] TASK-ID` (`[ ]` = not done yet, `[X]` = done)
- **Status field**: `Status: [Not Started|In Progress|Done|Blocked|Deferred]` (initialized to `Not Started`)
- **Session note**: Field for implementation agent to track blockers, progress, or issues
- **Implementation contract**: Implementation agent will keep checkbox and Status field aligned as work progresses

---

## Phase 1: Chat Persistence And Baseline Retrieval

**Goal:** Establish chat persistence, baseline retrieval contracts, and additive backend schema needed for grounded answer execution.

**Enabled scenarios:** US-001, US-002, US-005, SC-001, SC-004

**Completion criteria:**

- [ ] CC-001: A chat session and its turns can be created and persisted with scope, retrieval mode, and terminal status metadata.
- [ ] CC-002: Retrieval returns ranked chunk candidates with the metadata required for answer generation and citations across single-collection and all-collections scopes.

### Tasks

- [X] TASK-001: Design and implement SQLite schema for chat persistence
  Status: Done
  Summary: Create additive SQLite tables for chat_sessions, chat_messages, turn_metadata, refusal_logs, and citation_references. Include columns for session_id, user_id (optional), selected_collection_id, retrieval_mode, question_text, answer_status, refusal_category, created_at, completion_timestamp, and indexed lookups for session queries and citation mapping.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-001, REQ-006
  Linked acceptance criteria: AC-001, AC-006
  Affected file(s) or module(s): `backend/persistence/schema.py`, new migration or idempotent schema-creation script
  Depends on: Feature 1 schema must exist (documents, chunks, collections)
  Can run in parallel: No—foundational schema
  Validation note: Verify schema creates cleanly, all required columns exist with correct types, and can be re-run idempotently. Verify foreign-key constraints link chat turns to existing chunk and document records without breaking.
  Session note: 2026-05-05: Added additive chat tables, indexes, and migration-column support in `backend/persistence/schema.py` for sessions, messages, turn metadata, refusals, citations, and turn logs.

- [X] TASK-002: Create ChatSession and ChatMessage model classes
  Status: Done
  Summary: Implement SQLite-backed model classes for ChatSession (session_id, collection_id, created_at, updated_at, metadata) and ChatMessage (message_id, session_id, turn_order, role, content, answer_status, refusal_category, retrieval_mode_used). Include serialization to JSON for API responses.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/models/chat_session.py` (new), `backend/models/chat_message.py` (new)
  Depends on: TASK-001
  Can run in parallel: No—depends on schema
  Validation note: Write unit tests for create, read, update, list operations; verify message order is preserved per session; verify session_id is stable across re-queries.
  Session note: 2026-05-05: Added `backend/models/chat_session.py` and `backend/models/chat_message.py` with JSON-friendly field mapping used by the chat service layer.

- [X] TASK-003: Create ChatSessionService with CRUD and history retrieval
  Status: Done
  Summary: Implement ChatSessionService with methods for creating a new session with collection_id and retrieval_mode preferences, retrieving session history, adding a turn to a session, and updating turn status (pending → completed/failed/refusal). Preserve all metadata needed for AC-001 compliance.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/services/chat_service.py` (new)
  Depends on: TASK-002
  Can run in parallel: No—depends on models
  Validation note: Unit tests for session creation, add turn, update turn status, retrieve history; verify turns are returned in order; verify metadata is preserved.
  Session note: 2026-05-05: Implemented `backend/services/chat_service.py` for session CRUD, turn lifecycle updates, history retrieval, citation lookup, and log queries.

- [X] TASK-004: Implement semantic retrieval mode over ChromaDB
  Status: Done
  Summary: Create retrieval service method that performs semantic search: convert question to embedding using the configured embedding model, query ChromaDB with collection-scoped filter, return ranked chunks with similarity scores and full chunk metadata (document_id, chunk_id, page, source_url, content snippet).
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/services/retrieval_service.py` (new)
  Depends on: Feature 1 (ChromaDB vectors and chunks must exist)
  Can run in parallel: No—depends on existing chunk records
  Validation note: Unit tests with sample vectors; verify returned chunks are ranked by similarity; verify metadata is complete; verify collection_id filter works correctly.
  Session note: 2026-05-05: Added semantic retrieval in `backend/services/retrieval_service.py` using Chroma plus stored chunk metadata and collection scoping.

- [X] TASK-005: Implement keyword/sparse retrieval mode
  Status: Done
  Summary: Create retrieval service method for keyword or sparse retrieval: tokenize question, search SQLite chunk_metadata using full-text search or substring match on title and content, return ranked results by relevance score (e.g., term frequency or keyword density) with same metadata format as semantic mode.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/services/retrieval_service.py` (shared)
  Depends on: Feature 1 (chunk records must exist)
  Can run in parallel: Yes [P]—Keyword retrieval is independent from semantic; ownership boundary: `backend/services/retrieval_service.py` (coordinate retrieval mode dispatch). Reintegration: both modes must be exposed through unified retrieval interface with mode parameter.
  Validation note: Unit tests with known keywords; verify results are ranked; verify collection filter works; verify metadata matches semantic mode format.
  Session note: 2026-05-05: Added keyword retrieval with overlap-based ranking and the same chunk metadata contract as semantic retrieval.

- [X] TASK-006: Implement hybrid retrieval mode (combination of semantic and keyword)
  Status: Done
  Summary: Create retrieval service method that runs both semantic and keyword searches, merges results by combining normalized scores (e.g., weighted average or rank fusion), and returns unified ranked list of chunks with retrieval_mode_label="hybrid" in metadata.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/services/retrieval_service.py` (shared)
  Depends on: TASK-004, TASK-005
  Can run in parallel: No—depends on both semantic and keyword modes
  Validation note: Unit tests combining semantic and keyword results; verify merged results include both method contributors; verify scores are normalized and combined correctly.
  Session note: 2026-05-05: Added hybrid retrieval with normalized semantic and keyword scores, deduplication by `chunk_id`, and ranked merged output.

- [X] TASK-007: Create unified retrieval orchestration API (RetrievalService)
  Status: Done
  Summary: Implement RetrievalService.retrieve() method that accepts question, collection_id (optional), and retrieval_mode, dispatches to the correct retrieval implementation (semantic, keyword, hybrid), enforces collection-scoped filtering, and returns a consistent RetrievalResult object with retrieved_chunks array, metadata (retrieval_mode_used, collection_filter_applied, rank_count), and query_embedding if applicable.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/services/retrieval_service.py` (shared)
  Depends on: TASK-004, TASK-005, TASK-006
  Can run in parallel: No—integration layer
  Validation note: Test all three modes with same question; verify mode is correctly identified in output; verify collection filtering works for all modes.
  Session note: 2026-05-05: Implemented unified `retrieve()` dispatch with consistent metadata, mode labeling, and collection filtering across all retrieval modes.

- [X] TASK-008: Implement chat session REST API endpoints (create, list, history)
  Status: Done
  Summary: Build Flask REST endpoints for POST /api/chat/sessions (create with collection_id and retrieval_mode), GET /api/chat/sessions (list user's sessions), GET /api/chat/sessions/{session_id} (retrieve session with turn history). Return JSON with session_id, created_at, updated_at, collection_id, retrieval_mode, and turns array with metadata.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/routes/chat.py` (new)
  Depends on: TASK-003
  Can run in parallel: No—depends on service layer
  Validation note: Test session creation with valid collection_id; test list endpoint; test history retrieval; verify all metadata fields are returned.
  Session note: 2026-05-05: Added `POST /api/chat/sessions`, `GET /api/chat/sessions`, and `GET /api/chat/sessions/<session_id>` in `backend/routes/chat.py`.

- [X] TASK-009: Write Phase 1 integration tests (schema, models, retrieval)
  Status: Done
  Summary: Write SQLite + ChromaDB integration tests covering chat schema migration, session CRUD operations, retrieval mode dispatch for semantic/keyword/hybrid searches, collection-scoped filtering, and metadata preservation across all retrieval modes. Use fixtures with sample documents and chunks from feature 1.
  Plan reference: Phase 1
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/tests/integration/test_chat_foundation.py` (new)
  Depends on: TASK-008, TASK-007
  Can run in parallel: No—integration validation
  Validation note: Run all tests; verify CC-001 and CC-002 completion criteria are met; verify no regressions in feature 1 document/chunk storage.
  Session note: 2026-05-05: Added `backend/tests/integration/test_chat_foundation.py` to cover chat schema creation, session persistence, retrieval dispatch, and metadata preservation.

---

## Phase 2: Answer Generation, Answerability, And Citations

**Goal:** Implement grounded answer generation, answerability or refusal logic, citation assembly, and cancellation-safe turn lifecycle behavior.

**Enabled scenarios:** US-001, US-003, US-004, US-005, SC-001, SC-002, SC-003, SC-004

**Completion criteria:**

- [ ] CC-003: Supported questions can complete with grounded answers and structured citations.
- [ ] CC-004: Unsupported or weakly supported questions complete as refusals with visible reason categories rather than fabricated answers.
- [ ] CC-005: The backend exposes enough session, answer, citation, and progress metadata for the chat UI to render without reconstructing grounding logic client-side.

### Tasks

- [X] TASK-010: Design and implement answerability classification service
  Status: Done
  Summary: Create AnswerabilityService that evaluates whether a question can be answered from retrieved evidence using criteria: retrieval_confidence (min similarity score threshold, e.g., >0.5), support_coverage (number or percentage of relevant chunks), evidence_consistency (absence of contradictory chunks), and collection_scope_adequacy. Return answerability_score (0-1), reason_category (no_relevant_evidence, low_confidence, insufficient_support, conflicting_evidence, out_of_domain), and supporting_metrics dict.
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/services/answerability_service.py` (new), `backend/config.py` (extend with thresholds)
  Depends on: TASK-007 (retrieval must provide required metadata)
  Can run in parallel: No—depends on retrieval output structure
  Validation note: Unit tests for each reason_category; test boundary cases (just-above/just-below thresholds); verify metrics are computed correctly.
  Session note: 2026-05-05: Added `backend/services/answerability_service.py` and config thresholds for refusal categories, overlap checks, confidence checks, and conflict detection.

- [X] TASK-011: Implement context packing and token-window management
  Status: Done
  Summary: Create ContextPackingService that ranks and selects a subset of retrieved chunks to fit within a configurable token budget (e.g., 2000 tokens) while preserving relevant evidence. Strategy: rank by relevance score, pack greedily until budget is exceeded, or use importance-weighted packing. Return packed_context list with selected chunks, total_tokens used, and token_budget_remaining.
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/services/context_packing_service.py` (new), `backend/config.py` (extend)
  Depends on: TASK-007 (retrieval output)
  Can run in parallel: Yes [P]—Context packing is independent from answerability; ownership boundary: `backend/services/context_packing_service.py`.
  Validation note: Unit tests with various token budgets; verify selected chunks stay within budget; verify high-relevance chunks are prioritized.
  Session note: 2026-05-05: Added `backend/services/context_packing_service.py` to trim ranked chunks into the configured token budget and report packing metadata.

- [X] TASK-012: Implement citation object model and formatting service
  Status: Done
  Summary: Create Citation model with fields: cited_chunk_id, document_id, document_title, page_or_section, source_url, content_snippet, retrieval_score, retrieval_mode, inline_text_reference (optional). Implement CitationFormattingService.format_citations() to transform retrieved chunks into Citation objects, ensuring each citation maps directly to stored chunk metadata without synthesized content.
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-003, REQ-005
  Linked acceptance criteria: AC-003, AC-005
  Affected file(s) or module(s): `backend/models/citation.py` (new), `backend/services/citation_service.py` (new)
  Depends on: TASK-007 (retrieval metadata must be complete)
  Can run in parallel: No—depends on retrieval structure
  Validation note: Unit tests mapping retrieved chunks to Citation objects; verify no synthesized content appears; verify all metadata fields are preserved.
  Session note: 2026-05-05: Added `backend/models/citation.py` and `backend/services/citation_service.py` to format stored chunk evidence into structured citations.

- [X] TASK-013: Implement response-generation service (grounded answer from context)
  Status: Done
  Summary: Create ResponseGenerationService that accepts question, packed_context (from TASK-011), and optional configuration, then calls the configured generation provider (e.g., LLM API or OpenAI model) with a prompt that explicitly grounds generation in the provided context. Return GeneratedResponse with answer_text, citation_indices (array of cited chunk positions in context), internal_reasoning (optional), and generation_metadata (model, tokens_used, finish_reason).
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/services/generation_service.py` (new), `backend/providers/` (new)
  Depends on: TASK-011 (context packing)
  Can run in parallel: Yes [P]—Generation service is independent from answerability evaluation; ownership boundary: `backend/services/generation_service.py` (abstract generation interface for provider swapping). Reintegration: must accept packed context and return structured citation indices.
  Validation note: Unit tests with mock generator; verify answer references cited context; verify citation indices map back to packed context chunks.
  Session note: 2026-05-05: Added `backend/services/generation_service.py` with a deterministic local extractive provider in `backend/providers/local_extractive.py`.

- [X] TASK-014: Implement refusal response generation
  Status: Done
  Summary: Create RefusalService that when answerability thresholds are not met, generates a user-visible refusal message with visible reason category (e.g., "I don't have enough information to answer this question" for low_confidence, "The documents contain conflicting information" for conflicting_evidence). Return RefusalResponse with refusal_text, reason_category, supporting_metrics dict, and suggestion_for_user (optional, e.g., "Try asking about X instead").
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/services/refusal_service.py` (new)
  Depends on: TASK-010 (answerability evaluation must complete first)
  Can run in parallel: Yes [P]—Refusal generation is independent from answer generation; ownership boundary: `backend/services/refusal_service.py`.
  Validation note: Unit tests for each reason_category; verify refusal text is user-friendly; verify metrics are included.
  Session note: 2026-05-05: Added `backend/services/refusal_service.py` with user-facing refusal text and visible reason-category mapping.

- [X] TASK-015: Implement chat turn orchestration (retrieval → answerability → response)
  Status: Done
  Summary: Create ChatOrchestrationService that coordinates the complete turn workflow: retrieve evidence, pack context, evaluate answerability, then either generate a grounded answer (with citations) or a refusal. Return ChatTurnResult with result_type (answer|refusal), answer (if answer_type), refusal (if refusal_type), citations_array, retrieval_metadata, answerability_score, and terminal_status (completed|failed|cancelled).
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-001, REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-001, AC-003, AC-004, AC-006
  Affected file(s) or module(s): `backend/services/chat_orchestration_service.py` (new)
  Depends on: TASK-011, TASK-012, TASK-013, TASK-014
  Can run in parallel: No—orchestration layer
  Validation note: End-to-end tests covering answer path, refusal path, and error path; verify all metadata flows through correctly.
  Session note: 2026-05-05: Added `backend/services/chat_orchestration_service.py` to coordinate retrieval, packing, answerability, answer generation or refusal, citation persistence, and logs.

- [X] TASK-016: Implement turn-cancellation and state-cleanup logic
  Status: Done
  Summary: Add cancellation support to chat turns: mark in-progress turns as cancelled, preserve partial progress metadata (what was retrieved, why it was cancelled), and prevent final citations from being sent if cancellation is requested during generation. Implement CancellationManager with methods cancel_turn(turn_id) and is_cancelled(turn_id) that work safely across the orchestration pipeline.
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/services/cancellation_manager.py` (new)
  Depends on: TASK-015 (must integrate into orchestration)
  Can run in parallel: No—depends on orchestration
  Validation note: Test cancellation during retrieval, during generation, and after completion; verify partial state is preserved; verify final citations are not sent if cancelled.
  Session note: 2026-05-05: Added `backend/services/cancellation_manager.py` and integrated cancellation checkpoints into the orchestration flow.

- [X] TASK-017: Implement ask-question API endpoint (non-streamed)
  Status: Done
  Summary: Build Flask endpoint POST /api/chat/sessions/{session_id}/ask that accepts question text, optional retrieval_mode override, and optional collection_id override. Call ChatOrchestrationService, persist the turn with result, and return ChatTurnResult as JSON with answer_text or refusal_text, citations array, retrieval_mode_used, and completion metadata.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-001, REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-001, AC-003, AC-004, AC-006
  Affected file(s) or module(s): `backend/routes/chat.py` (shared)
  Depends on: TASK-015
  Can run in parallel: No—depends on orchestration service
  Validation note: Test with supported questions, unsupported questions, and error scenarios; verify response JSON includes all required fields.
  Session note: 2026-05-05: Added synchronous `POST /api/chat/sessions/<session_id>/ask` returning grounded answers or refusals with citations and turn metadata.

- [X] TASK-018: Implement streamed answer endpoint (Server-Sent Events or line-delimited JSON)
  Status: Done
  Summary: Build Flask endpoint POST /api/chat/sessions/{session_id}/ask-stream that accepts same parameters as TASK-017 but returns streamed progress events: { event: "retrieving", ... }, { event: "context_packed", ... }, { event: "generating", ... }, { event: "answer_chunk", text: "..." }, { event: "completed", citations: [...] }. Respect cancellation requests and ensure citations are sent only with completed event.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-001, REQ-006
  Linked acceptance criteria: AC-001, AC-006
  Affected file(s) or module(s): `backend/routes/chat.py` (shared)
  Depends on: TASK-015, TASK-016
  Can run in parallel: Yes [P]—Streamed endpoint is parallel variant of non-streamed; ownership boundary: `backend/routes/chat.py` (both endpoints share orchestration logic). Reintegration: both must produce identical final citations and turn state.
  Validation note: Test streaming with curl or EventSource; verify all events appear in order; verify citations appear only in completed event.
  Session note: 2026-05-05: Added NDJSON streaming at `POST /api/chat/sessions/<session_id>/ask-stream` with ordered progress events and final citations only on completion.

- [X] TASK-019: Implement cancel-generation endpoint
  Status: Done
  Summary: Build Flask endpoint POST /api/chat/sessions/{session_id}/turns/{turn_id}/cancel that marks a turn as cancelled, stops in-progress generation or retrieval, and returns the partial state if available. Verify cancellation prevents final citations from being sent.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/routes/chat.py` (shared)
  Depends on: TASK-016
  Can run in parallel: Yes [P]—Cancellation endpoint is independent; ownership boundary: `backend/routes/chat.py`.
  Validation note: Test cancellation during in-progress turn; verify turn is marked cancelled; verify final response is not sent.
  Session note: 2026-05-05: Added `POST /api/chat/sessions/<session_id>/turns/<turn_id>/cancel` to mark active turns as cancelled and return partial state.

- [X] TASK-020: Implement citation-detail endpoint
  Status: Done
  Summary: Build Flask endpoint GET /api/chat/sessions/{session_id}/citations/{citation_id} that returns full citation detail including document_id, document_title, chunk_id, chunk_order, page_or_section, source_url, full_snippet, retrieval_score, retrieval_mode, and embedding_or_rerank_score if applicable. Verify citation_id maps to a stored chunk in the knowledge base.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `backend/routes/chat.py` (shared)
  Depends on: TASK-012 (citation model must be finalized)
  Can run in parallel: Yes [P]—Citation detail is independent; ownership boundary: `backend/routes/chat.py`.
  Validation note: Test retrieving citation for a known chunk; verify all metadata fields are present; verify citation maps back to stored chunk in documents table.
  Session note: 2026-05-05: Added `GET /api/chat/sessions/<session_id>/citations/<citation_id>` to expose full evidence detail for cited chunks.

- [X] TASK-021: Write Phase 2 integration tests (orchestration, answers, refusals, citations)
  Status: Done
  Summary: Write comprehensive integration tests covering chat orchestration for supported questions (verify grounded answer), unsupported questions (verify refusal with reason_category), citation mapping, streaming completion, and cancellation. Use fixtures with real ingested documents from feature 1. Test scenarios: ask question with good evidence, ask question with weak evidence, ask question with conflicting evidence, cancel during generation.
  Plan reference: Phase 2
  Linked requirement(s): REQ-001, REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-001, AC-003, AC-004, AC-006
  Affected file(s) or module(s): `backend/tests/integration/test_chat_orchestration.py` (new)
  Depends on: TASK-017, TASK-018, TASK-019
  Can run in parallel: No—integration validation
  Validation note: Run all tests; verify CC-003, CC-004, and CC-005 completion criteria are met; verify no regressions in feature 1 or feature 2 phase 1.
  Session note: 2026-05-05: Added `backend/tests/integration/test_chat_orchestration.py` for supported answers, refusal behavior, streaming events, and citation-bearing completions.

---

## Phase 3: Chat UI And Citation Inspection

**Goal:** Deliver the chat UI and citation inspection workflow on top of the stabilized backend contracts.

**Enabled scenarios:** US-001, US-002, US-003, US-004, US-005, SC-001, SC-002, SC-003, SC-004

**Completion criteria:**

- [ ] CC-006: Reviewers can ask questions, inspect history, observe progress states, and cancel in-progress answers from the chat UI.
- [ ] CC-007: Citation presentation and citation-detail inspection expose the required source metadata and support traceability back to stored chunks.

### Tasks

- [X] TASK-022: Build Chat page HTML structure and base styling
  Status: Done
  Summary: Create `frontend/chat.html` with semantic HTML for: question input form, collection selector dropdown, retrieval-mode selector (semantic, keyword, hybrid), streaming control toggle, chat history panel with message threads, answer panel with status indicator, citations panel with inline or reference-list presentation, citation-detail modal. Add baseline CSS for layout, panels, and form elements.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-001, REQ-006
  Linked acceptance criteria: AC-001, AC-006
  Affected file(s) or module(s): `frontend/chat.html` (new), `frontend/styles.css` (extend)
  Depends on: TASK-017 (API must be ready for testing)
  Can run in parallel: No—foundational UI structure
  Validation note: Verify HTML is semantic and accessible; verify all required sections are present (history, input, collection selector, retrieval selector, answer, citations, modal).
  Session note: 2026-05-05: Added `frontend/chat.html` and extended `frontend/styles.css` with the chat layout, session list, panels, modals, and status treatments.

- [X] TASK-023: Implement session management (create, list, select) in Chat UI
  Status: Done
  Summary: Write JavaScript in `frontend/chat.js` to create a new chat session (POST /api/chat/sessions) with selected collection_id and retrieval_mode, list user's past sessions (GET /api/chat/sessions), switch between sessions, and load selected session's history. Display session metadata (created_at, collection_name, last_message) in session list. Persist selected session_id in browser session or URL.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `frontend/chat.js` (new)
  Depends on: TASK-008 (session API), TASK-022 (HTML structure)
  Can run in parallel: No—depends on API and HTML
  Validation note: Test creating new session; test listing sessions; test switching between sessions; verify history is loaded correctly.
  Session note: 2026-05-05: Implemented session creation, listing, selection, URL persistence, and history loading in `frontend/chat.js`.

- [X] TASK-024: Implement question submission and response handling (non-streamed)
  Status: Done
  Summary: Write JavaScript to handle question form submission: collect question text, selected collection_id, selected retrieval_mode, POST to /api/chat/sessions/{session_id}/ask, parse response (answer or refusal), render answer in answer panel, render citations in citations panel, add turn to chat history.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-001, REQ-003
  Linked acceptance criteria: AC-001, AC-003
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-017, TASK-022
  Can run in parallel: No—depends on non-streamed API
  Validation note: Test question submission with supported and unsupported questions; verify response is rendered; verify citations appear.
  Session note: 2026-05-05: Added non-streamed question submission, response parsing, answer or refusal rendering, and turn refresh in `frontend/chat.js`.

- [X] TASK-025: Implement streamed response handling with progress visibility
  Status: Done
  Summary: Write JavaScript to handle streamed responses (Server-Sent Events or line-delimited JSON): open event source or fetch stream to /api/chat/sessions/{session_id}/ask-stream, parse status events (retrieving, context_packed, generating, answer_chunk, completed), show live status indicator and answer text accumulation, prevent citations from being shown until completed event, finalize answer when completed event arrives.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-018, TASK-022
  Can run in parallel: Yes [P]—Streamed handling is parallel to non-streamed; ownership boundary: `frontend/chat.js` (coordinate form submission to choose endpoint). Reintegration: both paths must render identical final answers and citations.
  Validation note: Test streaming with actual server; verify status updates appear in real-time; verify answer accumulates; verify citations appear only after completed.
  Session note: 2026-05-05: Added NDJSON stream handling, progress-state updates, partial answer rendering, and completion handoff in `frontend/chat.js`.

- [X] TASK-026: Implement cancellation UI and cancel handler
  Status: Done
  Summary: Add a cancel button to the answer panel that is enabled during in-progress answer generation. Write JavaScript to POST /api/chat/sessions/{session_id}/turns/{turn_id}/cancel, show cancellation status, and stop listening to event stream if streaming.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-019, TASK-025
  Can run in parallel: Yes [P]—Cancellation UI is independent; ownership boundary: `frontend/chat.js`.
  Validation note: Test clicking cancel during in-progress answer; verify cancel request is sent; verify UI updates to show cancelled state.
  Session note: 2026-05-05: Added cancel button state management and cancel-request handling for in-progress streamed turns.

- [X] TASK-027: Implement inline citations rendering with reference markers
  Status: Done
  Summary: Modify answer-panel rendering to parse answer text and citation objects, insert reference markers (e.g., [1], [2] superscript or linked numbers) where citations apply, and build a reference list at the bottom showing citation metadata (document_title, page_or_section, source_url if available). Make reference markers clickable to open citation detail modal.
  Plan reference: Phase 3 / TASK-008
  Linked requirement(s): REQ-003, REQ-005
  Linked acceptance criteria: AC-003, AC-005
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-024 (response handling), TASK-020 (citation detail API)
  Can run in parallel: Yes [P]—Citation rendering is independent from answer rendering; ownership boundary: `frontend/chat.js` (answer panel rendering).
  Validation note: Test answer with citations; verify reference markers appear; verify reference list is shown; verify markers are clickable.
  Session note: 2026-05-05: Added clickable inline citation markers in the answer panel plus a reference-list citation panel fed from stored citation objects.

- [X] TASK-028: Implement citation-detail modal interaction
  Status: Done
  Summary: Write JavaScript to open a modal when user clicks a citation reference marker. Fetch citation detail from GET /api/chat/sessions/{session_id}/citations/{citation_id}, display document_title, chunk_id, page_or_section, source_url, full_snippet (content preview), retrieval_score, and retrieval_mode. Include a "View in Library" link to the document in the Document Library.
  Plan reference: Phase 3 / TASK-008
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-020, TASK-027
  Can run in parallel: Yes [P]—Citation detail modal is independent; ownership boundary: `frontend/chat.js`.
  Validation note: Test clicking citation marker; verify modal opens; verify all metadata is displayed; verify "View in Library" link works.
  Session note: 2026-05-05: Added citation-detail modal fetch flow and `View In Library` deep links to `document-library.html?document_id=...`.

- [X] TASK-029: Implement refusal display with reason category
  Status: Done
  Summary: Add refusal-specific rendering to answer panel: when result_type is refusal, display refusal_text prominently and show reason_category as a subtitle or info label (e.g., "Unable to answer: Low confidence in available evidence"). Display supporting_metrics if available (e.g., "Found 2 chunks but similarity was below threshold").
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-024 (response handling)
  Can run in parallel: Yes [P]—Refusal rendering is independent; ownership boundary: `frontend/chat.js` (answer panel).
  Validation note: Test with refusal response; verify refusal text and reason_category are displayed; verify metrics are shown if present.
  Session note: 2026-05-05: Added refusal-specific rendering with visible reason category and supporting metrics in the answer panel.

- [X] TASK-030: Implement chat history rendering and persistence
  Status: Done
  Summary: Write JavaScript to render chat history from GET /api/chat/sessions/{session_id}: display message thread with user questions on the left, assistant answers on the right, refusals highlighted, and timestamps. Preserve scroll position and message order. Auto-load history when switching sessions.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-023 (session selection)
  Can run in parallel: Yes [P]—History rendering is independent; ownership boundary: `frontend/chat.js` (history panel).
  Validation note: Test loading history for a session with multiple turns; verify all turns are displayed; verify order is correct; verify scroll position is preserved.
  Session note: 2026-05-05: Added threaded history rendering with timestamps, refusal styling, and session-switch reload behavior.

- [X] TASK-031: Implement collection and retrieval-mode selectors
  Status: Done
  Summary: Add JavaScript to populate collection selector dropdown (fetch from GET /api/collections, show collection names), retrieval-mode selector (hardcoded options: semantic, keyword, hybrid), and optional advanced controls (streaming toggle, debug panel toggle). Persist selected values in session storage or URL and apply them to new questions.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `frontend/chat.js` (shared)
  Depends on: TASK-022 (HTML structure)
  Can run in parallel: Yes [P]—Selector logic is independent; ownership boundary: `frontend/chat.js`.
  Validation note: Test collection dropdown; test retrieval-mode selector; verify selected values are applied to next question; verify persistence works across page reloads.
  Session note: 2026-05-05: Added collection loading from `/api/collections`, retrieval-mode controls, streaming and debug toggles, and sessionStorage persistence.

- [X] TASK-032: Write Phase 3 frontend integration test plan (manual browser verification)
  Status: Done
  Summary: Document manual test scenarios for chat UI: create session, ask supported question and verify answer with citations, ask unsupported question and verify refusal with reason, inspect citation detail, switch between sessions, verify history persistence, test cancellation during streaming, test all retrieval modes, verify collection scoping works. Prepare checklist for visual verification.
  Plan reference: Phase 3
  Linked requirement(s): REQ-001, REQ-003, REQ-004, REQ-005, REQ-006
  Linked acceptance criteria: AC-001, AC-003, AC-004, AC-005, AC-006
  Affected file(s) or module(s): `artifacts/features/2.grounded-chat-and-citations/manual-test-checklist.md` (new)
  Depends on: TASK-031 (all UI features ready for testing)
  Can run in parallel: No—planning task
  Validation note: Create checklist covering all user stories and acceptance criteria; verify each test scenario can be executed in the browser.
  Session note: 2026-05-05: Added `artifacts/features/2.grounded-chat-and-citations/manual-test-checklist.md` covering sessions, answers, refusals, streaming, cancellation, citations, and regressions.

---

## Phase 4: Hardening, Validation, And Observability

**Goal:** Harden the retrieval and chat behavior with automated validation and manual review evidence before feature closure.

**Enabled scenarios:** SC-001, SC-002, SC-003, SC-004

**Completion criteria:**

- [ ] CC-008: Automated checks cover the backend behavior that produces user-visible grounded answer, refusal, citation, and turn-state outcomes.
- [ ] CC-009: Manual verification confirms the chat UI meets the acceptance criteria and keeps citations and refusal reasons inspectable.

### Tasks

- [X] TASK-033: Add unit tests for retrieval modes (semantic, keyword, hybrid)
  Status: Done
  Summary: Write comprehensive unit tests for retrieval service covering semantic search ranking, keyword matching and ranking, hybrid score combination, collection scoping, and metadata preservation. Use fixtures with sample chunks and verify returned results are correctly ranked by each mode. Test edge cases: empty query, no matching chunks, single matching chunk.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/tests/unit/test_retrieval_modes.py` (new)
  Depends on: TASK-004, TASK-005, TASK-006
  Can run in parallel: Yes [P]—Unit tests for retrieval are independent; ownership boundary: one test function per retrieval mode.
  Validation note: Run pytest; verify all retrieval tests pass; verify coverage > 85% for retrieval service.
  Session note: 2026-05-05: Added `backend/tests/unit/test_retrieval_modes.py` for semantic, keyword, hybrid, scoping, and edge-case retrieval behavior.

- [X] TASK-034: Add unit tests for answerability classification
  Status: Done
  Summary: Write unit tests for answerability service covering all refusal reason categories (no_relevant_evidence, low_confidence, insufficient_support, conflicting_evidence, out_of_domain) with synthetic retrieved-chunk fixtures. Test threshold boundaries (just above and just below thresholds). Verify reason_category output is correct for each scenario.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/tests/unit/test_answerability.py` (new)
  Depends on: TASK-010
  Can run in parallel: Yes [P]—Answerability unit tests are independent.
  Validation note: Run pytest; verify all threshold tests pass; verify reason categories are correctly assigned.
  Session note: 2026-05-05: Added `backend/tests/unit/test_answerability.py` covering refusal categories and threshold boundaries.

- [X] TASK-035: Add unit tests for citation mapping and formatting
  Status: Done
  Summary: Write unit tests for citation service ensuring that retrieved chunks are correctly mapped to Citation objects and contain no synthesized content. Test scenarios: chunk with all metadata fields, chunk with minimal metadata, multiple chunks with overlapping information. Verify citation snapshots are immutable and trace back to stored chunks.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-003, REQ-005
  Linked acceptance criteria: AC-003, AC-005
  Affected file(s) or module(s): `backend/tests/unit/test_citation_formatting.py` (new)
  Depends on: TASK-012
  Can run in parallel: Yes [P]—Citation unit tests are independent.
  Validation note: Run pytest; verify all citation tests pass; verify no synthesized content.
  Session note: 2026-05-05: Added `backend/tests/unit/test_citation_formatting.py` to verify citation mapping preserves stored metadata without synthesized content.

- [X] TASK-036: Add regression-protection tests for citation correctness across streaming and non-streamed paths
  Status: Done
  Summary: Write integration tests ensuring that streamed and non-streamed answer paths produce identical final citations, turn state, and answer metadata. Test scenarios: ask question via non-streamed endpoint, ask same question via streamed endpoint, compare final citations and answer text for equivalence. Verify partial streaming does not corrupt final state.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-003, REQ-006
  Linked acceptance criteria: AC-003, AC-006
  Affected file(s) or module(s): `backend/tests/integration/test_citation_consistency.py` (new)
  Depends on: TASK-017, TASK-018
  Can run in parallel: No—regression-protection test
  Validation note: Run tests; verify streamed and non-streamed paths produce identical results; verify no citations are lost.
  Session note: 2026-05-05: Added `backend/tests/integration/test_citation_consistency.py` to compare final answer and citation outputs across streamed and non-streamed paths.

- [X] TASK-037: Add regression-protection tests for cancellation correctness
  Status: Done
  Summary: Write integration tests to ensure cancellation prevents final citations from being sent, preserves partial state if available, and does not corrupt turn history. Test scenarios: cancel during retrieval, cancel during generation, verify turn is marked cancelled, verify final response is not sent.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/tests/integration/test_cancellation.py` (new)
  Depends on: TASK-016, TASK-019
  Can run in parallel: No—regression-protection test
  Validation note: Run tests; verify cancellation is respected; verify no citations are sent after cancellation.
  Session note: 2026-05-05: Added `backend/tests/integration/test_cancellation.py` to verify cancellation prevents final citation emission and preserves cancelled turn state.

- [X] TASK-038: Add regression-protection tests for refusal correctness
  Status: Done
  Summary: Write integration tests ensuring refusals are triggered correctly, reason categories are assigned accurately, and refusals never appear as confident answers. Test scenarios: question with no relevant evidence (verify no_relevant_evidence), question with low-confidence matches (verify low_confidence), question with conflicting evidence (verify conflicting_evidence), verify refusal text is user-friendly and does not mention "error" or "failure".
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/tests/integration/test_refusal_correctness.py` (new)
  Depends on: TASK-014, TASK-021
  Can run in parallel: No—regression-protection test
  Validation note: Run tests; verify refusal scenarios are correctly identified; verify reason categories are accurate.
  Session note: 2026-05-05: Added `backend/tests/integration/test_refusal_correctness.py` for no-evidence, low-confidence, and conflicting-evidence refusal paths.

- [X] TASK-039: Add unit tests for context packing and token budgeting
  Status: Done
  Summary: Write unit tests for context packing service ensuring that selected chunks fit within token budget and high-relevance chunks are prioritized. Test scenarios: budget larger than all chunks, budget smaller than all chunks, budget that fits some but not all chunks. Verify total_tokens_used <= token_budget and returned chunks are highest-ranked.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/tests/unit/test_context_packing.py` (new)
  Depends on: TASK-011
  Can run in parallel: Yes [P]—Context packing unit tests are independent.
  Validation note: Run pytest; verify token budgeting is correct; verify high-relevance chunks are selected first.
  Session note: 2026-05-05: Added `backend/tests/unit/test_context_packing.py` to verify token-budget enforcement and relevance-prioritized selection.

- [X] TASK-040: Add observability logging for chat turns and decisions
  Status: Done
  Summary: Ensure all chat turns, retrieval results, answerability decisions, and refusals are logged with: turn_id, session_id, question_text, retrieval_mode_used, retrieved_chunk_count, answerability_score, refusal_category (if applicable), answer_length (in tokens), and final_citation_count. Make logs queryable through API endpoint (optional: GET /api/chat/logs) or UI debug panel.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `backend/models/chat_turn_log.py` (new), `backend/services/chat_service.py` (extend)
  Depends on: TASK-015 (orchestration must complete)
  Can run in parallel: Yes [P]—Logging is independent; ownership boundary: logging and optional log-query endpoint.
  Validation note: Verify logs are created for all turns; verify all fields are recorded; verify logs can be queried; verify logs are human-readable.
  Session note: 2026-05-05: Added `backend/models/chat_turn_log.py`, chat-turn logging in the orchestration flow, and `GET /api/chat/logs` for queryable debug output.

- [ ] TASK-041: Perform manual end-to-end chat workflow verification
  Status: Blocked
  Summary: Follow Chat manual test checklist: create session, ask a supported question (verify answer with citations), ask an unsupported question (verify refusal with reason_category), inspect citation detail modal, test all retrieval modes, verify collection scoping, test streaming and cancellation, verify history persistence. Screenshot or record observed state for each step.
  Plan reference: Phase 4 / TASK-010
  Linked requirement(s): REQ-001, REQ-003, REQ-004, REQ-005, REQ-006
  Linked acceptance criteria: AC-001, AC-003, AC-004, AC-005, AC-006
  Affected file(s) or module(s): `frontend/`, `backend/`
  Depends on: TASK-032 (test checklist ready)
  Can run in parallel: No—manual verification task
  Validation note: Execute all chat test scenarios; verify all functionality works; record any issues for follow-up; mark CC-009 if all steps pass.
  Session note: 2026-05-05: Blocked in this environment because there is no browser/GUI automation path to truthfully execute and capture the manual end-to-end chat workflow.

- [ ] TASK-042: Perform manual citation-detail inspection verification
  Status: Blocked
  Summary: Verify that each citation in an answer can be inspected through the citation-detail modal and that the displayed metadata (document_title, chunk_id, page_or_section, source_url, retrieval_score, retrieval_mode) is accurate and traces back to stored chunks in the Document Library. Verify no synthesized or uncited content appears.
  Plan reference: Phase 4 / TASK-010
  Linked requirement(s): REQ-003, REQ-005
  Linked acceptance criteria: AC-003, AC-005
  Affected file(s) or module(s): `frontend/`, `backend/`
  Depends on: TASK-041 (citation detail is accessible)
  Can run in parallel: No—manual verification task
  Validation note: Inspect multiple citations; verify all metadata is accurate; verify citations match stored chunks; record any discrepancies.
  Session note: 2026-05-05: Blocked in this environment because citation-detail inspection requires interactive browser validation against the rendered UI and linked document view.

- [ ] TASK-043: Run final traceability audit and closure
  Status: Blocked
  Summary: Verify complete coverage: REQ-001 through REQ-006, AC-001 through AC-006 are all mapped to tasks and validated. Ensure no major acceptance criteria are orphaned. Verify all 4 phases have completion criteria checks. Cross-check that feature 1 (ingestion) integration is not broken by chat additions. Document any deferred work or follow-ups. Finalize feature readiness.
  Plan reference: Phase 4
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
  Affected file(s) or module(s): `artifacts/features/2.grounded-chat-and-citations/tasks.md` (final review)
  Depends on: TASK-041, TASK-042 (manual verification complete)
  Can run in parallel: No—closure task
  Validation note: Verify all REQ/AC mappings are complete; verify all CC are checked; verify no test gaps exist; verify feature 1 tests still pass.
  Session note: 2026-05-05: Automated traceability and regression coverage are in place, but final closure remains blocked until TASK-041 and TASK-042 complete with real manual browser verification evidence.

---

## Notes Per Task

### TASK-001
Chat schema should be additive: new tables for chat_sessions, chat_messages, turn_metadata, refusal_logs, citation_references. Use idempotent schema creation (IF NOT EXISTS clauses). Consider foreign keys: chat_messages.session_id → chat_sessions.session_id, turn references → chunk records via chunk_id. Keep separate from feature 1 document tables to avoid entanglement.

### TASK-002
ChatSession model: session_id (UUID), user_id (optional), collection_id (FK to collections), retrieval_mode (enum: semantic, keyword, hybrid), created_at, updated_at, metadata dict. ChatMessage model: message_id (UUID), session_id (FK), turn_order (int), role (user|assistant), content (text), answer_status (pending|completed|failed|cancelled|refused), refusal_category (enum or null), retrieval_mode_used (enum). Ensure turn_order is auto-incremented per session.

### TASK-003
ChatSessionService: create_session(collection_id, retrieval_mode) → ChatSession, add_turn(session_id, question_text) → ChatMessage, update_turn_status(turn_id, status, result) → void, get_session_history(session_id) → [ChatMessage...]. Each method should preserve metadata and enforce status transitions (pending → completed/refused/cancelled only, not backwards).

### TASK-004
RetrievalService.retrieve_semantic(): embed question, query ChromaDB with collection filter, return ranked chunks. Handle missing embedding model gracefully. Verify similarity_score field is included in output.

### TASK-005
RetrievalService.retrieve_keyword(): tokenize question, search SQLite full-text or substring, rank by relevance (term frequency or keyword overlap), return results in same format as semantic. Metadata structure must match semantic output for unification.

### TASK-006
RetrievalService.retrieve_hybrid(): run both semantic and keyword, combine scores (e.g., normalize both to 0-1, weighted average with configurable weights like 0.6*semantic + 0.4*keyword), deduplicate by chunk_id, rank merged results, return with retrieval_mode="hybrid".

### TASK-007
RetrievalService.retrieve(question, collection_id=None, retrieval_mode="semantic") → RetrievalResult. RetrievalResult: { retrieved_chunks: [Chunk...], metadata: { retrieval_mode_used, collection_filter_applied, count, query_embedding (if semantic) } }. Enforce collection scoping: if collection_id is provided, filter chunks to that collection; if None, include all collections.

### TASK-008
Chat session endpoints: POST /api/chat/sessions with {collection_id, retrieval_mode} → {session_id, created_at, ...}, GET /api/chat/sessions → [{session_id, name, created_at, ...}], GET /api/chat/sessions/{session_id} → {session_id, turns: [...]}.

### TASK-009
Integration tests should use sample documents and chunks from feature 1. Test that schema creation doesn't break existing document tables. Verify session and message records can be created and retrieved. Verify all three retrieval modes return consistent metadata format.

### TASK-010
AnswerabilityService: evaluate(retrieved_chunks) → AnswerabilityResult { answerability_score: 0-1, reason_category, metrics: {min_similarity, chunk_count, consistency_score} }. Configurable thresholds (in config.py): min_similarity_threshold (default 0.5), min_chunk_count (default 1), consistency_threshold (default 0.8). reason_categories: no_relevant_evidence, low_confidence, insufficient_support, conflicting_evidence, out_of_domain.

### TASK-011
ContextPackingService: pack(chunks, token_budget, strategy="greedy") → PackedContext { selected_chunks: [Chunk...], total_tokens, budget_remaining }. Token counting: use tiktoken or similar library to estimate tokens. Greedy strategy: rank by relevance, add chunks until budget is exceeded, select last N that fit.

### TASK-012
Citation model: { chunk_id, document_id, document_title, page_or_section, source_url, content_snippet, retrieval_score, retrieval_mode, inline_reference (optional) }. CitationFormattingService.format_citations(retrieved_chunks) → [Citation...]. Preserve all metadata from original chunks; never synthesize content.

### TASK-013
ResponseGenerationService: __init__ accepts provider config (e.g., model_name, api_key). generate(question, packed_context) → GeneratedResponse { answer_text, citation_indices: [int...], generation_metadata: {model, tokens_used, finish_reason} }. Prompt design: instruct model to answer based only on provided context and cite relevant chunks. citation_indices: array of indices into packed_context.chunks that are cited in answer_text.

### TASK-014
RefusalService: generate_refusal(answerability_result) → RefusalResponse { refusal_text, reason_category, metrics: {...}, suggestion: optional str }. Hardcoded templates per reason_category:
- no_relevant_evidence: "I don't have any documents that match this question."
- low_confidence: "I found some related information, but I'm not confident enough to answer this question."
- insufficient_support: "The available documents don't have enough information to answer this comprehensively."
- conflicting_evidence: "The documents contain conflicting information on this topic."
- out_of_domain: "This question is outside the scope of available documents."

### TASK-015
ChatOrchestrationService: orchestrate_turn(session_id, question_text, retrieval_mode_override=None, collection_override=None) → ChatTurnResult { result_type: "answer"|"refusal"|"error"|"cancelled", answer: Answer{...} or refusal: Refusal{...}, citations: [Citation...], retrieval_metadata, answerability_score, terminal_status }. Internal flow: 1. retrieve(question, collection), 2. pack_context(chunks), 3. evaluate_answerability(chunks), 4a. if answerable: generate(question, packed_context) + format_citations, 4b. if not: generate_refusal(answerability). Persist turn in database with all metadata.

### TASK-016
CancellationManager: mark cancellation at turn_id level, store in in-memory map or cache. integrate into orchestration to check is_cancelled() at key points (after retrieval, after generation). If cancelled during generation, omit final citations from response. Test: ensure cancel doesn't corrupt turn state.

### TASK-017
POST /api/chat/sessions/{session_id}/ask with {question, retrieval_mode, collection_id (optional)}. Call ChatOrchestrationService synchronously, return ChatTurnResult as JSON. Response: { result_type, answer: {text, ...}, refusal: {text, reason_category, ...}, citations: [{chunk_id, document_title, ...}], retrieval_mode_used, answerability_score, terminal_status, turn_id }.

### TASK-018
Streaming endpoint: POST /api/chat/sessions/{session_id}/ask-stream with same parameters. Use line-delimited JSON or Server-Sent Events. Stream events: { event: "retrieving", ... }, { event: "context_packed", chunk_count: int }, { event: "generating", ... }, { event: "answer_chunk", text: "substring of answer" }, { event: "completed", citations: [...], turn_id, ... }. Ensure citations appear only in completed event.

### TASK-019
POST /api/chat/sessions/{session_id}/turns/{turn_id}/cancel. Call CancellationManager.cancel(turn_id), return { status: "cancelled", partial_state: {...} }. Verify in-progress generation stops and no final response is sent.

### TASK-020
GET /api/chat/sessions/{session_id}/citations/{citation_id}. Look up citation by chunk_id in stored chunks, return full metadata including document record link. Response: { chunk_id, document_id, document_title, page_or_section, source_url, full_snippet (full chunk content), retrieval_score, retrieval_mode, rerank_score (if applicable) }.

### TASK-021
Integration tests: mock generation if needed or use deterministic test data. Test scenarios:
1. Supported question (good evidence) → verify answer appears
2. Unsupported question (no evidence) → verify refusal with no_relevant_evidence
3. Weak question (low confidence) → verify refusal with low_confidence
4. Conflicting evidence → verify refusal with conflicting_evidence
5. Streaming completion → verify events appear in order, citations in completed only
6. Cancellation during retrieval → verify cancelled status, no final response

### TASK-022
Chat HTML: semantic structure with <form> for question input, <select> for collection and retrieval-mode, <button> for send and cancel, <div role="status"> for progress, <div id="chat-history"> for messages, <div id="answer"> for answer panel, <div id="citations"> for citations, <dialog> or <div role="dialog"> for citation-detail modal. Consider accessibility (ARIA labels, keyboard navigation).

### TASK-023
Session management: POST /api/chat/sessions on first visit or "New Chat" button, store session_id in URL (#chat/{session_id}) or sessionStorage. GET /api/chat/sessions to populate session list sidebar. Switch between sessions by clicking list item (update URL, fetch history).

### TASK-024
Form submission: collect question, POST to /api/chat/sessions/{session_id}/ask (non-streamed), parse response, render answer in #answer div, render citations in #citations div, add turn to #chat-history. Show error overlay if response is an error.

### TASK-025
Streaming: open event source or fetch stream to /api/chat/sessions/{session_id}/ask-stream, parse JSON lines or SSE events. Show "Retrieving..." when retrieving event, "Generating answer..." when generating, accumulate answer text chunks in real-time, show citations only when completed event is received.

### TASK-026
Cancel button enabled only when in-progress (while answer is generating). Click → POST /api/chat/sessions/{session_id}/turns/{turn_id}/cancel. Show "Cancelling..." status, disable cancel button, close event stream if streaming.

### TASK-027
Citation rendering: parse answer_text and citations array. Insert superscript or linked reference markers [1], [2] in answer at positions indicated by citation indices. Build reference list HTML: <ol><li>Citation 1 metadata</li>...</ol>. Make markers clickable to trigger citation-detail modal.

### TASK-028
Citation modal: open on marker click, fetch GET /api/chat/sessions/{session_id}/citations/{citation_id}, display document_title (link to Document Library), chunk_id, page_or_section, source_url, full_snippet (in scrollable <div>), retrieval_score, retrieval_mode. Include "View in Document Library" button linking to `/document-library.html?document_id={document_id}`.

### TASK-029
Refusal rendering: when result_type === "refusal", render refusal_text in larger, prominent style. Show reason_category as subtitle or info box. Display supporting_metrics if present (e.g., "Found 2 chunks, but minimum similarity was 0.3 (threshold: 0.5)").

### TASK-030
History rendering: for each ChatMessage in session.turns, render user message on left (gray background), assistant message on right (white/light background). Refusals: show with different background or icon. Timestamps: show creation time. Preserve scroll position when adding new messages.

### TASK-031
Collection dropdown: populate from GET /api/collections. Retrieval mode: <select> with options semantic, keyword, hybrid (default semantic). Streaming toggle: <input type="checkbox"> to enable streamed responses. Debug toggle: <input type="checkbox"> to show advanced fields (internal_reasoning, etc.). Persist selections in localStorage or URL params.

### TASK-032
Manual test checklist:
- [ ] Create new session (verify session_id generated, collection selected)
- [ ] Ask supported question (verify answer appears with citations)
- [ ] Ask unsupported question (verify refusal with reason_category)
- [ ] Click citation marker (verify detail modal opens with metadata)
- [ ] Test semantic retrieval (ask question, verify sources are semantically relevant)
- [ ] Test keyword retrieval (ask question, verify sources match keywords)
- [ ] Test hybrid retrieval (verify results combine both methods)
- [ ] Change collection scope (ask same question in different collections, verify answers differ)
- [ ] Test streaming (enable streaming toggle, observe real-time status updates)
- [ ] Cancel in-progress answer (verify cancellation stops generation)
- [ ] Switch to past session (verify history loads, can continue conversation)
- [ ] Verify all citation metadata is accurate (title, chunk_id, page, URL)

### TASK-033
Retrieval unit tests should use pytest with fixtures for sample chunks and vectors (or mock ChromaDB). Test each retrieval mode independently with known queries and expected results. Test edge cases: empty query, no results, single result, many results.

### TASK-034
Answerability unit tests: create synthetic retrieved_chunks with varying similarity scores (0.1, 0.5, 0.8, 0.95). Test each reason_category boundary:
- no_relevant_evidence: chunks with similarity < 0.1
- low_confidence: chunks with 0.1 < similarity < 0.5
- insufficient_support: chunk_count < min_chunk_count
- conflicting_evidence: chunks with contradictory content
Test that each scenario triggers correct reason_category.

### TASK-035
Citation unit tests: create sample chunks with full metadata, pass through CitationFormattingService, verify each Citation object has all required fields. Test missing metadata scenarios: chunk without source_url, chunk without page. Verify no synthesized content.

### TASK-036
Citation consistency tests: ask same question via both endpoints, compare final citations for equivalence (same chunks, same ordering, same metadata). Verify streamed path doesn't lose citations during partial transmission.

### TASK-037
Cancellation tests: orchestrate a turn, call cancel during retrieval phase, verify turn_id is marked cancelled. Attempt to cancel after completion, verify no effect. Verify turn history shows cancelled status.

### TASK-038
Refusal correctness tests: create test data with no relevant chunks, test no_relevant_evidence refusal. Create chunks with low similarity, test low_confidence. Create conflicting chunks, test conflicting_evidence. Verify refusal_text is appropriate and reason_category is accurate.

### TASK-039
Context packing unit tests: create chunks with varying token counts, call pack with budget that fits some but not all. Verify selected chunks are highest-ranked and total_tokens <= budget. Test budget larger and smaller than all chunks.

### TASK-040
Logging should record: turn_id, session_id, question_text, retrieval_mode_used, retrieved_chunk_count, answerability_score, refusal_category, answer_length (tokens), citation_count. Optional: GET /api/chat/logs?session_id={sid}&limit=50 endpoint or debug panel in frontend that displays logs.

### TASK-041
Full chat workflow: Create session with collection, ask supported question, verify answer and citations render, ask unsupported question, verify refusal text and reason_category, click citation to open detail modal, switch retrieval modes and ask same question, compare results, verify history is preserved when switching sessions back and forth.

### TASK-042
Citation detail verification: For each citation in an answer, click the marker to open modal. Verify document_title matches stored document, chunk_id is valid, page_or_section is accurate, source_url is correct if present, retrieval_score matches stored value, retrieval_mode matches what was selected. Click "View in Document Library" and verify document opens correctly.

### TASK-043
Traceability mapping:
- REQ-001 → AC-001 → TASK-001, TASK-003, TASK-008, TASK-023, TASK-024, TASK-030, TASK-041
- REQ-002 → AC-002 → TASK-004, TASK-005, TASK-006, TASK-007, TASK-031, TASK-033
- REQ-003 → AC-003 → TASK-012, TASK-013, TASK-027, TASK-028, TASK-035, TASK-041, TASK-042
- REQ-004 → AC-004 → TASK-010, TASK-014, TASK-029, TASK-038, TASK-041
- REQ-005 → AC-005 → TASK-020, TASK-028, TASK-042
- REQ-006 → AC-006 → TASK-001, TASK-011, TASK-015, TASK-016, TASK-018, TASK-022, TASK-025, TASK-026, TASK-039, TASK-040, TASK-041

Verify all phases are complete, all CC are satisfied, no REQ/AC is orphaned.

---

## Completion Notes

- What was delivered: Task list decomposition from Phase 1 through Phase 4 covering all 43 tasks, with explicit dependencies, parallel-safe markers, file paths, and validation notes for each task.
- What was deferred: None at this stage; all work required by spec.md and plan.md is included. However, advanced retrieval features (query expansion, HyDE, reranking) are intentionally out of scope and will be addressed in later features.
- What needs follow-up: Confirmation of generation provider choice (OpenAI API, local model, etc.) and API key/model name configuration before TASK-013 implementation; alignment on streaming transport (Server-Sent Events vs. line-delimited JSON) before TASK-018 implementation; decision on whether both inline and reference-list citations are required or if one presentation style is sufficient for the first version.

---

## Resume Notes

- Current phase: Ready for implementation—Phase 1 tasks are entry points; feature 1 must be complete first (PREREQ-001).
- Next recommended task: TASK-001 (chat schema design, depends on feature 1 schema being in place).
- Active blocker: Feature 1 (Knowledge Ingestion and Collections) must be complete before chat work begins; chat depends on stable document, chunk, and collection records.
- Last validation evidence added: None yet; task list is complete and ready for Phase 1 execution after feature 1 is delivered.

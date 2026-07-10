# Feature Specification

## Metadata

- Feature name: NotebookLM-Parity Document QA
- Feature slug: notebooklm-parity-doc-qa
- Delivery profile: Complex
- Owner: Unassigned
- Status: Draft
- Related knowledge artifact(s): README.md, design.md, backend/chat/service.py, backend/routers/generate.py, backend/routers/chat.py, backend/chat/knowledge_products.py

---

## Problem Statement

The repository ("KnowledgeBaseLab") is structurally a Google NotebookLM clone — it has Collections (= Notebooks), a 3-panel workspace (Sources / Chat / Studio), knowledge products, grounded generation with citations, streaming, provenance graphs, conflict detection, an evaluation dashboard, and a deep retrieval pipeline (hybrid search, query intelligence, HyDE, multi-hop, RRF, safety scanning). The RAG engine depth exceeds NotebookLM's visible surface.

However, several core **document-QA** features that make NotebookLM the reference product are missing or underdeveloped:

1. **No suggested follow-up questions** — NotebookLM surfaces 3–5 auto-generated follow-ups after each answer, plus starter prompts on an empty session.
2. **No notebook-level or pinned notes** — only chunk-attached notes exist; NotebookLM supports free-form notes that can be pinned to the notebook.
3. **No per-source active/inactive toggle** — chat retrieves against the whole collection (or one routed collection) with no user-controlled source filtering.
4. **Citation UX lacks quote-anchored navigation** — NotebookLM jumps inline to the exact quoted passage highlighted within the source viewer with surrounding context.
5. **Reranker is a stub** — README admits a dummy reranker; real cross-encoder reranking is unimplemented despite being the highest-ROI retrieval quality technique.
6. **Grounding score is binary** — `ChatService` sets groundedness to `1.0` when evidence is "sufficient"; the real graded score is only computed post-hoc.
7. **Follow-up resolution is implicit** — ambiguous follow-ups ("tell me more about that") are not explicitly resolved against prior turn's citations.
8. **Per-source summarization fallback** — when `doc_understanding` metadata is absent, `_get_document_summary` falls back to the first 3 chunks instead of generating a structured summary at ingestion time.

This spec defines the work to close these gaps for the **document-QA RAG core** only.

---

## Desired Outcomes

- **Outcome 1:** Users can chat with their document collection and receive contextually relevant, suggested follow-up questions after every answer — matching NotebookLM's conversational discoverability.
- **Outcome 2:** Users can view, create, and pin free-form notes at the notebook level alongside their sources — matching NotebookLM's notebook-notes experience.
- **Outcome 3:** Users can selectively activate or deactivate sources within a collection so chat queries are scoped to relevant documents only.
- **Outcome 4:** Citation clicks navigate to the exact quoted passage in the source viewer with visual highlight — matching NotebookLM's source-anchored citation experience.
- **Outcome 5:** Retrieval quality improves measurably through a real reranker, graded groundedness scoring, explicit follow-up resolution, and guaranteed structured per-source summaries.

---

## Minimum Release Slice

- **Ships in first useful release (Phase 1):**
  - Suggested questions (starter prompts + post-turn follow-ups)
  - Notebook-level notes + pinned notes CRUD
  - Active-source toggle per session
  - Quote-anchored citation navigation

- **Can wait (Phase 2):**
  - Real cross-encoder reranker
  - Graded groundedness score at evidence-evaluation time
  - Explicit anaphora/follow-up resolution in context assembly
  - Structured summary generation at ingestion time

- **Out of this spec (Phase 3 — documented as roadmap, not required):**
  - Async ingestion (Celery), OpenTelemetry tracing, per-query cost attribution, snapshot/restore. These are production-hardening items already listed in the README.

---

## Success Criteria

- **SC-001:** After every completed chat turn, the UI displays 3–5 suggested follow-up questions that are grounded in the retrieved context of that turn. *(→ AC-001, AC-002)*
- **SC-002:** Users can create free-form notes attached to a notebook (not just chunks), pin/unpin them, and these notes are included in the retrieval context package. *(→ AC-003, AC-004)*
- **SC-003:** Users can toggle sources in a collection to be active or inactive for chat; inactive sources are excluded from retrieval. *(→ AC-005, AC-006)*
- **SC-004:** Clicking a citation navigates to the source viewer with the exact quoted passage highlighted and visible in surrounding context. *(→ AC-007, AC-008)*
- **SC-005:** A real cross-encoder reranker re-scores retrieval results; ablation evaluation shows measurable context-precision improvement over the dummy reranker baseline. *(→ AC-009, AC-010)*
- **SC-006:** Groundedness score is computed as a graded value (0.0–1.0) at evidence-evaluation time, not a binary `1.0` placeholder, and is surfaced to the UI. *(→ AC-011)*
- **SC-007:** Ambiguous follow-up queries reference-resolve against prior turn's citation centroids before retrieval, improving retrieval relevance on multi-turn conversations. *(→ AC-012)*
- **SC-008:** Every source in a collection has a structured summary available at query time (no first-3-chunks fallback at runtime). *(→ AC-013)*

---

## In Scope

- **Suggested questions:** Post-turn follow-up generation (LLM call) + empty-session starter prompts + UI chips in ChatPanel.
- **Notebook notes:** Notebook-level note CRUD (extends existing `notes.py` chunk-note pattern), pinned-notes concept, inclusion of pinned notes in retrieval context.
- **Active-source toggle:** Session-level `active_source_ids` persistence, retrieval-layer filtering by active sources, UI toggle controls in SourcesPanel.
- **Quote-anchored citations:** `CitationResponse` enrichment with `anchor_text` and scroll/offset metadata, `SourceBrowser` highlight-and-scroll implementation.
- **Real reranker:** Cross-encoder reranking (`BAAI/bge-reranker-base` or Cohere Rerank) behind the existing `providers/` abstraction, replacing the dummy reranker.
- **Graded groundedness:** Replace the binary `1.0` placeholder at `service.py:164` with a real graded score computed at evidence-evaluation time.
- **Follow-up resolution:** Explicit anaphora/coreference detection in `context.py`; rewrite ambiguous follow-ups using prior turn's citation centroids before retrieval.
- **Structured summary at ingestion:** Generate and persist a structured per-source summary during ingestion (stored in `doc_understanding` metadata), eliminating runtime first-3-chunks fallback.

---

## Out Of Scope

- Audio Overview / podcast generation / TTS (explicitly excluded per user decision).
- Mind map visualization.
- New source formats: URL, YouTube transcript, DOCX, PPTX, XLSX, HTML, OCR. Keep PDF/TXT only.
- Multi-user collaboration / sharing / real-time co-editing.
- Voice input / speech-to-text.
- Mobile-native app (responsive web is sufficient).
- Async ingestion via Celery (Phase 3 roadmap item).
- OpenTelemetry / Prometheus observability (Phase 3).
- Per-query cost attribution / budget caps (Phase 3).
- Blue/green index swaps / re-embedding campaigns (Phase 3).

---

## Non-Goals

- **Non-goal 1:** Not building a general-purpose chatbot. The system is grounded in user-uploaded sources only; no external-knowledge mode.
- **Non-goal 2:** Not replacing the existing RAG pipeline architecture. All changes are additive — new modules, extended existing modules, no rewrites of working systems.
- **Non-goal 3:** Not matching NotebookLM's Google Docs / YouTube ingestion. Only PDF/TXT sources are in scope.
- **Non-goal 4:** Not adding a second LLM provider integration beyond the existing `providers/` abstraction. Reranker is a new provider type but follows the same pattern.

---

## Users And Stakeholders

- **Primary users:** Individual developers, researchers, and students who upload documents and ask questions grounded in those documents.
- **Secondary stakeholders:** Portfolio reviewers evaluating RAG engineering depth; potential contributors extending the platform.

---

## User Stories And Key Scenarios

- **US-001:** As a user, after I ask a question and receive an answer, I want to see suggested follow-up questions so I can explore the topic further without typing a new query.
- **US-002:** As a user, I want to create free-form notes attached to my notebook (not limited to chunk-level) so I can annotate my understanding of the collected sources.
- **US-003:** As a user, I want to pin important notes so they are always included in the chat context, even if they don't match the query semantically.
- **US-004:** As a user, I want to toggle which sources are active for a chat session so I can focus queries on a subset of my collection.
- **US-005:** As a user, when I click a citation in the answer, I want to jump to the exact quoted passage in the source viewer with it highlighted so I can verify the claim in context.
- **US-006:** As a user, I want the system to understand my follow-up questions like "tell me more about that" by referencing what "that" refers to from the previous turn.
- **US-007:** As a developer/reviewer, I want the evaluation dashboard to show the measurable improvement from reranking so I can verify the investment paid off.

### Detailed Scenarios

- **Scenario 1 (Happy Path — Suggested Questions):**
  - Given: A user has an active chat session with a collection containing multiple sources.
  - When: The user asks "What is the main argument of this paper?" and the system generates a grounded answer.
  - Then: The UI displays 3–5 suggested follow-up questions below the answer, each derived from the retrieved context.

- **Scenario 2 (Happy Path — Active Source Toggle):**
  - Given: A collection has 5 sources. The user has toggled 2 sources to "inactive."
  - When: The user asks a query.
  - Then: Only chunks from the 3 active sources are considered for retrieval; inactive source chunks are filtered out.

- **Scenario 3 (Happy Path — Quote-Anchored Citation):**
  - Given: A generated answer contains a citation badge linked to chunk #42 in "paper.pdf."
  - When: The user clicks the citation badge.
  - Then: The SourcesPanel / SourceBrowser scrolls to the relevant passage and highlights the exact `quote_text` from the citation, surrounded by 1–2 paragraphs of context.

- **Scenario 4 (Edge Case — No Sufficient Evidence):**
  - Given: A user asks a question for which the retrieved chunks do not provide sufficient evidence.
  - When: The system evaluates evidence and determines insufficiency.
  - Then: No suggested questions are generated (or a discrete "not enough context" message is shown); the refusal reason is displayed; the user is not blocked from asking a new question.

- **Scenario 5 (Edge Case — Follow-up Resolution):**
  - Given: The previous turn's answer cited chunks about "transformer attention mechanisms."
  - When: The user asks "can you explain that in more detail?"
  - Then: The system references the prior turn's citations, rewrites the query to "explain transformer attention mechanisms in more detail," and retrieves relevant chunks.

- **Scenario 6 (Error State — Reranker Failure):**
  - Given: The cross-encoder reranker service is unavailable or times out.
  - When: Retrieval reaches the reranking stage.
  - Then: The system falls back to pre-reranking retrieval order (graceful degradation), logs the failure, and the chat answer still generates — with a logged warning.

---

## Current Context

- **Current behavior summary:** The system has a complete RAG pipeline (safety → collection routing → advanced retrieval → chunk safety → grounding evaluation → context assembly → generation → finalize with provenance, groundedness, citations, conflict detection). Knowledge products (study guide, FAQ, glossary, flashcards, briefing, timeline) are generated from collection-level summaries. The 3-panel workspace (Sources / Chat / Studio) is functional with streaming, X-Ray debug panel, and evaluation dashboard.
- **Impacted boundaries:**
  - `backend/chat/service.py` — orchestration loop (suggested questions hook, groundedness score fix).
  - `backend/chat/context.py` — context assembly (active-source filtering, pinned-note injection, follow-up rewriting).
  - `backend/chat/knowledge_products.py` — `_get_document_summary` fallback path.
  - `backend/routers/notes.py` — extend for notebook-level notes.
  - `backend/routers/chat.py` — suggested questions endpoint.
  - `backend/routers/collections.py` — active-source configuration.
  - `frontend/src/components/ChatPanel.jsx` — follow-up question chips.
  - `frontend/src/components/SourcesPanel.jsx` — source toggle + note panel.
  - `frontend/src/components/SourceBrowser.jsx` — quote anchoring.
  - `frontend/src/components/CitationBadge.jsx` / `CitationModal.jsx` — citation navigation enrichment.
- **Preserved behavior:** All existing RAG pipeline behavior, knowledge products, streaming, X-Ray panel, evaluation dashboard, and safety scanning remain unchanged. New modules are additive; existing modules are extended, not rewritten.
- **Brownfield risk rating: Medium**
  - `service.py` is load-bearing (orchestrates the entire chat turn) — modifications must be surgical.
  - `context.py` is shared by both streaming and non-streaming paths.
  - Existing `notes.py` pattern provides a safe template for extension.
  - Reranker touches the retrieval path but can be gated behind a feature flag.

---

## Gray-Area Decisions

- **Locked decisions:**
  - TTS / Audio Overview is explicitly excluded (user decision).
  - Mind map is explicitly excluded (user decision).
  - New source formats (URL, YouTube, DOCX/PPTX) are excluded; only PDF/TXT (user decision).
  - Scope is RAG/document-QA core only (user decision).
  - This deliverable is a spec document only; user will review and implement later.
- **Remaining decisions that still block approval:**
  - Reranker choice: local model (`BAAI/bge-reranker-base`) vs API service (Cohere Rerank) vs both behind provider abstraction. *[user decision at implementation time]*
  - Suggested-questions model: same LLM as generation (GPT-4o) or a lighter/faster model for lower latency? *[user decision at implementation time]*
  - Pinned-note context budget: how many tokens do pinned notes consume before trimming? *[user decision at implementation time]*

---

## Dependencies And External Touchpoints

- **DEP-001:** Existing `providers/` abstraction for LLM and embedding providers — must extend (not replace) for reranker provider.
- **DEP-002:** Weaviate vector store — no schema changes required for active-source filtering (filtering is a query-time concern via `collection_ids` and `where` clauses).
- **DEP-003:** SQLite metadata DB — new tables/columns needed: `notebook_notes`, `active_source_config` (or extension of `chat_sessions.metadata_json`).
- **DEP-004:** Existing `CitationResponse` schema — must be extended with `anchor_text` and optional scroll/offset fields.
- **DEP-005:** Existing `doc_understanding` metadata field on documents — must be populated at ingestion time for all sources.

---

## Functional Requirements

### REQ-001: Suggested Follow-Up Questions

- **Requirement:** After every completed chat turn with sufficient evidence, the system generates 3–5 suggested follow-up questions derived from the turn's retrieved context and answer.
- **Why it matters:** Matches NotebookLM's conversational discoverability; reduces user friction in exploring a topic.
- **Impacted users or scenarios:** All chat users, immediately after receiving an answer.
- **Related success criteria:** SC-001
- **Priority:** Must Have
- **Acceptance notes:** Suggested questions must be grounded in the turn's retrieved chunks (not generic). If evidence is insufficient, no suggestions are generated (graceful omission).
- **Validation surface:** `POST /chat/turns/{turn_id}/suggestions` returns 3–5 question strings; UI renders them as clickable chips.

### REQ-002: Starter Prompts on Empty Session

- **Requirement:** When a chat session has no prior turns, the UI displays 3–5 starter prompts generated from the collection's source summaries.
- **Why it matters:** NotebookLM shows starter prompts to guide first interaction with a notebook.
- **Impacted users or scenarios:** Users opening a new chat session.
- **Related success criteria:** SC-001
- **Priority:** Should Have
- **Acceptance notes:** Starter prompts are generated from collection-level source summaries (using existing `doc_understanding` summary or fallback). Cached per collection until sources change.
- **Validation surface:** `GET /chat/sessions/{session_id}/starter-prompts` returns 3–5 prompts; UI renders in empty-state.

### REQ-003: Notebook-Level Notes CRUD

- **Requirement:** Users can create, read, update, and delete free-form notes attached to a notebook (collection), independent of any specific chunk.
- **Why it matters:** NotebookLM supports notebook-level notes, not just chunk-attached annotations.
- **Impacted users or scenarios:** Users annotating their understanding of a collection.
- **Related success criteria:** SC-002
- **Priority:** Must Have
- **Acceptance notes:** Follows the existing `notes.py` chunk-note pattern. New table `notebook_notes` with columns: `id`, `collection_id`, `note_text`, `is_pinned`, `created_at`, `updated_at`.
- **Validation surface:** `GET/POST/PUT/DELETE /collections/{collection_id}/notes`; UI NotePanel in Sources panel.

### REQ-004: Pinned Notes in Retrieval Context

- **Requirement:** Notes marked as pinned are injected into the retrieval context package alongside retrieved chunks, with a defined token budget.
- **Why it matters:** Pinned notes represent user-curated context that should always influence generation.
- **Impacted users or scenarios:** Users who pin notes for emphasis.
- **Related success criteria:** SC-002
- **Priority:** Should Have
- **Acceptance notes:** Token budget for pinned notes is configurable (default 512 tokens). Pinned notes are prepended to the context package with a "User Note:" prefix. Trimming follows existing context-window strategy.
- **Validation surface:** Context package (`context_used_json`) in a completed turn includes pinned notes; generation references them when relevant.

### REQ-005: Active-Source Toggle Per Session

- **Requirement:** Users can mark sources in a collection as active or inactive for a specific chat session. Only chunks from active sources are considered during retrieval.
- **Why it matters:** NotebookLM lets users scope queries to a subset of sources.
- **Impacted users or scenarios:** Users with multi-source collections who want to focus on specific documents.
- **Related success criteria:** SC-003
- **Priority:** Must Have
- **Acceptance notes:** `active_source_ids` stored on `chat_sessions` (via `metadata_json` or a dedicated column). Default = all sources active (backward compatible). Retrieval service filters by `document_id IN active_source_ids` before/after vector search.
- **Validation surface:** `PUT /chat/sessions/{session_id}/active-sources`; verification that retrieval results exclude inactive sources.

### REQ-006: Quote-Anchored Citation Navigation

- **Requirement:** Clicking a citation badge navigates to the source viewer, scrolls to the relevant passage, and visually highlights the exact quoted text within surrounding context.
- **Why it matters:** NotebookLM's citation UX jumps to the exact passage; this is the core trust mechanism for grounded answers.
- **Impacted users or scenarios:** Users verifying claims in the generated answer.
- **Related success criteria:** SC-004
- **Priority:** Must Have
- **Acceptance notes:** `CitationResponse` schema extended with `anchor_text` (the quoted passage) and optional `offset` / `chunk_order` for scroll positioning. `SourceBrowser` component performs text search and highlight upon navigation.
- **Validation surface:** Click citation → SourcesPanel switches to that source → SourceBrowser highlights `anchor_text` scrolled into view.

### REQ-007: Real Cross-Encoder Reranker

- **Requirement:** A real cross-encoder reranker (e.g., `BAAI/bge-reranker-base` local or Cohere Rerank API) re-scores initial retrieval results, replacing the dummy reranker.
- **Why it matters:** Reranking is the highest-ROI retrieval quality technique (20–30% precision improvement per README). The current dummy reranker only sorts by similarity score.
- **Impacted users or scenarios:** All chat queries — reranking impacts answer quality globally.
- **Related success criteria:** SC-005
- **Priority:** Must Have
- **Acceptance notes:** Reranker is behind the `providers/` abstraction (new `BaseRerankerProvider` + factory). Feature flag allows fallback to dummy reranker. Graceful degradation on reranker failure (log warning, use pre-reranking order).
- **Validation surface:** Ablation evaluation comparing dummy vs real reranker on golden test dataset; context precision delta observed.

### REQ-008: Graded Groundedness Score

- **Requirement:** The groundedness score is computed as a graded value (0.0–1.0) at evidence-evaluation time, replacing the binary `1.0` placeholder at `service.py:164`.
- **Why it matters:** A binary score provides no signal for partial grounding; NotebookLM displays faithfulness indicators.
- **Impacted users or scenarios:** All completed turns; UI displays the score.
- **Related success criteria:** SC-006
- **Priority:** Should Have
- **Acceptance notes:** Use existing `GroundingService` capabilities or extend it. Score reflects the proportion of generated claims supported by retrieved context. Surfaced as a chip/badge in the ChatPanel answer.
- **Validation surface:** `groundedness_score` field on `ChatTurnResponse` is a float (not hardcoded `1.0`); UI renders it.

### REQ-009: Explicit Follow-Up Resolution

- **Requirement:** When a follow-up query contains anaphoric references (pronouns, "that", "this", "it"), the system rewrites the query using the prior turn's citation centroids before retrieval.
- **Why it matters:** Multi-turn conversations in NotebookLM correctly resolve "tell me more about that" to the prior topic; implicit resolution risks poor retrieval.
- **Impacted users or scenarios:** Multi-turn chat sessions, follow-up queries.
- **Related success criteria:** SC-007
- **Priority:** Should Have
- **Acceptance notes:** Detection via simple heuristics (pronoun list + query length threshold) or LLM-based classification. Rewrite merges the referent topic from the previous turn's citations with the follow-up query. Visible in X-Ray panel as "Query Rewrite" stage.
- **Validation surface:** `retrieval_trace` in `ChatTurnResponse` shows rewritten query; retrieval uses rewritten query for embedding/search.

### REQ-010: Structured Summary at Ingestion Time

- **Requirement:** Every source ingested receives a structured summary (summary text + topic list) generated at ingestion time and stored in `doc_understanding` metadata.
- **Why it matters:** Eliminates the runtime first-3-chunks fallback in `_get_document_summary`; ensures consistent, structured summaries for knowledge product generation and starter prompts.
- **Impacted users or scenarios:** All sources; impacts knowledge products, starter prompts, and per-source display.
- **Related success criteria:** SC-008
- **Priority:** Must Have
- **Acceptance notes:** Summary generation happens during ingestion (synchronous or background). Stored in the existing `documents.metadata` JSON field under `doc_understanding`. Format: `{"summary": str, "topics": [str]}`. Re-summarization triggered on document update.
- **Validation surface:** New ingestion produces `doc_understanding` populated; `_get_document_summary` no longer hits the first-3-chunks fallback for new sources.

---

## Non-Functional Requirements

- **NFR-001 Performance:** Suggested questions generation adds ≤ 2 seconds latency to the post-turn flow. *(Linked ACs: AC-002)*
- **NFR-002 Performance:** Reranker adds ≤ 500ms latency for a 20-result reranking batch. *(Linked ACs: AC-010)*
- **NFR-003 Reliability:** Reranker failure degrades gracefully — retrieval proceeds with pre-reranking order, and the failure is logged. *(Linked ACs: AC-010)*
- **NFR-004 Security:** Notebook-level notes are scoped to their collection; no cross-collection leakage. Pinned notes are validated for length (max 5000 chars). *(Linked ACs: AC-004)*
- **NFR-005 Accessibility:** Suggested question chips are keyboard-navigable (Tab + Enter). Citation links are keyboard-activatable. Source highlight is visible without color-only cues (underline/bold). *(Linked ACs: AC-001, AC-007, AC-008)*
- **NFR-006 Observability:** Reranker usage, suggested-questions generation, and follow-up rewrites are logged with structured logging. Reranker fallback events are counted. *(Linked ACs: AC-010, AC-012)*

---

## Constraints

- **Technical:**
  - Must use existing `providers/` abstraction for reranker (no direct model coupling in `service.py`).
  - Must not change Weaviate schema for active-source filtering (query-time `where` filtering only).
  - Must follow existing `notes.py` CRUD pattern for notebook notes.
  - All new endpoints follow existing FastAPI router conventions.
- **Business:**
  - PDF/TXT sources only — no new ingestion formats.
  - Single-user — no multi-tenancy or collaboration features.
- **Delivery:**
  - Additive changes only — no rewrites of working systems.
  - Each phase is independently shippable.
  - Feature flags gate new capabilities (reranker, suggested questions) for safe rollout.

---

## Assumptions

- **ASM-001:** The existing `doc_understanding` metadata field in the `documents.metadata` JSON is the correct storage location for structured summaries and is already read by `knowledge_products.py`.
- **ASM-002:** The `providers/` abstraction pattern (used for LLM and embedding) can be cleanly extended to support a reranker provider type.
- **ASM-003:** Weaviate's `where` filter or `metadata.collection_ids` supports per-document filtering at query time without schema changes.
- **ASM-004:** The existing `ChatRepository.create_turn` and `list_turns_by_session` can support the `active_source_ids` field via `metadata_json` without schema migration.
- **ASM-005:** The `CitationResponse` Pydantic schema can be extended with optional fields without breaking existing API consumers.

---

## Risks

- **RISK-001:** Modifying `service.py` (load-bearing orchestration loop) could introduce regressions in the chat flow. *Mitigation:* All additions are surgical hooks (post-turn suggestions, score computation swap); existing flow is preserved. Feature flags gate new paths.
- **RISK-002:** Local cross-encoder model loading adds memory pressure and startup latency. *Mitigation:* Load model lazily (on first request) or use API-based reranker (Cohere) to avoid local model.
- **RISK-003:** Suggested questions could hallucinate topics not in the retrieved context. *Mitigation:* Prompt constrains generation to the turn's retrieved chunks; validate in AC.
- **RISK-004:** Quote-anchored navigation may fail if `anchor_text` is not an exact substring of the chunk text (truncation, encoding). *Mitigation:* Fallback to chunk-level scroll (no highlight) if exact match fails.
- **RISK-005:** Follow-up rewrite could degrade retrieval if the rewrite is wrong. *Mitigation:* Show rewrite in X-Ray panel for user transparency; feature flag to disable.

---

## Open Questions

- **Q-001:** Reranker provider: local model (`BAAI/bge-reranker-base`) or API service (Cohere Rerank) or both behind abstraction?
  - Type: Non-blocking (user decides at implementation time)
  - Owner: User
  - Next step: Decide during Phase 2 planning.

- **Q-002:** Suggested-questions model: reuse the generation LLM (GPT-4o) or use a lighter model for faster, cheaper question generation?
  - Type: Non-blocking
  - Owner: User
  - Next step: Decide during Phase 1 planning.

- **Q-003:** Pinned-note token budget — how many tokens before trimming? (Default proposed: 512)
  - Type: Non-blocking
  - Owner: User
  - Next step: Confirm default during Phase 1 planning.

- **Q-004:** Should `active_source_ids` be stored as a dedicated column on `chat_sessions` or inside the existing `metadata_json`?
  - Type: Non-blocking
  - Owner: User
  - Next step: Decide during Phase 1 planning; metadata_json is the lower-migration option.

---

## Acceptance Criteria

- [ ] **AC-001** Linked REQ: REQ-001
  - Linked scenario or success criteria: Scenario 1, SC-001
  - Validation method: Submit a chat turn → `POST /chat/turns/{turn_id}/suggestions` returns 3–5 question strings.
  - Proof target: API response contains 3–5 strings; all strings are derivable from the turn's retrieved context.

- [ ] **AC-002** Linked REQ: REQ-001, NFR-001
  - Linked scenario or success criteria: SC-001
  - Validation method: Measure latency from turn completion to suggested-questions response.
  - Proof target: Median latency ≤ 2 seconds.

- [ ] **AC-003** Linked REQ: REQ-003
  - Linked scenario or success criteria: SC-002
  - Validation method: `POST /collections/{id}/notes` with note text → `GET /collections/{id}/notes` returns the note → `DELETE` removes it.
  - Proof target: CRUD round-trip succeeds; note is scoped to the collection.

- [ ] **AC-004** Linked REQ: REQ-003, REQ-004, NFR-004
  - Linked scenario or success criteria: SC-002
  - Validation method: Pin a note → submit a query → inspect `context_used_json` for the pinned note.
  - Proof target: Pinned note appears in context package with "User Note:" prefix; pinned note text ≤ 5000 chars validated on create.

- [ ] **AC-005** Linked REQ: REQ-005
  - Linked scenario or success criteria: Scenario 2, SC-003
  - Validation method: Set `active_source_ids` on a session to exclude one source → submit query → inspect retrieved chunks.
  - Proof target: No retrieved chunks have `document_id` matching the inactive source.

- [ ] **AC-006** Linked REQ: REQ-005
  - Linked scenario or success criteria: SC-003
  - Validation method: Toggle all sources inactive → submit query.
  - Proof target: System returns an appropriate "no active sources" message (not a crash).

- [ ] **AC-007** Linked REQ: REQ-006, NFR-005
  - Linked scenario or success criteria: Scenario 3, SC-004
  - Validation method: Click a citation badge in a generated answer → observe SourcesPanel.
  - Proof target: SourceBrowser opens the correct source, scrolls to the passage containing `anchor_text`, and visually highlights it (with non-color cue).

- [ ] **AC-008** Linked REQ: REQ-006, NFR-005
  - Linked scenario or success criteria: SC-004
  - Validation method: Navigate citation via keyboard (Tab to citation → Enter).
  - Proof target: Source viewer opens and highlight is reachable without mouse.

- [ ] **AC-009** Linked REQ: REQ-007
  - Linked scenario or success criteria: SC-005
  - Validation method: Run ablation evaluation with reranker enabled vs disabled (dummy baseline).
  - Proof target: Context precision with real reranker > dummy reranker context precision on the golden test dataset.

- [ ] **AC-010** Linked REQ: REQ-007, NFR-002, NFR-003, NFR-006
  - Linked scenario or success criteria: Scenario 6, SC-005
  - Validation method: Force reranker failure (e.g., invalid model path or API key) → submit query.
  - Proof target: Chat answer still generates; logs contain reranker fallback warning; reranking stage shows fallback in X-Ray.

- [ ] **AC-011** Linked REQ: REQ-008
  - Linked scenario or success criteria: SC-006
  - Validation method: Submit a query → inspect `groundedness_score` on the turn response.
  - Proof target: Score is a float in [0.0, 1.0], not a hardcoded `1.0`; varies across queries of different evidence levels.

- [ ] **AC-012** Linked REQ: REQ-009
  - Linked scenario or success criteria: Scenario 5, SC-007
  - Validation method: Two-turn conversation — Turn 1 asks about a topic; Turn 2 uses "tell me more about that" → inspect `retrieval_trace`.
  - Proof target: Trace shows a rewritten query incorporating the prior turn's topic; retrieval uses the rewritten query.

- [ ] **AC-013** Linked REQ: REQ-010
  - Linked scenario or success criteria: SC-008
  - Validation method: Upload a new PDF source → inspect `documents.metadata` → query knowledge products.
  - Proof target: `doc_understanding.summary` and `doc_understanding.topics` are populated; `_get_document_summary` does not invoke the first-3-chunks fallback for the new source.

---

## Phased Roadmap

### Phase 1 — NotebookLM Core Parity (credibility features)

| # | Task | Module(s) | Priority |
|---|------|-----------|----------|
| 1.1 | Suggested follow-up questions | `backend/chat/suggested_questions.py` (new), `backend/routers/chat.py` (new endpoint), `frontend/src/components/ChatPanel.jsx` (chips) | Must Have |
| 1.2 | Starter prompts on empty session | `backend/chat/suggested_questions.py` (reuse), `backend/routers/chat.py` (new endpoint), `frontend/src/components/ChatPanel.jsx` (empty-state) | Should Have |
| 1.3 | Notebook-level notes CRUD | `backend/routers/notes.py` (extend), `backend/database.py` (new table `notebook_notes`), `frontend/src/components/NotePanel.jsx` (new), `frontend/src/components/SourcesPanel.jsx` (integrate) | Must Have |
| 1.4 | Pinned notes in retrieval context | `backend/chat/context.py` (inject pinned notes), `frontend/src/components/NotePanel.jsx` (pin toggle) | Should Have |
| 1.5 | Active-source toggle per session | `backend/routers/chat.py` (endpoint to set active sources), `backend/chat/retrieval.py` or `advanced_retrieval.py` (filter by `document_id`), `frontend/src/components/SourcesPanel.jsx` (toggle UI) | Must Have |
| 1.6 | Quote-anchored citation navigation | `backend/schemas/chat.py` (extend `CitationResponse`), `backend/chat/citations.py` (populate `anchor_text`), `frontend/src/components/SourceBrowser.jsx` (highlight+scroll), `frontend/src/components/CitationBadge.jsx` (navigation) | Must Have |

### Phase 2 — RAG Quality (closes the "stronger engine" promise)

| # | Task | Module(s) | Priority |
|---|------|-----------|----------|
| 2.1 | Real cross-encoder reranker | `backend/providers/base.py` (new `BaseRerankerProvider`), `backend/providers/factory.py` (reranker factory), `backend/chat/advanced_retrieval.py` (wire reranker), config + feature flag | Must Have |
| 2.2 | Graded groundedness score | `backend/chat/grounding.py` (extend for graded score), `backend/chat/service.py` (replace `1.0` placeholder at line ~164), `frontend/src/components/ChatPanel.jsx` (score chip) | Should Have |
| 2.3 | Explicit follow-up resolution | `backend/chat/context.py` (anaphora detection + query rewrite), `frontend/src/components/XRayPanel.jsx` (display rewrite) | Should Have |
| 2.4 | Structured summary at ingestion | `backend/ingestion/` (add summary generation step), `backend/chat/knowledge_products.py` (remove fallback path or keep as safety net) | Must Have |

### Phase 3 — Production Polish (roadmap only, not required for parity)

| # | Task | Notes |
|---|------|-------|
| 3.1 | Async ingestion (Celery) | Replace in-process `BackgroundTasks` with durable job queue |
| 3.2 | OpenTelemetry tracing | Per-stage SLOs, structured JSON logs, Prometheus metrics |
| 3.3 | Per-query cost attribution | Token/cost tracking, budget caps, cost-aware routing |
| 3.4 | Index lifecycle ops | Re-embedding campaigns, blue/green index swaps, snapshots/restore |
| 3.5 | Security hardening | SSRF protection, PII redaction, output moderation, secrets management |
| 3.6 | Deployment | Dockerfile, Kubernetes manifests, CI/CD pipeline, blue/green deploys |

---

## Related ADRs

- *[No ADRs found in `core-zero/memories/repo/adr-log.md` — file may not exist yet.]*

---

## Notes

- This spec was authored based on a grounded analysis of the existing codebase (README, design.md, `backend/chat/service.py`, `backend/chat/knowledge_products.py`, `backend/routers/generate.py`, `backend/routers/chat.py`, `backend/routers/notes.py`, `frontend/src/components/StudioPanel.jsx`, `frontend/src/components/WorkspaceLayout.jsx`).
- The comparison with Google NotebookLM was conducted on the RAG/document-QA core only, per explicit user decision. Audio Overview, mind map, URL/YouTube ingestion, and Office format support are excluded.
- This is a spec-only deliverable. The user will review and implement later.
- All changes are additive — no rewrites of working systems. Feature flags gate new capabilities for safe rollout.
# Analysis: Conflict Detection & Knowledge Products

## Metadata

- Investigation name: Conflict Detection and Knowledge Products Scoping
- Feature or issue slug: 2.0-conflict-detection-knowledge-products
- Owner: Antigravity
- Last updated: 2026-06-28

## Scope

- **What is being investigated:**
  - Technical design and endpoint architecture for Notebook LM Studio-like knowledge products (Study Guide, Briefing Doc, FAQ, Timeline, Glossary, Flashcards).
  - Integration of source conflict detection in RAG generation (both prompt-level and post-processing verification).
  - Schema extension requirements for persisting conflict traces or knowledge product generation results.
- **What is explicitly out of scope:**
  - Audio/podcast generation, slides generation, and video overview generation (per user instruction).
  - Real-time live synchronization of Google Docs or YouTube transcripts (to be handled in separate ingestion tasks).

## Current State

- **Observed current behavior:**
  - The chat pipeline (`backend/chat/service.py`) retrieves chunks, checks safety, and generates answers.
  - In Tier 1 Gap 3 implementation, `CONFLICT_INSTRUCTION` was added to the system prompt when chunks span multiple documents. However, there is no verification layer to guarantee the LLM didn't silently choose a side or hallucinate.
  - The system contains no endpoints or services for generating collection-wide study summaries, FAQs, or glossary lists.
- **Relevant boundaries or components:**
  - `backend/routers/collections.py`: Manages collection list/members.
  - `backend/chat/prompts.py`: Defines system prompts for grounded chat, safety, and evaluation.
  - `backend/chat/grounding.py`: Evaluates grounding score.
  - `backend/chat/service.py` / `backend/chat/streaming.py`: Orchestrates generation.
  - `backend/repositories/collection_repository.py`: Fetches collection documents.
- **Unchanged behavior that must be preserved:**
  - The 3-layer safety check pipeline in `backend/chat/safety.py` must run first.
  - Grounded generation rules (no external knowledge, inline citations) must remain active.

## Decision-Ready Summary

- **What matters most:**
  - We can construct high-quality knowledge products efficiently by utilizing the pre-computed `doc_understanding` summaries (created during ingestion in Tier 1) instead of stuffing all raw document texts into a single context window, which saves tokens and prevents context overflow.
  - Conflict detection should be treated as a post-generation evaluation layer similar to `calculate_groundedness`.
- **Strongest supported conclusion:**
  - Adding a dedicated router `backend/routers/generate.py` with endpoints scoped to collection IDs is the cleanest approach.
  - Introducing `ConflictDetectionService` under `backend/chat/conflict.py` allows checking the answer post-generation without cluttering `GroundingService`.
- **Single next proving step:**
  - Route to `/spec-requirements` to define the JSON schemas for the new endpoints and specify the exact markdown templates for the study guides, timelines, and glossary items.

## Findings

### Finding 1: Leveraging Pre-computed Summaries
- **Evidence:** `CollectionRepository.get_collection_members()` returns document metadata, which now contains `doc_understanding` (consisting of `summary`, `topics`, and `sections`) for documents ingested with document understanding enabled.
- **Type:** Fact
- **Impact:** We can feed these summaries into the LLM as the main context for generating Study Guides and Briefing Docs, resulting in fast synthesis times and low token usage.

### Finding 2: Graceful Degradation for Older Documents
- **Evidence:** Existing documents in SQLite may not have `doc_understanding` metadata.
- **Type:** Fact
- **Impact:** If `doc_understanding` is missing, the generation service must gracefully fall back to reading the first few chunks of the document or generating an on-the-fly summary of the document text.

### Finding 3: Post-processing Conflict Evaluation Prompt
- **Evidence:** We currently use `GroundingService.calculate_groundedness()` to evaluate answer factualness against the context.
- **Type:** Fact
- **Impact:** We can write a parallel `CONFLICT_EVALUATION_PROMPT` that asks the LLM to analyze the answer and the retrieved chunks, confirming that if a contradiction exists in the sources, the answer presented both viewpoints.

## Risks And Unknowns

- **Risk: Context Overflow for Large Collections**
  - *Why it matters:* If a collection has dozens of large documents, even concatenating their summaries might exceed the context window or degrade synthesis quality.
  - *Next proving step:* Implement pagination or limit the number of documents summarized in a single knowledge product generation call.

- **Risk: Conflict Detection Latency**
  - *Why it matters:* Running a post-processing conflict check adds another LLM call after generation, increasing latency for non-streaming turns.
  - *Next proving step:* Make the conflict check async or run it in a background task, or toggle it via settings (`conflict_detection_enabled`).

## Recommendation

- **Next skill or artifact:** `/spec-requirements`
- **Why:** The technical layout is well-understood, and the next step is defining the exact API specifications, schema parameters, and validation rules.
- **Exact next action:** Call `/spec-requirements` for `2.0-conflict-detection-knowledge-products`.

# Tasks: 17 Query Intent Classification

## Phase 1: Schema & Prompts (Foundations)

- [x] **TASK-1.1: Update Schema**
  - **File:** `backend/schemas/chat.py`
  - **Action:** Add `classification_confidence: Optional[float] = None` to `RetrievalTrace`.
  - **Proof:** Done. True.

- [x] **TASK-1.2: Update Classification Prompt**
  - **File:** `backend/chat/prompts.py`
  - **Action:** Rewrite `QUERY_CLASSIFICATION_PROMPT` to ask for JSON output (`{"intent": "...", "confidence_score": 0.0-1.0}`). List the 5 intents.
  - **Proof:** Done. Checked that the prompt outputs JSON.

- [x] **TASK-1.3: Create Intent-Specific Generation Prompts**
  - **File:** `backend/chat/prompts.py`
  - **Action:** Add 5 new prompt functions (e.g., `get_factual_system_prompt`, `get_how_to_system_prompt`) wrapping the base grounding rules with specific angles.
  - **Proof:** Done. Checked that the functions are imported/defined correctly.

## Phase 2: Retrieval Routing

- [x] **TASK-2.1: Parse JSON Classification**
  - **File:** `backend/chat/retrieval.py`
  - **Action:** Update `QueryIntelligenceService.classify_query` to use `parse_json_from_llm`. Extract and return `(intent: str, confidence_score: float)`. Fallback to `("factual", 0.0)` if parsing fails.
  - **Proof:** Done. Checked that the changes parse JSON and return tuple.

- [x] **TASK-2.2: Apply Fallback & Routing Logic**
  - **File:** `backend/chat/retrieval.py`
  - **Action:** In `AdvancedRetrievalService.retrieve`, unpack the tuple. If `confidence < 0.6`, force `intent = "factual"`. Store `trace.classification` and `trace.classification_confidence`. Apply `intent`-based config overrides (e.g. `intent == "how_to"` -> `config.hyde_enabled = True`).
  - **Proof:** Done. Checked that routing uses the new intents.

## Phase 3: Generation Service Plumbing

- [x] **TASK-3.1: Modify GenerationService Signature**
  - **File:** `backend/chat/generation.py`
  - **Action:** Update `generate_answer` and `generate_answer_stream` to accept `intent: Optional[str] = None`.
  - **Proof:** Done. Syntax check passed.

- [x] **TASK-3.2: Dynamic Prompt Selection**
  - **File:** `backend/chat/generation.py`
  - **Action:** Inside `GenerationService`, map the `intent` to the correct prompt function from `prompts.py`.
  - **Proof:** Done. Syntax check passed.

- [x] **TASK-3.3: Pass Intent from ChatService**
  - **File:** `backend/chat/service.py`
  - **Action:** In `ChatService.process_turn`, extract `trace.classification` and pass it as `intent` to `generation_service.generate_answer()`.
  - **Proof:** Done. Syntax check passed.

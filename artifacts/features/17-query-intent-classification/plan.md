# Implementation Plan: 17 Query Intent Classification

## Goal
Implement query intent classification to route queries to specialized retrieval pipelines (Factual, Comparison, How-to, Troubleshooting, Exploratory) and use intent-specific generation prompts. This plan translates the approved `spec.md` into concrete, sequenced implementation tasks.

## Open Questions
- Is modifying the `GenerationService.generate_answer(context_package, stream, intent)` signature acceptable for plumbing the intent, or would you prefer extending the `ContextPackage` schema? (I've proposed modifying `generate_answer` as it keeps the Context payload purely data-focused).

## Proposed Changes

### 1. Schemas (`backend/schemas/chat.py`)
- **[MODIFY] backend/schemas/chat.py**: Add `classification_confidence: Optional[float] = None` to `RetrievalTrace`.

### 2. Prompts (`backend/chat/prompts.py`)
- **[MODIFY] backend/chat/prompts.py**:
  - Update `QUERY_CLASSIFICATION_PROMPT` to instruct the LLM to return JSON with `{"intent": "...", "confidence_score": 0.9}`. Valid intents: `factual`, `comparison`, `how_to`, `troubleshooting`, `exploratory`.
  - Create 5 new generator functions (e.g., `get_factual_system_prompt`, `get_how_to_system_prompt`) that inherit the strict RAG citation rules but set the specific rhetorical angle.

### 3. Retrieval Services (`backend/chat/retrieval.py`)
- **[MODIFY] backend/chat/retrieval.py**:
  - **`QueryIntelligenceService.classify_query`**: Parse the LLM's JSON response using `parse_json_from_llm` and return a tuple: `(intent: str, confidence: float)`.
  - **`AdvancedRetrievalService.retrieve`**: 
    - Receive `(intent, confidence)`.
    - Apply fallback: If `confidence < 0.6`, set `intent = "factual"`.
    - Record `classification_confidence` in `RetrievalTrace`.
    - Map routing strategies:
      - `factual` -> Skip expansion, baseline search.
      - `comparison` -> Set `config.query_decomposition_enabled = True`.
      - `how_to` -> Set `config.hyde_enabled = True`.
      - `troubleshooting` -> Set `config.synonym_expansion_enabled = True`.
      - `exploratory` -> Set `config.query_expansion_enabled = True`.

### 4. Generation & Service Plumbing (`backend/chat/service.py` & `backend/chat/generation.py`)
- **[MODIFY] backend/chat/generation.py**:
  - Update `GenerationService.generate_answer` to accept `intent: Optional[str] = None`.
  - Route to the correct prompt function based on the `intent` (defaulting to the original grounded prompt).
- **[MODIFY] backend/chat/service.py**:
  - In `ChatService.process_turn`, extract `trace.classification` after retrieval.
  - Pass the intent classification to `self.generation_service.generate_answer(..., intent=trace.classification)`.

## Verification Plan
### Automated Tests
- Run `pytest` on `backend/chat/` to ensure no syntax or typing regressions.
### Manual Verification
- Execute 5 test queries matching each intent via the API or terminal.
- Verify in the logs/trace that the `classification` and `classification_confidence` match expectations.
- Verify that `RetrievalTrace.routing.selected_strategy` matches the strategy assigned to that intent.

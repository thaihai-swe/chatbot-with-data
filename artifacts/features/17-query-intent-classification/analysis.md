# Research Analysis: 17 Query Intent Classification

## Investigation Target
Map the current state of query classification, retrieval strategies, and prompt generation to identify the narrowest surface for adding specialized pipelines per query intent (Factual, Comparison, How-to, Troubleshooting, Exploratory).

## Current State & Existing Behavior
- **Query Intelligence & Routing Boundary (`backend/chat/retrieval.py`)**: 
  - `QueryIntelligenceService.classify_query(query_text)` calls an LLM to classify queries into 5 existing categories (`simple`, `multi_hop`, `comparative`, `conversational`, `out_of_domain`).
  - The returned string label is used by `AdvancedRetrievalService.retrieve()` to configure query expansions and decompositions (e.g. `multi_hop` triggers decomposition, `simple` skips expansion).
  - The classification is recorded in `RetrievalTrace.classification` (a string).
- **Generation & Prompts Boundary (`backend/chat/service.py`, `backend/chat/generation.py`, `backend/chat/prompts.py`)**:
  - `ChatService.process_turn` invokes `GenerationService.generate_answer(context_package)`.
  - `prompts.py` defines a single, universal `GROUNDED_CHAT_SYSTEM_PROMPT` which is used for all queries regardless of classification.
  - There is currently no intent confidence scoring, and no specialized generation prompt templates based on intent.

## Unchanged Behavior to Preserve
- **Safety Checks**: Pre-retrieval query checks, chunk safety checks, and grounding evaluation.
- **Base Retrieval**: `RetrievalService.retrieve_relevant_chunks` and its baseline execution logic.
- **Orchestration Flow**: The sequential workflow in `ChatService.process_turn` (Safety -> Retrieval -> Evaluation -> Context -> Generation).
- **Collection Routing**: If enabled, should continue operating alongside or before intent classification.

## Narrowest Surface That Matters
1. **`backend/chat/prompts.py`**: 
   - Update `QUERY_CLASSIFICATION_PROMPT` to output JSON containing the new intents (Factual, Comparison, How-to, Troubleshooting, Exploratory) and an `intent_confidence` score (float).
   - Add new intent-specific generation prompts.
2. **`backend/schemas/chat.py`**:
   - Update `RetrievalTrace` or create a new trace model to store the parsed intent classification and confidence score.
3. **`backend/chat/retrieval.py` (`QueryIntelligenceService` & `AdvancedRetrievalService`)**:
   - Update `classify_query` to parse the new JSON response (intent, confidence).
   - Update routing logic in `AdvancedRetrievalService` to map the new intents to the appropriate retrieval strategies (e.g., How-to might trigger decomposition, Exploratory might trigger expansion, Factual triggers baseline).
4. **`backend/chat/service.py` & `backend/chat/generation.py`**: 
   - Extract the classified intent from the `RetrievalTrace`.
   - Pass the intent into the context package or directly to `GenerationService` so it can select the corresponding intent-specific system prompt.

## Findings & Risks
- **Finding:** The current query classification returns a plain text string label. Moving to JSON output for classification will require updating `QueryIntelligenceService` to use a JSON parser (like `parse_json_from_llm`).
- **Finding:** `ChatService` does not currently pass the retrieval trace (or the classification result within it) into `GenerationService`. The intent will need to be explicitly plumbed through to generation.
- **Risk:** Changing the generation prompt for different intents might break the strict grounding and citation instructions. We must ensure every intent-specific prompt still enforces citation rules and strict context adherence.

## Next Proving Step
Proceed to `aiddk-spec` to define the JSON schema for classification (including confidence scoring), map the new intents to retrieval strategies, and draft the required intent-specific generation prompts.

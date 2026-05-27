# Specification: 17 Query Intent Classification

## 1. Context and Problem
Currently, all user queries are routed through a generic processing pipeline. A single "grounded generation" prompt is used regardless of whether the user is asking a direct factual question, comparing two entities, troubleshooting an error, or exploring a broad topic. Additionally, while the retrieval layer has dynamic routing based on simple text classifications, it lacks intent confidence scoring and nuanced retrieval strategies tailored to specific query types.

Different query intents need different retrieval strategies and different rhetorical angles in the final response to provide the best user experience.

## 2. Outcomes and Goals
- Classify incoming user queries into one of five distinct intents: Factual, Comparison, How-to, Troubleshooting, or Exploratory.
- Generate a confidence score for the classification.
- Dynamically route the query to the most appropriate combination of advanced retrieval techniques (e.g., expansion, decomposition, HyDE) based on its intent.
- Ensure the final generation uses an intent-specific system prompt that emphasizes the right angle (e.g., procedural vs. comparative) while maintaining strict factual grounding.

## 3. Scope Boundaries
### In Scope
- Modifying `QUERY_CLASSIFICATION_PROMPT` to enforce JSON output with `intent` and `confidence_score`.
- Updating the schema (`RetrievalTrace` and `ChatTurnResponse`) to persist intent classification and confidence.
- Implementing a mapping in `AdvancedRetrievalService` between the intent and specific retrieval strategies.
- Creating 5 fluid, intent-specific prompt templates in `prompts.py` that inherit the base grounding rules.
- Modifying the orchestration in `ChatService` to pass the detected intent to the `GenerationService`.

### Out of Scope
- Adding new intents beyond the five requested.
- Changing the underlying LLM provider or vector database configurations.

### Non-Goals
- We are not building a local classification model; we will continue using the LLM for intent classification.
- We will not enforce strict structural formatting (e.g., Markdown tables or numbered lists) in the prompts, allowing the model to remain fluid.

## 4. Primary User Scenarios
1. **The Factual Lookup:** A user asks "What is the capital of France?". The system classifies it as `Factual` (high confidence), uses baseline hybrid retrieval, and answers directly using the factual prompt template.
2. **The Comparative Analysis:** A user asks "Compare the memory usage of v1 vs v2". The system classifies it as `Comparison`, triggers Query Decomposition to fetch docs for both versions, and answers using the comparison prompt template.
3. **The Troubleshooting Effort:** A user says "I keep getting error code 500 when logging in." The system classifies it as `Troubleshooting`, uses Synonym Expansion (for error codes), and answers with a helpful troubleshooting angle.

## 5. Gray-Area Decisions
- **Fallback Strategy:** If the classification `confidence_score` is less than `0.6`, the system will fall back to treating the query as `Factual`. This ensures a safe baseline retrieval and standard grounded response when the intent is ambiguous.
- **Retrieval Strategy Mapping:** 
  - `Factual`: Baseline (no expansion)
  - `Comparison`: Query Decomposition (Multi-hop)
  - `How-to`: HyDE (Hypothetical Document Embeddings for procedural contexts)
  - `Troubleshooting`: Synonym Expansion (to catch error aliases)
  - `Exploratory`: Query Expansion (to broaden search surface)
- **Prompt Formatting:** Intent-specific prompts will focus on the *rhetorical angle* (e.g., "explain steps clearly" for How-to) rather than dictating strict UI structures like markdown tables, allowing natural fluidity.

## 6. Acceptance Criteria
1. **AC1: JSON Classification:** The query intelligence service outputs a JSON object with a valid intent string and a float confidence score.
   - *Verification:* Reviewer runs a query and inspects the `RetrievalTrace` output in the API response or logs to confirm JSON parsing and fields exist.
2. **AC2: Fallback Logic:** Queries with a confidence score below 0.6 are routed using the `Factual` strategy.
   - *Verification:* Reviewer mocks the LLM classification to return `0.4` confidence and verifies via logs/trace that the `Factual` fallback logic executed.
3. **AC3: Specialized Retrieval Routing:** Each of the 5 intents triggers its designated retrieval strategy.
   - *Verification:* Reviewer submits test queries for each intent and verifies the `RetrievalTrace` shows the correct strategy was enabled (e.g., `hyde_enabled` for How-to).
4. **AC4: Intent-Specific Prompts:** The final generated answer uses the prompt corresponding to the classified intent.
   - *Verification:* Reviewer inspects the final LLM prompt payload (via logs or debug trace) to ensure the intent-specific system instructions were injected.
5. **AC5: Unchanged Grounding:** The generated answers still contain accurate citations and do not hallucinate outside the retrieved context.
   - *Verification:* Run the existing automated groundedness evaluations and confirm the scores do not regress.

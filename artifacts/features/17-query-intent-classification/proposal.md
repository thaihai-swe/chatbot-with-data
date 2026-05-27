# Proposal: 17 Query Intent Classification

## Summary
Implement a robust query intent classification system that categorizes queries into five specific intents (Factual, Comparison, How-to, Troubleshooting, Exploratory) with an associated confidence score. This classification will dynamically route the query to the most appropriate retrieval strategy and select an intent-specific generation prompt, improving both accuracy and relevance.

## Proposed Scope
**In Scope:**
- Updating `QUERY_CLASSIFICATION_PROMPT` to output a JSON object containing the intent classification and a float `confidence_score` (0.0 to 1.0).
- Mapping the 5 intents to specific retrieval strategies:
  - **Factual**: Baseline hybrid search (no expansion needed).
  - **Comparison**: Query decomposition (multi-hop retrieval for each entity).
  - **How-to**: Baseline or Expansion (focus on procedural steps).
  - **Troubleshooting**: Synonym expansion (for error codes/symptoms) or HyDE.
  - **Exploratory**: Query expansion (to gather broader context).
- Defining 5 intent-specific generation prompts in `prompts.py` that inherit base grounding rules but adjust the structure of the answer (e.g., step-by-step for How-to, side-by-side for Comparison).
- Plumbing the intent from `RetrievalTrace` to the `GenerationService` so the correct prompt is used during generation.
- Updating `ChatTurnResponse` and `RetrievalTrace` schemas to persist the intent and confidence score.

**Out of Scope:**
- Completely overhauling the base `RetrievalService` or `GroundingService`.
- Adding new intents beyond the five requested.

## Open Questions (For Alignment)

1. **Fallback Strategy**: If the intent classification `confidence_score` falls below a certain threshold (e.g., < 0.6), should we default to a generic "Factual" retrieval and generic generation prompt? What should that threshold be?
2. **Retrieval Mapping**: Does the proposed mapping above (e.g., Comparison -> Decomposition, Troubleshooting -> Synonym Expansion) match your expectations, or do you have specific preferences for how these intents are retrieved?
3. **Intent Prompts**: Should the intent-specific prompts enforce strict structural formatting (e.g., "Always use bullet points for How-to") or remain fluid while just emphasizing the angle?

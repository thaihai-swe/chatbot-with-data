# Manual Testing Scenarios: 17 Query Intent Classification

This document provides human-executable scenarios to verify the intent classification and routing logic.

## Scenario 1: Factual Query (Baseline Retrieval)
1. **Action:** Send a chat message: "What is the primary function of the chunk repository?"
2. **Expected Trace:** 
   - `classification` should be `"factual"`.
   - `classification_confidence` should be high (e.g., `> 0.8`).
   - `routing.selected_strategy` should be `"baseline"`.
3. **Expected Output:** A direct, factual answer with citations.

## Scenario 2: Comparative Analysis (Decomposition)
1. **Action:** Send a chat message: "Compare the differences between the Semantic and Keyword retrieval modes."
2. **Expected Trace:** 
   - `classification` should be `"comparison"`.
   - `routing.selected_strategy` should be `"decomposition"`.
   - `transformations.sub_questions` should contain split questions about Semantic mode and Keyword mode.
3. **Expected Output:** An answer that clearly contrasts the two concepts, driven by the comparison prompt.

## Scenario 3: How-To / Procedural (HyDE)
1. **Action:** Send a chat message: "How do I configure the chatbot to use strict safety mode?"
2. **Expected Trace:**
   - `classification` should be `"how_to"`.
   - `routing.selected_strategy` should be `"hyde"`.
   - `transformations.hyde_doc` should contain a generated hypothetical document.
3. **Expected Output:** A step-by-step or procedural instruction list.

## Scenario 4: Troubleshooting (Synonym Expansion)
1. **Action:** Send a chat message: "Why am I getting a timeout error when uploading a large PDF?"
2. **Expected Trace:**
   - `classification` should be `"troubleshooting"`.
   - `routing.selected_strategy` should be `"synonym_expansion"`.
3. **Expected Output:** A helpful troubleshooting response aimed at root causes.

## Scenario 5: Fallback Logic (Low Confidence)
1. **Action:** (Requires mocking) Temporarily force the LLM prompt to return a `confidence_score` of `0.2` or send a completely ambiguous query.
2. **Expected Trace:**
   - `classification` should log the original intent but immediately fall back to `"factual"`.
   - `routing.selected_strategy` should fall back to `"baseline"`.
3. **Expected Output:** A generic, safe factual answer without hallucinated expansions.

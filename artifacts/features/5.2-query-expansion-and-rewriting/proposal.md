# Proposal: Query Expansion and Rewriting

## 💡 The Problem
User queries are often shorthand, slang-heavy, or phrased in a way that doesn't align well with the technical language of the knowledge base documents. Standard "Expansion" generates variations, but if the core intent is unclear or "noisy," those variations are also noisy. We need a "Rewriting" step to normalize the intent into a standalone, formal search query *before* or *alongside* expansion, without relying on conversation history.

## 🎯 Objectives
- **Intent Normalization:** Transform messy user input into a clean, standalone search string.
- **Precision Optimization:** Ensure the core query is as searchable as possible for vector and keyword engines.
- **Improved Recall via Pipeline:** Use the rewritten query as the high-quality seed for expansion variations.

## 🛠 High-Level Approach
- **Standalone Rewriting:** Implement a `rewrite_query` method in `QueryIntelligenceService` that takes ONLY the current query and produces a "normalized" version.
- **Two-Stage Intelligence:** 
  1. **Rewrite:** Normalize intent (e.g., "how much?" -> "What are the pricing details and costs?").
  2. **Expand:** Generate variations based on the *rewritten* version.
- **Pipeline Update:** Update `AdvancedRetrievalService` to orchestrate this new sequential flow: Raw -> [Rewrite] -> [Expand].
- **UI Visibility:** Show the "Clean Intent" (Rewritten Query) separately in the Retrieval Trace.

## ⚠️ Known Constraints / Risks
- **No Context Awareness:** The rewriter will not know about previous turns (as per explicit instruction). It must infer meaning entirely from the single input.
- **Hallucination Risk:** Rewriting might add specific terms not intended by the user.
- **Token Usage:** Adding a separate rewriting step increases LLM latency and cost.

## ✅ Success Criteria
- [ ] AC-1: Shorthand queries (e.g., "eligibility?") are rewritten into formal questions.
- [ ] AC-2: Expansion variations are visibly higher quality when derived from a rewritten seed.
- [ ] AC-3: The system can be configured to use both the raw user input and the rewritten intent for retrieval.

---
**Status:** 🟢 Aligned
**Decisions:**
- **Rewriting vs Expansion:** Rewriting is for intent normalization (formalization); Expansion is for variation generation.
- **Combined Expansion:** The system will generate expansion variations for BOTH the raw user query and the rewritten query.
- **Visibility:** Both the Raw and Rewritten queries will be displayed in the Retrieval Trace.

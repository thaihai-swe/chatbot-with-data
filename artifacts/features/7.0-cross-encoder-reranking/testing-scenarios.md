# Testing Scenarios: 7.0-cross-encoder-reranking

## Scenario 1: Semantic Overlap vs Exact Match
**Goal:** Verify the FlashRank cross-encoder can prioritize a semantically matching chunk over a chunk with high keyword overlap but incorrect context.

**Setup:**
1. Upload the three files from `feature-test/test_docs` into a collection.
   - `doc_a_distractor.txt`
   - `doc_b_target.txt`
   - `doc_c_irrelevant.txt`
2. Ensure `backend/config/settings.json` has `reranker_provider` set to `flashrank`.
3. Start or restart the backend server.

**Execution:**
- **Action:** Ask the query: "What is the return policy for defective electronics?"
- **Expected Outcome:** The system should cite `doc_b_target` as the primary source (giving 90 days). It should also correctly trigger a Source Contradiction Warning against `doc_a_distractor` (which claims 30 days). `doc_c_irrelevant` should be ignored.

**Status:** PASS (Verified via manual UI test in session).

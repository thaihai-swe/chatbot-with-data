# Cross-Encoder Reranking Test

This directory contains test files and instructions to verify the `7.0-cross-encoder-reranking` feature. The goal is to see if the new reranker correctly prioritizes the document that actually answers the question, rather than the one that just has the most keyword overlap.

## Test Data
There are 3 documents in `test_docs/`:
1. `doc_a_distractor.txt`: Contains lots of overlapping keywords ("return", "policy", "electronics", "defective") but gives the *wrong* answer (says electronics must be unopened).
2. `doc_b_target.txt`: Contains the *actual* answer for defective electronics (can be returned within 90 days).
3. `doc_c_irrelevant.txt`: Irrelevant filler.

## How to Test via the UI

1. Start the application (`backend` and `frontend`).
2. Create a new collection called "Return Policies".
3. Upload all three text files from the `test_docs/` folder into this collection.
4. Open the Chat Panel and ensure the "Return Policies" collection is selected.
5. **Ask the following question:**
   > "What is the return policy for defective electronics?"

## Expected Result
- **X-Ray Panel Observation:** Open the X-Ray panel (if enabled) or look at the citation sources for the answer. 
- You should see that `doc_b_target.txt` was given the highest `rerank_score` and was used as the primary source for the answer.
- **Chat Answer:** The LLM should correctly answer that you can return defective electronics within 90 days for a full refund (citing `doc_b_target.txt`). 
- If the reranker is off or failing (falling back to dummy), `doc_a_distractor.txt` often scores higher in raw vector similarity due to its high density of the exact words used in the query.

## How to Test via Backend API

If you want to test the routing and reranking directly via the API without the UI:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the return policy for defective electronics?", "collection_ids": ["<your-collection-id>"]}'
```
Check the server logs to see the `FlashRank model: ms-marco-MiniLM-L-12-v2` initialization and the reranking trace.

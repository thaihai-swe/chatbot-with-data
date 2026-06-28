# RAG Pipeline — Anti-Patterns

> **Ownership:** Collaborative — skill-updated + user-maintained.
> **Updated by:** `/context-memory` post-ship sync when a failure mode is observed during a completed feature.

## Bypassing the Safety Layer

**Why it fails:** A new query endpoint or direct LLM call that skips `safety.py` exposes the system to prompt injection, data exfiltration, and ungrounded output.

**What to do instead:** Route all user input through `backend/chat/safety.py` before any processing. The safety check is the mandatory entry gate.

**Citation:** `brownfield-map.md` records this as preserved behavior #1 (CRITICAL risk path).

---

## Single-Strategy Retrieval Without Justification

**Why it fails:** Using only BM25 or only vector search misses results the other strategy would find. The hybrid approach is the core differentiator.

**What to do instead:** Default to hybrid search (BM25 + vector) via RRF fusion. Only use single-strategy retrieval when explicitly justified in the task spec (e.g., latency-critical paths where the accuracy tradeoff is understood).

**Citation:** `brownfield-map.md` records this as preserved behavior #2.

---

## Mutating Streaming Output

**Why it fails:** SSE streams send tokens one at a time. Attempting to edit or reformat the stream mid-flight breaks the frontend's incremental rendering.

**What to do instead:** Complete the full generation, then apply post-processing (citation extraction, grounding checks) before persisting. The frontend receives raw streaming tokens and handles display formatting locally.

**Citation:** `backend/chat/streaming.py` sends raw token events; frontend `XRayPanel` handles display formatting.

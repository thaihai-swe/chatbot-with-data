# Product Roadmap — Chat with Documents RAG System

**Created:** 2026-07-11  
**Basis:** Full production-readiness review of all RAG features  
**Status:** Draft — awaiting review before implementation

---

## Current State Summary

The system has a sophisticated RAG architecture (3-layer prompt injection detection, query intelligence with 6 transformations, hybrid retrieval with RRF, multi-hop reasoning, conflict detection, provenance graphs, ablation evaluation). However, **it is not production-ready** due to critical security, durability, and correctness gaps.

**6 of 15 tracked features** are fully shipped and reviewed. **8 are implemented but unverified.** The HTTP/security/deployment layer is the weakest link.

---

## Phase 0 — Critical Security & Data Safety (Blocker)

Target: No system can go to production without these.

### 0.1 Rotate committed API key and purge from git history

- **Problem:** `backend/.env.local` is git-tracked and contains a live API key. `.gitignore` covers `.env` but NOT `.env.local` — the key is in plaintext in git history.
- **Tasks:**
  - Rotate the exposed key at the provider.
  - `git rm --cached backend/.env.local`.
  - Add `.env*` pattern to `.gitignore`.
  - Purge the file from git history (BFG or `git filter-repo`).
  - Add a pre-commit hook (e.g., `detect-secrets`) to prevent future secret commits.
- **Acceptance:** `git log --all -- backend/.env.local` returns nothing. `.env.local` is gitignored. Pre-commit hook blocks secret commits.

### 0.2 Add authentication to all endpoints

- **Problem:** Zero auth — every endpoint is open including `PUT /settings` which rewrites all runtime config to disk. Any client can list/get/delete ANY chat session by ID.
- **Tasks:**
  - Choose an auth strategy (API key header, JWT, or OAuth2).
  - Add a `Depends(verify_auth)` dependency on every router.
  - Add user/owner concept to chat sessions (`chat_sessions.owner_id`).
  - Enforce ownership checks on session/turn/document access.
  - Add a settings-level auth toggle for local dev (off) vs production (on).
  - Add admin role for settings mutation and evaluation endpoints.
- **Acceptance:** Unauthenticated requests return 401. Users can only access their own sessions. `PUT /settings` requires admin role.

### 0.3 Add rate limiting

- **Problem:** No rate limiting — trivial DoS / cost-bomb via LLM calls.
- **Tasks:**
  - Add `slowapi` or equivalent rate-limit middleware.
  - Per-IP limits on chat turn submission (e.g., 30/min).
  - Per-IP limits on file upload (e.g., 10/hour).
  - Global limit on evaluation sanity-check endpoint (expensive LLM batch).
  - Per-user daily LLM token budget configurable in settings.
- **Acceptance:** Exceeding limit returns 429 with `Retry-After` header. Token budget exhaustion returns a clear message.

### 0.4 File upload validation

- **Problem:** No file size limit, no MIME whitelist, no content-type verification. Receives entire file into memory — OOM risk. Original extension is preserved — a `.exe` or `.html` is stored as-is.
- **Tasks:**
  - Enforce max upload size in FastAPI (e.g., 50MB) before reading file into memory.
  - Validate file extension against allowlist (`.pdf`, `.txt`, `.md`).
  - Validate `Content-Type` header matches extension.
  - Add magic-byte verification for PDFs (verify `%PDF` header).
  - Reject unknown extensions with 422.
- **Acceptance:** Uploading a 100MB file returns 413. Uploading a `.exe` returns 422. A renamed `.txt` with `.pdf` extension is rejected by magic-byte check.

### 0.5 SSRF protection for URL ingestion

- **Problem:** No blocklist for localhost/internal IP ranges. An attacker can ingest internal service URLs (`http://169.254.169.254/` metadata endpoint, `http://localhost:8000/` own API).
- **Tasks:**
  - Validate URL scheme is `http` or `https` only.
  - Resolve DNS and reject private/loopback/link-local IP ranges.
  - Block common metadata endpoints (AWS, GCP, Azure).
  - Add configurable domain allowlist.
  - Limit redirect following (max 3 hops, validate each destination).
- **Acceptance:** Ingesting `http://localhost:8000/api/settings` returns 422. External HTTPS URLs work normally.

### 0.6 Containerize the application

- **Problem:** Only Weaviate is containerized — no Dockerfile for the app or frontend. No production deployment artifact exists.
- **Tasks:**
  - Create `Dockerfile` for backend (Python 3.10 slim, `requirements.txt`, `uvicorn` entrypoint).
  - Create `Dockerfile` for frontend (Node build, nginx serve).
  - Extend `docker-compose.yml` with `backend`, `frontend`, and `weaviate` services.
  - Add `.dockerignore`.
  - Add environment variable injection via `docker-compose` env files.
- **Acceptance:** `docker-compose up` starts the full stack with working health check on all services.

### 0.7 CORS hardening

- **Problem:** `allow_credentials=True` combined with `allow_methods=["*"]` and `allow_headers=["*"]` is overly permissive. With credentials, origins should be a restrictive allowlist.
- **Tasks:**
  - Set `allow_origins` from config (default to `http://localhost:5173` for dev).
  - For production, require explicit origin allowlist (no wildcard).
  - Restrict `allow_methods` to actual methods used (`GET, POST, PUT, PATCH, DELETE`).
  - Restrict `allow_headers` to actual headers used (`Content-Type, Authorization, X-Request-ID`).
- **Acceptance:** Production config rejects requests from non-allowlisted origins. Dev config works with frontend.

### 0.8 Error message sanitization

- **Problem:** Bare exception messages (including Weaviate connection strings, OpenAI API errors) land in the DB and are surfaced to API clients. Streaming error events expose `str(e)` to the client.
- **Tasks:**
  - Map known exception types to safe user-facing messages.
  - Never expose internal基础设施 details (URIs, stack traces, API keys in error messages).
  - Log full exception server-side; return generic message to client.
  - Sanitize streaming error events.
- **Acceptance:** API error responses contain no internal URIs, hostnames, or stack traces. Server logs retain full detail for debugging.

---

## Phase 1 — Correctness Fixes (High Priority)

Target: Fix bugs that produce wrong results or silent data loss.

### 1.1 Fix chunk-ID mismatch (breaks citations + telemetry)

- **Problem:** `ChunkRepository.get_chunk` returns rows with `id` column key, but all downstream consumers read `chunk.get("chunk_id")`. Parent-child expansion and multi-hop produce empty IDs. Citations on parent-expanded answers are unmappable.
- **Tasks:**
  - Normalize `get_chunk` return dict to include both `id` and `chunk_id` keys (or migrate all consumers to `id`).
  - Fix multi-hop chunk ID extraction to read `chunk_id` not `id`.
  - Verify all downstream consumers (reranking, context, citations, service).
  - Add a regression test that asserts chunk-id continuity through the full pipeline.
- **Acceptance:** Multi-hop trace `retrieved_chunk_ids` contains real UUIDs. Parent-expanded chunks have valid `chunk_id` in citations.

### 1.2 Fix partial-index status bug

- **Problem:** Both branches of the index status decision return `COMPLETED` — `PARTIAL` status is unreachable. Partially indexed documents are silently unsearchable with no surfaced reason. Batch insert ignores Weaviate's `batch.number_errors`.
- **Tasks:**
  - Change the error branch to return `IndexGenerationStatus.PARTIAL`.
  - Check `batch.number_errors` from Weaviate batch response.
  - Surface partial-index status to the ingestion attempt and frontend.
  - Add a warning badge in Document Library for partial-indexed documents.
- **Acceptance:** Ingestion attempt with some failed chunks shows `partial` status. Frontend displays a warning badge. Reindex action is available for partial documents.

### 1.3 Fix _restore_chunks data loss

- **Problem:** `_restore_chunks` re-creates chunk rows but NOT Weaviate vectors — old vectors already deleted. Silently loses data despite comment claiming "atomic restore." Parent-child `parent_chunk_id` also points at non-existent rows after re-create.
- **Tasks:**
  - Re-embed and re-insert vectors during restore, or don't delete vectors until new chunks are successfully indexed.
  - Make delete-old / insert-new ordered to avoid orphan state (delete chunks only after new vectors are confirmed).
  - Fix parent_chunk_id references during restore.
  - Add a test for the restore path covering both chunk rows and vectors.
- **Acceptance:** Re-chunking failure restores both chunk rows AND vectors. Parent-child relationships are preserved. Test passes.

### 1.4 Fix page-aware chunking dead code

- **Problem:** PageAwareChunker splits on `###PAGE_BREAK###` marker but PDF extractor joins pages with `\n` — page-aware chunking always falls through to fixed-size. The strategy is effectively dead code for the default PDF pipeline.
- **Tasks:**
  - Emit the page-break marker from the PDF extractor, or change the chunker to use a different mechanism (store page ranges per chunk metadata).
  - Add a test that verifies page boundaries are respected for multi-page PDFs.
  - Verify `page_number` metadata is correctly assigned to each chunk.
- **Acceptance:** PDF chunks contain correct `page_number` metadata. Each chunk stays within a single page. Citations reference correct page numbers.

### 1.5 Fix FixedSize chunker overlap math

- **Problem:** `self.overlap // 10` slices by sentence index using an arbitrary divisor. Overlap is effectively a no-op or behaves nothing like "N tokens of overlap."
- **Tasks:**
  - Implement token-based overlap: track sentence token counts, accumulate trailing sentences until overlap budget is met.
  - Re-estimate token count after joining sentences.
  - Add a test verifying overlap content appears at chunk boundaries and matches configured token count.
- **Acceptance:** Adjacent chunks share N tokens of overlap as configured. Token count of overlap is verifiable.

### 1.6 Wire semantic chunker embedding provider

- **Problem:** `ChunkingDispatcher` instantiates `SemanticChunker` without an `embedding_provider` — always degrades to Jaccard. The "semantic" strategy is therefore Jaccard-based, not embedding-based, despite the docstrings.
- **Tasks:**
  - Pass the embedding provider (from factory) to the dispatcher.
  - Pass it through to `SemanticChunker.__init__`.
  - Fix `sentences.index(s)` O(n²) bug that breaks on duplicate sentences.
  - Add a test verifying cosine similarity is used when a provider is available.
- **Acceptance:** Semantic chunker uses embeddings when available. Jaccard fallback only on timeout/error. Duplicate sentences don't cause score corruption.

### 1.7 Wire safety_mode config

- **Problem:** `safety_mode` is in settings but `check_query` is always called without it. Changing the setting has no effect — a dead config contract.
- **Tasks:**
  - Read `config.safety.safety_mode` in both `process_turn` and `stream_turn`.
  - Pass it to `check_query(query_text, mode=mode)`.
  - Also pass the mode to `check_chunks` for consistency.
  - Verify the strict/moderate/lenient thresholds actually change detection behavior.
- **Acceptance:** Setting `safety_mode=strict` increases detection sensitivity in a live query. Setting `lenient` decreases it. Changes take effect without restart.

### 1.8 Fix greedy-regex JSON parser

- **Problem:** `parse_json_from_llm` uses regex `r"(\[.*\]|\{.*\})"` with `re.DOTALL` — `.*` is greedy and unanchored, so for any response containing more than one JSON-shaped block (or any stray `{`/`}` later in prose), it captures from the first opener to the last closer, producing invalid JSON and a silent `None`.
- **Tasks:**
  - Replace greedy `.*` with non-greedy `.*?` or use a proper bracket-matching parser.
  - Handle multiple JSON blocks (return first valid or merge arrays).
  - Add test cases with multi-block LLM output and prose containing braces.
- **Acceptance:** LLM output with explanatory prose before/after JSON is parsed correctly. Multi-block responses return the intended JSON.

### 1.9 Fix collection routing in streaming path

- **Problem:** Sync `process_turn` does collection routing; streaming `stream_turn` does not — it only uses `[session.collection_id]`. The two paths have diverged.
- **Tasks:**
  - Extract collection routing into a shared method.
  - Call it from both sync and streaming paths.
  - Add a test verifying routing runs in both paths with the same logic.
- **Acceptance:** Streaming responses use the same collection routing as non-streaming. Identical queries produce identical routing decisions.

### 1.10 Fix test_hash Jaccard threshold for duplicate detection

- **Problem:** Jaccard on raw whitespace-tokenized text with hardcoded `0.75` threshold. No stopword removal, no stemming, no n-grams. Title-match returns `0.5` similarity even for completely unrelated docs sharing a generic title ("Introduction", "README"). False-positive risk is high.
- **Tasks:**
  - Remove stopwords before Jaccard calculation.
  - Make the Jaccard threshold configurable in settings.
  - Remove or rework the title-match heuristic (require text similarity above a minimum bar as well).
  - Add test cases for near-duplicate and clearly-distinct document pairs.
- **Acceptance:** Documents sharing only a generic title are not flagged as duplicates. Near-paraphrased documents are correctly detected.

---

## Phase 2 — Robustness & Observability (Medium Priority)

Target: Make the system resilient to failure and observable in production.

### 2.1 Add token budgeting to context assembly

- **Problem:** No token counting — all retrieved chunks concatenated into the system prompt regardless of model context limits. Intent-specific prompt variants exist but are unused dead code.
- **Tasks:**
  - Add `tiktoken` for token counting.
  - Set a configurable context budget (e.g., 80% of model context window).
  - Reserve budget for system prompt + chat history.
  - Allocate remaining budget to chunks; truncate or drop lowest-ranked chunks.
  - Add logging of budget allocation (chunks included/excluded, budget used).
- **Acceptance:** A query returning 20 large chunks does not exceed the model's context window. Dropped chunks are logged with reasons.

### 2.2 Add durable ingestion (job queue)

- **Problem:** `BackgroundTasks` is in-process and non-durable. Crash loses the job. Stuck `PROCESSING` attempts never recover — no reaper, no restart-on-boot.
- **Tasks:**
  - Choose a queue: Celery + Redis, or RQ, or a DB-backed polling loop.
  - Move `process_ingestion_attempt` to the queue.
  - Add a startup reaper for stuck `PROCESSING` attempts (re-queue or mark failed).
  - Add idempotency guard (lock on attempt_id) to prevent concurrent processing.
  - Add a job status webhook or WebSocket for completion notification.
- **Acceptance:** Killing the server mid-ingestion does not lose the job. Restart re-queues stuck attempts. Concurrent same-document processing is prevented.

### 2.3 Add Weaviate connection pool and reconnection

- **Problem:** A new Weaviate client is constructed per request. No reconnection on failure. No client reuse. URL parsing is fragile (breaks for URLs without scheme or with paths).
- **Tasks:**
  - Use a singleton or pooled Weaviate client with proper lifecycle management.
  - Use `urllib.parse` for URL parsing instead of string splitting.
  - Add reconnect logic on connection error.
  - Add circuit breaker for Weaviate outages (fail fast, don't pile up requests).
  - Add `validate_connection` health check on startup.
- **Acceptance:** Weaviate restart does not require app restart. Failed queries retry after reconnection. Circuit breaker prevents cascading failures.

### 2.4 Embedding cache keyed by content hash

- **Problem:** Cache keyed by `chunk_id` — re-ingesting the same text pays for embedding again. No content-level dedup of embeddings — only same-chunk-id reuse. Cache validity delete-then-reinsert has a race window (concurrent get_or_create hits UNIQUE constraint).
- **Tasks:**
  - Change cache key to `(text_hash, embedding_model)`.
  - Update `get_or_create` lookup to use text_hash.
  - Add migration to adjust the unique constraint.
  - Use `INSERT OR REPLACE` / `UPSERT` to fix the race window.
- **Acceptance:** Re-ingesting a document with unchanged text uses cached embeddings (no OpenAI calls for unchanged chunks). Concurrent get_or_create does not raise IntegrityError.

### 2.5 Batch embedding calls in ingestion

- **Problem:** Ingestion path makes one OpenAI call per chunk instead of using `embed_batch`. The batch method exists but is effectively unused for ingestion.
- **Tasks:**
  - Collect chunks into batches (e.g., 100 at a time).
  - Call `embed_batch` instead of per-chunk `embed`.
  - Handle partial batch failures (retry failed items individually).
  - Add retry/backoff to `embed_batch` (currently only single `embed` has retry).
  - Track per-batch cost stats.
- **Acceptance:** Ingestion of a 50-chunk document makes 1 batch call, not 50 single calls. Partial batch failures are retried without losing successful embeddings.

### 2.6 Add structured logging and metrics

- **Problem:** Plain-text logging only. No metrics. Health check doesn't probe dependencies. Error handler request IDs don't correlate with middleware IDs.
- **Tasks:**
  - Add `structlog` for JSON-structured logs searchable by request ID.
  - Add Prometheus metrics endpoint: request latency histogram, retrieval latency, generation latency, ingestion throughput, grounding score distribution, safety block rate.
  - Split health check: `/health` (liveness) and `/ready` (readiness — checks DB, Weaviate, LLM provider).
  - Fix error handler to reuse the request-scoped ID from middleware.
- **Acceptance:** `/metrics` returns Prometheus data. `/ready` fails if DB or Weaviate is down. Logs are searchable by request ID across all components.

### 2.7 Fix sync-in-async streaming blocking

- **Problem:** LLM provider's streaming iterator is synchronous; iterating it in an async generator blocks the event loop. Under load this will starve the async loop.
- **Tasks:**
  - Make `generate_completion(stream=True)` an async generator.
  - Or wrap the sync iterator with `asyncio.to_thread`.
  - Ensure concurrent SSE streams do not block each other.
- **Acceptance:** Two concurrent streaming responses both produce tokens without head-of-line blocking. Event loop is not blocked during streaming.

### 2.8 Fix duplicate detection scalability

- **Problem:** O(N) full-table scan loads every document into memory on every ingest. No DB uniqueness constraints. Race condition between dedupe check and insert.
- **Tasks:**
  - Add DB index on `file_hash` and `normalized_text_hash`.
  - Use indexed lookups for hash-based checks (exact match, same content).
  - Keep Jaccard similarity only for near-duplicate detection on a candidate subset.
  - Consider LSH / MinHash for large corpora (>10K docs).
  - Add a query timeout for the dedupe scan.
- **Acceptance:** Ingesting the 1000th document does not load 999 prior documents into memory. Hash-based dedupe is an indexed O(1) lookup.

### 2.9 Thread-safe safety scanner cache

- **Problem:** Fuzzy scanner uses a global module-level cache (`_GLOBAL_CORPUS_EMBEDDINGS`, `_CORPUS_LOADED`) that is not thread-safe. Concurrent first-loads could double-compute or corrupt the cache. Per-instance `_embedding_cache` is unbounded — memory leak.
- **Tasks:**
  - Add a thread lock around corpus initialization.
  - Bound the per-instance `_embedding_cache` with an LRU (e.g., `functools.lru_cache` or `cachetools.TTLCache`).
  - Extract corpus loading to a thread-safe singleton.
- **Acceptance:** Concurrent first-requests do not double-compute corpus embeddings. Long-running process does not leak memory.

### 2.10 Add fail-closed option for safety

- **Problem:** All 3 safety layers (heuristic, fuzzy, LLM) fail-open (return "safe" on error). No fail-closed option and no alert on degradation. The LLM scanner can be bypassed by adversarial queries that inject into the classifier prompt itself.
- **Tasks:**
  - Add a `safety_fail_mode` config option: `open` (current) or `closed` (block on scanner error).
  - Add an alert/log when any scanner degrades to fail-open.
  - Escape user query before interpolating into the safety classification prompt.
  - Add structured safety degradation events to metrics.
- **Acceptance:** In fail-closed mode, a scanner error blocks the query. Degradation is logged at WARNING level. Classifier prompt is not injectable.

### 2.11 Add multi-worker cancellation store

- **Problem:** Cancellation uses an in-process `set` — not distributed. A cancel request hitting a different worker won't stop the generating worker.
- **Tasks:**
  - Use Redis or DB table for cancellation flags.
  - Check the shared store instead of in-process `set`.
  - Add TTL/cleanup for stale cancellation entries.
- **Acceptance:** Cancel request from any worker stops the streaming turn on the generating worker. Stale entries are cleaned up.

### 2.12 Fix grounding evidence threshold

- **Problem:** Default `min_similarity_threshold = -0.2` is too permissive — nearly any non-empty result set passes the evidence gate.
- **Tasks:**
  - Raise default to a meaningful value (e.g., 0.3 or configurable per use case).
  - Make it configurable via settings with a sensible per-mode default.
  - Add a test verifying refusal on low-similarity results.
- **Acceptance:** Low-similarity retrieval results produce a refusal instead of a forced answer. Threshold is configurable.

### 2.13 Improve citation quote matching

- **Problem:** Jaccard on raw whitespace tokens — no stopword removal, no lemmatization, no punctuation stripping. A claim sentence and chunk sharing common stopwords ("the", "a", "of") can clear `0.35`. Implicit citation injection mutates answer text post-generation at a low `0.35` threshold.
- **Tasks:**
  - Add stopword removal and lemmatization before similarity calculation.
  - Raise the implicit citation injection threshold (e.g., 0.6).
  - Log implicit citations at WARNING level for auditability.
  - Consider disabling implicit citation injection by default.
- **Acceptance:** Citation quotes match on semantic content, not common stopwords. Implicit citations are rare and logged for review.

### 2.14 Add query intelligence caching

- **Problem:** Query intelligence re-issues an LLM call on every request for classify/expand/decompose/HyDE/synonyms. No LRU, no Redis, no result memoization. Repeated or similar queries waste LLM calls.
- **Tasks:**
  - Add an LRU cache (TTL-based) for classification, expansion, decomposition, HyDE, and synonym results.
  - Key cache by normalized query text + config flags.
  - Add cache hit/miss metrics.
- **Acceptance:** Repeated identical queries hit the cache (no LLM call). Cache hit rate is observable in metrics.

### 2.15 Batch chunk hydration in retrieval

- **Problem:** Retrieval issues one `get_chunk` query per result inside the loop — N round-trips to SQLite per retrieval. Document batch fetch exists but isn't used.
- **Tasks:**
  - Add a `get_chunk_batch(ids)` method to `ChunkRepository`.
  - Use batch fetch in retrieval after Weaviate returns IDs.
  - Use batch fetch in parent-child expansion.
- **Acceptance:** Retrieval with 20 results makes 1 batch query, not 20 individual queries.

---

## Phase 3 — Feature Completeness (Lower Priority)

Target: Close gaps between implemented features and their intended scope.

### 3.1 Enable real reranker by default

- **Problem:** FlashRank cross-encoder exists but `dummy` is the default. The dummy reranker just sorts by similarity score — produces no new signal.
- **Tasks:**
  - Change default `reranker_provider` to `flashrank`.
  - Add error handling around FlashRank inference (catch model load/inference errors, fallback to similarity sort).
  - Add a test for FlashRank fallback path.
  - Benchmark latency impact in the eval dashboard.
- **Acceptance:** Default out-of-the-box config uses cross-encoder reranking. Inference errors don't crash retrieval. Latency overhead is measured.

### 3.2 Wire intent-specific generation prompts

- **Problem:** 5 intent-specific system prompts (factual, comparison, how_to, troubleshooting, exploratory) are defined but never used. Classification doesn't reach generation. The `system_prompt` field in the context package is computed but never read.
- **Tasks:**
  - Pass classification result through the context package to `generate_answer`.
  - Use the matching intent prompt when available; fallback to grounded prompt.
  - Remove the dead `system_prompt` field or wire it properly.
  - Add a test verifying different query types produce different system prompts.
- **Acceptance:** A "how-to" query uses `get_how_to_system_prompt` instead of the generic grounded prompt. Intent selection is visible in traces.

### 3.3 Implement reference resolution for retrieval queries

- **Problem:** No coreference resolution — follow-up queries like "what about its second quarter?" retrieve against the raw ambiguous query. Entity tracking per session doesn't exist.
- **Tasks:**
  - Add a query rewriting step that uses recent chat history to resolve pronouns and abbreviations.
  - Wire it BEFORE retrieval (not just LLM context).
  - Add entity tracking per session (extract key entities from first turn, reference in follow-ups).
  - Add a test with multi-turn dialog where follow-up queries reference prior entities.
- **Acceptance:** Follow-up query "what about Q2?" in a session about "Acme Corp" retrieves Q2 results for Acme Corp.

### 3.4 Implement RAGAS evaluation metrics

- **Problem:** Only in-house groundedness heuristic. No faithfulness, answer relevance, context precision/recall. `expected_answer` field in golden dataset is unused.
- **Tasks:**
  - Add `ragas` to `requirements.txt`.
  - Compute: faithfulness, answer relevance, context precision, context recall.
  - Wire RAGAS metrics into the evaluation dashboard.
  - Use `expected_answer` field from the golden dataset as ground truth.
  - Add per-metric pass/fail thresholds.
- **Acceptance:** Evaluation run produces faithfulness and answer relevance scores alongside recall and groundedness. Metrics use the golden dataset's `expected_answer`.

### 3.5 Strip mock data from evaluation dashboard

- **Problem:** Hardcoded latency `420ms`, fabricated relevancy formula `(passed/total)*98`, hardcoded delta chips `+1.2%`/`-30ms`, hardcoded CASE→source mapping. Dashboard misleads users at production time.
- **Tasks:**
  - Replace hardcoded latency with actual mean latency from the run.
  - Replace fabricated relevancy formula with real metric.
  - Remove hardcoded delta chips or compute them from run history.
  - Replace `getMockSource` with actual source document names from the API.
- **Acceptance:** Evaluation dashboard displays only real data from the API. No hardcoded numbers remain.

### 3.6 Wire or remove settings stubs

- **Problem:** Integrations, Billing, Team categories are placeholders. PII Redaction, Prompt Injection toggles, reranker_model, API keys are mock-only (localStorage, never sent to backend).
- **Tasks:**
  - Either implement backend support for each mock setting or remove the UI controls.
  - If keeping as "coming soon," label them clearly as not functional and disable the control.
  - Move all real settings to use the `PUT /settings` backend endpoint.
- **Acceptance:** Every settings toggle the user sees actually changes system behavior. No mock-only controls remain.

### 3.7 Implement conversation memory compression

- **Problem:** Sliding window only (naive 10-turn slice). No context compression, no summarization of old turns. 10 long turns can blow the context window.
- **Tasks:**
  - Summarize turns beyond the sliding window using an LLM (once per N turns).
  - Include the summary as a "conversation so far" block in the context.
  - Make the summary recency-weighted (older turns get less detail).
  - Add a test verifying old-context compression reduces token count while preserving key facts.
- **Acceptance:** A 20-turn conversation uses a compressed summary for turns 1-10 and full text for 11-20. Total token count stays within budget.

### 3.8 Add session ownership and expiry

- **Problem:** Any client can list/get/delete ANY session by ID. No `owner_id` on sessions. No session expiry or cleanup logic.
- **Tasks:**
  - Add `owner_id` column to `chat_sessions` (migration).
  - Enforce ownership in all session/turn endpoints.
  - Add `expires_at` or auto-cleanup for sessions older than N days.
  - Add a cron/reaper to delete expired sessions.
- **Acceptance:** Users can only list/get/delete their own sessions. Expired sessions are automatically cleaned up.

### 3.9 Fix reranker order vs parent-child dependency

- **Problem:** Reranker scores children, then parent-child expansion swaps in chunks the reranker never saw. Parent substitution silently invalidates reranker order.
- **Tasks:**
  - Run parent-child expansion BEFORE reranking (so reranker sees parents).
  - Or skip reranking for parent-expanded chunks and carry child scores.
  - Document the intended ordering.
  - Add a test verifying reranker scores apply to the correct chunk identity.
- **Acceptance:** Reranker order is consistent with the final chunk list. No score invalidation from parent-child swap.

### 3.10 Add per-hop intra-call timeout for multi-hop

- **Problem:** Multi-hop timeout is checked BETWEEN hops, not during LLM calls. A single slow LLM/retrieval hop is unbounded. `_handle_step_failure` is dead code — never invoked.
- **Tasks:**
  - Add per-hop LLM call timeout (e.g., 10s per hop).
  - Wire `_handle_step_failure` to run on hop failure instead of just breaking.
  - Add configurable timeout via settings.
- **Acceptance:** A hung LLM call in hop 2 times out and triggers fallback. `_handle_step_failure` is invoked and logged.

### 3.11 Add web extractor robustness

- **Problem:** No User-Agent, no max-content-length, no redirect policy. Vulnerable to server blocks and unbounded response sizes.
- **Tasks:**
  - Add a configurable User-Agent header.
  - Enforce max response size (stream-download with size cap).
  - Limit redirect following (max 3 hops, validate each destination against SSRF rules).
  - Validate response Content-Type is HTML/text.
  - Return `file_hash` for URL-sourced documents (hash the fetched HTML).
- **Acceptance:** Large pages are truncated at the size limit. Redirects are validated. URL documents have a non-null `file_hash`.

---

## Phase 4 — New Feature Suggestions

Target: Enhance the RAG system beyond current scope.

### 4.1 PII Detection & Redaction

- **Problem:** PII detection is not implemented (roadmap item per architecture docs). Users may ingest documents containing SSNs, credit card numbers, medical records, or other sensitive data.
- **Tasks:**
  - Add a PII scanner as an ingestion pipeline step (regex + NLP model for common PII types).
  - Redact PII before chunking and embedding (replace with `[REDACTED-SSN]` tokens).
  - Add a per-document PII report visible in Document Library.
  - Add configurable PII categories (healthcare, financial, personal, custom).
  - Add a settings toggle for PII detection (on/off, categories).
- **Acceptance:** Ingesting a document with SSNs and emails replaces them with redaction tokens before embedding. Document Library shows a PII badge.

### 4.2 Query/Result caching layer

- **Problem:** Repeated or similar queries waste LLM and retrieval calls. No caching at any layer.
- **Tasks:**
  - Add a Redis (or SQLite-backed) cache for: collection routing decisions, query intelligence results (classified+expanded queries), retrieval results for identical query+collection combos, and LLM answers for identical query+context combos.
  - Add semantic cache: queries with >0.95 embedding similarity hit the cache.
  - Add cache invalidation on document reindex/deletion.
  - Add cache hit/miss metrics.
- **Acceptance:** Repeated identical queries return cached results in <50ms. Cache invalidates when a document in the relevant collection is reindexed.

### 4.3 Conversation export

- **Problem:** No way to export a chat session for sharing, archival, or compliance.
- **Tasks:**
  - Add `GET /chat/sessions/{id}/export?format=markdown|pdf|json`.
  - Include query, answer, citations, trace, and groundedness score in the export.
  - Add frontend "Export" button on session detail.
  - Add a shareable read-only link (with auth).
- **Acceptance:** A 10-turn conversation exports to a well-formatted Markdown file with citations linked to source chunks.

### 4.4 Document access control (per-document permissions)

- **Problem:** All documents are visible to all users. In multi-tenant or enterprise scenarios, documents need access control.
- **Tasks:**
  - Add `access_level` to documents (public, private, restricted).
  - Add `authorized_users` M:M table for restricted documents.
  - Enforce access control in retrieval (filter out chunks from inaccessible documents).
  - Enforce access control in Document Library (hide or show lock icon).
  - Add UI for setting document access level.
- **Acceptance:** A user without access to a restricted document gets no chunks from it in retrieval. Document Library shows a lock icon.

### 4.5 Bulk ingestion

- **Problem:** One file at a time. Uploading a folder or a zip archive is not supported.
- **Tasks:**
  - Add `POST /ingestion/bulk-upload` accepting a zip file or multiple files.
  - Extract and process each file in the queue (respecting dedupe).
  - Add a batch status view in Document Library.
  - Add progress tracking (% complete, files failed).
- **Acceptance:** Uploading a 50-file zip processes all files. Document Library shows batch progress.

### 4.6 Relevance feedback (thumbs up/down)

- **Problem:** No feedback loop. System can't learn from user satisfaction signals.
- **Tasks:**
  - Add a `POST /chat/turns/{id}/feedback` endpoint (rating: `positive` | `negative`, optional comment).
  - Store feedback in `chat_turns.feedback_rating` (migration).
  - Aggregate feedback per chunk (chunks with consistent negative feedback get lower retrieval weight).
  - Display feedback in evaluation dashboard.
  - Use negative feedback to identify weak golden dataset cases for improvement.
- **Acceptance:** A thumbs-down on an answer adjusts chunk relevance weight. Feedback stats appear in evaluation dashboard.

### 4.7 Cost tracking and budgets

- **Problem:** No OpenAI spend tracking. Users can run up costs without awareness.
- **Tasks:**
  - Track per-turn cost: embedding cost + LLM generation cost + query intelligence LLM cost.
  - Persist cost per turn in `chat_turns.estimated_cost` (migration).
  - Add daily/weekly spend dashboard.
  - Add per-user daily budget (hard limit returns 429).
  - Add alerting when spend crosses a threshold.
- **Acceptance:** Each chat turn shows estimated cost in the trace panel. Daily spend dashboard tracks total. Budget limit prevents overrun.

### 4.8 A/B testing framework for retrieval configs

- **Problem:** No way to compare retrieval configurations on live traffic. Ablation only runs on golden dataset.
- **Tasks:**
  - Add a config variant router (e.g., 50% baseline / 50% experimental).
  - Tag each turn with the config variant used.
  - Collect feedback + groundedness + latency per variant.
  - Add a comparison dashboard (variant A vs B: recall, groundedness, latency, satisfaction).
- **Acceptance:** Two retrieval configs can be compared on live queries. Dashboard shows statistically meaningful comparison.

### 4.9 Custom embedding model support

- **Problem:** Only OpenAI `text-embedding-3-small` is supported. Enterprise users may need local models (for data residency) or specialized domain models.
- **Tasks:**
  - Add a `HuggingFaceEmbeddingProvider` (sentence-transformers, locally hosted).
  - Add a `CohereEmbeddingProvider`.
  - Make embedding provider configurable via settings.
  - Add a migration path when switching models (re-embed all documents).
  - Add a "compare embeddings" evaluation view (same query, different models).
- **Acceptance:** Switching from OpenAI to a local HuggingFace model re-indexes all chunks. Retrieval quality is comparable in the eval dashboard.

### 4.10 Document preprocessing (OCR + table extraction)

- **Problem:** Scanned PDFs (image-only) produce no text. Tables in PDFs are lost as unstructured text.
- **Tasks:**
  - Add OCR for scanned PDFs using `pytesseract` or a cloud OCR API.
  - Detect scanned vs. text-based PDFs automatically.
  - Extract tables using `camelot` or `pdfplumber` table detection.
  - Store tables as structured metadata on chunks.
  - Add table-aware retrieval (summary + full table).
- **Acceptance:** A scanned PDF is processed and becomes searchable. Tables are stored as structured data and retrievable.

### 4.11 Graph RAG (knowledge graph extraction)

- **Problem:** Current RAG retrieves flat chunks. Multi-entity questions (e.g., "How do X and Y relate?") require traversing relationships across documents.
- **Tasks:**
  - Extract entities and relationships from documents during ingestion (LLM-based entity extraction).
  - Store in a graph database (Neo4j) or SQLite-graph hybrid.
  - Add graph-augmented retrieval: traverse entity relationships to find connected chunks.
  - Add a graph visualization in the X-Ray panel.
- **Acceptance:** A question about relationships between two entities retrieves chunks connected through the entity graph, not just keyword/semantic similarity.

### 4.12 Agentic RAG (tool-use and multi-step reasoning)

- **Problem:** Current multi-hop retrieval is sequential but not agentic. The system can't call external tools, APIs, or databases to answer questions.
- **Tasks:**
  - Add a tool registry (define available tools: web search, SQL query, calculator, API call).
  - Add function-calling to the generation service (let LLM call tools when context is insufficient).
  - Add a "tool-use" mode in AdvancedRetrievalConfig.
  - Display tool calls and results in the X-Ray trace panel.
- **Acceptance:** A question requiring current data triggers a web search tool call. The answer cites both document context and tool results.

### 4.13 Streaming backpressure handling

- **Problem:** Tokens are yielded directly to the client with no buffering. A slow client stalls the generator.
- **Tasks:**
  - Add a bounded queue between the LLM producer and the SSE consumer.
  - If the queue fills, apply backpressure (pause LLM streaming).
  - Add a client-disconnect detection timeout.
- **Acceptance:** A slow client does not stall the LLM producer indefinitely. Client disconnect is detected and streaming stops cleanly.

### 4.14 Audit trail for settings changes

- **Problem:** No audit log of who changed what settings. The `PUT /settings` endpoint silently rewrites runtime config.
- **Tasks:**
  - Add a `settings_changes` table (who, what, when, before, after).
  - Log every settings mutation.
  - Add a settings history view in the Settings UI.
  - Add a revert-to-previous action.
- **Acceptance:** Every `PUT /settings` call records the change. Settings history is viewable in the UI. Previous configs can be restored.

---

## Phase 5 — Test & CI Infrastructure

Target: Establish confidence before and after changes.

### 5.1 Add pytest-asyncio to requirements

- **Problem:** 6 async tests use `@pytest.mark.asyncio` but `pytest-asyncio` is not in `requirements.txt`. Fresh checkout fails these tests.
- **Tasks:**
  - Add `pytest-asyncio` to `requirements.txt`.
  - Add `pyproject.toml` or `pytest.ini` with `asyncio_mode = "auto"`.
  - Verify all async tests pass on fresh install.
- **Acceptance:** Fresh checkout + `pip install -r requirements.txt` + `pytest` passes (no skipped tests).

### 5.2 Add router integration tests

- **Problem:** CRUD routers (collections, documents, ingestion, duplicate-decisions, settings) have zero tests.
- **Tasks:**
  - Add integration tests using `TestClient` for each router.
  - Cover: list, create, update, delete, duplicate decision flow, settings update.
  - Add ingestion E2E test (upload → process → verify chunks in DB).
  - Add streaming SSE parsing test.
- **Acceptance:** All routers have at least 1 integration test. Coverage of routers ≥ 80%.

### 5.3 Add frontend tests

- **Problem:** Zero frontend tests despite vitest + testing-library installed.
- **Tasks:**
  - Add component tests for ChatPanel (citation rendering, session switching, SSE handling).
  - Add screen tests for Evaluation dashboard (metric display, ablation table).
  - Add screen tests for Document Library (upload, status tabs, reindex).
  - Add API mock tests for streaming SSE consumption.
- **Acceptance:** `npm test` runs and passes. Frontend has baseline component + screen coverage.

### 5.4 Add CI pipeline

- **Problem:** No CI config exists.
- **Tasks:**
  - Add GitHub Actions workflow (or equivalent).
  - Steps: lint, typecheck (if applicable), backend pytest, frontend vitest, build check.
  - Run on PR and on push to main.
  - Add coverage reporting.
  - Add linting (ruff/flake8 for Python, eslint for frontend).
- **Acceptance:** PRs are gated by CI. Failing tests block merge. Coverage is reported on PR.

### 5.5 Fix migration tests and hardcoded paths

- **Problem:** No forward/backward migration tests. `reset.py:5` has hardcoded absolute path that only works on one developer's machine.
- **Tasks:**
  - Fix hardcoded path in `reset.py` to use relative path or `__file__`.
  - Add tests: fresh DB applies all migrations, re-running is idempotent, version table is correct.
  - Add a test for `reset_database` from any working directory.
- **Acceptance:** `python backend/migrations/runner.py` works from any working directory. Migration tests pass.

### 5.6 Add Weaviate schema migration path

- **Problem:** Weaviate collection is created on every client construction with hardcoded property names. Changing the schema has no migration path — must `clear_all()` and lose all vectors.
- **Tasks:**
  - Add a schema version check for Weaviate.
  - Add migration steps for schema changes (add property, rename, re-embed if property type changes).
  - Document the Weaviate schema as code (version-controlled).
- **Acceptance:** Changing a Weaviate property runs a migration without losing existing vectors (except when data type changes require re-embedding).

---

## Phase 6 — Duplicate Detection & Deduplication Improvements

### 6.1 Add DB uniqueness constraints

- **Problem:** No unique constraint on `file_hash` or `normalized_text_hash` — duplicates can coexist at DB level.
- **Tasks:** Add unique index on `documents.file_hash` and `documents.normalized_text_hash` (nullable, enforced when non-null).
- **Acceptance:** Two documents with the same `file_hash` cannot coexist at DB level.

### 6.2 Fix race condition in duplicate detection

- **Problem:** Between dedupe check and insert, two concurrent ingests of the same content both pass and both persist.
- **Tasks:** Add a behavioral lock or DB-level check at insert time. Two concurrent ingests of the same content cannot both pass dedupe.
- **Acceptance:** Concurrent ingest of the same file does not produce two documents.

### 6.3 Add near-duplicate detection at scale (LSH/MinHash)

- **Problem:** Pairwise Jaccard scan is O(N²) — unworkable past a few thousand docs.
- **Tasks:**
  - Implement MinHash signatures for all documents.
  - Build an LSH index for fast near-duplicate lookup.
  - Query LSH instead of full scan during dedupe.
- **Acceptance:** Near-duplicate detection on 10K documents completes in <1s.

---

## Phase 7 — UX & Polish

### 7.1 Frontend routing cleanup

- **Problem:** `screens/Chat.jsx` exists but is dead — `App.jsx` renders `WorkspaceLayout` instead. Inconsistent routing.
- **Tasks:**
  - Either wire `Chat.jsx` into routing or delete it.
  - Verify all routes in `App.jsx` resolve to live components.
- **Acceptance:** No dead screen files. All routes work.

### 7.2 Markdown rendering improvements

- **Problem:** ChatPanel uses a hand-rolled minimal Markdown parser — no table, list, or code-fence support beyond what's literally rendered.
- **Tasks:**
  - Replace hand-rolled parser with `react-markdown` or `marked`.
  - Add syntax-highlighted code blocks (`react-syntax-highlighter`).
  - Add table rendering with citations support inside table cells.
  - Add copy-to-clipboard for code blocks.
- **Acceptance:** Markdown with tables, code blocks, inline citations renders correctly in the chat panel.

### 7.3 Per-collection routing rules UI

- **Problem:** No per-collection routing UI toggle. Collection routing is a global retrieval setting only.
- **Tasks:**
  - Add a `routing_keywords` field to collections (optional keywords to bias routing).
  - Add a UI control in Collection settings to configure routing hints.
  - Use the keywords in collection routing to improve confidence.
- **Acceptance:** A collection with routing keywords "finance, revenue" routes financial queries with higher confidence than the global setting.

### 7.4 Dead settings screen routes cleanup

- **Problem:** Integrations, Billing, Team categories render placeholder cards that tell users to "contact org admins" — no backend support.
- **Tasks:**
  - Remove placeholder categories OR implement them (see Phase 3.6).
  - Clean up styling bug in DuplicateWarning classNames (stale string compares `overwrite`/`create_new`/`ignore` that never match).

- **Acceptance:** Settings screen shows only categories with real functionality. Duplicate decision buttons render correct styling.

---

## Prioritization Matrix

| Phase | Effort | Impact | Risk if skipped |
|-------|--------|--------|-----------------|
| 0 — Critical Security | Medium | Critical | Secret leak, full system takeover, OOM, SSRF |
| 1 — Correctness | Medium | High | Wrong results, silent data loss, broken citations |
| 2 — Robustness | High | High | Crash loses jobs, context overflow, poor scaling, thread-safety |
| 3 — Feature Completeness | Medium-High | Medium | Features exist but don't fully work as intended |
| 4 — New Features | High | Medium-High | Competitive gap, missing essential RAG capabilities |
| 5 — Tests & CI | Medium | High (long-term) | Regression risk, no confidence in changes |
| 6 — Dedup Improvements | Low-Medium | Medium | Duplicate documents, scalability ceiling |
| 7 — UX & Polish | Low-Medium | Low-Medium | User-visible rough edges, dead code confusion |

---

## Feature Maturity After Roadmap

| Feature | Current | Target |
|---------|---------|--------|
| Document Ingestion | Partial | Production-ready (durable queue, validation, bulk upload, OCR) |
| Chunking | Partial | Production-ready (overlap fixed, page-aware working, semantic wired) |
| Embeddings | Partial | Production-ready (content-keyed cache, batch calls, multi-provider) |
| Hybrid Retrieval | Production-ready | Production-ready (connection pool, batch hydration, result cache) |
| Query Intelligence | Partial | Production-ready (caching, null guards, reference resolution) |
| Reranking | Partial (dummy default) | Production-ready (FlashRank default, error handling, order fix) |
| Multi-Hop | Partial | Production-ready (chunk-ID fix, intra-call timeout, fallback) |
| Safety | Partial | Production-ready (safety_mode wired, fail-closed option, thread-safe, escaped prompts) |
| Citations | Partial | Production-ready (better matching, no risky implicit injection) |
| Grounding | Partial | Production-ready (threshold fix, traceability wired) |
| Streaming | Partial | Production-ready (async streaming, multi-worker cancellation, backpressure) |
| Evaluation | Partial | Production-ready (RAGAS, real metrics, A/B testing, cost tracking) |
| Collections | Production-ready | Production-ready (per-collection routing rules) |
| Document Library | Production-ready | Production-ready (access control, bulk upload, PII badges) |
| Duplicate Detection | Not-ready | Production-ready (indexed lookups, race fix, LSH at scale) |
| Conversation Memory | Partial | Production-ready (compression, reference resolution, ownership, export) |
| Security | Not-ready | Production-ready (auth, rate limiting, secret hygiene, SSRF) |
| Deployment | Not-ready | Production-ready (containerized, CI, health probes) |
| Observability | Partial | Production-ready (structured logs, metrics, request correlation) |
| New: PII Detection | Not implemented | Production-ready (scanner, redaction, badges) |
| New: Cost Tracking | Not implemented | Production-ready (per-turn cost, budgets, alerts) |
| New: Graph RAG | Not implemented | Partial (entity extraction, graph-augmented retrieval) |
| New: Agentic RAG | Not implemented | Partial (tool registry, function calling, trace display) |
| New: A/B Testing | Not implemented | Production-ready (variant routing, comparison dashboard) |
| New: Relevance Feedback | Not implemented | Production-ready (thumbs up/down, chunk weighting) |
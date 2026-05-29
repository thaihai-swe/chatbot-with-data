# Enhancement Roadmap

**Status:** 🟡 Partial — describes implemented features and planned upgrades  
**Last verified:** 2026-05-29  
**Source files:** `backend/`, `frontend/src/`

---

## Overview

This document lists features that are **shipped**, **partially shipped**, and **planned** for the RAG Knowledge Base Lab. It serves as a roadmap for future development and a reference for what's already built.

For a complete feature specification, see [`rag-prd-requirement.md`](../rag-prd-requirement.md).

---

## Implemented Features ✅

These are shipped and working in the current codebase.

### Core RAG Pipeline
- ✅ **Document ingestion** (PDF, TXT, MD, URLs)
- ✅ **Duplicate detection** (file hash, text hash, similarity-based)
- ✅ **Five chunking strategies** (fixed-size, heading-aware, page-aware, semantic, parent-child)
- ✅ **Embedding generation & caching** (OpenAI text-embedding-3-small)
- ✅ **Hybrid search** (BM25 + semantic via Weaviate)
- ✅ **Query intelligence** (classification, expansion, decomposition, HyDE, synonym expansion, dynamic routing)
- ✅ **RRF merging** (Reciprocal Rank Fusion for multi-strategy results)
- ✅ **Grounded generation** (LLM answers only from retrieved context)
- ✅ **Citations** (link claims to source chunks)
- ✅ **Streaming responses** (token-by-token via SSE)
- ✅ **Multi-turn conversation** (session history with sliding window)
- ✅ **Prompt injection detection** (three-layer: heuristic, fuzzy, LLM)
- ✅ **Collection management** (organize documents by domain/project)
- ✅ **Evaluation harness** (sanity check on golden dataset)

### Infrastructure
- ✅ **FastAPI backend** with async support
- ✅ **SQLite metadata store** (16 tables, auto-migrations)
- ✅ **Weaviate vector DB** (Docker Compose)
- ✅ **React frontend** with Vite
- ✅ **Provider abstraction** (LLM, embedding, vector store)
- ✅ **Configuration management** (.env + runtime settings)
- ✅ **Error handling** (global exception handlers)
- ✅ **Request ID tracking** (X-Request-ID header)

### Observability
- ✅ **Query tracing** (capture pipeline stages and intermediate results)
- ✅ **Debug views** (X-Ray panel showing retrieved chunks, reranking, prompts)
- ✅ **Performance metrics** (latency per stage in `context_used_json`)
- ✅ **Audit logging** (lifecycle events, ingestion attempts)

---

## Partially Implemented Features 🟡

These have foundational code but are incomplete or placeholder implementations.

### Reranking
- 🟡 **Dummy reranker** — Currently sorts by similarity score only
- ⏳ **Real cross-encoder** — Pending: wire `BAAI/bge-reranker-base` or Cohere Rerank

### Evaluation Metrics
- 🟡 **Sanity check** — Runs on golden dataset; returns pass/fail
- ⏳ **RAGAS metrics** — Pending: implement faithfulness, answer relevance, context precision/recall

### Ingestion
- 🟡 **Async via BackgroundTasks** — In-process, not durable
- ⏳ **Job queue** — Pending: Celery/RQ for durable async

### Conversation Memory
- 🟡 **Sliding window** — Keeps last 10 turns
- ⏳ **Context compression** — Pending: summarize older turns
- ⏳ **Coreference resolution** — Pending: resolve pronouns to prior entities

### Index Lifecycle
- 🟡 **Schema foundation** — `index_generations` and `index_entries` tables exist
- ⏳ **Re-embedding** — Pending: job to re-embed with new model
- ⏳ **Blue/green swaps** — Pending: atomic index switching
- ⏳ **Snapshots/restore** — Pending: backup and recovery

---

## Planned Features ⏳

These are designed but not yet implemented.

### High Priority (Next Sprint)

| Feature | Why | Effort | Blocker |
|---------|-----|--------|---------|
| **Real reranker** | Dummy reranker is a credibility gap; real cross-encoder improves precision 20–30% | 1 day | None |
| **RAGAS metrics** | Evaluation is the bottleneck; need faithfulness, answer relevance, context precision/recall | 2 days | None |
| **PII detection** | Compliance requirement; block/redact sensitive data during ingestion | 3 days | None |
| **Async job queue** | Current BackgroundTasks lost on restart; need durable queue | 2 days | None |
| **Multi-format ingestion** | DOCX, PPTX, XLSX, HTML, OCR for scanned PDFs | 3 days | None |

### Medium Priority

| Feature | Why | Effort | Blocker |
|---------|-----|--------|---------|
| **Context compression** | Long conversations hit context window; need to summarize older turns | 2 days | None |
| **Coreference resolution** | "Tell me more" should resolve to prior turn; currently doesn't | 2 days | None |
| **Rate limiting** | Prevent abuse; cap queries/min, token budgets, embedding API spend | 2 days | None |
| **Cost tracking** | Per-query cost attribution; budget alerts | 1 day | None |
| **OpenTelemetry tracing** | Structured tracing with W3C context propagation | 2 days | None |
| **Structured JSON logs** | Correlation IDs, per-stage latency, audit trail | 1 day | None |
| **Re-embedding job** | Support embedding model upgrades | 2 days | Index lifecycle foundation |
| **Blue/green index swap** | Zero-downtime index updates | 1 day | Index lifecycle foundation |

### Lower Priority (Nice-to-Have)

| Feature | Why | Effort |
|---------|-----|--------|
| **SSRF protection** | Prevent URL ingestion from hitting internal IPs | 1 day |
| **Output moderation** | Scan LLM responses for harmful content | 1 day |
| **Secrets scanning** | Detect and redact secrets in ingested docs | 1 day |
| **Conversation export** | Export chat history as JSON/markdown/PDF | 1 day |
| **Conversation search** | Full-text search across past conversations | 1 day |
| **Advanced prompt injection** | Semantic analysis beyond pattern matching | 2 days |
| **Kubernetes manifests** | Deploy to K8s | 2 days |
| **CI/CD pipeline** | GitHub Actions or similar | 1 day |
| **Dockerfile** | Containerize backend | 1 day |
| **Helm chart** | Package for Kubernetes | 1 day |

---

## Deferred (Out of Scope for v1)

These are production-critical but deferred to v2+:

- **Multi-tenancy** — Tenant isolation, per-tenant quotas, cross-tenant leak prevention
- **Authentication & Authorization** — User/service account management, RBAC, session management
- **GDPR/CCPA compliance** — Right-to-delete, data residency, consent tracking, DSAR support
- **Disaster recovery** — RPO/RTO targets, cross-region replication, backup verification
- **SLA/SLO framework** — Availability targets, error budgets, incident runbooks
- **Fine-tuning** — Custom embedding or reranker models
- **Autonomous agents** — Multi-step planning and execution
- **Multi-tenant SaaS** — Billing, usage metering, subscription management

---

## Implementation Priorities

### Sprint 1 (Weeks 1–2)
1. Real reranker (1 day) — highest credibility impact
2. RAGAS metrics (2 days) — enables ablation studies
3. PII detection (3 days) — compliance requirement

### Sprint 2 (Weeks 3–4)
1. Async job queue (2 days) — reliability
2. Multi-format ingestion (3 days) — completeness
3. Rate limiting (2 days) — production safety

### Sprint 3+ (Ongoing)
1. Context compression + coreference (4 days)
2. OpenTelemetry + structured logs (3 days)
3. Index lifecycle ops (3 days)
4. Cost tracking (1 day)

---

## Effort Estimates

| Category | Effort | Notes |
|----------|--------|-------|
| **Quick wins** (< 1 day) | Real reranker, cost tracking, secrets scanning | High ROI, low risk |
| **Medium** (1–2 days) | RAGAS, rate limiting, structured logs, SSRF | Moderate complexity |
| **Large** (2–3 days) | PII detection, async queue, multi-format, context compression | Requires design + testing |
| **XL** (3+ days) | Kubernetes, CI/CD, multi-tenancy, disaster recovery | Infrastructure-heavy |

---

## Success Metrics

After implementing the high-priority features, we should see:

- **Reranker:** Context precision improves from 0.61 → 0.81 (33% gain)
- **RAGAS metrics:** Can measure and compare strategies quantitatively
- **PII detection:** 95%+ recall on test dataset; zero false negatives on SSN/credit card
- **Async queue:** Ingestion survives backend restart; no lost jobs
- **Multi-format:** Can ingest DOCX, PPTX, XLSX, HTML, scanned PDFs
- **Rate limiting:** API survives 100 QPS without degradation
- **Cost tracking:** Can attribute cost per query; budget alerts work

---

## Known Limitations

Current limitations that should be addressed:

1. **Reranker is dummy** — Sorts by similarity score; no real ranking
2. **Evaluation is basic** — Sanity check only; no RAGAS metrics
3. **Ingestion is not durable** — BackgroundTasks lost on restart
4. **Conversation memory is shallow** — No compression or coreference
5. **No PII detection** — Sensitive data can be indexed
6. **No rate limiting** — API vulnerable to abuse
7. **No cost tracking** — Can't see per-query spend
8. **No multi-format support** — Only PDF/TXT/MD/URLs
9. **No observability** — No OpenTelemetry, structured logs, or SLOs
10. **No deployment automation** — Manual setup required

---

## How to Contribute

To implement a feature from this roadmap:

1. **Pick a feature** from the "Planned" section
2. **Read the spec** in [`rag-prd-requirement.md`](../rag-prd-requirement.md)
3. **Design** — Sketch the implementation (file structure, APIs, DB changes)
4. **Implement** — Write code, tests, and docs
5. **Verify** — Run tests, manual testing, update this roadmap
6. **PR** — Submit with clear description of what was added

---

## Cross-References

- **Full PRD:** [`rag-prd-requirement.md`](../rag-prd-requirement.md)
- **System Architecture:** [`docs/system-architecture.md`](./system-architecture.md)
- **API Reference:** [`docs/api-flows.md`](./api-flows.md)
- **Database Schema:** [`docs/database-schema.md`](./database-schema.md)

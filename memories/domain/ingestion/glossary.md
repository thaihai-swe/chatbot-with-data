---
domain: ingestion
triggers: [ingestion, chunking, embedding, indexing, upload, extract, duplicate detection, document, weaviate, pdf, migration]
---

# Document Ingestion — Glossary

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Ubiquitous Language

| Term | Definition | Source |
|------|------------|--------|
| Chunking Strategies | 5 strategies for splitting documents: fixed-size, heading-aware (markdown), page-aware (PDF), semantic (topic-boundary), parent-child (hierarchical) | `backend/chunking/` |
| Duplicate Detection | Dedup by file hash, text hash, and content similarity checks | `backend/duplicate_detection/` |
| Weaviate | Vector database (1.27.0) with hybrid search (BM25 + vector) via gRPC :50051 | `backend/indexing/weaviate_store.py` |
| Embedding | OpenAI embedding model called through provider abstraction layer | `backend/embeddings/` |
| Ingestion Pipeline | Orchestrated flow: upload → extract → dedup → chunk → embed → index | `backend/ingestion/` |
| Migration Runner | SQLite schema migration system with 4 versions and 16 tables | `backend/migrations/runner.py` |

## Notes

- Chunking strategy is auto-selected by document type but can be overridden.
- Embedding results are cached to avoid redundant API calls.

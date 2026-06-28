# Glossary

## Domain Terms

| Term | Definition |
|------|------------|
| RAG | Retrieval-Augmented Generation — retrieve relevant document chunks, then generate answers grounded in those chunks |
| Hybrid Search | Combined BM25 keyword search + semantic vector search, fused via RRF (Reciprocal Rank Fusion) |
| Chunking | Splitting documents into searchable pieces; 5 strategies available (fixed-size, heading-aware, page-aware, semantic, parent-child) |
| Query Intelligence | Pre-retrieval pipeline: classify intent, expand/decompose query, generate HyDE, route to collections |
| Prompt Injection Defense | 3-layer protection: heuristic regex patterns + fuzzy similarity + LLM-based adversarial detection |
| Grounded Generation | Generate answers with evidence sufficiency scoring, groundedness checking, and inline citations |
| X-Ray Panel | Frontend debug panel exposing retrieval scores, chunk content, and generation internals |
| Collection Routing | LLM decides which document collections to search based on user intent |
| CandidateMerger | RRF-based combiner of multi-strategy retrieval results |


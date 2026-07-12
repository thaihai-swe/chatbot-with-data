---
domain: rag
triggers: [rag, chat, citations, ingestion, grounding, weaviate]
---

# Domain — Glossary

> Ownership: Collaborative — skill-updated + user-maintained.
> Updated by: `/context-memory` post-ship sync when new terms emerge from a completed feature.
> Read by: `/spec-requirements`, `/spec-plan`, `/spec-implement` to enforce consistent naming.

## Ubiquitous Language

| Term | Definition | Example Usage |
| |-|-|-|
| Citation | Reference back to a retrieved document chunk showing where LLM drew info | "Verify that each citation points to the correct chunk ID." |
| Grounding | Safety gate checking if LLM response is strictly backed by the retrieved text | "The grounding step blocked the response due to lack of evidence." |
| Ingestion | Parsing, understanding, chunking, and storing user-uploaded files | "PDF files are routed through the ingestion service before storage." |
| SSE | Server-Sent Events stream delivering token chunks to the client | "SSE connections stream both token characters and citation metadata." |
| Duplicate Detector | Check confirming if document hash or contents are already registered | "The duplicate detector flagged the file as AWAITING_USER_ACTION." |
| Reranker | FlashRank scorer selecting the top most relevant chunks from search results | "We feed the top Weaviate chunks into the reranker before grounding." |

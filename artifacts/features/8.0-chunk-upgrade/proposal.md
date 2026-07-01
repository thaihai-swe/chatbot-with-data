# Proposal: Chunk Upgrade — Notebook LM Adaptive Tiering

## The Problem
Our current chunking system always splits documents into fixed-size chunks regardless of document size. A 200-token document gets fragmented just like a 200K-token document. The heading-aware chunker drops heading context when splitting large sections. The semantic chunker uses Jaccard heuristics (not real embeddings). The parent-child chunker merges children by fixed count, not by content boundaries. This degrades retrieval quality and LLM response accuracy vs Notebook LM.

## Objectives
1. **Adaptive tiering**: Small documents injected whole (no unnecessary fragmentation); large documents use structure-aware segmentation
2. **Context preservation**: Every chunk carries its heading lineage so the LLM always knows what "this" refers to
3. **Configurability**: Context window threshold is user-configurable via Settings UI and settings.json (depends on the model)
4. **Full index coverage**: Even full-doc injection chunks are indexed in Weaviate for cross-document retrieval

## High-Level Approach
- Add an `AdaptiveChunker` decision layer before the existing dispatcher
- Tier 1 (full-doc): document below configurable threshold → single chunk, indexed to Weaviate
- Tier 2 (chunked): recursive heading extraction → heading path prepended to child chunks → embedding-based semantic boundary detection → boundary-aware parent-child
- All new config exposed in the existing Settings screen under "Ingestion & Chunking"
- Manual "Re-chunk" button per document for migrating existing documents

## Known Constraints / Risks
- Embedding-based semantic chunking adds ingestion latency (mitigation: Jaccard fallback)
- Existing documents retain old chunking strategy until user manually triggers re-chunk
- Full-doc injection for very small docs changes search behavior (mitigation: still indexed in Weaviate)

## Gray Areas To Resolve
- Locked: Full-doc chunks still go to Weaviate (for cross-document retrieval)
- Locked: New uploads use new strategy; existing docs get manual "Re-chunk" button
- Pending: What is the default adaptive tiering threshold? (Recommended: 30% of `llm.context_window_size`)

## Success Criteria
- [ ] A 500-token document uploads as a single chunk with Weaviate entry
- [ ] A document with `# A > ## B > ### C` produces chunks with `[A > B > C]` heading path in text
- [ ] A document with abrupt topic shift splits at the semantic boundary
- [ ] Context window threshold can be changed via Settings UI and takes effect on next upload
- [ ] Users can re-chunk an existing document from the document viewer

---

Status: Aligned

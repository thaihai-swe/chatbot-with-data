# Chunking Strategies

**Status:** 🟢 Implemented  
**Last verified:** 2026-06-30  
**Source files:** backend/chunking/

---

This document explains the various chunking strategies implemented in the system, how they work, and when to use them.

## Overview

Chunking is the process of splitting large documents into smaller, manageable pieces (chunks) before they are indexed in the vector database. High-quality chunking is critical for effective Retrieval-Augmented Generation (RAG) because it ensures that:
1. **Context is preserved**: Related information stays together.
2. **Retrieval is precise**: The system can find the exact snippet needed to answer a query.
3. **LLM limits are respected**: Chunks fit within the LLM's context window.

## Adaptive Tiering (Pre-Processing Layer)

Before any strategy is selected, the **AdaptiveChunker** decides whether to inject the full document as a single chunk (Tier 1) or proceed with structural chunking (Tier 2). This mirrors Notebook LM's approach:

- **Tier 1 (Full-Doc Injection)**: Documents smaller than the configurable threshold are stored as a single `adaptive_tier="full_doc"` chunk. This preserves the full context for small documents (FAQs, short notes) while still indexing them in Weaviate for cross-document search.
- **Tier 2 (Structural Chunking)**: Documents above the threshold are chunked using the standard strategy dispatch described below.

**Threshold**: `max(1000, context_window_size * ratio)` by default. An explicit `adaptive_tiering_threshold` overrides the ratio calculation.

**Configuration** (via Settings UI or `settings.json`):
| Parameter | Default | Description |
| :--- | :--- | :--- |
| `adaptive_tiering_enabled` | `true` | Master toggle |
| `adaptive_tiering_threshold` | `null` | Explicit threshold (overrides ratio when set) |
| `adaptive_tiering_ratio` | `0.3` | Fraction of `llm.context_window_size` |

Adaptive tiering is only active when `chunking_strategy` is not explicitly set (i.e., the auto-detect default). An explicit strategy override bypasses adaptive tiering entirely.

## Supported Strategies

The system supports six distinct chunking strategies, managed by the `ChunkingDispatcher`. All strategies listed below are Tier 2 strategies — they only run when the document exceeds the adaptive threshold.

### 1. Fixed-Size Chunking (`fixed_size`)
The foundational strategy that splits text into units of a specific token count with a configurable overlap.
- **Mechanism**: Splits text into sentences using regex, then aggregates them until the `chunk_size` limit is reached.
- **Overlap**: Retains a portion of the previous chunk at the start of the next one to maintain continuity at boundaries.
- **Best for**: Plain text files and documents with no clear structural markers.

### 2. Heading-Aware Chunking (`heading_aware`)
Tailored for structured documents like Markdown or web content.
- **Mechanism**: Identifies headings (`#`, `##`, etc.) using recursive extraction with a heading path stack. Each chunk's text starts with its full heading lineage (e.g., `[Introduction > Background > Historical Context]`).
- **Preservation**: Attempts to keep content under a single heading within one chunk. If a section is too large, it is split using fixed-size logic but retains the heading path in the chunk text.
- **Best for**: Documentation, technical manuals, and blog posts.
- **Upgrade**: Heading paths are now prepended to chunk text (not just metadata), so retrieved chunks always carry their section context.

### 3. Page-Aware Chunking (`page_aware`)
Designed specifically for PDF documents where page context is vital.
- **Mechanism**: Relies on page markers (e.g., `###PAGE_BREAK###`) inserted during the extraction phase.
- **Preservation**: Ensures that chunks do not cross page boundaries unless the content of a single page exceeds the `chunk_size`.
- **Best for**: Legal documents, academic papers, and any source where "page number" is a critical citation field.

### 4. Semantic Chunking (`semantic`)
An advanced strategy that uses content similarity to find natural topic boundaries.
- **Mechanism**: Calculates a "semantic continuity score" between adjacent sentences. When an embedding provider is available, uses real cosine similarity between sentence embeddings. Falls back to Jaccard similarity if the provider is unavailable or times out (>5s).
- **Fallback**: Automatically falls back to `fixed_size` if the semantic signal is too weak to provide meaningful boundaries.
- **Best for**: Narrative text or documents where headings are inconsistent but topics shift clearly.
- **Upgrade**: Now uses actual embedding cosine similarity instead of pure Jaccard heuristics, with transparent fallback to Jaccard when embeddings are unavailable.

### 5. Parent-Child Chunking (`parent_child`)
A hierarchical strategy for improved retrieval precision.
- **Mechanism**: Generates small "child" chunks (optimized for search) and links them to larger "parent" chunks (optimized for LLM context). Parent groups are now aligned to **heading/section boundaries** when detected, instead of using a fixed `children_per_parent` count.
- **Retrieval**: When a child chunk is found, the system can optionally retrieve and provide the full parent context to the LLM.
- **Best for**: Complex documents where precise facts are buried within broad context.
- **Upgrade**: Boundary-aware grouping ensures parents contain semantically coherent content from the same section, not arbitrary concatenations.

---

## Selection & Configuration

### Strategy Selection Logic
The system determines which strategy to use during the ingestion process in `backend/ingestion/service.py`:

1. **Explicit Strategy**: If a strategy is explicitly requested via the API or specific configuration, it is used.
2. **Global Default**: The `chunking_strategy` setting in `config/settings.json` is the primary source.
3. **Source-Aware Overrides**: If the global strategy is set to `fixed` (the default), the system applies intelligent overrides based on the file type:
   - **PDF** → `page_aware`
   - **Markdown/Web** → `heading_aware`
   - **Text** → `fixed_size`

### Configuration Parameters
These settings can be adjusted in the "Ingestion" section of the system settings:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `chunk_size` | 1000 | Target size for each chunk (approximate tokens). |
| `chunk_overlap` | 200 | Number of tokens to overlap between consecutive chunks. |
| `chunking_strategy` | `fixed` | The default strategy to apply. |
| `adaptive_tiering_enabled` | `true` | Enable adaptive tiering (full-doc injection for small docs). |
| `adaptive_tiering_threshold` | `null` | Explicit threshold (tokens); overrides ratio when set. |
| `adaptive_tiering_ratio` | `0.3` | Fraction of `llm.context_window_size` for auto threshold. |
| `semantic_similarity_threshold` | 0.8 | (Semantic only) Threshold for determining a topic shift. |
| `parent_child_enabled` | `false` | Whether to generate hierarchical relationships. |

---

## Implementation Details

- **Base Class**: `backend/chunking/base.py` (defines the `BaseChunker` interface; `ChunkData` with nullable `heading_path`, `content_type`, `adaptive_tier` fields).
- **AdaptiveChunker**: `backend/chunking/adaptive_chunker.py` (Tier 1 decision layer: `should_inject()`).
- **Dispatcher**: `backend/chunking/dispatcher.py` (routes logic to specific strategies).
- **Service**: `backend/chunking/service.py` (handles orchestration and database persistence).
- **Re-chunk**: `POST /documents/{id}/reindex` endpoint re-runs chunk-and-index with current config. Atomic (saves old chunks, restores on failure). Available via "Re-chunk" button on document detail view.

## Best Practices

- **Use Heading-Aware for Docs**: It significantly improves the LLM's understanding of "what section" the information came from.
- **Overlap is Essential**: For fixed-size chunking, an overlap of 15-20% helps prevent "lost context" where a sentence is split exactly in half.
- **Monitor Chunk Count**: If a small document results in hundreds of chunks, your `chunk_size` might be too small, leading to fragmented retrieval.
- **Semantic Chunking requires more compute**: While more accurate, the semantic strategy is slightly slower as it requires sentence-level similarity calculations.

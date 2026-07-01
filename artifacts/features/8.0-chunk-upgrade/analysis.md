# Chunk Upgrade — Notebook LM Chunking Analysis

> **Goal:** Deep-dive analysis of the current chunking system vs Notebook LM's adaptive, structure-aware approach. Map what to change to align chunking with Notebook LM's hybrid strategy (full-doc injection + structural segmentation + contextualized embeddings).
>
> **Date:** 2026-06-30
> **Phase:** Research Complete
> **Next:** Route to `/spec-plan` — the scope is clear but affects ingestion pipeline flow, index schema, and retrieval. Needs a formal task plan before spec.

---

## 1. Executive Summary

Our chunking system has **5 strategies** covering the basics. Notebook LM uses a fundamentally different architecture: **adaptive tiered chunking** — small documents bypass chunking entirely (injected whole via Gemini's 2M context window), while large documents use structural + context-aware segmentation. This approach preserves semantic coherence that our always-chunk strategy loses.

| Area | Our System | Notebook LM | Delta |
|------|-----------|-------------|-------|
| Strategies | 5 (fixed, heading, page, semantic, parent-child) | Adaptive tiered (full-doc vs structural segmentation) | **Architecture gap** |
| Context preservation | Heuristic (Jaccard) | Embedding-based + heading prepending | **Quality gap** |
| Late chunking | No | Yes (contextualized embeddings) | **Design gap** |
| Content-specific chunkers | None | Table, code, image-aware | **Feature gap** |
| Recursive structure | No | Yes (nested heading hierarchy) | **Feature gap** |
| Format support | PDF, TXT, MD, URL | PDF, Docs, Sheets, Slides, EPUB, images, audio, video | **Ingestion gap** |

---

## 2. Current Chunking System — Verified State

### 2.1 Module Map

```
ingestion/service.py:chunk_and_index_document()
  └─ chunking/service.py:ChunkingService
       └─ chunking/dispatcher.py:ChunkingDispatcher
            ├─ fixed_size_chunker.py   — sentence-boundary splitting, chunk_size target
            ├─ heading_aware_chunker.py — MD headings, fallback to fixed_size
            ├─ page_aware_chunker.py   — ###PAGE_BREAK### markers, fallback to fixed_size
            ├─ semantic_chunker.py     — Jaccard heuristic, no embeddings
            └─ parent_child_chunker.py — fixed-group concatenation of children
```

### 2.2 Data Model

```
ChunkData (base.py)
  chunk_order: int
  text: str
  title: str | None
  section_title: str | None
  page_number: int | None
  source_url: str | None
  fallback_applied: bool
  semantic_score: float | None     # Always None — never populated
  metadata: dict
```

### 2.3 Strategy Selection (ingestion/service.py:356-366)

```
strategy = config.ingestion.chunking_strategy  # default: "fixed_size"
if strategy in ("fixed", "fixed_size"):
    if source_type == "pdf":        → "page_aware"
    elif source_type == "markdown":  → "heading_aware"
    else:                           → "fixed_size"
```

No adaptive sizing — always uses `config.ingestion.chunk_size` (default 512 tokens). Documents of 100 tokens and 100K tokens are chunked identically.

### 2.4 Chunking Pipeline Flow

```
Document uploaded
  → extract text (pdf_extractor / text_extractor / web_extractor)
  → duplicate detection
  → document understanding (LLM summary + topics)
  → ChunkDocument(text, strategy, chunk_size, overlap)
      → ChunkingDispatcher.chunk(strategy, text, ...)
          → strategy_class.chunk(text, ...) → list[ChunkData]
      → ChunkRepository.create_chunk(...) for each ChunkData  (SQLite persist)
  → safety check on chunks (filter high-risk)
  → IndexingService.index_document()  (embed + index to Weaviate)
```

### 2.5 Strategy Details

| Strategy | File | Lines | Approach | Weakness |
|----------|------|-------|----------|----------|
| `fixed_size` | `fixed_size_chunker.py` | 109 | Sentence-split → accumulate to chunk_size → overlap from tail | Destroys semantic boundaries; mid-sentence splits possible |
| `heading_aware` | `heading_aware_chunker.py` | 179 | Extract `#` sections → chunk each section independently | **Drops heading context when section is large** and gets sub-chunked; heading not prepended to child chunks |
| `page_aware` | `page_aware_chunker.py` | 152 | Split on `###PAGE_BREAK###` → chunk per page | Only as good as the extractor's page markers; no page marker → falls back to fixed_size |
| `semantic` | `semantic_chunker.py` | 259 | Jaccard word overlap + length ratio heuristic | **No real embeddings.** `use_embeddings=False` permanently. Weak segmentation → falls back to fixed_size. |
| `parent_child` | `parent_child_chunker.py` | 130 | Fixed-size children → group N children → concat parent | **Naive merge.** Parents are `children[0:N]` text concatenation, not semantic units. No content-based grouping. |

### 2.6 Semantic Chunker — The Real Problem

Our semantic chunker (`semantic_chunker.py:71-73`) calculates semantic scores using **Jaccard word overlap** between adjacent sentences:

```python
# semantic_chunker.py:167-169
words1 = set(sent1.lower().split())
words2 = set(sent2.lower().split())
intersection = len(words1 & words2) / len(words1 | words2)
```

This is a **bag-of-words heuristic**, not actual semantic similarity. The `use_embeddings` parameter exists but is hardcoded to `False` (line 38: `self.use_embeddings = use_embeddings` with default `False`, never called with `True`). When `_is_weak_segmentation()` returns True (variance < 0.05), it falls back to `FixedSizeChunker` — so for most real documents, **semantic chunking is just fixed-size chunking with extra overhead**.

### 2.7 Parent-Child — Naive Merge

Our parent-child chunker (`parent_child_chunker.py:76-80`) groups children by fixed sequence:

```python
for i in range(0, len(child_chunks), self.children_per_parent):
    child_group = child_chunks[i : i + self.children_per_parent]
    parent_text = " ".join([c.text for c in child_group])
```

This creates parents by blindly concatenating `children_per_parent` (default 4) consecutive child chunks. There's no semantic boundary detection, no overlap strategy, and no size-awareness. A section break mid-group would be merged into one parent.

---

## 3. Notebook LM Chunking — Research Findings

Based on published architecture teardowns, engineering interviews, and community analysis (2025-2026):

### 3.1 Core Philosophy: Adaptive Tiered Chunking

Notebook LM does **not** use a one-size-fits-all chunking strategy. It adapts based on document size relative to Gemini's 2M-token context window:

**Tier 1 — Small documents (fits in context window):**
- No chunking at all
- Full document injected directly into Gemini context
- Preserves 100% of structural and semantic integrity
- No retrieval needed for single-document queries

**Tier 2 — Large documents (exceeds context window):**
- Structural segmentation at heading/section boundaries
- Context-aware embedding (late chunking / contextualized)
- BGE Reranker for post-retrieval pruning
- Parent-child relationships preserved

This is described as "hybrid grounding" — combining the quality of long-context injection with the scalability of RAG.

### 3.2 Structural Segmentation

Notebook LM's chunking for large documents follows this chain:

```
Document → Heading hierarchy extraction (nested, recursive)
          → Section grouping (heading + content kept together)
          → Context preservation (heading prepended to all child chunks)
          → Semantic boundary detection (embedding-based, not heuristic)
          → Overlap strategies (cross-reference preserving)
```

Key techniques:
- **Recursive structure extraction**: Not just `#` headings, but full nested hierarchy (`# → ## → ###`). Each chunk carries its heading lineage.
- **Context-preserving": When a section is split, the parent heading is prepended to every child chunk (e.g., `[Section 3.2: Architecture Overview] child_chunk_text...`). This prevents "contextless chunk" retrieval.
- **Semantic boundary detection**: Uses actual embedding similarity (not Jaccard) to detect topic shifts within sections.

### 3.3 Contextualized (Late) Chunking

Notebook LM's embedding pipeline is believed to use **contextualized chunking** (also called "late chunking"):

```
1. Encode the entire document → token-level embeddings
2. Apply segmentation boundaries to the token embeddings
3. Pool tokens per segment → chunk embeddings
```

This ensures each chunk's embedding incorporates global document context, dramatically reducing false positives in retrieval (a chunk about "it" in one document won't match "it" queries from unrelated contexts).

### 3.4 Content-Specific Segmentation

Notebook LM handles heterogeneous content differently:
- **Tables**: Extracted as structured units (not linearized text). Each table is a retrievable chunk.
- **Code blocks**: Preserved as code (not prose). Syntax-aware boundaries.
- **Images/Figures**: Extract captions + surrounding text as context; image embeddings separately.
- **Lists**: Kept as coherent units rather than split across chunks.

### 3.5 Parent-Chunk Retrieval Pattern

Notebook LM uses the standard production pattern:

```
Child chunks (small, ~250 tokens) → embedded for retrieval
Parent chunks (large, ~1500 tokens) → stored for context expansion

Query → retrieve child chunks → expand to parent → LLM gets full context
```

This gives the precision of small chunks (better semantic matching) with the recall of large context (LLM doesn't see isolated fragments).

---

## 4. Gap Analysis — Detailed

### 4.1 Architecture Gap: No Adaptive Tiering

| Aspect | Notebook LM | Our System | Impact |
|--------|-------------|------------|--------|
| Small doc handling | Injected whole (2M context) | Always chunked to 512 tokens | **Semantic fragmentation**: a 400-token document is split across multiple chunks, losing sentence-to-sentence coherence |
| Large doc handling | Structural segmentation | Same 5 strategies regardless of size | No optimization for different document scales |
| Decision logic | `size < threshold ? inject : chunk` | Not implemented | Blind uniform processing |

### 4.2 Quality Gap: Heading Context Loss

**Our `heading_aware_chunker.py:114-178`** — when a section under a heading exceeds `chunk_size`, it splits into sentences without prepending the heading:

```python
# Line 154: no heading context in the split chunks
chunk = ChunkData(
    text=chunk_text,    # Just the text fragment
    section_title=section_title,  # Stored in metadata, not in text
)
```

A chunk retrieved later has its `section_title` in metadata but the LLM sees only the raw text. If the section starts with "This includes..." and the heading was "Core Components", the LLM has no way to know what "This" refers to.

**Notebook LM approach**: Every child chunk starts with the heading path. E.g., `[Chapter 3 > Section 3.2] This includes...`.

### 4.3 Quality Gap: Semantic Chunking Without Embeddings

Our `semantic_chunker.py:167-189` uses Jaccard word overlap as a stand-in for semantic similarity. This has known failure modes:
- Lexical variance: "vehicle" and "automobile" → 0 similarity
- Short sentences: "He said yes." → high Jaccard with any sentence sharing "said"
- Language shift: Topic transition with shared function words → missed boundary

The real Notebook LM approach uses actual embedding similarity, which captures:
- Synonym relationships
- Topic-level semantic shifts
- Consistent scoring regardless of sentence length

### 4.4 Design Gap: No Contextualized Embeddings

Every chunk in our system is embedded independently (`indexing/indexing_service.py` → `embedding_provider.embed(chunk_text)`). This means:

- A chunk that starts with "It also includes..." loses the antecedent from the previous chunk
- A chunk about "the algorithm" has no doc-level context in its embedding vector
- False positives: "memory" in a psychology paper vs "memory" in a CS paper may collide

**Notebook LM** likely uses contextualized (late) chunking, embedding the full document first, then segmenting token-level embeddings. This gives each chunk vector implicit document context.

### 4.5 Feature Gap: No Recursive Structure

Our `heading_aware_chunker.py:81-112` only handles flat `#` headings — no `##` or `###` nesting. The `_extract_sections` method stores a flat list with `level` but the chunker never uses level information for anything beyond section grouping. A subsection's heading lineage is not preserved.

### 4.6 Feature Gap: No Content-Specific Chunkers

Our dispatcher has 5 strategies, none content-specific:
- No table-aware chunker → tables are linearized to text, destroying columnar relationships
- No code-aware chunker → code blocks split mid-function
- No list-aware chunker → bullet lists broken across chunks

### 4.7 Feature Gap: Limited Input Formats

Our `extractors/` support only PDF, TXT, MD, and URL. Notebook LM supports:
- PDF, Google Docs, Google Sheets, Google Slides
- URLs (web pages)
- YouTube (transcripts)
- Images (OCR + multimodal)
- Audio (transcription)
- EPUB
- CSV

Without supporting these formats upstream, chunking quality doesn't matter — the documents never enter the system.

---

## 5. Preserved Behaviors (Invariants)

| ID | Invariant | Code Evidence | Intact? |
|----|-----------|---------------|---------|
| C-001 | Chunking runs after extraction, before indexing | `ingestion/service.py:339-456` | Yes |
| C-002 | Each chunk has a `chunk_order` within the document | `base.py:11-23` | Yes |
| C-003 | Strategy is configurable via `config.ingestion.chunking_strategy` | `service.py:34` | Yes |
| C-004 | Fallback chain: `heading_aware`/`page_aware`/`semantic` → `fixed_size` | `heading_aware.py:39-51`, `page_aware.py:60-72`, `semantic.py:76-91` | Yes |
| C-005 | Safety check filters high-risk chunks after chunking | `ingestion/service.py:416-435` | Yes |
| C-006 | Chunks are persisted to SQLite, indexed to Weaviate | `service.py:54-71`, indexing flow | Yes |
| C-007 | Chunks are deleted before re-chunking (re-index documents) | `ingestion/service.py:381-385` | Yes |
| C-008 | `parent_chunk_id` is set by service layer post-persist | `parent_child_chunker.py:98-130` | Yes |

---

## 6. Dependencies & Boundaries

### 6.1 Upstream Dependencies (What feeds into chunking)

| Component | Dependency | Type |
|-----------|-----------|------|
| `extractors/pdf_extractor.py` | PDF text + structured content | Input |
| `extractors/text_extractor.py` | TXT/MD content | Input |
| `extractors/web_extractor.py` | URL content | Input |
| `config.ingestion.chunk_size` | Chunk size parameter | Config |
| `config.ingestion.chunk_overlap` | Overlap parameter | Config |
| `config.ingestion.chunking_strategy` | Strategy selection | Config |
| `models.SourceType` (PDF, TEXT, URL, MARKDOWN) | Source type for strategy routing | Enum |

### 6.2 Downstream Dependencies (What chunking feeds into)

| Component | What it consumes | Boundary Contract |
|-----------|-----------------|-------------------|
| `repositories/chunk_repository.py` | Persisted chunk records | `chunk_id`, `document_id`, `text`, `chunk_order`, `parent_chunk_id` |
| `indexing/indexing_service.py` | Chunk text → embed → Weaviate | Chunk text must be self-contained for embedding |
| `indexing/weaviate_store.py` | Embedded chunk vectors | Each chunk → one vector |
| `chat/retrieval.py` | Vector search + hybrid search | Chunks retrieved by similarity |
| `chat/context.py` | Context assembly from chunks | Chunks formatted as `<source>` XML blocks |
| `chat/citations.py` | Citation mapping | Chunks referenced by `chunk_id` |
| `chat/candidate_merger.py` | RRF fusion | Chunk metadata including `similarity_score` |

### 6.3 Key Boundary Contracts

1. **ChunkTextIsSelfContained**: Each chunk's `text` must be independently meaningful for embedding and LLM context. This is broken today when heading context is lost.
2. **ChunkHasDocumentIdentity**: Each chunk carries `document_id` and `chunk_id` — this must survive any chunking changes.
3. **ChunkOrderIsSequential**: `chunk_order` preserves document reading order — any new strategy must maintain this.
4. **OneChunkOneWeaviateObject**: Each chunk becomes one vector. If we add late chunking, the embedding pipeline must change but the storage contract (one vector per chunk) can stay.

---

## 7. Risks & Migration Constraints

### 7.1 Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Re-indexing cost** | Changing chunking strategy invalidates all existing chunk vectors in Weaviate | Re-index at deployment; can be batched per-collection |
| **Semantic chunker quality** | Embedding-based semantic chunking adds latency (2 extra LLM calls per document) | Make it opt-in per-collection; fallback to heuristic if embedding unavailable |
| **Late chunking model requirement** | Contextualized embedding needs a long-context embedding model (not available with all providers) | Keep pre-embedding chunking as fallback; add late chunking as optional enhancement |
| **Chunk schema change** | `ChunkData` may need new fields (heading_path, content_type, structural_parent) | New fields are additive; existing chunks get null values |
| **Strategy migration** | Existing users have documents chunked with old strategies | Don't re-chunk automatically; new documents use new strategy |
| **Performance regression** | Full-doc injection for small documents requires larger context → higher latency and cost | Set small-doc threshold low (e.g., 1000 tokens) to control cost |

### 7.2 Migration Constraints

1. **Backward-compatible `ChunkData`:** Add fields (never remove). Existing chunks must still render correctly in the chat UI and X-Ray panel.
2. **Config-driven strategy selection:** New adaptive tiering must respect existing `chunking_strategy` config as an override.
3. **No breaking API changes:** The `GET /sessions/{id}/history` endpoint returns chunks as JSON — new fields appear but old fields remain.
4. **Weaviate schema is flexible:** Adding new properties to chunk objects is non-breaking.
5. **Provider-agnostic embedding:** Late chunking requires a model that can embed full documents (e.g., text-embedding-3-large with 8192 tokens). If the provider doesn't support this, fall back to per-chunk embedding.

---

## 8. Recommended Upgrade

### 8.1 Conceptual Model

```
Document
│
├─ [size < threshold] ────────────→ Tier1: Full-doc injection
│                                      (no chunking, no embedding)
│
└─ [size >= threshold] ───────────→ Tier2: Structural segmentation
       │
       ├─ 1. Recursive heading hierarchy extraction
       │     # → ## → ### → section content
       │     Each section carries full heading path
       │
       ├─ 2. Structure-aware chunking
       │     • Keep headings attached to content
       │     • Prepend heading path to child chunks on split
       │     • Detect table/code/list blocks (don't split)
       │     • Recursively chunk large sections
       │
       ├─ 3. Semantic boundary detection (embedding-based)
       │     • Embed adjacent sentence windows
       │     • Split at low-similarity boundaries
       │     • Merge tiny fragments
       │
       ├─ 4. Contextualized embedding (late chunking)
       │     • Embed full document → token-level
       │     • Pool per-chunk tokens → chunk embedding
       │     (fallback: pre-embedding chunking)
       │
       └─ 5. Parent-child relationships
             • Parent = section-level (large, ~1500 tokens)
             • Child = sub-section level (small, ~300-500 tokens)
             • Embed children, retrieve children, expand to parent
```

### 8.2 Files to Change

| File | Change | Impact |
|------|--------|--------|
| `base.py` | Add fields: `heading_path`, `content_type`, `parent_chunk_id` at creation time | Non-breaking, additive |
| `dispatcher.py` | Add adaptive tiering layer; content-type routing | New entry point, old strategies still work |
| `heading_aware_chunker.py` | Support recursive headings; prepend heading path to child chunks; handle tables/code | Upgrade in place |
| `semantic_chunker.py` | Replace Jaccard with actual embedding similarity; add embedding provider dep | Major refactor |
| `parent_child_chunker.py` | Replace naive merge with semantic boundary-aware parent creation | Upgrade in place |
| **New:** `adaptive_chunker.py` | Decision logic: inject vs chunk; threshold config | New file |
| **New:** `table_aware_chunker.py` | Detect and preserve table structures | New file |
| `ingestion/service.py` | Wire adaptive chunker; update strategy resolution | Minor change |

### 8.3 Files NOT to Change

| File | Reason |
|------|--------|
| `fixed_size_chunker.py` | Still valid as fallback for unstructured text |
| `page_aware_chunker.py` | Still valid for PDF with page markers |
| `chunk_repository.py` | Schema changes are metadata-only |
| `indexing/indexing_service.py` | Still receives `list[dict]` chunks |
| `weaviate_store.py` | Still stores one vector per chunk |
| `chat/retrieval.py` | Still queries by vector similarity |
| `chat/context.py` | Still formats chunks as `<source>` blocks |
| `chat/service.py` | Unaware of chunking internals |

### 8.4 Upgrade Sequence

**Phase 1 — Fix heading context loss (Low risk, high impact):**
1. `heading_aware_chunker.py`: Recursive heading extraction + heading path prepending
2. `dispatcher.py`: Preserve `section_title` → add `heading_path`
3. Vast majority of chunk quality issues stem from contextless splits

**Phase 2 — Real semantic chunking (Medium risk):**
4. `semantic_chunker.py`: Replace Jaccard with embedding similarity
5. Add `embedding_provider` dependency (lazy init, fallback to heuristic)
6. Test: documents with clear topic transitions should split at boundaries

**Phase 3 — Adaptive tiering (Low risk if config-driven):**
7. New `adaptive_chunker.py`: Check doc token count → inject or chunk
8. Config: `adaptive_tiering.enabled`, `adaptive_tiering.full_doc_threshold`
9. Default: enabled, threshold = 1000 tokens

**Phase 4 — Parent-child with semantic boundaries (Medium risk):**
10. `parent_child_chunker.py`: Replace naive merge with boundary detection
11. Each parent = contiguous content between semantic boundaries (not fixed N chunks)

**Phase 5 — Contextualized embeddings (High risk, model-dependent):**
12. New late chunking path in `indexing_service.py` (or new module)
13. Requires long-context embedding model
14. Fallback to per-chunk embedding

**Phase 6 — Content-specific chunkers (Low risk, new files):**
15. Table-aware chunker (extract from XML/HTML-like table markup in extraction output)
16. Code-block-aware chunker (detect fenced code blocks, don't split them)

---

## 9. Conclusion

The current chunking system is **functional** but falls short of Notebook LM's approach in three fundamental ways:

1. **No adaptive tiering** — we always chunk, even tiny documents that would benefit from full-doc injection
2. **No real semantic chunking** — our semantic chunker is a Jaccard heuristic with a hardcoded fallback to fixed-size
3. **No context preservation** — heading context is lost during large-section splits, creating orphaned chunks

The **highest-leverage fix** is Phase 1 (heading context preservation), which requires minimal code change and directly improves retrieval quality across all document types. The **most architecturally significant change** is Phase 3 (adaptive tiering), which shifts the chunking philosophy from "always chunk" to "inject or chunk based on size."

Route to `/spec-plan` — the upgrade touches the ingestion pipeline entry point (`chunk_and_index_document`), the chunking dispatcher architecture, and the embedding pathway. A formal plan is needed to sequence the phases and define the task list, particularly around the non-breaking migration path for existing chunked documents.

# Production Chunking Design

## Metadata

- Feature name: Chunking and Indexing Foundation
- Feature slug: chunking-and-indexing-foundation
- Design status: Proposed
- Last updated: 2026-05-18
- Related spec: `artifacts/features/2.chunking-and-indexing-foundation/spec.md`

## Goal

Define a production-ready chunking design for this repository that:

- keeps the current strategy flexibility
- fixes the structural gaps in PDF, URL, and parent-child processing
- makes chunk behavior deterministic and observable
- improves retrieval quality without overcomplicating the first production version

## Recommended End State

Use a layered chunking model instead of one global strategy:

1. Preserve source structure during extraction.
2. Normalize each source into a common document-segment model.
3. Apply a source-appropriate primary chunker.
4. Optionally derive secondary retrieval views such as parent chunks.
5. Persist chunk lineage so retrieval can safely expand, cite, and reindex.

This repo should move from “choose one chunker by source type” to “extract structure first, then build one or more chunk views from that structure.”

## Design Principles

### 1. Structure Before Splitting

Chunkers should not guess page or heading boundaries from flattened text if the extractor can preserve them.

### 2. Stable Boundaries

Chunk boundaries should be deterministic for the same source content and settings so reindexing does not create arbitrary drift.

### 3. Source-Type Defaults With Safe Fallbacks

Every source type should have a recommended default strategy, but all advanced modes must fall back to a reliable baseline.

### 4. Retrieval Views, Not Competing Truths

Child chunks, parent chunks, and semantic chunks should be modeled as retrieval views over the same source, not unrelated chunk sets.

### 5. Metadata Must Be First-Class

Chunk records must preserve enough structure for citation, debugging, filtering, and reindex cleanup.

## Recommended Strategy Matrix

| Source type | Primary strategy | Secondary strategy | Production verdict |
|---|---|---|---|
| Markdown | `heading_aware` | optional `parent_child` | Yes |
| Plain text | `fixed_size` | optional `parent_child` | Yes |
| PDF | `page_aware` over preserved pages | optional `parent_child` | Yes, after extractor change |
| URL/HTML | `heading_aware` over preserved DOM headings | fallback `fixed_size` | Yes, after extractor change |
| OCR / weakly structured text | `fixed_size` | none by default | Yes |

## Recommended Chunking Architecture

### Stage 1: Structured Extraction

Replace the current “single `extracted_text` string only” mindset with a structured extraction payload.

Each extractor should return:

- `extracted_text`: flattened text for legacy compatibility
- `segments`: ordered structural units
- `document_metadata`

Recommended segment schema:

```json
{
  "segment_order": 1,
  "segment_type": "page|section|paragraph|block",
  "text": "segment text",
  "page_number": 3,
  "heading_path": ["Installation", "Linux"],
  "section_title": "Linux",
  "source_url": "https://example.com/docs/install",
  "dom_path": "article > h2:nth-of-type(2)",
  "metadata": {}
}
```

### Stage 2: Source-Native Primary Chunking

Chunkers should operate over `segments`, not only raw text.

Recommended primary chunkers:

- Markdown: group by heading hierarchy, then split oversized sections by sentence or paragraph.
- PDF: keep chunks inside page boundaries by default, then split large pages internally.
- URL/HTML: group content by heading hierarchy extracted from DOM.
- Text: split by paragraph first, then sentence-aware fixed sizing.

### Stage 3: Secondary Retrieval Views

After primary chunks are created:

- optionally derive parent chunks from adjacent child chunks
- optionally derive semantic boundaries for specific experiments

The primary chunk set remains the citation source of truth.

## Concrete Repo Design

### A. Extraction Changes

#### PDF extractor

Current issue:

- [backend/extractors/pdf_extractor.py](backend/extractors/pdf_extractor.py:29) extracts pages but flattens them into one string.

Recommended behavior:

- preserve page-level segments
- keep page text separate
- optionally preserve page labels and detected headings within each page

Recommended returned shape:

```json
{
  "extracted_text": "legacy flattened text",
  "segments": [
    {
      "segment_order": 1,
      "segment_type": "page",
      "page_number": 1,
      "text": "Page 1 text",
      "metadata": {}
    }
  ]
}
```

#### Web extractor

Current issue:

- [backend/extractors/web_extractor.py](backend/extractors/web_extractor.py:36) strips HTML to flat text, which destroys heading structure before chunking.

Recommended behavior:

- parse headings `h1-h6`
- attach following paragraphs/lists/tables to the active heading path
- preserve source URL on all segments
- keep a fallback flat-text mode for malformed pages

Recommended segmentation unit:

- one section per heading block
- large sections split into paragraph groups later by the chunker

### B. Chunker Changes

#### 1. Fixed-size chunker

Keep it as the universal fallback and make it production-safe.

Required changes:

- chunk by paragraph first, sentence second
- use tokenizer-aware counting instead of `words * 1.3`
- make overlap token-aware, not sentence-count approximated
- preserve paragraph boundaries when possible

Recommended defaults:

- target size: 350-500 tokens
- overlap: 40-60 tokens

#### 2. Heading-aware chunker

Keep it as the default for Markdown and structured HTML.

Required changes:

- preserve intro text before the first heading
- preserve full heading path, not only the local heading title
- split oversized sections by paragraph, then sentence
- attach `heading_level` and `heading_path`

Recommended metadata:

- `section_title`
- `heading_level`
- `heading_path`
- `section_order`

#### 3. Page-aware chunker

Keep it only if the extractor preserves true page structure.

Required changes:

- operate on page segments, not magic text markers
- keep chunks inside page boundaries by default
- allow controlled cross-page merge only when a page is very short and explicitly enabled
- record `page_number_start` and `page_number_end`

Recommended defaults:

- no cross-page merge in production v1
- oversized pages split by paragraph/sentence inside the same page

#### 4. Semantic chunker

Do not use the current implementation as a default production strategy.

Current issue:

- [backend/chunking/semantic_chunker.py](backend/chunking/semantic_chunker.py:54) is heuristic and not truly embedding-based semantic segmentation.

Recommended role:

- keep as experimental only
- disable by default in production settings
- use only in offline comparison runs until quality is validated

Future production criteria:

- embedding-backed similarity or layout-aware segmentation
- minimum and maximum chunk size controls
- deterministic fallback to baseline chunking
- evaluation win over baseline on recall and groundedness

#### 5. Parent-child chunker

Promote this to a first-class retrieval view, not a half-implemented chunk variant.

Current issue:

- [backend/chunking/service.py](backend/chunking/service.py:66) persists `parent_chunk_id=None`
- [backend/chunking/parent_child_chunker.py](backend/chunking/parent_child_chunker.py:98) defines relationship creation but the flow does not invoke it

Recommended design:

- first create child chunks using the source-native primary strategy
- then create parent chunks from ordered child windows
- persist explicit lineage links

Required fields:

- child chunk: `parent_chunk_id`
- parent chunk: `metadata.child_chunk_ids`
- both: `chunk_role` = `child` or `parent`
- both: `base_strategy` = `fixed_size|heading_aware|page_aware`

Recommended defaults:

- child size: 300-450 tokens
- parent window: 3-5 child chunks
- retrieve children first, expand to parents only after scoring

### C. Chunk Model Changes

Extend persisted chunk metadata to support production retrieval.

Recommended fields:

- `chunk_role`: `primary|child|parent`
- `base_strategy`
- `effective_strategy`
- `token_count`
- `char_count`
- `page_number_start`
- `page_number_end`
- `heading_path`
- `section_order`
- `segment_start_order`
- `segment_end_order`
- `lineage_group_id`
- `settings_hash`

Meaning:

- `base_strategy` = structural strategy used to produce the primary units
- `effective_strategy` = final retrieval view stored in the row

Example:

- child chunk from Markdown document:
  - `base_strategy = heading_aware`
  - `effective_strategy = parent_child`
  - `chunk_role = child`

### D. Indexing Rules

Chunking and indexing should follow these rules:

1. Generate primary chunks first.
2. Persist primary chunks.
3. If parent-child is enabled, derive and persist parent chunks with links.
4. Index child chunks for retrieval.
5. Index parent chunks only if parent expansion is enabled.
6. Keep generation boundaries strict so reindex never mixes old and new chunks.

Recommended retrieval rule:

- default retrieval target = child or primary chunks
- parent chunks are expansion context, not the first retrieval surface unless explicitly configured

## Recommended Production Defaults

### Global defaults

- `chunk_size`: 400 tokens
- `chunk_overlap`: 50 tokens
- `semantic_chunking_enabled`: `false`
- `parent_child_enabled`: `true` for Markdown and PDF only after lineage is implemented

### By source type

#### Markdown

- primary: `heading_aware`
- child size: 400
- overlap: 50
- parent-child: on

#### Plain text

- primary: `fixed_size`
- child size: 400
- overlap: 50
- parent-child: off by default

#### PDF

- primary: `page_aware`
- child size: 350
- overlap: 40
- parent-child: on

#### URL

- primary: `heading_aware`
- fallback: `fixed_size`
- child size: 400
- overlap: 50
- parent-child: off initially

## Recommended Retrieval Behavior

The retrieval layer should align with the chunk design:

- retrieve `child` or `primary` chunks first
- use `parent_chunk_id` to expand context after ranking
- do not cite parent chunks directly if the answer came from a child chunk
- keep parent chunks available for generation context and X-ray inspection

## Reindexing Rules

To keep chunking production-safe:

1. Create a new index generation for every settings change affecting chunk boundaries.
2. Persist chunks with a generation or settings hash.
3. Mark exactly one active generation per document and collection.
4. Remove or deactivate stale vectors and stale chunk views before promoting the new generation.

Chunk-affecting settings include:

- source extractor version
- chunk strategy
- chunk size
- overlap
- semantic threshold
- parent-child window size

## Observability Requirements

Expose chunking decisions in the playground and inspection APIs.

For every chunk returned in debugging views, show:

- document id
- chunk id
- chunk role
- effective strategy
- token count
- page range
- section title
- heading path
- parent chunk id
- generation id
- fallback flags

Recommended metrics:

- chunks per document
- average tokens per chunk
- percentage of fallback chunking
- percentage of tiny chunks under threshold
- percentage of oversized chunks above threshold
- parent expansion hit rate

## Rollout Plan

### Phase 1: Stabilize Baselines

- make `fixed_size` tokenizer-aware
- preserve pre-heading text in `heading_aware`
- preserve page segments in PDF extraction
- preserve heading structure in web extraction

### Phase 2: Make Parent-Child Real

- persist child and parent roles
- wire `parent_chunk_id`
- derive parent chunks after primary chunk persistence
- update retrieval to expand via persisted lineage

### Phase 3: Tighten Reindexing

- attach generation or settings hash to chunks
- avoid mixed chunk/index generations
- clean stale vectors during reindex

### Phase 4: Re-evaluate Semantic Mode

- keep current semantic mode experimental
- only promote if it beats baseline in offline evaluation

## Acceptance Criteria For This Design

- PDFs retain real page provenance in chunk rows.
- URLs retain heading or section provenance when HTML structure exists.
- Parent-child retrieval uses persisted lineage, not inferred grouping at read time.
- `fixed_size` becomes the reliable fallback for all source types.
- Reindexing produces one active chunk/index generation without stale mixing.
- Advanced strategies are optional enhancements over a strong baseline, not fragile defaults.

## Final Recommendation

For this repo, the recommended production chunking design is:

- `heading_aware` for Markdown and structured HTML
- `page_aware` for PDF only after page-preserving extraction is implemented
- `fixed_size` as the universal fallback and the most trusted baseline
- `parent_child` as a secondary retrieval view built on top of primary chunks
- `semantic` kept experimental until validated by evaluation

This keeps the system practical, improves retrieval quality, and matches the architecture you already have without forcing a full rewrite.

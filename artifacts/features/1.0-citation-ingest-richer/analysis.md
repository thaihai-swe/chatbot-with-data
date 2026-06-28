# Notebook LM Tier 1 — Core Gaps Analysis

## 1. Scope

Implement three Tier 1 gaps from the Notebook LM comparison (`artifacts/features/notebooklm-clone/analysis.md`):

1. **Quote-level citations** — extract exact cited sentences, store `quote_text`, highlight in modal
2. **Document understanding pipeline** — auto-summarize, extract key topics, preserve section hierarchy on ingestion
3. **Richer context engineering** — include source summaries, section context, citation mapping in LLM context package

---

## 2. Gap 1: Quote-Level Citations

### Current State

| Aspect | Current Implementation |
|--------|----------------------|
| Citation model | `Citation` dataclass has `quote_text: Optional[str]` field (already defined!) — see `models/chat.py:61` |
| CitationService.extract_citations | Regex `[Source N]` extraction from answer text — `chat/citations.py:17` |
| CitationService._format_citation | Returns `{chunk_id, document_id, title, page_number, section_title, source_url}` — **no quote_text** — `chat/citations.py:72-81` |
| Citation persistence | `chat/service.py:201-208` and `chat/streaming.py:193-201` create citations in SQLite; `quote_text` is never populated (None) |
| Frontend display | CitationModal shows entire chunk text (`chunk.text || chunk.content`) — not the specific quote — `CitationModal.jsx:37` |
| Prompt instruction | System prompt says: "Place citations immediately after the factual claim they support" — `prompts.py:9` |

### Key Observation

The `cite.quote_text` column **already exists** in both the `Citation` dataclass and the SQLite schema (`migrations/runner.py:267`). It's just never populated. The missing piece is:
- Extracting the **exact sentence(s)** from the chunk that correspond to each `[Source N]` marker
- Storing that in the citation record
- Rendering it in the CitationModal

### Boundary Contract

| Current Contract | Change Required |
|-----------------|-----------------|
| `CitationService.map_citations_to_chunks()` returns `[{chunk_id, document_id, title, page_number, ...}]` | Add `quote_text` field to return value |
| `ChatRepository.create_citation()` accepts `quote_text=None` | Call with extracted quote text |
| `CitationModal` shows `chunk.text` | Show `citation.quote_text` as primary, `chunk.text` as surrounding context |

### Options for Quote Extraction

| Option | Complexity | Quality | Notes |
|--------|-----------|---------|-------|
| **A. LLM post-processing** | Medium | High | Send answer + chunks to LLM, ask it to extract exact quote per citation. Most accurate but adds latency + cost |
| **B. Sentence overlap matching** | Low | Medium | Split chunk into sentences, find max-overlap sentence with the answer claim. No LLM call, but less precise |
| **C. Regex + proximity** | Low | Low | Find chunk text that appears near `[Source N]` in the answer. Simple but fragile |

**Recommendation:** Option B for the happy path, fall back to Option A for complex cases where B fails.

### Files to Modify

| File | Change |
|------|--------|
| `chat/citations.py` | Add `extract_quote(chunk_text, answer_text, label) -> str` method using sentence overlap |
| `chat/service.py:195-201` | Call `extract_quote()` and pass `quote_text` to `create_citation()` |
| `chat/streaming.py:187-194` | Same for streaming path |
| `CitationModal.jsx` | Show `quote_text` with highlight, show full chunk as secondary context |

---

## 3. Gap 2: Document Understanding Pipeline

### Current State

The current ingestion pipeline is:
```
Upload → Extract text → Duplicate detection → Create document → Chunk → Index
```

There is **no** step for:
- Generating a source summary
- Extracting key topics/keywords
- Preserving and storing section hierarchy metadata at the document level

**Current document metadata** stored in `documents.metadata_json` (freeform JSON):
- Source info (URL, filename, type)
- Page count, author (from PDF extractor)
- No summary, no topics, no section map

**Current chunk metadata** (`chunks` table):
- `section_title`, `page_number`, `source_url` — per-chunk
- But no document-level summary or section list

### What Notebook LM Does

1. On upload: LLM reads entire source → generates **source summary**
2. Extracts **key topics** from the source
3. Preserves **section hierarchy** (table of contents, heading structure)
4. Stores all of these in the notebook for later use in context engineering

### Design

#### 3a. Document Understanding Step

Insert a new step between extraction and chunking in `ingestion/service.py`:

```
Extract → Document Understanding → Duplicate detection → Create document → Chunk → Index
                   ↓
           {summary, topics, section_map}
                   ↓
           stored in documents.metadata_json
```

The document understanding step:
1. Calls LLM with the full extracted text
2. LLM returns: `{summary, topics: string[], sections: [{heading, level, start_offset, end_offset}]}`
3. Stored in `documents.metadata_json` → `{..., "doc_understanding": {...}}`

#### 3b. Section Hierarchy Preservation

Currently, section-aware chunkers (`heading_aware`, `page_aware`) already extract `section_title` per chunk. But we don't store the **overall section tree** at the document level.

Two options:
- **Lightweight**: Store section tree in document metadata (from the doc understanding LLM call)
- **Heavier**: Extract from chunker output by aggregating unique sections from chunks

**Recommendation:** Lightweight — include it in the LLM understanding call.

### Boundary Contract

| Current Contract | Change Required |
|-----------------|-----------------|
| `process_ingestion_attempt()` → `_finalize_successful_ingestion()` → `chunk_and_index_document()` | Insert new step after extraction, before `_finalize_successful_ingestion()` |
| `documents.metadata_json` | Add `doc_understanding.summary`, `doc_understanding.topics`, `doc_understanding.sections` |
| Extraction result dict `{title, extracted_text, metadata, ...}` | Add optional `doc_understanding` field |
| Settings schema | Add `doc_understanding_enabled: bool` toggle under `ingestion` |

### Files to Modify

| File | Change |
|------|--------|
| `ingestion/service.py` | Add `_understand_document(text, metadata) -> dict` step between extraction and finalization |
| `ingestion/service.py` | Store result in document metadata |
| `extractors/common.py` | Add `ExtractionResult` dataclass with optional `doc_understanding` field (or just use dict) |
| `schemas/settings.py` | Add `doc_understanding_enabled: bool`, `doc_understanding_model: str` to `IngestionSettings` |
| `chat/prompts.py` | Add `DOCUMENT_UNDERSTANDING_PROMPT` for LLM call |
| *(new file)* | Consider extracting understanding logic into `indexing/understanding.py` or keeping inline |

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| LLM cost for summarizing every source | MEDIUM | Only run when `doc_understanding_enabled=true`; use cheaper model for summarization |
| Latency added to ingestion path | MEDIUM | Run as async background task (already the case for chunking), not blocking the API response |
| Large documents exceed LLM context | MEDIUM | Use the same chunking strategy to summarize incrementally, or skip if > 100K tokens |

---

## 4. Gap 3: Richer Context Engineering

### Current State

`ContextService.assemble_context()` currently builds:

```
<source label="Source 1" id="..." title="..." page="...">
chunk text
</source>
<source label="Source 2" ...>
...
</source>
```

That's it — just tagged chunk text. The system prompt adds instructions for citation format and grounded answer rules.

**Current context package structure** (`chat/context.py:83-92`):
```python
{
    "system_prompt": "...<source>...</source>...",
    "context_string": "<source>...</source>...",
    "history": [...],
    "current_query": "...",
    "metadata": {"num_chunks": N, "num_history_turns": M}
}
```

### What Notebook LM's Context Package Includes

Per the research (huxiu.com article on Notebook LM technical architecture):

```
- User question
- Query intent
- Candidate evidence
- Evidence source metadata
- Section context (heading, surrounding paragraphs)
- Extended context (parent chunk)
- Source summaries
- Chat history
- User notes
- Citation mapping (which claim maps to which source)
- Answer constraints
- Insufficient-evidence handling rules
```

### Changes Required

#### 4a. Include Source Summaries

When `doc_understanding` is available on the document, include the source summary at the top of the context:

```xml
<document-summaries>
<document id="uuid-1" title="Annual Report 2025">
Summary: This document covers financial performance...
</document>
</document-summaries>

<source label="Source 1" ...>
chunk text
</source>
```

#### 4b. Include Section Context

For each chunk, include the full section path (section hierarchy):

```xml
<source label="Source 1" id="uuid-abc" title="..." page="..." section="3.2.1 > Revenue Growth">
chunk text
</source>
```

This requires the heading_aware chunker to output the full section path (already stores `section_title`), and the context builder to use it.

#### 4c. Include Citation Mapping

Add a mapping section before the sources:

```xml
<citation-map>
[Source 1] → "Annual Report 2025", Section "Revenue Growth", page 42
[Source 2] → "Q3 Earnings Call", page 12
</citation-map>
```

This helps the LLM cite correctly and lets us validate citations in post-processing.

#### 4d. Incorporate into System Prompt

Current system prompt (`prompts.py:3-18`):
```
You are a helpful and accurate assistant. You MUST answer based ONLY on the provided source text.
...
3. Always include citations in your answer using the source labels provided in the context (e.g., [Source 1], [Source 2]).
...
```

Add explicit instructions about:
- How to handle conflicting sources (flag the conflict)
- How to handle claims that lack source support (state "this is not directly supported by the sources")
- Structure for multi-source synthesis

### Boundary Contract

| Current | Change |
|---------|--------|
| `ContextService.assemble_context()` takes `query_text, retrieved_chunks, chat_history` | Add `collection_ids` param to look up document summaries |
| Context package dict shape | Add `source_summaries`, `section_hierarchy`, `citation_map` fields |
| System prompt template | Add conflict handling, source attribution, and uncertainty expression rules |
| `RetrievalResult[]` (chunk metadata) | Ensure `section_path` and `document_id` are always present for mapping |

### Files to Modify

| File | Change |
|------|--------|
| `chat/context.py` | Enrich context package with source summaries, section hierarchy, citation map |
| `chat/prompts.py` | Add conflict-handling and uncertainty rules to `BASE_GROUNDED_CHAT_SYSTEM_PROMPT` |
| `chat/service.py` | Pass collection context to `ContextService` |
| `repositories/document_repository.py` | Add `get_document_batch(ids)` to bulk-fetch document metadata |
| `chat/prompts.py` | Add `CONFLICT_DETECTION_INSTRUCTION` optional block |

---

## 5. Dependency Map

```
Gap 3 (Richer Context) ──depends on──► Gap 2 (Doc Understanding)
                                             provides source summaries + section hierarchy

Gap 1 (Quote Citations) ──independent──► can be done in parallel with Gaps 2+3

Gap 1 ──depends on──► ChatContext has citation map (Gap 3) for validation
                     (weak dependency — can work independently first)

Gap 2 ──depends on──► LLM provider for summarization (already exists)
                     Ingestion pipeline hook point (already exists)
```

**Recommended implementation order:** Gap 1 first (independent, lowest risk), then Gap 2, then Gap 3.

---

## 6. Preserved Behaviors (Don't Break)

| ID | Invariant | Why |
|----|-----------|-----|
| INV-001 | 3-layer safety before retrieval/generation | Must not move or skip |
| INV-002 | Hybrid search remains default retrieval | Single-strategy is degraded mode |
| INV-003 | SSE streams are append-only | Frontend depends on ordered events |
| INV-004 | No quote_text → old citations still render | `quote_text` is nullable; frontend must handle null gracefully |
| INV-005 | Doc understanding disabled → ingestion works same as before | Must be opt-in via settings toggle |
| INV-006 | Context assembly without doc understanding works | Source summaries are additive, not required |

---

## 7. Reuse Opportunities

| Existing Component | Reuse For |
|-------------------|-----------|
| `chat/prompts.py` prompt system | Add `DOCUMENT_UNDERSTANDING_PROMPT`, `CONFLICT_DETECTION_INSTRUCTION` |
| `CitationService` | Extend with `extract_quote()` method |
| `Citation` model `quote_text` field | Already exists, just needs population |
| `ContextService` | Extend with source summary injection |
| `ChatRepository.create_citation()` | Already accepts `quote_text` param |
| `ingestion/service.py` hook pattern | Insert doc understanding as another processing stage |
| `config.settings.json` ingestion settings | Add `doc_understanding_enabled` toggle |
| Heading-aware chunker | Already extracts `section_title` per chunk; full section path can be added |

---

## 8. Risks and Mitigations

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| LLM cost for doc understanding on every source | MEDIUM | HIGH | Toggle off by default; use cheaper model; batch summaries |
| Latency increase on ingestion | MEDIUM | HIGH | Already async; add timeout with fallback (skip understanding) |
| Quote extraction quality low | MEDIUM | MEDIUM | Use LLM fallback when sentence overlap fails |
| Section hierarchy from LLM is unreliable | LOW | HIGH | Use heuristic extraction from heading_aware chunker as ground truth |
| Context package grows too large (source summaries) | LOW | MEDIUM | Token-budget the summary section; truncate if needed |
| Frontend changes for quote highlight | LOW | LOW | Already have CitationModal; just change which field is primary |

---

## 9. Estimated Scope

| Gap | Files Changed | New Files | Est. LOC | Risk |
|-----|--------------|-----------|---------|------|
| 1. Quote citations | 4 (citations.py, service.py, streaming.py, CitationModal.jsx) | 0 | +~60 | LOW |
| 2. Doc understanding | 3 (ingestion/service.py, prompts.py, schemas/settings.py) | 1 (indexing/understanding.py) | +~150 | MEDIUM |
| 3. Richer context | 3 (context.py, prompts.py, document_repository.py) | 0 | +~80 | MEDIUM |
| **Total** | **~10 files** | **1 new file** | **+~290 LOC** | |

---

## 10. Conclusion

> All three gaps are well-bounded, minimally invasive, and build on existing infrastructure. The `quote_text` field already exists in the database — Gap 1 is mostly populating it. Gap 2 is a new pipeline stage that can be toggled off. Gap 3 is an additive enrichment that degrades gracefully. No architectural changes required.

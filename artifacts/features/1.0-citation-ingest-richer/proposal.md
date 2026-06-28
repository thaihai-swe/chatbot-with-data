# Proposal: Citation, Document Understanding, and Richer Context

## Overview
Close three high-impact gaps between the current chatbot RAG system and Google Notebook LM, focused on citation precision, source-level document understanding, and richer LLM context packages.

## In Scope

### Gap 1 — Quote-Level Citations
- Extract exact cited sentences from source chunks using sentence overlap matching
- Fall back to LLM-based quote extraction when overlap is weak (< 0.5 similarity)
- Store `quote_text` in citation records (column already exists in DB schema)
- Surface quote as primary content in the CitationModal frontend component
- Show surrounding chunk context as secondary/expandable

### Gap 2 — Document Understanding Pipeline
- Insert a new pipeline stage between text extraction and duplicate detection in `IngestionService`
- LLM generates: source summary, key topics list, section hierarchy map
- Store in `documents.metadata_json` under `doc_understanding` key
- New `ingestion.doc_understanding_enabled` settings toggle (default: true)
- New `DOCUMENT_UNDERSTANDING_PROMPT` in `chat/prompts.py`
- Extract understanding logic into `indexing/understanding.py`
- Graceful skip for documents exceeding 100K tokens

### Gap 3 — Richer Context Engineering
- Include source summaries in the LLM context package (from Gap 2 data)
- Include section hierarchy path in each source tag (`section="1.2 > Revenue"`)
- Include citation mapping block before source tags
- Add conflict detection instruction to system prompt
- Add uncertainty/insufficient-evidence rules to system prompt
- Bulk-fetch document metadata via `DocumentRepository.get_document_batch()`

## Out of Scope
- Multi-format ingestion (DOCX, EPUB, YouTube, etc.) — deferred
- Knowledge product generation (study guides, briefings, FAQs) — deferred
- User annotation/notes system — deferred
- Full-text source browser in frontend — deferred
- Audio/Slides/Video features — per user instruction

## Non-Goals
- Replace the existing chunking or retrieval architecture
- Change the SSE streaming protocol or event format
- Add new external dependencies or vector store integrations
- Modify the citation DB schema (column already exists)

## Key Design Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Quote extraction | Sentence overlap + LLM fallback | Cost-conscious with quality safety net |
| Doc understanding default | Enabled | Better UX out of the box |
| Implementation order | Sequential 1→2→3 | Clean dependency chain |
| Conflict detection | Included in Gap 3 | Completes the context enrichment |
| Section hierarchy source | LLM-generated (not chunker-derived) | Simpler, single source of truth |
| Doc understanding model | Same LLM provider (configurable) | No new dependency |

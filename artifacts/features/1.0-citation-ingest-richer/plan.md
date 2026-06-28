# Plan: Citation, Document Understanding, and Richer Context

## Part 1: Technical Design

**Complexity:** Moderate — multiple areas (chat pipeline, ingestion, frontend), schema change (add fields to `metadata_json`), but no external integrations.

### Gap 1 — Quote-Level Citations

#### Design

**QuoteExtractor (in `chat/citations.py`)**

New method on `CitationService`:

```
extract_quote(chunk_text, answer_text, label) -> str
```

Algorithm:
1. Split `answer_text` into sentences via `re.split(r'(?<=[.!?])\s+')`
2. Find the sentence containing `[Source {label}]` — this is the "claims sentence"
3. Split `chunk_text` into sentences
4. For each chunk sentence, compute Jaccard word-overlap with the claims sentence:
   `|words(s1) ∩ words(s2)| / |words(s1) ∪ words(s2)|`
5. If max overlap >= 0.5, return that chunk sentence
6. Else, call LLM with `QUOTE_EXTRACTION_PROMPT`, return LLM result

**New prompt in `chat/prompts.py`:**
```
QUOTE_EXTRACTION_PROMPT = """Extract the exact sentence(s) from the source chunk that support the claim: "{claim_sentence}"

Source chunk: "{chunk_text}"

Return ONLY the exact quote as a plain string. If nothing supports the claim, return "". Do not add explanations."""
```

**Integration:**
- `CitationService.map_citations_to_chunks()` — include `quote_text` in each dict
- `chat/service.py:process_turn` (line ~195) — call `extract_quote()` before `create_citation()`
- `chat/streaming.py:stream_turn` (line ~187) — same

**Frontend — `CitationModal.jsx`**
- If `quote_text` is set: display as primary content with highlighted background
- Add collapsed "Show full context" toggle below the quote, revealing `chunk.text`
- If `quote_text` is null: display full `chunk.text` as before (no toggle)

**Data flow:**
```
LLM response → extract [Source N] labels → extract_quote() per label → 
CitationService._format_citation() includes quote_text → 
create_citation(quote_text=...) → SSE/JSON response → CitationModal renders quote
```

### Gap 2 — Document Understanding Pipeline

#### Design

**New module: `indexing/understanding.py`**

```python
class DocumentUnderstandingService:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def understand(self, text: str, title: str | None = None) -> dict | None:
        """Returns {summary, topics, sections} or None on failure."""
```

**New prompt in `chat/prompts.py`:**
```
DOCUMENT_UNDERSTANDING_PROMPT = """Analyze the following document and return JSON.
Fields:
- "summary": 2-3 sentence summary
- "topics": array of 3-7 key topics/keywords
- "sections": array of {heading, level} representing the document's section hierarchy

Reply ONLY with valid JSON. No preamble.

Title: {title}
Document text:
{document_text}
JSON:"""
```

**Integration into ingestion pipeline (`ingestion/service.py`):**

Before the current sequence, insert a new step:

```
process_ingestion_attempt():
  1. Extract text (existing)
  2. UNDERSTAND: call DocumentUnderstandingService.understand()
     - Skip if text > 100K chars (AC-2.6)
     - Skip if settings doc_understanding_enabled=false (AC-2.5)
     - Skip on LLM error/failure (AC-2.7)
  3. Duplicate detection (existing)
  4. _finalize_successful_ingestion() (existing) — store understanding in metadata_json
  5. chunk_and_index_document() (existing)
```

**Settings additions (`schemas/settings.py`):**
```python
class IngestionSettings(BaseModel):
    # ... existing fields
    doc_understanding_enabled: bool = True
    doc_understanding_model: Optional[str] = None  # None = use default
```

**Data flow:**
```
Extraction → [new] DocumentUnderstandingService.understand()
  ↓ result stored in metadata_json["doc_understanding"]
_finalize_successful_ingestion() → creates/updates document
  ↓ metadata persists in SQLite documents.metadata_json
Later: ContextService reads from metadata_json via DocumentRepository
```

### Gap 3 — Richer Context Engineering

#### Design

**DocumentRepository addition:**

```python
def get_document_batch(self, ids: list[str]) -> dict[str, dict]:
    """Returns {id: {title, metadata}} for all given IDs."""
```

**ContextService enrichment (`chat/context.py`):**

New flow in `assemble_context()`:

1. Accept optional `collection_ids: list[str]` parameter
2. Collect unique `document_id` values from `retrieved_chunks`
3. Call `DocumentRepository.get_document_batch(ids)` to get summaries
4. Build `<document-summaries>` block:
   ```xml
   <document-summaries>
   <document id="uuid-1" title="Annual Report 2025">
   Summary: This document covers...
   </document>
   </document-summaries>
   ```
5. For each chunk, add `section` attribute using chunk's `section_title` or `metadata.section_path`
6. Build `<citation-map>` block from chunk metadata:
   ```xml
   <citation-map>
   [Source 1] → "Annual Report 2025", Section "3.2 > Revenue"
   </citation-map>
   ```
7. Modify system prompt injection to include `{conflict_instruction}` and `{uncertainty_instruction}` blocks
8. When only 1 unique document, exclude `{conflict_instruction}`

**System prompt updates (`chat/prompts.py`):**

```python
BASE_GROUNDED_CHAT_SYSTEM_PROMPT = """... {conflict_instruction} {uncertainty_instruction} <context>..."""

CONFLICT_INSTRUCTION = "If the sources contain conflicting information, explicitly state the conflict and present both sides. Do not silently choose one."

UNCERTAINTY_INSTRUCTION = "If a claim in your answer is not directly supported by the provided sources, clearly mark it with [unsupported]. Do not present unsupported claims as facts."
```

**Context package dict now includes:**
```python
{
    "system_prompt": "...with summaries + citation map...",
    "context_string": "<document-summaries>...<citation-map>...<source>...",
    "source_summaries": [...],
    "citation_map": [...],
    "history": [...],
    "current_query": "...",
}
```

### Architecture Diagram (Simplified)

```
┌─────────────┐     ┌──────────────────────┐     ┌──────────────┐
│  Ingestion   │ ──► │ DocumentUnderstanding │ ──► │  SQLite docs  │
│  (extract)   │     │  Service (LLM)       │     │  metadata    │
└─────────────┘     └──────────────────────┘     └──────┬───────┘
                                                        │
┌─────────────┐     ┌──────────────────────┐            │
│  User Query  │ ──► │  Retrieval Pipeline  │ ──► chunks │
└─────────────┘     └──────────────────────┘            │
                              │                         │
                              ▼                         ▼
┌──────────────────────────────────────────────────────────┐
│              ContextService (Gap 3)                       │
│  reads doc_understanding from metadata                   │
│  builds <document-summaries> + <citation-map>             │
│  injects conflict/uncertainty instructions                │
└──────────────────────────┬───────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────┐
│              GenerationService                             │
│  LLM produces answer with [Source N] markers              │
└──────────────────────────┬───────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────┐
│              CitationService (Gap 1)                      │
│  extract_quote() per marker → quote_text                 │
└──────────────────────────┬───────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────┐
│              CitationModal (Frontend)                     │
│  shows quote_text highlighted, full context toggle        │
└──────────────────────────────────────────────────────────┘
```

---

## Part 2: Delivery Strategy

### Phases

| Phase | Gaps | Dependencies | Est. Effort |
|-------|------|-------------|-------------|
| **Phase 1** | Gap 1 (Quote Citations) | None | ~6h |
| **Phase 2** | Gap 2 (Doc Understanding) | None | ~5h |
| **Phase 3** | Gap 3 (Richer Context) | Phase 2 (need doc_understanding data) | ~4h |
| **Total** | | | **~15h** |

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| LLM quote extraction unreliable | Sentence overlap handles 80%+ cases; LLM fallback only for edge cases |
| Doc understanding adds latency | Non-fatal skip; timeout configurable via settings |
| Context package grows too large | Summaries/citation map are small (< 500 tokens); token budget guard in ContextService |
| Backward compatibility broken | Every new path checks for null/empty old data before using new features |

### Architectural Gate Checklist

- [x] **Simplicity Gate**: No speculative code. Each piece directly satisfies spec ACs. No new abstractions beyond what the spec requires.
- [x] **Anti-Abstraction Gate**: Using existing patterns (`CitationService`, `IngestionService`, `ContextService`). No custom wrappers.
- [x] **No New Dependencies**: LLM provider already exists. No new pip packages.
- [x] **No Schema Migrations**: `quote_text` column already exists. `metadata_json` is freeform JSON — no ALTER TABLE needed.

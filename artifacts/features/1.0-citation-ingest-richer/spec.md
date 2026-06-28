# Spec: Citation, Document Understanding, and Richer Context

## 1. Why

Notebook LM achieves high user trust through three interconnected features: citing exact quotes (not whole chunks), understanding documents at the source level, and engineering rich context packages that help the LLM reason precisely. Our system has the pipeline architecture but lacks these refinements. Closing these gaps moves us from basic RAG to product-grade grounded generation.

---

## 2. Gap 1 — Quote-Level Citations

### What
After answer generation, extract the exact sentence(s) from the source chunk that correspond to each `[Source N]` citation marker. Store as `quote_text` in the citation record. Surface the quote as the primary display in the CitationModal, with the full chunk text as expandable context.

### Why
Users currently see the entire chunk when clicking a citation. They have to hunt through potentially hundreds of words to find the specific claim. Showing the exact cited sentence builds trust and speeds verification — the core value of citations.

### Acceptance Criteria

**AC-1.1:** `CitationService` has a new public method `extract_quote(chunk_text: str, answer_text: str, label: str) -> str` that:
- Splits `chunk_text` into sentences
- For each sentence, computes word-overlap Jaccard similarity with the sentence in `answer_text` that contains `[Source {label}]`
- Returns the best-matching sentence (score >= 0.5) from the chunk
- Falls back to LLM extraction when no sentence scores >= 0.5

**AC-1.2:** When best-matching chunk sentence has >= 0.5 overlap, the method returns it without calling the LLM.

**AC-1.3:** When no chunk sentence has >= 0.5 overlap, the method calls the LLM with a `QUOTE_EXTRACTION_PROMPT` to extract the exact quote, and returns the LLM result.

**AC-1.4:** `CitationService.map_citations_to_chunks()` includes `quote_text` in each returned citation dict.

**AC-1.5:** The non-streaming chat path (`chat/service.py:process_turn`) calls `extract_quote()` for each citation and passes `quote_text` to `ChatRepository.create_citation()`.

**AC-1.6:** The streaming chat path (`chat/streaming.py:stream_turn`) calls `extract_quote()` for each citation and includes `quote_text` in citation objects sent via SSE.

**AC-1.7:** CitationModal displays `quote_text` as the primary content (highlighted with a distinct background) and the full chunk text as expandable secondary content below a "Show full context" toggle.

**AC-1.8:** When `quote_text` is null (backward compatibility with old citations), CitationModal falls back to displaying full chunk text as before.

**AC-1.9:** Gherkin — CitationModal quote display:
```
Given a citation with quote_text "Revenue grew 15% in Q3"
  And chunk text containing "Revenue grew 15% in Q3, driven by international expansion"
When the user clicks the citation tag
Then the modal shows "Revenue grew 15% in Q3" with highlighted background
  And the modal shows a "Show full context" toggle
  And clicking the toggle reveals the full chunk text
```

**AC-1.10:** Gherkin — Backward compatibility:
```
Given an existing citation with quote_text = null
When the user clicks the citation tag
Then the modal shows the full chunk text
  And no "Show full context" toggle is shown
```

**Verification:** `python3 -m pytest tests/chat/test_citations.py -v` (add test file)

---

## 3. Gap 2 — Document Understanding Pipeline

### What
On ingestion, automatically generate a source summary, extract key topics, and map the section hierarchy of the document. Store in `documents.metadata_json` for later use in context engineering.

### Why
Notebook LM generates source summaries on upload, which serve two purposes: (1) the LLM uses them to understand what each source covers before reading chunks, and (2) users can quickly assess a source's relevance. Without this, the LLM only sees isolated chunks with no document-level context.

### Acceptance Criteria

**AC-2.1:** A new Python module `indexing/understanding.py` contains a `DocumentUnderstandingService` class with method `understand(text: str, title: str | None) -> dict` that:
- Calls the LLM with `DOCUMENT_UNDERSTANDING_PROMPT`
- Returns `{"summary": str, "topics": list[str], "sections": list[{"heading": str, "level": int}]}`

**AC-2.2:** `DOCUMENT_UNDERSTANDING_PROMPT` in `chat/prompts.py` instructs the LLM to:
- Generate a 2-3 sentence summary of the document
- Extract 3-7 key topics/keywords
- Map the section hierarchy (headings with nesting levels)

**AC-2.3:** `IngestionService.process_ingestion_attempt()` calls `DocumentUnderstandingService.understand()` after text extraction and before `_finalize_successful_ingestion()`.

**AC-2.4:** The understanding result is stored in `documents.metadata_json` under the `doc_understanding` key: `{"summary": "...", "topics": [...], "sections": [...]}`.

**AC-2.5:** When `doc_understanding_enabled` is `false` in settings, the understanding step is skipped entirely and ingestion proceeds as before.

**AC-2.6:** When document extracted text exceeds 100,000 characters, the understanding step is skipped and a warning is logged.

**AC-2.7:** If the LLM call fails or times out, the understanding step is skipped (non-fatal) and ingestion continues normally. A warning is logged.

**AC-2.8:** `IngestionSettings` in `schemas/settings.py` gains two new fields:
- `doc_understanding_enabled: bool = True`
- `doc_understanding_model: Optional[str] = None` (None = use default LLM model)

**AC-2.9:** Gherkin — Understanding runs on new ingestion:
```
Given a document is uploaded with 5000 words of text
  And doc_understanding_enabled is true
When the ingestion completes
Then the document record has doc_understanding.summary
  And doc_understanding.topics has 3-7 entries
  And doc_understanding.sections has at least 1 entry
```

**AC-2.10:** Gherkin — Understanding skip on large doc:
```
Given a document with 150,000 characters of text
When the ingestion processes it
Then a warning is logged "Skipping doc understanding: text exceeds 100K chars"
  And the document record has no doc_understanding field
  And the ingestion completes normally
```

**Verification:** `python3 -m pytest tests/ingestion/test_understanding.py -v` (add test file)

---

## 4. Gap 3 — Richer Context Engineering

### What
Enrich the LLM context package with source summaries, section hierarchy paths, and a citation mapping block. Add conflict detection and uncertainty-handling instructions to the system prompt.

### Why
The current context package is just chunk text in `<source>` tags. Notebook LM shows the LLM a richer picture: which sources cover what topics, where each chunk sits in the document structure, and how citations map to documents. This helps the LLM synthesize across sources more accurately and flag conflicts naturally.

### Acceptance Criteria

**AC-3.1:** `ContextService.assemble_context()` accepts an optional `collection_ids: list[str]` parameter and uses it to bulk-fetch document summaries via `DocumentRepository.get_document_batch()`.

**AC-3.2:** When source summaries are available, the context package includes a `<document-summaries>` block at the top listing each unique document's summary:
```xml
<document-summaries>
<document id="uuid-1" title="Annual Report">Summary: ...</document>
</document-summaries>
```

**AC-3.3:** Each `<source>` tag in the context includes a `section` attribute with the full section path when available (e.g., `section="3.2.1 > Revenue Growth"`).

**AC-3.4:** The context package includes a `<citation-map>` block mapping each source number to its document title and section:
```xml
<citation-map>
[Source 1] → "Annual Report", Section "3.2.1 > Revenue Growth"
[Source 2] → "Q3 Earnings", Section "Results Overview"
</citation-map>
```

**AC-3.5:** `DocumentRepository.get_document_batch(ids: list[str])` returns a dict keyed by document ID with `title` and `metadata.doc_understanding` fields.

**AC-3.6:** `BASE_GROUNDED_CHAT_SYSTEM_PROMPT` in `chat/prompts.py` is updated with two new instruction blocks (togglable via format variables):
- `{conflict_instruction}` — "If the sources contain conflicting information, explicitly state the conflict and present both sides. Do not silently choose one."
- `{uncertainty_instruction}` — "If a claim in your answer is not directly supported by the provided sources, clearly mark it with [unsupported]. Do not present unsupported claims as facts."

**AC-3.7:** When documents are present from only one source, the conflict instruction is excluded from the prompt (no conflict possible with a single source).

**AC-3.8:** Gherkin — Multi-source context:
```
Given chunks from 2 different documents with doc_understanding data
When ContextService.assemble_context() is called
Then the context string contains <document-summaries> with 2 entries
  And each <source> tag has a section attribute
  And the context string contains <citation-map>
  And the system prompt includes the conflict_instruction block
```

**AC-3.9:** Gherkin — Single-source context:
```
Given chunks from only 1 document
When ContextService.assemble_context() is called
Then the system prompt does NOT include the conflict_instruction block
```

**AC-3.10:** When no doc_understanding data exists (backward compatibility), context assembly skips the summaries block and citation map but still works with all existing fields.

**Verification:** `python3 -m pytest tests/chat/test_context.py -v` (add test file)

---

## 5. Non-Functional Requirements

| NFR | Target | Linked ACs |
|-----|--------|-----------|
| NFR-1: Quote extraction latency | < 50ms per citation for sentence overlap path | AC-1.1, AC-1.2 |
| NFR-2: Quote extraction latency | < 500ms per citation for LLM fallback path | AC-1.3 |
| NFR-3: Doc understanding latency | < 10s for documents under 50K chars | AC-2.3 |
| NFR-4: Doc understanding cost | No new model dependency; reuse existing LLM provider | AC-2.1 |
| NFR-5: Context assembly overhead | < 100ms added to existing assembly time | AC-3.1, AC-3.2 |
| NFR-6: Backward compatibility | All existing citations and contexts render without error | AC-1.8, AC-3.10 |
| NFR-7: Graceful degradation | Ingestion never fails due to understanding step | AC-2.5, AC-2.6, AC-2.7 |

---

## 6. Verification Surfaces

| Surface | What to verify | Command |
|---------|---------------|---------|
| Unit: citations | Quote extraction, format_citations | `pytest tests/chat/test_citations.py` |
| Unit: understanding | LLM prompt, parsing, metadata storage | `pytest tests/ingestion/test_understanding.py` |
| Unit: context | Context assembly with summaries, citation map | `pytest tests/chat/test_context.py` |
| Integration: ingestion | Full ingest flow with understanding enabled/disabled | Manual: upload doc via UI, inspect metadata_json |
| Integration: chat | End-to-end chat with quote citations rendered | Manual: ask question, click citation, verify quote |
| Frontend: CitationModal | Quote display, full context toggle, null fallback | Manual: visual inspection in browser |

---

## 7. Dependencies

| Gap | Depends On | Deliverable |
|-----|-----------|-------------|
| Gap 1 | None | Standalone — can be implemented first |
| Gap 2 | None | Standalone — can be implemented second |
| Gap 3 | Gap 2 (source summaries, section data) | Must wait for Gap 2 to populate metadata |

## 8. Open Questions (Resolved)

| Question | Resolution |
|----------|-----------|
| Quote extraction strategy | B (sentence overlap) + A (LLM fallback) |
| Doc understanding default | Enabled by default |
| Implementation order | Sequential 1 → 2 → 3 |
| Conflict detection scope | Included in Gap 3 |
| Doc understanding model | Same LLM provider (configurable via `doc_understanding_model`) |

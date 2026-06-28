# Test Questions — 1.0-citation-ingest-richer

Upload `rag-strategies-comparison.md` first, then try each question.

---

## Gap 1: Quote-Level Citations

| # | Question | What to check |
|---|----------|---------------|
| 1 | "What are the three limitations of Naive RAG?" | Should cite specific sentences; quote_text should highlight exact wording like "retrieval quality is highly sensitive to chunk size", "no query reformulation", "no mechanism for handling contradictory documents" |
| 2 | "How much does re-ranking improve top-3 accuracy?" | Citation should quote the exact claim "improves top-3 accuracy by 15-25%" |
| 3 | "What is the top-5 recall of Naive RAG on Natural Questions?" | Quote should contain "approximately 62%" |
| 4 | "What does HyDE stand for?" | Quote should contain the full expansion |
| 5 | "When should you use Modular RAG?" | Quote should mention "retrieval quality is the primary differentiator" and "engineering resources are available" |

## Gap 2: Document Understanding

| # | Question | What to check |
|---|----------|---------------|
| 6 | "What is this document about?" | System prompt should include a `<document-summaries>` block with a generated summary |
| 7 | "What are the main sections of the document?" | Should list Executive Summary, Naive RAG, Advanced RAG, Modular RAG, etc. |
| 8 | "What topics does this document cover?" | Topics from doc understanding should include RAG strategies, retrieval, re-ranking, etc. |

## Gap 3: Richer Context & Conflict Awareness

| # | Question | What to check |
|---|----------|---------------|
| 9 | "What are the trade-offs between Naive, Advanced, and Modular RAG?" | Should show balanced analysis with citations from multiple sections; the `<citation-map>` block should link sections to sources |
| 10 | "What is the most common mistake in RAG system design?" | Should quote the conclusion: "over-engineering the retrieval pipeline while neglecting chunking strategy, prompt design, and evaluation methodology" |

## Advanced: Multi-Doc Conflict

Upload a **second document** (e.g. one that argues Naive RAG is sufficient for production) then ask:

| # | Question | What to check |
|---|----------|---------------|
| 11 | "Is Naive RAG good enough for production?" | With two documents that disagree, the system prompt should include `<conflict-instruction>` and the answer should acknowledge conflicting sources |

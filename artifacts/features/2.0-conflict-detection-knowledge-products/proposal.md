# Proposal: Conflict Detection & Knowledge Products

## 💡 The Problem

The RAG system does not check for contradictions among retrieved documents, potentially presenting conflicting information as a single unified answer without alerting the user. Additionally, the system lacks Notebook LM-like "Studio" features to auto-generate structured synthesis products (Study Guides, Briefing Docs, FAQs, Glossaries, Timelines, and Flashcards) for a given collection, forcing users to write manual synthesis queries.

## 🎯 Objectives

1. **Source Conflict Checking:** Establish a post-processing verification step to programmatically detect contradictions in retrieved chunks and verify if they are accurately represented in generated responses.
2. **Studio Knowledge Products:** Introduce endpoints to generate structured study and summary materials on-demand for any collection.

## 🛠 High-Level Approach

- **Conflict Detection:** Add a post-generation verification step inside `ChatService` using an LLM-as-a-judge check. The evaluation result will be stored in `chat_turns.metadata_json` and exposed in `ChatTurnResponse`.
- **Knowledge Products:** Add `POST /collections/{collection_id}/generate/...` endpoints that fetch summaries from `documents.metadata_json` (doc_understanding metadata generated in Tier 1) and feed them to targeted LLM prompts to construct structured Markdown or JSON.

## ⚠️ Known Constraints / Risks

- **LLM Latency:** Running a post-processing conflict check adds a sequential LLM call, increasing turn latency. We will mitigate this by executing the check only when retrieved chunks span more than one unique document.
- **Context Limits:** Concatenating raw text of large collections for study guides will cause context exhaustion. We mitigate this by building products from pre-computed document summaries.

## 🧩 Gray Areas Resolved

- **Database Schema Preservation:** Instead of migrating database tables to add conflict columns, we store conflict traces in `chat_turns.metadata_json` and read them dynamically.
- **Answer Failures:** If a contradiction is detected but the LLM answer missed it, we do not block or retry generation (which would double latency/cost); instead, we flag `conflict_status: "unresolved_conflict"` and show a warning in the frontend.
- **Knowledge Product Storage:** We do not persist knowledge products in SQLite; they are generated on-the-fly and returned as raw Markdown or JSON.

## ✅ Success Criteria

- [ ] Standard pytest suite covering the new conflict checker and generation service.
- [ ] Endpoints return well-formatted Markdown for document synthesis products.
- [ ] Flashcards endpoint returns a parseable JSON array of Question/Answer pairs.
- [ ] Integration tests verify that `conflict_status` triggers when sources contain opposing claims and the answer fails to address the conflict.

---
**Status:** 🟢 Aligned

# Proposal: Deep Inspectability and Playground

## 💡 The Problem
While the application can return answers with citations, users currently lack a way to deeply inspect the exact context used by the LLM or to directly compare how different retrieval strategies affect the results for a single query. This limits the educational and experimental value of the RAG Knowledge Base Lab.

## 🎯 Objectives
1. Provide a "Citation Detail View" to allow users to inspect the exact chunk text, metadata, and parent context behind a specific citation.
2. Introduce a "Strategy Comparison Playground" where users can run a single query against two different retrieval configurations side-by-side to visually compare the retrieved chunks and generated answers.

## 🛠 High-Level Approach
*   **Citation Details:** Enhance the Chat UI to support clicking citation tags. This will open a modal displaying the raw text and metadata of the `chunk_id` referenced by that citation.
*   **Playground UI:** Create a new React view containing two independent chat/retrieval panels.
*   **Execution Strategy:** To maintain simplicity and reduce backend complexity, the Playground will reuse the existing `POST /chat` API endpoint by making two simultaneous requests from the frontend, each with its own specific advanced configuration override.
*   **Diffing Logic:** The Playground will use strict `chunk_id` matching to highlight which chunks are common between the two strategies and which are unique, providing clear visual feedback.
*   **Configuration Scope:** The first version of the Playground will focus on comparing combinations of: Retrieval Mode (Keyword/Semantic/Hybrid), HyDE, and Query Expansion.
*   **Persistence:** Playground sessions will be transient scratchpads; they will not be saved to the database.

## ⚠️ Known Constraints / Risks
*   **UI Complexity:** Rendering two full chat/retrieval results side-by-side on smaller screens might be challenging; responsive design consideration is needed.
*   **API Load:** The Playground effectively doubles the load on the backend and external APIs (OpenAI) for every comparative query run.

## ✅ Success Criteria
- [ ] Users can click a citation in the chat to view the exact chunk text and score in a modal.
- [ ] Users can navigate to the Playground, configure two different strategies (e.g., Semantic vs. Hybrid + HyDE), and see the side-by-side results for a single query.
- [ ] The Playground highlights retrieved chunks based on their uniqueness or overlap between the two strategies using strict `chunk_id` matching.

---
**Status:** 🟢 Aligned
*(Spec creation in progress)*

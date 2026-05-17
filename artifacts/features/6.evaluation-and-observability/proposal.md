# Proposal: Deep Observability and Basic Evaluation

## 💡 The Problem
Reviewers and developers need to "see inside" the RAG pipeline to understand why a specific answer was generated. Additionally, a lightweight way to verify that changes haven't broken core functionality (using a small, standard set of questions) is needed without the overhead of a full experimentation platform.

## 🎯 Objectives
- **X-Ray Visibility:** Real-time inspection of retrieval chunks, prompts, and pipeline logic via an integrated UI toggle.
- **Sanity Checking:** A UI-triggered "Basic Eval" that runs 10-20 "golden" test cases and reports Groundedness and Retrieval Recall.
- **Traceability:** Use a simple JSON-based dataset for managing test cases.

## 🛠 High-Level Approach
- **Observability Layer:** Instrument the backend to return "trace" metadata (chunks, prompt, logic) alongside chat responses. Add a "Debug Mode" toggle to the frontend chat screen.
- **Basic Eval Runner:** Create a backend service that iterates through a JSON dataset of questions/answers and uses an LLM-as-a-judge to score them.
- **UI Reporting:** Add an "Evaluation" section to the UI to trigger the run and display pass/fail results for the 10-20 cases.

## ⚠️ Known Constraints / Risks
- **Descope:** All batch experimentation, regression history, and strategy-comparison dashboards are moved to a future feature (Feature 9 or similar).
- **Latency:** Running LLM-based evaluations (Groundedness) takes time; the UI must handle the "running" state gracefully.

## ✅ Success Criteria
- [ ] Users can toggle a "Debug View" on the chat screen to see raw chunks and the final prompt for the last message.
- [ ] Users can trigger a "Sanity Check" run from the UI.
- [ ] The system reports Groundedness and Recall scores for 10-20 test cases stored in a JSON file.

---
**Status:** 🟢 Aligned

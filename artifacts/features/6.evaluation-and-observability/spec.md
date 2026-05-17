# Feature Specification: Evaluation and Observability

## Metadata

- Feature name: Evaluation and Observability
- Feature slug: evaluation-and-observability
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-17
- Related knowledge artifact(s): `prd-requirement.md`

## Problem Statement
Users and reviewers need to "see inside" the RAG pipeline to understand why a specific answer was generated. Additionally, a lightweight way to verify that changes haven't broken core functionality is needed without the overhead of a full experimentation platform.

## Desired Outcomes
- **Deep Observability:** Users can inspect the raw data (chunks, prompt, logic) behind any chat response in real-time.
- **Basic Evaluation:** Users can run a quick "Sanity Check" on 10-20 core scenarios to verify groundedness and retrieval recall.

## Success Criteria
- **SC-001:** A "Debug Mode" toggle in the Chat UI exposes raw retrieval chunks and the final LLM prompt.
- **SC-002:** A "Sanity Check" feature in the UI executes 10-20 test cases from a JSON file and displays pass/fail results.
- **SC-003:** Every chat response includes metadata tracing the selected strategy and retrieval scores.

## In Scope
- **Debug Visibility (X-Ray):** Integrated toggle in the chat interface to show internal pipeline state.
- **Basic Eval Runner:** UI-triggered script for running a small "golden" dataset.
- **LLM-as-a-Judge:** Simple integration to score "Groundedness" for the 10-20 test cases.
- **JSON Dataset Management:** Storing and reading test cases from `backend/test_data/eval_dataset.json`.

## Out Of Scope
- Large-scale batch evaluations (>20 cases).
- Historical experiment tracking and regression charts.
- Strategy-comparison dashboards.
- Cost/Token tracking across multiple sessions (moved to Feature 10).

## User Stories
- **US-001:** As a developer, I want to toggle "Debug Mode" so I can see if the correct document was retrieved for my query.
- **US-002:** As a reviewer, I want to run the "Sanity Check" to see if the system still correctly answers the 10 most important questions.
- **US-003:** As a user, I want to see the "X-Ray" of an answer to understand the citations better.

## Functional Requirements

### REQ-001: Debug Visibility Toggle
The Chat UI must include a toggle that, when enabled, displays an "X-Ray" or "Debug" panel for each message showing:
- **Retrieved Chunks:** Raw text, similarity scores, and source document metadata.
- **Final Prompt:** The exact text sent to the LLM (including context injection).
- **Pipeline Logic:** The active retrieval strategy (e.g., "Semantic + HyDE") and routing decisions.

### REQ-002: UI-Triggered Sanity Check
The UI must provide a way (e.g., an "Evaluation" tab or button) to:
- Trigger an execution of the "Golden Dataset."
- Display a progress indicator (since LLM scoring takes time).
- Show a tabular report of Question, Pass/Fail status, Groundedness Score, and Recall.

### REQ-003: LLM-as-a-Judge for Groundedness
The backend must implement a scoring function that:
- Uses an LLM to compare the generated answer against the retrieved chunks.
- Returns a "Groundedness" score (0-1) and a short reasoning.

### REQ-004: JSON Dataset Support
The system must read test cases from a JSON file with the following structure:
```json
[
  {
    "id": "case-001",
    "question": "What is the return policy?",
    "expected_document_id": "doc_123",
    "ground_truth_answer": "Returns are accepted within 30 days."
  }
]
```

## Non-Functional Requirements
- **NFR-001 (Latency):** The Debug Mode metadata should be returned in the same API call as the chat response to avoid extra round-trips.
- **NFR-002 (UI Feedback):** The "Sanity Check" must handle async execution so the UI doesn't freeze while waiting for 20 LLM calls.

## Acceptance Criteria
- [ ] AC-001: Toggling "Debug Mode" reveals raw chunk text and similarity scores for the last 3 chat turns.
- [ ] AC-002: Clicking "Run Sanity Check" executes all cases in `eval_dataset.json` and shows a list of results.
- [ ] AC-003: The "Final Prompt" view in the debug panel shows exactly how the context was formatted for the LLM.

# Design: Evaluation and Observability (Narrowed Scope)

## Metadata
- Feature: Evaluation and Observability
- Related Spec: `artifacts/features/6.evaluation-and-observability/spec.md`
- Implementation Phase: 1 (Observability & Basic Eval)

## 1. Technical Goals
- **Real-time X-Ray:** Expose internal pipeline metadata (retrieval transformations, scores, prompts) to the frontend.
- **Async Sanity Check:** Allow users to trigger a lightweight evaluation of 10-20 "golden" test cases and view results in the UI.
- **LLM-as-a-Judge:** Implement a robust groundedness scorer using the LLM.

## 2. Backend Architecture

### 2.1 Trace Instrumentation
The `ChatTurnResponse` schema already supports `retrieval_trace` and `safety_trace`.
- **AdvancedRetrievalService:** Already populates `RetrievalTrace`.
- **SafetyService:** Already populates `SafetyTrace`.
- **GroundingService (Update):** Will be updated to include an LLM-based `check_groundedness(answer, chunks)` method.

### 2.2 Evaluation Service (`backend/chat/evaluation.py`)
A new service to manage the sanity check workflow:
- **Load Dataset:** Reads `backend/data/eval_dataset.json`.
- **Execute cases:** Iterates through cases. For each case, it calls a lightweight version of `ChatService.process_turn` (bypassing persistence if needed, but ideally using the same logic).
- **Calculate Recall:** Check if `expected_document_id` (from JSON) matches any retrieved chunk's `document_id`.
- **Calculate Groundedness:** Uses the updated `GroundingService`.

### 2.3 API Endpoints
- **Existing:** `POST /api/chat/sessions/{id}/turns` (Returns trace data in response).
- **New:** `POST /api/chat/evaluate/sanity-check`
  - Triggers the run.
  - Returns: `List[EvalResult]` where `EvalResult` includes question, answer, recall, groundedness, and reasoning.

## 3. Frontend Architecture

### 3.1 Chat UI (X-Ray Panel)
- **Toggle:** A "Debug Mode" switch in the chat settings or header.
- **Visuals:** When enabled, an expandable "X-Ray" icon appears next to each bot message.
- **Panel Content:**
  - **Retrieval:** Show rewritten query, expanded queries, and a list of chunks with scores.
  - **Logic:** Show active strategy (Baseline vs Expansion vs HyDE).
  - **Prompt:** A "View Full Prompt" expandable section.

### 3.2 Evaluation Screen
- **Route:** `/evaluation`.
- **Interaction:** A "Start Sanity Check" button.
- **Feedback:** Progress bar (X / 20 cases).
- **Results:** A modern table showing Question, Status (Pass/Fail), Recall (%), and Groundedness Score.

## 4. Data Model
`backend/data/eval_dataset.json`:
```json
[
  {
    "id": "q1",
    "question": "How do I setup a virtualenv?",
    "expected_document_id": "python-setup-guide",
    "ground_truth_answer": "Use python -m venv .venv"
  }
]
```

## 5. Security & Privacy
- Trace data is only returned to the user in the session.
- Ensure system prompts shown in "X-Ray" don't expose API keys or sensitive backend logic (though this is a learning lab, so transparency is generally good).

## 6. Known Trade-offs
- **LLM Latency:** Running 20 groundedness checks sequentially will be slow (~20-40 seconds). We should consider parallelizing the calls in the backend evaluation runner.

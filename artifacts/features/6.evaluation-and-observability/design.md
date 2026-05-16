# Design: Evaluation and Observability

## 1. Overview
This feature introduces a structured evaluation framework to measure the quality of the RAG pipeline. It includes a backend runner for batch evaluations, an "LLM-as-a-judge" service for semantic metrics, and a frontend dashboard for experiment comparison and dataset management.

## 2. Data Models

### 2.1 Evaluation Dataset (`eval_dataset.json`)
Stored in `backend/data/eval/datasets/`.
```json
{
  "id": "default",
  "name": "Core RAG Benchmark",
  "cases": [
    {
      "id": "case-001",
      "question": "What is RAG?",
      "expected_answer": "Retrieval-Augmented Generation (RAG) is the process of optimizing LLM output by referencing an authoritative knowledge base...",
      "expected_document_ids": ["doc-123"],
      "tags": ["baseline", "fact-lookup"]
    }
  ]
}
```

### 2.2 Evaluation Run (`run_<timestamp>.json`)
Stored in `backend/data/eval/runs/`.
```json
{
  "id": "run-20260516-120000",
  "dataset_id": "default",
  "config": {
    "retrieval_mode": "hybrid",
    "enable_hyde": true,
    "top_k": 5
  },
  "metrics_summary": {
    "avg_groundedness": 0.85,
    "avg_relevance": 0.9,
    "recall_at_k": 0.75,
    "latency_ms": 1200
  },
  "results": [
    {
      "case_id": "case-001",
      "actual_answer": "...",
      "retrieved_chunk_ids": ["chunk-1", "chunk-2"],
      "metrics": {
        "groundedness": { "score": 1.0, "reason": "The answer is directly supported by the retrieved chunks." },
        "relevance": { "score": 1.0, "reason": "The answer accurately addresses the question." },
        "hit": true
      },
      "trace_id": "trace-abc-123"
    }
  ]
}
```

## 3. Component Architecture

### 3.1 `EvaluationService` (Backend)
- `run_evaluation(dataset_id, config)`: Iterates through cases, calls `ChatService.process_turn`, and collects results.
- `calculate_metrics(results)`: Aggregates per-case metrics into a summary.
- `save_run(run_data)`: Writes to JSON.

### 3.2 `JudgeService` (Backend)
- `evaluate_groundedness(answer, chunks) -> (score, reason)`
- `evaluate_relevance(answer, question) -> (score, reason)`
- Uses specific prompt templates in `backend/chat/prompts.py`.

### 3.3 API Endpoints
- `GET /api/eval/datasets`: List datasets.
- `POST /api/eval/datasets`: Update dataset JSON.
- `POST /api/eval/run`: Trigger an evaluation run.
- `GET /api/eval/runs`: List past runs.
- `GET /api/eval/runs/{run_id}`: Get run details.

### 3.4 UI Dashboard
- **Dataset Tab:** Monaco-style editor (or plain textarea) for editing the JSON dataset.
- **Runs Tab:** List of past runs with summary metrics.
- **Run Detail View:** Table of cases, highlighting failures and showing "Judge Reasoning".
- **Comparison View:** Side-by-side selection of two runs to compare metrics and per-case deltas.

## 4. LLM-as-a-Judge Strategy
We will use a "Chain-of-Thought" prompting approach for the judge:
1.  **Groundedness:** Ask the LLM to identify specific sentences in the answer and map them to retrieved chunks. If a sentence has no mapping, the score drops.
2.  **Relevance:** Ask the LLM to evaluate if the answer satisfies the user's intent without adding extraneous info.

## 5. Implementation Considerations
- **Concurrency:** Evaluation runs should be handled asynchronously (using a background task) to avoid blocking the API.
- **Cost Control:** Limit the number of cases per run by default (e.g., 20) to prevent accidental token spend.
- **Trace Persistence:** While runs are JSON files, they should link to `RetrievalTrace` objects (which are already returned by `ChatService`). We may need to save these traces as part of the run JSON.

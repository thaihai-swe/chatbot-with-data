# Feature Specification

## Metadata

- Feature name: Advanced Metrics and Reporting
- Feature slug: advanced-metrics-and-reporting
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16
- Related knowledge artifact(s): `prd-requirement.md`

## Problem Statement
While the current evaluation system provides LLM-based quality scores, it lacks the mathematical rigor required for production RAG systems (MRR, nDCG) and fails to track operational overhead like token usage and cost, making it difficult to justify strategy trade-offs.

## Desired Outcomes
- Users can view precise mathematical retrieval metrics.
- Users can track the token usage and estimated cost for different retrieval and generation strategies.
- Users can export evaluation results for offline sharing and reporting.

## Success Criteria
- [ ] SC-001: The system calculates and displays MRR (Mean Reciprocal Rank) and Precision@k for every evaluation run.
- [ ] SC-002: Token usage is tracked for every LLM call and aggregated in the run summary.
- [ ] SC-003: Users can export an evaluation run as a CSV or PDF report.

## In Scope
- Implementation of mathematical retrieval metrics: MRR, Precision@k, nDCG.
- Implementation of Token Usage tracking across the Chat and Judge services.
- Aggregated Cost Estimation logic in the backend.
- CSV/PDF Export functionality in the Evaluation Dashboard.

## Out Of Scope
- Fine-grained billing or multi-model cost comparison (beyond estimation).
- Modifying the core retrieval logic (this feature only measures it).

## User Stories
- **US-001:** As a researcher, I want to see the Mean Reciprocal Rank (MRR) of my retrieval strategies to understand how well they rank the ground-truth documents.
- **US-002:** As a budget-conscious user, I want to see the total token usage per evaluation run so I can optimize my strategies for cost-efficiency.

## Functional Requirements

### REQ-001: Mathematical Retrieval Metrics
The system must calculate MRR, nDCG, and Precision@k based on the `expected_document_ids` provided in the evaluation dataset.

### REQ-002: Token Usage Tracking
The system must capture token usage metadata (prompt, completion, total) from the OpenAI API responses and store them in the `EvaluationResult` and `RetrievalTrace`.

### REQ-003: Reporting & Export
The Evaluation Dashboard must provide buttons to export a run summary and per-case results to CSV or PDF.

## Acceptance Criteria
- [ ] AC-001: Every evaluation run includes a "Rank Accuracy" section in the UI showing MRR.
- [ ] AC-002: The run summary shows "Total Tokens Used" and "Estimated Cost ($)".
- [ ] AC-003: Clicking "Export CSV" downloads a file containing all test cases and their associated metrics.

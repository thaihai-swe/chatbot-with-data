# Proposal: Evaluation and Observability

## 💡 The Problem
The current RAG system works but lacks a quantitative way to measure quality improvements or regressions. Users cannot easily compare different retrieval strategies (like HyDE vs. baseline) using a standardized dataset, and the "educational" aspect of the project is limited by the lack of transparent, explainable metrics for answer quality.

## 🎯 Objectives
- Enable users to run repeatable evaluation suites against a standardized dataset.
- Provide explainable, LLM-based metrics (groundedness, relevance) that serve as learning artifacts.
- Allow side-by-side comparison of experiment runs to justify architectural choices.

## 🛠 High-Level Approach
1.  **Evaluation Runner:** A backend service that iterates through a JSON-based dataset (question/ground-truth pairs) and executes the RAG pipeline for each case.
2.  **LLM-as-a-Judge:** Implement custom, prompt-based metrics for groundedness and relevance, returning both a score and a "reasoning" block to educate the user.
3.  **JSON-per-run Storage:** Store evaluation results as individual JSON files on the filesystem for simplicity and portability.
4.  **UI Integration:** 
    - A dedicated **Evaluation Dashboard** to view/edit the dataset (as JSON) and trigger runs.
    - A toggleable **Chat-Level Metrics** view, allowing users to see real-time evaluation of their live chat turns.
    - **Experiment Comparison** to view the metrics of different runs side-by-side.

## ⚠️ Known Constraints / Risks
- **LLM Cost/Latency:** Running evaluations and custom judge prompts will increase token usage and latency.
- **Judge Reliability:** LLM-based judges can be inconsistent; prompts must be carefully engineered for reliability.
- **File Management:** As the number of runs grows, a flat directory of JSON files may become harder to navigate (mitigated by naming conventions).

## ✅ Success Criteria
- [ ] Users can trigger an evaluation run from the UI and see a summary of scores (Recall@k, Groundedness, Relevance).
- [ ] Users can view the internal "reasoning" of the LLM judge for any failed or low-scoring case.
- [ ] Users can toggle "Live Evaluation" on/off in the Chat UI.
- [ ] Users can view and edit the evaluation dataset JSON directly in the browser.

---
**Status:** 🟡 Awaiting Alignment
*(Move to 🟢 Aligned once user approves this proposal)*

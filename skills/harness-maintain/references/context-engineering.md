# Context Engineering

Managing the agent's context budget is critical for long-running tasks. Overloading the context leads to hallucinations and lost instructions.

## 1. Progressive Disclosure
*   Do not dump all rules into the main prompt or a single giant `AGENTS.md`.
*   Use `AGENTS.md` as a short router (< 50 lines) that points the agent to specific, deeper documentation when needed.
*   Load repo memory before raw code: constitution, harness config, security policy, knowledge base, and learned heuristics.

## 2. Just-In-Time (JIT) Loading
*   Instruct the agent to load only the artifacts relevant to the immediate task.
*   If working on Task 3, load the `plan.md` section for Task 3, not the entire plan and `spec.md` history.

## 3. Context Condensation
*   When approaching context limits, deliberately pause and summarize.
*   Replace full artifact content in the working memory with concise summaries.

## 4. Avoiding Context Pollution
*   Do not load massive log files, generated build artifacts, or irrelevant feature files into the context window unless explicitly needed for debugging.
*   Prefer durable generated references such as `docs/project/code-map.md` over repeated broad codebase reads.

## 5. Subagent Delegation
*   Offload broad exploration (e.g., "Find all usages of function X") to a subagent.
*   The main agent only receives the concise result, keeping its primary context focused on execution.

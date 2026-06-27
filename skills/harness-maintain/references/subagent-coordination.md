# Subagent Coordination

When tasks are complex, a single agent context becomes a bottleneck. Harnesses use subagent patterns to distribute load.

## 1. Subagent Delegation
*   **Exploration:** Use a research subagent to search the codebase and summarize findings.
*   **Execution:** Delegate repetitive or highly constrained tasks to an implementation subagent.
*   **Review:** Use a verification subagent to red-team the implementation against the spec.

## 2. Specialization Workflows
*   Pass the baton systematically: Researcher → Planner → Implementer → Reviewer.
*   Each role uses a specific public command or skill contract.

## 3. Context Partitioning
*   Ensure each agent only receives the context it needs. The implementer doesn't need the early brainstorming from the spec phase; it only needs the final `tasks.md`.

## 4. Merge Protocols
*   Define how subagent work is integrated.
*   If multiple subagents generate code, the main agent must merge it systematically, resolving conflicts, rather than blindly applying patches.

## 5. Conflict Resolution
*   If subagents provide conflicting information or fail, the main agent is responsible for identifying the discrepancy and either re-prompting or asking the human for clarity.

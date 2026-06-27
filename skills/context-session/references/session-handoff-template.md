# Handoff Template (Harness Edition)

This template is the harness-aware handoff produced by `context-session`.

### Session Details
*   **Session ID/Timestamp:** [UUID or Date]
*   **Feature & Phase:** [Slug] / [Phase]

### Current State
*   **Tasks Completed This Session:** [List IDs and evidence]
*   **Tasks Remaining:** [List IDs and dependencies]
*   **Active Blockers:** [List any]
*   **Active Delegations & Subagents:** [List subagent Conversation IDs, roles, target tasks, current status, and branched workspace URIs if any]

### Continuity Context
*   **Locked Decisions:** [Key choices from `spec.md` that must not be overturned]
*   **Context Condensation Summary:** [What was loaded, what was pruned. E.g., "Summarized research on auth module, dropped raw logs."]
*   **Loaded Context Tiers:** [Router | Repo Memory | Architecture | Feature Artifacts | Raw Code | Transient Logs]
*   **Evicted As Stale:** [Raw logs, superseded plan sections, broad listings, etc.]

### Next Steps
*   **Next Step Prompt:** [A copy-pasteable prompt for the user to start the next session, e.g., "Please resume implementation on Task 4, focusing on the database migration."]

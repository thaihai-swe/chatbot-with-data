# Skills

This directory holds the agent capability contracts. Each subdirectory (except `_shared/`) ships a `SKILL.md` that is the canonical behavioral spec for one slash command. References, templates, and examples for each skill live under its `references/` directory and are loaded on demand.

## Index

### Lifecycle

- [`starter-init`](starter-init/SKILL.md) — Initialize a project for harnessed agentic development. Detects repo type (greenfield / brownfield) and automatically runs an archaeology sweep (Phase A) before bootstrap (Phase B) when the repo has existing code, tests, CI, or history.
- [`spec-research`](spec-research/SKILL.md) — Investigate a problem, feature area, bug, or brownfield subsystem and produce one bounded analysis artifact grounded in repository evidence. Use when root cause is unknown or current behavior must be mapped first.
- [`spec-requirements`](spec-requirements/SKILL.md) — Define the "What & Why" of a feature. Handles specification authoring, Socratic refinement to resolve ambiguity, and a built-in readiness review to ensure requirements are testable and complete before planning.
- [`spec-plan`](spec-plan/SKILL.md) — Design the technical solution and sequence execution. Handles architectural design, implementation planning, task breakdown, and automated traceability from requirements to tasks.
- [`spec-implement`](spec-implement/SKILL.md) — Execute implementation work task-by-task. Uses the approved spec, plan, and task list to drive code changes with strict status tracking and validation.
- [`spec-adr`](spec-adr/SKILL.md) — Create or evaluate an architecture decision record (ADR). Use when choosing between technologies, documenting design trade-offs, or reviewing system proposals.
- [`harness-verify`](harness-verify/SKILL.md) — Verify implemented work against the spec and plan. Handles split verification modes, mechanical gates, implementation reviews (via `code-review`), optional fallow-pass cleanup, manual testing guides, and final closeout authority.

### Context & memory

- [`context-session`](context-session/SKILL.md) — Manage the session lifecycle (start, checkpoint, end) to maintain context continuity, assemble context deliberately, budget context windows, and generate durable handoffs.
- [`context-status`](context-status/SKILL.md) — Orchestrate and report on the status of all active features. Meta-skill that gives a high-level view of progress, blockers, and next steps across the repository.
- [`context-memory`](context-memory/SKILL.md) — Create, maintain, and route durable repository memory. Manages `MASTER_INDEX.md`, the constitution, security policy, learned heuristics, the project knowledge base, and the post-ship knowledge sync after `harness-verify` passes.
- [`context-compact`](context-compact/SKILL.md) — Compress oversized memory files while preserving critical rules and architectural constraints.

### Quality & docs

- [`code-review`](code-review/SKILL.md) — Perform code review following Google's Engineering Practices. Evaluates code health, design, functionality, complexity, testing, naming, and style.
- [`ponytail`](ponytail/SKILL.md) — Enforce the "lazy senior dev" ladder before writing code. Reviews diffs for over-engineering, trims bloated abstractions, and ensures maximum use of platform-native features.
- [`harness-maintain`](harness-maintain/SKILL.md) — Evaluate, construct, or repair an agent harness across seven core subsystems (Instructions, State, Verification, Scope, Lifecycle, Security, Context Engineering), including evaluation architecture and failure-driven improvement from observability findings.
- [`codebase-documenter`](codebase-documenter/SKILL.md) — Generate comprehensive codebase documentation covering architecture, components, data flow, setup, deployment, and contributing — produces a multi-file doc set.
- [`technical-docs`](technical-docs/SKILL.md) — Create technical documentation including HTTP/REST API contracts, end-to-end event and logical workflow flows, system boundaries, and actor interactions. Supports mode-based routing (api, flow, both).

### Visualization

- [`visualize`](visualize/SKILL.md) — Create a technical diagram (architecture, data flow, flowchart, sequence, agent/memory, UML, or concept map) and export it as SVG and/or Mermaid.

## Shared references

`_shared/` holds cross-skill references — status phases, doc conventions, and the diagram catalog. It is exempt from the SKILL.md rule. See [`_shared/README.md`](_shared/README.md).

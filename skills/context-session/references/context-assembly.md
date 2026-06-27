# Context Assembly Rules

`context-session` owns how working context is assembled, compacted, and trimmed during long-running feature work.

## Context Tiers

Load context from highest-signal to lowest-signal:

1. **Router**
   - `AGENTS.md` — runtime instruction router (always loaded)
   - `MASTER_INDEX.md` — master context routing index and memory router (always loaded)
   - Purpose: locate the workflow contract, repo entry rules, and the memory map
2. **Repo Memory — Always**
   - `memories/repo/core-policies.md`
   - Purpose: durable normative rules, security policy, and memory promotion thresholds needed every session
3. **Repo Memory — By Intent**
   - Resolve by matching the active task against trigger keywords listed in `MASTER_INDEX.md`.
   - **Config group** (`memories/repo/harness-config.md`) — loaded when the task touches setup, bootstrap, install, repository identity, commands, session defaults, lifecycle, or known limits.

   - **Knowledge group** (`project-knowledge-base.md`) — loaded when the task touches patterns, conventions, stack, or domain language.
   - **Learned group** (`learned-heuristics.md`) — loaded when the task echoes a heuristic trigger (recurring instinct, "we always/never", "last time").
   - **Architecture group** (`docs/project/architecture.md`, `docs/project/adr/index.md`, `docs/project/code-map.md`) — loaded when the task crosses module boundaries or the repo is unfamiliar.
   - **Debug group** (`memories/repo/harness-telemetry.md`, prior `session-extracts.md`) — loaded only on debug, retro, failure, or post-mortem work.
   - Purpose: durable knowledge, but loaded by relevance, not by default. Skip groups whose triggers do not match.
4. **Feature Artifacts**
   - `status.md`, `handoff.md`, `progress.md`
   - relevant `spec.md`, `plan.md`, `tasks.md`, `review.md`
   - Purpose: the current feature contract and exact execution state
5. **Raw Code**
   - only the files needed for the immediate task or failing proof surface
   - Purpose: implementation and debugging evidence
6. **Transient Logs**
   - command output, grep results, stack traces, browser traces
   - Purpose: short-lived debugging evidence that should be summarized quickly

## Assembly Order

1. Load tier 1 on every session start. Read `MASTER_INDEX.md` before loading any other memory file.
2. Load tier 2 (Always group) on every session start.
3. Load tier 3 by intent — match the task against `MASTER_INDEX.md` trigger keywords and load only the groups that hit. Record which groups were loaded and which were skipped in `progress.md` or the session opener.

4. Load tier 4 before editing or verifying anything.
5. Load tier 5 just-in-time for the current task.
6. Load tier 6 only when needed to prove or debug behavior.

## Intent Routing Rules

- A group loads when any of its trigger keywords or semantic concepts conceptually appear in the user request, the active feature `spec.md`, or the active `tasks.md` row.
- **Semantic Trigger Evaluation:** Evaluate the task requirements. If they align conceptually with architecture patterns, API contracts, codebase constraints, or previous heuristics, trigger the load even if literal keyword matching is absent.
- When the task is genuinely cross-cutting, load multiple groups but state which and why.
- When no by-intent group matches conceptually, proceed with the Always tier only and record "no by-intent groups matched" in the session opener — silent skipping is not allowed.
- If `MASTER_INDEX.md` is missing or stale, fall back to loading every memory file and route the gap to `context-memory` for index repair.

## Confidence-Scored Loading

- Count keyword matches between the active task and a group's trigger keywords (declared in `MASTER_INDEX.md`).
- **0–2 matches (low confidence)**: partial-load via `scripts/context-loader.py <file> --mode summary`.
- **3+ matches (high confidence)**: full-load the file.
- **Semantic match allowed**: if the file's core purpose matches the task intent even without literal keyword overlap, treat as high confidence.

## Compaction Triggers

Compact or checkpoint when any of these are true:

- more than 3 raw tool outputs are still in active context
- the active task changed and prior task details are no longer needed
- verification failed and the full log is longer than the immediate proof surface
- the loaded context includes artifacts for tasks not currently in progress
- the session has run long enough that the next action is less obvious than the last summary

## Stale-Context Eviction Rules

Evict or summarize these first:

- full grep/file listings after the findings are recorded
- superseded plan sections and resolved open questions
- old failing logs once the root cause or active symptom is captured
- raw generated files when a codemap or reference summary exists
- design alternatives that were rejected and already recorded in ADRs or plans

Never evict:

- current task ID and acceptance target
- locked product or technical decisions still affecting execution
- active blockers
- last known verification state
- repo-wide guardrails from `core-policies.md`

## Output Expectation

When compaction happens, preserve:

- current task and phase
- latest proof status
- blockers or risks
- files currently in scope
- what was pruned and where the durable summary now lives

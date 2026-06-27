---
id: skill-spec-implement
name: spec-implement
description: "Execute implementation work task-by-task. Uses the approved spec, plan, and task list to drive code changes with strict status tracking and validation."
tags: ['spec', 'implementation', 'delivery']
triggers: ['implement', 'code', 'build', 'deliver']
next_skill: 'harness-verify'

---
# Kit Implement

## Overview

Use this skill to perform the coding work. Follow `artifacts/features/<slug>/tasks.md` , execute one approved task at a time, and keep task state and proof honest. Answers: can I complete the selected task and prove it without inventing new scope?

## I/O Hand-off Protocol
- **Reads**: `artifacts/features/<slug>/plan.md`, `artifacts/features/<slug>/tasks.md`, `artifacts/features/<slug>/spec.md`, `memories/repo/harness-telemetry.md`, `docs/rules/ponytail.md`.
- **Writes**: Source code, `artifacts/features/<slug>/tasks.md` (to mark tasks done), `artifacts/features/<slug>/status.md`, `memories/repo/harness-telemetry.jsonl`, `.corezero/sessions/<slug>/progress.md`, `artifacts/features/<slug>/session-extracts.md` (candidate-only; promoted by `/context-memory` post-ship-sync).
- **Next Skill**: `/harness-verify`

> **Note on Artifact Responsibilities**:
> - `tasks.md` is strictly for machine-readable task checklists and validation evidence (parsed by the dashboard).
> - `progress.md` is for free-form human-readable session logs, daily blockers, and developer notes.

## Workflow

1. **Initialization**: Run `bash scripts/harness/phase-gate.sh <slug> "Implementing"` to verify preconditions. If the circuit breaker blocks (2+ consecutive gate failures), return to `/spec-plan` to re-approve before retrying. Update `artifacts/features/<slug>/status.md` phase to `Implementing`.
2. **Resumption Check**: (If resuming mid-task) Read the last entry in `.corezero/sessions/<slug>/progress.md` to identify the interrupted task. Re-run the task's proving command from pre-flight. If the proving command now fails, treat the task as not started: reset its status to `Pending` and restart from Step 3.
3. **Select Task**: Choose the first unblocked task ID (e.g., `TASK-001`) from `artifacts/features/<slug>/tasks.md`. Declare the target task before coding.
4. **Status Update**: Mark the task `In Progress` in `tasks.md`.
5. **Pre-Flight Baseline**: Read the task requirements. **Run the task's validation/proving command once in the terminal before editing** to establish a baseline. If files don't exist, create skeleton files first.
6. **Coding & Provenance**: Implement code and tests within the task boundary. Follow `rules/` (including `ponytail.md` for simplicity) and guidelines in `references/implementation-standards.md`.
    - **Decision Provenance**: If implementation requires a design decision not covered in `spec.md` or `plan.md` (e.g., swapping a library), stop coding. Route to `/spec-adr` if architectural. For minor choices: append a `## Decision Record` block to `.corezero/sessions/<slug>/progress.md` (choice, reason) before writing code. Do not implement undocumented mid-flight decisions silently.
    - **Proof Policy**: Satisfy planned proof surfaces. If the plan mandates tests, implement them.
    - **Parallel Execution**: Tasks marked `[P]` may be implemented in parallel by subagents. Ensure they have no shared mutable state before delegating.
7. **Mechanical Validation**: Re-run the local task proof to verify passes. Then, run `bash scripts/harness/gate-runner.sh` for all mechanical validation. If the gate fails:
    - Pipe the output into `bash scripts/harness/telemetry-collector.sh --task <TASK-NNN> --feature <slug>` to log a JSONL record.
    - The gate-runner automatically increments the circuit-breaker counter. At ≥2 consecutive failures, the phase-gate blocks Verifying until the plan is re-approved.
    - Resolve the root cause before retrying.
8. **Logging & Close**: Add validation evidence (e.g. test outputs) to `tasks.md`. Mark task `Done` and explicitly toggle the `- [ ]` markdown checkbox to `- [x]` in the task list. Update `.corezero/sessions/<slug>/progress.md` with session notes.
9. **Lesson Capture**: Check if any non-trivial design/approach decisions were made during this task that weren't in `plan.md`. If so, append a `[CANDIDATE]` entry to `artifacts/features/<slug>/session-extracts.md` documenting the decision and rationale for later memory promotion.
10. **Telemetry Update**: When a failure is resolved and a fix applied, close the telemetry record: `bash scripts/harness/telemetry-update.sh --id <OBS-NNN> --status closed --fix-applied "Fixed in <commit/PR>"`. This sets recurrence_risk based on fix quality.
11. **Next Step**: If tasks remain, continue `/spec-implement`. If complete, update the `Implementation complete` checkbox in `status.md` to `[x]`, and hand off to `/harness-verify`. If issues arise (scope break, planning gaps), stop and route to `/spec-plan`.

## Anti-Patterns

- **Vibe Coding**: Writing code without declaring the target task first. Every edit must be scoped to a declared task.
- **Silent Scope Creep**: Fixing unrelated lint issues or refactoring adjacent code during a task. Stick to the task boundary.
- **Ignoring Gate Failure**: When `gate-runner.sh` fails, the circuit breaker counts it. Fix the root cause before retrying — don't just re-run hoping it passes.
- **Skipping Pre-Flight**: Not establishing a baseline before editing. If the test was already red, you can't prove your change fixed it.
- **No Telemetry**: Gate failures that aren't logged via `telemetry-collector.sh`. The circuit breaker tracks consecutive failures, but telemetry provides the diagnostic record for `/harness-maintain`.
- **Parallel Without Isolation**: Running `[P]` tasks in parallel without verifying they touch disjoint files/code. Shared mutable state causes conflicts.
- **Context Overload**: Keeping raw test output and gate logs in context. Summarise and evict per the Context Eviction rule.

## Core Rules
- **No "Vibe Coding"**: Stick strictly to task scopes.
- **Stop at Scope Breaks**: If a requirement is missing or contradictory, return to `/spec-plan` instead of doing work-around coding.
- **Heuristic Citation**: If your implementation applies a learned heuristic from `learned-heuristics.md`, cite its LH-* ID in `.corezero/sessions/<slug>/progress.md` (SHOULD).
- **Ponytail Rule**: Maintain the lazy senior dev mindset. Never over-engineer. Use the standard library and native features before adding dependencies or custom code.
- **Minimum Viable Context (MVC)**: JIT-load only the specific files required for the current task. Do not load the entire codebase into context.
- **Circuit Breaker Awareness**: ≥2 consecutive gate failures blocks Verifying. Re-approve the plan to reset.
- **Context Eviction**: After running `gate-runner.sh`, you MUST summarize the raw terminal logs and evict the raw output from your context window to conserve token budget.

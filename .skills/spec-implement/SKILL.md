---
name: spec-implement
description: Execute approved implementation work from artifacts/features/<slug>/tasks.md using spec.md and plan.md as source-of-truth context. Use when the next unblocked task, or a selected set of task IDs, is ready to implement with dependency checks, task status updates, scoped code changes, test-first validation for behavior changes, and traceability back to requirements and acceptance criteria.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Spec Implement

## Overview

Use this skill to execute implementation work for a feature from its approved artifacts.

This skill implements from `tasks.md`, with `plan.md` and `spec.md` as governing context. It owns task-by-task execution, status tracking, validation, and scope discipline.

## Read First

Read these inputs when they exist:

- `artifacts/features/<slug>/tasks.md`
- `artifacts/features/<slug>/plan.md`
- `artifacts/features/<slug>/spec.md`
- `artifacts/features/<slug>/design.md`
- `artifacts/features/<slug>/analysis.md`
- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `references/tasks-template.md` to confirm the expected task block and status fields
- the files being changed plus the direct callers, interfaces, tests, configs, and docs that make the change risky

## When to Use

Use this skill when the user needs to:

- implement the next unblocked task from `tasks.md`
- implement specific task IDs from `tasks.md`
- update task status while work progresses
- make code and test changes that satisfy the approved spec, plan, and task list

Do not use this skill for:

- inventing work directly from chat intent
- repairing weak upstream specs, plans, or task lists by guessing
- silently broadening scope beyond the selected task

If the selected task is not actually executable, route back to the blocked upstream artifact instead of compensating in code.

## Preconditions

Do not proceed unless these are true:

- `tasks.md` exists and contains executable tasks with dependencies
- `plan.md` exists and defines the technical approach and phase sequence
- `spec.md` exists and defines requirements and acceptance criteria
- the selected task exists and is executable
- dependencies and prerequisites are already satisfied

If no task is explicitly selected, default to the first unblocked task in sequence.

## Stop Conditions

Stop and explain what blocks execution when any of these are true:

- `spec.md`, `plan.md`, or `tasks.md` is missing
- task dependencies prevent execution
- the selected task is ambiguous, contradictory, or too broad
- plan prerequisites are not yet in place
- implementation would contradict the approved spec, plan, or constitution
- the task turns out to be materially larger, more cross-cutting, or more ambiguous than described

When stopping, identify:

- which task or prerequisite is blocked
- what upstream artifact or decision must change
- why implementation cannot proceed safely

## Core Rules

- Work from `tasks.md`, not vague chat intent.
- Respect phase order, task dependencies, and resume notes.
- Execute one task at a time by default.
- Parallelize only when tasks are marked `[P]`, have no shared file boundaries, have no data or dependency conflicts, and have explicit ownership or reintegration notes.
- Implement only what the selected task describes.
- Add tests and validation during implementation, not afterthought.
- Surface upstream defects instead of working around them silently.
- Read the code you are changing and the relevant surrounding boundaries before editing.
- Reuse repository patterns that are already visible in the codebase unless the approved artifacts explicitly require a new direction.
- When behavior changes, write or update the targeted failing test first unless the task is strictly non-behavioral.
- Verify the failing test fails for the expected reason before relying on it as proof.
- Prefer minimal code that satisfies the task and its tests over speculative cleanup or extra features.
- Do not claim completion from plausible code alone; fresh verification evidence is required.
- If the repo starts from a dirty or unstable baseline that affects the task, say so explicitly before continuing.
- If implementation review later disproves a `Done` task, reopen it immediately instead of leaving misleading task state behind.

## Task Status Protocol

Update `tasks.md` immediately as task state changes.

Before starting a task:

- keep the checkbox unchecked: `- [ ]`
- change `Status:` from `Not Started` to `In Progress`

After validation passes:

- change the checkbox from `- [ ]` to `- [X]`
- change `Status:` from `In Progress` to `Done`

If blocked:

- keep the checkbox unchecked
- change `Status:` to `Blocked`
- record the reason in `Session note:`

If work is intentionally postponed rather than blocked:

- keep the checkbox unchecked
- change `Status:` to `Deferred`
- record the deferral reason in `Session note:`

If a completed task must be reopened after review or failed follow-up validation:

- change the checkbox from `- [X]` back to `- [ ]`
- change `Status:` from `Done` to `In Progress` or `Blocked`
- record the reason in `Session note:`

Do not batch these updates. Change task status at the moment work starts and at the moment validation completes.

## References

- Use [references/tasks-template.md](references/tasks-template.md) as the bundled definition of the expected task block structure.
- Keep checkbox state, `Status:`, and `Session note:` aligned with that template.

## Scope Discipline

If implementation reveals that a task is materially larger, more ambiguous, or more cross-cutting than the task list says:

1. Stop.
2. Describe the mismatch between the task and reality.
3. Recommend revisiting `tasks.md` or upstream artifacts.
4. Do not silently expand the implementation slice.

## Source-Grounded Implementation

Before editing:

- read the selected task and its linked requirements and acceptance criteria
- inspect the touched files and the immediate boundaries that consume or depend on them
- match established repository patterns when they already solve the problem
- if repository reality contradicts the task assumptions, stop and route back upstream instead of inventing a local workaround

## Verification Discipline

Before claiming a task is done:

- identify which command or commands prove the task outcome
- run those commands fresh after the change
- read the full output rather than inferring success from partial signals
- base the task status on observed evidence, not confidence
- keep the task open when review findings or failed follow-up checks still contradict the claimed outcome

Examples of acceptable evidence include targeted tests, relevant integration tests, lint or typecheck runs, and other repository quality gates that actually prove the task outcome.

## Workflow

1. Validate that the required artifacts and prerequisites exist.
2. Select the next unblocked task, or confirm the user-selected task IDs are executable.
3. Update the task status in `tasks.md` to `In Progress`.
4. Inspect the touched files and relevant surrounding boundaries before editing.
5. If the task changes behavior, write or update the most targeted failing test first and verify it fails for the expected reason.
6. Implement only the scoped task outcome.
7. Add or update any additional tests and validation needed for that task.
8. Run the proving verification commands and confirm the task outcome matches its linked requirements and acceptance criteria.
9. Mark the task `Done` immediately after validation passes, or `Blocked` with a reason if it cannot complete.
10. Run implementation review when the slice is ready for review.
11. If review finds local issues, reopen the task, fix them, rerun the proof, and only then return it to `Done`.
12. Update resume context in `tasks.md` before moving on.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The task is a little vague, but I can fill in the gap." | Silent gap-filling is how scope drift and broken traceability start. |
| "I'll update task status after everything passes." | Task state must reflect reality as work progresses, not after the fact. |
| "The code looks correct, so the proof can be minimal." | Completion requires fresh relevant evidence, not confidence. |

## Red Flags

- implementation is being driven from chat instead of `tasks.md`
- behavior changed but no failing proof or targeted validation exists
- task state claims `Done` while review or validation still contradicts that claim
- the change introduces patterns not grounded in the repository or approved artifacts

## Verification

Before marking a task done, verify:

- the code change stayed inside the selected task boundary
- test-first behavior was followed when the task changed behavior
- the code change was grounded in the repository files and interfaces actually touched by the task
- any parallel execution assumptions remained safe
- verification was fresh and directly relevant to the task
- task state would still be truthful if another agent reviewed it immediately
- no hidden scope expansion or unrecorded blocker remains

## Self-Review

Before marking the task done, verify:

- implementation matches the task description
- relevant tests and repo quality gates were run when applicable
- changed behavior still aligns with `spec.md`, `plan.md`, and the selected task
- evidence exists for the linked acceptance criteria
- task status in `tasks.md` matches the actual verification outcome

Use the repository’s `task-traceability-audit` skill when available to confirm the selected task still traces cleanly to requirements, acceptance criteria, and validation.

## Output Rules

- Produce code and test changes only for the selected executable task scope.
- Update task status in `artifacts/features/<slug>/tasks.md` as work progresses.
- Do not mark tasks done without validation.
- Do not proceed when upstream artifacts are missing, contradictory, or too weak to execute safely.

---
name: aiddk-implement
description: Execute implementation work task-by-task. This skill uses the approved spec, plan, and task list to drive code changes with strict status tracking and validation.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Kit Implement

## Overview

Use this skill to perform the coding work. You must follow `tasks.md` and update its state as you progress.

## Read First

- `artifacts/features/<slug>/status.md`
- `tasks.md`
- `plan.md`
- `spec.md`
- `references/design-standards.md`
- Files being touched + their callers/interfaces.

## When to Use

- Implement the next unblocked task from `tasks.md`.
- Update task status while work progresses.
- Make code and test changes that satisfy the approved spec and plan.

## Workflow

1. **Initialization:** If `status.md` exists, set phase to `Implementing`.
2. **Select:** Pick the exact next unblocked task ID from `tasks.md`. Say which task you are executing before coding.
3. **Pre-Flight:** Read the task, linked requirements, linked acceptance criteria, and touched callers/interfaces. Record the exact proving command or proof target before editing.
4. **Status:** Mark the task `In Progress` before making code changes.
5. **RED First (when behavior changes):** Run the failing test or proof first. If there is no named failing proof, stop and tighten the task or plan.
6. **Code:** Implement only the selected task. Match project patterns.
7. **Validate:** Re-run the exact proving command or proof required by the task.
8. **Close:** Add validation evidence and session notes to `tasks.md`. Mark the task `Done` only after validation passes. Update `status.md` with progress.

## Stop Conditions

- `spec.md`, `plan.md`, or `tasks.md` is missing.
- Task dependencies prevent execution.
- Implementation would contradict the approved spec or plan.

## Core Rules

- **No "Vibe Coding":** Only implement what is in the task.
- **Exact Task Discipline:** Do not work from "Task 1" or "the auth task." Always use the exact task ID.
- **Proof Before Code:** Name the proving command or proof target before editing. For behavior changes, get a RED result first whenever practical.
- **TDD (Red-Green-Refactor):** For behavioral changes, write/update a failing test first. Ensure it fails (RED) before making it pass (GREEN).
- **Caveman Mode (Token Efficiency):** During technical execution turns, use ultra-concise communication (minimal filler, bullet points) to maximize context window utility.
- **Traceability:** Every code change must trace back to a task ID.
- **Evidence-Based:** "Done" means validation evidence exists.
- **No Silent Task Switching:** If the selected task uncovers missing upstream work, stop and return to planning instead of quietly doing extra tasks.
- **Anti-AI Slop:** For UI/UX tasks, follow `design-standards.md` strictly. No generic defaults.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The task is a little vague, but I can fill in the gap." | Silent gap-filling is how scope drift starts. |
| "I'll update task status after everything passes." | Task state must reflect reality as work progresses. |

## Red Flags

- Implementation is being driven from chat instead of `tasks.md`.
- The agent cannot state the proving command before editing.
- A behavior-changing task has no RED proof.
- Task state claims `Done` while validation still fails.

## Verification

Before marking a task done, verify:
- The code change stayed inside the selected task boundary.
- Test-first behavior was followed for behavioral changes.
- Verification was fresh and directly relevant to the task.
- `tasks.md` now includes the passing validation evidence for that task.

## Output Rules

- Produce code and test changes only for the selected task scope.
- Update task status in `tasks.md` as work progresses.
- Update the task's validation evidence and session note before moving on.
- Do not mark tasks done without validation.

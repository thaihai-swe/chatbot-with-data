---
name: aiddk-handoff
description: Package the current project state for the next agent session. This skill prevents context loss by creating a durable bridge (handoff.md) that summarizes work done, blockers, and the next immediate prompt.
compatibility: Designed for all Agent Skills-compatible tools to manage session transitions.
metadata:
  author: spec-driven-development-kit
---

# Kit Handoff

## Overview

Use this skill when you are reaching context limits, ending a long work session, or passing the project to a different agent. It generates a `handoff.md` artifact in the feature's artifact folder.

The result should be skim-friendly and actionable in under a minute.

## Read First

- `artifacts/features/<slug>/status.md`
- `tasks.md`
- `plan.md`
- `spec.md`
- Current implementation status (git status/diff).

## When to Use

- Ending a working session.
- Nearing the LLM's context window limit.
- Switching to a different agent model (e.g., from Research to Implement).

## Workflow

1. **Status Sync:** Read `status.md` to ensure the handoff reflects the current phase and blockers.
2. **Inventory:** Check `tasks.md` for completed, in-progress, blocked, and next-unblocked task IDs.
3. **State Check:** Record the current working tree or validation state if it matters to the next step.
4. **Analysis:** Identify active blockers, unresolved ambiguities, and failed attempts worth preserving.
5. **Draft:** Populate `references/handoff-template.md` with the shortest useful summary of the current state.
6. **Finalize:** Write the content to `artifacts/features/<slug>/handoff.md`. Update `status.md` with the handoff reference if necessary.
7. **Prompt:** Provide the user with the "Next Step Prompt" found in the handoff.

## Stop Conditions

- No feature slug is identified (cannot determine output path).
- The current work state is too volatile to summarize (try to reach a checkpoint first).

## Core Rules

- **No Amnesia:** The handoff must contain enough detail that the next agent doesn't need to re-read the entire history.
- **Actionable Next Step:** Always include a specific, copy-pasteable prompt for the user to start the next session.
- **Skimmable In 60 Seconds:** Prefer exact task IDs, files, commands, and blocker statements over narrative summaries.
- **Validation State Matters:** If work stopped before proof passed, say that directly.
- **Blocker Transparency:** Explicitly call out why work stopped (e.g., "Waiting for user clarification on X").

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The next agent will just read the code." | Reading code doesn't explain *intent* or *failed attempts*. |
| "I'll just summarize in the chat." | Chat history is transient; `handoff.md` is durable. |

## Red Flags

- Handoff contains vague statements like "Work is progressing."
- The next step still requires guessing which file, task, or command to use.
- No "Next Step Prompt" is provided.

## Verification

Before finalizing the handoff, verify:
- All completed tasks in `tasks.md` are correctly reflected.
- The "Next Step Prompt" actually references the next task in the plan.
- The handoff states whether validation is complete, incomplete, or failing.
- The file path follows the `artifacts/features/<slug>/handoff.md` convention.

## Output Rules

- Create or update `artifacts/features/<slug>/handoff.md`.
- Provide the final "Next Step Prompt" as the last message of the session.

---
id: skill-context-session
name: context-session
description: "Manage session start, checkpoint, and end handoffs for an existing feature."
tags: ['context', 'session', 'startup']
triggers: ['session', 'start', 'checkpoint', 'context']
next_skill: 'context-memory'

---
# Context Session

## Overview
Used to resume, checkpoint, or close work for an existing feature slug. This skill is for session boundaries after `artifacts/features/<slug>/status.md` exists; new feature intake starts with `/spec-requirements` or `/spec-research`.

## Modes

| Mode | Use When | Primary Outputs |
|---|---|---|
| `START` | Starting a new day, switching branches, or opening a new chat window. | Readiness summary with loaded context, current phase, next task, blockers. |
| `CHECKPOINT` | Pausing before a break or after meaningful progress. | Updated `progress.md` with session notes. |
| `END` | Handoff to another developer/agent or closing a long session. | `handoff.md`, `progress.md` notes, and candidate `session-extracts.md` entries. |

`END` is required for long sessions because chat history is volatile. It is not the only mode.

## I/O Hand-off Protocol
- **Reads**: `AGENTS.md`, `MASTER_INDEX.md`, feature `status.md`, `tasks.md`, `.corezero/sessions/<slug>/progress.md`, optional `.corezero/sessions/<slug>/handoff.md`, and routed memory files.
- **Writes**: `.corezero/sessions/<slug>/progress.md`, `.corezero/sessions/<slug>/handoff.md`, optional `artifacts/features/<slug>/session-extracts.md`, and telemetry pruning updates when required.

> **Note on Artifact Responsibilities**:
> - `tasks.md` is strictly for machine-readable task checklists and validation evidence (parsed by the dashboard).
> - `progress.md` is for free-form human-readable session logs, daily blockers, and developer notes.

## Workflow

### Session Start
1. **Slug Check**: If multiple features exist, run `/context-status` first to select the active slug.
   **First-run path**: If `.corezero/sessions/<slug>/` does not exist, create it. If `.corezero/sessions/<slug>/progress.md` does not yet exist (first session after `/spec-requirements` created the slug), create it from `references/progress-template.md` before loading context. Skip the Resumption step (Step 4) and go directly to Step 5 (Report & Log).
2. **Context Load**: Load minimum required context per `references/context-assembly.md` and `references/session-start-flow.md`. When reading `MASTER_INDEX.md`, strictly obey the **Confidence-Scored Loading** rule: if ≤2 keywords match a group, perform a **partial-load** (load only the index/header file for that group). Only load the full group for high-confidence matches (3+ keywords).
3. **Resumption**: Identify current phase, next task/artifact, and blockers. Read `.corezero/sessions/<slug>/handoff.md` if it exists to pick up from the previous session.
4. **Report & Log**: Update `.corezero/sessions/<slug>/progress.md` with resumption details and name the exact next core command.

### Session Checkpoint
1. Review completed tasks. Append a snapshot or session notes to `.corezero/sessions/<slug>/progress.md`.
2. Check context budget. If crowded, run condensation/eviction per `references/context-condensation.md`. Prune raw logs and broad searches.

### Session End
1. Summarize completion state, proof status, and blockers.
2. **Delegation**: Document Conversation ID, role, and branch URIs for active subagents.
3. **Log & Extract**: Append end entry to `.corezero/sessions/<slug>/progress.md`. Extract lessons to `artifacts/features/<slug>/session-extracts.md`:
   - `Complex` complexity: **Required**. Document at least 3 candidate lessons.
   - `Moderate` complexity: **Required** when reusable lessons exist. Document "no extractable lessons" explicitly if none.
   - `Simple` complexity: Optional. Candidates can be brief or omitted.
4. **Handoff**: Write `handoff.md` to `.corezero/sessions/<slug>/handoff.md` using `references/session-handoff-template.md`, ending with the next core command.


## Stop Conditions

- `starter-init` has not been run (no `AGENTS.md` or `memories/repo/harness-config.md` present).
- No feature slug is selected or `artifacts/features/<slug>/status.md` does not exist yet. In plain terms: status.md does not exist yet for this feature. Route to `/spec-requirements` when requirements can be defined directly, or `/spec-research` when brownfield behavior or root cause is unknown.
- At session start, if running the test command from `memories/repo/harness-config.md` `## Verification Commands` exits non-zero: surface the broken baseline to the user and stop. Do not load feature context over a broken build. Session Honesty requires surfacing this, not hiding it.

## Preconditions

- **Required files**: `AGENTS.md`, `memories/repo/core-policies.md`.
- **Required feature state**: Existing `artifacts/features/<slug>/status.md` created by `/spec-requirements` or `/spec-research`.
- **Phase sets**: Manages lifecycle across existing feature phases.

## Core Rules

- **No Amnesia**: The progress log is the system of record. Update it mid-session and on end.
- **Session Honesty**: Never hide a broken build or failing test in handoffs.
- **Tiered Assembly**: Read `MASTER_INDEX.md` first, load only by-intent groups relevant to the active task.
- **Evict Stale Context**: Prune old logs/files once analyzed. Keep context window lean.

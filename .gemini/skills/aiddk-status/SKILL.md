---
name: aiddk-status
description: Orchestrate and report on the status of all active features. This meta-skill acts as a project manager, providing a high-level view of progress, blockers, and next steps across the repository.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use artifacts/features/.
metadata:
  author: spec-driven-development-kit
---

# Kit Status

## Overview

Use this skill to get a bird's-eye view of the repository's active work.

It handles:
1. **Repository Health:** Scanning all `artifacts/features/` for `status.md` files.
2. **Progress Reporting:** Summarizing the current phase of every active feature.
3. **Blocker Identification:** Highlighting any active blockers or open questions.
4. **Next-Step Guidance:** Recommending the exact `/aiddk-[skill]` command to move each feature forward.

## Read First

- `artifacts/features/**/status.md`

## When to Use

- Start a new session to see where things left off.
- Get a summary of all active work for a status update.
- Identify which features are blocked and why.

## Workflow

1. **Discovery:** Find all directories in `artifacts/features/`.
2. **Parsing:** Read the `status.md` (and `handoff.md` if relevant) in each directory.
3. **Synthesis:** Create a summary table showing:
   - Feature Slug
   - Current Phase
   - Last Updated
   - Blockers (Yes/No)
4. **Detailing:** For each feature, provide a 1-line summary of the "Next Step" as defined in its `status.md`.
5. **Guidance:** If a feature is missing a `status.md`, recommend running `/aiddk-spec` (or the appropriate initialization skill) to fix the process drift.

## Stop Conditions

- No features found in `artifacts/features/`.

## Core Rules

- **Process First:** Call out features that are drifting from the SDD workflow.
- **Actionable:** Every feature summary must include a recommended next command.
- **Concise:** Keep the high-level report brief; only go into detail when blockers are present.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The status doesn't matter if the code is getting done." | Status is the bridge between agents and sessions; without it, context is lost. |
| "I'll update the status after I finish the PR." | Status must be updated at every skill boundary to prevent drift. |

## Red Flags

- Feature directories exist without a `status.md`.
- Features are marked `Done` but missing verification evidence.
- The "Next Step" command is missing or logically incorrect for the current phase.

## Verification

Before finalizing the report, verify:
- All active feature folders were scanned.
- The "Next Step" commands are syntactically correct (e.g., `/aiddk-plan`).
- Blockers are clearly highlighted.

## Output Rules

- Produce a summary report in the chat.
- Do not modify any files.

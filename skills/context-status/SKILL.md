---
id: skill-context-status
name: context-status
description: "Orchestrate and report on the status of all active features. This meta-skill acts as a project manager, providing a high-level view of progress, blockers, and next steps across the repository."
tags: ['context', 'status', 'report']
triggers: ['status', 'report', 'overview', 'progress']
next_skill: 'harness-maintain'

---
# Context Status

## Overview
Aggregates status across all active feature branches, updates the repo-wide status dashboard, and synchronizes the active task phase.

## I/O Hand-off Protocol
- **Reads**: `memories/repo/harness-telemetry.md`, `artifacts/features/*/status.md`, `artifacts/features/*/tasks.md`.
- **Writes**: `memories/repo/harness-telemetry.md` `# Current State` section, command line status dashboard.

## Workflow
1. **Load Current State**: Read `memories/repo/harness-telemetry.md` to load the current global phase and failure counters.
2. **Scan Features**: Scan all feature subdirectories under `artifacts/features/` and read their respective `status.md` and `tasks.md` files. Identify:
   - Feature slug name.
   - Active phase (`## Current Phase`).
   - Complexity (`## Complexity`).
   - Current active task (`## Active Task`).
   - Blockers or open clarification flags (`## Blockers`).
   - Task completion percentage (from `tasks.md`).
   *Note: If `status.md` does not strictly follow the sections in `skills/_shared/status-template.md`, the dashboard parser will fail. Flag any malformed status files.*
3. **Compile Dashboard**: Format a text-based status dashboard using `references/status-report-template.md` containing:
   - A list of all active features, their current phase, and active task.
   - Any currently active blocker flags.
   - Current failure logs summary.
4. **Update Current State**: If the active feature slug or current task phase has changed, write the updated `# Current State` values to `memories/repo/harness-telemetry.md`.
5. **Regenerate HTML Dashboard**: You MUST run `python3 scripts/generate-dashboard.py` to sync status to `docs/generated/dashboard.html`.
6. **Feature Completion Cleanup (GC)**: If `status.md` shows `## Current Phase: Done`:
   - Check if `artifacts/features/<slug>/session-extracts.md` has been triaged (look for `<!-- triaged: true -->`).
   - If NOT triaged: emit a warning in your final response — "session-extracts.md for <slug> has not been triaged. Run /context-memory before cleanup." Do NOT delete files.
   - If triaged (or missing): delete `.corezero/sessions/<slug>/progress.md` and `.corezero/sessions/<slug>/handoff.md`. If `.corezero/sessions/<slug>/` is empty, remove the directory.
   - Do NOT delete durable artifacts (`spec.md`, `plan.md`, `status.md`, etc.).
   - Log the cleanup: `bash scripts/harness/telemetry-collector.sh --task system --feature <slug>` with classification "maintenance" and description "Feature completion GC: removed ephemeral artifacts."

## Core Rules
- **No Stale Statuses**: Always run context-status to sync telemetry state when a feature transitions to a new phase or completes a task.
- **Accurate Aggregation**: Do not guess feature statuses. If `status.md` is missing for a feature directory, mark its phase as `[UNKNOWN]`.

## Read First

Read this skill thoroughly before invoking it.

## When to Use

Use this skill for its designated purpose within the delivery flow.

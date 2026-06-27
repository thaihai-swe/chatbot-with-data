---
id: skill-harness-maintain
name: harness-maintain
description: "Maintain harness configuration, assess health, and self-improve from telemetry."
tags: ['harness', 'maintenance', 'health']
triggers: ['maintain', 'health', 'assess', 'improve']
next_skill: 'spec-adr'

---
# Harness Maintain

## Overview
Administrative tools to assess harness health, repair missing state, and evolve rules based on telemetry logs. The harness is evaluated across seven core subsystems: Instructions, State, Verification, Scope, Lifecycle, Security, and Context Engineering. See `references/assessment-rubric.md` for the full scoring model.

## I/O Hand-off Protocol
- **Reads**: Entire codebase, `memories/repo/`, `manifest.json`, `harness-telemetry.md`.
- **Writes**: `docs/generated/harness-assessment.md`, `memories/repo/learned-heuristics.md`, `docs/project/code-map.md`, `docs/generated/dashboard.html`.

## Modes

When invoking this skill, you must specify one of the following modes:

| Mode | Trigger | Focus |
|---|---|---|
| **assess** | `assess` | Generates a health report checking memory sizes, stale references, and orphaned artifacts. |
| **create** | `create` | Scaffolds missing harness directories or files. |
| **improve** | `improve` | Self-healing: reads telemetry logs and drafts new heuristics/rules from failures. |
| **eval** | `eval` | Validates internal consistency of CC-* rules, manifest, and harness scripts. |
| **doctor** | `doctor` | The "fix it" mode. Runs assess + regenerates stale codemaps and dashboard. |

## Workflow

### 1. Assess Mode (`assess`)
1. Read all files in `memories/repo/`. Count line lengths. Flag any file > 600 lines as a warning, > 800 lines as a critical compaction risk.
2. Check for orphaned feature artifacts (e.g., a directory in `artifacts/features/` with no `status.md`).
3. Check for missing required sections in `memories/repo/core-policies.md`.
4. Output a structured health report to `docs/generated/harness-assessment.md`.

### 2. Create Mode (`create`)
1. Read the health report or system baseline.
2. Scaffold any missing standard directories (e.g., `memories/domain/`, `docs/generated/`).
3. Create missing placeholder files if they were accidentally deleted.

### 3. Improve Mode (`improve`)
1. Read `memories/repo/harness-telemetry.md` `## Entries`.
2. Find all `open` entries (OBS-*) where `promotion_candidate: true`.
3. For each candidate, draft a new rule or heuristic that would prevent the failure.
4. Append the draft to `memories/repo/learned-heuristics.md` clearly marked as `[DRAFT]`.
5. Update the `## Trend Summary` table in `harness-telemetry.md`.
6. Set the entry status to `promoted`.
7. **Rule**: Never finalize a `[DRAFT]` rule without explicit user review.

### 4. Eval Mode (`eval`)
1. Verify all `CC-*` identifiers defined in `memories/repo/core-policies.md` are present and sequential.
2. Run `scripts/harness/gate-runner.sh` (or `gate-runner.local.sh` if it exists) and capture output to verify stack detection.
3. Compare `manifest.json` against the actual file tree to catch drift.

### 5. Doctor Mode (`doctor`)
1. Run Assess steps to check for structural health.
2. Check for broken markdown file links inside `skills/**/*.md`.
3. Regenerate `docs/project/code-map.md` with the updated repository hierarchy.
4. Run `python3 scripts/generate-dashboard.py` to regenerate the HTML dashboard.
5. Report what was fixed and what still requires manual intervention.

## Core Rules
- **No Silent Promotion**: Improve mode drafts rules but the user must approve them.
- **Audit Before Ship**: Every package release requires running Eval mode to ensure manifest consistency.

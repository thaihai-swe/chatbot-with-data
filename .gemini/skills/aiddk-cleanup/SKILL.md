---
name: aiddk-cleanup
description: Perform surgical refactoring, dead-code removal, or orphan cleanup after a feature implementation. This "Fallow Pass" ensures the repository remains clean and maintainable.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools.
metadata:
  author: spec-driven-development-kit
---

# Kit Cleanup (The Fallow Pass)

## Overview

Use this skill to perform surgical refactoring and cleanup.

It handles:
1. **Orphan Cleanup:** Removing unused imports, variables, and functions created during implementation.
2. **Technical Debt Grooming:** Refactoring "just-in-case" abstractions into simpler forms.
3. **Comment Sanitization:** Removing "TODO" notes and obsolete documentation.
4. **Tool-Driven Cleanup:** Running `lint --fix`, `format`, and other repository health tools.

## Read First

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `artifacts/features/<slug>/tasks.md`
- Files modified in the last feature wave.

## When to Use

- Immediately after a feature is verified and marked `Done`.
- During a dedicated "Cleanup" sprint.
- Removing unused imports, variables, or functions.

## Workflow

1. **Inventory:** Identify all files touched in the recent feature implementation.
2. **Orphan Hunt:** Use static analysis (or grep) to find unused code introduced in those files.
3. **Execution:** Apply surgical changes to remove debt and orphans.
4. **Tool Pass:** Run the project's standard linter and formatter.
5. **Validation:** Run the full test suite to ensure no behavior was broken during cleanup.

## Stop Conditions

- The change requires a behavior modification (use `aiddk-spec` instead).
- The cleanup target is too broad for a single surgical session.

## Core Rules

- **Zero Behavior Change:** If the tests fail after cleanup, the cleanup was too aggressive.
- **Campground Rule:** Always leave the code cleaner than you found it.
- **Surgical:** Touch only what is necessary; do not perform "drive-by" refactors of unrelated code.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll just fix this bug while I'm cleaning up." | Cleanup should never change behavior. Stop and use `aiddk-spec`. |
| "A little refactor in this adjacent file won't hurt." | Surgicality is the rule. Touch only the debt identified in the inventory. |

## Red Flags

- The change includes logic modifications or behavioral shifts.
- Unrelated files are touched during the cleanup.
- Tests fail after the cleanup wave.

## Verification

Before finalizing the cleanup, verify:
- Behavior remains identical (All tests pass).
- No new linting or type-checking errors were introduced.
- Dead code identified in the inventory phase has been removed.

## Output Rules

- Apply only the minimum changes needed for cleanup.
- Provide a summary of "Debt Removed" to the user.

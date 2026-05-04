---
name: refactor-cleaner
description: Remove dead code, duplicate code, unused exports, and stale dependencies with a conservative, evidence-based cleanup workflow. Use when the goal is bounded refactoring or cleanup rather than new feature work, especially when safety depends on proving code is truly unused before deleting or consolidating it.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in repositories where cleanup must be verified against real references, tests, and public API risk.
metadata:
  author: spec-driven-development-kit
---

# Refactor Cleaner

## Overview

Use this skill for conservative cleanup and consolidation work.

This skill owns dead-code removal, duplicate consolidation, and unused dependency cleanup. It does not own feature development, speculative rewrites, or broad architectural redesign.

## Read First

Read these inputs when they exist:

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- related feature artifacts when the cleanup is tied to a specific feature
- relevant package manifests, lockfiles, lint or type-check configs, and test commands
- the files being cleaned and the callers that depend on them

Prefer repository evidence over tool output alone.

## When to Use

Use this skill when the user needs to:

- remove dead code, unused exports, stale files, or unused dependencies
- consolidate obvious duplicate utilities, modules, or components
- reduce cleanup debt after behavior has already stabilized
- verify whether suspected dead code is actually safe to delete

Do not use this skill for:

- active feature development where scope is still changing
- major redesigns that need `spec-requirement`, `spec-design`, or `spec-plan`
- cleanup justified only by style preference
- deleting code that may be part of a public or externally consumed API without explicit confirmation

If the cleanup turns into behavior change, route back to the spec-driven workflow instead of smuggling the change through refactoring.

## Stop Conditions

Stop and explain exactly what is blocking safe cleanup when:

- there is no practical validation path for the affected area
- the code may be part of a public API, plugin surface, template contract, or documented extension point
- dynamic loading, reflection, code generation, string-based lookups, or runtime configuration make usage uncertain
- the requested cleanup is mixed with unrelated feature work and cannot be reviewed safely as one change
- repository evidence contradicts the cleanup tool result

When stopping, say:

- what looks removable or duplicative
- why the evidence is insufficient
- what proof or decision is needed next

## Core Rules

- Be conservative. Tool output is a lead, not proof.
- Verify every removal against real repository references before editing.
- Prefer smaller cleanup batches over one sweeping rewrite.
- Start with the safest categories first: unused imports, obviously unused local code, stale dependencies, then larger file or duplicate consolidation.
- Preserve behavior unless the user explicitly asked for a behavior change.
- Do not silently narrow or expand public API surface.
- Do not rewrite working code just to make it look cleaner.
- When duplicate code differs semantically, treat it as a design question, not automatic deduplication.
- If a cleanup changes behavior, route back to the appropriate spec-driven artifact flow instead of smuggling a feature change through refactoring.

## Evidence Sources

Use the strongest available evidence for the repository:

- direct reference search with `rg`
- imports, exports, and call sites in the codebase
- build, lint, type-check, and test results
- package-manager or language-specific cleanup tools when already available
- repository docs or public API descriptions

Helpful but non-authoritative examples include:

- `knip`
- `depcheck`
- `ts-prune`
- linter warnings about unused disable directives or imports

Do not install new tooling unless the user asked for that or the cleanup clearly depends on it.

## Risk Classification

Classify findings before changing code:

- `Safe`: local unused imports, private helpers with no references, stale dependencies confirmed by code search and existing tooling
- `Careful`: cross-module exports, duplicates with overlapping behavior, files referenced indirectly by config or conventions
- `Risky`: public APIs, generated code, framework magic, runtime string lookups, migrations, templates, or externally documented interfaces

Default to not deleting `Risky` items without stronger proof or explicit user direction.

## Workflow

1. Clarify the cleanup goal, affected area, and whether the user wants analysis only or code changes.
2. Read repo memory, relevant artifacts, and the files or modules in scope.
3. Gather candidate cleanup items from repository evidence and available analysis tools.
4. Classify candidates as `Safe`, `Careful`, or `Risky`.
5. For each candidate you intend to change, verify references, indirect usage paths, configuration hooks, and public API exposure.
6. Remove or consolidate one bounded batch at a time, starting with the safest category.
7. Run the smallest meaningful validation after each batch.
8. If validation fails, fix the root cause or revert that cleanup direction instead of forcing the result.
9. Summarize what was removed, what was intentionally left in place, and any residual cleanup candidates that need stronger proof.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The tool says it's unused, so we can delete it." | Tool output is a lead, not proof. |
| "While we're here, we should clean up the neighboring code too." | Unrelated cleanup makes the change harder to review and validate safely. |
| "It probably isn't public." | Public API risk is exactly where conservative cleanup matters most. |

## Red Flags

- cleanup batches mix dead-code removal with feature behavior changes
- deletions rely on one tool report with no repository evidence
- indirectly referenced files or config hooks were not checked

## Verification

Before finalizing cleanup, verify:

- every removal had evidence stronger than a single tool report
- validation was run after each bounded batch or at the smallest meaningful checkpoint
- public behavior and extension points were either preserved or explicitly escalated
- uncertain candidates were left documented instead of removed optimistically

## Self-Review

Before finalizing, verify:

- the cleanup stayed within the requested scope
- the final result still reads like cleanup rather than a disguised feature change
- any intentionally retained risky candidates are called out clearly
- tests, lint, or other validation match the risk of the cleanup
- the summary distinguishes what was removed from what still needs stronger proof

## Output Standard

The work is complete only when it:

- removes or consolidates code for a clear reason
- preserves intended behavior or clearly calls out approved behavior changes
- includes validation evidence proportional to the risk
- leaves high-risk uncertain cases untouched or explicitly escalated

## Output Rules

- Prefer direct code changes when the cleanup is sufficiently proven and bounded.
- If the evidence is not strong enough to edit safely, return a conservative candidate list instead of guessing.
- Keep the result reviewable. Separate unrelated cleanup categories instead of bundling them together.

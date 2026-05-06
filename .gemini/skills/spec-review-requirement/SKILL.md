---
name: spec-review-requirement
description: Review artifacts/features/<slug>/spec.md for readiness before design or planning and write artifacts/features/<slug>/requirements-review.md. Use when checking clarity, completeness, scope control, and testability without rewriting the specification in place.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Spec Review Requirements

## Overview

Use this skill to review `artifacts/features/<slug>/spec.md` and create or update `artifacts/features/<slug>/requirements-review.md`.

This skill is the readiness gate between specification authoring and downstream design or planning.

## Read First

Read these inputs when they exist:

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `artifacts/features/<slug>/spec.md`
- `references/requirements-review-template.md`

## When to Use

Use this skill when the user needs to:

- assess whether a spec is ready for design or planning
- identify blocking gaps in requirements or acceptance criteria
- capture non-blocking improvements without rewriting the spec

Do not use this skill for:

- rewriting `spec.md` directly
- producing design proposals except when pointing out a missing design decision
- implementation review

If the request is really about fixing the spec rather than judging it, route back to `spec-requirement`.

## Stop Conditions

Stop and explain what blocks a meaningful readiness review when:

- `spec.md` is missing
- the request is actually asking for a rewrite instead of a review
- the available artifact is too incomplete to judge for design or planning readiness

When stopping, say:

- what is missing
- whether the correct next step is `spec-requirement`
- why a verdict would be misleading right now

## Core Rules

- Review the spec as written.
- Be precise about defects and point to exact weak sections when possible.
- Distinguish blocking issues from non-blocking improvements.
- Focus on readiness for downstream design and planning.
- Do not silently repair the spec during review.

## References

- Use [references/requirements-review-template.md](references/requirements-review-template.md) as the bundled structure.
- Keep the verdict explicit: `ready`, `ready with minor issues`, or `not ready`.
- Make the output useful for the next authoring pass, not just judgmental.

## Workflow

1. Read the spec and any relevant repo memory.
2. Check clarity, completeness, scope boundaries, and testability.
3. Identify blocking issues that should stop design or planning.
4. Identify non-blocking improvements that would strengthen the spec.
5. Write a clear readiness verdict and concrete recommendations.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The spec is close enough; planning can fill in the blanks." | Downstream work should not invent missing requirement decisions. |
| "I can just fix the spec while reviewing it." | Review must judge the artifact as written. |
| "If the feature is urgent, the verdict can be softer." | Weak requirements stay weak regardless of urgency. |

## Red Flags

- the review rewrites the spec instead of evaluating it
- blocking ambiguity is described as a minor issue
- acceptance criteria are vague but the verdict still says ready

## Verification

Before finalizing the review, verify:

- the verdict is explicit and evidence-based
- blocking issues and non-blocking improvements are separated
- the feedback helps the next `spec-requirement` pass instead of replacing it
- readiness is judged for downstream design and planning, not general writing quality

## Output Standard

The review is ready only when it:

- gives a clear readiness verdict
- identifies blocking gaps precisely
- identifies non-blocking improvements precisely
- helps the specification improve without rewriting it in place

## Output Rules

- Update only `artifacts/features/<slug>/requirements-review.md`.
- Do not rewrite `spec.md` in this step.
- If the spec is already strong, say so clearly and briefly.

---
name: task-traceability-audit
description: Verify that implementation workflow artifacts preserve traceability from requirements through acceptance criteria, tasks, and validation. Use when generating tasks, implementing work, or reviewing delivery to check that REQ -> AC -> TASK -> validation coverage is complete and not misleading.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Task Traceability Audit

## Overview

Use this skill to verify that the implementation workflow preserves traceability from requirements through validation.

This skill audits the chain `REQ -> AC -> TASK -> validation`. It does not replace planning, task generation, implementation, or review.

## When to Use

Use this skill when the user needs to:

- verify that `tasks.md` covers the approved requirements
- check whether implementation evidence still matches the claimed task state
- audit traceability before finalizing tasks, implementation, or review

Do not use this skill for:

- inventing missing requirements or tasks
- pretending weak upstream artifacts are audit-ready
- implementation review beyond the traceability question

## Read First

Read these inputs when they exist:

- `artifacts/features/<slug>/spec.md`
- `artifacts/features/<slug>/plan.md`
- `artifacts/features/<slug>/tasks.md`
- `artifacts/features/<slug>/review.md`
- relevant validation evidence from implementation or review
- `references/audit-template.md`

## Workflow

1. Identify the feature and the artifact set being audited.
2. Check that each material `REQ-*` maps to one or more `AC-*`.
3. Check that each material `AC-*` maps to one or more `TASK-*`.
4. Check that tasks changing behavior name the validation or evidence proving completion.
5. Compare completed task state against the available validation evidence.
6. Report what is complete, what is partial, and which gaps are blocking.

## Stop Conditions

Stop and explain what blocks a meaningful audit when:

- `spec.md` or `tasks.md` is missing
- acceptance criteria are too weak to map safely
- task state or validation evidence is absent enough that the chain cannot be verified

When stopping, say:

- which part of the chain is missing
- which artifact needs repair first
- whether the gap blocks implementation, review, or closeout

## Core Rules

- Audit the artifact chain as written; do not silently repair it in place.
- Treat missing validation for completed behavior-changing tasks as a traceability finding.
- Distinguish between complete coverage, partial coverage, and misleading coverage.
- Prefer explicit task and validation references over optimistic inference.
- Route back to `spec-tasks`, `spec-implement`, or `spec-review-implementation` when the gap belongs there.

## References

- Use [references/audit-template.md](references/audit-template.md) when a structured audit record helps.
- Use [references/example-audit.md](references/example-audit.md) to calibrate complete, partial, misleading, and blocked outcomes.
- Keep the audit focused on the traceability chain rather than broad implementation judgment.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The intent is obvious even if the links are missing." | Missing links are exactly what makes future execution and review unsafe. |
| "If the code works, the traceability can wait." | Weak traceability breaks review, resumption, and maintenance. |
| "One passing test covers everything." | Validation has to prove the right requirement-task chain, not just any behavior. |

## Red Flags

- a `REQ-*` has no downstream task coverage
- an `AC-*` has no validation path
- a task is marked `Done` but no evidence proves its linked behavior
- the audit result depends on guessing which task or requirement a change belongs to

## Verification

Before finalizing the audit, verify:

- each material `REQ-*` maps to `AC-*`
- each material `AC-*` maps to `TASK-*`
- behavior-changing tasks name validation or evidence
- completed task state is supported by current evidence
- blocking and non-blocking gaps are called out separately

## Output Standard

The audit is ready only when it:

- makes the current state of the traceability chain explicit
- distinguishes blocking gaps from non-blocking gaps
- points the next repair back to the owning artifact or skill

## Output Rules

- Clearly report what part of the chain is complete, partial, or missing.
- State whether each gap is blocking or non-blocking.
- Use the template shape when a maintainer wants a reusable audit record.
- Do not rewrite the audited artifacts during the audit itself.

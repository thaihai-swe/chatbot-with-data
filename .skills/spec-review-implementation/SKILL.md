---
name: spec-review-implementation
description: Review implemented feature work against spec.md, plan.md, tasks.md, and repository quality expectations. Use when implementation has been attempted and you need an evidence-based verdict on requirement coverage, validation quality, scope control, traceability, task-state accuracy, and readiness to merge or ship.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Spec Review Implementation

## Overview

Use this skill to review implemented work for a feature against its approved artifacts and the current repository state.

This skill is the implementation quality gate. It reviews evidence, not vague intent or chat history.

## Read First

Read these inputs when they exist:

- `artifacts/features/<slug>/spec.md`
- `artifacts/features/<slug>/plan.md`
- `artifacts/features/<slug>/tasks.md`
- `artifacts/features/<slug>/design.md`
- `artifacts/features/<slug>/analysis.md`
- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `references/definition-of-done.md`

If a durable written review is useful, write or update:

`artifacts/features/<slug>/review.md`

## When to Use

Use this skill when the user needs to:

- review delivered implementation against the feature artifacts
- determine whether the feature is approved, approved with follow-ups, or changes required
- audit traceability, validation quality, and scope control after implementation
- check security-sensitive changes such as auth, permissions, secrets, data handling, or externally reachable interfaces

Do not use this skill for:

- requirement-readiness review before planning
- silently rewriting the spec, plan, or task list during review

If the change is not implementation reviewable yet, route back to `spec-implement` or the missing upstream artifact.

## Preconditions

Before review, verify:

- `spec.md`, `plan.md`, and `tasks.md` exist
- implementation work has actually been attempted
- task state is reviewable rather than obviously stale
- there is enough validation evidence to assess the delivered change

If those are not true, stop and say exactly what is missing.

## Stop Conditions

Stop and explain what blocks a meaningful implementation review when:

- required upstream artifacts are missing
- implementation has not actually been attempted
- validation evidence is too weak or stale to support a verdict

When stopping, say:

- what is missing
- whether the correct next step is `spec-implement`, `spec-tasks`, or another upstream skill
- why a review verdict would be misleading

## Core Rules

- Review the implemented work against the artifacts as written.
- Distinguish blocking issues from follow-up improvements.
- Use repository rules and stable patterns when relevant.
- Be precise about gaps, risks, regressions, and misleading task state.
- Keep the review proportional to the feature’s size and risk.
- Prefer fresh verification evidence over implementation plausibility or agent claims.
- Treat missing, stale, or weak verification as a review finding, not a paperwork issue.
- Apply a security lens when the change touches auth, permissions, secrets, data handling, external interfaces, or other security-sensitive boundaries.
- Call out when task status says `Done` but the evidence does not support that claim.
- Call out when the implementation should reopen a task instead of carrying a misleading `Done` state.
- Do not silently rewrite scope drift as “acceptable interpretation” when the implementation materially diverged from the approved artifacts.
- Re-review is normal when findings are fixed; do not treat the first review pass as the only meaningful gate.

## References

- Use [references/definition-of-done.md](references/definition-of-done.md) as a bundled checklist for closeout expectations.
- Use the repository’s `task-traceability-audit` skill when available to verify `REQ -> AC -> TASK -> validation`.
- If no issues are found, say so clearly.

## Verdict Rules

Use exactly one verdict:

- `approved`
- `approved with follow-ups`
- `changes required`

Choose `changes required` when requirements are unmet, validation is too weak for the risk, implementation materially diverges from approved scope, repo rules are violated, or task state creates meaningful operational risk.

## Workflow

1. Read the approved feature artifacts and any relevant repo memory.
2. Inspect the repository changes, tests, docs, touched files, and the current task-state evidence.
3. Identify which verification commands or artifacts actually prove the delivered behavior and prefer fresh evidence when available.
4. Check whether the change crosses security-sensitive boundaries and, if so, inspect auth, permission, secret-handling, input-validation, and externally reachable behavior explicitly.
5. Check whether any claimed `Done` task should be reopened because the evidence is stale, weak, contradicted, or missing.
6. Compare implementation against requirements, acceptance criteria, task outcomes, and repo rules.
7. Classify issues as blocking or follow-up.
8. Produce a verdict based on evidence.
9. Write `review.md` only when a durable written review is useful.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The diff looks right, so the review can be light." | Review is about evidence, not plausibility. |
| "Missing verification is just a paperwork issue." | Weak or stale evidence is a real review finding. |
| "We can leave the task as done and mention the caveat." | Misleading task state is itself an operational risk. |

## Red Flags

- the verdict depends on confidence instead of fresh evidence
- completed task state contradicts the available validation
- scope drift is excused instead of called out
- security-sensitive changes were reviewed as if they were low-risk plumbing

## Verification

Before finalizing the review, verify:

- each finding points to evidence rather than intuition
- requirement coverage, verification quality, and scope control were all checked
- security-sensitive boundaries were checked when relevant
- task-state accuracy was reviewed alongside the code changes
- any reopen-needed task state is called out clearly
- the verdict matches the severity of the findings
- absence of findings is stated explicitly when nothing material is wrong

## Self-Review

Before finalizing the review, verify:

- each finding points to evidence rather than intuition
- requirement coverage, verification quality, and scope control were all checked
- security-sensitive boundaries were checked when relevant
- task-state accuracy was reviewed alongside the code changes
- any reopen-needed task state is called out clearly
- the verdict matches the severity of the findings
- absence of findings is stated explicitly when nothing material is wrong

## Output Standard

The review is ready only when it:

- uses a clear verdict
- ties findings to evidence
- distinguishes blocking issues from follow-ups
- covers requirement coverage, validation quality, scope control, and handoff state
- identifies misleading completion claims when present
- makes misleading completion claims or stale task state visible when present

## Output Rules

- Prefer concise, evidence-based review findings.
- Use `review.md` only when a durable written review is useful.
- Do not invent universal thresholds the repository does not actually require.
- If the change is small, keep the review proportionate.

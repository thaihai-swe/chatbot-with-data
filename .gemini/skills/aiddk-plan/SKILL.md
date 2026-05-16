---
name: aiddk-plan
description: Design the technical solution and sequence execution. This skill handles architectural design, implementation planning, task breakdown, and automated traceability from requirements to tasks.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Kit Plan

## Overview

Use this skill to create `design.md`, `plan.md`, `status.md`, and `tasks.md`.

It turns an approved spec into a concrete execution strategy that an implementer can pick up cold.

## Read First

- `artifacts/features/<slug>/status.md`
- `artifacts/features/<slug>/spec.md`
- `artifacts/features/<slug>/requirements-review.md`
- `references/status-template.md`
- `references/design-template.md`
- `references/plan-template.md`
- `references/tasks-template.md`

## When to Use

- Turn an approved `spec.md` into an implementation strategy.
- Refine a task list after design changes.
- Map requirements and acceptance criteria into execution tasks.

## Workflow

1. **Initialization:** Update `status.md`. Set phase to `Planning`.
2. **Design (Optional):** Only create `design.md` when technical ambiguity or trade-offs still need resolution. If not needed, keep the plan lean and say why.
3. **First Slice First:** Identify the first releasable or risk-reducing slice before writing long-form phases.
4. **Planning:** Create `plan.md` with the execution order, impacted boundaries, proving strategy, and rollback posture.
5. **Tasking:** Decompose the plan into `tasks.md`. Each task must have an exact task ID, a bounded file or module target, explicit dependencies, and a proving command or proof target.
6. **Automated Traceability:** Verify that every `REQ-*` and `AC-*` from the spec maps to at least one task and validation step.
7. **Finalization:** Update `status.md` to show `Plan Approved`.

## Stop Conditions

- `spec.md` is missing or `requirements-review.md` is `not ready`.
- Technical constraints make the spec's goals impossible as stated.
- Sequencing depends on unresolved design choices.

## Core Rules

- **Stress-Testing:** Use a subagent to "red-team" your proposed design against the existing codebase to find hidden side effects or edge cases.
- **Stay Anchored:** Align strictly with the approved `spec.md`.
- **Lean by Default:** Do not turn `plan.md` into a second spec. Include only the detail needed to execute safely.
- **Phased Rollout:** Prefer reversible, phased changes over big-bang rewrites.
- **Validation-First:** Plan validation (tests, proofs) as part of the tasks.
- **Small Tasks:** Each task should ideally produce one reviewable diff and one clear proof.
- **Immediate Usability:** The next implementer should be able to start the first unblocked task from `tasks.md` without rereading the entire discussion.
- **Parallel Safety:** Mark tasks with `[P]` only if boundaries are truly independent.
- **Explicit Ownership:** If a task is parallel-safe, state the ownership boundary and reintegration expectations.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The implementer can figure out the rest." | Planning should remove core sequencing and approach ambiguity. |
| "Validation can be added later during coding." | Validation belongs inside the plan, not as cleanup. |

## Red Flags

- The plan is a vague brainstorm instead of an execution strategy.
- The first unblocked task still leaves core approach decisions to the implementer.
- Parallel work is implied without clear ownership boundaries.

## Verification

Before finalizing the plan, verify:
- Each phase is actionable and sequenced for safe execution.
- Validation is embedded in the plan.
- The first unblocked task is executable from `tasks.md` alone.
- Nothing in the plan requires implementation to invent core approach details.

## Output Rules

- Update only `design.md`, `plan.md`, and `tasks.md`.
- Do not update `spec.md`.
- Do not write code.

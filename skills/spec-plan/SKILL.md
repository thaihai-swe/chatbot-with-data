---
id: skill-spec-plan
name: spec-plan
description: "Design the technical solution and sequence execution. Handles architectural design, implementation planning, task breakdown, and automated traceability from requirements to tasks."
tags: ['spec', 'planning', 'tasks']
triggers: ['plan', 'task', 'breakdown', 'estimate']
next_skill: 'spec-implement'

---
# Kit Plan

## Overview
Converts an approved spec into a concrete execution strategy. Produces `plan.md` (which explicitly defines the Technical Design first) and `tasks.md` in `artifacts/features/<slug>/`. Tasks are derived from the design portion of the plan. It answers: how will we build this safely, and what task does implementation start with?

## I/O Hand-off Protocol
- **Reads**: `artifacts/features/<slug>/spec.md`, `memories/repo/harness-telemetry.md`, `docs/rules/ponytail.md`.
- **Writes**: `artifacts/features/<slug>/plan.md`, `artifacts/features/<slug>/tasks.md`, `artifacts/features/<slug>/status.md`.
- **Next Skill**: `/spec-implement`

## Workflow
1. **Initialize State**: Update the `## Current Phase` section of `artifacts/features/<slug>/status.md` to set phase to `Planning`.
2. **Design First**: You MUST write `artifacts/features/<slug>/plan.md` using `references/plan-template.md`. You must complete **Part 1: Technical Design** before defining execution phases or tasks. Read the `## Complexity` from `status.md` and choose depth for the Technical Design section:
   - **Simple**: fill only the Lightweight Design section.
   - **Moderate**: fill the Comprehensive Design section.
   - **Complex**: fill the Comprehensive Design section. If uncertainties remain, halt and invoke `/spec-research`.
   If the design reveals a contested decision with ≥2 viable approaches and material tradeoffs (e.g., build vs. buy, sync vs. async, new dependency vs. in-house), STOP. Invoke `/spec-adr` to record the decision before proceeding. Do not silently pick an approach.
   The delivery strategy (Part 2 of the plan) must pass the **Architectural Gates** (see Core Rules) and conform to `ponytail.md` guidelines.
3. **Task Breakdown**: Create `artifacts/features/<slug>/tasks.md` using `references/tasks-template.md` by breaking down the technical approach from the `plan.md`. Each task MUST be traceable to a design decision or component defined in the Technical Design. Use unique task IDs (`TASK-001`), clear targets, and specific proof validations. Mark independent, non-blocking tasks with `[P]` to indicate safe parallel execution zones.
    - **Traceability Protocol**: For each task, include a `Covers:` field referencing the REQ or AC IDs from `spec.md`.
    - **Task Granularity**: Each task should be completable in a single session (2–4 hours). If a task would take longer, split it. If a task is trivial (single file, one function), merge it with an adjacent task.
4. **Traceability**: Verify every requirement in `artifacts/features/<slug>/spec.md` maps to a task in `artifacts/features/<slug>/tasks.md`.
5. **Readiness & Handoff**: Run a completeness check using `references/definition-of-ready.md` to ensure the plan and tasks meet all preconditions. Run `bash scripts/harness/phase-gate.sh <slug> "Plan Approved"` to verify preconditions. If it fails, fix the root cause before proceeding. Set `artifacts/features/<slug>/status.md` to `Plan Approved`, ensure the `Plan approved` checkbox under High-Level Progress is marked `[x]`, and route to `/spec-implement`.

## Anti-Patterns

- **Design After Tasks**: Writing task breakdown before technical design. Tasks must derive from design, not vice versa.
- **Undocumented Tradeoffs**: Choosing between two viable approaches without recording an ADR. If there's a real choice, `/spec-adr` must fire.
- **Overly Granular Tasks**: 30 tasks for a 2-day feature creates overhead. Target 2–4 hour increments.
- **Missing Traceability**: No `Covers:` or `ACs:` fields in tasks.
- **Premature Optimization**: Designing for scale that the spec doesn't require. Ponytail rule: build only what the spec demands.
- **Silent Spec Amendments**: Changing the plan without re-running the phase gate. If the spec changed, the plan is stale — follow the Spec Amendment Protocol.
- **Context Hoarding**: Keeping the full spec, plan, and research docs in context after planning is done. Evict raw logs and summarise before handoff.

## Core Rules
- **Hierarchical Detail Management**: Keep `plan.md` high-level and readable. Do NOT dump raw code or algorithms into the plan; extract those to separate implementation detail files if necessary.
- **Heuristic Citation**: If your design applies a learned heuristic from `learned-heuristics.md`, cite its LH-* ID in `tasks.md` design rationale or `plan.md` (SHOULD).
- **Architectural Gates**:
  - **Simplicity Gate**: No speculative future-proofing. Build only what satisfies the exact requirements.
  - **Anti-Abstraction Gate**: Use framework features directly. Avoid creating custom wrappers or premature abstractions.
- **Verifiable Task Increments**: Break work into low-risk tasks that can be proven independently.
- **No Spec Re-opening**: Stick to the approved requirements.
- **Spec Amendment Protocol**: If `spec.md` is amended after `plan.md` has been approved, the agent MUST:
  1. Add a `[STALE — spec amended <date>]` header to the top of `plan.md` and `tasks.md`.
  2. Set `status.md` phase back to `Planning`.
  3. Re-run Steps 2–4 (Design, Task Breakdown, Traceability) before any implementation task resumes.
  Implementation MUST NOT continue against a stale plan.
- **Context Eviction**: After drafting the plan, you MUST summarize any raw architectural logs and evict them from your context window before handing off to `/spec-implement`.

## Read First

Read this skill thoroughly before invoking it.

## When to Use

Use this skill for its designated purpose within the delivery flow.

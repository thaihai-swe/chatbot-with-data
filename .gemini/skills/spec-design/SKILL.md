---
name: spec-design
description: Create or refine artifacts/features/<slug>/design.md when a feature needs architectural clarification, interface decisions, flow design, or risk reduction before planning. Use for cross-boundary, interface-changing, data-shaping, or otherwise technically consequential work where comparing alternatives and documenting decisions materially reduces ambiguity.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Spec Design

## Overview

Use this skill to create or refine `artifacts/features/<slug>/design.md`.

This skill explains how the feature will work at a system level. It owns decisions, interfaces, flows, and tradeoffs needed before planning.

## Read First

Read these inputs when they exist:

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `artifacts/features/<slug>/spec.md`
- `artifacts/features/<slug>/requirements-review.md`
- `artifacts/features/<slug>/analysis.md`
- `references/design-template.md`

## When to Use

Use this skill when the feature:

- spans multiple modules or services
- introduces or changes interfaces
- affects data flow or architecture
- changes brownfield behavior in risky areas
- needs explicit tradeoff decisions before planning

For highly localized changes, prefer a short design or recommend proceeding directly to planning if design is unnecessary.

## Stop Conditions

Stop and explain what blocks safe design work when:

- `spec.md` is missing or not ready enough to design against
- the change is so small that a design artifact would be ceremonial
- the key technical choices still depend on unresolved product ambiguity

When stopping, say:

- what is missing or unnecessary
- whether the correct next step is `spec-requirement` or `spec-plan`
- which decision still needs clarification if design cannot proceed

## Preconditions

- `spec.md` must exist and be complete enough to design against.
- If `requirements-review.md` says the spec is not ready, stop and say so.

## Core Rules

- Explain how the feature will work at a system level.
- Keep implementation detail limited to what downstream planning needs.
- Focus on decisions, interfaces, flows, and tradeoffs.
- For each major design choice, include the decision, rationale, alternatives, affected boundaries, and risks introduced or reduced.
- Treat `design.md` as the feature's primary decision log for non-obvious technical choices.
- When a design decision becomes durable repository knowledge, call it out for later promotion into `memories/repo/project-knowledge-base.md` instead of creating a standalone `DECISIONS.md`.
- Keep the design proportional to the feature complexity.
- For non-trivial design choices, compare 2-3 viable approaches before locking the recommended one.
- Lead with the recommended option and make the tradeoff explicit in plain language.
- Present large or risky designs in reviewable sections instead of one undifferentiated wall of content.
- Do not treat the design as stable while the key approach or boundaries are still unresolved.

## References

- Use [references/design-template.md](references/design-template.md) as the bundled design structure.
- Keep the artifact technical but not patch-level.
- Recommend skipping design when it would be ceremonial rather than clarifying.

## Workflow

1. Confirm the spec and its review state are ready for design.
2. Read repo memory and any relevant analysis.
3. Identify the technical drivers, boundaries, and risky decisions.
4. For non-trivial choices, compare 2-3 viable approaches and confirm the preferred direction before finalizing detailed design content.
5. Describe the proposed architecture, interfaces, and major flows.
6. Record alternatives considered, the rationale for the chosen approach, and any promotion-worthy decisions.
7. Present the draft design back in reviewable sections when the design introduced material tradeoffs or cross-boundary changes.
8. Surface open decisions that still matter for planning.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We can skip design and figure it out in implementation." | Cross-boundary ambiguity gets more expensive downstream. |
| "The first workable approach is enough." | Non-trivial technical choices need explicit tradeoffs before planning. |
| "This should include the exact patch." | Design should clarify architecture and interfaces, not collapse into implementation. |

## Red Flags

- the design is really a task list or patch plan
- technical tradeoffs were present but no alternatives were compared
- planning would still need to invent the core approach

## Verification

Before finalizing the design, verify:

- the design answers the technical ambiguity that justified writing it
- major boundaries, interfaces, and flows are coherent with the spec
- the chosen approach is explicit and alternatives are summarized where they matter
- hidden coupling, contradictory decisions, and task-level drift are removed
- remaining open questions are real planning blockers or clearly bounded follow-ups

## Self-Review

Before finalizing the design, verify:

- the design answers the technical ambiguity that justified writing it
- major boundaries, interfaces, and flows are coherent with the spec
- the chosen approach is explicit and alternatives are summarized where they matter
- hidden coupling, contradictory decisions, and design drift into task-level detail are removed
- remaining open questions are real planning blockers or clearly bounded follow-ups

## Output Standard

The design is ready only when it:

- reduces ambiguity for planning
- captures key technical decisions and tradeoffs
- identifies major interfaces and risks
- is stable enough that planning does not need to re-open core design choices
- stays proportional to the feature size

## Output Rules

- Update only `artifacts/features/<slug>/design.md`.
- Do not create `plan.md` or `tasks.md` in this step.
- If a design artifact is unnecessary, say so plainly and recommend proceeding to planning.

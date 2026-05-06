---
name: spec-requirement
description: Create or refine a feature specification in artifacts/features/<slug>/spec.md. Use when defining what should change and why, clarifying target users, problem, goals, user journeys, requirements, and acceptance criteria before design or planning. Prefer this skill for spec authoring and refinement, especially when ambiguity must be resolved without drifting into technical implementation.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Spec Requirement

## Overview

Use this skill to create or refine `artifacts/features/<slug>/spec.md`.

This skill owns specification authoring and the clarification pass that happens before requirements review. It defines what should change and why. It does not own architecture, task sequencing, or implementation planning.

## Read First

Read these inputs when they exist:

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `artifacts/features/<slug>/analysis.md`
- other existing feature artifacts for the same slug
- `references/spec-template.md` for the canonical bundled spec structure

## When to Use

Use this skill when the user needs to:

- define a new feature or change request
- refine an existing `spec.md`
- resolve product ambiguity before `/spec-review-requirements`
- capture users, problem, goals, scenarios, requirements, and acceptance criteria

Do not use this skill for:

- design decisions or technical solutioning
- implementation planning or task breakdown
- code changes

If the request is really about current-state discovery, route to `analyze` before drafting future-state requirements.

## Preconditions

Before finalizing the spec, verify that the request is clear enough to define:

- who the users are
- the problem being solved
- the core user workflow or experience
- the intended success outcomes

If one of those is missing and cannot be safely inferred, stop and state exactly what must be clarified.

If context supports reasonable assumptions or safe defaults, proceed and document them in `Assumptions`.

Assess scope before drafting in detail.

- If the request spans multiple loosely coupled capabilities, user journeys, or delivery tracks, do not force them into one oversized spec.
- Decompose the work into smaller feature candidates, explain the split, and continue only with the highest-priority slice when the user has not named a narrower scope.
- Treat "one spec" as "one reviewable product change" rather than "everything mentioned in the request."

## Stop Conditions

Stop and explain what blocks safe spec authoring when:

- the users, problem, or intended outcomes are still too unclear to define requirements
- multiple materially different product directions remain unresolved
- the change should be decomposed into smaller feature specs before writing detailed requirements

When stopping, say:

- what is unclear
- whether the next step is clarification, `analyze`, or a narrower spec slice
- why downstream review would be misleading right now

## Output Rules

- Update only `artifacts/features/<slug>/spec.md`.
- DO NOT create `design.md`, `plan.md`, or `tasks.md`.
- Do not finalize the spec if requirements or acceptance criteria are not reviewable.
- Do not finalize one oversized spec when the request should be split into multiple feature artifacts.
- If the spec is not ready, state exactly what is missing instead of guessing.


## Core Rules

- Focus on what and why, not how.
- Keep requirements testable and acceptance criteria observable.
- Preserve stable identifiers when the repo already uses them.
- Identify 3-7 major scenario areas, capability slices, or user-journey segments before writing detailed requirements when the feature is broad enough to need decomposition.
- Keep scope bounded; move future ideas to `Non-Goals` or `Open Questions`.
- Separate current-state observations from future-state requirements.
- Capture external dependencies, integration touchpoints, and policy or compliance constraints in requirement language when they materially shape scope or acceptance.
- Define non-functional expectations only when they matter to the user, business, risk posture, or review readiness; keep them specific enough to verify.
- Avoid prescribing frameworks, APIs, databases, file structures, or deployment details unless they are true business constraints.
- Write for business stakeholders and reviewers, not implementers.

## Requirements Analysis Lens

Before treating the spec as stable, make sure it covers the relevant parts of this checklist:

- Functional requirements: the concrete behaviors or outcomes the change must deliver
- Non-functional requirements: performance, reliability, security, accessibility, observability, or compliance expectations that materially affect acceptance
- Users and stakeholders: primary users, affected secondary actors, and who experiences the risk or value
- User journeys and scenarios: the key flows, edge conditions, and failure cases that shape scope
- Success criteria: measurable signals that the feature solved the stated problem
- Dependencies and external touchpoints: upstream systems, third-party services, manual processes, or cross-team interactions that affect the requirement boundary
- Current-state gap: what exists today, what must change, and what must stay unchanged for brownfield work

This is a coverage aid, not a mandate to bloat the document. Omit categories that do not materially affect the feature.

## Clarification Rules

This skill owns clarification during specification authoring.

- Resolve ambiguity before handing the spec to downstream review when possible.
- Make reasonable assumptions when safe defaults exist.
- Surface only unresolved questions that materially affect scope, security/privacy, or core user experience.
- Do not push unstable product ambiguity downstream into planning.
- When clarification is needed, ask one material question at a time instead of sending a broad questionnaire.
- Prefer constrained options when the likely answer space is small enough to guide the user without biasing the outcome.

Classify uncertainty as:

- `Blocking clarification`: cannot safely finalize the spec without an answer
- `Non-blocking assumption`: proceed, but record the assumption
- `Safe default`: apply a normal default without escalation

Use `[NEEDS CLARIFICATION: specific question]` only when multiple reasonable interpretations would materially change scope, security/privacy posture, or core UX.

Rules for unresolved markers:

- maximum 3 total
- mirror each one into `Open Questions`
- do not treat the spec as review-ready while blocking clarification remains

For non-trivial product choices, do not jump straight from ambiguity to detailed requirements.

- Briefly outline 2-3 viable product-shaping options when different choices would materially change user experience, scope, or validation strategy.
- Lead with the recommended option and explain the tradeoff in plain language.
- Record the chosen direction in `Notes` or `Assumptions` when it affects how the spec should be interpreted later.

## Iteration Rules

- When ambiguity is high, refine one section at a time instead of forcing a full stable spec in one pass.
- Stabilize upstream sections first: users, problem, goals, and scenarios should be coherent before detailed requirements multiply.
- If the request is still evolving, prefer a clearly marked draft with explicit assumptions and open questions over a falsely complete spec.
- Re-check requirement and acceptance-criteria traceability after each major refinement pass, not only at the end.
- Present the draft back to the user before treating it as stable when the request required meaningful clarification, decomposition, or product-direction choices.

## Research-Informed Specification

When `analysis.md` exists:

- treat it as the current-state evidence baseline for the feature
- compare proposed future behavior against observed current behavior before finalizing requirements
- make unchanged protected behavior explicit when the change is brownfield or regression-sensitive
- distinguish repository facts from product decisions; analysis informs the spec but does not replace product intent
- if analysis and requested behavior conflict, surface the conflict explicitly instead of smoothing it over

When `analysis.md` does not exist but the work is brownfield, still check whether the spec needs a short current-state summary to make the requirement boundary understandable.

## Workflow

1. Validate that the request has enough product context to proceed.
2. Read repo memory and current feature artifacts for the slug.
3. Assess whether the request is small enough for one reviewable feature spec; if not, decompose it and continue with the selected slice only.
4. If `analysis.md` exists, summarize the current-state baseline, affected boundaries, and protected behavior that matter for the spec.
5. Extract users, problem, major scenario areas, constraints, desired outcomes, dependencies, external touchpoints, and any material quality expectations.
6. Resolve what you can with safe defaults and documented assumptions.
7. When non-trivial product choices remain, present 2-3 viable approaches with tradeoffs and confirm the preferred direction before locking detailed requirements.
8. Draft or refine `spec.md` section by section, stabilizing problem framing and scenarios before expanding detailed requirements.
9. Run a self-review for placeholders, contradictions, unbounded scope, ambiguous wording, missing requirement categories, and weak requirement-to-acceptance traceability.
10. Present the drafted spec or key sections back to the user when review gating is needed, then incorporate feedback.
11. Check that acceptance criteria trace back to requirements and are observable by a reviewer.
12. If blocking clarification remains, stop and say exactly what is missing.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We can lock requirements and fill in the product gaps later." | Unresolved product ambiguity leaks downstream into design and planning. |
| "A big umbrella spec is faster." | Oversized specs hide scope decisions and make review weaker. |
| "The technical solution belongs here so implementers know what to do." | Specs should define what and why, not implementation detail. |

## Red Flags

- the spec reads like a design or task list
- acceptance criteria are not observable by a reviewer
- multiple feature slices are being bundled into one artifact without clear scope control

## Verification

Before finalizing the spec, verify:

- no placeholder text remains unless explicitly intentional and called out as blocking
- requirements do not contradict each other or the stated outcomes
- scope is still narrow enough to hand off as one feature
- material dependency, integration, and quality expectations are either captured or intentionally omitted
- acceptance criteria are concrete enough for a reviewer to verify without guessing
- the document stays in requirement space and does not drift into design or implementation planning

## References

- Use [references/spec-template.md](references/spec-template.md) as the bundled section template.
- Remove sections that do not apply instead of leaving placeholders.
- Keep the skill body focused on workflow and rules; keep structural detail in the reference file.


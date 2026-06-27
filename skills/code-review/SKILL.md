---
id: skill-code-review
name: code-review
description: "Perform code review following Google's Engineering Practices. Evaluates code health, design, functionality, complexity, testing, naming, and style."
tags: ['review', 'quality', 'standards']
triggers: ['review', 'merge', 'pull request', 'code quality']
next_skill: ''

---
# Code Review Skill


## Overview

Use this skill to perform code reviews based on Google's Engineering Practices. The goal is to ensure the overall code health of the codebase improves over time. Usually invoked as a helper from `harness-verify`.

## Read First

- PR description and diff
- `memories/repo/core-policies.md` (code standards, naming, principles, security boundaries, and sensitive paths)
- `docs/rules/ponytail.md` (simplicity, anti-abstraction, and verifiable increments)
- Style guides under `docs/rules/`

## When to Use

- Assigned to review a new PR or CL.
- Evaluating quality, maintainability, and correctness of proposed changes before merge.

## I/O Hand-off Protocol

### Inputs
- PR description, diff, and linked issues
- `memories/repo/core-policies.md` (code standards, security policy)
- `docs/rules/` style guides

### Outputs
- Structured review verdict: overall decision, mandatory findings, optional suggestions
- `review.md` written in gated integration mode
- Security halt with `SECURITY_HALT:` marker if security-sensitive paths are modified

### Next Skill
None (terminal — review output is consumed by human developers or `harness-verify`)

## Execution Modes: Standalone vs. Gated Integration

| Dimension | Standalone PR Review Mode | Gated Integration Mode (via `/harness-verify`) |
|---|---|---|
| **Trigger** | Assigned to review a new PR or CL | Automatically invoked at step 8 of `/harness-verify` |
| **Audience** | Human developers | Execution engine / automated verifiers |
| **Outcome** | PR Approval / Request Changes | Written directly to `review.md` |
| **Scope** | Complete PR diff + adjacent callers | Touch files & task boundaries (`tasks.md`) only |
| **Ceremony** | Mentorship, explanations, nit tags | Fails loud on AC/gate failures |

### Gated Integration Mode Contract
When called from `/harness-verify`:
- **Scope**: Restrict review strictly to touched files and specific task boundaries.
- **Outcome**: Produce a structured response (verdict, mandatory findings, options, compliments) and return to `/harness-verify` to write to `review.md`.

## Code Review Standards

Favor approving any CL that improves overall code health, even if imperfect.
- **No Perfectionism**: Do not block progress for minor polish.
- **No Degradation**: Do not approve changes that worsen code health (except in true emergencies).
- **Feature Fit**: Reject features that do not belong in the system.
- **Mentoring**: Share knowledge. Mark non-mandatory comments with `Nit:` or `Optional:`.

## Review Velocity

Code review completes in the same session it is invoked. Do not defer reviews or partial-review a diff — complete the review or stop with a documented reason.

## Workflow

1. **Context Load**: Read `spec.md` and `plan.md` for the feature context. Understand the intent before reading code. If standalone mode (no spec), read the PR description and linked issue.
2. **Mechanical Verification**: Confirm the mechanical gate passed (tests, lint, build). If not, stop — do not review unverified code.
3. **Core Files Review**: Read each changed file in the diff. For each:
   - Verify it is within task scope (matches `tasks.md` targets).
   - Assess design quality: does it integrate cleanly with existing architecture?
   - Check functionality and edge cases.
4. **Test Adequacy**: Verify tests are meaningful (assert behavior, not just line coverage). Check for races, missing edge cases, and assertion correctness.
5. **Naming, Style, Comments**: Apply `rules/` style guides or local consistency. Verify comments explain *why*, not *what*.
6. **Security Lens**: Check every changed file against `memories/repo/core-policies.md` `## Security Policy`. Flag any modification to security-sensitive paths. See Stop Conditions for escalation.
7. **Verdict**: Write structured outcome: overall verdict, mandatory changes (must-fix), optional suggestions (`Nit:`/`Optional:`), and positive callouts for notable improvements.

## Review Checklist

For each review dimension, tick off before writing the verdict:

- [ ] **Design**: Change integrates cleanly. No unplanned coupling or interface leakage.
- [ ] **Functionality**: Behavior matches spec ACs. Edge cases addressed.
- [ ] **Complexity**: No over-engineering. Solves today's problems.
- [ ] **Tests**: Tests assert behavior, not just execution. Assertions are meaningful.
- [ ] **Naming & Style**: Names are clear and self-documenting. Style guide followed.
- [ ] **Comments & Docs**: Comments explain *why*. Relevant docs updated.
- [ ] **Security**: No security-sensitive paths modified without evidence. No new attack surface introduced.

## Writing Comments & Handling Pushback

- **Courtesy**: Focus comments on the code, never on the developer.
- **Severity**: Differentiate suggestions (`Nit:`, `Optional:`, `FYI:`) from mandatory fixes.
- **Pushback**: Resolve disagreements with technical facts. Do not accept "will fix in later PR" for new complexity; require fix now. Pre-existing issues get a TODO + bug ticket.

## Stop Conditions

- PR description is missing or too vague.
- Modifies security-sensitive paths without explicit security evidence → **Security Escalation**: stop the review, write `SECURITY_HALT: <description>` to `review.md`, surface the finding to the user, and route to `/context-memory` to update `core-policies.md` if a new boundary has been identified.
- CL is pure documentation/comment changes (run lightweight pass).

## Core Rules

- **Technical Facts Over Opinions**: Prefer the author's approach if multiple valid options exist.
- **Understand Every Line**: Read and comprehend every modified line.



## Verification

- [ ] Every file in the diff was read.
- [ ] Mandatory comments are explicitly distinguished from optional ones.
- [ ] Security policy sensitive paths checked.
- [ ] Explicit review outcome (LGTM / Request Changes / Reject) provided.

## Output Rules

- Produce structured response: overall verdict, mandatory changes, optional suggestions, positive callouts.
- **Standalone mode**: Write verdict to `artifacts/features/<slug>/review.md`. If no active slug, write to `docs/reviews/review-<YYYY-MM-DD>.md`.
- **Gated Integration mode** (called from `/harness-verify`): Return structured response to the caller; `/harness-verify` writes it to `review.md`.

---
name: aiddk-spec
description: Define the "What & Why" of a feature. This skill handles specification authoring, Socratic refinement to resolve ambiguity, and a built-in readiness review to ensure requirements are testable and complete before planning.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Kit Spec

## Overview

Use this skill to create or refine `artifacts/features/<slug>/spec.md`, `proposal.md`, `status.md`, and `requirements-review.md`.

It owns:
1. **Socratic Alignment:** Asking clarifying questions to eliminate ambiguity.
2. **The Proposal Wave:** Drafting a high-level `proposal.md` to gain user alignment before detailed spec'ing.
3. **Status Tracking:** Maintaining `status.md` to track process state.
4. **Specification Authoring:** Defining users, problems, scenarios, and acceptance criteria.
5. **Readiness Review:** Judging if the spec is ready for design or planning.

## Read First

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `artifacts/features/<slug>/analysis.md`
- `references/status-template.md`
- `references/proposal-template.md`
- `references/spec-template.md`
- `references/requirements-review-template.md`

## When to Use

- Define a new feature or change request.
- Refine an existing `spec.md`.
- Resolve product ambiguity before design or planning.

## Workflow

1. **Initialization:** If `status.md` does not exist, create it from `references/status-template.md`. Set phase to `Spec'ing`.
2. **The Grilling Phase (Relentless Alignment):** Before drafting, you **must** ask 3-5 targeted clarifying questions that reduce product ambiguity. Do not ask a generic questionnaire. If the request is non-trivial, keep grilling until the path to success is 100% clear.
3. **Alignment (The Proposal):** Draft `proposal.md` from `references/proposal-template.md`. Present it to the user and **stop**. Wait for alignment confirmation before proceeding to the full spec.
4. **Scope Cut:** Once aligned, define the smallest useful release slice. Make `In Scope`, `Out Of Scope`, and `Non-Goals` explicit before writing detailed requirements.
5. **Authoring:** Draft `spec.md` focusing on *what* and *why*, not how. Prioritize 1-3 primary user scenarios and tie every requirement back to a scenario or outcome.
6. **Acceptance Design:** Every acceptance criterion must name how a reviewer will verify it. If an answer is still unknown, record it as an assumption or open question instead of inventing a direction.
7. **Self-Review:** Create `requirements-review.md`. If the verdict is `not ready`, iterate on the spec before stopping.
8. **Locking:** Once `ready`, state that the spec is locked for planning. Update `status.md` to show `Spec Approved`.

## Stop Conditions

- Product ambiguity is too high to define outcomes.
- User answers to Socratic questions are still contradictory.
- Multiple materially different product directions remain unresolved.

## Core Rules

- **The 3-Question Minimum:** Never start a spec without asking at least 3 high-signal questions.
- **What, not How:** Avoid prescribing technical solutions in the spec.
- **Smallest Useful Slice:** Default to the smallest releasable scope that still solves the stated problem.
- **Explicit Non-Goals:** If something is intentionally excluded, say so directly.
- **Testable AC:** Every acceptance criterion must be observable by a reviewer.
- **Validation-Aware:** Each acceptance criterion must name the proof surface: test, manual scenario, log, metric, or reviewer observation.
- **Scope Control:** Decompose oversized requests into smaller feature specs.
- **Brownfield Protection:** Preserve unchanged behavior explicitly when modifying existing systems.
- **Spec-Anchored:** The `spec.md` is the source of truth. If requirements change during implementation, you must return to this skill first.

## Rationalization vs. Reality

| Rationalization | Reality |
|---|---|
| "We can lock requirements and fill in the product gaps later." | Unresolved product ambiguity leaks downstream into design and planning. |
| "A big umbrella spec is faster." | Oversized specs hide scope decisions and make review weaker. |
| "The user's prompt is clear enough, no need to ask questions." | "Vibe alignment" is a trap. 3-5 targeted questions often reveal hidden constraints or simpler paths. |
| "I'll define the 'How' here to save time during planning." | Mixing 'What' and 'How' locks you into technical debt before you've even understood the problem. |

## Red Flags

- The request could be shipped as a smaller slice, but the spec keeps broadening anyway.
- The spec reads like a design or task list.
- Acceptance criteria are not observable by a reviewer or do not name a validation method.

## Verification

Before finalizing the spec, verify:
- No placeholder text remains.
- Requirements do not contradict each other or the stated outcomes.
- Scope boundaries and non-goals are explicit.
- Acceptance criteria are concrete enough for a reviewer to verify.
- Open questions that still matter are either resolved or clearly marked as blocking/non-blocking.

## Output Rules

- Update only `spec.md` and `requirements-review.md`.
- Do not create `design.md`, `plan.md`, or `tasks.md`.

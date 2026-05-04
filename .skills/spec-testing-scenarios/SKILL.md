---
name: spec-testing-scenarios
description: Create or refine a manual testing guide in artifacts/features/<slug>/testing-scenarios.md after implementation or implementation review. Use when users, QA, or testers need structured end-to-end test scenarios, setup instructions, expected results, regression checks, and sign-off guidance grounded in the approved artifacts and delivered behavior.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Spec Testing Scenarios

## Overview

Use this skill to create or refine `artifacts/features/<slug>/testing-scenarios.md`.

This skill packages delivered feature behavior into a human-run testing guide for users, testers, QA, or reviewers. It is a post-implementation artifact, not a replacement for tests or implementation review.

## Read First

Read these inputs when they exist:

- `artifacts/features/<slug>/spec.md`
- `artifacts/features/<slug>/plan.md`
- `artifacts/features/<slug>/tasks.md`
- `artifacts/features/<slug>/review.md`
- `artifacts/features/<slug>/design.md`
- `artifacts/features/<slug>/analysis.md`
- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- `references/testing-scenarios-template.md`

Also inspect the implemented behavior, relevant docs, setup steps, and user-visible flows that the testing guide needs to validate.

## When to Use

Use this skill when the user needs to:

- create a manual testing guide after implementation
- give QA or product reviewers a clear scenario checklist
- convert requirements and delivered behavior into human-run test cases
- document setup, execution steps, expected outcomes, and regression checks

Do not use this skill for:

- writing automated tests
- reviewing whether implementation is approved
- guessing behavior that has not been implemented or approved

If the implementation is not reviewable yet, route back to `spec-review-implementation` before presenting a full testing guide.

## Preconditions

Do not finalize testing scenarios unless these are true:

- implementation has been attempted
- enough delivered behavior exists to test manually
- the feature artifacts are available to derive intended outcomes
- setup and expected outcomes can be described concretely

If `spec-review-implementation` found blocking issues, either stop or clearly mark the guide as draft and limit it to the reviewable delivered scope.

## Stop Conditions

Stop and explain what blocks a useful manual test guide when:

- implementation has not been attempted
- delivered behavior is too incomplete to describe concrete tester steps
- setup or expected outcomes are still too unclear to write honest scenarios

When stopping, say:

- what delivered scope is missing
- whether the correct next step is `spec-implement` or `spec-review`
- whether a draft-only guide would still be useful

## Core Rules

- Base scenarios on delivered behavior plus approved artifacts, not vague intent.
- Focus on user-visible flows, tester actions, and expected outcomes.
- Include prerequisites and setup when they matter.
- Include regression-sensitive or high-risk paths explicitly.
- Separate happy-path scenarios from edge cases and failure cases.
- Keep the guide executable by a human without hidden chat context.
- If implementation is partial, say so clearly instead of presenting a full-release test plan.

## References

- Use [references/testing-scenarios-template.md](references/testing-scenarios-template.md) as the bundled structure.
- Prefer clear scenario steps and expected results over long prose.
- Keep the guide proportional to feature size and delivery risk.

## Workflow

1. Read the approved artifacts and current implementation state.
2. Identify the user-visible scenarios and regression-sensitive behaviors that need manual coverage.
3. Capture prerequisites, setup steps, and any required environment or test data.
4. Write scenario-by-scenario steps with expected outcomes.
5. Add edge cases, failure paths, and regression checks where relevant.
6. Add a short completion or sign-off section so testers can record what passed, failed, or was deferred.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "QA can figure it out from the feature artifacts." | A manual test guide should be executable without hidden context. |
| "The implementation is partial, but we can write the full release plan anyway." | Testing scenarios must stay honest about delivered scope. |
| "Expected results are obvious." | Manual verification fails fast when expected outcomes are vague. |

## Red Flags

- the guide describes intended behavior that has not been implemented
- setup prerequisites are missing for non-trivial flows
- happy paths are covered but high-risk regression paths are omitted

## Verification

Before finalizing the guide, verify:

- scenarios reflect delivered behavior and approved artifacts
- prerequisites and setup are concrete enough for a human to follow
- expected outcomes are explicit
- partial scope or known limitations are called out honestly

## Output Standard

The testing guide is ready only when it:

- covers the delivered user-visible behavior
- gives humans enough setup context to execute the scenarios
- includes clear expected outcomes
- includes regression checks where relevant
- is honest about partial scope or known limitations

## Output Rules

- Update only `artifacts/features/<slug>/testing-scenarios.md`.
- Do not invent behavior beyond what the implementation and approved artifacts support.
- If the implementation is too incomplete to produce a useful guide, say so clearly.

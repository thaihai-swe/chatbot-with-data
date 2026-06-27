# Status Report Template

Use this template when running `/context-status` to produce a consistent, scannable project-wide status view.

## Report Header

```
# Project Status Report
Generated: [DATE]
Scope: All active features in artifacts/features/
Total Features: [N]
```

## Summary Table

| Feature Slug | Phase | Profile | Last Updated | Blockers | Next Step |
|---|---|---|---|---|---|
| `<slug-1>` | Spec Approved | Moderate | [DATE] | None | `/spec-plan` |
| `<slug-2>` | Implementing | Complex | [DATE] | Waiting on auth team | `/spec-implement` Task 5 |
| `<slug-3>` | Done | Simple | [DATE] | None | (Complete) |

## Phase Definitions

- **Init** — Repository bootstrapped, harness initialized
- **Researching** — Investigating existing behavior or brownfield state
- **Spec'ing** — Defining requirements and acceptance criteria
- **Planning** — Designing solution and breaking into tasks
- **Implementing** — Executing tasks, building code
- **Verifying** — Running mechanical gate, alignment audit, security check
- **Done** — Feature complete, verified, ready for merge

## Profile Definitions

- **Simple** — Small, reversible, low-risk (1–2 hours)
- **Moderate** — Clear feature or bug-fix (4–8 hours)
- **Complex** — Ambiguity, cross-boundary, risky (1–2 days)

## Blocker Format

When a feature has blockers, expand the summary table with a "Blockers" section:

```
### Blockers

**Feature: `<slug>`**
- **Blocker:** [Description]
- **Reason:** [Why it's blocked]
- **Unblocks:** [What happens when resolved]
- **Owner:** [Who can unblock]
- **ETA:** [When expected to resolve]
```

## Next-Step Guidance

For each feature, recommend the exact next command:

| Phase | Next Step |
|---|---|
| Init | `/starter-init` |
| Researching | `/spec-research` or `/spec-requirements` |
| Spec'ing | `/spec-requirements` or `/spec-plan` |
| Planning | `/spec-plan` or `/spec-implement` |
| Implementing | `/spec-implement` (specific task ID) or `/harness-verify` |
| Verifying | `/harness-verify` or (Complete) |
| Done | (Archive or start new feature) |

## Example Report

```
# Project Status Report
Generated: 2026-05-29
Scope: All active features in artifacts/features/
Total Features: 3

## Summary

| Feature Slug | Phase | Profile | Last Updated | Blockers | Next Step |
|---|---|---|---|---|---|
| `user-auth` | Done | Moderate | 2026-05-28 | None | (Complete) |
| `oauth-integration` | Implementing | Complex | 2026-05-29 | None | `/spec-implement` Task 6 |
| `password-reset` | Spec'ing | Simple | 2026-05-27 | Waiting on product | `/spec-requirements` (grilling waves) |

## Blockers

**Feature: `password-reset`**
- **Blocker:** Product team hasn't decided on email provider (SendGrid vs AWS SES)
- **Reason:** Affects spec acceptance criteria for email delivery SLA
- **Unblocks:** Can finalize spec and move to planning
- **Owner:** Product Manager
- **ETA:** 2026-05-30

## Recommendations

1. **Unblock `password-reset`** — Follow up with product on email provider decision
2. **Continue `oauth-integration`** — On track, no blockers
3. **Archive `user-auth`** — Complete and verified, ready for merge
```

## Output Rules

- Keep the summary table to one line per feature
- Expand blockers only when they exist
- Always include the exact next public command
- Report is read-only (do not modify feature artifacts)
- Regenerate on each session to reflect current state

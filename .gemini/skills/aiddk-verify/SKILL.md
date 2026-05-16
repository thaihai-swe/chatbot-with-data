---
name: aiddk-verify
description: Verify implemented work against the spec and plan. This skill handles implementation review, manual testing guides, and the Spec-Drift Guardian check.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Kit Verify

## Overview

Use this skill to close the loop on a feature.

It handles:
1. **Status Tracking:** Updating `status.md` phase to `Verifying`.
2. **Drift Audit:** Detecting misalignment between spec and code (`review.md`).
3. **Implementation Review:** Auditing code, task state, and evidence against artifacts.
4. **Testing Scenarios:** Creating a manual guide for testers (`testing-scenarios.md`).
5. **Evidence Freshness:** Detecting stale or missing validation.

## Read First

- `artifacts/features/<slug>/status.md`
- `spec.md`, `plan.md`, `tasks.md`
- The delivered code and test output.
- `references/definition-of-done.md`
- `references/review-template.md`

## When to Use

- Review delivered implementation against the feature artifacts.
- Audit traceability and validation quality.
- Detect "Spec Drift" after implementation.

## Workflow

1. **Initialization:** Update `status.md`. Set phase to `Verifying`.
2. **Drift Check (Alignment Audit):** Compare every requirement (`REQ-X`) and acceptance criterion (`AC-X`) against the code. Document any **Missing**, **Excess (Ghost)**, or **Misaligned** behavior in `review.md`.
3. **Evidence Check:** Review the available proof before trusting task state.
4. **Traceability Audit:** Check `REQ -> AC -> TASK -> validation` coverage.
5. **Review:** Write `review.md` with findings first (including Drift), then verdict.
6. **Scenarios:** Create `testing-scenarios.md` for human-run validation.
7. **Finalization:** If the verdict is `Pass`, update `status.md` phase to `Done`.

## Stop Conditions

- Required upstream artifacts are missing.
- Implementation has not actually been attempted.
- Validation evidence is too weak or stale.

## Core Rules

- **Evidence over Confidence:** Review fresh evidence, not just the diff.
- **Security Lens:** Always audit auth, permissions, and data handling.
- **Traceability:** Verify `REQ -> AC -> TASK -> validation` is intact.
- **Drift Detection:** If implementation materially diverged from artifacts, call it out.
- **Stale Evidence Is A Finding:** Old, missing, or indirect proof does not count as done.
- **Missing Tests Matter:** If a behavior changed and the proof surface is weak, record it as a finding.
- **Task-State Honesty:** Reopen or downgrade task state when the evidence does not support `Done`.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The diff looks right, so the review can be light." | Review is about evidence, not plausibility. |
| "Missing verification is just a paperwork issue." | Weak or stale evidence is a real review finding. |

## Red Flags

- The verdict depends on confidence instead of fresh evidence.
- The review summarizes success without enumerating concrete findings or gaps.
- Behavior changed but no proof was updated.
- Completed task state contradicts the available validation.

## Verification

Before finalizing the review, verify:
- Each finding points to evidence rather than intuition.
- Requirement coverage and validation quality were checked.
- Task-state accuracy was reviewed.
- Spec drift, stale evidence, and missing-proof risks were checked explicitly.

## Output Rules

- Update only `review.md` and `testing-scenarios.md`.
- Do not rewrite the spec or plan during review.

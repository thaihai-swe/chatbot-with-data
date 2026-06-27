---
id: skill-harness-verify
name: harness-verify
description: "Verify implemented work against the spec and plan. Handles split verification modes, mechanical gates, implementation reviews (via the code-review skill), optional fallow-pass cleanup, manual testing guides, and final closeout authority."
tags: ['harness', 'verification', 'gates']
triggers: ['verify', 'gate', 'test', 'validation']
next_skill: 'context-status'

---
# Harness Verify

## Overview
Use this skill to close the loop on a feature. It updates `status.md` to `Verifying`, runs mechanical gates, audits alignment and traceability, performs a security lens check, runs optional code-review or harness maintenance, executes fallow-pass cleanup, drafts testing scenarios, runs post-ship memory sync, and writes the final verdict in `review.md`.

## I/O Hand-off Protocol
- **Reads**: `artifacts/features/<slug>/tasks.md`, `artifacts/features/<slug>/spec.md`, `artifacts/features/<slug>/plan.md`, `artifacts/features/<slug>/status.md`
- **Writes**: `artifacts/features/<slug>/status.md`, `memories/repo/harness-telemetry.md`
- **Next Skill**: `/context-memory` (to log lessons learned) or done.

## Workflow

1. **Initialization**: Run `bash scripts/harness/phase-gate.sh <slug> "Verifying"` to verify preconditions. If it fails, fix the root cause before proceeding. Update `artifacts/features/<slug>/status.md` phase to `Verifying`.
2. **Mechanical Gate Audit**: Run `bash scripts/harness/gate-runner.sh` to mechanically verify the workspace. Do not guess commands. Write the results into `review.md`.
3. **Gate Failure Telemetry**: If the gate in Step 2 fails, pipe the output into `bash scripts/harness/telemetry-collector.sh --task <TASK-NNN> --feature <slug>`. Then count failures for this task using `bash scripts/harness/telemetry-count.sh --task <TASK-NNN>`. If failures < 2, hand off to `/spec-implement`. If failures >= 2 on the same task, escalate to the user for a rethink or route to `/code-review`. Do not proceed.
4. **Clean-State Check**: Ensure no uncommitted changes or broken builds. This is a precondition — state must be clean before the alignment audit begins. If the gate in Step 2 passed, reset the failure counter: post-fallow failures count fresh, not against the Step 2 count.
5. **Alignment Audit**: For each AC in `spec.md`, identify the task ID (`TASK-NNN`) in `tasks.md` whose validation covers it.
   **Pass/Fail threshold**: Zero tolerance — every `AC-*` item in `spec.md` must map to at least one task with recorded validation evidence in `tasks.md`. A single AC with no implementation evidence = `Fail`. There is no partial pass.
6. **Design Conformance Check**: Read `plan.md`. For each major component or decision listed in the Technical Design section, confirm it is reflected in the delivered code and task list. Any component in the design section with zero corresponding implementation evidence in `tasks.md` is a `Fail`.
7. **Security Lens**: Audit verified scope against `memories/repo/core-policies.md` `## Security Policy`.
8. **Production Readiness (Optional)**: If the change is production-bound, run `references/production-readiness-checklist.md` and append findings to `review.md`.
9. **Fallow Pass (Optional)**: Simplify touched files by removing dead code/unused imports.
   **Scope limit**: Applies only to files explicitly listed in this feature's `tasks.md` task targets. No structural refactors are allowed during this step.
   **Ordering**: Step 4 (Clean-State) is a precondition checked before alignment. This step (Fallow Pass) is optional post-alignment simplification. Re-run the mechanical gate after cleanup before proceeding — this is a fresh verification, counted against a reset counter (Step 4 resets the failure counter after a successful pre-fallow gate).
10. **Helper Skills**:
    - **Code Review**: For substantial changes, invoke `/code-review` and merge findings into `review.md`.
    - **Harness Maintain**: Invoke `/harness-maintain` if changes touch the kit structure.
11. **Artifact Generation**: Write findings into `review.md`. Draft `testing-scenarios.md` using `references/testing-scenarios-template.md` (Required for `Moderate` and `Complex`, optional for `Simple`).
12. **Finalization & Handoff**: Apply `references/definition-of-done.md` checklist before issuing verdict. Set verdict (`Pass`, `Pass with Follow-Up Debt`, or `Fail`). If passed, update `status.md` to `Done` and explicitly hand off to `/context-memory` for post-ship sync.

## Core Rules

- **Proof Must Match Plan**: Require verification on the planned proof surfaces.
- **Evidence over Confidence**: Review fresh, reproducible execution outputs.
- **Split Modes**: Perform mechanical, alignment, and security audits separately.
- **Drift Detection**: Mismatches between code and spec must fail verification.
- **Circuit Breaker**: After 2 consecutive gate failures (tracked in `harness-state.json`), the engine blocks re-entry to `Verifying` until `/spec-plan` re-approves. Do not attempt a 3rd verify without a replan.
- **Done Authority**: This skill is the sole authority for marking a feature `Done`.

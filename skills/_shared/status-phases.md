

The canonical feature lifecycle state machine for CoreZero. Every skill that
reads or writes `artifacts/features/<slug>/status.md` must use exactly these phase
strings and follow the transition rules below.

# Why This File Exists

Phase strings are scattered across individual SKILL.md files and historically
differ slightly between them. This file is the single source of truth. Any skill
that transitions phase reads from this table, not from memory.

# Complexity Tiers (Canonical Vocabulary)

The canonical complexity scale is `Simple | Moderate | Complex`. All skills use
these three terms. Legacy aliases (`Tiny`, `Standard`) map as follows:

| Canonical | Legacy alias | Depth |
|-----------|--------------|-------|
| Simple    | Tiny         | Lightweight |
| Moderate  | Standard     | Standard |
| Complex   | Complex      | Comprehensive |

# Phase Reference

| Phase | Set by | Meaning | Unlocks next skill |
|---|---|---|---|
| `Researching` | `spec-research` | Investigation is active | — |
| `Research Complete` | `spec-research` | `analysis.md` is ready; root cause or brownfield map is written | `spec-requirements` |
| `Spec'ing` | `spec-requirements` | Spec authoring is active | — |
| `Spec Approved` | `spec-requirements` | `spec.md` is locked | `spec-plan` |
| `Planning` | `spec-plan` | Plan authoring is active | — |
| `Plan Approved` | `spec-plan` | `plan.md` and `tasks.md` are ready; first unblocked task is executable | `spec-implement` |
| `Implementing` | `spec-implement` | Code work is active | — |
| `Verifying` | `harness-verify` | Verification is active | — |
| `Done` | `harness-verify` | Mechanical gate passed, alignment passed, post-ship sync complete | — |

# Transition Rules

1. **Forward only.** A skill must not set a phase to an earlier state unless it is
   explicitly correcting a failed or stale state (e.g., reopening a spec after a
   planning blocker is discovered).

2. **Set phase at skill start.** Each skill sets the in-progress phase as its
   first `status.md` update (e.g., `spec-plan` sets `Planning` at step 1 before
   any design work begins). This makes the current state visible immediately.

3. **Approved/Done phase requires verification.** A skill MUST NOT set
   `Spec Approved`, `Plan Approved`, or `Done` unless its own internal
   verification checklist passes. Setting the approved phase is the last act
   of the skill, not the first.

4. **No phase skipping.** `spec-implement` requires `Plan Approved`.
   `harness-verify` requires `Implementing` or a re-verify trigger.
   An agent must not skip phases to save time.

5. **Re-entry is explicit.** If implementation reveals a spec gap, the correct
   action is to return to `spec-requirements` (setting phase back to `Spec'ing`)
   with an explicit note in `status.md` explaining why. Silent re-entry is a Red Flag.

# Optional Phases

These phases may appear in `status.md` but do not block the core flow.

> [!NOTE]
> Optional phases are supplementary. They should be set alongside or as sub-phases/notes rather than completely replacing the primary core delivery phase in `status.md`. If an optional phase is temporarily written to the main `# Phase` section (e.g. `Blocked`), the previous core delivery phase must be restored once resolved, or tracked in the metadata so `/context-status` can compute the correct next core command.

| Phase | Set by | Meaning |
|---|---|---|
| `ADR In Progress` | `spec-adr` | An architecture decision is being documented; does not pause the feature |
| `Blocked` | Any skill | Work is stalled on an external dependency; must name the blocker |

# Status File Sections

A minimal `status.md` must always contain:

```markdown
# Phase
[current phase from the table above]


# Feature Slug
[slug]

# Last Updated
[ISO date]

# Notes
[optional — blockers, re-entry reason, anything that explains a non-standard state]
```

# Cross-References

- Template: `_shared/status-template.md`
- Skill preconditions: each core skill's `# Preconditions` section

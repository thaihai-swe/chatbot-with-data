# Brownfield Mapping Template

Use this template when running `spec-research` in brownfield mapping mode — before any feature work begins on an inherited or unfamiliar codebase. The goal is a decision-ready map, not a feature investigation.

Output path: `artifacts/features/<slug>/analysis.md` or `docs/brownfield-map.md` for repo-wide mapping.

This template doubles as the kit's brownfield readiness artifact for the first safe feature in an inherited codebase.

---

# Metadata

- Repository:
- Mapped by:
- Date:
- Confidence: High | Medium | Low

# Scope

- What is being mapped:
- What is explicitly out of scope:

# Entry Points

List all primary entry points into the system.

| Entry Point | Type | Path | Notes |
|---|---|---|---|
| | CLI / HTTP / Queue / Cron | | |

# Major Boundaries

Map the major subsystem boundaries. For each, note what it owns, what it depends on, and what must not change.

| Boundary | Owns | Depends On | Must Preserve | Fragility |
|---|---|---|---|---|
| | | | | Low / Medium / High |

# Test Coverage State

- Test runner: `[command]`
- Current pass rate: `[X/Y tests passing]`
- Known broken tests: list them explicitly — do not fix silently
- Baseline proof surface: `[best available command, script, or manual proof]`
- Areas with no test coverage:
- Areas with strong coverage:

# Known Fragile Areas

List subsystems, files, or integrations that are risky to touch.

| Area | Why Fragile | Evidence | Recommended Approach |
|---|---|---|---|
| | | | |

# Brownfield Risk Register

List the highest-risk areas that could cause regressions or stalled delivery during the first feature.

| Risk | Trigger | Blast Radius | Mitigation |
|---|---|---|---|
| | | | |

# Preserved Behavior Inventory

List behaviors that must not change regardless of what feature work is done. These become brownfield constraints in downstream specs and plans.

| Behavior | Where It Lives | Why It Must Be Preserved | Verification Method |
|---|---|---|---|
| | | | |

# Existing Patterns To Reuse

List coding patterns, conventions, or utilities already in the codebase that new work should follow rather than reinvent.

| Pattern | Location | When To Use |
|---|---|---|
| | | |

# Migration Constraints

- Existing migrations or data contracts to preserve:
- Rollback limits:
- Compatibility promises:

# Security And Permission Watchouts

- Auth/session handling location:
- Secret or credential handling:
- Known security-sensitive paths:
- Prompt-injection or external-input surfaces:

# Recommended First-Touch Surface

Based on the map above, what is the safest, smallest area to start feature work?

- Recommended first feature area:
- Why it is safe:
- What to avoid until later:
- Suggested first `spec-research` investigation target:

# Open Questions

- Q-001 Question:
  Why unresolved:
  Best next source of truth:

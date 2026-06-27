---
id: skill-spec-research
name: spec-research
description: "Investigate a problem, feature area, bug, or brownfield subsystem and produce one bounded analysis artifact grounded in repository evidence. Use when root cause is unknown or current behavior must be mapped first."
tags: ['spec', 'research', 'exploration']
triggers: ['research', 'explore', 'brownfield', 'unknown']
next_skill: 'spec-requirements'

---
# Kit Research

## Overview
Investigate system behaviors and produce `artifacts/features/<slug>/analysis.md`. Use this for debugging, failure tracing, and mapping brownfield code before writing a spec or plan.
## When to Use

- Understand current behavior before writing a spec/plan.
- Diagnose and reproduce bugs.
- Map boundaries, dependencies, and stable patterns in brownfield paths.
## I/O Hand-off Protocol
- **Reads**: `artifacts/features/<slug>/status.md`, codebase files, domain packs.
- **Writes**: `artifacts/features/<slug>/analysis.md`, `artifacts/features/<slug>/status.md`.
- **Next Skill**: `/spec-requirements`, `/spec-adr`, or `/spec-plan`.

## Workflow

1. **Initialization**: Create `status.md` if missing (from `_shared/status-template.md`). Update the `## Current Phase` section to set phase to `Researching`.
2. **Context Alignment**: For each installed pack listed in `MASTER_INDEX.md`, read `memories/domain/<name>/glossary.md` frontmatter `triggers:`. If matched, note in `status.md` and load that pack's `glossary.md` before conducting research.
3. **Bug Diagnosis Mode (For Bugs/Regressions)**: Recreate the failure with a script or concrete steps before investigating. You MUST follow this strict debugging loop:
   1. **Build a Feedback Loop**: Create a red-capable command (a fast, deterministic test, curl, or script) that asserts the exact bug symptom. Do not proceed without this.
   2. **Reproduce & Minimize**: Shrink the repro to the smallest scenario that still goes red.
   3. **Hypothesize**: Generate 3-5 ranked, falsifiable hypotheses before testing any.
   4. **Instrument**: Add targeted logs or debugger probes to test one hypothesis at a time.
   5. **Propose Fix**: Document the verified root cause and propose the regression test seam and fix in `analysis.md` (to be handed off to implementation).
   6. **Cleanup**: Ensure all debug instrumentation is removed.
   - **Subagent-First Exploration (SFE):** For large unknown subsystems, delegate bounded explorations to subagents and return summaries.
4. **Brownfield Mapping**: Map target files, trace dependencies, identify preserved behaviors, boundary contracts, reuse patterns, risks, and migration constraints.
5. **Document**: Write all findings, risks, and next steps in `artifacts/features/<slug>/analysis.md` using the Brownfield Readiness Artifact structure from `references/analysis-template.md` (or `references/brownfield-mapping-template.md`).
6. **Handoff**: Update `status.md` to `Research Complete`. Route based on findings:
   - Scope and requirements clear → `/spec-requirements`
   - Contested technical choice blocks requirements → `/spec-adr` first, then `/spec-requirements`
   - Brownfield complexity requires formal plan before spec → `/spec-plan` (document rationale)
   - Inconclusive (evidence too sparse) → stop. Write `[INCONCLUSIVE]` in `analysis.md` and surface to user.
## Core Rules
- **Fact-Focused**: Separate observed facts from inferences. Prove hypotheses with code evidence.
- **Scope Limit**: Write analysis only. Do NOT write code or plans yet.
- **Strict I/O**: Do not create custom artifacts outside of the designated files.

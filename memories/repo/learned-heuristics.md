# CoreZero Learned Heuristics

## Purpose

This file captures repeated, evidence-backed heuristics that improve maintenance of the kit.

## Heuristics

### LH-001: Docs drift fastest at the workflow surface
- Trigger:
  - a skill contract or command surface changes
- Working heuristic:
  - update `documents/skills-guide.md` in the same wave
- Evidence:
  - repeated drift found in lifecycle docs, command references, and install guidance
- Confidence: High
- Last reviewed: 2026-05-27
- Promote to stronger rule? No

### LH-002: Bootstrap and docs must be verified together
- Trigger:
  - repo memory or canonical artifact set changes
- Working heuristic:
  - update `scripts/install.sh`, seeded templates, and consistency checks in one change
- Evidence:
  - prior bootstrap/docs drift around `core-policies.md` and removed commands
- Confidence: High
- Last reviewed: 2026-05-27
- Promote to stronger rule? No

### LH-003: Generated references are worth seeding early
- Trigger:
  - the repo grows enough that repeated codebase rediscovery is happening
- Working heuristic:
  - maintain `docs/project/code-map.md` as a compact landing surface
- Evidence:
  - repeated review and documentation passes required broad repo sweeps
- Confidence: Medium
- Last reviewed: 2026-05-27
- Promote to stronger rule? No

### LH-004: Agent tends to overscaffold when starting new files
- Trigger:
  - agent creates a new file or module for the first time in a session
- Working heuristic:
  - check existing files of similar type before writing; match their structure, not a generic template. Prefer the smallest file that satisfies the task over a boilerplate scaffold.
- Evidence:
  - repeated over-generation of boilerplate sections that the codebase never uses (e.g., full docstrings, empty method stubs, placeholder configs)
- Confidence: High
- Last reviewed: 2026-06-20
- Promote to stronger rule? **[PROMOTED]** Added to `docs/policies/code-design.md`

### LH-006: Token budget underestimation causes context compaction mid-complex task
- Trigger:
  - running a complex feature that loads many memory files and generates large tool output
- Working heuristic:
  - estimate token cost at feature start: count loaded files, add 2x buffer for tool output. If total exceeds 60% of capacity (120,000 tokens), split work into smaller phases and checkpoint between them.
- Evidence:
  - context compaction triggered mid-implementation, causing loss of design details and rework
- Confidence: High
- Last reviewed: 2026-06-18
- Promote to stronger rule? No — operational guidance, not normative

### LH-007: Memory promotion thresholds trigger after files are already oversized
- Trigger:
  - running `/context-memory audit` or noticing a memory file exceeds 800 lines
- Working heuristic:
  - track memory file sizes proactively in `harness-telemetry.md` Trend Summary. When any file reaches 600 lines, create a promotion proposal early rather than waiting for the 800-line warning.
- Evidence:
  - `project-knowledge-base.md` and `learned-heuristics.md` have grown past thresholds without triggering promotion because the check only runs during post-ship sync
- Confidence: Medium
- Last reviewed: 2026-06-18
- Promote to stronger rule? Yes — candidate for `memories/repo/core-policies.md` Memory Promotion Thresholds

### LH-008: Domain packs are ignored when building new features
- Trigger:
  - agent implements a feature that touches a domain with an installed pack but does not load it
- Working heuristic:
  - during `/spec-research` and `/spec-requirements`, explicitly check if the task keywords match any domain pack triggers in `MASTER_INDEX.md` `## By Domain Packs`. If a match exists, load the pack before writing the spec.
- Evidence:
  - features built without loading domain packs repeated patterns that were already captured in the pack, or violated boundary rules
- Confidence: High
- Last reviewed: 2026-06-20
- Promote to stronger rule? **[PROMOTED]** Added as a MUST rule in `spec-requirements/SKILL.md`

# CoreZero Learned Heuristics

## Index

- **LH-001** — Docs drift at workflow surface; update in same wave
- **LH-002** — Bootstrap and docs verified together
- **LH-003** — Generated references worth seeding early (code-map.md)
- **LH-004** — Agent overscaffolds new files [ARCHIVED — promoted to code-design.md]
- **LH-005** — Vague task validation leads to skipped verification
- **LH-006** — Token budget underestimation triggers mid-task compaction
- **LH-007** — Memory thresholds trigger post-oversize; track proactively
- **LH-008** — Domain packs ignored when building features [ARCHIVED — promoted to spec-requirements]

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

### LH-004: Agent tends to overscaffold when starting new files — ARCHIVED on 2026-06-25, see archive/deprecated-heuristics.md

### LH-005: Task validation evidence must be specific and machine-verifiable
- Trigger:
  - creating tasks in `tasks.md`
- Working heuristic:
  - every task must specify a concrete command or test file that runs and exits 0 as its validation proof, rather than vague human descriptions.
- Evidence:
  - tasks with vague proof criteria (e.g. "manual verify") lead to incomplete or skipped validation during alignment audits
- Confidence: High
- Last reviewed: 2026-06-23
- Promote to stronger rule? No

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
  - track memory file sizes proactively in `harness-telemetry.md` Trend Summary. When any file reaches the Early Warning threshold (per `core-policies.md` `## Memory Promotion Thresholds`), create a promotion proposal early rather than waiting for the Threshold Breach band.
- Evidence:
  - `project-knowledge-base.md` and `learned-heuristics.md` have grown past early-warning thresholds without triggering promotion because the check only runs during post-ship sync
- Confidence: Medium
- Last reviewed: 2026-06-18
- Promote to stronger rule? Yes — candidate for `memories/repo/core-policies.md` Memory Promotion Thresholds

### LH-008: Domain packs are ignored when building new features — ARCHIVED on 2026-06-25, see archive/deprecated-heuristics.md

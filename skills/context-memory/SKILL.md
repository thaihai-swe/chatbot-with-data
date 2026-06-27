---
id: skill-context-memory
name: context-memory
description: "Update repository memories and learned heuristics."
tags: ['context', 'memory', 'heuristics']
triggers: ['memory', 'heuristic', 'learned', 'update memory']
next_skill: 'context-compact'

---
# Context Memory

## Overview
Updates persistent AI memories (e.g., rules, architecture) so future agents don't repeat mistakes.

## I/O Hand-off Protocol
- **Reads**: Current context, `memories/repo/`.
- **Writes**: Files in `memories/repo/`.
- **Next Skill**: `/context-status` (if audit mode used)

## Workflow
1. **Mode Selection**: Determine if this is a regular update or audit (see Audit Mode below).
2. **Session Extracts**: Read `artifacts/features/<slug>/session-extracts.md`. For each entry marked `[CANDIDATE]`: promote confirmed durable lessons to `learned-heuristics.md` (using `references/learned-heuristics-template.md`) or the relevant domain pack's `patterns.md`; discard noise. Remove promoted entries from the candidates list. After all candidates are processed, write a marker comment at the top of the file: `<!-- triaged: true, date: YYYY-MM-DD -->`.
3. **Config Drift Check**: Identify any new file paths, canonical commands, or module roots introduced during the session. Update `memories/repo/harness-config.md` and `project-knowledge-base.md` `## Repository Overview` to reflect them (consult `references/pkb-*-template.md` as needed). Mark unknowns `[UNKNOWN]` per CC-003 — do not guess.
4. **Domain Pack Update**: If the active feature touched a domain with an installed pack, check whether any new patterns or anti-patterns emerged. Update `memories/domain/<name>/patterns.md` or `anti-patterns.md` with evidence-backed entries only.
5. **Size Check**: For every file modified in Steps 2–4, count lines. If any file exceeds 600 lines, open a promotion proposal at `artifacts/features/<slug>/promotions.md` per `MASTER_INDEX.md` Section 2 Rule 5. If the file should be compacted in-place rather than split, route to `/context-compact`.
6. **Decay Action**: If a prior `memory-audit.md` flagged LH-* entries as Archive candidates, and the user confirms (or if running non-interactively with `--apply-decay`), move each archived entry:
   a. Append the full entry to `memories/archive/deprecated-heuristics.md` preserving its LH-* ID and all fields.
   b. In `learned-heuristics.md`, replace the entry body with a one-line tombstone: `### LH-NNN: [Name] — ARCHIVED on YYYY-MM-DD, see archive/deprecated-heuristics.md`
   c. Update the `## Index` section: mark the entry as `[ARCHIVED]`.
   d. Do NOT delete the LH-* ID from the file — context-compact's ID preservation check requires all IDs to remain present.
   e. For Fading entries: add `- Status: Fading` field to the structured entry (not a heading prefix). Update `Last reviewed` date to today.

## Core Rules
- No fabrication: do not invent patterns or heuristics; only record what was observed.
- Incremental growth: add detail over time rather than creating new files for minor insights.
- Evidence-based: every entry should trace to a specific observation or session extract.

## Memory Tiers

The kit uses three durability tiers for persistent memory. Each tier has a different owner, lifecycle, and promotion path.

### Instruction Tier
- **Files:** `memories/repo/core-policies.md` (CC-* rules), `docs/policies/code-design.md`.
- **Owner:** `/context-memory` + user.
- **Promotion:** Candidate rules from `learned-heuristics.md` are promoted when recurrence-count >= 3.
- **Demotion:** Rules are deprecated via CC-* amendment, never deleted silently.

### Auto Tier
- **Files:** `memories/repo/harness-telemetry.md` (OBS-* entries).
- **Owner:** `telemetry-collector.sh` writes; `harness-verify` and `harness-maintain` govern.
- **Promotion:** When an OBS-* entry reaches `recurrence-count >= 3`, a promotion candidate is proposed to `learned-heuristics.md` or `core-policies.md`.
- **Demotion:** Entries are moved to `## Retired Entries` when the corresponding failure mode is resolved or the context no longer applies.

### Extracted Tier
- **Files:** `artifacts/features/<slug>/session-extracts.md` (EXT-* candidates).
- **Owner:** `/context-session` writes candidates; `/context-memory` triages via `references/extraction-triage.md`.
- **Promotion:** Candidate → triage (promote/defer/discard) → destination by category (Heuristic → `learned-heuristics.md` LH-*; Pattern → `project-knowledge-base.md` or `docs/project/architecture.md`; Rule → `core-policies.md` CC-*).
- **Demotion:** Discarded candidates remain in `## Triaged` with a reason. The trail matters — do not delete.

### Identifier Namespaces
| Prefix | File | Purpose |
|--------|------|---------|
| CC- | `core-policies.md` | Normative rules |
| LH- | `learned-heuristics.md` | Learned heuristics |
| OBS- | `harness-telemetry.md` | Auto-tier observations |
| EXT- | `session-extracts.md` | Extracted-tier candidates |
| INV- | `domain/*/boundaries.md` | Domain invariants |
| ADR- | `adr-log.md` | Architecture decisions |
| TASK- | `tasks.md` | Implementation tasks |
| REQ-/AC- | `spec.md` | Requirements and acceptance criteria |

## Audit Mode

### Usage
Invoke with `/context-memory --audit` (or pass `audit` as the subcommand).

### Checks
1. **File size thresholds** — for every `memories/repo/*.md`, count lines and report against the canonical ladder in `core-policies.md ## Memory Promotion Thresholds`:
   - >= 600 lines: early warning (start a promotion proposal)
   - >= 800 lines: threshold breached (open `artifacts/features/<slug>/promotions.md`)
   - >= 1200 lines: hard cap (block further appends until promotion lands)
2. **Domain pack trigger relevance** — for every pack under `memories/domain/`, read trigger keywords from `glossary.md` frontmatter and grep the codebase for occurrences. Flag triggers with zero matches as candidates for removal or rewording.
3. **Memory-to-code accuracy** — sample referenced paths, file names, and module roots from `project-knowledge-base.md`, `memories/repo/harness-config.md`, and `MASTER_INDEX.md` and confirm each still exists. Flag stale references.
4. **Domain pack usage** — read `harness-telemetry.md` (when populated) and `artifacts/features/*/session-extracts.md` for pack-load events; list packs not loaded in any recent session.
5. **Promotion watchlist sync** — compare files flagged in checks 1–4 against `MASTER_INDEX.md` `## Promotion Watchlist`. Surface drift in either direction.
6. **Heuristic Decay Scan** — mechanically assess LH-* citation recency:
   a. Scan all `artifacts/features/*/status.md` for `## Current Phase: Done`. Sort by the date field. Take the last 3 completed features (and track the last 5 for the archive threshold).
   b. `grep -rEoh "LH-[0-9]+"` across those features' `tasks.md`, `progress.md`, and `plan.md`. Build a hit-count map per LH-* ID.
   c. For each LH-* in `learned-heuristics.md`, cross-reference hit count + `Last reviewed` date:
      - Citations in last 1-2 features → **Active** (no action).
      - Zero citations in last 3 features AND `Last reviewed` > 1 month → flag **Fading** in the audit report.
      - Zero citations in last 3 features AND `Last reviewed` < 1 month → leave alone (grace period, too early to tell).
      - Zero citations in last 5 features AND `Last reviewed` > 1 month → flag **Archive candidate** in the audit report.
   d. No edits — report only. Matches existing audit philosophy.

### Output
Write a structured Markdown report to `artifacts/features/<slug>/memory-audit.md` (feature-scoped) or `docs/generated/memory-audit.md` (global). Sections:

- `## Summary` — counts by severity (info / warn / error)
- `## Size Findings` — table of file, line count, severity, suggested action
- `## Trigger Drift` — domain packs with stale or unmatched triggers
- `## Stale References` — paths and identifiers that no longer exist
- `## Unused Packs` — domain packs with zero recent loads
- `## Watchlist Sync` — proposed updates to `MASTER_INDEX.md` `## Promotion Watchlist`
- `## Decay Findings` — table of LH-* ID, hit count (last 3/5), Last reviewed date, status (Active/Fading/Archive candidate), suggested action.

### Core Rules — Audit Mode
- Mechanical only — count lines, grep keywords, stat paths. Do not interpret content.
- Evidence-required — every finding cites the file and the check that produced it.
- No edits — the audit produces a report only. Promotions and rewrites stay manual or route through a regular `/context-memory` invocation.

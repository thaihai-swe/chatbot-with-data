---
id: skill-context-compact
name: context-compact
description: "Detect and safely compact oversized memory files to prevent context window saturation. Summarizes, deduplicates, and prunes while retaining 100% of normative intent."
tags: ['context', 'compression', 'memory']
triggers: ['compact', 'compress', 'memory full', 'token budget']
next_skill: 'context-status'

---
# Context Compact

## Overview

As a project matures, memory files grow. Files over the thresholds in `core-policies.md ## Memory Promotion Thresholds` cause LLM amnesia and crowd out task context. This skill's sole job is to shrink a target memory file — safely and verifiably — using summarization, deduplication, and pruning, while preserving every normative rule and stable identifier intact.

This is a focused maintenance operation, not a feature workflow. It does not route findings, promote heuristics, or update the domain pack — those are `/context-memory` responsibilities.

## I/O Hand-off Protocol

- **Reads**: Target oversized file from `memories/repo/` (or `docs/project/`).
- **Writes**: Compacted version of the same file, in-place.
- **Next Skill**: Done. If the target file was `core-policies.md`, run `/context-memory --audit` afterwards to confirm no stale references remain.

## When to Use

- A memory file exceeds the early warning or threshold breach limits in `core-policies.md ## Memory Promotion Thresholds`.
- `/context-memory --audit` flags a file as oversized.
- The user explicitly requests compaction of a named file.

**Do not invoke this skill for:**
- Routing or promoting new knowledge — use `/context-memory`.
- Editing the content of rules or heuristics — use `/context-memory` or direct edit.
- Files under 200 lines — compaction cannot reduce below a meaningful minimum.

## Read First

Before compacting, read:
- The target file in full.
- `memories/repo/core-policies.md ## Memory Promotion Thresholds` — for current line-count thresholds and promotion proposal rules.
- `MASTER_INDEX.md ## 5. Promotion Watchlist` — to check if the file is already flagged for promotion (splitting). If it is, stop and ask the user whether to compact or promote instead.

## Workflow

### Step 1 — Triage

1. Count lines in the target file: `wc -l <file>`.
2. If lines < 200: stop. The file is not oversized. Report this and exit.
3. If the file is already in `MASTER_INDEX.md ## 5. Promotion Watchlist`: stop. Compaction is the wrong tool — the file needs to be *split*, not compressed. Surface this to the user.
4. Otherwise: proceed.

### Step 2 — Pre-Compaction Snapshot (MANDATORY)

Before touching the file:

```bash
cp <file> <file>.bak
grep -E "CC-[0-9]+|LH-[0-9]+|INV-[0-9]+" <file> | sort > /tmp/ids_before.txt
wc -l <file>
```

Record the before-line-count and identifier list. These are the safety baseline.

### Step 3 — Compact

Apply these techniques in order. Do not delete content — only condense presentation:

| Technique | What to do |
|---|---|
| **Paragraph → bullets** | Convert multi-sentence prose into tight bullet lists. |
| **Merge overlapping entries** | If two heuristics or rules say the same thing from different angles, merge them into one entry. Update the `recurrence-count` to the sum. |
| **Remove superseded content** | If a rule, heuristic, or note explicitly contradicts a newer entry in the same file, keep the newer one; remove the older. |
| **Drop resolved examples** | Remove inline examples that duplicate what the rule states. Keep only examples that add genuine disambiguation. |
| **Trim verbose preambles** | Section intros that restate the section header add no value. Remove them. |
| **Compress history tables** | In `## Change Log` or `## Delta History` tables, collapse entries older than 1 month into a single `(N older entries archived)` row. |

**Hard rules:**
- Do NOT delete any CC-*, LH-*, INV-* identifier or its core constraint.
- Do NOT remove `##` or `###` headers — only compress the body underneath.
- Do NOT change the meaning of any rule, even when rewording.
- Do NOT merge two rules that address genuinely different concerns.

### Step 4 — Post-Compaction Verification (MANDATORY)

After writing the compacted version:

```bash
grep -E "CC-[0-9]+|LH-[0-9]+|INV-[0-9]+" <file> | sort > /tmp/ids_after.txt
diff /tmp/ids_before.txt /tmp/ids_after.txt
wc -l <file>
```

**Abort conditions — restore from `.bak` immediately if:**
- Any identifier present in `ids_before.txt` is missing from `ids_after.txt`.
- Line count increased (compaction made the file larger).
- Line count reduction is less than 10% — the file was not meaningfully oversized; do not save.

**On abort:** restore from `.bak`, report exactly which identifiers were lost and why, and stop.

### Step 5 — Confirm and Clean Up

1. Report the before/after line count and reduction percentage to the user.
2. List any identifiers that were merged (note: merged, not removed).
3. **Wait for explicit user confirmation** before deleting the `.bak` file.
4. On confirmation: `rm <file>.bak`.

## Target Files

This skill may compact any of the following files. All other files are outside scope.

| File | Stable Identifiers to Preserve | Notes |
|---|---|---|
| `memories/repo/core-policies.md` | `CC-*` | The Amendment Rules section must stay verbatim. |
| `memories/repo/learned-heuristics.md` | `LH-*` | Merge overlapping heuristics; never drop one with `recurrence-count ≥ 3`. Tombstoned LH-* entries (marked [ARCHIVED]) are excluded from compaction merges but their IDs MUST be preserved. |
| `memories/repo/project-knowledge-base.md` | None (prose) | Dedup aggressively. |
| `memories/domain/*/boundaries.md` | `INV-*` | Do not remove invariants; do not compact `## Change Log` entries younger than 1 month. |
| `docs/project/architecture.md` | None (prose) | Trim stale component descriptions only. |

## Core Rules

- **No data loss**: Compaction reduces word count, not intent.
- **Safety protocol is mandatory**: Never compact without the pre/post snapshot.
- **Target 30–50% reduction**: Less than 10% means the file wasn't ready; more than 60% suggests content was deleted, not compacted.
- **One file at a time**: Do not compact multiple files in a single pass. Run the full workflow per file.
- **Never self-promote**: If compaction reveals the file should be split, not compacted, stop and propose a promotion instead of proceeding.

## Verification Checklist

- [ ] Pre-compaction snapshot exists (`<file>.bak` and `ids_before.txt`).
- [ ] Post-compaction identifier diff shows zero missing identifiers.
- [ ] Line count reduced by at least 10%.
- [ ] No `##` headers were removed.
- [ ] No rule meaning was changed, only presentation.
- [ ] User confirmed before `.bak` was deleted.

# Lazy-Load Reference Manifest

## Purpose
This file indexes optional references. It is metadata only; the context engine does not
automatically load these files from broad keywords or wildcard groups.

## Lazy-Load Tags

### [LAZY:visualize]
Load explicitly when the `visualize` skill requests a diagram reference:
Files:
- `skills/visualize/references/formats-multi.md`
- `skills/visualize/references/icons.md`
- `skills/visualize/references/style-light.md`
- `skills/visualize/references/style-dark.md`

### [LAZY:audit]
Load explicitly for an audit operation:
Files:
- `skills/context-memory/references/audit-checklist.md`
- `skills/context-memory/references/post-ship-sync.md`

### [LAZY:spec]
Select one named reference for the active spec operation. Do not load the whole
`skills/spec-*` tree. The skill contract names the exact reference to read.

### [LAZY:code-review]
Load explicitly when a review is requested:
Files:
- `skills/code-review/references/*.md`

### [LAZY:context]
Load explicitly for context or memory maintenance:
Files:
- `skills/context-memory/references/audit-checklist.md`
- `skills/context-memory/references/post-ship-sync.md`
- `skills/context-compact/references/target-files.md`

### [LAZY:harness]
Load explicitly for harness maintenance or verification:
Files:
- `skills/harness-*/references/*.md`

## Usage

### Explicit Load
When a skill needs a lazy-loaded reference, prefix the read instruction with `[LAZY:tag]`:
```
[LAZY:visualize] Read `skills/visualize/references/formats-multi.md` for Mermaid syntax.
```

### Selection Rule
The active skill must name the exact reference path needed for the current task.
Never expand a wildcard or load an entire skill reference directory at session start.

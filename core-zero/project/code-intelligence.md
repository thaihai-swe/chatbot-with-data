---
# Code Intelligence Configuration
# This YAML block is the machine-readable config. The agent reads this first.
# Prose sections below provide context and per-provider pointers.

active_provider: codebase-memory-mcp

providers:
  gitnexus:
    enabled: false
    configured: false          # Set to true after filling in provider-specific setup.

  codebase-memory-mcp:
    enabled: true
    configured: true

---

# Code Intelligence Configuration

<!--
  PURPOSE
  CoreZero skills use capability-intent routing — they ask for "impact analysis"
  or "symbol context", not a specific tool name. This file is the entry point:
  it declares the active provider and maps each intent to a numbered index.
  Per-provider setup, tool mappings, and skill file references live in separate
  files (see "Provider Files" below).

  HOW THE AGENT USES THIS
  1. Read `active_provider` and verify the corresponding `providers.<name>.enabled` is `true`.
  2. If `active_provider: none`, skip all code intelligence steps.
  3. Load the provider-specific file listed in "Provider Files" below.
  4. Resolve capability intents (by number) to concrete tool calls using that file's mapping table.
  5. If a capability is `N/A` for the active provider, apply the Fallback Rules.

  SKIP IF NOT USING
  If you do not want any code intelligence tool, leave active_provider: none.
  All AGENTS.md code intelligence rules are suppressed — no impact on the kit.
-->

## Capability Intents

These are the standard intents CoreZero skills use. Map each to the active provider's concrete call.

| #   | Capability Intent         | When used                                                      |
| - | - | - |
| 1   | Explore / query concept   | Exploring unfamiliar code; finding execution flows by concept  |
| 2   | Symbol context            | Full context on a symbol: callers, callees, execution flows    |
| 3   | Impact — upstream callers | Who calls this? Blast radius before editing a symbol           |
| 4   | Impact — downstream deps  | What does this depend on? Side-effects of changing it          |
| 5   | Summarize file or module  | Fast "what does this file do?" before deep reading             |
| 6   | Detect changed symbols    | Pre-commit check — did changes touch only expected symbols?    |
| 7   | Safe rename               | Rename a symbol across the call graph without find-and-replace |
| 8   | Codebase overview         | Session start — check index freshness and understand structure |
| 9   | All functional clusters   | Understand module groupings and functional areas               |
| 10  | All execution flows       | List all named processes / entry points                        |
| 11  | Single execution trace    | Step-by-step trace of one named execution flow                 |


## Provider Files

| Provider            | File                                       |
| - | - |
| gitnexus            | `code-intelligence-gitnexus.md`            |
| codebase-memory-mcp | `code-intelligence-codebase-memory-mcp.md` |

## Provider: (template for future tools)

To add a new provider:
1. Add a `providers.<name>` entry in the YAML frontmatter above.
2. Create `<name>.md` with setup instructions + tool mapping table.
3. Add a row in the "Provider Files" table above.
4. Register the file in `manifest.json` under `files.overwrite`.

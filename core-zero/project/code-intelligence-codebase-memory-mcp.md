# Provider: codebase-memory-mcp

repo: https://github.com/DeusData/codebase-memory-mcp

## Setup

```bash
# 1. Download the binary for your platform from the releases page.
# 2. Add to your MCP client config:
#    { "codebase-memory": { "command": "/path/to/codebase-memory-mcp" } }
# 3. Index the repo:
codebase-memory-mcp index /path/to/repo
```

After setup, set `enabled: true` and `active_provider: codebase-memory-mcp` in `code-intelligence.md`.

## Stale Index

```bash
codebase-memory-mcp index /path/to/repo
```

## Tool Mapping

| #   | Capability Intent         | Tool call                                                          |
| - | - | - |
| 1   | Explore / query concept   | `search_code({query: "concept"})`                                  |
| 2   | Symbol context            | `get_symbol({name: "symbolName"})`                                 |
| 3   | Impact — upstream callers | `find_references({symbol: "symbolName"})`                          |
| 4   | Impact — downstream deps  | `get_symbol({name: "symbolName"})` — inspect `dependencies` field  |
| 5   | Summarize file or module  | `get_file_summary({path: "path/to/file"})`                         |
| 6   | Detect changed symbols    | N/A — use `git diff --name-only HEAD` + `find_references` per file |
| 7   | Safe rename               | N/A — use `find_references` to map all sites, then edit manually   |
| 8   | Codebase overview         | `get_overview()`                                                   |
| 9   | All functional clusters   | `list_modules()`                                                   |
| 10  | All execution flows       | `search_code({query: "entry points"})`                             |
| 11  | Single execution trace    | `trace_calls({symbol: "entryPointName"})`                          |

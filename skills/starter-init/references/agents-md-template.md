# AGENTS Router Source

`starter-init` no longer maintains a forked AGENTS template in this file.

## Canonical Source

- The shipped router body lives at [`../../../../AGENTS.md`](../../../../AGENTS.md).
- `manifest.json` seeds downstream `AGENTS.md` directly from that canonical file.

## Rule

- Do not duplicate the router body here.
- If the router contract changes, update `AGENTS.md`, then verify the install surface and `starter-init` references still align.

## Why

Keeping a second full AGENTS template caused silent drift between the shipped router and the seeded downstream router, which is exactly the class of harness inconsistency the kit is meant to prevent.

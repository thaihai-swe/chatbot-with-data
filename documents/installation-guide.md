# CoreZero Adopter Guide

> **Audience:** Adopter
> **Journey:** Install and Adopt
> **Status:** Shipped package guide
> **Source of truth:** `kit/manifest.json`, `kit/scripts/install.sh`, and shipped `skills/*/SKILL.md`

## What CoreZero provides

CoreZero gives coding agents a spec-anchored workflow, durable memory, context routing, and mechanical verification. It ships 18 skill contracts plus scripts, rules, references, project seeds, and feature artifacts.

## Install

From an installed checkout:

```bash
bash scripts/install.sh <target_directory>
bash scripts/install.sh <target_directory> --dry-run
```

Public release installs use the release URL documented by the project maintainers. Run `--dry-run` before upgrading an existing repository.

## First 30 minutes

1. Read root `AGENTS.md` for operating rules.
2. Read root `MASTER_INDEX.md` for context routing.
3. Open `core-zero/index.html` for the local documentation portal.
4. Review adopter-owned seeds under `core-zero/project/`; use `[UNKNOWN]` where facts are not known.
5. Run `/starter-init`.
6. Start a greenfield feature with `/spec-requirements`, or investigate brownfield behavior with `/spec-research`.
7. Continue `/spec-plan` → `/spec-implement` → `/harness-verify`.
8. Use `scripts/corezero context-load` before non-trivial agent work to load routed memory, `scripts/corezero session-start|session-checkpoint|session-end` for session lifecycle, and `scripts/corezero status` for project status. Use `/context-memory` and `/harness-maintain` for governance work.

## Installed layout

```text
<project>/
├── AGENTS.md                  # Seeded once; adopter-owned router
├── MASTER_INDEX.md            # Seeded once; memory router
├── artifacts/features/        # Preserved feature artifacts
├── .corezero/sessions/        # Ephemeral session state
├── core-zero/
│   ├── index.html             # Documentation portal
│   ├── generated/             # Generated reports and dashboard
│   ├── project/               # Adopter-owned project facts and config
│   ├── rules/                 # Kit-managed rules
│   └── memories/              # Repo and domain memory
├── references/                # Kit-managed references
├── scripts/                   # Installer, Python engine, harness
├── skills/                    # 18 kit-managed skill contracts
└── documents/installation-guide.md
```

Exact files and ownership come from `kit/manifest.json`. Directories may exist before generated files are created.

## Upgrade ownership

- `overwrite`: kit-managed content updates on install.
- `copyIfMissing`: seeds adopter files only when absent; later edits remain.
- `preserve`: existing adopter content is not rewritten.

Back up `core-zero/`, `artifacts/`, and `.corezero/` before upgrades. Use dry-run first. Never restore a whole old tree over a new install; merge adopter-owned files deliberately.

## Verification

```bash
bash scripts/harness/doctor.sh
bash scripts/harness/gate-runner.sh
```

Use `/harness-verify` for feature-level proof and alignment. Use `scripts/corezero status` for current feature state.

## Troubleshooting

- Missing kit-managed files: rerun installer dry-run, then repair package/install source. Do not create shadow infrastructure manually.
- Unknown project facts: keep `[UNKNOWN]` until confirmed.
- Script permission errors: inspect executable bits in the installed package and rerun the installer; do not broadly chmod unrelated files.
- Upgrade concerns: back up adopter-owned memory, project seeds, artifacts, and session state before running the real install.

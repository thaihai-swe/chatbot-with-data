# Master Index & Memory Router

> Always-loaded master routing index.
> Read this at session start to locate domain-specific and category-specific index files, and to determine which memory files to load based on the active task's trigger keywords.

## 1. Context Indexes (load on demand)

| File | Contents | When to load |
|------|----------|--------------|
| `docs/project/code-map.md` | Generated map of code locations, file structures, counts, roots, and component domains. | Before any implementation task: new file, new route, new component. |
| `docs/rules/*.md` | Per-domain coding and policy rules (security, simplicity, etc.). | When the active task touches a security-sensitive domain or when loading a specific rule set. |
| `manifest.json` | Installation manifest listing kit-managed (overwrite) and adopter-owned (copyIfMissing/preserve) files. | When auditing or modifying the kit file structure or installation behavior. |
| memories/repo/core-policies.md | Repo-wide normative rules (CC-* identifiers), security policy, and memory promotion thresholds. | Read at session start and before changing core policies or security rules. |
| memories/repo/harness-config.md | Adopter-tailored seed: repository identity, work tracking, artifact routing, verification commands, session defaults, lifecycle. | Load when the task touches setup, bootstrap, commands, session defaults, or lifecycle configuration. |

## 2. Memory Router

1. Files in the **Always** group load on every session start.
2. Files in the **By Intent** groups are evaluated individually. Do not load a group all at once.
   - **Granular Routing:** Evaluate the active task against *each individual file's* description. Load ONLY the specific files whose contents are strictly required for the current task.
   - **Semantic Triggers:** You may load a file if its core purpose matches the task's intent, even if exact literal keywords are absent.
   - **Partial Loading:** For low-confidence matches or when you only need an overview, use `scripts/context-loader.py <file> --mode summary` to extract just the file's index or summary, preserving token budget.
3. Files in the **By Debug** group load only when debugging, retro, or post-mortem work begins.
4. The **Phase × Guidance Matrix** below tells you what to add (and what to stop reading) at each phase of the delivery loop.
5. If a file outgrows its slot (per `core-policies.md` `## Memory Promotion Thresholds`), open a promotion proposal under `artifacts/features/<slug>/promotions.md`.

### Always (load every session)

- `memories/repo/core-policies.md` — repo-wide normative rules (CC-* identifiers), security policy, memory promotion thresholds. Loaded every session.

### By Intent — Config

Broad Intent Keywords: `setup`, `bootstrap`, `install`, `repository identity`, `workspace`, `environment`, `command`, `verification command`, `session default`, `convention`, `lifecycle`, `known limit`, `workaround`.

*(Evaluate individually; do not block-load the group)*

- `memories/repo/harness-config.md` — adopter-tailored seed: repository identity, work tracking, artifact routing, verification commands, session defaults, delivery lifecycle, known limits.

### By Intent — Knowledge

Broad Intent Keywords: `architecture`, `pattern`, `convention`, `stack`, `module`, `api surface`, `domain`, `glossary`, `terminology`, `bootstrap`, `skill`, `template`, `adr`, `decision`, `decision record`, `product`, `users`, `metric`, `dependency`, `tooling`, `constraint`, `compliance`, `budget`, `deploy`.

*(Evaluate files individually; do not block-load the group)*

- `memories/repo/project-knowledge-base.md` — durable patterns, watchouts, project continuity facts.
- `memories/repo/adr-log.md` — index of architecture decisions; load when the task touches prior decisions or architectural tradeoffs. *(Skip if the file does not exist yet.)*
- `docs/project/architecture.md` — durable system structure, boundaries, integration seams.
- `docs/project/product-sense.md` — product vision, target users, success metrics. Load on product/scoping work.
- `docs/project/glossary.md` — shared vocabulary and naming conventions. Load when naming or terminology matters.
- `docs/project/tech-stack.md` — dependencies, APIs, tools, conventions. Load before adding deps or touching integrations. If gitnexus is listed under Development Tools, the project's code graph is available via MCP.
- `docs/project/project-constraints.md` — budgets, compliance, deploy, security constraints. Load when constraints bound the change.
- `docs/project/code-map.md` — generated map of code locations.

### By Intent — Rules

Broad Intent Keywords: `security`, `secret`, `auth`, `input validation`, `injection`, `simplicity`, `yagni`, `refactor`, `ponytail`, `minimal`, plus the domain name of any rule file added here.

*(Evaluate files individually; do not block-load the group)*

- `docs/rules/security.md` — cross-language security do/don't patterns; load on security-sensitive work (secrets, auth, external input).
- `docs/rules/ponytail.md` — lazy senior dev rules (YAGNI, minimal code); load when writing, planning, or refactoring code to enforce simplicity.
- `docs/policies/code-design.md` — normative cross-cutting coding policy (overengineering pitfalls, spec/behavior drift); load when changing or adding software design. Its `MUST`/`MUST NOT` rules carry priority-rule weight.

### By Intent — Learned

Broad Intent Keywords: `heuristic`, `instinct`, `recurring`, `lesson`, `we always`, `we never`, `last time`.

*(Evaluate files individually; do not block-load the group)*

- `memories/repo/learned-heuristics.md` — evidence-backed instincts that improve future execution.
- `memories/archive/deprecated-heuristics.md` — Cold storage for decayed LH-* heuristics. Not loaded into context by default.

### By Domain Packs

Domain packs live in `memories/domain/`. Trigger keywords are declared in `glossary.md` frontmatter.

- **`glossary.md`:** Load whenever 1+ trigger keywords match (establishes baseline vocabulary).
- **`boundaries.md`:** Load ONLY when the task involves cross-domain API calls, schema migrations, or multi-feature integration.
- **`patterns.md`:** Load ONLY when actively planning or implementing code *inside* that domain.
- **`anti-patterns.md`:** Load ONLY during code reviews, mechanical verification, or debugging.
- **No match:** Skip domain packs.
- **No packs installed:** Skip this section entirely.

Installed packs:
- **example** (`memories/domain/`) — triggers: `example`, `sample`, `demo`, `template`, `walkthrough`. Worked-example pack shipped as a schema demo; replace with a real domain pack.

### By Debug (load on debug, retro, or failure)

Trigger keywords: `debug`, `failure`, `regression`, `incident`, `retro`, `flaky`, `why did`, `root cause`.

- `memories/repo/harness-telemetry.jsonl` + `.md` — JSONL records written by `telemetry-collector.sh`, human view rendered by `telemetry-render.sh`. Triaged by `/harness-maintain`.
- `artifacts/features/<slug>/session-extracts.md` — per-feature distillation, candidate-only until triaged.

## 3. Phase × Guidance Matrix

The Always group loads every session. This matrix says what to **add** at each phase of the delivery loop. The AI agent should use this as a baseline guide and dynamically load extra files (using intent-based routing) if the task risk warrants it. `Must` = required reading; `Should` = read unless reason to skip; `Skip` = do not read.

| Source | Spec | Plan | Implement | Verify |
|---|---|---|---|---|---|
| `core-policies.md` | Must {## Purpose, ## Normative Rules} | Must {## Amendment Rules, ## Release Guardrails} | Must {## Normative Rules, ## Active Session Limits & FinOps Guardrails, ## Security Policy} | Must {## Memory Promotion Thresholds, ## Security Policy} |
| `harness-config.md` | Skip | Should {## Artifact Routing, ## Verification Commands} | Should {## Verification Commands, ## Session Defaults} | Skip |
| `project-knowledge-base.md` | Should | Must | Should | Should |
| `docs/project/architecture.md` | Should | Should | Skip | Should |
| `docs/project/product-sense.md` | Should | Skip | Skip | Skip |
| `docs/project/glossary.md` | Should | Should | Skip | Skip |
| `docs/project/tech-stack.md` | Skip | Should | Should | Skip |
| `docs/project/project-constraints.md` | Should | Should | Skip | Should |
| `learned-heuristics.md` | Should | Should | Should | Should |
| `docs/project/code-map.md` | Should | Should | Should | Skip |
| `docs/rules/*.md` (on language/domain match) | Skip | Should | Must | Should |
| `docs/policies/code-design.md` (on software-design change) | Skip | Should | Should | Skip |
| `domain/glossary.md` (on match) | Should | Should | Should | Skip |
| `domain/boundaries.md` (on match) | Should | Should | Skip | Should |
| `domain/patterns.md` (on match) | Skip | Should | Must | Skip |
| `domain/anti-patterns.md` (on match) | Skip | Skip | Skip | Must |
| `gitnexus` MCP (if installed) | Skip | Should | Should | Should | — Use `gitnexus impact` / `gitnexus context` before planning changes. If not installed, skip. |

| `harness-telemetry.md` | Skip | Skip | Skip | Should |
| Prior `session-extracts.md` | Skip | Should | Skip | Skip |

Phase definitions (Mapped to the canonical 7-Phase Delivery Loop):
- **Bootstrap**: Initializing workspace via `starter-init`.
- **Session START**: Starting session via `context-session START`.
- **Requirements Intake (Spec)**: Defining requirements via `spec-requirements`.
- **Planning (Plan)**: Designing features and drafting task lists via `spec-plan`.
- **Implementation (Implement)**: Coding, proving tasks, and evicting context via `spec-implement`.
- **Verification (Verify)**: Running mechanical test runners and audits via `harness-verify`.
- **Memory Sync**: Triaging and promoting heuristics via `context-memory` and closing session via `context-session END`.

## 4. Domain Context Packs

Domain packs add project-specific semantic context to the memory router. Each pack captures the ubiquitous language, proven patterns, anti-patterns, and boundary rules for a specific business or technical domain.

Domain packs live in `memories/domain/`. The memory router loads a pack when the active task's keywords match the pack's declared triggers.

> [!NOTE]
> Domain packs represent context for a specific *bounded subdomain* within the app. They do not replace or duplicate project-wide documentation. Use `docs/project/glossary.md` for project-wide dictionary terms, `docs/project/architecture.md` for top-level component maps, and `docs/project/tech-stack.md` for global dependencies.

### Trigger Keyword Rules

- Keywords are declared in `glossary.md` YAML frontmatter under `triggers:`.
- A single keyword match activates the domain pack.
- Once activated, use the Phase × Guidance Matrix to determine which files from the pack to load.
- With 0 matches, the pack is skipped entirely.

See `memories/domain/README.md` for the full file schema, creation steps, and lifecycle guidance.

## 5. Promotion Watchlist

Files flagged for structural action (split, extract, or retire) when they exceed the thresholds in `core-policies.md ## Memory Promotion Thresholds`. Written by `/context-memory` post-ship sync; read by `/context-compact` to abort if a file is flagged for splitting rather than compaction.

| File | Proposal | Proposed action | Date | Status |
|------|----------|-----------------|------|--------|
| (path to file) | artifacts/features/<slug>/promotions.md | split / extract / retire | YYYY-MM-DD | open / approved / done |

- **open**: proposal submitted, awaiting review.
- **approved**: user approved the action; `/context-compact` or manual split may proceed.
- **done**: action completed; row retained for audit trail.

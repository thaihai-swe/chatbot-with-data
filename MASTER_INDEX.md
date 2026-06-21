# Master Index & Memory Router

> Always-loaded master routing index.
> Read this at session start to locate domain-specific and category-specific index files, and to determine which memory files to load based on the active task's trigger keywords.

## 1. Context Indexes (load on demand)

| File | Contents | When to load |
|------|----------|--------------|
| `docs/project/code-map.md` | Generated map of code locations, file structures, counts, roots, and component domains. | Before any implementation task: new file, new route, new component. |
| `docs/rules/*.md` | Per-language and per-domain coding rules (e.g., Python style, security rules). | When the active task touches a specific language or security-sensitive domain. |
| `manifest.json` | Installation manifest listing kit-managed (overwrite) and adopter-owned (copyIfMissing/preserve) files. | When auditing or modifying the kit file structure or installation behavior. |
| memories/repo/core-policies.md | Repo-wide normative rules, canonical commands, limits, and security policy. | Read at session start and before changing core policies or security rules. |

## 2. Memory Router

1. Files in the **Always** group load on every session start.
2. Files in the **By Intent** groups are evaluated individually. Do not load a group all at once.
   - **Granular Routing:** Evaluate the active task against *each individual file's* description. Load ONLY the specific files whose contents are strictly required for the current task.
   - **Semantic Triggers:** You may load a file if its core purpose matches the task's intent, even if exact literal keywords are absent.
   - **Partial Loading:** For low-confidence matches or when you only need an overview, use `kit/scripts/context-loader.py <file> --mode summary` to extract just the file's index or summary, preserving token budget.
3. Files in the **By Debug** group load only when debugging, retro, or post-mortem work begins.
4. The **Phase × Guidance Matrix** below tells you what to add (and what to stop reading) at each phase of the delivery loop.
5. If a file outgrows its slot (>800 lines, 3+ distinct subtopics, or 5+ artifacts reference one slice), open a promotion proposal under `artifacts/features/<slug>/promotions.md`.

### Always (load every session)

- `memories/repo/core-policies.md` — repo-wide normative rules (CC-* identifiers), canonical commands, limits, and security policy.

### By Intent — Knowledge

Broad Intent Keywords: `architecture`, `pattern`, `convention`, `stack`, `module`, `api surface`, `domain`, `glossary`, `terminology`, `bootstrap`, `skill`, `template`, `adr`, `decision`, `decision record`, `product`, `users`, `metric`, `dependency`, `tooling`, `constraint`, `compliance`, `budget`, `deploy`.

*(Evaluate files individually; do not block-load the group)*

- `memories/repo/project-knowledge-base.md` — durable patterns, watchouts, project continuity facts.
- `memories/repo/adr-log.md` — index of architecture decisions; load when the task touches prior decisions or architectural tradeoffs. *(Skip if the file does not exist yet.)*
- `docs/project/architecture.md` — durable system structure, boundaries, integration seams.
- `docs/project/product-sense.md` — product vision, target users, success metrics. Load on product/scoping work.
- `docs/project/glossary.md` — shared vocabulary and naming conventions. Load when naming or terminology matters.
- `docs/project/tech-stack.md` — dependencies, APIs, tools, conventions. Load before adding deps or touching integrations.
- `docs/project/project-constraints.md` — budgets, compliance, deploy, security constraints. Load when constraints bound the change.
- `docs/project/code-map.md` — generated map of code locations.

### By Intent — Rules

Broad Intent Keywords: `python`, `security`, `secret`, `auth`, `input validation`, `injection`, `simplicity`, `yagni`, `refactor`, `ponytail`, `minimal`, plus the language or domain name of any rule file added here.

*(Evaluate files individually; do not block-load the group)*

- `docs/rules/python.md` — Python conventions and style; load on Python work.
- `docs/rules/security.md` — cross-language security do/don't patterns; load on security-sensitive work (secrets, auth, external input).
- `docs/rules/ponytail.md` — lazy senior dev rules (YAGNI, minimal code); load when writing, planning, or refactoring code to enforce simplicity.
- `docs/policies/code-design.md` — normative cross-cutting coding policy (overengineering pitfalls, spec/behavior drift); load when changing or adding software design. Its `MUST`/`MUST NOT` rules carry priority-rule weight.

### By Intent — Learned

Broad Intent Keywords: `heuristic`, `instinct`, `recurring`, `lesson`, `we always`, `we never`, `last time`.

*(Evaluate files individually; do not block-load the group)*

- `memories/repo/learned-heuristics.md` — evidence-backed instincts that improve future execution.

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

- `memories/repo/harness-telemetry.md` — auto-tier failure log written by `/harness-verify` and triaged by `/harness-maintain`.
- `artifacts/features/<slug>/session-extracts.md` — per-feature distillation, candidate-only until triaged.

## 3. Phase × Guidance Matrix

The Always group loads every session. This matrix says what to **add** at each phase of the delivery loop. The AI agent should use this as a baseline guide and dynamically load extra files (using intent-based routing) if the task risk warrants it. `Must` = required reading; `Should` = read unless reason to skip; `Skip` = do not read.

| Source | Spec | Plan | Implement | Verify |
|---|---|---|---|---|
| `core-policies.md` | Must | Must | Must | Must |
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

### Creating a Domain Pack

1. Create directory: `memories/domain/<name>`
2. Create all 4 required files using the schema below.
3. Optionally create `spec.md` if the domain has a cross-cutting REQ/AC contract.
4. Add trigger keywords to `glossary.md` frontmatter.
5. Add the domain to the `By Domain Packs` list above.

### Trigger Keyword Rules

- Keywords are declared in `glossary.md` YAML frontmatter under `triggers:`.
- The memory router evaluates domain intent based on matches. A single keyword match activates the domain pack.
- Once activated, use the Phase × Guidance Matrix to determine exactly which files from the pack to load (e.g., `patterns.md` for Implementation, `anti-patterns.md` for Verification).
- With 0 matches, the pack is skipped entirely.

### File Schema

#### glossary.md
Frontmatter:
```yaml
domain: <name>
triggers: [keyword1, keyword2, keyword3, keyword4, keyword5]
```
Body: Ubiquitous language table — terms the agent must use consistently when working in this domain. One row per term.

#### patterns.md
Proven implementation patterns for this domain. Each pattern entry:
- **Pattern name** (bold heading)
- When to use it
- Key implementation notes
- Citation (file or PR where this was established)

#### anti-patterns.md
Known failure modes and what NOT to do. Each entry:
- **Anti-pattern name** (bold heading)
- Why it fails in this domain
- What to do instead
- Citation (incident, review, or post-mortem)

#### boundaries.md
What this domain owns, what it explicitly does NOT own, and how it integrates with adjacent domains.
- **Owns:** What this domain is responsible for
- **Does not own:** What this domain defers to other domains
- **Integration contracts:** How this domain's outputs become other domains' inputs

#### spec.md (optional)
Canonical REQ/AC contract for the domain — the durable list of behaviors that all features in this domain must respect. Same shape as a feature `spec.md`.

Use it when:
- Multiple features touch the same set of REQs (auth, billing, data model).
- Cross-feature regressions are a real risk.
- Brownfield refactors need a stable map of "what already exists."

Skip it when:
- The domain has no shared contract — only ad-hoc utilities.
- The codebase is small enough that the source-of-truth can stay in code.

When a feature changes a domain's behavior or boundaries, the agent directly edits `boundaries.md` to update its `## Invariants` and appends a row to the `## Change Log`. This happens in the `/context-memory` post-ship sync.

### Lifecycle

- Domain packs are **adopter-owned** — the kit seeds the schema but does not prescribe content.
- Update packs during `/context-memory` Post-Ship Sync when new patterns emerge from features.
- Promote durable patterns from `artifacts/features/<slug>/session-extracts.md` into the domain pack.
- Remove outdated entries when the codebase no longer uses a pattern.

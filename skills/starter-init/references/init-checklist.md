# Initialization Checklist

Use this checklist to ensure the repository is fully prepared for harnessed agentic development.

### Brownfield Phase A (if applicable — skip for greenfield repos)

- [ ] Repo confirmed non-trivial (has existing code, tests, CI, or meaningful history).
- [ ] Subagent read-only sweep completed. No raw grep output in main context — summaries only.
- [ ] Archaeology sweep findings (baseline commands, security paths, and preserved behaviors) recorded in `memories/repo/project-knowledge-base.md` and `memories/repo/core-policies.md`.
- [ ] `memories/repo/learned-heuristics.md` has 3–5 new entries with file citations.
- [ ] `memories/repo/core-policies.md` limits/caveats updated.

### Phase B — Bootstrap (all repos)

- [ ] `install.sh` has already seeded the harness surface. If a seeded file is missing, re-run the installer before init continues.
- [ ] `AGENTS.md` exists at the project root and is router-style (< 50 lines, links to deeper docs).
- [ ] `memories/repo/core-policies.md` exists and captures repository workflow defaults.
- [ ] `memories/repo/core-policies.md` exists and contains normative repo-wide rules.
- [ ] `memories/repo/core-policies.md` contains a Security Policy section that captures permission tiers, trust boundaries, and secret handling.
- [ ] `memories/repo/learned-heuristics.md` exists and captures descriptive repeated heuristics only.
- [ ] `memories/repo/project-knowledge-base.md` exists and contains descriptive stack details, patterns, and conventions.
- [ ] Seeded adopter-owned docs under `docs/project/*.md` exist before pre-fill begins.
- [ ] `docs/project/architecture.md` exists when the repository has meaningful subsystem boundaries, runtime layers, or external integrations.
- [ ] `docs/project/code-map.md` exists when the repo is large enough to benefit from a generated structural map.
- [ ] Language runtime and dependency config files (e.g. package.json, requirements.txt, Cargo.toml) identified from manual code search.
- [ ] Test runner command identified from manifests and documented in `core-policies.md`.
- [ ] Lint/format/type-check commands identified from configurations and documented in `core-policies.md`.
- [ ] CI pipeline and build configs identified and documented in `core-policies.md`.
- [ ] Context compaction triggers and stale-context rules are documented in `core-policies.md`.
- [ ] Security and sandbox expectations are documented in `core-policies.md`.
- [ ] Directory structure boundaries documented in the knowledge base.
- [ ] Issue tracker mode, artifact routing, and slug conventions documented in `core-policies.md`.
- [ ] Baseline verification: The repository passes all existing tests and lint checks in its current state.

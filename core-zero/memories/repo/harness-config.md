# Harness Config

## Index

- Repository Identity
- Work Tracking
- Artifact Routing
- Verification Commands
- Session Defaults
- Environment And Access
- Conventions That Affect Automation
- Delivery Loop Lifecycle
- Known Limits & Workarounds

## Repository Identity

- Project name: Chatbot With Data
- Repository type: Production-grade RAG system (portfolio/learning project)
- Primary code roots: `backend/`, `frontend/`
- Default working branch: main
- Supported agent clients: opencode

## Work Tracking

- Issue tracker mode: GitHub
- Issue/project location: https://github.com/thaihai-swe/chatbot-with-data/issues
- Default work item format: GitHub Issues
- Required labels or states: `breaking-change`
- Escalation / blocker handling: Stop and ask user

## Artifact Routing

- Feature artifact root: `artifacts/features/<slug>/`
- Docs root: `core-zero/`
- Architecture doc path: `core-zero/project/architecture.md`
- Security policy path: `memories/repo/core-policies.md` `## Security Policy`
- Learned heuristics path: `memories/repo/learned-heuristics.md`
- ADR location: `core-zero/project/adr/[number]-[slug].md`
- Generated documentation location: `core-zero/generated/`
- Codemap path: `core-zero/project/code-map.md`
- Harness config path: `core-zero/project/harness-config.yaml`

## Verification Commands

- Install / bootstrap command: N/A
- Lint / format command: N/A (none configured)
- Typecheck command: N/A (none configured)
- Build command: `npm run build` (from `frontend/`)
- Test command (frontend): `npm test` (vitest scaffolded, no tests written)
- Test command (backend): `pytest` (scaffolded, no tests written)
- Docker: `docker-compose up -d` (starts Weaviate)
- Harness config file: `core-zero/project/harness-config.yaml` (defines delivery phases and mechanical validation gates)
- Harness gate-runner command: `bash scripts/harness/gate-runner.sh` (overridden by `scripts/harness/gate-runner.local.sh` if present)

## Session Defaults

- Session bootstrap skill: `/starter-init`
- Progress log path: `artifacts/features/<slug>/progress.md`
- Handoff path: `artifacts/features/<slug>/handoff.md`
- When to checkpoint: After completing a skill or major edit wave
- Context compaction triggers: Raw grep output, large file listings, superseded design detail
- Stale-context eviction rules: Summarize raw tool output after extracting findings
- When to stop and escalate: After two failed corrections on the same issue

## Environment And Access

- Required local services: None
- Required env files or secrets handling: None
- Sandbox / permission watchouts: Do not modify target project files outside bootstrap
- Browser / UI verification target: N/A

## Conventions That Affect Automation

- Feature slug format: kebab-case
- Branch naming format: features/<name>
- Commit / PR expectations: Subject under 72 chars, body explains why
- Required reviewers or owners: None (solo maintainer)

## Delivery Loop Lifecycle

Every feature lifecycle follows the canonical 7-Phase Delivery Loop:
1. **Bootstrap**: Environment setup via `/starter-init`.
2. **Session START**: Active feature boundaries setup via `/context-session START`.
3. **Requirements Intake**: Defining and locking spec checks via `/spec-requirements`.
4. **Planning**: Creating implementation task lists and proofs via `/spec-plan`.
5. **Implementation**: Coding, task proof validation, and context eviction via `/spec-implement`.
6. **Verification**: Mechanical verification gates, alignment audits, and review via `/harness-verify`.
7. **Memory Sync**: Post-ship promotion and session close via `/context-memory` and `/context-session END`.

## Known Limits & Workarounds

- **Observability log:** Empty until real failures get captured. Expect entries once features run end-to-end.
- **Session extracts:** Only exist per-feature; expect them to populate as features run `/context-session END`.
- **Mermaid rendering:** `visualize` ships in the package, but Mermaid-to-SVG rendering still depends on optional `mmdc` (CLI tool). Structural Mermaid validation works without it.
- **Adversarial spec review:** Recommended for cross-cutting or high-risk work but not yet a separate skill.

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

- Project name: AI Agents Development Kit (CoreZero)
- Repository type: Harness Engineering kit (template/starter kit)
- Primary code roots: `skills/`, `scripts/`, `memories/repo/`
- Default working branch: main
- Supported agent clients: All standard autonomous agents (using AGENTS.md)

## Work Tracking

- Issue tracker mode: GitHub
- Issue/project location: https://github.com/thaihai-swe/CoreZero/issues
- Default work item format: GitHub Issues
- Required labels or states: `breaking-change` for skill name or artifact schema changes
- Escalation / blocker handling: Stop and ask user

## Artifact Routing

- Feature artifact root: `artifacts/features/<slug>/`
- Docs root: `docs/`
- Architecture doc path: `docs/project/architecture.md`
- Security policy path: `memories/repo/core-policies.md` `## Security Policy`
- Learned heuristics path: `memories/repo/learned-heuristics.md`
- ADR location: `docs/project/adr/[number]-[slug].md`
- Generated documentation location: `docs/generated/`
- Codemap path: `docs/project/code-map.md`

## Verification Commands

- Install / bootstrap command: `bash scripts/install.sh /path/to/target`
- Lint / format command: N/A (documentation-first repo)
- Typecheck command: N/A
- Build command: N/A
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

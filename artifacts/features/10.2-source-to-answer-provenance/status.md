# Status: 10.2 Source-to-Answer Provenance

# Current Phase: Verifying

# Complexity: Complex

# 🧪 Intake

- *Input type:* new_initiative
- *Risk flags:* data_model, migration, cross_boundary, public_api
- *One-line restatement:* Build claim-level source-to-answer provenance (post-gen claim→chunk graph + coverage + X-Ray) on top of 9.0, per ADR-001.
- *Affected core-zero/specs:* n/a (feature under artifacts/features/10.2-source-to-answer-provenance)
- *Reasoning:* Multi-boundary product capability (chat pipeline + schema + SSE + UI + eval); not a narrow bugfix. Schema/SSE additive fields and dual orchestrators drive risk flags.

# Active Task
None

# High-Level Progress
- [x] Research complete
- [x] Spec approved
- [x] Plan approved
- [x] Implementation complete
- [ ] Verification complete

# Blockers
None

# Domain Packs Loaded
- `rag` — triggers: citation, generation, context assembly, streaming, grounding
- `frontend` — ChatPanel, CitationBadge, SourceBrowser, XRayPanel, WorkspaceContext

# Related Artifacts
- Source: `artifacts/features/production-rag-audit/analysis.md` §5.4
- Predecessor (Done): `artifacts/features/9.0-citation-upgrade/`
- Spec: `artifacts/features/10.2-source-to-answer-provenance/spec.md`
- Proposal: `artifacts/features/10.2-source-to-answer-provenance/proposal.md`
- Plan: `artifacts/features/10.2-source-to-answer-provenance/plan.md`
- Tasks: `artifacts/features/10.2-source-to-answer-provenance/tasks.md`

# Architecture Decisions
- ADR-001 Accepted: post-gen claim graph + `provenance_json` + coverage; no constrained decoding / hard repair in v1.
  Artifact: `core-zero/project/adr/001-source-to-answer-provenance-mode.md`

# Grilling Decisions (locked)
- Primary consumers: chat verify UX + X-Ray/eval equal
- Uncited mark: display-layer only (`[unsupported]` in ChatPanel; no answer_text mutation)
- Claim unit: paragraph blocks (blank-line split)
- Badge label: keep `Source N - Title`
- Badge click: panel anchor only (`setActiveChunkId`); no CitationModal
- SSE shape: additive `provenance` on existing `citations` event + GET
- Phase 0: stream groundedness parity + delete legacy Chat.jsx citation path
- Latency: no hard budget (expected <10ms)

# Resume Notes
- Done: All 13 tasks
- Blocker: None
- Next proof: Run full test suite + manual E2E
- Verification: `/harness-verify` next

# Next Step
Run `/harness-verify` to complete verification phase.

# Blockers
None

# Domain Packs Loaded
- `rag` — triggers: citation, generation, context assembly, streaming, grounding
- `frontend` — ChatPanel, CitationBadge, SourceBrowser, XRayPanel, WorkspaceContext

# Related Artifacts
- Source: `artifacts/features/production-rag-audit/analysis.md` §5.4
- Predecessor (Done): `artifacts/features/9.0-citation-upgrade/`
- Spec: `artifacts/features/10.2-source-to-answer-provenance/spec.md`
- Proposal: `artifacts/features/10.2-source-to-answer-provenance/proposal.md`
- Plan: `artifacts/features/10.2-source-to-answer-provenance/plan.md`
- Tasks: `artifacts/features/10.2-source-to-answer-provenance/tasks.md`

# Architecture Decisions
- ADR-001 Accepted: post-gen claim graph + `provenance_json` + coverage; no constrained decoding / hard repair in v1.
  Artifact: `core-zero/project/adr/001-source-to-answer-provenance-mode.md`

# Grilling Decisions (locked)
- Primary consumers: chat verify UX + X-Ray/eval equal
- Uncited mark: display-layer only (`[unsupported]` in ChatPanel; no answer_text mutation)
- Claim unit: paragraph blocks (blank-line split)
- Badge label: keep `Source N - Title`
- Badge click: panel anchor only (`setActiveChunkId`); no CitationModal
- SSE shape: additive `provenance` on existing `citations` event + GET
- Phase 0: stream groundedness parity + delete legacy Chat.jsx citation path
- Latency: no hard budget (expected <10ms)

# Resume Notes
- Done: TASK-001, TASK-002, TASK-011
- Next: TASK-003 (Provenance Pydantic models) — unblocks TASK-004+
- Task graph: PASS (13 tasks, no cycles)

# Next Step
Run `/spec-implement` for TASK-003.

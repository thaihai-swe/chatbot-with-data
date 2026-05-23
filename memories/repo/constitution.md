# Project Constitution

## Purpose

This document defines durable repo-wide principles, guardrails, and quality gates for `chatbot-with-data`.
It is the durable source of truth for how work should be shaped across the repository, especially when feature artifacts, docs, and local code patterns need to be reconciled.

## Scope

This constitution applies to the full repository, including:

- the FastAPI backend under `backend/`
- the React frontend under `frontend/`
- feature artifacts under `artifacts/features/`
- durable repo memory under `memories/repo/`
- supporting docs under `docs/`

All human contributors and AI agents should follow it when planning, implementing, reviewing, and documenting work in this repo.

## Core Principles

- CC-001 Spec-driven delivery:
  Changes should be traceable to the repository's feature-artifact workflow under `artifacts/features/<slug>/` when the work is non-trivial.
  Why it matters: this repo already uses specs, plans, and tasks as the coordination layer for larger features.

- CC-002 Surgical change scope:
  Edits must stay tightly aligned to the requested outcome and avoid unrelated refactors, formatting churn, or opportunistic rewrites.
  Why it matters: the repo contains active feature work and brownfield code where drive-by changes increase review and regression risk.

- CC-003 Evidence before assertion:
  Behavior, architecture, and completion claims must be grounded in repository files, executed verification, or both.
  Why it matters: this project mixes implementation, docs, and feature artifacts, so unverified assumptions drift quickly.

## Delivery Rules

- CC-101 Frontend work must read `design.md` and follow the repo's existing UI conventions before editing `frontend/`.
- CC-102 Non-trivial work should update or create the relevant feature artifacts under `artifacts/features/<slug>/` before or alongside implementation.
- CC-103 Durable repo-wide lessons learned must be promoted to `memories/repo/project-knowledge-base.md` or this constitution instead of being left only in chat.

## Quality And Validation Gates

- CC-201 Work is not done until the changed behavior has been verified with the narrowest practical check, such as targeted tests, build validation, or a direct manual workflow.
- CC-202 Verification results must be reported honestly; skipped checks, failing checks, and unverified assumptions must be called out explicitly.
- CC-203 If a change affects an observable existing behavior, validation must cover regression risk, not only the new happy path.

## Architectural Guardrails

- CC-301 Backend HTTP behavior should remain routed through the FastAPI backend under `backend/routers/` with domain logic kept in backend modules rather than pushed into the frontend.
- CC-302 Frontend concerns should stay in the React app under `frontend/src/`, with API access going through the existing frontend API modules rather than ad hoc request code scattered across screens.
- CC-303 Durable system documentation belongs in `docs/`; feature-local design reasoning belongs in `artifacts/features/<slug>/`.

## Brownfield Safety Rules

- CC-401 Do not silently replace an established local pattern when editing an existing module; follow the dominant nearby pattern unless the task explicitly includes a refactor.
- CC-402 Do not revert or overwrite unrelated work in the repository without explicit instruction.
- CC-403 When repository docs and implementation disagree, preserve working code carefully, note the mismatch, and update the appropriate artifact instead of guessing.

## AI Agent Operating Rules

- CC-501 Agents must read the relevant local files before proposing or applying changes.
- CC-502 Agents must not fabricate paths, APIs, verification results, or repository state.
- CC-503 Agents must use repo memory and feature artifacts as durable context, and promote reusable findings when they become repo-wide knowledge.

## Amendment Process

- Amend this document only for repo-wide, durable, normative rules.
- Prefer refining existing CC-* entries over adding overlapping rules.
- Amendments are required when repeated work reveals a stable new guardrail or when an existing rule becomes inaccurate.
- Changes here should trigger a quick review of `memories/repo/project-knowledge-base.md` and any affected templates or feature workflows.

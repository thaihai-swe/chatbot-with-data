# Project Constitution

## Purpose

This document defines durable principles, guardrails, and quality gates for the RAG Knowledge Base Lab.
It guides all subsequent development decisions and constrains AI agent behavior.

This is the **source of truth** for what "done" means.

## Scope

- **Repositories:** All files within the `chatbot-with-data` workspace.
- **Audience:** All engineers and AI agents contributing to this project.
- **Precedence:** This document overrides temporary session instructions and general workflows when in conflict.

## Core Principles

- **CC-001 High-Signal Communication:** No flattery, no filler. Skip openers like "Great question" or "You're absolutely right". Start with the answer or action.
- **CC-002 Intellectual Honesty:** Disagree when you disagree. If a premise is wrong, say so before doing the work. Never fabricate file paths, symbols, or results.
- **CC-003 Precision and Scope Control:** Touch only what you must. Every changed line must trace directly to a requirement. No "drive-by" refactors or unrequested improvements.
- **CC-004 SOLID Principles:** Adhere strictly to SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) to ensure maintainable and scalable code.

## Delivery Rules

- **CC-101 Skill-First Workflow:** Use matching skills under `.gemini/skills/` before performing freeform work. Skills are the workflow contract.
- **CC-102 Empirical Validation:** Never report "done" based on a plausible-looking diff. Plausibility is not correctness. Run tests, linters, and type checkers to verify every change.
- **CC-103 Stop on Ambiguity:** If a task has multiple plausible interpretations or if instructions conflict with repo state, stop and ask for clarification.

## Quality And Validation Gates

- **CC-201 Automated Verification:** Every behavior change must include or be verified by an automated test.
- **CC-202 Static Analysis:** All Python code must pass virtualenv-scoped linting and type checking (if configured).
- **CC-203 Grounded Generation:** AI answers must be grounded in retrieved evidence with structured citations. Hallucinations or unsupported claims are blocking defects.

## Architectural Guardrails

- **CC-301 Service-Oriented Backend:** Maintain a clean separation between routers, services, and repositories.
- **CC-302 Client-Side Frontend:** Build screens as JavaScript clients that call REST API endpoints; avoid backend-rendered views.
- **CC-303 Data Isolation:** Keep frontend (`frontend/`) and backend (`backend/`) strictly separated.

## AI Agent Operating Rules

- **CC-501 Agents must:** Reproduce reported issues empirically before applying fixes.
- **CC-502 Agents must not:** Revert changes unless they result in errors or are explicitly requested to do so.
- **CC-503 Required artifact usage:** Maintain feature specifications, implementation plans, and task breakdowns in `artifacts/features/`.

## Amendment Process

- **Update Frequency:** Amendments are made when repo-wide principles are corrected or expanded.
- **Versioning:** Semantic versioning applies (Current version: 1.0.0).
- **Process:** Use the `constitution` skill to refine `memories/repo/constitution.md`.

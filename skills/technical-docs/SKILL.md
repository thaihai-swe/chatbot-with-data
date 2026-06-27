---
id: skill-technical-docs
name: technical-docs
description: "Generate API docs or developer guides for specific features. Use this skill when a feature introduces new public APIs, CLI commands, database schemas, or complex component interactions that require structured, durable technical documentation for team reference and code maintenance."
tags: ['docs', 'technical', 'api']
triggers: ['technical docs', 'api docs', 'reference']
next_skill: ''

---
# Technical Docs

## Overview
Generates targeted technical documentation for features, specifically focusing on API definitions, data schemas, and complex integration flows.

## When to Use
- **API Changes:** When introducing or modifying public REST endpoints, gRPC services, public libraries, or CLI parameters.
- **Integration Flows:** When a feature involves complex orchestration across multiple services or components.
- **Database/Schema Changes:** Documenting migrations, key tables, and state transitions.

## I/O Hand-off Protocol
- **Reads:** Source code, tests, `spec.md`, `plan.md`.
- **Writes:** Targeted files under `docs/` or `docs/generated/` based on the feature's layout.
- **Next Skill:** Return to previous skill (e.g., `/spec-implement` or `/harness-verify`).

## Workflow

1. **Information Discovery**:
   - Inspect the codebase, route maps, and source files to identify all affected API contracts and interfaces.
   - Trace execution paths to understand cross-component messages or data flows.

2. **Select Template**:
   - For public-facing endpoints, schemas, or CLI references, use `references/api-document-template.md` and check completeness against `references/api-coverage-checklist.md`.
   - For system diagrams, sequential lifecycles, and orchestration logic, use `references/flow-document-template.md` and check completeness against `references/flow-coverage-checklist.md`.

3. **Draft Documentation**:
   - Write clear, version-controlled Markdown. Focus on code blocks, payload structures, sequence sequences, and constraints.
   - Do not use placeholders or generic examples. Provide complete, valid payload/command examples.

4. **Verify**:
   - Validate that all code symbol references (classes, methods, schemas) are accurate and currently present.
   - Confirm that all payload examples match the actual validation logic in the codebase.

## Core Rules
- **No Stale Data:** Always align technical documentation with the final implemented code.
- **Machine Readability:** Keep schemas, payloads, and parameter definitions in plain text (Markdown code blocks or tables) rather than screenshots or images.
- **Clear Limits:** Explicitly state request limits, error structures, and failure responses.

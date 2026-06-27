# System Flow Document Template

Use this structure unless the user asked for a different format.

## 1. Audience and Scope

- Who this document is for
- What system or subsystem it covers
- What is explicitly in scope and out of scope
- Where the facts came from: code, specs, ADRs, README, runbook, tests

## 2. System Overview

- What the system does
- Primary business or technical goal
- System boundary and ownership
- Main actors or initiating systems

## 3. Primary End-to-End Flow

Start with one Mermaid diagram for the most important system path.

Recommended summary table:

| Workflow | Trigger | Entry Point | Outcome | Notes |
| --- | --- | --- | --- | --- |
| Order creation | User submits order | `POST /orders` | Order persisted and event emitted | Main happy path |

## 4. Core Workflows

Repeat this section for each major workflow.

### Workflow: `Name`

**Purpose**
- What this workflow achieves

**Trigger**
- User action, event, scheduler, webhook, CLI command, or internal service call

**Entry Point**
- Controller, consumer, job runner, workflow engine, or queue subscriber

**Main Steps**
- Key orchestration steps in order

**Data / Event Handoffs**
- Persistent writes, reads, cache use, messages, downstream calls

**Dependencies**
- Internal components and external systems involved

**Failure / Alternate Paths**
- Only the ones that materially change understanding

**Notes**
- Assumptions, gaps, or conflicts with existing docs

## 5. Supporting Diagram or Structured Section

Add one of these when the system is non-trivial:

- System context or container diagram
- Workflow branching flowchart
- State diagram for a lifecycle-heavy entity
- ERD or shared data model
- Dependency matrix or integration table

## 6. Components and Boundaries

Summarize the major components, responsibilities, and system edges.

## 7. Data and Integration Handoffs

Summarize stores, events, queues, caches, and external services that matter to the core workflows.

## 8. Key States and Transitions

Capture lifecycle phases when behavior depends on state.

## 9. Risks, Gaps, or Operational Notes

Capture retries, idempotency, eventual consistency, missing observability, ownership gaps, or brittle dependencies when relevant.

## 10. Open Questions

List unresolved points only when they affect correctness or reader trust.

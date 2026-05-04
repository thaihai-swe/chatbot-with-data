# Feature Specification

## Metadata

- Feature name: Configuration And Learning Portfolio Controls
- Feature slug: configuration-and-learning-portfolio-controls
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-03
- Related knowledge artifact(s): `prd-requirement.md`, `artifacts/features/6.evaluation-and-experiment-dashboard/spec.md`

## Problem Statement

The product is meant to be both a working RAG lab and a portfolio artifact. Users need a clear way to inspect and change configuration, save named experiment setups, understand which pipeline features are enabled, and surface reusable learning and portfolio evidence. Without centralized configuration and explicit learning controls, the system becomes hard to reproduce, hard to teach from, and hard to present to reviewers.

## Desired Outcomes

- Users can inspect and update configuration across ingestion, retrieval, generation, safety, observability, and evaluation domains.
- Users can save and reuse named configurations and feature-toggle combinations for experiments.
- Learners and reviewers can see a visual representation of the pipeline and preserve supporting portfolio artifacts from the product.

## Success Criteria

- SC-001: A reviewer can inspect current configuration values for the major RAG subsystems from one settings experience.
- SC-002: A reviewer can save and reuse named configurations for experiments and understand which feature toggles are active.
- SC-003: A reviewer can inspect a visual pipeline that reflects optional advanced stages when they are enabled.
- SC-004: A reviewer can identify portfolio-ready supporting artifacts generated or surfaced by the product without reverse-engineering the repo.

## In Scope

- Centralized configuration visibility and editability
- Settings or configuration screen
- Named configurations and feature-toggle visibility
- Visual pipeline for enabled RAG stages
- Portfolio-facing supporting outputs surfaced by the product

## Out Of Scope

- Core ingestion, chat, safety, advanced retrieval, and evaluation behaviors already covered by earlier specs
- Detailed technical design of how configuration is stored internally

## Users And Stakeholders

- Primary users: Engineers iterating on a configurable RAG system and wanting repeatable experiment setups
- Secondary stakeholders: Reviewers who need to understand what the system can do and how the demonstrated results were produced

## User Stories And Key Scenarios

- US-001: As a learner, I inspect and update configuration values that control ingestion, retrieval, generation, safety, evaluation, and observability.
- US-002: As a learner, I save a named configuration for an experiment and reuse it later.
- US-003: As a learner, I inspect which feature toggles are enabled and see the visual pipeline update accordingly.
- US-004: As a reviewer, I use the app's settings and surfaced artifacts to understand the project's capabilities without reading internal implementation details first.

## Current Context

The repository currently exposes only a PRD and dependency list, with no implemented settings or learning surfaces. This feature comes last in sequence because it depends on the earlier specs defining which subsystems and toggles the product actually needs to expose.

## Dependencies And External Touchpoints

- DEP-001: Configurable behavior from the ingestion, chat, safety, advanced retrieval, and evaluation features
- DEP-002: Experiment records from `evaluation-and-experiment-dashboard`
- DEP-003: UI surface for settings, pipeline visualization, and artifact surfacing

## Functional Requirements

### REQ-001

Requirement:
The system must provide a centralized settings experience where users can inspect and update the major configuration domains for ingestion, duplicate detection, chunking, embeddings, vector storage, retrieval, query processing, generation, streaming, safety, evaluation, and observability across the supported configuration surfaces.

Why it matters:
The product's educational and experimental value depends on making the system's behavior inspectable and adjustable rather than buried in code.

Impacted users or scenarios:
US-001, US-004

Related success criteria:
SC-001

Priority: Must Have

Acceptance notes:
Users must be able to tell which values are currently active without opening repository files manually, and the product must support configuration through one or more of `.env`, YAML or JSON files, the settings UI, and command-line inputs for evaluation workflows when applicable. The settings surface must preserve sections for ingestion, duplicate detection, chunking, semantic chunking, parent-child retrieval, embeddings, vector database, retrieval, query expansion, query decomposition, HyDE, synonym expansion, dynamic routing, automatic collection detection, rerankers, query processing, generation, streaming, safety, prompt-injection detection, evaluation, and observability.

### REQ-002

Requirement:
The system must support named configurations or presets that users can save, inspect, reuse, and associate with experiment runs, preserving enough detail to distinguish how one preset changes ingestion, retrieval, generation, safety, evaluation, or observability behavior from another.

Why it matters:
Reproducible experimentation requires more than one-off manual edits; users need durable named setups they can compare and revisit.

Impacted users or scenarios:
US-001, US-002

Related success criteria:
SC-002

Priority: Must Have

Acceptance notes:
Saved configurations must remain distinguishable enough for users to know what changed between presets.

### REQ-003

Requirement:
The system must expose feature-toggle state for the major advanced RAG capabilities and reflect those toggles in a visual pipeline that shows which stages are active for the current configuration.

Why it matters:
Learners and reviewers need a simple way to understand the system's active retrieval and safety path without reading a full technical design.

Impacted users or scenarios:
US-003, US-004

Related success criteria:
SC-002, SC-003

Priority: Must Have

Acceptance notes:
The visual pipeline must distinguish the core path of question, pre-retrieval intelligence, classify, rewrite, expand or decompose, route, retrieve, rerank, select context, answer, cite, and evaluate from optional advanced stages when they are enabled, and the feature-toggle inventory must explicitly preserve query rewriting, query expansion, query decomposition, HyDE, synonym expansion, dynamic routing, reranking, configurable reranker selection, hybrid search, multi-hop retrieval, parent-child retrieval, semantic chunking, groundedness checks, prompt-injection detection, advanced prompt-injection detection, collection filtering, automatic collection detection, and streaming UI.

### REQ-004

Requirement:
The product must surface portfolio-ready supporting outputs, such as benchmark reports, architecture or pipeline views, example evaluation artifacts, example strategy-comparison or debug artifacts, screenshots or saved UI evidence, and other reusable evidence of system behavior.

Why it matters:
The project is explicitly intended to function as a portfolio piece, so evidence of capability needs to be accessible and reusable outside a live demo.

Impacted users or scenarios:
US-004

Related success criteria:
SC-004

Priority: Should Have

Acceptance notes:
The surfaced artifacts must remain understandable to a reviewer who did not personally run the original experiment, and the artifact inventory must preserve demo notebooks, benchmark reports, an architecture diagram or equivalent system view, an example evaluation dataset, before or after retrieval comparisons, feature-specific comparison examples, prompt-injection test results, screenshots of debug views, screenshots of the strategy comparison UI, screenshots of the experiment dashboard, and a short project README or equivalent orientation artifact.

## Non-Functional Requirements

- NFR-001 Reproducibility: The settings experience must make it easy to understand which configuration produced a given experiment or demo result.
- NFR-002 Supportability: Configuration surfaces must reduce reliance on direct file edits for normal experimentation and review.
- NFR-003 Accessibility: The visual pipeline and settings views must remain understandable to users who are learning the system for the first time.
- NFR-004 Reliability: Configuration updates and preset reuse must not silently misrepresent which feature state is active.
- NFR-005 Product Quality: The product must preserve simple local setup, laptop-friendly development, modular architecture, clear separation of components, local persistence for vectors, metadata, logs, and evaluations, and configurable fallbacks when advanced features fail.

## Constraints

- Technical constraints: This feature must expose the earlier specs' configuration domains and preserve the v1 local-first direction of an HTML, CSS, and JavaScript frontend client that calls REST API endpoints, a Python backend operated in a virtual environment, ChromaDB for vectors, SQLite for metadata, runs, evaluations, and logs, one provider first, and no heavy infrastructure requirement for the first version.
- Business constraints: The product's learning and portfolio goals are first-class, so presentation and reproducibility matter alongside raw functionality.
- Delivery constraints: This slice is sequenced after the major product behaviors because it depends on them being defined and inspectable first, but it also owns the cross-cutting settings and presentation responsibilities that make the whole product reviewable as one lab.

## Assumptions

- ASM-001: The settings experience is a control and inspection layer over existing subsystem behavior, not a substitute for the underlying feature specs.
- ASM-002: Portfolio-facing artifacts can come from prior experiment, debug, and comparison flows as long as they are surfaced clearly for reuse.

## Risks

- RISK-001 Risk: The settings screen may become overwhelming if every configuration value is exposed without clear grouping.
  Mitigation: Organize configuration by subsystem and preserve visible mapping between presets and the subsystems they affect.
- RISK-002 Risk: Portfolio evidence may feel curated or disconnected if it cannot be tied back to real runs and configurations.
  Mitigation: Require surfaced artifacts to remain linked to their originating configuration or experiment context.

## Open Questions

- Q-001 Question: Should the first review require end-user editing of every configuration value in the UI, or is a mixed approach acceptable if the UI still provides full visibility and reusable presets?
  Type: Non-blocking
  Owner: Product reviewer
  Next step: Confirm the minimum editing depth expected in the settings experience.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001
  Linked user story or scenario: US-001, US-004
  Linked success criteria: SC-001
  Validation method: Open the settings experience and verify that the required RAG subsystem configuration sections, including duplicate detection, chunking, semantic chunking, parent-child retrieval, embedding, vector storage, retrieval, query-intelligence helpers, generation, safety, evaluation, and observability, are visible from one navigable surface.
- [ ] AC-002 Linked requirement(s): REQ-002
  Linked user story or scenario: US-001, US-002
  Linked success criteria: SC-002
  Validation method: Save a named configuration, reuse it for a later run, and verify that the preset remains distinguishable from other saved setups.
- [ ] AC-003 Linked requirement(s): REQ-003
  Linked user story or scenario: US-003, US-004
  Linked success criteria: SC-002, SC-003
  Validation method: Toggle one or more advanced features and verify that the visual pipeline updates to show which optional stages are active across query transformation, routing, retrieval optimization, safety, and streaming steps.
- [ ] AC-004 Linked requirement(s): REQ-004
  Linked user story or scenario: US-004
  Linked success criteria: SC-004
  Validation method: Inspect the surfaced supporting artifacts and verify that benchmark-style artifacts, feature-comparison evidence, and UI evidence can be understood outside the original live session.

## Notes

This spec covers PRD section 7.14, UI section 7.15.8, the cross-cutting non-functional and v1 direction requirements in sections 8 and 9, and the learning and portfolio requirements in sections 11, 12, and the configuration-related parts of 13. It closes the sequence by making the entire RAG lab inspectable, repeatable, and presentable.

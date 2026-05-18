# Feature Specification

## Metadata

- Feature name: Split Chat and Embedding Configuration
- Feature slug: split-chat-embedding-config
- Owner: Claude Code (you)
- Status: Draft
- Last updated: 2026-05-17
- Related knowledge artifact(s): `proposal.md`

## Problem Statement

Currently, chat and embedding services share the same API base URL (`OPENAI_API_BASE`) and API key (`OPENAI_API_KEY`). This configuration is inflexible and prevents users from utilizing different endpoints or models for chat versus embedding tasks, especially when using hybrid setups (e.g., cloud-based chat with local embeddings, or vice-versa). This limits optimization and cost-effectiveness.

## Desired Outcomes

- Users can independently configure the API base URL and API key for chat services.
- Users can independently configure the API base URL and API key for embedding services.
- The system correctly routes requests to the appropriate configured endpoint for chat and embedding.

## Minimum Release Slice

- **What ships in the first useful release:**
  - Introduction of `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY` environment variables.
  - Logic to use these new variables for embedding service initialization.
  - Backward compatibility where if these new variables are not set, the existing `OPENAI_API_BASE` and `OPENAI_API_KEY` are used for embeddings.
- **What can wait:**
  - Support for providers other than OpenAI for the embedding-specific configuration (though the design should consider this extensibility).
  - UI elements for configuring these separate endpoints (assuming backend-only configuration for now).

## Success Criteria

- SC-001: User can successfully set `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY` in `.env` (or equivalent configuration).
- SC-002: Chat functionality continues to work correctly using `OPENAI_API_BASE` and `OPENAI_API_KEY`.
- SC-003: Embedding generation uses `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY` when provided.
- SC-004: If `EMBEDDING_API_BASE` or `EMBEDDING_API_KEY` are not provided, embedding generation correctly falls back to `OPENAI_API_BASE` and `OPENAI_API_KEY`.

## In Scope

- Modification of backend configuration loading to support new environment variables.
- Update of the embedding service initialization to utilize the new dedicated configuration.
- Preservation of existing chat functionality.
- Backward compatibility for users not providing the new variables.

## Out Of Scope

- UI for managing these configurations.
- Configuration for providers other than OpenAI (e.g., Ollama, local models) in this iteration. The configuration system should be designed with extensibility in mind but specific provider logic for embeddings beyond OpenAI is out of scope.
- Changes to the chat model configuration beyond ensuring it remains unaffected.

## Non-Goals

- Re-architecting the core LLM or embedding service abstractions.
- Implementing a feature-flag system for this change.

## Users And Stakeholders

- Primary users: Developers and administrators configuring the backend services.
- Secondary stakeholders: End-users who benefit from more flexible model deployment.

## User Stories And Key Scenarios

- **US-001:** As a developer, I want to configure a local embedding model endpoint while using a cloud-based chat model, so that I can optimize for cost and performance.
- **US-002:** As an administrator, I want to ensure that separating chat and embedding configurations does not break existing functionality, so that deployment is seamless.

### Detailed Scenarios

- **Scenario 1 (Happy Path - Separate Config):**
  - **Given:** The `.env` file contains `OPENAI_API_BASE`, `OPENAI_API_KEY`, `EMBEDDING_API_BASE` (pointing to a local embedding server), and `EMBEDDING_API_KEY`.
  - **When:** The backend service starts and processes data for embedding.
  - **Then:** The embedding service uses `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY`.
  - **And:** Chat requests are still processed using `OPENAI_API_BASE` and `OPENAI_API_KEY`.

- **Scenario 2 (Happy Path - Shared Config Fallback):**
  - **Given:** The `.env` file contains `OPENAI_API_BASE` and `OPENAI_API_KEY`, but `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY` are missing.
  - **When:** The backend service starts and processes data for embedding.
  - **Then:** The embedding service uses `OPENAI_API_BASE` and `OPENAI_API_KEY`.

- **Scenario 3 (Error State - Invalid Embedding Endpoint):**
  - **Given:** `EMBEDDING_API_BASE` is set to an invalid URL, but `OPENAI_API_BASE` is valid.
  - **When:** The embedding service attempts to initialize or make a call.
  - **Then:** An appropriate error is raised, clearly indicating the embedding endpoint is unreachable, without affecting chat functionality.

## Current Context

Existing configuration is centralized via environment variables, primarily `OPENAI_API_BASE` and `OPENAI_API_KEY` in `.env.sample` (and presumably `.env`). Services like `backend/embeddings/` and potentially parts of `backend/chat/` or `backend/ingestion/` (for embedding generation during ingestion) currently read these shared values. The goal is to introduce specific variables for embeddings while maintaining the existing behavior as a fallback.

## Dependencies And External Touchpoints

- DEP-001: Backend configuration loading mechanism (likely in `backend/config.py` or similar).
- DEP-002: Initialization logic for embedding clients (e.g., OpenAI client, Weaviate client if it uses embeddings directly).
- DEP-003: Initialization logic for chat clients.

## Functional Requirements

### REQ-001

Requirement:
Introduce `EMBEDDING_API_BASE` environment variable to specify the API endpoint for embedding models.

Why it matters:
Allows users to direct embedding requests to a different server (e.g., local Ollama, a dedicated embedding API) than the chat model.

Impacted users or scenarios:
US-001, US-002; Scenario 1, Scenario 2.

Related success criteria: SC-001, SC-003, SC-004.

Priority: Must Have

Acceptance notes:
This variable should be read and used by the embedding service.

Validation surface:
Code inspection, Unit tests, Integration tests.

### REQ-002

Requirement:
Introduce `EMBEDDING_API_KEY` environment variable to specify the API key for embedding models.

Why it matters:
Allows for separate authentication credentials for embedding services, enhancing security and flexibility.

Impacted users or scenarios:
US-001, US-002; Scenario 1, Scenario 2.

Related success criteria: SC-001, SC-003, SC-004.

Priority: Must Have

Acceptance notes:
This variable should be read and used by the embedding service.

Validation surface:
Code inspection, Unit tests, Integration tests.

### REQ-003

Requirement:
Ensure chat functionality continues to use `OPENAI_API_BASE` and `OPENAI_API_KEY` when `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY` are not provided.

Why it matters:
Guarantees backward compatibility and prevents disruption of existing chat features.

Impacted users or scenarios:
US-002; Scenario 2.

Related success criteria: SC-002, SC-004.

Priority: Must Have

Acceptance notes:
Defaulting logic must be correctly implemented.

Validation surface:
Unit tests, Integration tests.

### REQ-004

Requirement:
When `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY` are provided, the embedding service must use them exclusively.

Why it matters:
This is the core of the feature, enabling separate configurations.

Impacted users or scenarios:
US-001; Scenario 1, Scenario 3.

Related success criteria: SC-001, SC-003.

Priority: Must Have

Acceptance notes:
Embedding service initialization logic needs to prioritize these new variables.

Validation surface:
Unit tests, Integration tests.

## Non-Functional Requirements

- NFR-001 Performance: No significant performance degradation in either chat or embedding operations is acceptable.
- NFR-002 Reliability: The system should gracefully handle missing or invalid `EMBEDDING_API_BASE` / `EMBEDDING_API_KEY` by falling back to shared defaults or raising clear errors, without impacting chat.
- NFR-003 Security or Privacy: API keys must be handled securely and not exposed in logs or non-secure contexts.

## Constraints

- Technical constraints: Modifications should be confined to configuration loading and service initialization points. Avoid deep architectural changes.
- Business constraints: Minimize development time; leverage existing patterns for configuration management.
- Delivery constraints: Aim for a single, focused release.

## Assumptions

- ASM-001: The underlying embedding client libraries support dynamic configuration of API base URLs and keys.
- ASM-002: All services requiring embedding model access are identifiable and can be updated to use the new configuration.

## Risks

- RISK-001 Risk: Failure to correctly implement fallback logic could break existing functionality.
  Mitigation: Thorough unit and integration testing of configuration loading and service initialization.
- RISK-002 Risk: Introduction of new environment variables might conflict with existing ones or patterns.
  Mitigation: Careful choice of variable names and adherence to existing naming conventions.

## Open Questions

- Q-001 Question: What is the exact name for the embedding API key variable? (`EMBEDDING_API_KEY` is proposed, but needs confirmation).
  Type: Blocking
  Owner: User
  Next step: User confirmation.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001, REQ-003, REQ-004
  Linked user story or scenario: US-001, US-002; Scenario 1, Scenario 2, Scenario 3
  Linked success criteria: SC-001, SC-002, SC-003, SC-004
  Validation method: Unit tests for configuration loading and service initialization, integration tests verifying separate endpoint usage.
  Proof target: Specific test cases in `tests/backend/`.

- [ ] AC-002 Linked requirement(s): REQ-002, REQ-003, REQ-004
  Linked user story or scenario: US-001, US-002; Scenario 1, Scenario 2, Scenario 3
  Linked success criteria: SC-001, SC-002, SC-003, SC-004
  Validation method: Unit tests for configuration loading and service initialization, integration tests verifying separate API key usage.
  Proof target: Specific test cases in `tests/backend/`.

## Notes

This feature aims to provide greater flexibility in configuring LLM services by decoupling chat and embedding endpoints. The primary mechanism will be through new environment variables, with robust fallback and error handling.

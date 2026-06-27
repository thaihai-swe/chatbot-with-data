# Tool Safety and Concurrency

A well-engineered harness restricts what tools can do and how they interact to prevent destructive interference.

## 1. Sandbox Patterns
*   Where possible, execute tests and builds in isolated environments to prevent side effects on the main working tree.
*   For destructive operations (e.g., database migrations), ensure clear warnings and rollback mechanisms are documented.

## 2. Tool Approval Policies
*   **Auto-Approve:** Read-only tools (view file, grep, list dir) and local unit tests.
*   **Require Approval:** Destructive file modifications outside the feature scope, external API calls, or wide-ranging refactors.

## 3. Concurrency Control
*   Prevent parallel writes to the same file.
*   If subagents are working concurrently, they must operate on distinct, non-overlapping boundaries.

## 4. Error Handling
*   Tools should fail loudly. Silent failures (e.g., a test runner crashing without output) lead the agent to assume success.
*   Capture stack traces and stderr, and ensure they are presented clearly to the agent.

## 5. Permission Boundaries
*   Define what directories an agent is allowed to touch. E.g., `spec-requirements` should only touch `artifacts/features/`, never `src/`.

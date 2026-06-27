# Memory Persistence Patterns

Agent memory is volatile across context windows and sessions. A robust harness relies on durable state stored in the file system.

## 1. Constitution vs. Knowledge Base
*   **Constitution (`memories/repo/core-policies.md`)**: Contains normative, repo-wide rules (the "musts"). Examples: Security guardrails, mandatory formatting rules, quality gates.
*   **Knowledge Base (`memories/repo/project-knowledge-base.md`)**: Contains descriptive facts (the "whats" and "hows"). Examples: Tech stack details, architecture boundaries, common conventions.

## 2. Session Progress Logs
*   A `progress.md` file tracks what was done in a specific session.
*   It acts as an externalized "short-term memory" that survives context condensation and model swaps.

## 3. Handoff Artifacts
*   When a session ends, a `handoff.md` bridges the gap.
*   It must contain the exact state, blockers, and the specific prompt needed to resume.

## 4. Decision Durability
*   Never leave important product or technical decisions in the chat history.
*   If a choice materially affects the outcome, record it in `spec.md` (for product) or `plan.md` (for tech).

## 5. Memory Promotion
*   Local findings (e.g., "this specific API endpoint is flaky") should be promoted to the Knowledge Base if they are likely to affect future features.
*   Use `context-memory` to route findings appropriately.

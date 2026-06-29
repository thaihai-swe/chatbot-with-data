# Analysis: Remove Playground and Strategy Comparison

## Metadata

- Investigation name: Remove Playground and A/B Analysis Strategy Comparison
- Feature or issue slug: 6.0-remove-playground
- Owner: Antigravity
- Last updated: 2026-06-29

## Scope

- **What is being investigated:** Identification of all frontend/backend files, components, routes, styles, documentation, and metadata associated with the Playground and A/B Analysis Strategy Comparison features that must be removed.
- **What is explicitly out of scope:** Modifying or removing core chat retrieval modes, chat routers, or LLM-as-a-judge system evaluations (which are used by the Sanity Check tool on the Evaluation Screen).

## Current State

- **Observed current behavior:** 
  - The Playground screen `/playground` allows side-by-side comparison of different retrieval configurations.
  - It uses [Playground.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/screens/Playground.jsx) and [PlaygroundPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/PlaygroundPanel.jsx).
  - The [ExperimentComparison.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ExperimentComparison.jsx) component is defined but currently unused.
  - These tools are linked via the main application header navbar.
- **Relevant boundaries or components:**
  - NavLink in [App.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/App.jsx) (header).
  - Route in [App.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/App.jsx) (router switch).
- **Unchanged behavior that must be preserved:**
  - The Evaluation screen (`/evaluation`), settings screen (`/settings`), document library (`/`), and chat workspace (`/chat`) must remain fully functional.
  - Core backend query endpoints `/chat/sessions` and `/chat/send` must remain untouched as they serve the primary workspace.

## Decision-Ready Summary

- **What matters most:** Clean deletion of all unused screens and components, ensuring router alignment in `App.jsx` is updated without breaking layout states.
- **Strongest supported conclusion:** The Playground / Strategy Comparison features can be entirely removed without any impact on backend query processing or ingestion. All backend APIs are shared and will not break.
- **Single next proving step:** Draft requirements detailing exact component evictions and route deletions.

## Findings

*   **Finding ID: FND-001**
    *   *Evidence:* `grep` search for `ExperimentComparison` shows that it is defined in [ExperimentComparison.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ExperimentComparison.jsx) but never imported in any screen or active module.
    *   *Type:* Fact
*   **Finding ID: FND-002**
    *   *Evidence:* Grep for `/playground` and `PlaygroundScreen` shows they are imported and routed solely in [App.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/App.jsx).
    *   *Type:* Fact

## Risks And Unknowns

- **Risk:** Removing references to `playground` or `strategy comparison` from documentation might leave dead links.
  - *Why it matters:* Poor documentation quality for new onboarders.
  - *Next proving step:* Scan documentation files (`README.md`, `onboarding.md`, `architecture.md`) and strip out references.

## Recommendation

- **Next skill or artifact:** `/spec-requirements`
- **Why:** Requirements are now clearly identified and bounded. We can define the spec directly.
- **Exact next prompt or action:** Generate requirements spec.md and transition the feature phase to Requirements.

# Feature Specification: Remove Playground and Strategy Comparison

## Metadata

- Feature name: Remove Playground and Strategy Comparison
- Feature slug: 6.0-remove-playground
- Delivery profile: Simple
- Owner: Antigravity
- Status: Approved
- Last updated: 2026-06-29
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/6.0-remove-playground/analysis.md)

## Problem Statement

The Playground and A/B Strategy Comparison features are no longer needed and add unnecessary complexity to the UI. The user wants them completely removed from the codebase and user interface.

## Desired Outcomes

- **Outcome 1:** Simplified UI navigation and smaller client bundle size by completely removing Playground, PlaygroundPanel, and ExperimentComparison components and routes.

## Minimum Release Slice

- **What ships:** Complete removal of route registration, nav links, components, and documentation references in one release.
- **What can wait:** None.

## Success Criteria

- **SC-001:** Navigation menu has no "Playground" link.
- **SC-002:** Navigating to `/playground` displays the default fallback route or blank instead of loading the Playground screen.
- **SC-003:** Files `Playground.jsx`, `PlaygroundPanel.jsx`, and `ExperimentComparison.jsx` are removed.
- **SC-004:** All pytests and gate checks pass.

## In Scope

- Deleting [Playground.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/screens/Playground.jsx).
- Deleting [PlaygroundPanel.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/PlaygroundPanel.jsx).
- Deleting [ExperimentComparison.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/components/ExperimentComparison.jsx).
- Removing router links and imports from [App.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/App.jsx).
- Updating documentation and memory indices to remove references to the deleted files and features.

## Out Of Scope

- Removing any backend RAG modes or query processing logic (they remain valid for other parts of the application).
- Removing the System Evaluation screen `/evaluation` (Sanity checks).

## Users And Stakeholders

- **Primary users:** App Users
- **Secondary stakeholders:** System Developers

## User Stories And Key Scenarios

- **US-001:** As a user, I want the navbar to not show the "Playground" link so that the interface remains clean.

### Detailed Scenarios

- **Scenario 1 (Happy Path - Nav Link Removal):**
  - **Given:** The user is on the main Document Library page.
  - **When:** The user inspects the header navigation links.
  - **Then:** The "Playground" link is not displayed, but "Collections", "Chat", "Evaluation", and "Settings" are still visible.

- **Scenario 2 (Happy Path - Route Removal):**
  - **Given:** The user types `/playground` directly in the browser address bar.
  - **When:** The route loads.
  - **Then:** The page does not render the strategy comparison panels.

## Current Context

- **Current behavior summary:** The application currently routes `/playground` to `PlaygroundScreen` which compares strategies.
- **Impacted boundaries:** Frontend routing and navigation bar.
- **Preserved behavior:** System evaluation (`/evaluation`) and chat workspace (`/chat`) must not be affected.
- **Brownfield risk rating:** Low.

## Gray-Area Decisions

- **Locked decisions:** Playground is fully removed.

## Dependencies And External Touchpoints

- **DEP-001:** Router path definitions in `App.jsx`.

## Functional Requirements

### REQ-001: Evict Playground Route and Components
- **Requirement:** Completely remove references to and registration of the Playground screen, its layout, and sub-panels.
- **Why it matters:** Cleans up navigation and eliminates dead code.
- **Impacted users or scenarios:** US-001
- **Related success criteria:** SC-001, SC-002, SC-003
- **Priority:** Must Have
- **Validation surface:** Frontend navigation and routing checks.

### REQ-002: Evict Experiment Comparison Components
- **Requirement:** Delete the unused `ExperimentComparison.jsx` component.
- **Why it matters:** Prevents compilation/bundler baggage and clutter.
- **Impacted users or scenarios:** Developer cleanliness.
- **Related success criteria:** SC-003
- **Priority:** Must Have
- **Validation surface:** Filesystem clean check.

### REQ-003: Update Documentation & Metadata
- **Requirement:** Strip playground references from `README.md`, `onboarding.md`, and memories/domain files.
- **Why it matters:** Keeps documentation fresh and aligned with codebase reality.
- **Impacted users or scenarios:** Developers
- **Related success criteria:** SC-004
- **Priority:** Should Have
- **Validation surface:** Documentation search checks.

## Non-Functional Requirements

- **NFR-001 Security or Privacy:** No endpoints are exposed or changed.
  - *Linked ACs:* AC-003

## Constraints

- **Technical:** None.

## Assumptions

- **ASM-001:** No other components in the codebase rely on `PlaygroundScreen` or `ExperimentComparison`.

## Risks

- **RISK-001:** Accidental breakage of routing structure in `App.jsx`.
  - *Mitigation:* Run local compiler check and route navigation manually to verify layout continuity.

## Acceptance Criteria

- [ ] AC-001: Navbar link and Route path to `/playground` are deleted from [App.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/App.jsx).
  - *Linked scenario:* Scenario 1, Scenario 2
  - *Validation method:* Inspection of `App.jsx`.
  - *Proof target:* Git diff check.
- [ ] AC-002: Playground and comparison source files are deleted from the disk.
  - *Linked scenario:* US-001
  - *Validation method:* Verify file existence checks return false.
  - *Proof target:* Directory check.
- [ ] AC-003: All existing test suites pass.
  - *Linked scenario:* None
  - *Validation method:* Execution of `pytest` and `gate-runner.sh`.
  - *Proof target:* Green terminal output.

## Related ADRs

None.

## Notes

None.

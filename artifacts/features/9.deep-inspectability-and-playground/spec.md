# Feature Specification: Deep Inspectability and Playground

## Metadata

- Feature name: Deep Inspectability and Playground
- Feature slug: deep-inspectability-and-playground
- Owner: Gemini CLI
- Status: Approved
- Last updated: 2026-05-17
- Related knowledge artifact(s): `prd-requirement.md`, `proposal.md`

## Problem Statement

While the RAG Knowledge Base Lab allows users to chat with documents, the "black box" nature of retrieval makes it difficult for learners to verify the AI's claims or understand how different configurations (like HyDE or Hybrid search) actually impact the results. Users need tools to inspect the underlying data and compare strategies side-by-side to gain intuition about RAG patterns.

## Desired Outcomes

- Users can verify the source of any claim by inspecting the exact text chunk and its metadata.
- Users can experiment with different RAG strategies in a "Playground" to see real-time differences in retrieval performance and answer quality.

## Minimum Release Slice

- **Citation Detail View:** A modal accessible from chat citations showing chunk text, score, and document metadata.
- **Strategy Comparison Playground:** A side-by-side view for a single query using two different configurations.
- **Config Toggles:** Support for Retrieval Mode, HyDE, and Query Expansion in the Playground.
- **Visual Diffing:** Highlighting of chunks present in one strategy but missing in the other based on `chunk_id`.

## Success Criteria

- SC-001: Every citation in the Chat UI can be clicked to open a detail view.
- SC-002: The Playground UI executes two parallel retrieval/generation requests for a single input query.
- SC-003: Chunks retrieved by both strategies in the Playground are visually distinguished from unique chunks.

## In Scope

- **Citation Modal:** Displaying `chunk_text`, `score`, `document_title`, `document_id`, and `source_url`.
- **Playground View:** Dual-panel UI for comparing "Strategy A" and "Strategy B".
- **Frontend Parallelism:** Making two simultaneous calls to the existing `POST /chat` endpoint.
- **Strict Diffing:** Using `chunk_id` to identify overlapping and unique results.

## Out Of Scope

- Persistent Playground runs (history is not saved).
- Backend-side comparison logic (handled by frontend state).
- Multi-query comparison (only one query at a time).
- Comparison of more than two strategies simultaneously.

## Non-Goals

- Providing a leaderboard for strategies.
- Automated optimization of RAG parameters.

## Users And Stakeholders

- **Primary users:** Software engineers learning AI concepts, Portfolio reviewers.
- **Secondary stakeholders:** Hiring managers.

## User Stories And Key Scenarios

- **US-001 (Verification):** As a learner, I want to click a citation and see the exact chunk text so I can confirm the AI isn't hallucinating.
- **US-002 (Experimentation):** As a developer, I want to compare "Semantic" vs "Hybrid" search side-by-side to see which one retrieves the more relevant chunks for my specific query.

### Detailed Scenarios

- **Scenario 1 (Inspecting a Citation):**
  - **Given:** A chat session with an answer containing a citation `[1]`.
  - **When:** The user clicks the citation tag.
  - **Then:** A modal opens showing the raw text of the chunk, the retrieval score (e.g., 0.85), and the source document title.
- **Scenario 2 (Playground Comparison):**
  - **Given:** The Playground screen with two panels.
  - **When:** User enters "How do I install the CLI?", sets Panel A to "Semantic" and Panel B to "Hybrid + HyDE", and clicks "Run".
  - **Then:** Both panels load independently; Panel A shows 5 chunks and an answer; Panel B shows 5 chunks and a different answer; overlapping chunks are highlighted in a neutral color, unique chunks in a contrasting color.

## Current Context

The system currently has a `POST /chat` endpoint that returns `answer` and `citations` (which include `chunk_id`, `score`, `metadata`, etc.). The UI renders these as simple tags. The backend supports the necessary toggles (HyDE, Query Expansion) via the `ChatRequest` schema.

## Dependencies And External Touchpoints

- **Backend API:** Depends on `POST /chat` returning complete citation metadata (which it already does).
- **Frontend State:** Requires managing two independent "chat result" states in the Playground.

## Functional Requirements

### REQ-001: Citation Detail View
- **Requirement:** Clicking a citation in any chat message must open a modal.
- **Why it matters:** Provides transparency and ground-truth verification.
- **Impacted users:** US-001.
- **Priority:** Must Have.
- **Acceptance notes:** Must include chunk text, score, and document title.
- **Validation surface:** UI Manual Check.

### REQ-002: Playground Side-by-Side View
- **Requirement:** A dedicated UI screen with two vertical panels, each with its own configuration controls.
- **Why it matters:** Enables direct experimentation.
- **Impacted users:** US-002.
- **Priority:** Must Have.
- **Acceptance notes:** Configurations must include Mode, HyDE, and Expansion.
- **Validation surface:** UI Manual Check.

### REQ-003: Front-End Execution & Diffing
- **Requirement:** The Playground must trigger two `POST /chat` calls and diff the results by `chunk_id`.
- **Why it matters:** Keeps backend simple while providing powerful visual feedback.
- **Priority:** Must Have.
- **Acceptance notes:** Chunks with the same `chunk_id` in both panels must be visually marked as "Matches".
- **Validation surface:** Network Log (confirming 2 calls), UI Visual Check.

## Non-Functional Requirements

- **NFR-001 Performance:** Both playground requests should fire simultaneously to minimize total wait time.
- **NFR-005 Observability:** Errors in one playground panel should not prevent the other panel from rendering its results.

## Constraints

- **API Rate Limits:** Running dual queries increases token consumption and potential rate limiting from providers like OpenAI.

## Assumptions

- **ASM-001:** The existing `POST /chat` response already contains enough chunk metadata to populate the Detail View (verified against `backend/schemas/chat.py`).

## Risks

- **RISK-001 Screen Real Estate:** Showing two results and two sets of chunks side-by-side may be cramped.
  - **Mitigation:** Use a "Stacked" view for mobile or allow collapsing the "Chunks" section to focus on the "Answer".

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001
  - Validation method: Click citation tag `[1]` in Chat.
  - Proof target: Modal displays chunk text and "Score: 0.XX".
- [ ] AC-002 Linked requirement(s): REQ-002
  - Validation method: Open Playground, enter query, click "Run".
  - Proof target: Two independent loaders appear and resolve to two different answers/chunk lists.
- [ ] AC-003 Linked requirement(s): REQ-003
  - Validation method: Use a query that returns overlapping chunks in Playground.
  - Proof target: Overlapping chunks are highlighted (e.g., with a green border or "Matched" badge).

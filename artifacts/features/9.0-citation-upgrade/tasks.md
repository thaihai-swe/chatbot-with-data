# Task Breakdown

## Metadata
- Feature name: Citation Upgrade & UI Anchoring
- Feature slug: 9.0-citation-upgrade
- Date: 2026-07-01
- Status: Not Started

## Heuristic Citations
- None.

## Tasks

### Phase 1: Backend Prompt & Parser Upgrades
Goal: Upgrade system prompt instructions and flexible backend citation matching.
Acceptance criteria covered: AC-001, AC-002
Independent proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_citations.py`
Completion criteria:
- [ ] CC-001 System prompt requires factual claims to be strictly cited.
- [ ] CC-002 Backend regex parses both legacy and short-form citations successfully.

Tasks:
- [ ] TASK-001
  Status: Not Started
  Routing: AFK
  Summary: Modify system prompt instructions in prompts.py to enforce strict citation formatting.
  Outcome enabled: Accurate generation-time citations.
  Plan reference: Phase 1
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  User story: US-001 (P1)
  Affected file(s) or module(s): `backend/chat/prompts.py`
  Depends on: None
  Can run in parallel: no
  Proving command or proof: Check system prompt text in `prompts.py`.
  Validation evidence: 
  Session note: 

- [ ] TASK-002
  Status: Not Started
  Routing: AFK
  Summary: Update CitationService regex to match `\[(?:Source\s+)?([^\]]+)\]` and add unit tests to verify matching for both format types.
  Outcome enabled: Backward-compatible parsing of citations on the backend.
  Plan reference: Phase 1
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  User story: US-002 (P1)
  Affected file(s) or module(s): `backend/chat/citations.py`, `backend/tests/chat/test_citations.py`
  Depends on: TASK-001
  Can run in parallel: no
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_citations.py`
  Validation evidence: 
  Session note: 

---

### Phase 2: Frontend Regex & Context State
Goal: Implement unified badge parsing, short label rendering, and workspace context updates.
Acceptance criteria covered: AC-003, AC-004
Independent proof: Manual inspection of React context actions and badge labels.
Completion criteria:
- [ ] CC-003 Inline chat badges display only normalized short labels `[Source N]`.
- [ ] CC-004 Workspace context successfully manages active document and chunk selections.

Tasks:
- [ ] TASK-003
  Status: Not Started
  Routing: AFK
  Summary: Modify ChatPanel.jsx regex to `\[(?:Source\s+)?([^\]]+)\]` and normalize inline badge display to `[Source N]` (avoiding long document titles).
  Outcome enabled: Short inline badges to maintain text readability.
  Plan reference: Phase 2
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  User story: US-001 (P1)
  Affected file(s) or module(s): `frontend/src/components/ChatPanel.jsx`
  Depends on: TASK-002
  Can run in parallel: no
  Proving command or proof: Run the app and verify generated message text contains short badges only.
  Validation evidence: 
  Session note: 

- [ ] TASK-004
  Status: Not Started
  Routing: AFK
  Summary: Extend WorkspaceContext.jsx state to track activeChunkId, add setActiveChunkId action, and wire it to expand the left panel when set.
  Outcome enabled: Multi-panel state coordination on citation clicks.
  Plan reference: Phase 2
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  User story: US-002 (P1)
  Affected file(s) or module(s): `frontend/src/context/WorkspaceContext.jsx`, `frontend/src/components/ChatPanel.jsx`
  Depends on: TASK-003
  Can run in parallel: no
  Proving command or proof: Trace context action dispatch on citation badge click.
  Validation evidence: 
  Session note: 

---

### Phase 3: Visual Highlight & Anchoring
Goal: Highlight and auto-scroll target chunk in SourceBrowser, clear highlights on collapse, and support disabled status for invalid citations.
Acceptance criteria covered: AC-005, AC-006, AC-007
Independent proof: Manual verification of visual scrolling, panel highlights, and cleanup on collapse.
Completion criteria:
- [ ] CC-005 Chunk items auto-scroll and highlight inside SourceBrowser upon badge click.
- [ ] CC-006 Highlights reset cleanly when closing SourceBrowser or collapsing the sources panel.
- [ ] CC-007 Invalid/mismatched citation indices render as disabled badges.

Tasks:
- [ ] TASK-005
  Status: Not Started
  Routing: HITL
  Summary: Update SourceBrowser.jsx to select and scroll the active chunk element matching activeChunkId into view.
  Outcome enabled: End-to-end visual citation anchoring.
  Plan reference: Phase 3
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  User story: US-002 (P2)
  Affected file(s) or module(s): `frontend/src/components/SourceBrowser.jsx`
  Depends on: TASK-004
  Can run in parallel: no
  Proving command or proof: Click citation badge in chat panel -> observe scroll and focus alignment in SourceBrowser.
  Validation evidence: 
  Session note: 

- [ ] TASK-006
  Status: Not Started
  Routing: AFK
  Summary: Add visual border and highlight styling in styles.css and implement disabled badge styling for unmatched/invalid citation tags.
  Outcome enabled: Visual highlight feedback and graceful handling of invalid citations.
  Plan reference: Phase 3
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  User story: US-001 (P2)
  Affected file(s) or module(s): `frontend/src/styles.css`, `frontend/src/components/ChatPanel.jsx`
  Depends on: TASK-005
  Can run in parallel: no
  Proving command or proof: Audit visual focus styling; verify fabricated invalid citations render as disabled plain text.
  Validation evidence: 
  Session note: 

- [ ] TASK-007
  Status: Not Started
  Routing: AFK
  Summary: Reset activeChunkId to null when manually collapsing left Sources panel or closing the SourceBrowser.
  Outcome enabled: Reset of active highlight state to prevent stale focus.
  Plan reference: Phase 3
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  User story: US-002 (P2)
  Affected file(s) or module(s): `frontend/src/components/SourcesPanel.jsx`, `frontend/src/components/SourceBrowser.jsx`
  Depends on: TASK-005
  Can run in parallel: no
  Proving command or proof: Collapse left panel, re-expand, verify no highlighted chunk remains.
  Validation evidence: 
  Session note: 

## Completion Notes
- What was delivered:
- What was deferred:
- What needs follow-up:

## Resume Notes
- Current phase: Setup & Backend
- Next recommended task: TASK-001
- Active blocker: None
- Last validation evidence added: None
- Exact next command or proof to run: None

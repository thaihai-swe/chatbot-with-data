# Status: 9.0 Citation Upgrade

# Current Phase: Plan Approved

# Complexity: Complex

# 🧪 Intake

- *Input type:* new_initiative
- *Risk flags:* none
- *One-line restatement:* Upgrade, enhance, and implement generation-time citation enforcement and UI/UX anchoring improvements based on the Production RAG Audit findings.
- *Affected core-zero/specs:* `backend/chat/citations.py`, `backend/chat/service.py`, `backend/chat/prompts.py`, frontend chat panels.
- *Reasoning:* The production RAG audit identified a design gap: our system uses post-hoc regex citation extraction, whereas Notebook LM enforces token-level citation at generation time. We need to upgrade our RAG pipeline prompts and citation extraction, and improve user interaction in the UI (anchoring/hover behavior).

# Active Task
None

# High-Level Progress
- [x] Research complete
- [x] Spec approved
- [x] Plan approved
- [ ] Implementation complete
- [ ] Verification complete

# Blockers
None

# Next Step
Run `/spec-implement` to start coding and testing tasks in order.

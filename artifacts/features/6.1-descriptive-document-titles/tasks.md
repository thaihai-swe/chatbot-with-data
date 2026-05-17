# Task Breakdown: 6.1 Descriptive Document Titles

## Metadata

- Feature name: Descriptive Document Titles
- Related spec: artifacts/features/6.1-descriptive-document-titles/spec.md
- Related plan: artifacts/features/6.1-descriptive-document-titles/plan.md
- Related design: N/A
- Owner: Gemini CLI
- Last updated: 2026-05-17

## Rules

- Keep each task small and testable.
- TDD Requirement: Identify failing test/proof before fix.

## Phase 1: Dispatcher and Extractor Updates

Goal: Enable extraction logic to accept and prioritize fallback titles.

Completion criteria:

- [ ] CC-001: Extractors use `fallback_title` if provided and metadata is missing.

Tasks:

- [X] TASK-001
  Status: Done
  Summary: Create a reproduction unit test for `TextExtractor` and `PdfExtractor`.
  Outcome enabled: Scenario 1, Scenario 2.
  Plan reference: Phase 1.
  Linked requirement(s): REQ-001, REQ-002.
  Linked acceptance criteria: AC-001, AC-002, AC-003.
  Ownership boundary: `backend/tests/unit/test_6_1_repro.py`.
  Affected file(s) or module(s): `backend/extractors/`.
  Depends on: None.
  Can run in parallel: No.
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/unit/test_6_1_repro.py`
  Validation evidence: 3 passed (confirming UUID titles and TypeError for new param).
  Session note: Successfully reproduced the issue and confirmed the lack of parameter support.

- [X] TASK-002
  Status: Done
  Summary: Update `ExtractorDispatcher.extract` and child extractors to accept `fallback_title`.
  Outcome enabled: Scenario 1.
  Plan reference: Phase 1.
  Linked requirement(s): REQ-001.
  Linked acceptance criteria: AC-001.
  Ownership boundary: `backend/extractors/`.
  Affected file(s) or module(s): `backend/extractors/dispatcher.py`, `backend/extractors/pdf_extractor.py`, `backend/extractors/text_extractor.py`.
  Depends on: TASK-001.
  Can run in parallel: No.
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/unit/test_6_1_repro.py` (Verify `test_text_extractor_fails_to_accept_fallback_title` fails).
  Validation evidence: 1 failed, 2 passed (confirming TypeError no longer raised).
  Session note: Signatures updated successfully.
- [X] TASK-003
  Status: Done
  Summary: Implement title selection logic in `PdfExtractor` and `TextExtractor`.
  Outcome enabled: Scenario 2, Scenario 3.
  Plan reference: Phase 1, Phase 3.
  Linked requirement(s): REQ-002.
  Linked acceptance criteria: AC-002, AC-003.
  Ownership boundary: `backend/extractors/`.
  Affected file(s) or module(s): `backend/extractors/pdf_extractor.py`, `backend/extractors/text_extractor.py`.
  Depends on: TASK-002.
  Can run in parallel: Yes [P].
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/unit/test_6_1_repro.py` (Should PASS).
  Validation evidence: 3 passed (confirming fallback and metadata priority).
  Session note: Logic implemented and verified.
- [X] TASK-004
  Status: Done
  Summary: Update `IngestionService.process_ingestion_attempt` to pass `submitted_filename`.
  Outcome enabled: US-001, US-002.
  Plan reference: Phase 2.
  Linked requirement(s): REQ-001.
  Linked acceptance criteria: AC-001.
  Ownership boundary: `backend/ingestion/service.py`.
  Affected file(s) or module(s): `backend/ingestion/service.py`.
  Depends on: TASK-003.
  Can run in parallel: No.
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/integration/test_6_1_ingestion.py`
  Validation evidence: 1 passed (confirming filename passed to dispatcher).
  Session note: Integration successful.

- [ ] TASK-005
  Status: In Progress
  Summary: Run full integration verification with PDF and Text files.
Goal: Verify end-to-end behavior and ensure no regressions.

Completion criteria:

- [ ] CC-003: Full ingestion flow produces descriptive titles.

Tasks:

- [X] TASK-005
  Status: Done
  Summary: Run full integration verification with PDF and Text files.
  Outcome enabled: All.
  Plan reference: Phase 2, Phase 3.
  Linked requirement(s): REQ-001, REQ-002.
  Linked acceptance criteria: AC-001, AC-002, AC-003.
  Ownership boundary: System-wide.
  Affected file(s) or module(s): N/A.
  Depends on: TASK-004.
  Can run in parallel: No.
  Proving command or proof: `PYTHONPATH=backend pytest backend/tests/`
  Validation evidence: 4 passed.
  Session note: All tests pass, feature verified.

## Resume Notes

- Current phase: Planning
- Next recommended task: TASK-001
- Active blocker: None.
- Last validation evidence added: None.
- Exact next command or proof to run: `PYTHONPATH=backend pytest backend/tests/unit/test_6_1_repro.py` (after creating the test).

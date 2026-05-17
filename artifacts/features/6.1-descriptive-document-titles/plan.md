# Implementation Plan: 6.1 Descriptive Document Titles

## Metadata

- Feature name: Descriptive Document Titles
- Related spec: artifacts/features/6.1-descriptive-document-titles/spec.md
- Related requirements review: artifacts/features/6.1-descriptive-document-titles/requirements-review.md
- Related design: N/A (Lean plan)
- Owner: Gemini CLI
- Status: Draft
- Last updated: 2026-05-17

## Plan Summary

The execution approach involves propagating the `submitted_filename` from the `IngestionService` through the `ExtractorDispatcher` to the individual extractors (`PdfExtractor`, `TextExtractor`). The extractors will use this filename as a fallback title when internal metadata (like PDF 'Title') is missing. This replaces the current behavior where the UUID-based storage path was used to derive titles.

## Execution Context

- Relevant repository patterns for execution: Service layer (`backend/ingestion/service.py`), Dispatcher pattern (`backend/extractors/dispatcher.py`), and specialized extractors.
- Brownfield execution constraints: Files must remain UUID-named in storage to avoid collisions.
- Unchanged behavior: URL ingestion title logic remains as-is. Database schema for `Document` and `IngestionAttempt` is sufficient.

## First Delivery Slice

- Smallest useful slice: Update `TextExtractor` and `ExtractorDispatcher` to handle `fallback_title`.
- Why this slice goes first: Simplest path to verify the title propagation without PDF metadata complexity.
- What proof should exist when this slice is done: A unit test verifying that `TextExtractor` uses the provided `fallback_title`.

## Technical Approach

- Chosen approach: Functional parameter passing. Update `extract` methods to accept `fallback_title: str | None = None`.
- Architectural or integration shape: `IngestionService` -> `ExtractorDispatcher` -> `BaseExtractor`.
- Key interfaces or contracts:
    - `ExtractorDispatcher.extract(..., fallback_title=...)`
    - `PdfExtractor.extract(..., fallback_title=...)`
    - `TextExtractor.extract(..., fallback_title=...)`

## Requirements And Constraints

- REQ-001 Capture Submitted Filename:
  Implementation note: Modify `IngestionService.process_ingestion_attempt` to pass `attempt["submitted_filename"]` (stemmed) to the dispatcher.
  Planned validation: Integration test verifying document creation with correct title.
  Linked scenario or outcome: US-001.
- REQ-002 Descriptive Title Selection:
  Implementation note: Update logic in `PdfExtractor` to check `pdf_metadata.get("Title")` first, then `fallback_title`.
  Planned validation: Unit tests with PDF samples (with and without metadata titles).
  Linked scenario or outcome: Scenario 2, Scenario 3.

## Impacted Areas

- Services or modules: `backend/ingestion/service.py`, `backend/extractors/*.py`
- APIs or interfaces: Internal service calls.
- UI or UX: Indirectly improved by descriptive titles in existing UI.

## Protected Behavior

- Behavior that must not regress: UUID-based storage for files.
  Protection approach: Do not modify `LocalStorage.save_upload` or how `artifact_path` is handled.

## Affected Files

- FILE-001 `backend/extractors/dispatcher.py`: Update `extract` signature.
- FILE-002 `backend/extractors/pdf_extractor.py`: Update `extract` signature and title logic.
- FILE-003 `backend/extractors/text_extractor.py`: Update `extract` signature and title logic.
- FILE-004 `backend/ingestion/service.py`: Update call to `dispatcher.extract`.

## Dependencies

- DEP-001 Internal dependency: `IngestionAttempt` must have `submitted_filename` populated.
  Why it matters: It's our source of truth for the descriptive title.

## Implementation Prerequisites

- None.

## Execution Phases

### Phase 1: Core Propagation

Goal: Update dispatcher and extractors to accept and use `fallback_title`.
Enabled user scenario(s) or outcome(s): Scenario 1.

Entry proof: `backend/extractors/dispatcher.py` exists.
Exit proof: Unit tests for `TextExtractor` pass with custom titles.

Completion criteria:

- CC-001: `ExtractorDispatcher.extract` and all child extractors accept `fallback_title`.

### Phase 2: Ingestion Service Integration

Goal: Pass the original filename from the ingestion attempt record.
Enabled user scenario(s) or outcome(s): US-001, Scenario 3.

Entry proof: Phase 1 complete.
Exit proof: Integration test uploading a text file results in a document with the correct title.

Completion criteria:

- CC-002: `IngestionService` passes the correct fallback title.

### Phase 3: PDF Metadata Refinement

Goal: Ensure PDF metadata titles are preferred over filenames.
Enabled user scenario(s) or outcome(s): Scenario 2.

Entry proof: Phase 2 complete.
Exit proof: Test with PDF containing metadata title "Report" results in document title "Report".

Completion criteria:

- CC-003: `PdfExtractor` prioritizes metadata titles.

## Validation Strategy

- TEST-001 Unit tests: Update `backend/tests/unit/test_extractors.py` (if exists) or create new ones for title logic.
- TEST-002 Integration tests: Run a full ingestion flow via a script or existing integration tests.
- TEST-004 Manual verification: Upload files through the UI and check titles in the Document Library.

## Traceability Matrix

- Scenario or outcome -> Plan phase(s): US-001 -> Phase 2; Scenario 2 -> Phase 3.
- REQ-001 -> Plan phase / task IDs: Phase 1, Phase 2.
- REQ-002 -> Plan phase / task IDs: Phase 3.
- AC-001 -> Validation step(s): Phase 2 Integration Test.
- AC-002 -> Validation step(s): Phase 3 PDF Test.

## Rollout Plan

- Release approach: Direct update to ingestion logic. No database migration required.
- Backward compatibility notes: Existing ingestion attempts will continue to work as `fallback_title` is optional.

## Rollback Plan

Revert code changes in `backend/extractors/` and `backend/ingestion/service.py`.

## Risks And Mitigations

- RISK-001: Filename with weird characters.
  Mitigation: `title_from_filename` and stemming should handle most cases. `submitted_filename` is already sanitized by FastAPI/Browsers.

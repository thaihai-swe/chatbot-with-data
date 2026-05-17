# Feature Specification: 6.1 Descriptive Document Titles

## Metadata

- Feature name: Descriptive Document Titles
- Feature slug: 6.1-descriptive-document-titles
- Owner: Gemini CLI
- Status: Draft
- Last updated: 2026-05-17
- Related knowledge artifact(s): PRD 7.15.4 (Citation Detail View)

## Problem Statement

Currently, the system renames uploaded files to UUIDs for storage and then uses these UUIDs as the document titles. This is confusing for users who expect to see the original filename or descriptive metadata (like PDF titles) in the document library and chat citations.

## Desired Outcomes

- Documents uploaded by users display descriptive titles (original filename or PDF metadata) instead of GUIDs.
- Citations in the chat interface use descriptive document titles for better groundedness perception.

## Minimum Release Slice

- Updated ingestion pipeline that captures and uses the original filename as a fallback title.
- Updated PDF extractor that prefers internal PDF metadata 'Title' over the filename.

## Success Criteria

- SC-001: Documents in the UI display human-readable titles (e.g., "Manual.pdf").
- SC-002: Citations in chat display human-readable titles.
- SC-003: PDF files with internal metadata 'Title' use that title instead of the filename.

## In Scope

- File ingestion (PDF, TXT, MD).
- Preserving `submitted_filename` through the extraction process.
- Fallback logic: PDF Metadata Title > Submitted Filename > UUID (last resort).
- Display of descriptive titles in Document Library and Chat Citations.

## Out Of Scope

- Changing URL title logic (already uses HTML `<title>` or URL).
- Renaming files in the storage layer (UUIDs are maintained for collision avoidance).
- Retroactive renaming of existing documents in the database.

## Non-Goals

- Implementing complex NLP-based title generation from document content.

## Users And Stakeholders

- Primary users: End users interacting with the chatbot and managing documents.
- Developers: Maintenance of the ingestion service.

## User Stories And Key Scenarios

- US-001: As a user, I want to see "Financial_Report_2025.pdf" in my document list so I can easily find it.
- US-002: As a user, I want chat citations to refer to "Financial_Report_2025" instead of "a1b2-c3d4..." so I can trust the source.

### Detailed Scenarios

- **Scenario 1 (Text File Upload):**
  - **Given:** A file named `meeting_notes.txt`.
  - **When:** The user uploads the file.
  - **Then:** The document title in the system is set to `meeting_notes`.
- **Scenario 2 (PDF with Metadata):**
  - **Given:** A PDF file named `doc1.pdf` with internal metadata title "Project Specification".
  - **When:** The user uploads the file.
  - **Then:** The document title in the system is set to `Project Specification`.
- **Scenario 3 (PDF without Metadata):**
  - **Given:** A PDF file named `resume.pdf` with no internal metadata title.
  - **When:** The user uploads the file.
  - **Then:** The document title in the system is set to `resume`.

## Current Context

- `LocalStorage.save_upload` renames files to UUIDs.
- `ExtractorDispatcher.extract` calls extractors with the UUID path.
- `PdfExtractor` and `TextExtractor` use `title_from_filename(path)`, which results in the UUID being used as the title.
- `IngestionService.process_ingestion_attempt` receives the extraction result and updates the ingestion attempt/document.

## Dependencies And External Touchpoints

- `backend/storage/local.py`
- `backend/extractors/dispatcher.py`
- `backend/extractors/pdf_extractor.py`
- `backend/extractors/text_extractor.py`
- `backend/ingestion/service.py`

## Functional Requirements

### REQ-001: Capture Submitted Filename

Requirement: The ingestion system must pass the original submitted filename to the extraction layer.

Why it matters: The extraction layer currently only knows about the storage path (UUID).

Impacted users or scenarios: All file uploads.

Related success criteria: SC-001, SC-002.

Priority: Must Have

Acceptance notes: `ExtractorDispatcher.extract` accepts an optional `fallback_title`.

Validation surface: Code review, Unit tests.

### REQ-002: Descriptive Title Selection

Requirement: The extraction layer must select titles in the following order: Internal Metadata (if PDF) > Fallback Title (Submitted Filename) > Storage Filename (UUID).

Why it matters: Ensures the most descriptive name is used while maintaining a reliable fallback.

Impacted users or scenarios: Scenario 2, Scenario 3.

Related success criteria: SC-003.

Priority: Must Have

Acceptance notes: `PdfExtractor` checks for metadata "Title" before using `fallback_title`.

Validation surface: Integration tests with sample PDF and text files.

## Non-Functional Requirements

- NFR-001 Performance: Title extraction must not add measurable latency to the ingestion process.

## Constraints

- Files must still be stored as UUIDs on disk to prevent collisions and handle special characters safely.

## Assumptions

- ASM-001: The `submitted_filename` in `IngestionAttempt` is reliable and populated for all file uploads.

## Risks

- RISK-001: Very long filenames might clutter the UI.
  Mitigation: UI should truncate long titles (already handled by most modern CSS layouts).

## Open Questions

- None at this time.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001, REQ-002
  Linked user story or scenario: US-001, Scenario 1
  Validation method: Upload `test.txt`. Verify title is `test`.
  Proof target: Backend API Response / DB Entry.
- [ ] AC-002 Linked requirement(s): REQ-002
  Linked user story or scenario: US-002, Scenario 2
  Validation method: Upload PDF with internal title "Hello World". Verify document title is "Hello World".
  Proof target: Backend API Response / DB Entry.
- [ ] AC-003 Linked requirement(s): REQ-001
  Linked user story or scenario: Scenario 3
  Validation method: Upload PDF without internal title named `my_file.pdf`. Verify document title is `my_file`.
  Proof target: Backend API Response / DB Entry.

# Task Breakdown

## Metadata

- Feature name: Knowledge Ingestion And Collections
- Related spec: `artifacts/features/1.knowledge-ingestion-and-collections/spec.md`
- Related plan: `artifacts/features/1.knowledge-ingestion-and-collections/plan.md`
- Related design: None
- Owner: Unassigned
- Last updated: 2026-05-04

## Rules

- Keep each task small and testable.
- Include validation tasks, not just implementation tasks.
- Record blockers and dependencies explicitly.
- Link every task back to requirement and acceptance criteria IDs.
- Link every task back to the plan task or phase it came from.
- Link each phase or task group back to the user scenario or outcome it enables when relevant.
- Mark tasks that can run in parallel when they have no dependency relationship.
- Only mark tasks as parallel-safe when they do not create obvious write conflicts or contract conflicts.
- If a task is marked `[P]`, state the ownership boundary and any reintegration expectation explicitly.
- Prefer explicit file or module targets when known from the plan.
- Use these task states consistently: `Not Started`, `In Progress`, `Blocked`, `Done`, `Deferred`.
- Make regression-sensitive or protected behavior explicit in validation or safeguard tasks when relevant.
- For behavior-changing tasks, prefer validation notes that name the failing proof or targeted test expected before the fix.
- Do not finalize task lists until REQ -> AC -> TASK -> validation coverage is complete.

## Status Tracking Requirements

Every task MUST have both a checkbox and a Status field for implementation tracking:

- **Checkbox format**: `- [ ] TASK-ID` or `- [X] TASK-ID` (`[ ]` = not done yet, `[X]` = done)
- **Status field**: `Status: [Not Started|In Progress|Done|Blocked|Deferred]` (initialized to `Not Started`)
- **Session note**: Field for implementation agent to track blockers, progress, or issues
- **Implementation contract**: Implementation agent will keep checkbox and Status field aligned as work progresses

---

## Phase 1: Metadata And Collections Foundation

**Goal:** Establish the backend data model, persistence contracts, and collection lifecycle foundation that later ingestion and chunk work will depend on.

**Enabled scenarios:** US-004, US-005, SC-003, SC-004

**Completion criteria:**

- [ ] CC-001: Collection and document metadata can be created, updated, queried, and deleted consistently through backend interfaces.
- [ ] CC-002: A document can be assigned to and moved between collections without breaking metadata integrity.

### Tasks

- [X] TASK-001: Set up Python backend structure and local persistence initialization
  Status: Done
  Summary: Create `backend/` package structure with Flask app factory, SQLite schema initialization, ChromaDB client setup, and idempotent local data directory creation. Establish the module layout for services, persistence adapters, API routes, and tests.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-002, REQ-005
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s) or module(s): `backend/app.py`, `backend/config.py`, `backend/persistence/` (new), `backend/models/` (new)
  Depends on: PREREQ-001 (Python virtualenv active)
  Can run in parallel: No—foundational infrastructure
  Validation note: Verify Flask app initializes, SQLite schema creates tables without errors, ChromaDB client connects, and local directories exist and are writable.
  Session note: 2026-05-04: Virtualenv created, backend bootstrap scaffold added, and `.venv/bin/python -m unittest tests.test_app_bootstrap` passed.

- [X] TASK-002: Implement SQLite schema for documents, ingestion attempts, and metadata
  Status: Done
  Summary: Define and migrate SQLite schema with tables for `documents`, `ingestion_attempts`, `duplicate_logs`, and `chunk_metadata`. Include columns for document_id, source_type, ingestion_status, collection_id, created_at, last_indexed_at, deletion_state, and source-identity fields required by REQ-002.
  Plan reference: Phase 1 / TASK-001
  Linked requirement(s): REQ-002, REQ-005
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s) or module(s): `backend/persistence/schema.py`, `backend/migrations/` (new)
  Depends on: TASK-001
  Can run in parallel: No—foundational schema
  Validation note: Verify schema creates cleanly, all required columns exist with correct types, and idempotent re-runs do not error.
  Session note: 2026-05-04: Expanded SQLite schema with required tables, lifecycle columns, and indexes. Covered by bootstrap and phase-1 integration tests.

- [X] TASK-003: Implement Collection model and CRUD operations in backend service
  Status: Done
  Summary: Create `Collection` model class, implement SQLite-backed persistence for collection create, read, update, delete, and list operations. Include fields for collection_id, name, description, created_at, default_collection flag, and document-count metadata.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `backend/models/collection.py` (new), `backend/services/collection_service.py` (new)
  Depends on: TASK-002
  Can run in parallel: No—depends on schema
  Validation note: Write unit tests for create, read, update, delete, list; verify stable collection_id assignment; test that default-collection state is preserved.
  Session note: 2026-05-04: Added collection model and SQLite-backed collection service with create, list, detail, update, delete, and default-selection flows. Validated by integration tests.

- [X] TASK-004: Implement Document model and document-to-collection assignment operations
  Status: Done
  Summary: Create `Document` model class, implement SQLite-backed persistence for document create, read, update, and list operations. Include fields for document_id, source_type, source_url, collection_id, ingestion_status, duplicate_status, deletion_state, and metadata preservation fields (title, created_at, last_indexed_at). Implement assignment and move operations for binding documents to collections.
  Plan reference: Phase 1 / TASK-001, TASK-002
  Linked requirement(s): REQ-002, REQ-005
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s) or module(s): `backend/models/document.py` (new), `backend/services/document_service.py` (new)
  Depends on: TASK-002, TASK-003
  Can run in parallel: No—depends on collection schema
  Validation note: Write unit tests for document CRUD, collection assignment, and move operations; verify document_id remains stable across updates; verify collection membership is consistent when moved.
  Session note: 2026-05-04: Added document model and document service with stable document records, metadata persistence, and collection move operations. Validated by integration tests.

- [X] TASK-005: Implement collection REST API endpoints (CRUD, default, list)
  Status: Done
  Summary: Build Flask REST endpoints for GET /api/collections (list), POST /api/collections (create), GET /api/collections/{id}, PUT /api/collections/{id} (update), DELETE /api/collections/{id}, PATCH /api/collections/{id}/default (set default). Return JSON payloads with collection metadata and document-count statistics.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s) or module(s): `backend/routes/collections.py` (new)
  Depends on: TASK-003
  Can run in parallel: No—depends on service layer
  Validation note: Test all endpoints with valid and invalid payloads; verify collection_id and metadata are returned correctly; verify default-collection updates do not corrupt other collections.
  Session note: 2026-05-04: Added collection REST endpoints for list, create, detail, update, delete, and set-default behaviors. Validated by integration tests.

- [X] TASK-006: Implement document REST API endpoints (create, list, get, move-to-collection)
  Status: Done
  Summary: Build Flask REST endpoints for GET /api/documents (list with optional collection filter and search), GET /api/documents/{id}, POST /api/documents (create minimal document record), PATCH /api/documents/{id}/collection (move to collection). Return JSON payloads with document metadata, chunk count placeholder, and status fields.
  Plan reference: Phase 1 / TASK-002
  Linked requirement(s): REQ-002, REQ-005, REQ-006
  Linked acceptance criteria: AC-002, AC-005, AC-006
  Affected file(s) or module(s): `backend/routes/documents.py` (new)
  Depends on: TASK-004
  Can run in parallel: No—depends on service layer
  Validation note: Test all endpoints; verify documents are listed with correct collection membership; verify move-to-collection updates both document and metadata consistently.
  Session note: 2026-05-04: Added document REST endpoints for create, list, detail, move-to-collection, re-index, and delete wiring. Phase-1 collection and document movement validated by integration tests.

- [X] TASK-007: Write Phase 1 integration tests (collections and document assignment)
  Status: Done
  Summary: Write SQLite + REST integration tests covering collection CRUD, default-collection state, document creation, document-to-collection assignment, and document move operations. Test scenarios: create collection, create document, assign to collection, move to another collection, verify metadata consistency.
  Plan reference: Phase 1
  Linked requirement(s): REQ-002, REQ-005
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s) or module(s): `backend/tests/integration/test_collections_and_documents.py` (new)
  Depends on: TASK-005, TASK-006
  Can run in parallel: No—integration validation task
  Validation note: Run all tests; verify no regressions in collection or document state; verify CC-001 and CC-002 completion criteria are met.
  Session note: 2026-05-04: Added backend/tests/integration/test_collections_and_documents.py and passed `.venv/bin/python -m unittest tests.test_app_bootstrap tests.integration.test_collections_and_documents`.

---

## Phase 2: Ingestion, Duplicate Detection, And Chunking

**Goal:** Implement the complete ingestion pipeline for all supported source types, duplicate detection and handling, baseline chunking, and embedding-ready index preparation.

**Enabled scenarios:** US-001, US-002, US-003, US-005, SC-001, SC-002, SC-004

**Completion criteria:**

- [ ] CC-003: Each supported source type (PDF, TXT, Markdown, URL) can be ingested into a stable document record with explicit terminal state.
- [ ] CC-004: Duplicate and near-duplicate attempts trigger visible classification and decision flows.
- [ ] CC-005: Accepted documents produce chunk and index records with required metadata and collection linkage.

### Tasks

- [X] TASK-008: Implement source parsing and text extraction for PDF, TXT, Markdown, and URL
  Status: Done
  Summary: Create parser modules for each source type using PyPDF2 or pdfplumber (PDF), built-in file I/O (TXT, Markdown), and BeautifulSoup + requests (URL). Return extracted text, metadata (title, page count for PDF, URL source), and error messages. Handle parsing failures gracefully and log extraction errors.
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/parsers/` (new), `backend/parsers/pdf_parser.py`, `backend/parsers/text_parser.py`, `backend/parsers/markdown_parser.py`, `backend/parsers/url_parser.py`
  Depends on: TASK-001
  Can run in parallel: Yes [P]—Each parser module is independent; ownership boundary: one parser per module.
  Validation note: Unit tests for each parser with valid and malformed inputs; verify extracted text is non-empty for valid inputs; verify error messages are actionable.
  Session note: 2026-05-04: Added parser modules for PDF, text, Markdown, and URL sources. Exercised through ingestion pipeline integration tests.

- [X] TASK-009: Implement duplicate-detection pipeline (exact hash, URL canonical, content hash)
  Status: Done
  Summary: Create duplicate-detection service that runs pre-ingestion checks using file hash (for uploaded files), normalized URL canonicalization (for URLs), and normalized-text content hash against existing document records. Classify results as `unique`, `exact_duplicate`, `same_url`, or `same_content_different_source`. Log detection method, matched document_id, and similarity score if applicable.
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/services/duplicate_detection_service.py` (new)
  Depends on: TASK-004 (needs document records to compare against)
  Can run in parallel: No—depends on document model
  Validation note: Unit tests for each detection method (file hash, URL canonicalization, content hash); verify `exact_duplicate` and `same_url` are caught; test with synthetic near-duplicates to verify `same_content_different_source` detection; verify logging captures all required fields.
  Session note: 2026-05-04: Added duplicate detection with file hash, canonical URL, normalized text hash, plus near-duplicate/title checks. Verified through upload and URL-duplicate integration tests.

- [X] TASK-010: Implement ingestion request handler and status state machine
  Status: Done
  Summary: Create `IngestionService` with request handler that orchestrates parsing, duplicate detection, document record creation, and ingestion-attempt logging. Manage ingestion status state machine: `pending` → (`completed`, `failed`, `duplicate_detected`, `skipped`). Persist ingestion_attempt records with status, errors, duplicate_class, user_decision, and timestamp fields.
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/services/ingestion_service.py` (new), `backend/models/ingestion_attempt.py` (new)
  Depends on: TASK-008, TASK-009
  Can run in parallel: No—orchestration layer
  Validation note: Test successful ingestion through all source types; test failure modes (parse error, network error, duplicate detected); verify terminal states are reached correctly; verify ingestion_attempt records are created with all required fields.
  Session note: 2026-05-04: Added ingestion orchestration, attempt records, duplicate_detected flow, completed flow, skipped flow, and replace/version-as-new handling in backend/services/ingestion_service.py.

- [X] TASK-011: Implement multipart file upload endpoint (POST /api/documents/upload)
  Status: Done
  Summary: Build Flask multipart file-upload endpoint that accepts PDF, TXT, or Markdown files, calls the ingestion service, returns ingestion status, and handles errors. Include collection_id parameter to assign document to collection during ingestion. Return document_id, status, errors, and duplicate_class in JSON response.
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/routes/ingestion.py` (new)
  Depends on: TASK-010
  Can run in parallel: No—depends on ingestion service
  Validation note: Test upload of each file type; verify status response is correct; verify document_id is stable across subsequent calls; test error handling for invalid file types.
  Session note: 2026-05-04: Added multipart upload endpoint and validated successful upload through integration test.

- [X] TASK-012: Implement URL ingestion endpoint (POST /api/documents/ingest-url)
  Status: Done
  Summary: Build Flask endpoint that accepts URL, optional collection_id, calls the ingestion service with URL parser, returns ingestion status. Handle network errors, timeouts, and 4xx/5xx responses with actionable error messages. Return document_id, status, errors, and duplicate_class in JSON response.
  Plan reference: Phase 2 / TASK-003
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/routes/ingestion.py` (shared with TASK-011)
  Depends on: TASK-010
  Can run in parallel: Yes [P]—URL endpoint is independent from file upload; ownership boundary: `backend/routes/ingestion.py` file (coordinate endpoint registration). Reintegration: both endpoints should be registered in the same Flask blueprint.
  Validation note: Test ingest of valid URL; verify network error handling; test redirect handling; verify document_id and status in response.
  Session note: 2026-05-04: Added URL ingestion endpoint and validated duplicate handling with mocked remote HTML response.

- [X] TASK-013: Implement duplicate-decision endpoint (PATCH /api/documents/{id}/duplicate-decision)
  Status: Done
  Summary: Build Flask endpoint that accepts a document_id, user decision (skip, replace, version-as-new, ingest-anyway), and optional metadata-merge options. Update ingestion_attempt record with user decision, finalize or reject the document record, and return updated status.
  Plan reference: Phase 2 / TASK-004
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/routes/ingestion.py` (shared)
  Depends on: TASK-010
  Can run in parallel: Yes [P]—Duplicate-decision endpoint is independent; ownership boundary: `backend/routes/ingestion.py`. Reintegration: must coordinate with main ingestion flow to ensure decisions are applied before final acceptance.
  Validation note: Test all decision types; verify skip prevents document finalization; verify replace updates matched document; verify version-as-new creates new document with link to duplicate.
  Session note: 2026-05-04: Added duplicate-decision endpoint supporting skip, replace, version-as-new, and ingest-anyway backend paths.

- [X] TASK-014: Implement baseline chunking service (fixed-size, Markdown heading-aware, PDF page-aware)
  Status: Done
  Summary: Create chunking service with configurable chunk_size and chunk_overlap parameters. Implement fixed-size chunking, heading-aware chunking for Markdown (preserve # structure), and page-aware chunking for PDF (split on page boundaries). Return list of chunk objects with chunk_id, content, metadata (chunk_order, page or section, source_url when applicable), and parent document_id.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/services/chunking_service.py` (new), `backend/models/chunk.py` (new)
  Depends on: TASK-008 (parsers provide source-specific metadata)
  Can run in parallel: No—depends on parser output structure
  Validation note: Unit tests for each chunking strategy; verify chunk_size and overlap are respected; verify Markdown headings are preserved; verify PDF page boundaries are respected; verify all chunks are assigned sequential chunk_order and parent document_id.
  Session note: 2026-05-04: Added chunking service with fixed-size, Markdown heading-aware, and PDF page-aware behavior.

- [X] TASK-015: Implement embedding and ChromaDB index creation (POST /api/documents/{id}/index)
  Status: Done
  Summary: Create indexing service that takes a document record and its chunks, generates embeddings using a configurable embedding model (default: OpenAI or similar local/free provider in first version), stores vectors in ChromaDB collection with collection-aware namespace, and creates index records linking chunks to embeddings. Preserve chunk metadata (chunk_id, chunk_order, page, source_url, document_id, collection_id) in ChromaDB metadata fields.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-004, REQ-005
  Linked acceptance criteria: AC-004, AC-005
  Affected file(s) or module(s): `backend/services/indexing_service.py` (new), `backend/models/index_record.py` (new)
  Depends on: TASK-014, TASK-003 (collection context)
  Can run in parallel: No—depends on chunking
  Validation note: Unit tests for embedding generation; verify ChromaDB stores vectors with correct metadata; verify re-index operation updates vectors correctly; verify collection namespace isolation.
  Session note: 2026-05-04: Added local hash-based embedding/indexing service with ChromaDB metadata preservation and document reindex support.

- [X] TASK-016: Implement re-index endpoint and cleanup operations (PATCH /api/documents/{id}/re-index, DELETE /api/documents/{id})
  Status: Done
  Summary: Build endpoints for re-chunking and re-indexing a document (when chunking settings change) and for deleting a document (removes document record, chunks, and ChromaDB vectors). Delete endpoint should remove related ingestion_attempt and chunk_metadata records. Re-index should atomically update both SQLite and ChromaDB state.
  Plan reference: Phase 2 / TASK-005
  Linked requirement(s): REQ-004, REQ-005
  Linked acceptance criteria: AC-004, AC-005
  Affected file(s) or module(s): `backend/routes/documents.py` (shared), shared deletion and re-index logic
  Depends on: TASK-015
  Can run in parallel: No—depends on indexing service
  Validation note: Test re-index on a document with existing chunks; verify old vectors are replaced; test delete operation; verify document and related records are removed from both SQLite and ChromaDB; verify no orphaned records remain.
  Session note: 2026-05-04: Added re-index and delete endpoints plus metadata/vector cleanup paths. Verified delete and re-index through ingestion integration test.

- [X] TASK-017: Write Phase 2 integration tests (ingestion, duplication, chunking, indexing)
  Status: Done
  Summary: Write comprehensive integration tests covering all source types, duplicate detection paths, document decision flows, chunking, embedding, and re-index operations. Test scenarios: ingest PDF, ingest URL with duplicate detection, skip duplicate, replace duplicate, ingest-anyway, version-as-new, verify chunk counts and embeddings, re-index with new chunking settings, delete document and verify ChromaDB cleanup.
  Plan reference: Phase 2
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004, AC-005
  Affected file(s) or module(s): `backend/tests/integration/test_ingestion_pipeline.py` (new)
  Depends on: TASK-011, TASK-012, TASK-013, TASK-016
  Can run in parallel: No—integration validation task
  Validation note: Run all tests; verify CC-003, CC-004, CC-005 completion criteria are met; ensure all REQ-001 through REQ-005 acceptance notes are covered by tests.
  Session note: 2026-05-04: Added backend/tests/integration/test_ingestion_pipeline.py and passed `.venv/bin/python -m unittest tests.integration.test_ingestion_pipeline`.

---

## Phase 3: Document Library And Collections UI

**Goal:** Deliver the two required frontend screens (Document Library and Collections) with full AJAX integration for all backend operations and status visibility.

**Enabled scenarios:** US-001, US-003, US-004, US-005, SC-001, SC-002, SC-003, SC-004

**Completion criteria:**

- [ ] CC-006: Reviewers can manage documents and collections through the required screens without direct database access.
- [ ] CC-007: The frontend shows required document-row and collection fields, plus long-running status visibility.

### Tasks

- [X] TASK-018: Build Document Library HTML and base styling
  Status: Done
  Summary: Create `frontend/document-library.html` with static HTML structure for document list table (columns: title, ID, source type, collection, status, duplicate flag, chunk count, created, last indexed, actions), upload form, URL ingestion form, and action buttons (delete, re-index). Add baseline CSS for readability and form layout. Include modal/overlay containers for duplicate-warning prompts and error messages.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-006
  Affected file(s) or module(s): `frontend/document-library.html` (new), `frontend/styles.css` (new or extended)
  Depends on: TASK-006 (API must be ready for testing)
  Can run in parallel: No—foundational UI structure
  Validation note: Verify HTML structure is semantic and accessible; verify all required columns are present; verify forms have proper labels and input types.
  Session note: 2026-05-04: Completed the Document Library shell in `frontend/document-library.html` and `frontend/styles.css`, including required columns, forms, duplicate modal, error modal, and accessible table captions. Verified the screen is served through Flask at `/document-library.html`.

- [X] TASK-019: Implement Document Library file upload and form handling (JavaScript)
  Status: Done
  Summary: Write JavaScript in `frontend/document-library.js` to handle file selection, multipart form construction, and POST to /api/documents/upload with collection_id parameter. Show upload progress and status message. Handle success (show new document row) and error (show error overlay with actionable message).
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-001, REQ-002, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-006
  Affected file(s) or module(s): `frontend/document-library.js` (new)
  Depends on: TASK-011, TASK-018
  Can run in parallel: No—depends on upload endpoint and HTML structure
  Validation note: Test file selection; verify POST request is sent correctly; verify response status is displayed; verify error messages are user-friendly.
  Session note: 2026-05-04: Implemented multipart upload handling in `frontend/document-library.js` with status banners, collection selection, success refresh, and error modal handling against `/api/documents/upload`.

- [X] TASK-020: Implement Document Library URL ingestion form (JavaScript)
  Status: Done
  Summary: Write JavaScript to handle URL input, validate format, and POST to /api/documents/ingest-url with collection_id. Show status message and error handling similar to file upload. Add input validation for URL format.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-001, REQ-002, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-006
  Affected file(s) or module(s): `frontend/document-library.js` (shared)
  Depends on: TASK-012, TASK-018
  Can run in parallel: Yes [P]—URL ingestion form is independent from file upload form; ownership boundary: both forms in same JavaScript file, ensure independent event handlers.
  Validation note: Test URL input validation; verify POST request is sent with correct parameters; verify error messages are clear.
  Session note: 2026-05-04: Added URL ingestion handling with client-side URL validation, POST to `/api/documents/ingest-url`, shared status/error display, and post-ingestion list refresh.

- [X] TASK-021: Implement duplicate-warning modal and decision handling (JavaScript)
  Status: Done
  Summary: Write JavaScript to detect duplicate_class in ingestion response, show modal overlay with duplicate details (matched document, similarity score, duplicate classification), and provide decision buttons (skip, replace, version-as-new, ingest-anyway). On decision, POST to /api/documents/{id}/duplicate-decision and update document list.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-003, REQ-006
  Linked acceptance criteria: AC-003, AC-006
  Affected file(s) or module(s): `frontend/document-library.js` (shared)
  Depends on: TASK-013, TASK-018
  Can run in parallel: Yes [P]—Duplicate-decision handler is independent; ownership boundary: `frontend/document-library.js` (coordinate modal event handlers).
  Validation note: Verify modal appears when duplicate is detected; verify all decision options are clickable; verify correct decision is sent to backend; verify document list refreshes after decision.
  Session note: 2026-05-04: Wired duplicate response handling to open a modal with matched document, classification, score, and detection method, plus decision submission for skip, replace, version-as-new, and ingest-anyway.

- [X] TASK-022: Implement document list fetch and rendering (JavaScript)
  Status: Done
  Summary: Write JavaScript to fetch document list from GET /api/documents?collection_id=... (optional filter), render table rows with all required columns (title, ID, source type, collection, status, duplicate status, chunk count, created, last indexed). Include search/filter inputs for title and collection. Reload list after ingestion, deletion, or re-index.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-006
  Affected file(s) or module(s): `frontend/document-library.js` (shared)
  Depends on: TASK-006
  Can run in parallel: No—depends on API endpoint
  Validation note: Test list fetch and render with 0, 1, and 5+ documents; verify all columns are displayed; verify collection filter works; verify search by title works; verify status field shows ingestion state correctly.
  Session note: 2026-05-04: Implemented document list fetch, search, collection filter, empty-state row, and rendering of all required document fields from `/api/documents`.

- [X] TASK-023: Implement document actions (delete, re-index) in Document Library (JavaScript)
  Status: Done
  Summary: Write JavaScript for delete and re-index buttons in document-library table. Delete: confirm dialog, then DELETE /api/documents/{id}, then refresh list. Re-index: POST /api/documents/{id}/re-index, show status update, refresh list.
  Plan reference: Phase 3 / TASK-006
  Linked requirement(s): REQ-004, REQ-006
  Linked acceptance criteria: AC-004, AC-006
  Affected file(s) or module(s): `frontend/document-library.js` (shared)
  Depends on: TASK-016
  Can run in parallel: Yes [P]—Action handlers are independent; ownership boundary: `frontend/document-library.js`.
  Validation note: Test delete flow (confirm dialog, API call, list refresh); test re-index flow (status message, list refresh); verify deleted documents no longer appear in list.
  Session note: 2026-05-04: Added delete confirmation and re-index actions with backend calls, status updates, and list refresh on completion.

- [X] TASK-024: Build Collections management HTML and base styling
  Status: Done
  Summary: Create `frontend/collections.html` with static HTML structure for collections list (columns: name, ID, document count, chunk count, last updated, actions), collection creation form, default-collection selector, and action buttons (edit, delete). Include table for documents in selected collection with move-to-collection options. Add CSS styling for collections view.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s) or module(s): `frontend/collections.html` (new)
  Depends on: TASK-005 (API must be ready)
  Can run in parallel: No—foundational UI structure
  Validation note: Verify HTML structure is complete; verify all required columns present; verify forms are properly labeled.
  Session note: 2026-05-04: Completed the Collections screen shell in `frontend/collections.html` with create form, collection table, selected collection statistics panel, move-document table, and accessible captions.

- [X] TASK-025: Implement Collections list fetch and rendering (JavaScript)
  Status: Done
  Summary: Write JavaScript to fetch collection list from GET /api/collections, render table rows with all required columns (name, ID, document count, chunk count, last updated). Include default-collection indicator and update list after create, update, or delete operations.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s) or module(s): `frontend/collections.js` (new)
  Depends on: TASK-005
  Can run in parallel: No—depends on API
  Validation note: Test list fetch and render; verify all columns display correctly; verify default-collection indicator is shown; verify counts are accurate.
  Session note: 2026-05-04: Implemented collection list loading and rendering with default badge, empty-state handling, and required count/timestamp fields from `/api/collections`.

- [X] TASK-026: Implement collection CRUD operations in Collections screen (JavaScript)
  Status: Done
  Summary: Write JavaScript for create collection form (name, description), PUT /api/collections/{id} for updates, DELETE /api/collections/{id} for deletion with confirm dialog, PATCH /api/collections/{id}/default for setting default collection. Refresh list and show status messages.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s) or module(s): `frontend/collections.js` (shared)
  Depends on: TASK-005
  Can run in parallel: Yes [P]—CRUD operations are independent; ownership boundary: `frontend/collections.js`.
  Validation note: Test create, update, delete, and set-default operations; verify list updates after each operation; verify error messages are clear.
  Session note: 2026-05-04: Added create, edit, delete, and set-default collection actions with status banners and refresh behavior in `frontend/collections.js`.

- [X] TASK-027: Implement document-move-to-collection in Collections screen (JavaScript)
  Status: Done
  Summary: Write JavaScript to fetch documents in selected collection, show them in a sub-table, and provide dropdown/button to move document to another collection. POST to /api/documents/{id}/collection endpoint with new collection_id, refresh document list in current collection.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s) or module(s): `frontend/collections.js` (shared)
  Depends on: TASK-006 (move endpoint)
  Can run in parallel: Yes [P]—Document-move is independent; ownership boundary: `frontend/collections.js`.
  Validation note: Test document-move operation; verify document appears in new collection's list; verify old collection's list is updated; verify document record is not duplicated.
  Session note: 2026-05-04: Added selected-collection document loading plus move-to-collection controls backed by `PATCH /api/documents/{id}/collection`.

- [X] TASK-028: Implement collection statistics display (JavaScript)
  Status: Done
  Summary: Write JavaScript to display collection-level statistics in Collections screen: document count, chunk count, last-updated timestamp. Update statistics after document add, delete, or move operations.
  Plan reference: Phase 3 / TASK-007
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s) or module(s): `frontend/collections.js` (shared)
  Depends on: TASK-005
  Can run in parallel: Yes [P]—Statistics display is independent; ownership boundary: `frontend/collections.js`.
  Validation note: Verify statistics are displayed correctly; verify they update after operations; verify counts match backend state.
  Session note: 2026-05-04: Collection statistics panel now renders collection ID, document count, chunk count, last updated timestamp, and description metadata, and refreshes after collection and document mutations.

- [X] TASK-029: Write Phase 3 frontend integration test plan (manual browser verification)
  Status: Done
  Summary: Document manual test scenarios for Document Library and Collections screens: upload PDF, ingest URL, handle duplicate warning, create collection, assign document to collection, move document, delete document, delete collection, verify all fields and status messages are visible. Prepare checklist for visual verification.
  Plan reference: Phase 3
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
  Affected file(s) or module(s): `artifacts/features/1.knowledge-ingestion-and-collections/manual-test-checklist.md` (new)
  Depends on: TASK-023 (all UI features ready for testing)
  Can run in parallel: No—planning task
  Validation note: Create checklist covering all user stories and success criteria; verify each test scenario can be executed in the browser.
  Session note: 2026-05-04: Added `artifacts/features/1.knowledge-ingestion-and-collections/manual-test-checklist.md` covering Document Library, Collections, and observability verification flows.

---

## Phase 4: Hardening, Validation, And Observability

**Goal:** Harden validation coverage, add regression-protection tests, ensure observability of ingestion and duplicate decisions, and verify complete acceptance criteria coverage.

**Enabled scenarios:** SC-001, SC-002, SC-003, SC-004

**Completion criteria:**

- [ ] CC-008: Automated checks cover the backend behaviors that produce user-visible lifecycle state.
- [ ] CC-009: Manual verification confirms the UI meets the acceptance criteria and exposes actionable failures.

### Tasks

- [X] TASK-030: Add unit tests for source parsers (PDF, TXT, Markdown, URL)
  Status: Done
  Summary: Write comprehensive unit tests for each parser module covering valid inputs, malformed inputs, edge cases (empty file, very large file, special characters), and error messages. Verify extracted text is correct and metadata is preserved. Use fixtures with sample files.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Affected file(s) or module(s): `backend/tests/unit/test_parsers.py` (new)
  Depends on: TASK-008
  Can run in parallel: Yes [P]—Unit tests for parsers are independent; ownership boundary: one test function per parser.
  Validation note: Run pytest; verify all parser tests pass; verify coverage > 85% for parser modules.
  Session note: 2026-05-04: Added parser unit coverage in `backend/tests/unit/test_parsers.py` with sample fixtures for TXT, Markdown, and PDF plus URL parsing mocks. Verified with `.venv/bin/python -m unittest discover backend/tests`.

- [X] TASK-031: Add unit tests for duplicate-detection helpers
  Status: Done
  Summary: Write unit tests for file-hash, URL-canonicalization, and content-hash functions covering exact duplicates, near-duplicates, URL variations (http/https, trailing slash, query params), and content with minor variations. Verify classification output is correct.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/tests/unit/test_duplicate_detection.py` (new)
  Depends on: TASK-009
  Can run in parallel: Yes [P]—Unit tests are independent.
  Validation note: Run pytest; verify all tests pass; verify edge cases (very long text, Unicode, whitespace variations) are handled correctly.
  Session note: 2026-05-04: Added duplicate-detection unit coverage for file hash, canonical URL, normalized text hash, near-duplicate similarity, and title-match fallback in `backend/tests/unit/test_duplicate_detection.py`.

- [X] TASK-032: Add unit tests for chunking service
  Status: Done
  Summary: Write unit tests for fixed-size chunking, Markdown heading-aware chunking, and PDF page-aware chunking, covering various inputs: small documents, large documents, documents with headings, PDF with multiple pages. Verify chunk boundaries, overlap, and metadata are correct.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/tests/unit/test_chunking.py` (new)
  Depends on: TASK-014
  Can run in parallel: Yes [P]—Unit tests are independent.
  Validation note: Run pytest; verify all chunk tests pass; verify chunk_size and overlap are respected; verify Markdown structure is preserved.
  Session note: 2026-05-04: Added chunking unit coverage for fixed-size overlap behavior, Markdown heading-aware chunking, PDF page-aware chunking, and empty-text handling in `backend/tests/unit/test_chunking.py`.

- [X] TASK-033: Add unit tests for embedding and indexing helpers
  Status: Done
  Summary: Write unit tests for embedding generation, ChromaDB vector storage, and metadata preservation. Test with synthetic vectors and mock embedding service. Verify vectors are stored with correct metadata and can be retrieved.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/tests/unit/test_indexing.py` (new)
  Depends on: TASK-015
  Can run in parallel: Yes [P]—Unit tests are independent.
  Validation note: Run pytest; verify all tests pass; verify ChromaDB operations are correct.
  Session note: 2026-05-04: Added indexing unit coverage in `backend/tests/unit/test_indexing.py` for vector metadata preservation, collection namespace moves, and vector deletion.

- [X] TASK-034: Add regression-protection tests for collection move and delete consistency
  Status: Done
  Summary: Write integration tests to ensure collection moves and deletes do not leave orphaned or inconsistent metadata across SQLite and ChromaDB. Test scenarios: move document between collections, verify document appears in new collection's vector namespace; delete collection with documents, verify documents are either reassigned or properly cleaned up; delete document, verify it is removed from both SQLite and ChromaDB index.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-005, NFR-002
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `backend/tests/integration/test_consistency.py` (new)
  Depends on: TASK-016
  Can run in parallel: No—regression-protection test
  Validation note: Run all tests; verify no inconsistencies exist after operations; verify data integrity is maintained.
  Session note: 2026-05-04: Added `backend/tests/integration/test_consistency.py` covering cross-collection moves, protected deletion of non-empty collections, SQLite cleanup, and Chroma cleanup.

- [X] TASK-035: Add regression-protection tests for stable document_id assignment
  Status: Done
  Summary: Write tests to ensure document_id remains stable across re-ingestion attempts, re-index operations, and metadata updates. Test scenarios: upload file, get document_id; upload same file again, verify duplicate is detected and same document_id is offered; accept document, verify same document_id is assigned; re-index document, verify document_id is unchanged.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-002, NFR-002
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/tests/integration/test_document_id_stability.py` (new)
  Depends on: TASK-010, TASK-015
  Can run in parallel: No—regression-protection test
  Validation note: Run tests; verify document_id never changes for the same document.
  Session note: 2026-05-04: Added `backend/tests/integration/test_document_id_stability.py` verifying stable matched document identity across duplicate handling, collection moves, and re-index operations.

- [X] TASK-036: Add observability: ingestion and duplicate decision logging
  Status: Done
  Summary: Ensure all ingestion requests, duplicate detections, and user decisions are logged with timestamp, document_id, source_type, duplicate_class, decision, and result. Make logs queryable through API or UI (optional: simple GET /api/ingestion-logs endpoint). Preserve logs in SQLite for inspection.
  Plan reference: Phase 4 / TASK-008
  Linked requirement(s): REQ-003, NFR-004
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/models/ingestion_attempt.py` (extend), `backend/routes/ingestion.py` (extend with log endpoint)
  Depends on: TASK-010, TASK-013
  Can run in parallel: Yes [P]—Logging is independent from core functionality; ownership boundary: logging and log-query endpoint.
  Validation note: Verify logs are created for all ingestion attempts; verify duplicate decisions are logged; verify logs can be queried and are human-readable.
  Session note: 2026-05-04: Confirmed the log endpoint and ingestion attempt logging with `backend/tests/integration/test_observability_logs.py`, covering duplicate detection fields and persisted user decisions.

- [ ] TASK-037: Perform manual end-to-end Document Library workflow verification
  Status: Blocked
  Summary: Follow Document Library manual test checklist: upload PDF, upload TXT, ingest URL, handle duplicate warning (skip, replace, version-as-new), verify document rows display all required fields (title, ID, source type, collection, status, duplicate flag, chunk count, created, last indexed), verify delete works, verify re-index works. Screenshot or record observed state for each step.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004, AC-006
  Affected file(s) or module(s): `frontend/`, `backend/`
  Depends on: TASK-029 (test checklist ready)
  Can run in parallel: No—manual verification task
  Validation note: Execute all Document Library test scenarios; verify all fields are visible; verify actions work as expected; record any issues for follow-up; mark CC-009 if all steps pass.
  Session note: 2026-05-04: Blocked in this environment because no browser automation or GUI access is available for truthful end-to-end manual execution and screenshot capture. `manual-test-checklist.md` is ready for a human run.

- [ ] TASK-038: Perform manual end-to-end Collections management workflow verification
  Status: Blocked
  Summary: Follow Collections manual test checklist: create collection, list collections (verify name, ID, document count, chunk count, last updated), set default collection, edit collection name, move document to another collection, verify document appears in new collection, delete collection, verify it no longer appears in list. Screenshot or record observed state for each step.
  Plan reference: Phase 4 / TASK-009
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Affected file(s) or module(s): `frontend/`, `backend/`
  Depends on: TASK-029 (test checklist ready)
  Can run in parallel: No—manual verification task
  Validation note: Execute all Collections test scenarios; verify all fields and actions work correctly; record any issues for follow-up; mark CC-009 if all steps pass.
  Session note: 2026-05-04: Blocked in this environment because no browser automation or GUI access is available for truthful end-to-end manual execution and screenshot capture. `manual-test-checklist.md` is ready for a human run.

- [ ] TASK-039: Run final traceability audit and closure
  Status: Blocked
  Summary: Verify complete coverage: REQ-001 through REQ-006, AC-001 through AC-006 are all mapped to tasks and validated. Ensure no major acceptance criteria are orphaned. Verify all 4 phases have completion criteria checks. Document any deferred work or follow-ups. Finalize feature readiness.
  Plan reference: Phase 4
  Linked requirement(s): REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
  Affected file(s) or module(s): `artifacts/features/1.knowledge-ingestion-and-collections/tasks.md` (final review)
  Depends on: TASK-037, TASK-038 (manual verification complete)
  Can run in parallel: No—closure task
  Validation note: Verify all REQ/AC mappings are complete; verify all CC are checked; verify no test gaps exist.
  Session note: 2026-05-04: Blocked pending TASK-037 and TASK-038. Automated implementation and verification are complete, but final closure still requires human browser validation against the manual checklist.

---

## Notes Per Task

### TASK-001
Backend foundational setup: Flask app factory, virtualenv activation, SQLite initialization, ChromaDB client setup, local data directories (data/uploads, data/db, data/vectors or similar). Verify Flask dev server starts without errors.

### TASK-002
SQLite schema must be idempotent (use `IF NOT EXISTS` clauses). Include indexes on document_id, collection_id, source_type, and status fields for efficient queries. Consider foreign-key constraints between documents and collections.

### TASK-003
Collection model should include created_at, updated_at timestamps. Consider whether collections have metadata fields beyond name and description (e.g., description, tags, routing_description per REQ-005 acceptance notes). Ensure default_collection state is properly initialized.

### TASK-004
Document model must preserve all metadata fields from REQ-002: source_type, source_url, ingestion_status, duplicate_status, deletion_state, created_at, last_indexed_at, source_identity (hash or URL for lookup). Ensure document_id is UUID or stable identifier, not auto-increment.

### TASK-005
Collection REST API should return document-count statistics in list and detail responses. Consider pagination for large collections. Verify response JSON includes all fields required by AC-005 (collection name, ID, document count, chunk count, last updated, default flag).

### TASK-006
Document REST API list endpoint should support optional filters: ?collection_id=X, ?status=completed, ?search=title-substring. Verify document detail responses include chunk_count and duplicate_status fields. Consider whether chunk_count is calculated at query time or cached.

### TASK-007
Integration tests should use SQLite in-memory database (`:memory:`) for speed or a temporary file for test isolation. Mock ChromaDB client if needed for phase 1. Verify all collection and document operations work correctly together.

### TASK-008
Parsers should return consistent output: (text: str, metadata: dict, errors: list). PDF parser should extract page numbers. URL parser should return the URL and title. Markdown parser should preserve structure. TXT parser should extract plain text. Handle encoding errors (UTF-8 fallback).

### TASK-009
Duplicate detection should run BEFORE document finalization. Implement at least three methods: file hash (MD5 or SHA256), normalized URL canonicalization (strip protocol, trailing slash, query params), and content-hash (normalized text hash). Log detection method and confidence score.

### TASK-010
IngestionService should orchestrate parsing → duplicate check → document creation. If duplicate is detected, create ingestion_attempt with status `duplicate_detected` and wait for user decision. On decision, update document record or skip ingestion. Use descriptive error messages for parse failures.

### TASK-011
Multipart file-upload endpoint should accept collection_id parameter to assign document during ingestion. Return response with document_id, ingestion_status, duplicate_class (if applicable), and error message (if failed). Consider file-size limits and supported MIME types.

### TASK-012
URL ingestion endpoint should handle HTTP redirects, timeouts (e.g., 30s), and non-2xx responses with actionable error messages. Return similar response format to file upload: document_id, status, errors.

### TASK-013
Duplicate decision endpoint should accept one of: `skip`, `replace`, `version-as-new`, `ingest-anyway`. Skip prevents document finalization. Replace deletes the new attempt. Version-as-new creates a new document with link to original. Ingest-anyway proceeds despite duplicate warning.

### TASK-014
Chunking service should accept configurable chunk_size and chunk_overlap (e.g., chunk_size=512, overlap=64). Markdown heading-aware chunking should split on top-level headings (# or ##) and preserve structure. PDF page-aware should split on page boundaries. All chunks should have sequential chunk_order and parent document_id.

### TASK-015
Indexing service should use a configurable embedding model. In the first version, consider free/local providers (e.g., Sentence Transformers, OpenAI API with usage limits, or local models). Store vectors in ChromaDB with collection-aware namespacing (e.g., collection_{collection_id}). Preserve all required metadata: chunk_id, chunk_order, document_id, collection_id, source_url, page/section.

### TASK-016
Delete endpoint must remove document from documents table, related chunks, ingestion attempts, and all ChromaDB vectors. Atomic operation: either all succeed or all roll back to avoid orphaned records. Re-index endpoint should update chunk list and vectors without changing document_id.

### TASK-017
Integration tests should use realistic test data (sample PDF, URL with HTML, Markdown document). Test all decision paths: accept, skip, replace, version-as-new. Verify chunk counts are correct. Verify embeddings are created. Verify re-index cleans up old vectors.

### TASK-018
HTML structure should be semantic: use `<table>` for document list, `<form>` for uploads. All input fields should have `<label>`. Modal overlays for duplicate warnings and errors should use semantic HTML (e.g., `<dialog>` if browser support is acceptable, otherwise `<div role="dialog">`). Consider accessibility (ARIA labels, keyboard navigation).

### TASK-019
File upload form should show selected filename, upload progress if possible (XMLHttpRequest.upload.onprogress or Fetch API with ReadableStream). On success, show "Document uploaded successfully" and refresh document list. On error, show backend error message.

### TASK-020
URL ingestion form should validate URL format (basic regex or URL constructor). Show "Fetching URL..." during request. On success, show ingestion status. On error, show network or parse error.

### TASK-021
Duplicate modal should show: matched document title, matched document ID, duplicate classification, and similarity score if available. Provide four buttons: Skip (cancel ingestion), Replace (use new content), Version as new (create new document linked to original), Ingest anyway (proceed despite warning). On decision, POST to duplicate-decision endpoint and refresh document list.

### TASK-022
Document list fetch should use GET /api/documents?collection_id={id}&search={query}. Render table with rows for each document, showing all AC-006 fields. Add pagination if list is large (e.g., 20 rows per page). Add search input for title substring match. Add dropdown for collection filter.

### TASK-023
Delete action should show confirm dialog: "Delete document '{title}'? This cannot be undone." On confirm, DELETE /api/documents/{id}, then refresh list. Re-index action should POST /api/documents/{id}/re-index, show status message "Re-indexing...", then refresh list and show "Re-indexed successfully" or error.

### TASK-024
Collections HTML should have two main sections: (1) Collections list table with CRUD controls, (2) Documents in selected collection with move-to-collection options. Include create collection form (name, description inputs). Default-collection selector (radio button or star icon).

### TASK-025
Collections list should fetch from GET /api/collections and render table. Each row shows: name, ID, document count (calculated from documents with collection_id), chunk count (calculated from chunks with collection_id), last_updated timestamp. Add indicator for default collection (e.g., star icon or "DEFAULT" label).

### TASK-026
Create collection form: POST /api/collections with {name, description}. Edit: PUT /api/collections/{id} with updates. Delete: DELETE /api/collections/{id} with confirm dialog. Set default: PATCH /api/collections/{id}/default. All operations should refresh the collection list.

### TASK-027
Document-move-to-collection: When user clicks a document row, show move dropdown with list of target collections. On selection, PATCH /api/documents/{id}/collection with {collection_id}. Then refresh documents list for both old and new collections.

### TASK-028
Collection statistics: Display document count, chunk count, last_updated as read-only fields in the collections view. Update these stats after document add, delete, or move via API response or by re-fetching collection detail.

### TASK-029
Manual test checklist should cover:
- [ ] Upload PDF file → verify status "Completed" and document appears in list
- [ ] Upload TXT file → verify status "Completed"
- [ ] Ingest URL → verify status "Completed"
- [ ] Upload duplicate file → verify duplicate warning appears, test all decision options
- [ ] Create collection → verify collection appears in Collections list
- [ ] Assign document to collection during upload → verify document appears in collection
- [ ] Move document to another collection → verify it appears in new collection and disappears from old
- [ ] Delete document → verify it is removed from list
- [ ] Re-index document → verify status updates and chunk count is preserved
- [ ] Verify all document fields are visible: title, ID, source type, collection, status, duplicate flag, chunk count, created, last indexed
- [ ] Verify all collection fields are visible: name, ID, document count, chunk count, last updated
- [ ] Verify error messages are actionable (e.g., "Invalid URL format" not "400 Bad Request")

### TASK-030
Parser unit tests should use pytest. Create fixture files in `backend/tests/fixtures/` (sample.pdf, sample.txt, sample.md, etc.). Test edge cases: empty file, very large file (>10 MB), special characters (emoji, non-ASCII), corrupted headers. Verify error messages are descriptive.

### TASK-031
Duplicate-detection unit tests should cover:
- Exact file hash duplicate (same content)
- URL canonicalization (http vs https, trailing slash, query params)
- Content hash (normalize whitespace and newlines, minor text changes)
- Test data: create synthetic documents with known duplicates and near-duplicates

### TASK-032
Chunking unit tests should verify:
- Fixed-size chunking respects chunk_size and overlap parameters
- Markdown heading-aware chunking preserves # structure and sections
- PDF page-aware chunking respects page boundaries
- All chunks have correct chunk_order and parent document_id
- Edge cases: very short document (< chunk_size), very long document, document with no clear sections

### TASK-033
Indexing unit tests should use mock embedding service or synthetic vectors. Verify:
- Embeddings are generated for all chunks
- ChromaDB stores vectors with correct metadata
- Re-index operation updates vectors without changing document_id
- Collection namespace isolation works (vectors in one collection are not mixed with another)

### TASK-034
Regression-protection tests for consistency: Use integration test setup with real SQLite and ChromaDB. Test scenarios:
- Create document in collection A, move to collection B → verify document appears only in B, chunk metadata is updated, ChromaDB vectors are in correct namespace
- Delete collection with documents → verify documents are reassigned to default or removed, no orphaned records
- Delete document → verify document, chunks, and vectors are all removed

### TASK-035
Document_id stability tests:
- Upload file → store document_id
- Upload same file (should detect exact duplicate) → verify same document_id is in duplicate warning
- Accept duplicate decision → verify document_id is unchanged
- Re-index document → verify document_id never changes

### TASK-036
Observability enhancements:
- Log every ingestion request with: timestamp, document_id, source_type, file_path or URL, status, errors
- Log every duplicate detection with: detected duplicate document_id, duplicate_class, similarity score
- Log every user decision with: decision (skip, replace, version-as-new, ingest-anyway), timestamp, user ID (if available)
- Optional: GET /api/ingestion-logs endpoint to query logs by date, document_id, or status

### TASK-037
Document Library manual verification checklist execution. Follow the test scenarios in TASK-029 for Document Library. Record pass/fail for each scenario. If all pass, mark CC-009 as satisfied.

### TASK-038
Collections manual verification checklist execution. Test create, edit, delete, set-default, move-document operations. Verify all fields are visible and stats are correct. Record pass/fail. If all pass, contribute to CC-009 satisfaction.

### TASK-039
Final traceability audit: Create a table mapping:
- REQ-001 → AC-001 → TASK-003, TASK-008, TASK-011, TASK-018, TASK-019, TASK-030, TASK-037
- REQ-002 → AC-002 → TASK-002, TASK-003, TASK-004, TASK-010, TASK-030, TASK-035
- REQ-003 → AC-003 → TASK-009, TASK-013, TASK-021, TASK-031, TASK-036
- REQ-004 → AC-004 → TASK-014, TASK-015, TASK-016, TASK-032, TASK-033
- REQ-005 → AC-005 → TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-025, TASK-026, TASK-027
- REQ-006 → AC-006 → TASK-018-028, TASK-037, TASK-038

Verify no REQ or AC is orphaned.

---

## Completion Notes

- What was delivered: Task list decomposition from Phase 1 through Phase 4 covering all 39 tasks, with explicit dependencies, parallel-safe markers, file paths, and validation notes for each task.
- What was deferred: None at this stage; all work required by spec.md and plan.md is included.
- What needs follow-up: Alignment on embedding model choice (OpenAI, local Sentence Transformers, etc.) before TASK-015 implementation; confirmation of whether near-duplicate detection beyond content hash is required in first version; decision on long-running ingestion async handling (currently assumed synchronous).

---

## Resume Notes

- Current phase: Ready for implementation—Phase 1 tasks are entry points; no prior work completed.
- Next recommended task: TASK-001 (backend setup and Flask initialization).
- Active blocker: None; all preconditions are met.
- Last validation evidence added: None yet; task list is complete and ready for Phase 1 execution.

# Manual Test Checklist

## Setup

- [ ] Activate the project virtualenv.
- [ ] Start the Flask app with `.venv/bin/python -m flask --app app run`.
- [ ] Open `http://127.0.0.1:5000/document-library.html`.
- [ ] Open `http://127.0.0.1:5000/collections.html`.

## Document Library

- [ ] Upload a PDF file and verify the response banner reports success.
- [ ] Upload a TXT file and verify the document appears in the table with title, document ID, source type, collection, status, duplicate status, chunk count, created timestamp, and last indexed timestamp.
- [ ] Upload a Markdown file and verify the heading-derived title is displayed.
- [ ] Ingest a URL and verify the response banner reports success and the new document appears in the table.
- [ ] Enter an invalid URL and verify the screen shows an actionable validation message.
- [ ] Upload a duplicate file and verify the duplicate modal appears with matched document, classification, similarity score, and detection method.
- [ ] In the duplicate modal, test `skip` and verify the document status becomes `skipped`.
- [ ] Upload the duplicate again, test `replace`, and verify the matched document remains usable.
- [ ] Upload the duplicate again, test `version-as-new`, and verify a separate completed document row appears.
- [ ] Upload the duplicate again, test `ingest-anyway`, and verify the new document completes indexing.
- [ ] Click `Re-index` on a completed document and verify the banner reports success and the document remains in the list.
- [ ] Click `Delete` on a document and verify the row disappears from the table.
- [ ] Use the title search input and verify the table filters correctly.
- [ ] Use the collection filter and verify the table only shows documents from the selected collection.

## Collections

- [ ] Create a collection and verify it appears in the collections table with name, collection ID, document count, chunk count, and last updated timestamp.
- [ ] Set a collection as default and verify the default indicator appears in the table.
- [ ] Edit a collection name and verify the updated value appears in both the table and selected collection panel.
- [ ] Click a collection row and verify the selected collection panel shows collection ID, document count, chunk count, last updated timestamp, and description text.
- [ ] Upload or move a document into a collection and verify it appears in the `Documents In Selected Collection` table.
- [ ] Move a document from one collection to another and verify it disappears from the old collection view and appears in the new one.
- [ ] Attempt to delete a non-empty collection and verify the UI surfaces the backend error clearly.
- [ ] Delete an empty collection and verify it disappears from the table.

## Observability

- [ ] Call `GET /api/ingestion-logs` in the browser or a REST client and verify entries include document ID, source type, status, duplicate class, user decision, and timestamps.
- [ ] Confirm duplicate decisions remain visible in the log payload after the decision is applied.

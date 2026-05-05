# Manual Test Checklist

## Setup

- [ ] Activate the project virtualenv.
- [ ] Start the Flask app with `.venv/bin/python -m flask --app backend.app run --debug`.
- [ ] Open `http://127.0.0.1:5000/chat.html`.
- [ ] Verify `Document Library`, `Collections`, and `Grounded Chat` are all reachable from the top navigation.

## Sessions And Scope

- [ ] Create a new chat session and verify a session entry appears in the sidebar.
- [ ] Select a specific collection, create another session, and verify the selected collection is reflected in the session metadata.
- [ ] Switch between two existing sessions and verify the conversation history changes with the selected session.
- [ ] Refresh the page and verify the previously selected session can still be reopened from the URL or sidebar.

## Supported Answers

- [ ] Ask a supported question against a populated collection and verify a grounded answer appears.
- [ ] Verify the answer panel shows a final completed state rather than an idle or error state.
- [ ] Verify citations appear only after the final answer is completed.
- [ ] Switch retrieval mode between `semantic`, `keyword`, and `hybrid` and verify the chosen mode is reflected in the response metadata or debug panel.
- [ ] Switch collection scope between a specific collection and `All collections` and verify the answer or sources change when the underlying evidence differs.

## Refusals

- [ ] Ask a question with no matching evidence and verify the UI shows a refusal rather than a fabricated answer.
- [ ] Verify the refusal includes a visible reason category such as `no_relevant_evidence`, `low_confidence`, `insufficient_support`, `conflicting_evidence`, or `out_of_domain`.
- [ ] Verify supporting metrics appear when they are provided.

## Streaming And Cancellation

- [ ] Enable the streaming toggle and ask a supported question.
- [ ] Verify visible progress states appear in order, such as retrieving, packing context, generating, and final completion.
- [ ] While streaming is active, click `Cancel` and verify the answer stops and the turn is marked cancelled.
- [ ] Verify cancelled turns do not render final citations.

## Citation Inspection

- [ ] Click an inline citation marker from a completed answer and verify the citation detail modal opens.
- [ ] Verify the modal shows document title, chunk ID, page or section, retrieval mode, retrieval score, source URL when available, and a supporting snippet.
- [ ] Click `View In Library` and verify the link opens `document-library.html` with the cited document highlighted by its `document_id` query parameter.
- [ ] Inspect multiple citations in the same answer and verify they map back to real stored chunks rather than synthesized content.

## History And Regression

- [ ] Ask multiple questions in one session and verify the history panel preserves message order and timestamps.
- [ ] Verify refusals are visually distinguishable from successful answers in the conversation history.
- [ ] Open the Document Library and Collections pages after chat testing and verify feature 1 behavior still works.

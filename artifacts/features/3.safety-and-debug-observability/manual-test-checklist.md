# Manual Test Checklist

## Setup

- [ ] Activate the project virtualenv.
- [ ] Start the Flask app with `.venv/bin/python -m flask --app backend.app run --debug`.
- [ ] Open `http://127.0.0.1:5000/chat.html`.
- [ ] Verify `Document Library`, `Collections`, and `Grounded Chat` remain reachable from the top navigation.

## Warning Surfaces

- [ ] Ask a benign supported question and verify no warning banner is shown beyond the normal groundedness state.
- [ ] Ask a query containing suspicious instruction-like text and verify the UI shows a safety warning or refusal explanation.
- [ ] Trigger excluded-evidence behavior with a suspicious document chunk and verify the UI shows an excluded-evidence notice that explains the effect on the answer flow.
- [ ] Verify groundedness, answerability, and refusal messaging remain readable on both desktop and mobile widths.

## Debug View

- [ ] Toggle `Debug Panel` on and ask a supported question.
- [ ] Verify the Debug View shows query, retrieval mode, retrieved chunks, selected context, citations, latency, token count, model identifiers, and final answer data.
- [ ] Trigger a refused run and verify the Debug View still renders refusal details, safety issues, and final decision data.
- [ ] Trigger a suspicious chunk exclusion and verify excluded chunks are listed with reasons.

## Persisted Re-entry

- [ ] Complete at least one answered run and one warned or refused run.
- [ ] Refresh the page and reopen the same session.
- [ ] Verify the latest response panel still shows the prior warning or refusal state from persisted run data.
- [ ] Click `Inspect Debug View` from conversation history and verify the persisted run can still be inspected after reload.

## Regression Checks

- [ ] Open the Document Library and Collections pages after safety-debug testing and verify feature 1 behavior still works.
- [ ] Ask a normal grounded question again and verify the answer still includes citations and is not falsely refused.

# Testing Guide: Citation Upgrades & UI Anchoring

This guide provides the instructions and test cases to verify the generation-time citations, unified inline badge formatting, auto-scrolling, visual highlighting, and invalid citation styling.

---

## 1. Setup: Upload & Ingest
1. Open the Chatbot UI in your browser.
2. Create or select a Collection.
3. In the Documents panel, click **Upload** and select [q3_earnings.txt](file:///Users/thaihai-swe/Desktop/chatbot-with-data/test-features/q3_earnings.txt).
4. Wait for the ingestion pipeline to complete and verify the document is listed.

---

## 2. Test Cases

### Test Case 1: Multi-Source Answer & Short Labels
* **Input Question**:
  ```text
  What was the company's revenue, operating expenses, and net income in Q3 2024?
  ```
* **Expected Response**:
  The assistant should generate an answer where each claim is accompanied by an inline citation:
  * Revenue claim is cited (e.g. `[1]` or `[Source 1]`).
  * Operating expenses claim is cited (e.g. `[2]` or `[Source 2]`).
  * Net income claim is cited (e.g. `[3]` or `[Source 3]`).
* **Verification**:
  * Check that the citations are parsed and displayed as uniform badges showing both the source ID and the document name, e.g., `[Source 1 - q3_earnings.txt]`, `[Source 2 - q3_earnings.txt]`, and `[Source 3 - q3_earnings.txt]`.

### Test Case 2: Citation Click Popup Modal
1. Locate any inline citation badge in a generated response (e.g., `[Source 1 - q3_earnings.txt]`).
2. Click the badge.
3. **Verification**:
  * A modal popup must open containing the exact cited text chunk quote and document title.
  * Clicking "Close" on the modal must successfully dismiss the popup.

### Test Case 3: Visual Highlight in SourceBrowser
1. Open the left **Sources** panel and open `q3_earnings.txt` (or `.md`) in the document browser.
2. Select any chunk from the chunk list.
3. **Verification**:
  * The selected chunk must be highlighted with a soft background shade and a distinct focus border to differentiate it clearly from other chunks.
  * Clicking another chunk must immediately move the visual highlight to the newly selected chunk.

### Test Case 4: Invalid/Mismatched Citations
* **Test Input**:
  Ask the model a question, or mock a chat history entry where the text includes an out-of-range index (e.g., `[Source 9]` or `[4]` when only 3 sources exist).
* **Verification**:
  * The invalid citation badge `[Source 9]` must render with muted styling (reduced opacity, gray color, no underline).
  * The cursor should remain as the default pointer when hovering.
  * Hovering must NOT open a HoverCard.
  * Clicking the badge must have no effect.

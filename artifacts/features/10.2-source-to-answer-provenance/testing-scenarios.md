# Testing Scenarios — 10.2 Source-to-Answer Provenance

## Purpose

Manual and semi-automated verification of claim-level provenance: paragraph classification (cited/uncited), coverage metrics, SSE/GET payload, ChatPanel `[unsupported]` markers, badge→panel anchoring, X-Ray provenance section, and stream groundedness parity.

## Scope

- Feature name: Source-to-Answer Provenance
- Feature slug: `10.2-source-to-answer-provenance`
- Delivered scope under test: ADR-001 post-gen claim graph + `provenance_json` + coverage + X-Ray + display-layer `[unsupported]` + panel anchor
- Out of scope: constrained decoding, hard repair loops, multi-modal cites, save-to-note, badge label reformat

## Estimated Time

- Approximate total time: **25–40 minutes** (setup + happy path + edges)

## Prerequisites

- Required environment: App running (`backend` + `frontend` + Weaviate if used for retrieval)
- Required accounts or permissions: none (local)
- Required services or dependencies: LLM provider configured (same as normal chat)
- Required data or fixtures:
  - `artifacts/features/10.2-source-to-answer-provenance/fixtures/q3-revenue-report.md`
  - `artifacts/features/10.2-source-to-answer-provenance/fixtures/cost-efficiency-memo.md`

## Setup

1. Start backend and frontend (per project README / docker-compose).
2. Open the app → **Library** (or Collections) → create a collection named `10.2-provenance-verify`.
3. Upload both fixture files into that collection and wait until indexing completes.
4. Open **Chat** → select collection `10.2-provenance-verify` → ensure both documents are checked in Sources.
5. Optional API check: `GET /chat/turns/{id}/provenance` available after a turn completes.

### Fixture files (upload these)

| File | Path | Purpose |
|------|------|---------|
| Q3 Revenue Report | `fixtures/q3-revenue-report.md` | Primary factual source (revenue, margin, outlook) |
| Cost Efficiency Memo | `fixtures/cost-efficiency-memo.md` | Second source (cost savings, cloud, vendors) |

### Recommended questions (copy-paste)

| ID | Question | Why |
|----|----------|-----|
| Q1 | What was Acme's Q3 2024 revenue growth, and what operating margin did they report? | Multi-fact answer likely fully cited from revenue report |
| Q2 | Summarize Q3 revenue growth and the cost-efficiency program savings. Mention any geographic mix. | Cross-document; should cite both sources across paragraphs |
| Q3 | What is the capital of France, and how does it relate to Acme's Q3 results? | Forces uncited / unsupported content → expect `[unsupported]` on some paragraphs |
| Q4 | List every cost-saving initiative from the efficiency memo and the annualized cloud savings. | Dense citation from memo only |
| Q5 | Write three short paragraphs: (1) revenue growth, (2) your personal opinion on whether Acme is a buy, (3) cloud savings. | Paragraph 2 should be uncited if model complies with grounded prompt |

---

## Scenario Matrix

| Scenario | Linked AC | Goal | Priority | Notes |
|-|-|-|-|-|
| SCN-001 Fully cited multi-fact answer | AC-001, AC-002, AC-005 | Claim graph + 100% coverage | P0 | Use Q1 |
| SCN-002 Partial citation + `[unsupported]` | AC-001, AC-003, AC-005 | Uncited paragraphs marked | P0 | Use Q3 or Q5 |
| SCN-003 Badge → panel anchor | AC-006 | Click badge opens Sources + highlight | P0 | After SCN-001 |
| SCN-004 SSE provenance payload | AC-005 | `provenance` on citations event | P0 | DevTools / network |
| SCN-005 GET provenance endpoint | AC-004, AC-005 | Same shape as SSE | P1 | After any turn |
| SCN-006 X-Ray provenance section | AC-007 | Coverage + claims + reverse map | P1 | Debug/X-Ray open |
| SCN-007 Stream groundedness score | AC-009 | Score persisted on stream path | P1 | SSE or DB |
| SCN-EDGE-001 Empty / no-evidence query | AC-001, AC-002 | Refusal or 0 coverage, no crash | P1 | |
| SCN-EDGE-002 Invalid citation labels | AC-001 | Hallucinated [Source 99] → uncited | P2 | |
| SCN-EDGE-003 Single-paragraph answer | AC-001, AC-002 | total=1 path | P2 | |
| SCN-EDGE-004 History reload | AC-003, AC-005 | Provenance survives refresh | P1 | |
| SCN-EDGE-005 Dual-format [N] vs [Source N] | AC-001 | Both parse | P2 | |
| SCN-REG-001 Streaming tokens still work | INV-003 | Tokens before citations event | P0 | |
| SCN-REG-002 Safety + grounding refusal | INV-010 | No fake citations on refuse | P1 | |
| SCN-REG-003 Legacy Chat.jsx path dead | AC-010 | No modal path from ChatScreen | P2 | Code/grep check |

---

## Happy Path Scenarios

### SCN-001: Fully cited multi-fact answer

**Goal:** Prove claim graph classifies every paragraph as cited with coverage 100% when the model cites sources.

**Linked acceptance criteria:** AC-001, AC-002, AC-005

**Steps:**

1. Complete Setup (both fixtures indexed, collection selected).
2. Ask **Q1**: *What was Acme's Q3 2024 revenue growth, and what operating margin did they report?*
3. Wait for stream to finish (status → finalizing → done).
4. Inspect chat answer: badges like `Source 1 - …` appear after factual claims.
5. Open browser DevTools → Network → SSE (or EventStream) → find `event: citations` payload; confirm `provenance.claims` and `provenance.coverage` exist.
6. Open X-Ray (if available on the turn) and confirm Provenance section shows coverage and claims.
7. Optional: `curl -s http://127.0.0.1:8000/chat/turns/{turn_id}/provenance | jq .`

**Expected results:**

- Answer has ≥1 paragraph with citation badges (not plain uncited text only).
- `provenance.coverage.total ≥ 1` and `cited` equals number of paragraphs with resolved labels (often 100% for Q1).
- Each claim has `index`, `text`, `labels`, `chunks`, `cited`.
- No crash; SSE order remains: tokens → citations → done.

**Evidence to capture:** Screenshot of answer + X-Ray; JSON snippet of `provenance.coverage`.

---

### SCN-002: Partial citation shows `[unsupported]`

**Goal:** Uncited paragraphs render muted `[unsupported]` without mutating stored answer text.

**Linked acceptance criteria:** AC-001, AC-003, AC-005

**Steps:**

1. Same collection as SCN-001.
2. Ask **Q3**: *What is the capital of France, and how does it relate to Acme's Q3 results?*  
   (or **Q5** for forced multi-paragraph mix).
3. Wait for completion.
4. Inspect chat UI for any paragraph prefixed/marked with muted `[unsupported]`.
5. Confirm cited paragraphs still show normal badges.
6. Reload history for the session; markers still appear from stored `provenance` / GET (display-layer only).

**Expected results:**

- At least one claim has `cited: false` in provenance when model invents off-corpus content.
- UI shows `[unsupported]` (muted, non-clickable) only on uncited paragraphs.
- Stored `answer_text` does not gain literal `[unsupported]` strings if inspected via API (display-layer only).
- Coverage `cited/total < 1` when uncited paragraphs exist.

**Evidence:** Screenshot of `[unsupported]` + provenance JSON with `uncited_indices`.

---

### SCN-003: Badge click anchors Sources panel

**Goal:** Finish 9.0 wire-up — badge opens left panel and highlights chunk (no CitationModal).

**Linked acceptance criteria:** AC-006

**Steps:**

1. From SCN-001 answer, click a citation badge (`Source N - Title`).
2. Observe left Sources panel: expands if collapsed, document opens in SourceBrowser.
3. Confirm target chunk is selected/highlighted and scrolled into view.
4. Confirm **no** CitationModal overlay opens as primary action.

**Expected results:**

- `setActiveChunkId` path: Sources expanded, chunk highlighted.
- Modal does not open from badge click.

**Evidence:** Screenshot of Sources panel with highlighted chunk.

---

### SCN-004: SSE `citations` includes provenance

**Goal:** Additive protocol field present.

**Linked acceptance criteria:** AC-005

**Steps:**

1. Open DevTools Network before sending Q1 or Q2.
2. Submit turn via stream endpoint.
3. Locate `event: citations` data JSON.
4. Assert keys: `citations`, `retrieved_chunks`, `provenance` (with `claims` + `coverage`), optionally `groundedness_score`.

**Expected results:**

- `provenance.claims` is an array; `provenance.coverage` has `cited`, `total`, `uncited_indices`.
- Event order unchanged: tokens first, then citations, then done.

---

### SCN-005: GET `/chat/turns/{id}/provenance`

**Goal:** REST parity with SSE payload.

**Linked acceptance criteria:** AC-004, AC-005

**Steps:**

1. After any completed turn, copy `turn_id` from SSE `done` or history.
2. Run:  
   `curl -s http://127.0.0.1:8000/chat/turns/{turn_id}/provenance | jq .`
3. Compare shape to SSE `provenance` field.

**Expected results:**

- 200 with `{ claims: [...], coverage: {...} }`.
- 404 for unknown turn id.
- Empty/default object if turn has no provenance (legacy turns).

---

### SCN-006: X-Ray Provenance section

**Goal:** Debug surface shows claim graph + reverse map.

**Linked acceptance criteria:** AC-007

**Steps:**

1. Complete Q2 (cross-document).
2. Open Pipeline X-Ray for that turn.
3. Verify sections: coverage summary (`X/Y paragraphs cited (Z%)`), claim list, reverse map chunk → claim indices.

**Expected results:**

- Coverage numbers match GET/SSE provenance.
- Claims show cited/uncited badge and excerpt.
- Reverse map lists chunk ids supporting claim indices.

---

### SCN-007: Stream path groundedness score

**Goal:** Stream finalize persists groundedness (Phase 0 parity).

**Linked acceptance criteria:** AC-009

**Steps:**

1. Stream Q1.
2. In SSE `citations` event, check `groundedness_score` is a number.
3. Optional: inspect turn row / history response for `groundedness_score`.

**Expected results:**

- Score present on stream path (not only sync).
- X-Ray Safety grounded % may reflect same score when trace includes it.

---

## Edge Cases And Failure Paths

### SCN-EDGE-001: Empty / no-evidence query

**Goal:** No crash; refusal or empty provenance.

**Linked acceptance criteria:** AC-001, AC-002

**Steps:**

1. Uncheck all documents (or use empty collection).
2. Ask: *What is Acme's revenue?*
3. Observe refusal / insufficient evidence path.

**Expected results:**

- No 500; turn completes or refuses cleanly.
- No fabricated citation badges claiming sources that were not retrieved.
- Provenance empty or all uncited — no exception in finalize.

---

### SCN-EDGE-002: Invalid / OOB citation labels

**Goal:** Hallucinated `[Source 99]` does not map to chunks.

**Linked acceptance criteria:** AC-001

**Steps:**

1. Ask Q1; if model emits only valid labels, note in evidence and skip, **or** inspect unit-test path already covering invalid labels.
2. In provenance, claims with only invalid labels: `cited: false`, `chunks: []`, labels may still list `"99"`.

**Expected results:**

- Invalid labels not mapped to chunks.
- UI treats those paragraphs as uncited / muted badges if present.

---

### SCN-EDGE-003: Single-paragraph answer

**Goal:** Boundary total=1.

**Linked acceptance criteria:** AC-001, AC-002

**Steps:**

1. Ask: *In one short sentence only: what was Q3 revenue growth?*
2. Inspect provenance.

**Expected results:**

- `coverage.total === 1`.
- `cited` is 0 or 1; no off-by-one in uncited_indices.

---

### SCN-EDGE-004: History reload preserves display markers

**Goal:** Display-layer markers work after refresh.

**Linked acceptance criteria:** AC-003, AC-005

**Steps:**

1. Complete SCN-002.
2. Refresh page / re-open session history.
3. Confirm `[unsupported]` still appears for uncited claims (via history `provenance` or GET).

**Expected results:**

- History turn includes provenance (or client fetches GET).
- Markers reappear without re-running generation.

---

### SCN-EDGE-005: Dual citation formats

**Goal:** `[Source 1]` and `[1]` both resolve.

**Linked acceptance criteria:** AC-001

**Steps:**

1. Prefer unit tests already covering dual regex; optionally ask model to use short form if prompt allows.
2. Confirm badges render for both formats when present.

**Expected results:**

- Both formats map to chunks; no parse crash.

---

### SCN-EDGE-006: Concurrent rapid submits `[OUT OF SCOPE — Optional]`

**Goal:** Race stability.

**Steps:** Fire two questions quickly in same session.

**Expected results:** Each turn gets own provenance; no cross-turn chunk mix-up. Document any flake.

---

## Regression Checks

| Behavior that must still work | Validation | Evidence |
|-------------------------------|------------|----------|
| SSE tokens stream before citations (INV-003) | SCN-004 event order | Network log |
| 3-layer safety still runs | Injection-style query refused | Screenshot |
| Grounding refusal no fake cites (INV-010) | SCN-EDGE-001 | Answer text |
| Hybrid retrieval still returns chunks | Q1 has retrieved_chunks | SSE payload |
| SourceBrowser scroll still works for manual doc open | Open doc without citation click | Manual |
| X-Ray retrieval/safety sections unchanged | Open X-Ray | Screenshot |
| Legacy Chat.jsx has no CitationModal (AC-010) | `grep CitationModal frontend/src/screens/Chat.jsx` → 0 | Terminal |

**Unit proof (automated):**

```bash
PYTHONPATH=backend python3 -m pytest \
  backend/tests/chat/test_provenance.py \
  backend/tests/chat/test_citations.py \
  backend/tests/chat/test_migrations.py \
  backend/tests/chat/test_conflict.py -v
```

Expect: all pass (41 in last implement run).

---

## Notes For Testers

- **Model nondeterminism:** Coverage % depends on whether the LLM emits `[Source N]`. Prefer Q1/Q2 for high citation rate; use Q3/Q5 to force uncited content.
- **Indexing lag:** If answers say “no documents,” wait for index complete and recheck collection checkboxes.
- **Badge label:** Still `Source N - Title` by design (not short-only).
- **Modal:** Should not open from badge click; notes may still live in SourceBrowser.
- **Escalate immediately:** 500 on finalize, missing `provenance` key on new turns, panel never expands on badge click, or `[unsupported]` written into stored `answer_text`.

### Known limitations (v1)

- Paragraph split on blank lines only (lists/code may mis-segment).
- Jaccard-only quotes (no LLM quote fallback).
- Soft prompt enforcement only — model may under-cite even on Q1.

---

## Sign-Off

- Tested by:
- Date:
- Passed scenarios:
- Failed scenarios:
- Deferred scenarios:
- Overall outcome: ☐ Pass  ☐ Pass with notes  ☐ Fail
- Evidence or screenshots linked:

---

## Quick-start card (print this)

```
1. Create collection "10.2-provenance-verify"
2. Upload:
   - fixtures/q3-revenue-report.md
   - fixtures/cost-efficiency-memo.md
3. Chat → select collection → both docs checked
4. Ask: "What was Acme's Q3 2024 revenue growth, and what operating margin did they report?"
5. Check: badges present, X-Ray Provenance, click badge → Sources highlight
6. Ask: "What is the capital of France, and how does it relate to Acme's Q3 results?"
7. Check: [unsupported] on off-corpus paragraphs
8. curl GET /chat/turns/{turn_id}/provenance
```

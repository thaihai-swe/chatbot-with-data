# PII Detection (Roadmap)

**Status:** ⏳ Planned — not yet implemented  
**Last verified:** 2026-05-29  
**Source files:** N/A (no PII detector exists in current codebase)

---

## Honest Status

**PII detection is not implemented.** This document describes the planned design and configuration once the feature is built.

The previous version of this doc described a working system with `presidio-analyzer`, `PII_Detector`, and `.env` configuration. None of that code exists. `requirements.txt` does not include `presidio`. The `chat/safety.py` module covers prompt injection only, not PII.

If you are looking for shipped safety features, see:
- [PROMPT_INJECTION_DETECTION.md](./PROMPT_INJECTION_DETECTION.md) — three-layer injection defense (heuristic, fuzzy, LLM)
- [SYSTEM_VALIDATION_GUIDE.md](./SYSTEM_VALIDATION_GUIDE.md) — input validation

---

## Why Add PII Detection

In production RAG systems, ingested documents may contain personally identifiable information (PII): emails, phone numbers, SSNs, credit card numbers, names, addresses. Indexing this data without controls creates:

- **Compliance risk** — GDPR, CCPA, HIPAA require controls over PII storage and retrieval.
- **Leakage risk** — RAG retrieval can surface PII to users who shouldn't see it.
- **Audit gap** — Without detection, you cannot answer "does our index contain PII?"

---

## Planned Design

### Detection Layer
- **Library:** `presidio-analyzer` (Microsoft) — open source, mature, supports custom recognizers.
- **Coverage:** Email, phone, SSN, credit card, IBAN, IP address, person names (NER), addresses, dates of birth.
- **Custom recognizers:** Domain-specific patterns (employee IDs, internal references) via YAML config.
- **Multi-language:** Initial English support; extendable via spaCy models.

### Pipeline Integration
PII detection runs at two points:

1. **At ingestion** — Scan extracted text before chunking. Block, redact, or flag based on configuration.
2. **At retrieval/response** — Optional second pass on retrieved chunks before sending to LLM, and on LLM output before returning to user.

### Sensitivity Levels
- **`strict`** — Block any PII detection (high false-positive rate; safe default for regulated industries).
- **`moderate`** — Block high-risk PII (SSN, credit card); flag others.
- **`lenient`** — Log only; allow indexing.

### Actions
- **`block`** — Reject ingestion; surface error to user.
- **`redact`** — Replace PII with `[REDACTED:EMAIL]` style tokens; index redacted version.
- **`warn`** — Allow ingestion; log detection event; flag in UI.
- **`log`** — Allow silently; record to audit trail.

### Configuration (Planned)
```bash
# .env
DETECT_PII=true
PII_DETECTION_LEVEL=moderate          # strict | moderate | lenient
PII_ACTION=warn                        # block | redact | warn | log
PII_ALLOWED_COLLECTIONS=internal-hr    # semicolon-separated allowlist
PII_CUSTOM_RECOGNIZERS=config/pii_patterns.yaml
```

### Schema Changes (Planned)
New table: `pii_detections`
```sql
CREATE TABLE pii_detections (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_id TEXT,
    pii_type TEXT NOT NULL,        -- email, phone, ssn, etc.
    confidence REAL NOT NULL,
    excerpt TEXT,                   -- redacted snippet
    action_taken TEXT NOT NULL,     -- block, redact, warn, log
    created_at TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY(chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
);
```

Add column on `documents`: `pii_status TEXT` (none, detected, redacted, blocked).

### API Endpoints (Planned)
- `GET /pii/detections` — List PII detection events (filterable by document, type, action).
- `GET /pii/stats` — Summary stats per collection.
- `POST /documents/{id}/redact` — Re-process document with current PII rules.

### UI Surface (Planned)
- **Document Library:** Show PII badge on documents with detected PII.
- **Ingestion screen:** Show PII warnings before final indexing.
- **Settings:** Configure detection level and actions per collection.

---

## Implementation Steps

When this lands, expected order of work:

1. Add `presidio-analyzer` and spaCy English model to `requirements.txt`.
2. Add `backend/safety/pii_detector.py` with `PIIDetector` class.
3. Add `pii_detections` table via new migration.
4. Wire detection into `ingestion/service.py` after extraction, before chunking.
5. Add config flags to `Settings` and `GlobalSettings` (Pydantic).
6. Expose endpoints in a new `routers/pii.py`.
7. Add UI badges and warnings.
8. Add eval cases: documents with known PII, verify detection rate.
9. Document custom recognizer authoring.

---

## Why This Doc Exists Now

Production RAG PRDs require PII handling. Keeping a clearly-labeled roadmap doc:
- Sets reviewer expectations honestly.
- Captures design intent before implementation.
- Avoids the previous trap of describing nonexistent features as if shipped.

When PII detection ships, this doc graduates to `🟢 Implemented` and gains real configuration examples, test cases, and tuning guidance.

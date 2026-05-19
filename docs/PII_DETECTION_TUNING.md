# PII Detection Tuning Guide (Chatbot System)

This guide provides practical guidance for configuring and tuning PII detection in the chatbot system. It mirrors the reference document `ref-docs/PII_DETECTION_TUNING.md` but includes concrete examples, CLI commands, and integration points specific to this implementation.

## Configuration Overview

PII detection is governed by four environment variables in the project's ``.env`` file:

```bash
# Enable or disable PII detection globally
DETECT_PII=true

# Detection sensitivity: strict, moderate, or lenient
PII_DETECTION_LEVEL=moderate

# Collections allowed to contain PII (semicolon-separated list)
PII_ALLOWED_COLLECTIONS=

# Action when PII is detected: warn, block, or log
PII_ACTION=warn
```

### How the Chatbot Uses These Settings

- **During ingestion** (`POST /ingestion/*`), the `backend/chat/safety.py` module runs `SafetyService._check_heuristics` and, if enabled, invokes the `PII_Detector` (built on `presidio-analyzer`).
- **Before indexing** each document chunk, the system validates against the configured `PII_DETECTION_LEVEL` and respects `PII_ALLOWED_COLLECTIONS`.
- **User feedback** is generated via the `SafetyService` response, matching the `PII_ACTION` behavior.

## Recommended Settings per Deployment

| Environment | DETECT_PII | PII_DETECTION_LEVEL | PII_ALLOWED_COLLECTIONS | PII_ACTION |
|------------|------------|---------------------|------------------------|-----------|
| **Production (HIPAA/PCI)** | true | strict | (empty) – no exemptions | block |
| **Enterprise SaaS** | true | moderate | test_data;demo | warn |
| **Development** | true | lenient | dev_data;test_data | log |
| **Open‑source demo** | true | moderate | demo_collection | warn |

### Why These Choices
- **Production**: `strict` catches every possible PII; `block` guarantees no PII enters the system, meeting compliance.
- **Enterprise SaaS**: `moderate` balances coverage and usability; `warn` offers operators choice while preserving audit trail.
- **Development**: `lenient` reduces false positives when engineers use realistic test data; `log` avoids interrupting workflow yet keeps an audit.
- **Demo**: Allows a clean public demo collection while still warning users of any accidental PII.

## CLI Utilities for Tuning

The chatbot ships with CLI helpers (via `backend.cli`). Use them to verify configuration and inspect detection results.

```bash
# Validate current PII configuration
python -m backend.cli validate-pii-config

# Simulate PII detection on a sample file
python -m backend.cli test-pii-detection --file path/to/sample.txt

# Export recent PII incidents from audit log (last 7 days)
python -m backend.cli export-pii-incidents --days 7 --format csv > pii_report.csv
```

### Example Output (warning mode)
```
⚠️  PII DETECTED

The document you're about to ingest contains:
  - Email addresses (2 found)
  - Phone numbers (1 found)

Options:
1. Cancel - Do not ingest
2. Force Ingest - Continue anyway (logged)
3. Help - Learn more about PII handling
Choose: [1/2/3]
```

## Tuning Tips

1. **Adjust Sensitivity**
   - To reduce false positives on technical docs, switch to `lenient`:
     ```bash
     PII_DETECTION_LEVEL=lenient
     ```
   - To tighten coverage for regulated data, use `strict`.
2. **Exempt Collections**
   - Add collections that intentionally store PII (e.g., `test_data`):
     ```bash
     PII_ALLOWED_COLLECTIONS=test_data;training_data
     ```
   - Remember: even exempted collections still log findings if `PII_ACTION=log`.
3. **Change Action**
   - For fully automated pipelines, set `PII_ACTION=log` to silently ingest while keeping audit trails.
   - For strict compliance, set `PII_ACTION=block`.
4. **Review Audit Logs**
   - All detections are recorded in `logs/security_audit.log` as JSON Lines. Use `jq` to filter:
     ```bash
     jq 'select(.event_type=="PII_DETECTED")' logs/security_audit.log | wc -l
     ```
5. **Test Before Deploy**
   - Run `python -m backend.cli test-pii-detection` on a representative dataset to verify false‑positive/negative rates.

## Common Pitfalls

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Frequent warnings on code snippets | `PII_DETECTION_LEVEL=moderate` treating `example@example.com` in comments as PII | Switch to `lenient` or add collection to `PII_ALLOWED_COLLECTIONS` |
| No warnings but audit shows `PII_DETECTED` events | `PII_ACTION=log` suppresses UI warnings | Check audit log for hidden detections |
| Ingestion blocked unexpectedly | `PII_ACTION=block` with `strict` level on a collection not in `PII_ALLOWED_COLLECTIONS` | Add collection to allowed list or change action to `warn` |

## Integration Points

- **Ingestion Service (`backend/ingestion/service.py`)** – Calls `SafetyService.check_query` and `SafetyService.check_chunks` before persisting.
- **LLM Generation (`backend/generation.py`)** – After generating a response, the system may re‑run `SafetyService` on the answer to catch any generated PII.
- **Audit Logging (`backend/safety/audit.py`)** – All PII events flow here and are stored in `logs/security_audit.log`.

## Monitoring & Alerts

Configure alerting (e.g., via webhook) for high‑severity PII events:

```bash
# .env addition for webhook
PII_ALERT_WEBHOOK_URL=https://example.com/pii-alert
PII_ALERT_SEVERITY=high
```

The `backend.cli` tool can test webhook delivery:

```bash
python -m backend.cli test-pii-alert --type high
```

## Review Cycle

1. **Quarterly** – Review audit logs for false‑positive trends.
2. **When adding new collections** – Update `PII_ALLOWED_COLLECTIONS` if they hold test data.
3. **After regulatory changes** – Re‑evaluate `PII_DETECTION_LEVEL` and `PII_ACTION`.

---

For more details on the underlying detection engine, see `ref-docs/PII_DETECTION_TUNING.md` and the `presidio-analyzer` documentation.

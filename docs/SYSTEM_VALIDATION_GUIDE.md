# System Validation Guide

This guide explains the validation and quality assurance mechanisms in the RAG Knowledge Base Lab system, covering input validation, data integrity checks, configuration validation, and system health monitoring.

## Overview

The system includes comprehensive validation across multiple layers to ensure data quality, system stability, and reliable operation. This guide covers:

1. **Input Validation** – Validates queries, documents, and configuration.
2. **Data Integrity** – Ensures consistency across storage layers.
3. **Configuration Validation** – Verifies environment and system settings.
4. **Health Monitoring** – Tracks system status and performance.
5. **Error Recovery** – Handles failures gracefully.

---

## 1. Input Validation

### Query Validation

**Purpose:** Ensure queries are safe, well‑formed, and within system limits.

**What Gets Validated:**

1. **Query Length** – Maximum 10,000 characters by default
   - **Why:** Prevents memory exhaustion and embedding model overload.
   - **What it stops:** Extremely long inputs that could crash the system.

2. **Injection Patterns** – Detects prompt‑injection keywords (e.g., "ignore previous instructions", "system override").
   - **Why:** Identifies attempts to override system instructions.
   - **What it stops:** Queries attempting to manipulate LLM behavior.

3. **Character Encoding** – Validates UTF‑8 encoding.
   - **Why:** Prevents Unicode‑based attacks that could confuse parsers.
   - **What it stops:** Invalid byte sequences designed to bypass validation.

4. **Query Structure** – Validates query format and completeness.
   - **Why:** Ensures queries can be processed by the retrieval pipeline.
   - **What it stops:** Malformed queries that would cause parsing errors.

**Configuration:**

```bash
# Maximum query length in characters (default: 10000)
MAX_QUERY_LENGTH=10000

# Enable injection detection (default: true)
ENABLE_INJECTION_DETECTION=true

# Injection detection level: strict, moderate, lenient (default: moderate)
INJECTION_DETECTION_LEVEL=moderate
```

**User Experience:**

When a query is rejected:

```
Error: Query Validation Failed

Problem: Your query exceeds the maximum length limit

Context: Query length is 15,000 characters (max: 10,000)

Why This Matters: Long queries consume excessive memory during embedding and retrieval,
potentially destabilizing the system for other users.

What To Do: Please split your query into smaller, focused questions.
Example: Instead of asking 5 questions at once, ask them one at a time.
```

### Document Validation

**Purpose:** Protect the system against memory exhaustion and encoding attacks during ingestion.

**What Gets Validated:**

1. **File Size** – Maximum 100 MB by default
   - **Why:** Prevents memory exhaustion when loading documents.
   - **What it stops:** Attackers uploading multi‑gigabyte files to crash the system.

2. **File Format** – Validates supported formats (PDF, TXT, MD).
   - **Why:** Ensures documents can be parsed correctly.
   - **What it stops:** Unsupported formats that could cause parsing failures.

3. **Character Encoding** – Validates UTF‑8 encoding.
   - **Why:** Ensures documents can be safely parsed and chunked.
   - **What it stops:** Malformed documents that could cause parsing failures.

4. **Content Validation** – Checks for valid content structure.
   - **Why:** Ensures documents contain extractable text.
   - **What it stops:** Corrupted or empty files.

**Configuration:**

```bash
# Maximum document size in MB (default: 100)
MAX_DOCUMENT_SIZE_MB=100

# Supported file formats (comma‑separated)
SUPPORTED_FILE_FORMATS=pdf,txt,md

# Enable content validation (default: true)
ENABLE_CONTENT_VALIDATION=true
```

**User Experience:**

When a document is rejected:

```
Error: Document Validation Failed

Problem: Your document exceeds the 100 MB size limit

Context: Uploaded file is 250 MB

Why This Matters: Large files consume significant memory during processing. This limit
prevents memory exhaustion attacks and ensures system stability.

What To Do: Please split your document into smaller files (max 100 MB each) and
upload them separately. You can upload multiple documents and search across them together.
```

### PII Detection

**Purpose:** Protect user privacy by identifying sensitive data before processing.

**What Gets Detected:**

The system identifies five types of PII:

1. **Email Addresses** – `user@example.com` format.
2. **Phone Numbers** – `(555) 123‑4567` or `555‑123‑4567` format.
3. **Social Security Numbers** – `123‑45‑6789` format (US).
4. **Credit Card Numbers** – `4532‑1111‑2222‑3333` format.
5. **Passport Numbers** – `AB123456789` format.

**Detection Levels:**

- **strict** – Catches all PII, may have false positives.
- **moderate** (default) – Balanced approach, minimal false positives.
- **lenient** – Only catches obvious PII, fewer false positives.

**Configuration:**

```bash
# Enable/disable PII detection (default: true)
DETECT_PII=true

# Detection sensitivity: strict, moderate, or lenient (default: moderate)
PII_DETECTION_LEVEL=moderate

# Collections allowed to contain PII (semicolon‑separated)
PII_ALLOWED_COLLECTIONS=test_data;training_data

# Action when PII is detected: warn, block, or log (default: warn)
PII_ACTION=warn
```

---

## 2. Data Integrity Validation

### Embedding Cache Validation

**Purpose:** Ensure embeddings are correctly cached and retrievable.

**What Gets Validated:**

1. **Embedding Dimensions** – Validates embedding vector size (1536 for `text‑embedding‑3‑small`).
   - **Why:** Ensures embeddings are compatible with the vector store.
   - **What it stops:** Corrupted embeddings that would break search.

2. **Embedding Completeness** – Verifies all chunks have embeddings.
   - **Why:** Ensures all documents are searchable.
   - **What it stops:** Partial ingestions that leave documents unsearchable.

3. **Cache Consistency** – Checks SQLite cache matches Weaviate index.
   - **Why:** Prevents stale or duplicate embeddings.
   - **What it stops:** Search returning incorrect results.

**Configuration:**

```bash
# Enable embedding cache validation (default: true)
VALIDATE_EMBEDDING_CACHE=true

# Expected embedding dimension (default: 1536)
EMBEDDING_DIMENSION=1536

# Validate cache consistency on startup (default: true)
VALIDATE_CACHE_ON_STARTUP=true
```

### Chunk Integrity Validation

**Purpose:** Ensure document chunks are valid and complete.

**What Gets Validated:**

1. **Chunk Size** – Validates chunks are within acceptable range.
   - **Why:** Ensures chunks fit within LLM context windows.
   - **What it stops:** Oversized chunks that would be truncated.

2. **Chunk Completeness** – Verifies chunks contain complete text.
   - **Why:** Ensures chunks are meaningful and searchable.
   - **What it stops:** Partial chunks from corrupted documents.

3. **Chunk Metadata** – Validates chunk metadata is present and valid.
   - **Why:** Ensures chunks can be traced back to source documents.
   - **What it stops:** Orphaned chunks without source information.

**Configuration:**

```bash
# Minimum chunk size in characters (default: 100)
MIN_CHUNK_SIZE=100

# Maximum chunk size in characters (default: 2000)
MAX_CHUNK_SIZE=2000

# Enable chunk metadata validation (default: true)
VALIDATE_CHUNK_METADATA=true
```

### Collection Consistency Validation

**Purpose:** Ensure collections maintain referential integrity.

**What Gets Validated:**

1. **Document References** – Verifies all documents reference valid collections.
   - **Why:** Prevents orphaned documents.
   - **What it stops:** Data inconsistency from failed operations.

2. **Chunk References** – Verifies all chunks reference valid documents.
   - **Why:** Ensures chunks can be traced to source.
   - **What it stops:** Orphaned chunks from deleted documents.

3. **Metadata Consistency** – Validates collection metadata is valid.
   - **Why:** Ensures collection configuration is correct.
   - **What it stops:** Invalid configurations that break retrieval.

**Configuration:**

```bash
# Enable referential integrity checks (default: true)
VALIDATE_REFERENTIAL_INTEGRITY=true

# Auto‑repair orphaned records (default: false)
AUTO_REPAIR_ORPHANED_RECORDS=false

# Log consistency violations (default: true)
LOG_CONSISTENCY_VIOLATIONS=true
```

---

## 3. Configuration Validation

### Environment Variable Validation

**Purpose:** Ensure all required configuration is present and valid.

**What Gets Validated:**

1. **Required Variables** – Checks all required env vars are set.
   - **Why:** Prevents runtime failures from missing configuration.
   - **What it stops:** Crashes from undefined settings.

2. **Variable Types** – Validates env var values match expected types.
   - **Why:** Ensures configuration is interpreted correctly.
   - **What it stops:** Type errors from invalid configuration.

3. **Variable Ranges** – Validates numeric values are within acceptable ranges.
   - **Why:** Prevents invalid configurations that break system behavior.
   - **What it stops:** Out‑of‑range values that cause unexpected behavior.

**Configuration:**

```bash
# Required environment variables (comma‑separated)
REQUIRED_ENV_VARS=OPENAI_API_KEY,CHROMA_DB_PATH,EMBEDDING_API_BASE

# Validate on startup (default: true)
VALIDATE_CONFIG_ON_STARTUP=true

# Fail on validation error (default: true)
FAIL_ON_CONFIG_ERROR=true
```

### API Configuration Validation

**Purpose:** Ensure API endpoints and credentials are valid.

**What Gets Validated:**

1. **API Endpoints** – Validates API URLs are well‑formed and reachable.
   - **Why:** Ensures external services can be contacted.
   - **What it stops:** Requests to invalid endpoints.

2. **API Credentials** – Validates API keys are present and formatted correctly.
   - **Why:** Ensures authentication will succeed.
   - **What it stops:** Failed API calls from invalid credentials.

3. **API Timeouts** – Validates timeout values are reasonable.
   - **Why:** Prevents hanging requests.
   - **What it stops:** Requests that hang indefinitely.

**Configuration:**

```bash
# Validate API endpoints on startup (default: true)
VALIDATE_API_ENDPOINTS=true

# API request timeout in seconds (default: 30)
API_REQUEST_TIMEOUT=30

# Retry failed API calls (default: true)
RETRY_FAILED_API_CALLS=true

# Maximum API retries (default: 3)
MAX_API_RETRIES=3
```

---

## 4. Health Monitoring

### System Health Checks

**Purpose:** Monitor system status and detect issues early.

**What Gets Monitored:**

1. **Database Connectivity** – Checks SQLite and Weaviate are accessible.
   - **Why:** Ensures core storage is available.
   - **What it detects:** Database connection failures.

2. **API Availability** – Checks external APIs (OpenAI, embedding service) are reachable.
   - **Why:** Ensures external services are available.
   - **What it detects:** API outages or network issues.

3. **Disk Space** – Monitors available disk space.
   - **Why:** Prevents out‑of‑disk errors.
   - **What it detects:** Low disk space conditions.

4. **Memory Usage** – Monitors system memory consumption.
   - **Why:** Prevents memory exhaustion.
   - **What it detects:** Memory leaks or excessive usage.

**Configuration:**

```bash
# Enable health checks (default: true)
ENABLE_HEALTH_CHECKS=true

# Health check interval in seconds (default: 60)
HEALTH_CHECK_INTERVAL=60

# Minimum disk space in GB (default: 1)
MIN_DISK_SPACE_GB=1

# Maximum memory usage in GB (default: 8)
MAX_MEMORY_USAGE_GB=8
```

### Performance Monitoring

**Purpose:** Track system performance and identify bottlenecks.

**What Gets Monitored:**

1. **Query Latency** – Measures time from query submission to answer completion.
   - **Why:** Identifies slow queries and bottlenecks.
   - **What it detects:** Performance regressions.

2. **Retrieval Performance** – Measures time to retrieve relevant chunks.
   - **Why:** Identifies retrieval bottlenecks.
   - **What it detects:** Slow search operations.

3. **Embedding Performance** – Measures time to generate embeddings.
   - **Why:** Identifies embedding service issues.
   - **What it detects:** Slow embedding generation.

4. **API Performance** – Measures time for external API calls.
   - **Why:** Identifies API latency issues.
   - **What it detects:** Slow external services.

**Configuration:**

```bash
# Enable performance monitoring (default: true)
ENABLE_PERFORMANCE_MONITORING=true

# Performance monitoring interval in seconds (default: 60)
PERFORMANCE_MONITORING_INTERVAL=60

# Query latency threshold in seconds (default: 10)
QUERY_LATENCY_THRESHOLD=10

# Alert on slow queries (default: true)
ALERT_ON_SLOW_QUERIES=true
```

---

## 5. Error Recovery

### Validation Error Handling

**Purpose:** Handle validation failures gracefully and provide helpful feedback.

**Error Categories:**

1. **Input Validation Errors** – Query or document validation failures.
   - **Recovery:** Reject input with helpful error message.
   - **Logging:** Log validation failure for analysis.

2. **Data Integrity Errors** – Inconsistencies detected in storage.
   - **Recovery:** Attempt automatic repair or manual intervention.
   - **Logging:** Log integrity violation for investigation.

3. **Configuration Errors** – Invalid environment or API configuration.
   - **Recovery:** Fail fast with clear error message.
   - **Logging:** Log configuration error for debugging.

4. **Health Check Failures** – System health issues detected.
   - **Recovery:** Alert operators and degrade gracefully.
   - **Logging:** Log health check failure for monitoring.

**Configuration:**

```bash
# Error recovery strategy: fail_fast, degrade_gracefully, retry (default: retry)
ERROR_RECOVERY_STRATEGY=retry

# Maximum error recovery attempts (default: 3)
MAX_ERROR_RECOVERY_ATTEMPTS=3

# Log all validation errors (default: true)
LOG_VALIDATION_ERRORS=true

# Alert on critical errors (default: true)
ALERT_ON_CRITICAL_ERRORS=true
```

---

## 6. Audit Logging for Validation

### Validation Event Logging

**Purpose:** Track all validation events for security and compliance.

**What Gets Logged:**

Every validation event is logged with:

- **Timestamp** – When the event occurred (ISO 8601 format).
- **Event Type** – `QUERY_VALIDATION`, `DOCUMENT_VALIDATION`, `CONFIG_VALIDATION`, `HEALTH_CHECK`.
- **Status** – `PASSED`, `FAILED`, `WARNING`.
- **Reason** – Why the validation passed or failed.
- **Input Summary** – First 100 characters of the validated input.
- **Severity** – `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- **Details** – Additional metadata.

**Example log entry:**

```json
{"timestamp":"2026-05-19T04:49:39.876Z","event_type":"QUERY_VALIDATION","status":"PASSED","reason":"Query length within limits","input_summary":"What is machine learning?","severity":"LOW","details":{"query_length":24,"max_length":10000}}
```

**Viewing Validation Logs**

Validation logs are stored in `logs/validation_audit.log` (relative to the project root) in **JSON Lines** format.

Quick examples:

```bash
# Count all validation failures
jq 'select(.status == "FAILED")' logs/validation_audit.log | wc -l

# Find all HIGH severity events
jq 'select(.severity == "HIGH")' logs/validation_audit.log

# Find all document validation failures
jq 'select(.event_type == "DOCUMENT_VALIDATION" and .status == "FAILED")' logs/validation_audit.log

# View validation events from last 24 hours
jq 'select(.timestamp > "2026-05-18T04:49:39Z")' logs/validation_audit.log
```

---

## 7. Best Practices

### For System Administrators

1. **Regular Validation Review** – Check validation logs weekly for patterns.
2. **Monitor Health Checks** – Set up alerts for health‑check failures.
3. **Validate Configuration** – Review environment variables regularly.
4. **Archive Logs** – Archive old validation logs for long‑term compliance.
5. **Test Recovery** – Periodically test error‑recovery procedures.

### For Data Operators

1. **Know Limits** – Be aware of size and length limits.
2. **Pre‑validate Documents** – Validate documents before ingestion.
3. **Watch Ingestion** – Monitor ingestion status for failures.
4. **Review Errors** – Understand validation error messages.
5. **Report Issues** – Notify administrators of validation failures.

### For Developers

1. **Graceful Errors** – Catch validation exceptions and show helpful messages.
2. **Contextual Logging** – Log enough context for investigation.
3. **Leave Validation Enabled** – Validation defaults to safe; keep it enabled.
4. **Performance** – Ensure validation overhead stays < 5 ms per query.
5. **Edge‑Case Testing** – Test validation with boundary values and edge cases.

---

## 8. Validation Checklist

- [ ] Query validation rejects queries over 10,000 characters.
- [ ] Query validation detects injection patterns.
- [ ] Document validation rejects files over 100 MB.
- [ ] Document validation validates file formats.
- [ ] PII detection identifies email addresses.
- [ ] PII detection identifies phone numbers.
- [ ] Embedding cache validation detects missing embeddings.
- [ ] Chunk integrity validation detects oversized chunks.
- [ ] Collection consistency validation detects orphaned documents.
- [ ] Configuration validation checks required environment variables.
- [ ] API configuration validation checks endpoint reachability.
- [ ] Health checks detect database connectivity issues.
- [ ] Health checks detect API availability issues.
- [ ] Performance monitoring tracks query latency.
- [ ] Validation events are logged to audit trail.
- [ ] Error recovery handles failures gracefully.
- [ ] Validation errors provide helpful user feedback.

---

## 9. Related Reading

- [Security Validation Guide](SECURITY_VALIDATION_GUIDE.md) – Security‑focused validation.
- [Audit Log Query Guide](AUDIT_LOG_GUIDE.md) – Query and analyze audit logs.
- [Error Message Reference](ERROR_MESSAGE_REFERENCE.md) – Understand error messages.
- [System Architecture](System%20Architecture.md) – System design and components.

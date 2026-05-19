# Task Breakdown: Advanced Prompt Injection Detection

## Metadata

- **Feature name:** Advanced Prompt Injection Detection
- **Related spec:** spec.md
- **Related plan:** plan.md
- **Related design:** N/A
- **Owner:** Implementation Team
- **Last updated:** 2026-05-19

---

## Phase 1: Pattern Library (Days 1-2)

**Goal:** Expand patterns from 9 to 40+ and enable YAML-based pattern storage

**Completion criteria:**
- [ ] CC-001: `backend/config/injection_patterns.yaml` created with 40+ patterns
- [ ] CC-002: SafetyService loads patterns from YAML at startup
- [ ] CC-003: Unit tests pass for all 7 pattern categories
- [ ] CC-004: Integration test: SQL injection query blocked
- [ ] CC-005: Integration test: Custom pattern in YAML blocks query
- [ ] CC-006: Regression test: Existing 9 patterns work identically

**Tasks:**

- [ ] TASK-001
  Status: Not Started
  Summary: Create YAML config with SQL injection patterns (6 patterns)
  Outcome enabled: SQL injection attacks detected
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/config/injection_patterns.yaml (sql category)
  Affected file(s): backend/config/injection_patterns.yaml (NEW)
  Depends on: None
  Can run in parallel: Yes [P] with TASK-002 to TASK-007
  Proving command: `grep -A 10 "sql:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-002
  Status: Not Started
  Summary: Create YAML config with NoSQL injection patterns (5 patterns)
  Outcome enabled: NoSQL injection attacks detected
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/config/injection_patterns.yaml (nosql category)
  Affected file(s): backend/config/injection_patterns.yaml
  Depends on: None
  Can run in parallel: Yes [P] with TASK-001, TASK-003 to TASK-007
  Proving command: `grep -A 10 "nosql:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-003
  Status: Not Started
  Summary: Create YAML config with LDAP injection patterns (4 patterns)
  Outcome enabled: LDAP injection attacks detected
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/config/injection_patterns.yaml (ldap category)
  Affected file(s): backend/config/injection_patterns.yaml
  Depends on: None
  Can run in parallel: Yes [P] with TASK-001, TASK-002, TASK-004 to TASK-007
  Proving command: `grep -A 10 "ldap:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-004
  Status: Not Started
  Summary: Create YAML config with XSS patterns (6 patterns)
  Outcome enabled: XSS attacks detected
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/config/injection_patterns.yaml (xss category)
  Affected file(s): backend/config/injection_patterns.yaml
  Depends on: None
  Can run in parallel: Yes [P] with TASK-001 to TASK-003, TASK-005 to TASK-007
  Proving command: `grep -A 10 "xss:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-005
  Status: Not Started
  Summary: Create YAML config with command injection patterns (8 patterns)
  Outcome enabled: Command injection attacks detected
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/config/injection_patterns.yaml (command category)
  Affected file(s): backend/config/injection_patterns.yaml
  Depends on: None
  Can run in parallel: Yes [P] with TASK-001 to TASK-004, TASK-006, TASK-007
  Proving command: `grep -A 10 "command:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-006
  Status: Not Started
  Summary: Create YAML config with path traversal patterns (4 patterns)
  Outcome enabled: Path traversal attacks detected
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/config/injection_patterns.yaml (path category)
  Affected file(s): backend/config/injection_patterns.yaml
  Depends on: None
  Can run in parallel: Yes [P] with TASK-001 to TASK-005, TASK-007
  Proving command: `grep -A 10 "path:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-007
  Status: Not Started
  Summary: Create YAML config with code execution patterns (7 patterns)
  Outcome enabled: Code execution attacks detected
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/config/injection_patterns.yaml (code category)
  Affected file(s): backend/config/injection_patterns.yaml
  Depends on: None
  Can run in parallel: Yes [P] with TASK-001 to TASK-006
  Proving command: `grep -A 10 "code:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-008
  Status: Not Started
  Summary: Add existing 9 patterns to YAML config
  Outcome enabled: Backward compatibility with existing patterns
  Plan reference: Phase 1, REQ-007
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: backend/config/injection_patterns.yaml (prompt_override category)
  Affected file(s): backend/config/injection_patterns.yaml
  Depends on: TASK-001 to TASK-007
  Can run in parallel: No
  Proving command: `grep -A 20 "prompt_override:" backend/config/injection_patterns.yaml`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-009
  Status: Not Started
  Summary: Implement `_load_patterns_from_yaml()` in SafetyService
  Outcome enabled: Patterns loaded from YAML at startup
  Plan reference: Phase 1, REQ-002
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Ownership boundary: backend/chat/safety.py (_load_patterns_from_yaml method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-008
  Can run in parallel: No
  Proving command: `python -c "from backend.chat.safety import SafetyService; s = SafetyService(); print(len(s.patterns))"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-010
  Status: Not Started
  Summary: Add YAML validation logic (required fields, valid regex)
  Outcome enabled: Invalid patterns fail gracefully
  Plan reference: Phase 1, REQ-002
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Ownership boundary: backend/chat/safety.py (_validate_pattern method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-009
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_invalid_yaml_fails`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-011
  Status: Not Started
  Summary: Update `_check_heuristics()` to use loaded patterns
  Outcome enabled: All 40+ patterns checked during safety checks
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/chat/safety.py (_check_heuristics method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-010
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_sql_injection_blocked`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-012
  Status: Not Started
  Summary: Write unit tests for SQL injection patterns
  Outcome enabled: SQL injection patterns verified
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: tests/test_safety.py (SQL injection tests)
  Affected file(s): tests/test_safety.py (NEW)
  Depends on: TASK-011
  Can run in parallel: Yes [P] with TASK-013, TASK-014
  Proving command: `python -m pytest tests/test_safety.py::test_sql_injection_patterns -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-013
  Status: Not Started
  Summary: Write unit tests for all other pattern categories (NoSQL, LDAP, XSS, command, path, code)
  Outcome enabled: All pattern categories verified
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: tests/test_safety.py (pattern category tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-011
  Can run in parallel: Yes [P] with TASK-012, TASK-014
  Proving command: `python -m pytest tests/test_safety.py::test_pattern_categories -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-014
  Status: Not Started
  Summary: Run regression tests for existing 9 patterns
  Outcome enabled: Backward compatibility verified
  Plan reference: Phase 1, REQ-007
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: tests/test_safety.py (regression tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-011
  Can run in parallel: Yes [P] with TASK-012, TASK-013
  Proving command: `python -m pytest tests/test_safety.py::test_existing_patterns_unchanged -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

---

## Phase 2: Configuration Modes (Day 2)

**Goal:** Implement strict/moderate/lenient safety modes

**Completion criteria:**
- [ ] CC-007: `safety_mode` field added to SafetySettings
- [ ] CC-008: Environment variable `SAFETY_MODE` loaded correctly
- [ ] CC-009: Threshold mapping implemented (strict=0.5, moderate=0.7, lenient=0.9)
- [ ] CC-010: Unit test: Threshold applied correctly per mode
- [ ] CC-011: Integration test: Same query blocked in strict, allowed in lenient

**Tasks:**

- [ ] TASK-015
  Status: Not Started
  Summary: Add `safety_mode` field to SafetySettings schema
  Outcome enabled: Safety mode configurable
  Plan reference: Phase 2, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: backend/schemas/settings.py (SafetySettings class)
  Affected file(s): backend/schemas/settings.py
  Depends on: TASK-014 (Phase 1 complete)
  Can run in parallel: No
  Proving command: `python -c "from backend.schemas.settings import SafetySettings; print(SafetySettings.model_fields.keys())"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-016
  Status: Not Started
  Summary: Add environment variable loading for `SAFETY_MODE`
  Outcome enabled: Safety mode loaded from environment
  Plan reference: Phase 2, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: backend/config.py (SettingsManager)
  Affected file(s): backend/config.py
  Depends on: TASK-015
  Can run in parallel: No
  Proving command: `SAFETY_MODE=strict python -c "from backend.config import get_config; print(get_config().safety.safety_mode)"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-017
  Status: Not Started
  Summary: Implement threshold mapping logic (strict=0.5, moderate=0.7, lenient=0.9)
  Outcome enabled: Threshold varies by mode
  Plan reference: Phase 2, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: backend/chat/safety.py (_get_threshold_for_mode method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-016
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_threshold_mapping -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-018
  Status: Not Started
  Summary: Update `check_query()` to use mode-based threshold
  Outcome enabled: Query safety checks use mode threshold
  Plan reference: Phase 2, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: backend/chat/safety.py (check_query method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-017
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_mode_affects_query_blocking -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-019
  Status: Not Started
  Summary: Write unit tests for mode configuration
  Outcome enabled: Mode configuration verified
  Plan reference: Phase 2, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: tests/test_safety.py (mode configuration tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-018
  Can run in parallel: Yes [P] with TASK-020
  Proving command: `python -m pytest tests/test_safety.py::test_safety_modes -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-020
  Status: Not Started
  Summary: Write integration test for strict/lenient behavior
  Outcome enabled: Mode behavior verified end-to-end
  Plan reference: Phase 2, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: tests/test_safety.py (integration tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-018
  Can run in parallel: Yes [P] with TASK-019
  Proving command: `python -m pytest tests/test_safety.py::test_strict_blocks_lenient_allows -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

---

## Phase 3: Fuzzy Detection (Day 3)

**Goal:** Implement embedding-based fuzzy detection for obfuscated attacks

**Completion criteria:**
- [ ] CC-012: Embedding corpus created with 50+ examples
- [ ] CC-013: `_check_fuzzy()` method implemented in SafetyService
- [ ] CC-014: Embedding cache implemented (in-memory dict)
- [ ] CC-015: Similarity scoring algorithm correct (cosine similarity)
- [ ] CC-016: Unit test: Similarity scoring works correctly
- [ ] CC-017: Integration test: Typo variant "ignor previous" blocked
- [ ] CC-018: Performance test: Embedding API latency <100ms
- [ ] CC-019: Fallback test: Regex-only works if API fails

**Tasks:**

- [ ] TASK-021
  Status: Not Started
  Summary: Create embedding corpus JSON with 50+ injection examples
  Outcome enabled: Fuzzy detection corpus available
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/config/injection_corpus.json (NEW)
  Affected file(s): backend/config/injection_corpus.json (NEW)
  Depends on: TASK-020 (Phase 2 complete)
  Can run in parallel: No
  Proving command: `python -c "import json; corpus = json.load(open('backend/config/injection_corpus.json')); print(len(corpus['examples']))"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-022
  Status: Not Started
  Summary: Implement embedding generation using OpenAI API
  Outcome enabled: Embeddings generated for queries and corpus
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/chat/safety.py (_generate_embedding method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-021
  Can run in parallel: No
  Proving command: `python -c "from backend.chat.safety import SafetyService; s = SafetyService(); emb = s._generate_embedding('test'); print(len(emb))"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-023
  Status: Not Started
  Summary: Implement embedding cache (dict: example -> embedding)
  Outcome enabled: Embeddings cached to reduce API calls
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/chat/safety.py (_embedding_cache attribute)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-022
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_embedding_cache_hit_rate -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-024
  Status: Not Started
  Summary: Implement cosine similarity scoring function
  Outcome enabled: Similarity between embeddings calculated
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/chat/safety.py (_cosine_similarity method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-023
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_cosine_similarity -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-025
  Status: Not Started
  Summary: Implement `_check_fuzzy()` method in SafetyService
  Outcome enabled: Fuzzy detection checks queries against corpus
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/chat/safety.py (_check_fuzzy method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-024
  Can run in parallel: No
  Proving command: `python -c "from backend.chat.safety import SafetyService; s = SafetyService(); score = s._check_fuzzy('ignor previous'); print(score)"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-026
  Status: Not Started
  Summary: Integrate fuzzy detection into `check_query()`
  Outcome enabled: Query-level fuzzy detection active
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/chat/safety.py (check_query method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-025
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_fuzzy_detection_query_level -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-027
  Status: Not Started
  Summary: Integrate fuzzy detection into `check_chunks()`
  Outcome enabled: Chunk-level fuzzy detection active
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/chat/safety.py (check_chunks method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-026
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_fuzzy_detection_chunk_level -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-028
  Status: Not Started
  Summary: Implement fallback logic (API failure -> regex-only)
  Outcome enabled: System continues working if embedding API fails
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: backend/chat/safety.py (_check_fuzzy method)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-027
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_embedding_api_fallback -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-029
  Status: Not Started
  Summary: Write unit tests for similarity scoring
  Outcome enabled: Similarity algorithm verified
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: tests/test_safety.py (similarity tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-028
  Can run in parallel: Yes [P] with TASK-030, TASK-031, TASK-032
  Proving command: `python -m pytest tests/test_safety.py::test_similarity_scoring -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-030
  Status: Not Started
  Summary: Write integration test for typo variant detection
  Outcome enabled: Fuzzy detection verified end-to-end
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: tests/test_safety.py (integration tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-028
  Can run in parallel: Yes [P] with TASK-029, TASK-031, TASK-032
  Proving command: `python -m pytest tests/test_safety.py::test_typo_variant_blocked -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-031
  Status: Not Started
  Summary: Write performance test for embedding API latency
  Outcome enabled: Embedding API performance verified
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: tests/test_safety.py (performance tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-028
  Can run in parallel: Yes [P] with TASK-029, TASK-030, TASK-032
  Proving command: `python -m pytest tests/test_safety.py::test_embedding_api_latency -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-032
  Status: Not Started
  Summary: Write fallback test for API failure
  Outcome enabled: Fallback behavior verified
  Plan reference: Phase 3, REQ-003
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: tests/test_safety.py (fallback tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-028
  Can run in parallel: Yes [P] with TASK-029, TASK-030, TASK-031
  Proving command: `python -m pytest tests/test_safety.py::test_api_failure_fallback -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

---

## Phase 4: Ingestion Safety (Day 3)

**Goal:** Add synchronous chunk scanning during ingestion

**Completion criteria:**
- [ ] CC-020: Safety check integrated into ingestion pipeline
- [ ] CC-021: Chunks filtered before indexing
- [ ] CC-022: Blocked chunks logged with reason
- [ ] CC-023: Integration test: Malicious document upload blocked
- [ ] CC-024: Performance test: Ingestion overhead <20%
- [ ] CC-025: Log verification: Blocked chunks logged correctly

**Tasks:**

- [ ] TASK-033
  Status: Not Started
  Summary: Add `safety_service.check_chunks()` call in IngestionService
  Outcome enabled: Chunks scanned during ingestion
  Plan reference: Phase 4, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/ingestion/service.py (ingest_document method)
  Affected file(s): backend/ingestion/service.py
  Depends on: TASK-032 (Phase 3 complete)
  Can run in parallel: No
  Proving command: `grep -n "safety_service.check_chunks" backend/ingestion/service.py`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-034
  Status: Not Started
  Summary: Filter chunks with `safety_risk="high"` before indexing
  Outcome enabled: Malicious chunks blocked from indexing
  Plan reference: Phase 4, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/ingestion/service.py (chunk filtering logic)
  Affected file(s): backend/ingestion/service.py
  Depends on: TASK-033
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_ingestion.py::test_malicious_chunks_filtered -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-035
  Status: Not Started
  Summary: Add logging for blocked chunks with reason
  Outcome enabled: Blocked chunks logged for audit
  Plan reference: Phase 4, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/ingestion/service.py (logging logic)
  Affected file(s): backend/ingestion/service.py
  Depends on: TASK-034
  Can run in parallel: No
  Proving command: `grep -A 5 "Blocked.*chunks" logs/ingestion.log`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-036
  Status: Not Started
  Summary: Return count of blocked chunks in ingestion response
  Outcome enabled: User informed of blocked chunks
  Plan reference: Phase 4, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/ingestion/service.py (response format)
  Affected file(s): backend/ingestion/service.py
  Depends on: TASK-035
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_ingestion.py::test_blocked_chunks_count_returned -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-037
  Status: Not Started
  Summary: Write integration test for malicious document blocking
  Outcome enabled: Ingestion safety verified end-to-end
  Plan reference: Phase 4, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: tests/test_ingestion.py (integration tests)
  Affected file(s): tests/test_ingestion.py (NEW)
  Depends on: TASK-036
  Can run in parallel: Yes [P] with TASK-038, TASK-039
  Proving command: `python -m pytest tests/test_ingestion.py::test_malicious_document_blocked -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-038
  Status: Not Started
  Summary: Write performance test for ingestion overhead
  Outcome enabled: Ingestion performance verified (<20% overhead)
  Plan reference: Phase 4, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: tests/test_ingestion.py (performance tests)
  Affected file(s): tests/test_ingestion.py
  Depends on: TASK-036
  Can run in parallel: Yes [P] with TASK-037, TASK-039
  Proving command: `python -m pytest tests/test_ingestion.py::test_ingestion_overhead -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-039
  Status: Not Started
  Summary: Verify logs contain blocked chunk details
  Outcome enabled: Audit trail verified
  Plan reference: Phase 4, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: tests/test_ingestion.py (log verification tests)
  Affected file(s): tests/test_ingestion.py
  Depends on: TASK-036
  Can run in parallel: Yes [P] with TASK-037, TASK-038
  Proving command: `python -m pytest tests/test_ingestion.py::test_blocked_chunks_logged -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

---

## Phase 5: UX & Testing (Day 4)

**Goal:** Update error messages, create adversarial dataset, run comprehensive tests

**Completion criteria:**
- [ ] CC-026: Error message format updated with clear reason
- [ ] CC-027: Adversarial dataset created with 50+ test cases
- [ ] CC-028: All unit tests pass
- [ ] CC-029: All integration tests pass
- [ ] CC-030: All performance tests pass
- [ ] CC-031: All regression tests pass
- [ ] CC-032: False negative rate <5% on adversarial dataset
- [ ] CC-033: False positive rate <2% on adversarial dataset
- [ ] CC-034: Documentation updated (admin guide, pattern categories)

**Tasks:**

- [ ] TASK-040
  Status: Not Started
  Summary: Update error message format in SafetyService
  Outcome enabled: Clear error messages for blocked queries
  Plan reference: Phase 5, REQ-006
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Ownership boundary: backend/chat/safety.py (error message format)
  Affected file(s): backend/chat/safety.py
  Depends on: TASK-039 (Phase 4 complete)
  Can run in parallel: No
  Proving command: `python -m pytest tests/test_safety.py::test_error_message_format -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-041
  Status: Not Started
  Summary: Create adversarial dataset JSON with 50+ test cases
  Outcome enabled: Adversarial evaluation dataset available
  Plan reference: Phase 5, REQ-008
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: tests/adversarial_dataset.json (NEW)
  Affected file(s): tests/adversarial_dataset.json (NEW)
  Depends on: TASK-040
  Can run in parallel: Yes [P] with TASK-042, TASK-043, TASK-044
  Proving command: `python -c "import json; ds = json.load(open('tests/adversarial_dataset.json')); print(len(ds['test_cases']))"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-042
  Status: Not Started
  Summary: Add test cases for all 7 attack categories
  Outcome enabled: All attack categories covered in dataset
  Plan reference: Phase 5, REQ-008
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: tests/adversarial_dataset.json (category coverage)
  Affected file(s): tests/adversarial_dataset.json
  Depends on: TASK-041
  Can run in parallel: Yes [P] with TASK-043, TASK-044
  Proving command: `python -c "import json; ds = json.load(open('tests/adversarial_dataset.json')); cats = set(tc['category'] for tc in ds['test_cases']); print(len(cats))"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-043
  Status: Not Started
  Summary: Add test cases for typo/obfuscation variants
  Outcome enabled: Fuzzy detection coverage in dataset
  Plan reference: Phase 5, REQ-008
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: tests/adversarial_dataset.json (variant coverage)
  Affected file(s): tests/adversarial_dataset.json
  Depends on: TASK-041
  Can run in parallel: Yes [P] with TASK-042, TASK-044
  Proving command: `python -c "import json; ds = json.load(open('tests/adversarial_dataset.json')); variants = [tc for tc in ds['test_cases'] if 'variant' in tc['category']]; print(len(variants))"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-044
  Status: Not Started
  Summary: Add test cases for false positives
  Outcome enabled: False positive coverage in dataset
  Plan reference: Phase 5, REQ-008
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: tests/adversarial_dataset.json (false positive coverage)
  Affected file(s): tests/adversarial_dataset.json
  Depends on: TASK-041
  Can run in parallel: Yes [P] with TASK-042, TASK-043
  Proving command: `python -c "import json; ds = json.load(open('tests/adversarial_dataset.json')); fps = [tc for tc in ds['test_cases'] if tc['expected_blocked'] == False]; print(len(fps))"`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-045
  Status: Not Started
  Summary: Run all unit tests and verify pass
  Outcome enabled: Unit test coverage verified
  Plan reference: Phase 5, REQ-001 to REQ-008
  Linked requirement(s): All REQs
  Linked acceptance criteria: AC-001 to AC-009
  Ownership boundary: tests/test_safety.py (all unit tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-044
  Can run in parallel: Yes [P] with TASK-046, TASK-047, TASK-048
  Proving command: `python -m pytest tests/test_safety.py -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-046
  Status: Not Started
  Summary: Run all integration tests and verify pass
  Outcome enabled: Integration test coverage verified
  Plan reference: Phase 5, REQ-001 to REQ-008
  Linked requirement(s): All REQs
  Linked acceptance criteria: AC-001 to AC-009
  Ownership boundary: tests/ (all integration tests)
  Affected file(s): tests/test_safety.py, tests/test_ingestion.py
  Depends on: TASK-044
  Can run in parallel: Yes [P] with TASK-045, TASK-047, TASK-048
  Proving command: `python -m pytest tests/ -k integration -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-047
  Status: Not Started
  Summary: Run all performance tests and verify pass
  Outcome enabled: Performance requirements verified
  Plan reference: Phase 5, NFR-001
  Linked requirement(s): NFR-001
  Linked acceptance criteria: AC-009
  Ownership boundary: tests/ (all performance tests)
  Affected file(s): tests/test_safety.py, tests/test_ingestion.py
  Depends on: TASK-044
  Can run in parallel: Yes [P] with TASK-045, TASK-046, TASK-048
  Proving command: `python -m pytest tests/ -k performance -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-048
  Status: Not Started
  Summary: Run all regression tests and verify pass
  Outcome enabled: Backward compatibility verified
  Plan reference: Phase 5, REQ-007
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: tests/test_safety.py (regression tests)
  Affected file(s): tests/test_safety.py
  Depends on: TASK-044
  Can run in parallel: Yes [P] with TASK-045, TASK-046, TASK-047
  Proving command: `python -m pytest tests/test_safety.py -k regression -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-049
  Status: Not Started
  Summary: Measure false negative rate on adversarial dataset
  Outcome enabled: False negative rate verified (<5%)
  Plan reference: Phase 5, REQ-008
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: tests/test_adversarial.py (NEW)
  Affected file(s): tests/test_adversarial.py (NEW)
  Depends on: TASK-048
  Can run in parallel: Yes [P] with TASK-050
  Proving command: `python -m pytest tests/test_adversarial.py::test_false_negative_rate -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-050
  Status: Not Started
  Summary: Measure false positive rate on adversarial dataset
  Outcome enabled: False positive rate verified (<2%)
  Plan reference: Phase 5, REQ-008
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: tests/test_adversarial.py
  Affected file(s): tests/test_adversarial.py
  Depends on: TASK-048
  Can run in parallel: Yes [P] with TASK-049
  Proving command: `python -m pytest tests/test_adversarial.py::test_false_positive_rate -v`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-051
  Status: Not Started
  Summary: Create admin guide for pattern management
  Outcome enabled: Admin documentation available
  Plan reference: Phase 5, NFR-005
  Linked requirement(s): NFR-005
  Linked acceptance criteria: AC-009
  Ownership boundary: docs/admin_guide_injection_patterns.md (NEW)
  Affected file(s): docs/admin_guide_injection_patterns.md (NEW)
  Depends on: TASK-050
  Can run in parallel: Yes [P] with TASK-052
  Proving command: `test -f docs/admin_guide_injection_patterns.md && wc -l docs/admin_guide_injection_patterns.md`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

- [ ] TASK-052
  Status: Not Started
  Summary: Document pattern categories with examples
  Outcome enabled: Pattern documentation available
  Plan reference: Phase 5, NFR-005
  Linked requirement(s): NFR-005
  Linked acceptance criteria: AC-009
  Ownership boundary: docs/injection_pattern_categories.md (NEW)
  Affected file(s): docs/injection_pattern_categories.md (NEW)
  Depends on: TASK-050
  Can run in parallel: Yes [P] with TASK-051
  Proving command: `test -f docs/injection_pattern_categories.md && wc -l docs/injection_pattern_categories.md`
  Validation evidence: (to be filled after implementation)
  Session note: (to be filled during implementation)

---

## Completion Notes

- **What was delivered:** (to be filled after implementation)
- **What was deferred:** (to be filled after implementation)
- **What needs follow-up:** (to be filled after implementation)

---

## Resume Notes

- **Current phase:** Phase 1 (Pattern Library)
- **Next recommended task:** TASK-001 (Create YAML config with SQL injection patterns)
- **Active blocker:** None
- **Last validation evidence added:** None
- **Exact next command to run:** `mkdir -p backend/config && touch backend/config/injection_patterns.yaml`

---

**Task Breakdown Complete. Ready for Implementation.**

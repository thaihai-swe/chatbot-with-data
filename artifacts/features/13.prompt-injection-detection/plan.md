# Implementation Plan: Advanced Prompt Injection Detection

## Metadata

- **Feature name:** Advanced Prompt Injection Detection
- **Related spec:** spec.md
- **Related requirements review:** requirements-review.md
- **Related design:** N/A (technical approach defined in spec)
- **Owner:** Implementation Team
- **Status:** Draft
- **Last updated:** 2026-05-19

---

## Plan Summary

Expand prompt injection detection from 9 to 40+ patterns across 7 attack categories, add embedding-based fuzzy detection, secure the ingestion pipeline, and implement configurable safety modes. Implementation follows a 5-phase approach prioritizing pattern expansion first (highest value, lowest risk), then configuration modes, fuzzy detection, ingestion safety, and finally testing/validation.

**Primary technical approach:**
- Store patterns in YAML config file for maintainability
- Load patterns at startup with validation
- Add embedding-based similarity matching (0.70+ threshold) with caching
- Integrate safety checks into ingestion pipeline synchronously
- Preserve existing two-stage architecture and SafetyTrace schema

**Major risks:**
- Fuzzy detection complexity (embedding API dependency, caching strategy)
- Ingestion performance impact (target <20% overhead)
- False positive rate (mitigated by lenient mode and adversarial testing)

**Validation posture:**
- Unit tests for each pattern category
- Integration tests for safety pipeline
- Performance tests for ingestion and query latency
- Adversarial evaluation dataset (50+ test cases)
- Regression tests for existing 9 patterns

**Rollout/rollback stance:**
- Phased rollout: staging first, measure false positive rate
- Feature flag: `SAFETY_MODE` environment variable
- Rollback: Revert to existing 9 patterns by removing YAML config

---

## Execution Context

**Design reference:** N/A (technical approach defined in spec; no separate design needed)

**Relevant repository patterns:**
- Configuration loading: `backend/config.py` SettingsManager pattern
- Safety checks: Two-stage architecture (query + chunk level)
- Pattern matching: Regex-based with case-insensitive matching
- Integration: SafetyService called from ChatService and StreamingOrchestrator

**Brownfield execution constraints:**
- Must preserve existing 9 patterns identically
- Must not modify SafetyTrace schema
- Must not break ChatService/StreamingOrchestrator integration points
- Must maintain LLM classification fallback behavior

**Unchanged behavior that must be preserved:**
- Two-stage safety architecture (query + chunk)
- Query-level: regex + LLM classification
- Chunk-level: regex only (no LLM)
- SafetyTrace metadata format
- Logging of filtered chunks
- Groundedness checks (separate from injection detection)
- Citation validation

---

## First Delivery Slice

**Smallest useful slice:**
- REQ-001: Pattern expansion to 40+ across 7 categories
- REQ-002: YAML/JSON pattern storage and loading

**Why this slice goes first:**
- Highest security value (closes 80% coverage gap)
- Lowest technical risk (straightforward regex expansion)
- Enables custom patterns immediately
- No external dependencies (no embedding API)
- Fast to implement and test

**What proof should exist when this slice is done:**
- 40+ patterns loaded from `backend/config/injection_patterns.yaml`
- All 7 categories tested (SQL, NoSQL, LDAP, XSS, command, path, code)
- Existing 9 patterns still work identically
- Unit tests pass for all pattern categories
- Integration tests show patterns block malicious queries

---

## Technical Approach

**Chosen approach:**
1. **Pattern Storage:** YAML config file with category metadata
2. **Pattern Loading:** Load at startup, validate, merge with existing 9 patterns
3. **Fuzzy Detection:** Embedding-based similarity with cached corpus
4. **Ingestion Safety:** Synchronous chunk scanning before indexing
5. **Configuration:** Threshold-based modes (strict/moderate/lenient)

**Architectural shape:**
```
SafetyService
├─ _load_patterns_from_yaml() -> List[Pattern]
├─ _check_heuristics(text) -> bool (existing, expanded patterns)
├─ _check_fuzzy(text) -> float (NEW: embedding similarity)
├─ check_query(query) -> SafetyTrace (existing, enhanced)
└─ check_chunks(chunks) -> List[Chunk] (existing, enhanced)

IngestionService
└─ ingest_document() -> calls SafetyService.check_chunks()

SafetySettings
└─ safety_mode: str (NEW: strict/moderate/lenient)
```

**Key interfaces:**
- SafetyService API: No changes (internal enhancements only)
- SafetyTrace schema: No changes (backward compatible)
- Pattern format: YAML with category, regex, severity, description

**Operational considerations:**
- Pattern file changes require app restart (hot reload in v1.1)
- Embedding cache stored in memory (Redis in v1.1)
- Ingestion performance monitored via metrics
- False positive rate tracked via logging

---

## Requirements And Constraints

### REQ-001: Pattern Expansion to 40+ Across 7 Categories
**Implementation note:**
- Create `backend/config/injection_patterns.yaml` with 40+ patterns
- Categories: SQL (6), NoSQL (5), LDAP (4), XSS (6), command (8), path (4), code (7)
- All patterns case-insensitive with `(?i)` flag
- Merge with existing 9 patterns (no duplicates)

**Planned validation:**
- Unit test: Each pattern matches expected attack string
- Unit test: Each pattern doesn't match legitimate query
- Integration test: Malicious query blocked at query level
- Integration test: Malicious chunk blocked at chunk level

**Linked scenario:** Scenario 1 (SQL injection detection)

### REQ-002: YAML/JSON Pattern Storage and Loading
**Implementation note:**
- YAML format: category, pattern, regex, severity, description
- Load at SafetyService initialization
- Validate: required fields, valid regex, no catastrophic backtracking
- Merge custom patterns with default patterns

**Planned validation:**
- Unit test: Valid YAML loads successfully
- Unit test: Invalid YAML fails gracefully with clear error
- Integration test: Custom pattern in YAML blocks query

**Linked scenario:** Scenario 5 (custom pattern added)

### REQ-003: Embedding-Based Fuzzy Detection
**Implementation note:**
- Create embedding corpus: 50+ known injection examples
- Generate embeddings using OpenAI API
- Cache embeddings in memory (dict: example -> embedding)
- Similarity scoring: cosine similarity >= 0.70 triggers match
- Fallback: If embedding API fails, continue with regex-only

**Planned validation:**
- Unit test: Similarity scoring algorithm correct
- Unit test: Cache hit rate >95%
- Integration test: Typo variant "ignor previous" blocked
- Performance test: Embedding API latency <100ms

**Linked scenario:** Scenario 2 (fuzzy detection of obfuscated attack)

### REQ-004: Synchronous Chunk Scanning During Ingestion
**Implementation note:**
- Add `safety_service.check_chunks(chunks)` call in `backend/ingestion/service.py`
- Location: After chunking, before indexing
- Filter chunks with `safety_risk="high"`
- Log blocked chunks with reason
- Return count of blocked chunks in response

**Planned validation:**
- Integration test: Malicious document upload blocked
- Performance test: Ingestion overhead <20%
- Log verification: Blocked chunks logged with reason

**Linked scenario:** Scenario 3 (ingestion of malicious document)

### REQ-005: Strict/Moderate/Lenient Mode Configuration
**Implementation note:**
- Add `safety_mode: str` field to SafetySettings
- Environment variable: `SAFETY_MODE=strict|moderate|lenient`
- Threshold mapping: strict=0.5, moderate=0.7, lenient=0.9
- All 40+ patterns checked in all modes (only threshold differs)

**Planned validation:**
- Unit test: Threshold applied correctly per mode
- Integration test: Same query blocked in strict, allowed in lenient
- Configuration test: Environment variable loaded correctly

**Linked scenario:** Scenario 4 (lenient mode false positive)

### REQ-006: False Positive UX - Clear Blocking Reason
**Implementation note:**
- Update error message format in SafetyService
- Include: category, matched pattern or similarity score, contact admin instruction
- Log blocked queries with full details for audit

**Planned validation:**
- Manual test: Blocked query shows clear message
- Log verification: Message logged with query details

**Linked scenario:** Scenario 1 (SQL injection detection)

### REQ-007: Backward Compatibility with Existing 9 Patterns
**Implementation note:**
- Include existing 9 patterns in YAML config
- Verify SafetyTrace output identical for existing patterns
- No changes to SafetyService API
- Regression test suite for existing patterns

**Planned validation:**
- Regression test: Existing 9 patterns work identically
- SafetyTrace comparison: Output unchanged
- API compatibility test: No breaking changes

**Linked scenario:** All existing safety checks

### REQ-008: Adversarial Evaluation Dataset
**Implementation note:**
- Create `tests/adversarial_dataset.json` with 50+ test cases
- Categories: All 7 attack types (6-8 cases each)
- Include: Typo variants, false positives, edge cases
- Format: id, query, category, expected_blocked, reason

**Planned validation:**
- Test execution: All test cases pass
- False negative rate: <5% on dataset
- False positive rate: <2% on dataset

**Linked scenario:** All safety checks

### NFR-001: Performance
**Implementation note:**
- Measure ingestion overhead with 1000-chunk document
- Measure per-query latency with 100-query batch
- Monitor embedding cache hit rate
- Target: <20% ingestion overhead, <50ms query latency

### NFR-002: Reliability
**Implementation note:**
- Validate patterns on load (invalid patterns fail gracefully)
- Fallback to regex-only if embedding API fails
- Catch all exceptions, log errors, no silent failures

### NFR-003: Security
**Implementation note:**
- Validate user-submitted patterns (max length, no injection)
- Audit log all blocked queries with timestamp, user ID, pattern
- No user override capability

### NFR-004: Observability
**Implementation note:**
- Log all blocked queries with reason, matched pattern, similarity score
- Track metrics: false positive/negative rates, pattern hit rates
- Include safety checks in query tracing (Feature #21 integration)

### NFR-005: Maintainability
**Implementation note:**
- YAML config version controlled
- Pattern categories documented
- Admin guide for custom patterns

### NFR-006: Compliance
**Implementation note:**
- Audit trail of blocked queries for regulatory compliance
- Logs retained per compliance policy
- Access control: Only admins can modify patterns

---

## Impacted Areas

**Services or modules:**
- `backend/chat/safety.py` - SafetyService (pattern expansion, fuzzy detection)
- `backend/ingestion/service.py` - IngestionService (add safety check)
- `backend/config.py` - SettingsManager (load YAML patterns)

**APIs or interfaces:**
- SafetyService API: No changes (internal enhancements only)
- SafetyTrace schema: No changes (backward compatible)

**Data model or storage:**
- SafetySettings: Add `safety_mode` field
- Pattern storage: New YAML config file

**UI or UX:**
- Error messages: Update to show clear blocking reason

**Infrastructure or deployment:**
- New config file: `backend/config/injection_patterns.yaml`
- Environment variable: `SAFETY_MODE`

**Documentation:**
- Admin guide: Pattern management and mode configuration
- Pattern categories: Document all 7 categories with examples

---

## Protected Behavior

**Behavior that must not regress:**
1. Existing 9 patterns work identically
2. SafetyTrace schema unchanged
3. Two-stage architecture preserved
4. LLM classification fallback works
5. Chunk-level filtering works
6. Logging of filtered chunks works

**Protection approach:**
- Regression test suite for existing 9 patterns
- SafetyTrace output comparison tests
- Integration tests for ChatService and StreamingOrchestrator
- API compatibility tests

---

## Affected Files

**FILE-001:** `backend/config/injection_patterns.yaml` (NEW)
- **Reason:** Store 40+ patterns with category metadata
- **Change:** Create new YAML config file

**FILE-002:** `backend/chat/safety.py`
- **Reason:** Load patterns from YAML, add fuzzy detection, expand pattern matching
- **Change:** Add `_load_patterns_from_yaml()`, `_check_fuzzy()`, expand `INJECTION_PATTERNS`

**FILE-003:** `backend/schemas/settings.py`
- **Reason:** Add safety_mode configuration
- **Change:** Add `safety_mode: str` field to SafetySettings

**FILE-004:** `backend/ingestion/service.py`
- **Reason:** Add safety check during ingestion
- **Change:** Call `safety_service.check_chunks()` after chunking, before indexing

**FILE-005:** `backend/chat/prompts.py`
- **Reason:** Update error messages for clear blocking reason
- **Change:** Update refusal message format

**FILE-006:** `tests/test_safety.py` (NEW)
- **Reason:** Unit tests for pattern matching and fuzzy detection
- **Change:** Create new test file

**FILE-007:** `tests/adversarial_dataset.json` (NEW)
- **Reason:** Adversarial evaluation dataset
- **Change:** Create new test dataset file

**FILE-008:** `backend/config.py`
- **Reason:** Load YAML patterns at startup
- **Change:** Add pattern loading logic to SettingsManager

---

## Dependencies

**DEP-001:** OpenAI embeddings API
- **Why it matters:** Required for fuzzy detection similarity scoring
- **Mitigation:** Fallback to regex-only if API fails; cache embeddings to reduce calls

**DEP-002:** Existing SafetyService architecture
- **Why it matters:** Must preserve two-stage architecture and SafetyTrace schema
- **Mitigation:** Regression tests ensure no breaking changes

**DEP-003:** Ingestion pipeline
- **Why it matters:** Must integrate safety check without breaking ingestion
- **Mitigation:** Integration tests verify ingestion still works; performance tests measure overhead

**DEP-004:** YAML parsing library
- **Why it matters:** Required to load patterns from config file
- **Mitigation:** Use standard library `pyyaml`; validate YAML on load

---

## Implementation Prerequisites

**PREREQ-001:** Verify OpenAI embeddings API is available and configured
- Check: `OPENAI_API_KEY` environment variable set
- Check: Embeddings API endpoint accessible

**PREREQ-002:** Verify existing 9 patterns work correctly
- Run: Existing safety tests pass
- Check: SafetyTrace output correct for existing patterns

**PREREQ-003:** Create backup of current SafetyService
- Action: Commit current state before changes
- Reason: Enable easy rollback if needed

---

## Execution Phases

### Phase 1: Pattern Library (Days 1-2)

**Goal:** Expand patterns from 9 to 40+ and enable YAML-based pattern storage

**Enabled user scenario(s):**
- US-002: SQL injection detection
- US-005: Admin adds custom pattern

**Entry proof:**
- Existing 9 patterns work correctly
- SafetyService tests pass

**Exit proof:**
- 40+ patterns loaded from YAML
- All 7 categories tested
- Custom patterns loadable without code changes
- Existing 9 patterns still work identically

**Completion criteria:**
- CC-001: `backend/config/injection_patterns.yaml` created with 40+ patterns
- CC-002: SafetyService loads patterns from YAML at startup
- CC-003: Unit tests pass for all 7 pattern categories
- CC-004: Integration test: SQL injection query blocked
- CC-005: Integration test: Custom pattern in YAML blocks query
- CC-006: Regression test: Existing 9 patterns work identically

**Tasks:** (See tasks.md for detailed breakdown)
- TASK-001: Create YAML config with SQL injection patterns (6 patterns)
- TASK-002: Create YAML config with NoSQL injection patterns (5 patterns)
- TASK-003: Create YAML config with LDAP injection patterns (4 patterns)
- TASK-004: Create YAML config with XSS patterns (6 patterns)
- TASK-005: Create YAML config with command injection patterns (8 patterns)
- TASK-006: Create YAML config with path traversal patterns (4 patterns)
- TASK-007: Create YAML config with code execution patterns (7 patterns)
- TASK-008: Add existing 9 patterns to YAML config
- TASK-009: Implement `_load_patterns_from_yaml()` in SafetyService
- TASK-010: Add YAML validation logic
- TASK-011: Update `_check_heuristics()` to use loaded patterns
- TASK-012: Write unit tests for each pattern category
- TASK-013: Write integration test for custom pattern loading
- TASK-014: Run regression tests for existing 9 patterns

### Phase 2: Configuration Modes (Day 2)

**Goal:** Implement strict/moderate/lenient safety modes

**Enabled user scenario(s):**
- US-001: Admin configures safety mode
- US-004: Lenient mode allows legitimate queries

**Entry proof:**
- Phase 1 complete (40+ patterns loaded)

**Exit proof:**
- Safety modes configurable via environment variable
- Threshold applied correctly per mode
- Same query blocked in strict, allowed in lenient

**Completion criteria:**
- CC-007: `safety_mode` field added to SafetySettings
- CC-008: Environment variable `SAFETY_MODE` loaded correctly
- CC-009: Threshold mapping implemented (strict=0.5, moderate=0.7, lenient=0.9)
- CC-010: Unit test: Threshold applied correctly per mode
- CC-011: Integration test: Same query blocked in strict, allowed in lenient

**Tasks:**
- TASK-015: Add `safety_mode` field to SafetySettings schema
- TASK-016: Add environment variable loading for `SAFETY_MODE`
- TASK-017: Implement threshold mapping logic
- TASK-018: Update `check_query()` to use mode-based threshold
- TASK-019: Write unit tests for mode configuration
- TASK-020: Write integration test for strict/lenient behavior


### Phase 3: Fuzzy Detection (Day 3)

**Goal:** Implement embedding-based fuzzy detection for obfuscated attacks

**Enabled user scenario(s):**
- US-004: Typo variant of known attack detected

**Entry proof:**
- Phase 2 complete (modes configurable)
- OpenAI embeddings API accessible

**Exit proof:**
- Fuzzy detection catches typo variants (0.70+ similarity)
- Embedding cache hit rate >95%
- Fallback to regex-only if API fails

**Completion criteria:**
- CC-012: Embedding corpus created with 50+ examples
- CC-013: `_check_fuzzy()` method implemented in SafetyService
- CC-014: Embedding cache implemented (in-memory dict)
- CC-015: Similarity scoring algorithm correct (cosine similarity)
- CC-016: Unit test: Similarity scoring works correctly
- CC-017: Integration test: Typo variant "ignor previous" blocked
- CC-018: Performance test: Embedding API latency <100ms
- CC-019: Fallback test: Regex-only works if API fails

**Tasks:**
- TASK-021: Create embedding corpus JSON with 50+ injection examples
- TASK-022: Implement embedding generation using OpenAI API
- TASK-023: Implement embedding cache (dict: example -> embedding)
- TASK-024: Implement cosine similarity scoring function
- TASK-025: Implement `_check_fuzzy()` method in SafetyService
- TASK-026: Integrate fuzzy detection into `check_query()`
- TASK-027: Integrate fuzzy detection into `check_chunks()`
- TASK-028: Implement fallback logic (API failure -> regex-only)
- TASK-029: Write unit tests for similarity scoring
- TASK-030: Write integration test for typo variant detection
- TASK-031: Write performance test for embedding API latency
- TASK-032: Write fallback test for API failure

### Phase 4: Ingestion Safety (Day 3)

**Goal:** Add synchronous chunk scanning during ingestion

**Enabled user scenario(s):**
- US-003: Malicious document blocked during upload

**Entry proof:**
- Phase 3 complete (fuzzy detection works)
- Ingestion pipeline functional

**Exit proof:**
- Malicious chunks blocked before indexing
- Ingestion overhead <20%
- Blocked chunks logged with reason

**Completion criteria:**
- CC-020: Safety check integrated into ingestion pipeline
- CC-021: Chunks filtered before indexing
- CC-022: Blocked chunks logged with reason
- CC-023: Integration test: Malicious document upload blocked
- CC-024: Performance test: Ingestion overhead <20%
- CC-025: Log verification: Blocked chunks logged correctly

**Tasks:**
- TASK-033: Add `safety_service.check_chunks()` call in IngestionService
- TASK-034: Filter chunks with `safety_risk="high"` before indexing
- TASK-035: Add logging for blocked chunks with reason
- TASK-036: Return count of blocked chunks in ingestion response
- TASK-037: Write integration test for malicious document blocking
- TASK-038: Write performance test for ingestion overhead
- TASK-039: Verify logs contain blocked chunk details

### Phase 5: UX & Testing (Day 4)

**Goal:** Update error messages, create adversarial dataset, run comprehensive tests

**Enabled user scenario(s):**
- US-006: False positive shows clear reason
- All scenarios: Comprehensive testing

**Entry proof:**
- Phase 4 complete (ingestion safety works)

**Exit proof:**
- Clear error messages for blocked queries
- Adversarial dataset created (50+ test cases)
- All tests pass (unit, integration, performance, regression)
- False negative rate <5%, false positive rate <2%

**Completion criteria:**
- CC-026: Error message format updated with clear reason
- CC-027: Adversarial dataset created with 50+ test cases
- CC-028: All unit tests pass
- CC-029: All integration tests pass
- CC-030: All performance tests pass
- CC-031: All regression tests pass
- CC-032: False negative rate <5% on adversarial dataset
- CC-033: False positive rate <2% on adversarial dataset
- CC-034: Documentation updated (admin guide, pattern categories)

**Tasks:**
- TASK-040: Update error message format in SafetyService
- TASK-041: Create adversarial dataset JSON with 50+ test cases
- TASK-042: Add test cases for all 7 attack categories
- TASK-043: Add test cases for typo/obfuscation variants
- TASK-044: Add test cases for false positives
- TASK-045: Run all unit tests and verify pass
- TASK-046: Run all integration tests and verify pass
- TASK-047: Run all performance tests and verify pass
- TASK-048: Run all regression tests and verify pass
- TASK-049: Measure false negative rate on adversarial dataset
- TASK-050: Measure false positive rate on adversarial dataset
- TASK-051: Create admin guide for pattern management
- TASK-052: Document pattern categories with examples

---

## Validation Strategy

**TEST-001: Unit tests**
- Pattern matching: Each pattern matches expected attack, doesn't match legitimate query
- Fuzzy detection: Similarity scoring algorithm correct
- Configuration: Mode thresholds applied correctly
- YAML loading: Valid YAML loads, invalid YAML fails gracefully

**TEST-002: Integration tests**
- Query-level: Malicious query blocked before retrieval
- Chunk-level: Malicious chunk filtered after retrieval
- Ingestion: Malicious document blocked during upload
- Custom patterns: Pattern in YAML blocks query
- Modes: Same query blocked in strict, allowed in lenient

**TEST-003: Performance tests**
- Ingestion overhead: <20% with 1000-chunk document
- Query latency: <50ms impact with 100-query batch
- Embedding API: <100ms latency per call
- Cache hit rate: >95% for embedding cache

**TEST-004: Regression tests**
- Existing 9 patterns: Work identically to current implementation
- SafetyTrace: Output unchanged for existing patterns
- API compatibility: No breaking changes to SafetyService API

**TEST-005: Adversarial evaluation**
- False negative rate: <5% on 50+ test cases
- False positive rate: <2% on 50+ test cases
- Coverage: All 7 attack categories tested
- Variants: Typo/obfuscation variants tested

**TEST-006: Manual verification**
- Error messages: Clear and user-friendly
- Logging: Blocked queries logged with full details
- Configuration: Environment variable loaded correctly

**TEST-007: Observability checks**
- Metrics: False positive/negative rates tracked
- Logs: All blocked queries logged with reason
- Tracing: Safety checks included in query tracing (if Feature #21 implemented)

---

## Traceability Matrix

**Scenario -> Plan phase:**
- Scenario 1 (SQL injection) -> Phase 1 (Pattern Library)
- Scenario 2 (Fuzzy detection) -> Phase 3 (Fuzzy Detection)
- Scenario 3 (Ingestion) -> Phase 4 (Ingestion Safety)
- Scenario 4 (Lenient mode) -> Phase 2 (Configuration Modes)
- Scenario 5 (Custom pattern) -> Phase 1 (Pattern Library)

**REQ -> Plan phase / task IDs:**
- REQ-001 (Pattern expansion) -> Phase 1 / TASK-001 to TASK-008
- REQ-002 (YAML storage) -> Phase 1 / TASK-009 to TASK-011
- REQ-003 (Fuzzy detection) -> Phase 3 / TASK-021 to TASK-032
- REQ-004 (Ingestion safety) -> Phase 4 / TASK-033 to TASK-039
- REQ-005 (Configuration modes) -> Phase 2 / TASK-015 to TASK-020
- REQ-006 (False positive UX) -> Phase 5 / TASK-040
- REQ-007 (Backward compatibility) -> Phase 1, Phase 5 / TASK-014, TASK-048
- REQ-008 (Adversarial dataset) -> Phase 5 / TASK-041 to TASK-044

**AC -> Validation step:**
- AC-001 (40+ patterns) -> TEST-001 (unit tests), TEST-005 (adversarial)
- AC-002 (YAML loading) -> TEST-002 (integration: custom pattern)
- AC-003 (Fuzzy detection) -> TEST-002 (integration: typo variant), TEST-005 (adversarial)
- AC-004 (Ingestion safety) -> TEST-002 (integration: malicious document), TEST-003 (performance)
- AC-005 (Configuration modes) -> TEST-001 (unit: threshold), TEST-002 (integration: strict/lenient)
- AC-006 (False positive UX) -> TEST-004 (manual: error message), TEST-006 (manual: logging)
- AC-007 (Backward compatibility) -> TEST-004 (regression: existing patterns)
- AC-008 (Adversarial dataset) -> TEST-005 (adversarial evaluation)
- AC-009 (Non-functional requirements) -> TEST-003 (performance), TEST-006 (observability)

---

## Rollout Plan

**Release approach:**
- Phased rollout: staging first, then production
- Measure false positive rate on staging for 1 week
- Tune thresholds based on feedback
- Deploy to production with lenient mode default
- Gradually tighten thresholds based on monitoring

**Feature flags:**
- `SAFETY_MODE` environment variable (strict/moderate/lenient)
- Default: moderate (threshold 0.7)
- Can be changed per deployment without code changes

**Migration needs:**
- None (backward compatible)
- Existing 9 patterns continue to work
- SafetyTrace schema unchanged

**Backward compatibility notes:**
- Existing 9 patterns included in YAML config
- SafetyService API unchanged (internal enhancements only)
- SafetyTrace schema unchanged
- Integration points unchanged (ChatService, StreamingOrchestrator)
- LLM classification fallback preserved

---

## Rollback Plan

**How to revert safely:**

1. **Immediate rollback (if critical issue):**
   - Remove or rename `backend/config/injection_patterns.yaml`
   - Restart application
   - System reverts to existing 9 hardcoded patterns
   - No data loss, no schema changes

2. **Partial rollback (disable fuzzy detection only):**
   - Comment out `_check_fuzzy()` call in SafetyService
   - Restart application
   - Regex patterns still work, fuzzy detection disabled

3. **Rollback ingestion safety (if performance issue):**
   - Comment out `safety_service.check_chunks()` call in IngestionService
   - Restart application
   - Query-level safety still works, ingestion safety disabled

4. **Rollback configuration modes:**
   - Set `SAFETY_MODE=moderate` (default)
   - Restart application
   - System uses default threshold (0.7)

**Rollback verification:**
- Run regression tests to verify existing 9 patterns work
- Check SafetyTrace output matches pre-deployment
- Verify no errors in logs

---

## Risks And Mitigations

**RISK-001: False positive rate too high**
- **Risk:** Legitimate queries blocked, users frustrated, support burden increases
- **Mitigation:**
  - Deploy with lenient mode (0.9 threshold) initially
  - Measure false positive rate on staging for 1 week
  - Create adversarial dataset with false positive test cases
  - Provide clear error messages to guide users to admin
  - Establish feedback mechanism to identify and fix false positives

**RISK-002: Ingestion performance degradation**
- **Risk:** Synchronous chunk scanning slows ingestion >20%, users complain
- **Mitigation:**
  - Performance testing before release (target <20% overhead)
  - Monitor ingestion latency in production
  - Async scanning option in v1.1 if needed
  - Cache pattern matches to reduce redundant checks
  - Optimize regex patterns for performance

**RISK-003: Pattern maintenance burden**
- **Risk:** 40+ patterns become outdated, new attacks bypass detection
- **Mitigation:**
  - Version control patterns in YAML (git history)
  - Document pattern categories and examples
  - Establish process for updating patterns (monthly/quarterly)
  - Monitor security advisories for new attack patterns
  - Assign owner for pattern maintenance (Security Team)

**RISK-004: Embedding API dependency**
- **Risk:** OpenAI embeddings API fails, fuzzy detection unavailable
- **Mitigation:**
  - Fallback to regex-only detection if API fails
  - Cache embeddings to reduce API calls (target >95% hit rate)
  - Monitor API availability and latency
  - Plan for alternative embedding provider in v1.1 (local models)

**RISK-005: Pattern injection via custom patterns**
- **Risk:** Admin adds malicious regex pattern that breaks system
- **Mitigation:**
  - Validate all patterns before loading (required fields, valid regex)
  - Test patterns against safe queries before deployment
  - Limit pattern complexity (max length, no catastrophic backtracking)
  - Require admin review before custom patterns go live
  - Log all pattern changes for audit trail

**RISK-006: Fuzzy detection complexity**
- **Risk:** Embedding-based similarity matching is complex, may have bugs
- **Mitigation:**
  - Comprehensive unit tests for similarity scoring
  - Integration tests for typo variant detection
  - Adversarial dataset to measure effectiveness
  - Fallback to regex-only if fuzzy detection fails
  - Monitor fuzzy detection hit rate and accuracy

---

## Open Questions

**Q-001: Should fuzzy detection be enabled by default or opt-in?**
- **Type:** Non-blocking
- **Owner:** Product
- **Next step:** Decide based on false positive rate measurement on staging
- **Current plan:** Enable by default, monitor false positive rate

**Q-002: How often should the injection example corpus be updated?**
- **Type:** Non-blocking
- **Owner:** Security Team
- **Next step:** Establish update cadence (monthly? quarterly?)
- **Current plan:** Quarterly updates, ad-hoc for critical new attacks

**Q-003: Should pattern updates trigger automatic re-scanning of existing chunks?**
- **Type:** Non-blocking
- **Owner:** Product
- **Next step:** Defer to v1.1 (out of scope for v1.0)
- **Current plan:** No re-scanning in v1.0, manual re-ingestion if needed

**Q-004: What's the maximum number of custom patterns an admin can add?**
- **Type:** Non-blocking
- **Owner:** Product
- **Next step:** No limit for v1.0, revisit if performance issues arise
- **Current plan:** No hard limit, monitor performance

---

**Plan Status:** Ready for Task Breakdown  
**Next Step:** Create tasks.md with detailed 2-5 minute task breakdown

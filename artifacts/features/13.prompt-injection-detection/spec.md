# Feature Specification: Advanced Prompt Injection Detection

## Metadata

- **Feature name:** Advanced Prompt Injection Detection
- **Feature slug:** 13.prompt-injection-detection
- **Owner:** Security Team
- **Status:** Draft → In Review (awaiting approval)
- **Last updated:** 2026-05-19
- **Related artifacts:** analysis.md, proposal.md, PRODUCT_ROADMAP.md (Feature #7.7.1)

---

## Problem Statement

The system currently detects only 9 basic prompt injection patterns, leaving 80% of documented attack vectors undetected. This creates three critical vulnerabilities:

1. **Query-level attacks:** SQL, NoSQL, LDAP, XSS, command injection, and code execution attempts bypass detection
2. **Ingestion-level attacks:** Malicious documents are indexed without safety checks, poisoning the knowledge base
3. **Obfuscated attacks:** Typo variations and spacing obfuscation bypass exact regex matching

**For whom:** System administrators, security teams, and end users who depend on the system to reject malicious inputs.

**Why now:** System is approaching production deployment. Current detection gaps create unacceptable security risk for enterprise use cases.

---

## Desired Outcomes

1. **Comprehensive pattern coverage:** Detect 40+ injection attack patterns across 7 categories (SQL, NoSQL, LDAP, XSS, command, path, code)
2. **Fuzzy attack detection:** Catch obfuscated and typo-variant attacks via embedding-based similarity matching
3. **Secure ingestion:** Block malicious documents at upload time, preventing knowledge base poisoning
4. **Configurable safety:** Support strict/moderate/lenient modes for different risk tolerances
5. **Maintainability:** Update patterns without code changes; support custom patterns per deployment
6. **Backward compatibility:** Existing 9 patterns work identically; no breaking changes to SafetyTrace or integration points

---

## Minimum Release Slice

**What ships in v1.0:**
- 40+ regex patterns across 7 categories (hardcoded + YAML config)
- Embedding-based fuzzy detection (0.70+ similarity threshold)
- Synchronous chunk scanning during ingestion
- Strict/moderate/lenient modes (threshold-based configuration)
- Adversarial evaluation dataset (50+ test cases)
- Full backward compatibility with existing 9 patterns

**What can wait (v1.1+):**
- Dynamic pattern updates from threat feeds
- Per-collection safety policies
- Admin UI for pattern management
- Real-time false positive feedback loop
- Integration with external security databases

---

## Success Criteria

- **SC-001:** All 40+ patterns implemented and tested; false negative rate <5% on adversarial dataset
- **SC-002:** Fuzzy detection catches 80%+ of typo/obfuscation variants in test dataset
- **SC-003:** Ingestion overhead <20%; per-query latency impact <50ms
- **SC-004:** Strict/moderate/lenient modes configurable and functional
- **SC-005:** Patterns loadable from YAML without code changes
- **SC-006:** Existing 9 patterns work identically; SafetyTrace schema unchanged
- **SC-007:** All blocked queries logged with clear reason for audit trail
- **SC-008:** Zero breaking changes to ChatService, StreamingOrchestrator, or SafetyService API

---

## In Scope

- Expand regex patterns to 40+ across 7 categories (SQL, NoSQL, LDAP, XSS, command, path, code)
- Implement embedding-based fuzzy detection with 0.70+ similarity threshold
- Add synchronous chunk scanning during ingestion pipeline
- Implement strict (0.5) / moderate (0.7) / lenient (0.9) modes via threshold configuration
- Store patterns in YAML/JSON config file (`backend/config/injection_patterns.yaml`)
- Support user-submitted custom patterns (stored in config)
- Create adversarial evaluation dataset with 50+ test cases
- Maintain backward compatibility with existing 9 patterns
- Update SafetySettings to expose mode configuration
- Add logging for all blocked queries with reason

---

## Out Of Scope

- Dynamic pattern updates from external threat feeds (future enhancement)
- Per-collection safety policies (future enhancement)
- Admin UI for pattern management (future enhancement)
- Real-time false positive feedback loop (future enhancement)
- Integration with external security databases (future enhancement)
- Changes to LLM classification prompt or logic
- Changes to two-stage safety architecture
- Changes to SafetyTrace schema or format

---

## Non-Goals

- Replace LLM classification with pattern-only detection
- Modify chunk-level detection to use LLM classification (keep regex-only for performance)
- Add user override capability for blocked queries
- Implement automatic pattern learning from blocked queries
- Support per-query pattern configuration

---

## Users And Stakeholders

**Primary users:**
- **System administrators:** Configure safety modes, add custom patterns, review blocked queries
- **Security teams:** Audit injection attempts, validate pattern effectiveness, update threat corpus
- **End users:** Submit queries, receive clear feedback when blocked

**Secondary stakeholders:**
- **DevOps:** Monitor ingestion performance impact
- **Compliance:** Audit trail of blocked queries for regulatory requirements
- **Product:** Measure false positive rates, gather user feedback

---

## User Stories And Key Scenarios

### US-001: Admin Configures Safety Mode
**As a** system administrator  
**I want to** set the safety mode to strict/moderate/lenient  
**So that** I can balance security vs. usability for my deployment

### US-002: User Submits Query with SQL Injection
**As a** user  
**I want to** submit a query like "'; DROP TABLE users; --"  
**So that** I can test the system  
**But** the system should block it with a clear reason

### US-003: Malicious Document Uploaded
**As a** document uploader  
**I want to** upload a document containing injection patterns  
**So that** I can test ingestion safety  
**But** the system should block malicious chunks before indexing

### US-004: Typo Variant of Known Attack
**As a** attacker  
**I want to** submit "ignor previous instructions" (typo)  
**So that** I can bypass exact regex matching  
**But** fuzzy detection should catch it

### US-005: Admin Adds Custom Pattern
**As a** system administrator  
**I want to** add a custom injection pattern to the YAML config  
**So that** I can protect against domain-specific attacks  
**And** the pattern should be loaded without code changes

### US-006: False Positive Blocked Query
**As a** user  
**I want to** submit a legitimate query that gets blocked  
**So that** I can understand why  
**And** I can contact admin to whitelist the pattern

---

## Detailed Scenarios

### Scenario 1: SQL Injection Detection (Happy Path)
**Given:** System is running with moderate safety mode (threshold 0.7)  
**When:** User submits query "SELECT * FROM users WHERE id = 1 OR 1=1"  
**Then:**
- Query matches SQL injection pattern `' OR '1'='1`
- SafetyService.check_query() returns injection_risk="high"
- Query is rejected before retrieval
- User sees: "Query blocked: SQL injection pattern detected. Contact admin if this is a false positive."
- Blocked query logged with timestamp, user ID, query text, matched pattern

### Scenario 2: Fuzzy Detection of Obfuscated Attack (Edge Case)
**Given:** System has fuzzy detection enabled with 0.70+ similarity threshold  
**When:** User submits "i g n o r e previous instructions" (spaced out)  
**Then:**
- Regex patterns don't match (exact match fails)
- Embedding-based fuzzy detection compares against corpus
- Similarity score 0.75 > 0.70 threshold
- Query blocked as high injection risk
- User sees clear reason

### Scenario 3: Ingestion of Malicious Document (Error State)
**Given:** Admin uploads document containing "eval(user_input)"  
**When:** Ingestion pipeline processes chunks  
**Then:**
- SafetyService.check_chunks() called synchronously
- Chunk matches code execution pattern `eval\(`
- Chunk marked as safety_risk="high"
- Chunk blocked before indexing
- Ingestion completes with warning: "1 malicious chunk blocked"
- Blocked chunk logged for audit

### Scenario 4: Lenient Mode False Positive (Configuration)
**Given:** System configured with lenient mode (threshold 0.9)  
**When:** User submits legitimate query "How do I execute a shell script?"  
**Then:**
- Query matches command injection pattern `execute.*shell`
- Risk score 0.65 < 0.9 threshold
- Query allowed to proceed
- No false positive in strict mode (threshold 0.5)

### Scenario 5: Custom Pattern Added (Maintenance)
**Given:** Admin adds custom pattern to `backend/config/injection_patterns.yaml`  
**When:** System restarts or pattern file is reloaded  
**Then:**
- Custom pattern loaded without code changes
- Pattern applied to all subsequent queries and ingestions
- Existing 9 patterns continue to work
- No SafetyService code modified

---

## Current Context (Brownfield)

**Existing behavior to preserve:**
1. Two-stage safety architecture (query-level + chunk-level)
2. Query-level uses regex + LLM classification
3. Chunk-level uses regex only (no LLM)
4. SafetyTrace metadata format and schema
5. Integration points: ChatService.process_turn() and StreamingOrchestrator.stream_turn()
6. LLM classification fallback behavior
7. Existing 9 patterns work identically
8. Logging of filtered chunks

**Impacted boundaries:**
- SafetyService class (add new methods, expand patterns)
- SafetySettings schema (add mode configuration)
- Ingestion pipeline (add safety check call)
- Configuration loading (add YAML pattern loading)

**Unchanged behavior:**
- Groundedness checks (separate from injection detection)
- Citation validation
- Answer generation logic
- Retrieval pipeline (except chunk filtering)

---

## Dependencies And External Touchpoints

- **DEP-001:** OpenAI embeddings API (for fuzzy detection similarity scoring)
- **DEP-002:** YAML/JSON config file loading (backend/config/injection_patterns.yaml)
- **DEP-003:** Existing SafetyService architecture (must preserve)
- **DEP-004:** ChatService and StreamingOrchestrator integration points (must not break)
- **DEP-005:** SafetyTrace schema (must remain compatible)
- **DEP-006:** Ingestion pipeline (must add safety check call)

---

## Functional Requirements

### REQ-001: Pattern Expansion to 40+ Across 7 Categories

**Requirement:**
Implement 40+ regex patterns covering 7 attack categories:
1. **SQL Injection (6 patterns):** `' OR '1'='1`, `UNION SELECT`, `DROP TABLE`, `INSERT INTO`, `UPDATE SET`, `DELETE FROM`
2. **NoSQL Injection (5 patterns):** `$ne`, `$gt`, `$lt`, `$where`, `{"$regex": ".*"}`
3. **LDAP Injection (4 patterns):** `*)(uid=*)`, `admin*`, `*))(&`, `*)(|(uid=*`
4. **XSS Patterns (6 patterns):** `<script>`, `javascript:`, `onerror=`, `onload=`, `<iframe>`, `<img src=`
5. **Command Injection (8 patterns):** `; rm -rf`, `| cat`, `$(whoami)`, `` `whoami` ``, `&& rm`, `|| cat`, `> /dev/null`, `< /etc/passwd`
6. **Path Traversal (4 patterns):** `../../../etc/passwd`, `..\\..\\..\\windows`, `%2e%2e%2f`, `....//....//`
7. **Code Execution (7 patterns):** `eval(`, `exec(`, `__import__`, `subprocess.call`, `os.system`, `pickle.loads`, `compile(`

**Why it matters:**
- Closes 80% coverage gap identified in analysis
- Protects against sophisticated attacks beyond basic prompt override
- Aligns with OWASP injection attack categories

**Impacted users or scenarios:**
- US-002 (SQL injection detection)
- US-003 (malicious document blocking)
- US-004 (obfuscated attack detection)

**Related success criteria:**
- SC-001 (40+ patterns implemented, <5% false negative rate)

**Priority:** Must Have

**Acceptance notes:**
- All 40+ patterns must be case-insensitive
- Patterns must be tested against adversarial dataset
- False negative rate must be <5% on test dataset
- No false positives on legitimate queries (baseline: existing 9 patterns)

**Validation surface:**
- Unit tests for each pattern category
- Adversarial evaluation dataset (50+ test cases)
- False positive/negative rate measurement

---

### REQ-002: YAML/JSON Pattern Storage and Loading

**Requirement:**
Store all 40+ patterns in `backend/config/injection_patterns.yaml` with category metadata. Load patterns at startup and support hot reload without code changes.

**Format:**
```yaml
injection_patterns:
  sql:
    - pattern: "' OR '1'='1"
      regex: "(?i)('\\s+OR\\s+'1'\\s*=\\s*'1)"
      severity: high
      description: "SQL OR-based injection"
  noSQL:
    - pattern: "$ne"
      regex: "(?i)\\$ne"
      severity: high
      description: "NoSQL $ne operator"
  # ... more patterns
  custom:
    - pattern: "domain-specific-attack"
      regex: "(?i)domain.*specific.*attack"
      severity: medium
      description: "Custom pattern for this deployment"
```

**Why it matters:**
- Enables pattern updates without code changes
- Supports custom patterns per deployment
- Centralizes pattern maintenance
- Allows version control of patterns

**Impacted users or scenarios:**
- US-005 (admin adds custom pattern)

**Related success criteria:**
- SC-005 (patterns loadable from YAML)

**Priority:** Must Have

**Acceptance notes:**
- YAML file must be validated on load
- Invalid patterns must fail gracefully with clear error
- Patterns must be reloadable without restart (optional for v1.0)
- Custom patterns must be mergeable with default patterns

**Validation surface:**
- Config file parsing tests
- Pattern validation tests
- Integration test: custom pattern blocks query

---

### REQ-003: Embedding-Based Fuzzy Detection

**Requirement:**
Implement embedding-based similarity matching against a corpus of known injection examples. Match queries/chunks with 0.70+ similarity to any corpus example.

**Corpus:**
- Predefined: ~50 known injection examples across all 7 categories
- User-submitted: Admins can add custom examples to YAML
- Format: List of injection example strings with category tags

**Algorithm:**
1. Generate embedding for user query/chunk using OpenAI embeddings API
2. Compare against all corpus embeddings (cached)
3. If max similarity >= 0.70, flag as high injection risk
4. Log matched corpus example for audit

**Why it matters:**
- Catches obfuscated and typo-variant attacks
- Handles novel attack patterns not in regex library
- Complements regex-based detection

**Impacted users or scenarios:**
- US-004 (typo variant detection)

**Related success criteria:**
- SC-002 (fuzzy detection catches 80%+ of variants)

**Priority:** Must Have

**Acceptance notes:**
- Similarity threshold must be 0.70 (configurable in future)
- Corpus must include at least 50 examples
- Embeddings must be cached to avoid API calls on every query
- Fallback: If embedding API fails, continue with regex-only detection

**Validation surface:**
- Unit tests for similarity scoring
- Adversarial dataset with typo/obfuscation variants
- Performance test: embedding cache hit rate >95%

---

### REQ-004: Synchronous Chunk Scanning During Ingestion

**Requirement:**
Call SafetyService.check_chunks() synchronously during ingestion pipeline. Block malicious chunks before indexing.

**Integration point:**
- Location: `backend/ingestion/service.py` (after chunking, before indexing)
- Call: `safety_service.check_chunks(chunks)` returns filtered chunks
- Behavior: Chunks with safety_risk="high" removed before indexing

**Why it matters:**
- Prevents malicious documents from poisoning knowledge base
- Ensures all indexed chunks are safe
- Provides immediate feedback to uploader

**Impacted users or scenarios:**
- US-003 (malicious document blocking)

**Related success criteria:**
- SC-003 (ingestion overhead <20%)

**Priority:** Must Have

**Acceptance notes:**
- Ingestion overhead must be <20% (measured on 1000-chunk document)
- Blocked chunks must be logged with reason
- Ingestion must complete successfully even if some chunks blocked
- User must see count of blocked chunks in response

**Validation surface:**
- Performance test: ingestion time with/without safety checks
- Integration test: malicious document upload blocked
- Log verification: blocked chunks logged with reason

---

### REQ-005: Strict/Moderate/Lenient Mode Configuration

**Requirement:**
Implement three safety modes via threshold configuration in SafetySettings:
- **Strict:** injection_risk_threshold = 0.5 (aggressive filtering)
- **Moderate:** injection_risk_threshold = 0.7 (current behavior)
- **Lenient:** injection_risk_threshold = 0.9 (fewer false positives)

**Configuration:**
- Environment variable: `SAFETY_MODE=strict|moderate|lenient`
- SafetySettings field: `safety_mode: str`
- Behavior: All 40+ patterns checked in all modes; only threshold differs

**Why it matters:**
- Allows different risk tolerances for different deployments
- Strict mode for high-security environments
- Lenient mode for user-friendly environments

**Impacted users or scenarios:**
- US-001 (admin configures safety mode)
- US-004 (lenient mode allows legitimate queries)

**Related success criteria:**
- SC-004 (modes configurable and functional)

**Priority:** Must Have

**Acceptance notes:**
- Mode must be configurable via environment variable
- Mode must be persisted in SafetySettings
- All 40+ patterns must be checked in all modes
- Only threshold changes between modes

**Validation surface:**
- Unit test: threshold applied correctly per mode
- Integration test: same query blocked in strict, allowed in lenient
- Configuration test: environment variable loaded correctly

---

### REQ-006: False Positive UX - Clear Blocking Reason

**Requirement:**
When a query is blocked, return clear error message explaining why:
- Pattern category (SQL injection, XSS, etc.)
- Matched pattern or similarity score
- Instruction to contact admin for whitelist

**Message format:**
```
Query blocked: [Category] injection pattern detected.
Matched: [Pattern or "Fuzzy match (0.75 similarity)"]
Contact admin if this is a false positive.
```

**Why it matters:**
- Users understand why they're blocked
- Reduces support burden (users know to contact admin)
- Enables audit trail of false positives

**Impacted users or scenarios:**
- US-006 (false positive blocked query)

**Related success criteria:**
- SC-007 (all blocked queries logged with clear reason)

**Priority:** Must Have

**Acceptance notes:**
- Message must be user-friendly and non-technical
- Message must include category and matched pattern
- Message must be logged for audit trail
- No user override capability (by design)

**Validation surface:**
- Manual test: blocked query shows clear message
- Log verification: message logged with query details

---

### REQ-007: Backward Compatibility with Existing 9 Patterns

**Requirement:**
Existing 9 patterns must work identically:
1. `ignore\s+previous\s+instructions`
2. `disregard\s+all\s+previous`
3. `reveal\s+your\s+system\s+prompt`
4. `system\s+instructions`
5. `you\s+are\s+now\s+a`
6. `new\s+rule:`
7. `instead\s+of\s+answering`
8. `do\s+not\s+cite\s+sources`
9. `disable\s+citations`

**Behavior:**
- Patterns must be checked at both query and chunk level
- Risk scoring must be identical to current implementation
- SafetyTrace schema must not change
- Integration points must not change

**Why it matters:**
- Ensures no regression in existing detection
- Maintains API compatibility
- Allows gradual rollout

**Impacted users or scenarios:**
- All existing safety checks

**Related success criteria:**
- SC-006 (existing patterns work identically)
- SC-008 (zero breaking changes)

**Priority:** Must Have

**Acceptance notes:**
- All 9 patterns must be included in YAML config
- Patterns must be tested against existing test cases
- SafetyTrace output must be identical for existing patterns
- No changes to SafetyService API

**Validation surface:**
- Regression test: existing 9 patterns work identically
- SafetyTrace comparison: output unchanged for existing patterns
- API compatibility test: no breaking changes

---

### REQ-008: Adversarial Evaluation Dataset

**Requirement:**
Create adversarial evaluation dataset with 50+ test cases covering:
- All 7 attack categories (6-8 cases each)
- Typo/obfuscation variants (10+ cases)
- False positives (legitimate queries that might be blocked)
- Edge cases (boundary conditions, mixed attacks)

**Format:**
```json
{
  "test_cases": [
    {
      "id": "sql_001",
      "query": "SELECT * FROM users WHERE id = 1 OR 1=1",
      "category": "sql_injection",
      "expected_blocked": true,
      "reason": "SQL OR-based injection"
    },
    {
      "id": "fp_001",
      "query": "How do I execute a shell script?",
      "category": "false_positive",
      "expected_blocked": false,
      "reason": "Legitimate question about shell scripts"
    }
  ]
}
```

**Why it matters:**
- Measures detection effectiveness
- Identifies false positives/negatives
- Enables regression testing
- Supports continuous improvement

**Impacted users or scenarios:**
- All safety checks

**Related success criteria:**
- SC-001 (false negative rate <5%)

**Priority:** Must Have

**Acceptance notes:**
- Dataset must have 50+ test cases
- Must cover all 7 categories
- Must include false positive cases
- Must be version controlled
- Must be updated as new attacks emerge

**Validation surface:**
- Test execution: all test cases pass
- False negative rate: <5% on dataset
- False positive rate: <2% on dataset

---

## Non-Functional Requirements

### NFR-001: Performance
- **Ingestion overhead:** <20% (measured on 1000-chunk document)
- **Per-query latency impact:** <50ms (measured on 100-query batch)
- **Embedding cache hit rate:** >95% (avoid redundant API calls)
- **Pattern matching latency:** <10ms per query (40+ patterns)

### NFR-002: Reliability
- **Pattern validation:** Invalid patterns fail gracefully with clear error
- **LLM fallback:** If embedding API fails, continue with regex-only detection
- **Config reload:** Pattern file changes detected and reloaded without restart (optional v1.1)
- **Error handling:** All exceptions caught and logged; no silent failures

### NFR-003: Security
- **Pattern validation:** No pattern injection attacks possible
- **Corpus validation:** User-submitted patterns validated before use
- **Audit logging:** All blocked queries logged with timestamp, user ID, pattern matched
- **No bypass:** No user override capability for blocked queries

### NFR-004: Observability
- **Logging:** All blocked queries logged with reason, matched pattern, similarity score
- **Metrics:** Track false positive/negative rates, pattern hit rates
- **Tracing:** Safety checks included in query tracing (Feature #21)
- **Debugging:** Clear error messages for configuration issues

### NFR-005: Maintainability
- **Pattern storage:** YAML/JSON config file, version controlled
- **Custom patterns:** Admins can add patterns without code changes
- **Documentation:** Pattern categories documented, examples provided
- **Testing:** Unit tests for each pattern category, integration tests for pipeline

### NFR-006: Compliance
- **Audit trail:** All blocked queries logged for regulatory compliance
- **Data retention:** Logs retained per compliance policy
- **Access control:** Only admins can view/modify patterns
- **Transparency:** Users informed why queries are blocked

---

## Constraints

**Technical constraints:**
- Must use existing OpenAI embeddings API (no new dependencies)
- Must preserve two-stage safety architecture
- Must not modify SafetyTrace schema
- Must not break existing integration points

**Business constraints:**
- Implementation must fit in 2-3 days (per PRODUCT_ROADMAP.md)
- No new external dependencies allowed
- Must support existing deployments without migration

**Delivery constraints:**
- Must be backward compatible (no breaking changes)
- Must include test coverage (>80%)
- Must include documentation for admins

---

## Assumptions

- **ASM-001:** OpenAI embeddings API will remain available and performant
- **ASM-002:** 40+ patterns are sufficient for production security (can be expanded later)
- **ASM-003:** 0.70 similarity threshold is appropriate for fuzzy detection (can be tuned)
- **ASM-004:** Ingestion overhead <20% is acceptable for security guarantee
- **ASM-005:** Admins will maintain pattern corpus as new attacks emerge
- **ASM-006:** Users will contact admin for false positive whitelisting (no self-service override)

---

## Risks

### RISK-001: False Positive Rate Too High
**Risk:** Legitimate queries blocked, users frustrated, support burden increases  
**Mitigation:**
- Lenient mode (0.9 threshold) for user-friendly deployments
- Adversarial dataset to measure false positive rate
- Clear error messages to guide users to admin
- Feedback mechanism to identify and fix false positives

### RISK-002: Ingestion Performance Degradation
**Risk:** Synchronous chunk scanning slows ingestion >20%, users complain  
**Mitigation:**
- Performance testing before release
- Async scanning option in v1.1 if needed
- Caching of pattern matches to reduce redundant checks
- Monitoring of ingestion latency in production

### RISK-003: Pattern Maintenance Burden
**Risk:** 40+ patterns become outdated, new attacks bypass detection  
**Mitigation:**
- Version control patterns in YAML
- Document pattern categories and examples
- Establish process for updating patterns
- Monitor security advisories for new attack patterns

### RISK-004: Embedding API Dependency
**Risk:** OpenAI embeddings API fails, fuzzy detection unavailable  
**Mitigation:**
- Fallback to regex-only detection if API fails
- Cache embeddings to reduce API calls
- Monitor API availability
- Plan for alternative embedding provider in v1.1

### RISK-005: Pattern Injection via Custom Patterns
**Risk:** Admin adds malicious regex pattern that breaks system  
**Mitigation:**
- Validate all patterns before loading
- Test patterns against safe queries before deployment
- Limit pattern complexity (max length, no catastrophic backtracking)
- Require admin review before custom patterns go live

---

## Open Questions

- **Q-001:** Should fuzzy detection be enabled by default or opt-in?
  - Type: Non-blocking
  - Owner: Product
  - Next step: Decide based on false positive rate measurement

- **Q-002:** How often should the injection example corpus be updated?
  - Type: Non-blocking
  - Owner: Security Team
  - Next step: Establish update cadence (monthly? quarterly?)

- **Q-003:** Should pattern updates trigger automatic re-scanning of existing chunks?
  - Type: Non-blocking
  - Owner: Product
  - Next step: Defer to v1.1 (out of scope for v1.0)

- **Q-004:** What's the maximum number of custom patterns an admin can add?
  - Type: Non-blocking
  - Owner: Product
  - Next step: No limit for v1.0, revisit if performance issues arise

---

## Acceptance Criteria

- [ ] **AC-001** Linked requirement(s): REQ-001
  - Linked user story: US-002, US-003, US-004
  - Linked success criteria: SC-001
  - Validation method: Unit tests + adversarial dataset
  - Proof target: All 40+ patterns tested; false negative rate <5%

- [ ] **AC-002** Linked requirement(s): REQ-002
  - Linked user story: US-005
  - Linked success criteria: SC-005
  - Validation method: Integration test
  - Proof target: Custom pattern in YAML blocks query without code change

- [ ] **AC-003** Linked requirement(s): REQ-003
  - Linked user story: US-004
  - Linked success criteria: SC-002
  - Validation method: Adversarial dataset with typo variants
  - Proof target: Fuzzy detection catches 80%+ of variants

- [ ] **AC-004** Linked requirement(s): REQ-004
  - Linked user story: US-003
  - Linked success criteria: SC-003
  - Validation method: Performance test + integration test
  - Proof target: Ingestion overhead <20%; malicious chunks blocked

- [ ] **AC-005** Linked requirement(s): REQ-005
  - Linked user story: US-001, US-004
  - Linked success criteria: SC-004
  - Validation method: Unit test + integration test
  - Proof target: Modes configurable; same query blocked in strict, allowed in lenient

- [ ] **AC-006** Linked requirement(s): REQ-006
  - Linked user story: US-006
  - Linked success criteria: SC-007
  - Validation method: Manual test + log verification
  - Proof target: Blocked query shows clear reason; logged for audit

- [ ] **AC-007** Linked requirement(s): REQ-007
  - Linked user story: All existing safety checks
  - Linked success criteria: SC-006, SC-008
  - Validation method: Regression test
  - Proof target: Existing 9 patterns work identically; no API changes

- [ ] **AC-008** Linked requirement(s): REQ-008
  - Linked user story: All safety checks
  - Linked success criteria: SC-001
  - Validation method: Test execution
  - Proof target: 50+ test cases; false negative rate <5%; false positive rate <2%

- [ ] **AC-009** Linked requirement(s): NFR-001, NFR-002, NFR-003, NFR-004, NFR-005, NFR-006
  - Linked user story: All
  - Linked success criteria: All
  - Validation method: Performance test, reliability test, security review, observability test
  - Proof target: All NFRs met; no regressions

---

## Notes

**Related documents:**
- `analysis.md` - Current state investigation and gap analysis
- `proposal.md` - High-level approach and trade-offs
- `PRODUCT_ROADMAP.md` - Feature #7.7.1 specification
- `docs/enhancement-recommendations.md` - Original 31 feature proposals

**Implementation guidance:**
- Start with pattern expansion (REQ-001) - most straightforward
- Then YAML storage (REQ-002) - enables custom patterns
- Then fuzzy detection (REQ-003) - most complex, highest value
- Then ingestion integration (REQ-004) - requires pipeline changes
- Then modes (REQ-005) - simple configuration change
- Then UX (REQ-006) - error message updates
- Finally, backward compatibility testing (REQ-007) and evaluation dataset (REQ-008)

**Testing strategy:**
- Unit tests for each pattern category
- Integration tests for safety pipeline
- Performance tests for ingestion and query latency
- Adversarial evaluation dataset (50+ test cases)
- Regression tests for existing 9 patterns
- False positive/negative rate measurement

**Rollout strategy:**
- Deploy to staging first
- Measure false positive rate on real queries
- Tune thresholds based on feedback
- Deploy to production with lenient mode default
- Gradually tighten thresholds based on monitoring

---

**Specification Status:** Ready for Implementation Review  
**Next Step:** Planning phase (aiddk-plan) to create implementation tasks

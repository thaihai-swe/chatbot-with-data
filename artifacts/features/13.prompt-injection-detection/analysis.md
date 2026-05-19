# Prompt Injection Detection Analysis

**Feature:** 13.prompt-injection-detection  
**Date:** 2026-05-19  
**Status:** Research Complete  
**Next Step:** Specification (aiddk-spec)

---

## Executive Summary

**Current State:** Basic prompt injection detection with 9 regex patterns and LLM-based classification at query level only.

**Critical Findings:**
- ✅ Two-stage safety architecture (query + chunk level)
- ⚠️ Only 9/40+ patterns implemented (80% gap)
- ❌ No embedding-based fuzzy detection
- ❌ No ingestion-time safety checks
- ❌ No strict mode configuration
- ❌ No test coverage

**Recommendation:** Implement advanced detection as specified in PRODUCT_ROADMAP.md Feature #7.7.1 (2-3 days effort).

---

## Current Implementation

### Architecture

**Two-Stage Safety Pipeline:**

```
Stage 1: Query-Level Check (Early Rejection)
├─ Location: SafetyService.check_query()
├─ Timing: Before retrieval
├─ Methods: Regex patterns + LLM classification
└─ Result: SafetyTrace with injection_risk + answerability

Stage 2: Chunk-Level Check (Post-Retrieval)
├─ Location: SafetyService.check_chunks()
├─ Timing: After retrieval, before generation
├─ Methods: Regex patterns only (no LLM)
└─ Result: Filtered chunks (malicious removed)
```

**Integration Points:**
- `backend/chat/service.py` - ChatService.process_turn() (lines 62, 109)
- `backend/chat/streaming.py` - StreamingOrchestrator.stream_turn() (lines 66, 107)

### Current Patterns (9 total)

**File:** `backend/chat/safety.py`

```python
INJECTION_PATTERNS = [
    r"(?i)ignore\s+previous\s+instructions",
    r"(?i)disregard\s+all\s+previous",
    r"(?i)reveal\s+your\s+system\s+prompt",
    r"(?i)system\s+instructions",
    r"(?i)you\s+are\s+now\s+a",
    r"(?i)new\s+rule:",
    r"(?i)instead\s+of\s+answering",
    r"(?i)do\s+not\s+cite\s+sources",
    r"(?i)disable\s+citations",
]
```

**Coverage:**
- ✅ Basic prompt override attempts
- ✅ System instruction disclosure
- ✅ Citation manipulation
- ❌ SQL injection
- ❌ NoSQL injection
- ❌ LDAP injection
- ❌ XSS patterns
- ❌ Command injection
- ❌ Path traversal
- ❌ Code execution attempts

### Configuration

**SafetySettings Model** (`backend/schemas/settings.py`):

```python
class SafetySettings(BaseModel):
    groundedness_check_enabled: bool = True
    prompt_injection_detection_enabled: bool = True
    injection_risk_threshold: float = 0.7  # LLM risk score threshold
    refusal_threshold: float = 0.5
    min_similarity_threshold: float = 0.1
    min_results_count: int = 1
```

**Environment Variables:**
- `SAFETY_RISK_THRESHOLD=0.7`
- `MIN_SIMILARITY_THRESHOLD=0.1`
- `MIN_RESULTS_COUNT=1`

**Observed Behavior:**
- `prompt_injection_detection_enabled` flag exists but **not used in code**
- No strict mode configuration
- No per-collection safety policies

### LLM Classification

**Prompt:** `SAFETY_CLASSIFICATION_PROMPT` in `backend/chat/prompts.py`

**Process:**
1. Query sent to LLM with classification instructions
2. LLM returns JSON: `{"risk_score": 0.0-1.0, "classification": "answerable|unanswerable|...", "reason": "..."}`
3. JSON parsed via regex extraction (fragile)
4. Risk score combined with heuristic risk
5. Classification determines answerability

**Limitations:**
- No retry logic for LLM failures
- Fallback to heuristic-only if LLM unavailable
- JSON parsing fragile (regex-based)
- Only used at query level, not chunk level

---

## Critical Gaps

### 1. Pattern Coverage (80% Gap)

**Documented:** 40+ patterns  
**Implemented:** 9 patterns  
**Missing Categories:**
- SQL injection: `' OR '1'='1`, `UNION SELECT`, `DROP TABLE`
- NoSQL injection: `$ne`, `$gt`, `$where`, `{"$regex": ".*"}`
- LDAP injection: `*)(uid=*)`, `admin*`
- XSS: `<script>`, `javascript:`, `onerror=`
- Command injection: `; rm -rf`, `| cat /etc/passwd`, `$(whoami)`
- Path traversal: `../../../etc/passwd`
- Code execution: `eval()`, `exec()`, `__import__`

**Evidence:** Documentation claims 40+ patterns but code shows only 9.

### 2. No Fuzzy Detection

**Current:** Exact regex matching only  
**Missing:** Embedding-based similarity detection

**Impact:**
- Typo variations bypass detection: "ignor previous instructions"
- Obfuscated attacks bypass: "i g n o r e previous"
- Novel attack patterns not detected

**Requirement:** Embedding-based fuzzy detection against known injection corpus.

### 3. No Ingestion-Time Safety

**Current:** Safety checks only at query/retrieval time  
**Missing:** Document scanning during ingestion

**Impact:**
- Malicious documents can be ingested into knowledge base
- Injection patterns embedded in chunks
- No pre-filtering before indexing

**Evidence:** `backend/ingestion/service.py` does not call SafetyService.

### 4. Inconsistent Chunk-Level Detection

**Query-Level:** Regex + LLM classification  
**Chunk-Level:** Regex only (no LLM)

**Impact:**
- Chunks not classified by LLM
- Inconsistent risk assessment
- Potential false negatives

### 5. No Strict Mode

**Current:** Single threshold (0.7)  
**Missing:** Configurable strict/moderate/lenient modes

**Requirement:**
- Strict mode: Lower threshold, more aggressive filtering
- Moderate mode: Current behavior
- Lenient mode: Higher threshold, fewer false positives

### 6. No Test Coverage

**Observed:** No test files for SafetyService  
**Missing:**
- Unit tests for pattern matching
- Integration tests for safety pipeline
- Adversarial evaluation datasets
- False positive/negative rate measurement

---

## Unchanged Behavior to Preserve

**Must Maintain:**
1. Two-stage safety architecture (query + chunk)
2. Early refusal for unanswerable queries
3. SafetyTrace metadata in responses
4. Configuration via SafetySettings
5. Integration points in ChatService and StreamingOrchestrator
6. Logging of filtered chunks

**Must Not Break:**
- Existing 9 patterns must continue to work
- LLM classification fallback behavior
- Groundedness checks (separate from injection detection)
- Citation validation

---

## Root Cause Analysis

**Why Only 9 Patterns?**
- Initial implementation focused on common prompt override attacks
- Documentation written aspirationally (40+ patterns planned, not implemented)
- No systematic pattern library or categorization
- No test-driven development to ensure coverage

**Why No Fuzzy Detection?**
- Requires embedding infrastructure (exists but not integrated)
- Requires known injection corpus (not created)
- Requires similarity threshold tuning (not researched)

**Why No Ingestion Safety?**
- Ingestion pipeline built before safety service
- No requirement for pre-ingestion scanning in original PRD
- Performance concerns (scanning all chunks during ingestion)

---

## Risks

### High Risk
1. **Injection Pattern Gap:** 80% of documented patterns missing, system vulnerable to SQL/NoSQL/XSS/command injection
2. **No Ingestion Safety:** Malicious documents can be ingested without detection
3. **No Test Coverage:** Changes could break existing detection without notice

### Medium Risk
1. **Inconsistent Detection:** Chunk-level uses regex only, query-level uses LLM
2. **LLM Dependency:** Safety depends on LLM availability, no robust fallback
3. **Configuration Not Used:** `prompt_injection_detection_enabled` flag ignored

### Low Risk
1. **No Strict Mode:** Single threshold may not fit all use cases
2. **Minimal Logging:** Hard to debug false positives/negatives
3. **No Metrics:** Cannot measure detection effectiveness

---

## Next Proving Step

**Recommended:** Create specification (aiddk-spec) for Advanced Prompt Injection Detection

**Specification Should Address:**
1. **Pattern Expansion:** Define 40+ patterns across 7 categories (SQL, NoSQL, LDAP, XSS, command, path, code)
2. **Fuzzy Detection:** Design embedding-based similarity check with threshold tuning
3. **Strict Mode:** Define three modes (strict/moderate/lenient) with thresholds
4. **Ingestion Safety:** Design per-chunk scanning during ingestion with performance optimization
5. **Test Strategy:** Define adversarial evaluation datasets and acceptance criteria
6. **Migration Path:** Ensure backward compatibility with existing 9 patterns

**Implementation Estimate:** 2-3 days (per PRODUCT_ROADMAP.md Feature #7.7.1)

---

## Promotion Candidates

**For Constitution:**
- Safety checks must occur at both query and chunk level
- LLM classification must have fallback to heuristic-only mode
- Configuration flags must be enforced in code, not just defined

**For Project Knowledge Base:**
- SafetyService architecture: Two-stage pipeline (query + chunk)
- Integration points: ChatService.process_turn() and StreamingOrchestrator.stream_turn()
- Pattern library location: backend/chat/safety.py INJECTION_PATTERNS

---

## Appendix: File Inventory

**Core Implementation:**
- `backend/chat/safety.py` (128 lines) - SafetyService with 9 patterns
- `backend/chat/grounding.py` - GroundingService (separate from injection)
- `backend/chat/prompts.py` - SAFETY_CLASSIFICATION_PROMPT
- `backend/schemas/chat.py` - SafetyTrace, SafetyGroundedness schemas
- `backend/schemas/settings.py` - SafetySettings configuration

**Integration:**
- `backend/chat/service.py` - ChatService.process_turn()
- `backend/chat/streaming.py` - StreamingOrchestrator.stream_turn()

**Configuration:**
- `backend/config.py` - SettingsManager
- `backend/.env.sample` - Environment defaults

**Documentation:**
- `docs/system-architecture.md` - Claims 40+ patterns
- `docs/enhancement-recommendations.md` - Future hardening plans
- `PRODUCT_ROADMAP.md` - Feature #7.7.1 specification

---

## Verification

**Facts vs. Inferences:**
- ✅ FACT: 9 patterns in INJECTION_PATTERNS list (observed in code)
- ✅ FACT: No SafetyService call in ingestion pipeline (verified by code search)
- ✅ FACT: No test files for SafetyService (verified by file search)
- ✅ FACT: `prompt_injection_detection_enabled` not used (verified by grep)
- ⚠️ INFERENCE: 40+ patterns needed (based on documentation, not observed attacks)
- ⚠️ INFERENCE: Embedding-based detection will improve accuracy (hypothesis, not proven)

**Evidence Quality:** High - All findings backed by code inspection and file search.

**Next Step Justification:** Specification needed to define exact patterns, thresholds, and integration points before implementation.

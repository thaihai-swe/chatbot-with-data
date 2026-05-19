# Proposal: Advanced Prompt Injection Detection

**Feature:** 13.prompt-injection-detection  
**Date:** 2026-05-19  
**Status:** 🟡 Awaiting Alignment

---

## 💡 The Problem

The system currently detects only 9 basic prompt injection patterns (prompt override, system disclosure, citation manipulation). This leaves 80% of documented attack vectors undetected:

- **SQL/NoSQL injection:** Attackers can inject database queries through knowledge base documents or user queries
- **XSS/Command injection:** Malicious code can be embedded in ingested documents
- **Obfuscated attacks:** Typos and spacing variations bypass exact regex matching
- **Ingestion gap:** Malicious documents are indexed without safety checks, poisoning the knowledge base
- **No test coverage:** Changes could break existing detection without notice

**Impact:** System is vulnerable to sophisticated injection attacks that bypass current detection.

---

## 🎯 Objectives

1. **Expand pattern coverage** from 9 to 40+ patterns across 7 attack categories (SQL, NoSQL, LDAP, XSS, command, path, code execution)
2. **Add fuzzy detection** via embedding-based similarity matching against known injection examples
3. **Secure ingestion pipeline** by scanning chunks during document upload
4. **Enable configurable safety modes** (strict/moderate/lenient) for different risk tolerances
5. **Maintain backward compatibility** with existing 9 patterns and two-stage safety architecture

---

## 🛠 High-Level Approach

### Architecture (Unchanged)
- Preserve two-stage safety pipeline: query-level (early rejection) + chunk-level (post-retrieval filtering)
- Keep SafetyTrace metadata and integration points in ChatService/StreamingOrchestrator
- Maintain LLM classification fallback behavior

### Pattern Expansion
- **Storage:** YAML/JSON config file (`backend/config/injection_patterns.yaml`)
- **Categories:** SQL, NoSQL, LDAP, XSS, command injection, path traversal, code execution
- **Maintenance:** Patterns updatable without code changes; admin can add custom patterns

### Fuzzy Detection
- **Corpus:** Predefined set of ~50 known injection examples + user-submitted custom examples
- **Threshold:** 0.70+ embedding similarity triggers match
- **Integration:** Runs alongside regex patterns at query and chunk level
- **Fallback:** Uses existing OpenAI embeddings infrastructure

### Ingestion Safety
- **Timing:** Synchronous scanning (block malicious chunks before indexing)
- **Performance:** ~10-20% ingestion overhead acceptable for security guarantee
- **Integration:** SafetyService.check_chunks() called during ingestion pipeline

### Configuration Modes
- **Strict mode:** `injection_risk_threshold = 0.5` (aggressive filtering)
- **Moderate mode:** `injection_risk_threshold = 0.7` (current behavior)
- **Lenient mode:** `injection_risk_threshold = 0.9` (fewer false positives)
- **Behavior:** All 40+ patterns checked in all modes; only threshold differs

### False Positive Handling
- **User experience:** Clear error message explaining why query was blocked
- **No override:** Users must contact admin to whitelist patterns
- **Logging:** All blocked queries logged for audit trail

---

## ⚠️ Known Constraints / Risks

### Performance
- Ingestion will be 10-20% slower due to synchronous chunk scanning
- Fuzzy detection adds embedding API calls (mitigated by caching)
- 40+ regex patterns increase per-query latency slightly

### Backward Compatibility
- Existing 9 patterns must continue to work identically
- SafetyTrace schema must remain compatible
- LLM classification fallback must be preserved

### Maintenance Burden
- 40+ patterns require ongoing updates as new attacks emerge
- User-submitted patterns need validation to prevent false positives
- Injection example corpus needs periodic refresh

### Testing
- No existing test coverage for SafetyService
- Adversarial evaluation dataset must be created and maintained
- False positive/negative rates must be measured

### External Dependencies
- Embedding-based fuzzy detection depends on OpenAI embeddings API
- Pattern corpus requires security research or threat feed integration

---

## ✅ Success Criteria

- [ ] **Pattern Coverage:** 40+ patterns implemented across 7 categories (SQL, NoSQL, LDAP, XSS, command, path, code)
- [ ] **Fuzzy Detection:** Embedding-based similarity matching with 0.70+ threshold functional
- [ ] **Ingestion Safety:** Chunks scanned synchronously during ingestion; malicious chunks blocked
- [ ] **Configuration:** Strict/moderate/lenient modes configurable via SafetySettings
- [ ] **Pattern Storage:** Patterns loaded from `backend/config/injection_patterns.yaml`; updatable without code changes
- [ ] **Backward Compatibility:** Existing 9 patterns work identically; SafetyTrace schema unchanged
- [ ] **False Positive UX:** Blocked queries show clear reason; users cannot override
- [ ] **Test Coverage:** Adversarial evaluation dataset created; false positive/negative rates measured
- [ ] **Performance:** Ingestion overhead <20%; per-query latency impact <50ms
- [ ] **Documentation:** Pattern categories documented; admin guide for custom patterns

---

## 📋 Scope Definition

### In Scope
- Expand regex patterns to 40+ across 7 categories
- Implement embedding-based fuzzy detection (0.70+ similarity)
- Add synchronous chunk scanning during ingestion
- Implement strict/moderate/lenient modes (threshold-based)
- Store patterns in YAML/JSON config file
- Create adversarial evaluation dataset
- Maintain backward compatibility with existing 9 patterns

### Out of Scope
- Dynamic pattern updates from external threat feeds (future enhancement)
- Per-collection safety policies (future enhancement)
- Admin UI for pattern management (future enhancement)
- Real-time false positive feedback loop (future enhancement)
- Integration with external security databases (future enhancement)

### Non-Goals
- Replace LLM classification with pattern-only detection
- Change two-stage safety architecture
- Modify SafetyTrace schema
- Add new safety checks beyond injection detection

---

## 🚀 Next Steps

**If aligned:** Proceed to detailed specification (`spec.md`) defining:
1. Exact 40+ patterns with regex and category
2. Fuzzy detection algorithm and corpus format
3. Ingestion integration points and performance targets
4. Configuration schema and environment variables
5. Test strategy and acceptance criteria

**Estimated implementation:** 2-3 days (per PRODUCT_ROADMAP.md Feature #7.7.1)

---

**Status:** 🟡 Awaiting Your Alignment  
*Please confirm this direction is correct, or suggest changes before we proceed to detailed spec.*

# Document Ingestion — Anti-Patterns

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Editing Past Migration Versions

**Why it fails:** Modifying an already-applied migration version breaks existing databases and the migration runner's state tracking.

**What to do instead:** Add a new migration version directory. The migration runner handles sequential application automatically.

**Citation:** `backend/migrations/runner.py` tracks applied versions by directory name.

---

## Skipping Duplicate Detection

**Why it fails:** Identical files or near-duplicate text content get indexed multiple times, wasting embedding API calls, storage, and polluting search results.

**What to do instead:** Run duplicate detection (file hash → text hash → similarity) before chunking and embedding. Present duplicates for user decision.

**Citation:** `backend/duplicate_detection/` provides 3-tier dedup; `backend/ingestion/` routes through it.

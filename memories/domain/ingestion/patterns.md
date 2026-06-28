# Document Ingestion — Patterns

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Strategy Pattern for Chunking

**When to use:** When documents of different formats need format-specific splitting.

**Key implementation notes:**
- Each chunking strategy implements a common interface with `chunk(document) → list[Chunk]`
- Auto-selection dispatches by document MIME type / extension
- New strategies can be added without modifying existing ones

**Citation:** `backend/chunking/` contains 5 strategy modules all implementing the same interface.

---

## Metadata-First, Vector-Second Indexing

**When to use:** When documents need both SQL metadata and vector search.

**Key implementation notes:**
- Write document metadata to SQLite first (reliable OLTP commit)
- Then compute embeddings and index into Weaviate (async, retry-capable)
- Metadata serves as the source of truth; Weaviate is a search index that can be rebuilt

**Citation:** `backend/ingestion/` orchestrates this two-phase flow.

---

## Append-Only Migration Pattern

**When to use:** When the SQLite schema evolves over time.

**Key implementation notes:**
- Each migration is a numbered version directory with `up.sql` and `down.sql`
- `runner.py` tracks applied versions in a meta-table
- Never modify past migration versions — always add new ones

**Citation:** `backend/migrations/` contains 4 version directories; `backend/migrations/runner.py` manages execution.

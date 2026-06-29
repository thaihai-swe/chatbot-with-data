<!-- triaged: true, date: 2026-06-29 -->
# Session Extracts: 5.0-session-by-collection

*   **EXT-001 (Candidate Heuristic):** SQLite migration queries on deprecated tables must check for table existence.
    *   *Observation:* Fresh database builds (e.g. running reset scripts) execute `SCHEMA_STATEMENTS` first. Since deprecated tables are removed from these statements, executing legacy data-migrations that target these tables will crash with "no such table".
    *   *Heuristic:* Always check `sqlite_master` for table existence before running data-migrations on deprecated/dropped tables.
    *   *Proposed Destination:* [learned-heuristics.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/memories/repo/learned-heuristics.md)

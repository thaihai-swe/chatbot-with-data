"""Delete all records from SQLite and Weaviate."""

import sys
import os

# Ensure we load the .env from backend/ regardless of CWD
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.join(_scripts_dir, "..", "backend")
sys.path.insert(0, _backend_dir)

from dotenv import load_dotenv

dotenv_path = os.path.join(_backend_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # fallback to default discovery
    load_dotenv()

# --- SQLite ---
from migrations.runner import reset_database, apply_migrations

print("=== Resetting SQLite ===")
reset_database()
apply_migrations()
print("SQLite reset and migrations reapplied.")

# --- Weaviate ---
try:
    from indexing.weaviate_store import WeaviateVectorStore

    print("=== Resetting Weaviate ===")
    store = WeaviateVectorStore()
    count_before = store.count()
    print(f"Objects before: {count_before}")
    store.clear_all()
    count_after = store.count()
    print(f"Objects after: {count_after}")
    store.client.close()
except Exception as e:
    print(f"Weaviate reset skipped (not available?): {e}")

print("Done.")

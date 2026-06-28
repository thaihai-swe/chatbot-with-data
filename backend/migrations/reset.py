import sys
import os

# Add backend directory to sys.path so we can import things
backend_dir = "/Users/thaihai-swe/Desktop/chatbot-with-data/backend"
sys.path.insert(0, backend_dir)

# Import and reset SQLite
print("Resetting SQLite database...")
from migrations.runner import reset_database, apply_migrations
reset_database()
apply_migrations()
print("SQLite database reset and migrated.")

# Import and clear Weaviate
print("Clearing Weaviate collection...")
from indexing.weaviate_store import WeaviateVectorStore
store = WeaviateVectorStore()
store.clear_all()
print("Weaviate collection cleared.")

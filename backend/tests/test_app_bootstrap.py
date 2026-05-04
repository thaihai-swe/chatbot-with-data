import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class AppBootstrapTest(unittest.TestCase):
    def test_create_app_initializes_local_persistence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            app = create_app(
                {
                    "TESTING": True,
                    "DATA_DIR": str(base_dir / "data"),
                    "SQLITE_PATH": str(base_dir / "data" / "app.sqlite3"),
                    "CHROMA_DIR": str(base_dir / "data" / "chroma"),
                }
            )

            self.assertTrue((base_dir / "data").exists())
            self.assertTrue((base_dir / "data" / "chroma").exists())
            self.assertTrue((base_dir / "data" / "app.sqlite3").exists())
            self.assertIn("chroma_client", app.extensions)

            with sqlite3.connect(base_dir / "data" / "app.sqlite3") as conn:
                rows = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()

            table_names = {row[0] for row in rows}
            self.assertTrue(
                {
                    "collections",
                    "documents",
                    "ingestion_attempts",
                    "duplicate_logs",
                    "chunk_metadata",
                }.issubset(table_names)
            )


if __name__ == "__main__":
    unittest.main()

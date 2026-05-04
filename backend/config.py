from pathlib import Path


def build_config(overrides=None):
    backend_dir = Path(__file__).resolve().parent
    data_dir = backend_dir / "data"

    config = {
        "TESTING": False,
        "DATA_DIR": str(data_dir),
        "UPLOAD_DIR": str(data_dir / "uploads"),
        "SQLITE_PATH": str(data_dir / "app.sqlite3"),
        "CHROMA_DIR": str(data_dir / "chroma"),
        "CHROMA_COLLECTION_PREFIX": "collection",
        "DEFAULT_CHUNK_SIZE": 512,
        "DEFAULT_CHUNK_OVERLAP": 64,
        "DEFAULT_EMBEDDING_MODEL": "local-hash-v1",
        "EMBEDDING_DIMENSIONS": 32,
        "URL_TIMEOUT_SECONDS": 30,
    }

    if overrides:
        config.update(overrides)

    return config

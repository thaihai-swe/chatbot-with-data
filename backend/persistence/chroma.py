from pathlib import Path

from chromadb import PersistentClient


def init_chroma_client(chroma_dir):
    chroma_path = Path(chroma_dir)
    chroma_path.mkdir(parents=True, exist_ok=True)
    return PersistentClient(path=str(chroma_path))

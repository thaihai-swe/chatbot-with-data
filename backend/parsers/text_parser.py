from pathlib import Path


def parse_text_file(path):
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    return {
        "text": text,
        "metadata": {
            "title": file_path.stem,
            "source_filename": file_path.name,
        },
        "errors": [],
    }

from pathlib import Path

from backend.parsers.text_parser import parse_text_file


def parse_markdown_file(path):
    result = parse_text_file(path)
    title = Path(path).stem
    for line in result["text"].splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip() or title
            break
    result["metadata"]["title"] = title
    return result

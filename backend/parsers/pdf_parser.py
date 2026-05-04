from pathlib import Path

from PyPDF2 import PdfReader


def parse_pdf_file(path):
    file_path = Path(path)
    reader = PdfReader(str(file_path))
    page_texts = []

    for page in reader.pages:
        page_texts.append(page.extract_text() or "")

    return {
        "text": "\n".join(page_texts),
        "metadata": {
            "title": file_path.stem,
            "source_filename": file_path.name,
            "page_count": len(page_texts),
            "page_texts": page_texts,
        },
        "errors": [],
    }

import pytest
from pathlib import Path
from extractors.text_extractor import TextExtractor
from extractors.pdf_extractor import PdfExtractor
from unittest.mock import MagicMock

def test_text_extractor_uses_uuid_path_as_title(tmp_path):
    file_path = tmp_path / "some_uuid.txt"
    file_path.write_text("content")
    extractor = TextExtractor()
    
    # Passing a descriptive fallback title
    result = extractor.extract(str(file_path), "txt", fallback_title="Meeting Notes.txt")
    
    # It should use the fallback title (stemmed)
    assert result["title"] == "Meeting Notes"

def test_pdf_extractor_prefers_metadata_over_fallback(tmp_path, mocker):
    file_path = tmp_path / "some_uuid.pdf"
    file_path.write_bytes(b"%PDF-1.4")
    
    # Mock PdfReader to return metadata with a title
    mock_reader = mocker.patch("extractors.pdf_extractor.PdfReader")
    mock_reader.return_value.metadata = {"/Title": "Internal PDF Title"}
    mock_reader.return_value.pages = []
    
    # Mock pdfplumber to avoid error
    mock_pdfplumber = mocker.patch("pdfplumber.open")
    mock_pdfplumber.return_value.__enter__.return_value.pages = []
    
    extractor = PdfExtractor()
    result = extractor.extract(str(file_path), fallback_title="Uploaded Name.pdf")
    
    # Should PREFER internal title
    assert result["title"] == "Internal PDF Title"

def test_pdf_extractor_uses_fallback_when_metadata_missing(tmp_path, mocker):
    file_path = tmp_path / "some_uuid.pdf"
    file_path.write_bytes(b"%PDF-1.4")
    
    # Mock PdfReader to return NO metadata
    mock_reader = mocker.patch("extractors.pdf_extractor.PdfReader")
    mock_reader.return_value.metadata = {}
    mock_reader.return_value.pages = []
    
    # Mock pdfplumber
    mock_pdfplumber = mocker.patch("pdfplumber.open")
    mock_pdfplumber.return_value.__enter__.return_value.pages = []
    
    extractor = PdfExtractor()
    result = extractor.extract(str(file_path), fallback_title="My Resume.pdf")
    
    # Should use fallback title
    assert result["title"] == "My Resume"

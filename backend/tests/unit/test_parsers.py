import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from backend.parsers.markdown_parser import parse_markdown_file
from backend.parsers.pdf_parser import parse_pdf_file
from backend.parsers.text_parser import parse_text_file
from backend.parsers.url_parser import parse_url


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class ParserTests(unittest.TestCase):
    def test_parse_text_file_reads_fixture_and_metadata(self):
        result = parse_text_file(FIXTURES_DIR / "sample.txt")

        self.assertIn("Plain text fixture", result["text"])
        self.assertEqual(result["metadata"]["title"], "sample")
        self.assertEqual(result["metadata"]["source_filename"], "sample.txt")
        self.assertEqual(result["errors"], [])

    def test_parse_text_file_replaces_invalid_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "broken.txt"
            path.write_bytes(b"hello\xffworld")

            result = parse_text_file(path)

        self.assertEqual(result["text"], "hello\ufffdworld")
        self.assertEqual(result["metadata"]["title"], "broken")

    def test_parse_markdown_file_uses_first_heading_as_title(self):
        result = parse_markdown_file(FIXTURES_DIR / "sample.md")

        self.assertEqual(result["metadata"]["title"], "Product Notes")
        self.assertIn("## Detail", result["text"])

    def test_parse_pdf_file_extracts_text_and_page_metadata(self):
        result = parse_pdf_file(FIXTURES_DIR / "sample.pdf")

        self.assertEqual(result["metadata"]["page_count"], 1)
        self.assertEqual(result["metadata"]["page_texts"], ["Hello PDF"])
        self.assertIn("Hello PDF", result["text"])
        self.assertEqual(result["errors"], [])

    def test_parse_pdf_file_raises_on_corrupt_input(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "broken.pdf"
            path.write_text("not a real pdf", encoding="utf-8")

            with self.assertRaises(Exception):
                parse_pdf_file(path)

    @patch("backend.parsers.url_parser.requests.get")
    def test_parse_url_extracts_title_and_body_text(self, mock_get):
        response = Mock()
        response.text = "<html><head><title>Fixture Doc</title></head><body>Alpha <strong>Beta</strong></body></html>"
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = parse_url("https://example.com/docs")

        self.assertEqual(result["metadata"]["title"], "Fixture Doc")
        self.assertEqual(result["metadata"]["source_url"], "https://example.com/docs")
        self.assertEqual(result["text"], "Fixture Doc Alpha Beta")
        self.assertEqual(result["errors"], [])

    @patch("backend.parsers.url_parser.requests.get")
    def test_parse_url_raises_http_errors(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("boom")
        mock_get.return_value = response

        with self.assertRaises(requests.HTTPError):
            parse_url("https://example.com/broken")


if __name__ == "__main__":
    unittest.main()

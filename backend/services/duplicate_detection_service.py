import hashlib
import re
from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit

from backend.persistence.db import get_connection
from backend.utils import sha256_text


class DuplicateDetectionService:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    @staticmethod
    def compute_file_hash(data):
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def normalize_text(text):
        return re.sub(r"\s+", " ", (text or "")).strip().lower()

    @classmethod
    def compute_text_hash(cls, text):
        return sha256_text(cls.normalize_text(text))

    @staticmethod
    def canonicalize_url(url):
        if not url:
            return None
        parts = urlsplit(url.strip())
        netloc = parts.netloc.lower()
        path = parts.path.rstrip("/")
        return urlunsplit(("", netloc, path, "", ""))

    def detect(self, source_type, file_hash, source_url, raw_text, title):
        canonical_url = self.canonicalize_url(source_url)
        normalized_text = self.normalize_text(raw_text)
        text_hash = self.compute_text_hash(raw_text) if raw_text else None

        with get_connection(self.sqlite_path) as connection:
            existing = connection.execute(
                """
                SELECT document_id, title, source_url, source_identity, raw_text, file_hash, text_hash
                FROM documents
                WHERE deletion_state = 'active'
                """
            ).fetchall()

        best_match = None

        for record in existing:
            if file_hash and record.get("file_hash") == file_hash:
                return {
                    "status": "exact_duplicate",
                    "method": "file_hash",
                    "matched_document_id": record["document_id"],
                    "similarity_score": 1.0,
                    "canonical_url": canonical_url,
                    "text_hash": text_hash,
                }
            if text_hash and record.get("text_hash") == text_hash:
                status = "same_content_different_source"
                if canonical_url and self.canonicalize_url(record.get("source_url")) == canonical_url:
                    status = "exact_duplicate"
                return {
                    "status": status,
                    "method": "normalized_text_hash",
                    "matched_document_id": record["document_id"],
                    "similarity_score": 1.0,
                    "canonical_url": canonical_url,
                    "text_hash": text_hash,
                }
            if canonical_url and self.canonicalize_url(record.get("source_url")) == canonical_url:
                return {
                    "status": "same_url",
                    "method": "url_canonicalization",
                    "matched_document_id": record["document_id"],
                    "similarity_score": None,
                    "canonical_url": canonical_url,
                    "text_hash": text_hash,
                }

            existing_text = self.normalize_text(record.get("raw_text"))
            if normalized_text and existing_text:
                ratio = SequenceMatcher(None, normalized_text, existing_text).ratio()
                if ratio >= 0.92:
                    return {
                        "status": "near_duplicate",
                        "method": "near_duplicate_overlap",
                        "matched_document_id": record["document_id"],
                        "similarity_score": round(ratio, 4),
                        "canonical_url": canonical_url,
                        "text_hash": text_hash,
                    }
                if title and record.get("title") and title.strip().lower() == record["title"].strip().lower():
                    best_match = {
                        "status": "same_title_different_content",
                        "method": "title_metadata_match",
                        "matched_document_id": record["document_id"],
                        "similarity_score": round(ratio, 4),
                        "canonical_url": canonical_url,
                        "text_hash": text_hash,
                    }

        if best_match:
            return best_match

        return {
            "status": "unique",
            "method": "none",
            "matched_document_id": None,
            "similarity_score": None,
            "canonical_url": canonical_url,
            "text_hash": text_hash,
        }

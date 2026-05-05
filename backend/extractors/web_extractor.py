from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

from config import get_settings
from extractors.common import normalized_text_hash
from storage import LocalStorage


def canonicalize_url(url: str) -> str:
    split = urlsplit(url)
    path = split.path.rstrip("/") or "/"
    return urlunsplit((split.scheme.lower(), split.netloc.lower(), path, "", ""))


class WebExtractor:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.storage = LocalStorage()

    def extract(self, source_uri: str) -> dict[str, Any]:
        try:
            response = requests.get(source_uri, timeout=self.settings.url_timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ValueError(f"Unable to fetch URL: {exc}") from exc

        html = response.text
        snapshot_path = self.storage.save_snapshot(content=html)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else source_uri
        text = soup.get_text(separator="\n", strip=True)
        return {
            "title": title,
            "source_uri": source_uri,
            "canonical_source_uri": canonicalize_url(source_uri),
            "mime_type": response.headers.get("Content-Type"),
            "extracted_text": text,
            "metadata": {
                "http_headers": dict(response.headers),
                "status_code": response.status_code,
            },
            "file_hash": None,
            "normalized_text_hash": normalized_text_hash(text),
            "snapshot_path": snapshot_path,
        }

#!/usr/bin/env python3
"""Compact, human-readable session state for context loading and resumption."""

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = 2
FRONT_MATTER = "---"
CONTEXT_START = "<!-- COREZERO_CONTEXT -->"
CONTEXT_END = "<!-- /COREZERO_CONTEXT -->"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def default_session_dir(root, feature):
    if not feature:
        return None
    return Path(root) / ".corezero" / "sessions" / feature


def default_session_path(root, feature):
    session_dir = default_session_dir(root, feature)
    return session_dir / "session.md" if session_dir else None


def _front_matter(text):
    if not text.startswith(f"{FRONT_MATTER}\n"):
        return {}, text
    end = text.find(f"\n{FRONT_MATTER}\n", len(FRONT_MATTER) + 1)
    if end == -1:
        raise ValueError("Invalid session.md front matter: closing delimiter is missing")
    raw = text[len(FRONT_MATTER) + 1:end]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid session.md front matter: {exc}") from exc
    return data, text[end + len(f"\n{FRONT_MATTER}\n"):]


def load_session(path):
    if not path:
        return None
    path = Path(path)
    if not path.exists():
        return None
    try:
        metadata, body = _front_matter(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Invalid session state: {path}: {exc}") from exc
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported session schema in {path}: "
            f"{metadata.get('schema_version')!r} (expected {SCHEMA_VERSION})"
        )
    return {"metadata": metadata, "body": body}


def _managed_context(context):
    lines = [
        CONTEXT_START,
        "## Context Evidence",
        "",
        f"- Loaded sources: {context.get('loaded_count', 0)}",
        f"- Omitted sources: {context.get('omitted_count', 0)}",
        f"- Estimated tokens: {context.get('total_tokens', 0)}",
    ]
    warnings = context.get("warnings", [])
    if warnings:
        lines.append(f"- Warnings: {'; '.join(warnings)}")
    else:
        lines.append("- Warnings: None")
    lines.append(CONTEXT_END)
    return "\n".join(lines)


def _replace_context(body, context):
    block = _managed_context(context)
    pattern = re.compile(
        re.escape(CONTEXT_START) + r".*?" + re.escape(CONTEXT_END),
        re.DOTALL,
    )
    if pattern.search(body):
        return pattern.sub(block, body, count=1).rstrip() + "\n"
    body = body.rstrip()
    return f"{body}\n\n{block}\n" if body else f"{block}\n"


def write_session(path, metadata, context):
    """Update front matter and managed context while preserving human notes."""
    path = Path(path)
    existing = load_session(path) if path.exists() else None
    body = existing["body"] if existing else (
        f"# Session: {metadata.get('feature') or '[feature]'}\n\n"
        "## Progress\n\n"
        "## Handoff\n\n"
    )
    payload = dict(metadata)
    payload["schema_version"] = SCHEMA_VERSION
    payload["updated_at"] = utc_now()
    payload["loaded_count"] = context.get("loaded_count", 0)
    payload["omitted_count"] = context.get("omitted_count", 0)
    payload["total_tokens"] = context.get("total_tokens", 0)
    payload["warnings"] = list(context.get("warnings", []))
    content = (
        f"{FRONT_MATTER}\n"
        f"{json.dumps(payload, indent=2)}\n"
        f"{FRONT_MATTER}\n"
        f"{_replace_context(body, context)}"
    )
    atomic_write(path, content)


def update_session_sections(path, progress=None, handoff=None):
    """Replace human-owned session sections without touching managed state."""
    path = Path(path)
    session = load_session(path)
    if not session:
        raise ValueError(f"Session state does not exist: {path}")

    body = session["body"]

    def replace_section(text, title, replacement):
        if replacement is None:
            return text
        pattern = re.compile(
            rf"(^## {re.escape(title)}\s*$)(.*?)(?=^## |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        content = replacement.rstrip()
        if not content:
            content = ""
        replacement_text = rf"\1\n\n{content}\n\n"
        if pattern.search(text):
            return pattern.sub(lambda match: replacement_text, text, count=1)
        return text.rstrip() + f"\n\n## {title}\n\n{content}\n"

    body = replace_section(body, "Progress", progress)
    body = replace_section(body, "Handoff", handoff)
    raw = path.read_text(encoding="utf-8")
    marker = raw.find(f"\n{FRONT_MATTER}\n", len(FRONT_MATTER) + 1)
    if marker == -1:
        raise ValueError(f"Invalid session state: {path}: closing delimiter is missing")
    content = raw[:marker + len(f"\n{FRONT_MATTER}\n")] + body
    atomic_write(path, content)

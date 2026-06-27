#!/usr/bin/env python3
"""Validate Mermaid syntax locally.

Usage:
  python3 validate_mermaid.py <diagram.mmd>

The script always performs basic structural validation. If `mmdc` is available,
it also invokes the Mermaid parser by rendering to a temporary SVG.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


KNOWN_PREFIXES = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "mindmap",
    "journey",
    "timeline",
    "gantt",
    "C4Context",
    "C4Container",
    "C4Component",
    "C4Dynamic",
    "C4Deployment",
)


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def basic_validate(content: str) -> None:
    stripped = content.strip()
    if not stripped:
        fail("Mermaid file is empty.")

    first_line = next((line.strip() for line in stripped.splitlines() if line.strip()), "")
    if not first_line.startswith(KNOWN_PREFIXES):
        fail(f"Unknown Mermaid diagram prefix: {first_line!r}")

    if stripped.count("[") != stripped.count("]"):
        fail("Unbalanced square brackets in Mermaid source.")

    if stripped.count("{") != stripped.count("}"):
        fail("Unbalanced curly braces in Mermaid source.")

    if stripped.count("(") != stripped.count(")"):
        fail("Unbalanced parentheses in Mermaid source.")


def parser_validate(path: Path) -> bool:
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "mermaid-validate.svg"
        completed = subprocess.run(
            [mmdc, "-i", str(path), "-o", str(output)],
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip() or "unknown mmdc error"
            fail(f"mmdc validation failed: {stderr}")
    return True


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: python3 validate_mermaid.py <diagram.mmd>")

    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.is_file():
        fail(f"File not found: {path}")

    content = path.read_text(encoding="utf-8")
    basic_validate(content)
    parser_validated = parser_validate(path)

    if parser_validated:
        print(f"OK: Mermaid syntax and render validation passed for {path}")
    else:
        print(f"OK: Mermaid structural validation passed for {path}")
        print("WARN: `mmdc` is not installed; parser-level render validation was skipped.")


if __name__ == "__main__":
    main()

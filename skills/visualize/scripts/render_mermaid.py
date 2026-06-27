#!/usr/bin/env python3
"""Render Mermaid source to SVG via Mermaid CLI.

Usage:
  python3 render_mermaid.py <diagram.mmd> <diagram.svg>
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def main() -> None:
    if len(sys.argv) != 3:
        fail("Usage: python3 render_mermaid.py <diagram.mmd> <diagram.svg>")

    mmdc = shutil.which("mmdc")
    if not mmdc:
        fail("`mmdc` is not installed. Install `@mermaid-js/mermaid-cli` to render Mermaid to SVG.")

    source = Path(sys.argv[1]).expanduser().resolve()
    target = Path(sys.argv[2]).expanduser().resolve()

    if not source.is_file():
        fail(f"File not found: {source}")

    target.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [mmdc, "-i", str(source), "-o", str(target)],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "unknown mmdc error"
        fail(f"Mermaid render failed: {stderr}")

    print(f"OK: Rendered Mermaid SVG to {target}")


if __name__ == "__main__":
    main()

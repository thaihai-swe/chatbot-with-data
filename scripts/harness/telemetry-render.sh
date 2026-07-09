#!/usr/bin/env bash
# telemetry-render.sh — regenerate harness-telemetry.md from JSONL records
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

ROOT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT_DIR="$2"; shift 2 ;;
    *) echo "Usage: $0 [--root <path>]"; exit 1 ;;
  esac
done

RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-${HARNESS_REPO_ROOT:-}}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}

JSONL_FILE="$RESOLVED_ROOT/core-zero/memories/repo/harness-telemetry.jsonl"

if [[ ! -f "$JSONL_FILE" ]]; then
  MD_FILE="$RESOLVED_ROOT/core-zero/memories/repo/harness-telemetry.md"
  echo "# Harness Telemetry" > "$MD_FILE"
  echo "No records yet." >> "$MD_FILE"
  echo "Rendered empty report to $MD_FILE"
  exit 0
fi

python3 -c "
import os, sys
sys.path.insert(0, os.path.join('$RESOLVED_ROOT', 'scripts/core'))
from _lib.telemetry_store import render_md
render_md('$RESOLVED_ROOT')
print('Rendered telemetry report')
"

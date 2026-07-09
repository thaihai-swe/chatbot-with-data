#!/usr/bin/env bash
# telemetry-update.sh — update fields on an existing JSONL telemetry record
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

ROOT_DIR=""
RECORD_ID=""
STATUS=""
FIX_APPLIED=""

usage() { echo "Usage: $0 --id <OBS-NNN> --status <open|closed|wontfix> [--fix-applied <desc>] [--root <path>]"; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id)         RECORD_ID="$2"; shift 2 ;;
    --status)     STATUS="$2"; shift 2 ;;
    --fix-applied) FIX_APPLIED="$2"; shift 2 ;;
    --root)       ROOT_DIR="$2"; shift 2 ;;
    *) usage ;;
  esac
done

[[ -z "$RECORD_ID" ]] && usage

RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-${HARNESS_REPO_ROOT:-}}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}

TELEMETRY_FILE="$RESOLVED_ROOT/core-zero/memories/repo/harness-telemetry.jsonl"
[[ -f "$TELEMETRY_FILE" ]] || { echo "ERROR: $TELEMETRY_FILE not found"; exit 1; }

python3 -c "
import os, sys
sys.path.insert(0, os.path.join('$RESOLVED_ROOT', 'scripts/core'))
from _lib.telemetry_store import update_record
update_record('$RESOLVED_ROOT', '$RECORD_ID', '${STATUS:-}' or None, '${FIX_APPLIED:-}' or None)
print('Updated $RECORD_ID')
"

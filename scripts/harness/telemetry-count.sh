#!/usr/bin/env bash
# telemetry-count.sh
# Count open JSONL telemetry records for a given task or feature.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

ROOT_DIR=""
TASK_ID=""
FEATURE_SLUG=""

usage() {
  echo "Usage: $0 --task <TASK-NNN> [--root <path>] [--feature <slug>]"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)    ROOT_DIR="$2"; shift 2 ;;
    --task)    TASK_ID="$2"; shift 2 ;;
    --feature) FEATURE_SLUG="$2"; shift 2 ;;
    *) usage ;;
  esac
done

[[ -z "$TASK_ID" ]] && usage

ROOT_DIR=$(resolve_repo_root "${ROOT_DIR:-}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}

python3 -c "
import os, sys
sys.path.insert(0, os.path.join('$ROOT_DIR', 'scripts/core'))
from _lib.telemetry_store import count_open
print(count_open('$ROOT_DIR', '$TASK_ID', '${FEATURE_SLUG:-}' or None))
"

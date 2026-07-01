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

TELEMETRY_FILE="$ROOT_DIR/core-zero/memories/repo/harness-telemetry.jsonl"
[[ -f "$TELEMETRY_FILE" ]] || { echo "0"; exit 0; }

python3 -c "
import json, sys

fn = '$TELEMETRY_FILE'
task_id = '$TASK_ID'
feature_slug = '${FEATURE_SLUG:-}'
count = 0

with open(fn) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            if rec.get('task') == task_id and rec.get('status') == 'open':
                if not feature_slug or rec.get('feature') == feature_slug:
                    count += 1
        except json.JSONDecodeError:
            pass

print(count)
"

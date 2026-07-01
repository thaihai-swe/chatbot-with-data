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
import json, os, sys

fn = '$TELEMETRY_FILE'
rid = '$RECORD_ID'
new_status = '${STATUS:-}' or None
new_fix = '${FIX_APPLIED:-}' or None
found = False
lines = []

with open(fn) as f:
    for line in f:
        line = line.rstrip('\n')
        if not line.strip():
            lines.append('')
            continue
        try:
            rec = json.loads(line)
            if rec.get('id') == rid:
                found = True
                rec['status'] = new_status or rec.get('status', 'open')
                if new_fix is not None:
                    rec['fix_applied'] = new_fix
                lines.append(json.dumps(rec, ensure_ascii=False))
            else:
                lines.append(line)
        except json.JSONDecodeError:
            lines.append(line)

if not found:
    print(f'ERROR: no record with id {rid}', file=sys.stderr)
    sys.exit(1)

with open(fn, 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f'Updated {rid}: status={new_status or \"unchanged\"} fix_applied={\"updated\" if new_fix is not None else \"unchanged\"}')
"

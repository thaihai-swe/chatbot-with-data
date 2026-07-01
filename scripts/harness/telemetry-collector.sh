#!/usr/bin/env bash
# telemetry-collector.sh — append JSONL telemetry record
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

ROOT_DIR=""
ERROR_MSG=""
TASK_ID=""
FEATURE_SLUG=""
CLASSIFICATION=""
SKILL_NAME=""
ROOT_CAUSE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)     ROOT_DIR="$2"; shift 2 ;;
    --task)     TASK_ID="$2"; shift 2 ;;
    --feature)  FEATURE_SLUG="$2"; shift 2 ;;
    --classification) CLASSIFICATION="$2"; shift 2 ;;
    --skill)    SKILL_NAME="$2"; shift 2 ;;
    --root-cause) ROOT_CAUSE="$2"; shift 2 ;;
    *)
      if [[ -z "$ERROR_MSG" ]]; then ERROR_MSG="$1"; else ERROR_MSG="$ERROR_MSG $1"; fi
      shift ;;
  esac
done

if [ ! -t 0 ] && read -t 0 -r; then
  STDIN_MSG=$(cat)
  ERROR_MSG="${ERROR_MSG:+${ERROR_MSG}$'\n'}${STDIN_MSG}"
fi

[[ -z "$ERROR_MSG" ]] && {
  echo "Usage: $0 [--root <path>] [--task <TASK-NNN>] [--feature <slug>] [--classification <class>] [--skill <skill>] [--root-cause <cause>] \"Error message\""
  echo "       or pipe output to $0"
  exit 1
}

RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-${HARNESS_REPO_ROOT:-}}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}

TELEMETRY_FILE="$RESOLVED_ROOT/core-zero/memories/repo/harness-telemetry.jsonl"
mkdir -p "$(dirname "$TELEMETRY_FILE")"

NEXT_ID=$(python3 -c "
import json, os, re
fn = os.path.expanduser('$TELEMETRY_FILE')
ids = [0]
if os.path.isfile(fn):
    for line in open(fn):
        try:
            d = json.loads(line.strip())
            m = re.search(r'OBS-(\d+)', d.get('id',''))
            if m: ids.append(int(m.group(1)))
        except: pass
print(f'OBS-{max(ids)+1:03d}')
")

CLEAN_DESC=$(python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()[:500]))' <<< "$ERROR_MSG")

python3 -c "
import json, os
entry = {
    'id': '$NEXT_ID',
    'date': '$(date +%Y-%m-%d)',
    'classification': '${CLASSIFICATION:-unknown}',
    'severity': 'medium',
    'skill': '${SKILL_NAME:-unknown}',
    'task': '${TASK_ID:-unknown}',
    'feature': '${FEATURE_SLUG:-unknown}',
    'description': $CLEAN_DESC,
    'root_cause': '${ROOT_CAUSE:-unknown}',
    'fix_applied': 'none yet',
    'recurrence_risk': 'medium',
    'promotion_candidate': False,
    'status': 'open',
    'timestamp': '$(date +%Y-%m-%dT%H:%M:%S)'
}
with open('$TELEMETRY_FILE', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
"

echo "=> Telemetry logged as $NEXT_ID -> $TELEMETRY_FILE"

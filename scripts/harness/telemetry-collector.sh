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
SEVERITY="medium"
RECURRENCE_RISK="medium"
SKILL_NAME=""
ROOT_CAUSE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)              ROOT_DIR="$2"; shift 2 ;;
    --task)              TASK_ID="$2"; shift 2 ;;
    --feature)           FEATURE_SLUG="$2"; shift 2 ;;
    --classification)    CLASSIFICATION="$2"; shift 2 ;;
    --severity)          SEVERITY="$2"; shift 2 ;;
    --recurrence-risk)   RECURRENCE_RISK="$2"; shift 2 ;;
    --skill)             SKILL_NAME="$2"; shift 2 ;;
    --root-cause)        ROOT_CAUSE="$2"; shift 2 ;;
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
  echo "Usage: $0 [--root <path>] [--task <TASK-NNN>] [--feature <slug>] [--classification <class>] [--severity <level>] [--recurrence-risk <level>] [--skill <skill>] [--root-cause <cause>] \"Error message\""
  echo "       or pipe output to $0"
  exit 1
}

RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-${HARNESS_REPO_ROOT:-}}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}

CLEAN_DESC=$(python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()[:500]))' <<< "$ERROR_MSG")

python3 -c "
import os, sys, json
sys.path.insert(0, os.path.join(sys.argv[1], 'scripts/core'))
from _lib.telemetry_store import append_record
root, task, feature, classification, desc, severity, risk, skill, cause = sys.argv[1:10]
append_record(
    root, task, feature, classification, json.loads(desc),
    severity=severity, recurrence_risk=risk,
    skill=skill or None, root_cause=cause or None,
)
" "$RESOLVED_ROOT" "$TASK_ID" "$FEATURE_SLUG" "$CLASSIFICATION" "$CLEAN_DESC" "$SEVERITY" "$RECURRENCE_RISK" "$SKILL_NAME" "$ROOT_CAUSE"

echo "=> Telemetry logged for $TASK_ID/$FEATURE_SLUG"

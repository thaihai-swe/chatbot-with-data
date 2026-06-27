#!/usr/bin/env bash
# gate-runner.sh — thin wrapper around harness.py (subcommand: gates)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TELEMETRY_SCRIPT="$SCRIPT_DIR/telemetry-collector.sh"

TASK_ID=""
FEATURE_SLUG=""
ROOT_DIR=""
DRY_RUN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task) TASK_ID="$2"; shift 2 ;;
    --feature) FEATURE_SLUG="$2"; shift 2 ;;
    --root) ROOT_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN="--dry-run"; shift ;;
    *) shift ;;
  esac
done

source "$SCRIPT_DIR/_lib/root.sh"
RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}
RESOLVED_ROOT="$(cd "$RESOLVED_ROOT" && pwd)"

cd "$RESOLVED_ROOT"

if [ -f "./scripts/harness/gate-runner.local.sh" ]; then
  echo "=> Using project-local gate-runner override."
  bash "./scripts/harness/gate-runner.local.sh"; exit $?
fi

PYTHON_ENGINE="$SCRIPT_DIR/../core/harness.py"

if ! OUTPUT=$(python3 "$PYTHON_ENGINE" --config "$RESOLVED_ROOT/docs/project/harness-config.yaml" --root "$RESOLVED_ROOT" $DRY_RUN gates 2>&1); then
  echo "$OUTPUT"
  if [ -n "$FEATURE_SLUG" ]; then
    python3 "$PYTHON_ENGINE" --root "$RESOLVED_ROOT" lifecycle --action record-failure --feature "$FEATURE_SLUG" --gate "$TASK_ID" 2>/dev/null || true
  fi
  if [ -x "$TELEMETRY_SCRIPT" ]; then
    tmpargs=()
    [[ -n "$TASK_ID" ]] && tmpargs+=(--task "$TASK_ID")
    [[ -n "$FEATURE_SLUG" ]] && tmpargs+=(--feature "$FEATURE_SLUG")
    echo "$OUTPUT" | "$TELEMETRY_SCRIPT" "${tmpargs[@]}"
  fi
  exit 1
fi

echo "$OUTPUT"
if [ -n "$FEATURE_SLUG" ]; then
  python3 "$PYTHON_ENGINE" --root "$RESOLVED_ROOT" lifecycle --action record-success --feature "$FEATURE_SLUG" 2>/dev/null || true
fi
exit 0

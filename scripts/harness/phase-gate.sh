#!/usr/bin/env bash
# phase-gate.sh — thin wrapper around harness.py (subcommand: phase-gate)

set -euo pipefail

ROOT_DIR=""
DRY_RUN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN="--dry-run"; shift ;;
    *) break ;;
  esac
done

FEATURE_SLUG="${1:-}"
TARGET_PHASE="${2:-}"

if [[ -z "$FEATURE_SLUG" || -z "$TARGET_PHASE" ]]; then
  echo "usage: phase-gate.sh [--root <path>] [--dry-run] <feature-slug> <target-phase>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"
RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}
RESOLVED_ROOT="$(cd "$RESOLVED_ROOT" && pwd)"

PYTHON_ENGINE="$SCRIPT_DIR/../core/harness.py"

exec python3 "$PYTHON_ENGINE" --config "$RESOLVED_ROOT/docs/project/harness-config.yaml" --root "$RESOLVED_ROOT" $DRY_RUN phase-gate --phase "$TARGET_PHASE" --feature "$FEATURE_SLUG"

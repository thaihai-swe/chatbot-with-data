#!/usr/bin/env bash
# harness-lifecycle.sh — thin wrapper around harness.py (subcommand: lifecycle)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR=""
DRY_RUN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN="--dry-run"; shift ;;
    *) break ;;
  esac
done

ACTION="${1:-}"
PHASE="${2:-}"
FEATURE="${3:-}"

if [[ -z "$ACTION" ]]; then
  echo "usage: harness-lifecycle.sh [--root <path>] [--dry-run] <transition|state> [phase] [feature]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"
RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}
RESOLVED_ROOT="$(cd "$RESOLVED_ROOT" && pwd)"

PYTHON_ENGINE="$SCRIPT_DIR/../core/harness.py"

ARGS=(--config "$RESOLVED_ROOT/docs/project/harness-config.yaml" --root "$RESOLVED_ROOT")
[[ -n "$DRY_RUN" ]] && ARGS+=("$DRY_RUN")
ARGS+=(lifecycle --action "$ACTION")
[[ -n "$PHASE" ]] && ARGS+=(--phase "$PHASE")
[[ -n "$FEATURE" ]] && ARGS+=(--feature "$FEATURE")

exec python3 "$PYTHON_ENGINE" "${ARGS[@]}"

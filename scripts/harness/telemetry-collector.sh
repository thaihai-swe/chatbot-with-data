#!/usr/bin/env bash
# telemetry-collector.sh
# Collects errors from the execution environment and logs them into harness-telemetry.md.

set -euo pipefail

ROOT_DIR=""
ERROR_MSG=""

# Parse options
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      if [[ $# -gt 1 ]]; then
        ROOT_DIR="$2"
        shift 2
      else
        echo "ERROR: --root requires an argument" >&2
        exit 1
      fi
      ;;
    *)
      if [[ -z "$ERROR_MSG" ]]; then
        ERROR_MSG="$1"
      else
        ERROR_MSG="$ERROR_MSG $1"
      fi
      shift
      ;;
  esac
done

if [ ! -t 0 ] && read -t 0 -r; then
  STDIN_MSG=$(cat)
  if [[ -n "$ERROR_MSG" ]]; then
    ERROR_MSG="${ERROR_MSG}
${STDIN_MSG}"
  else
    ERROR_MSG="$STDIN_MSG"
  fi
fi

if [[ -z "$ERROR_MSG" ]]; then
  echo "Usage: $0 [--root <path>] \"Error message or log snippet\""
  echo "       or pipe output to $0"
  exit 1
fi

# Resolve root directory
if [[ -n "$ROOT_DIR" ]]; then
  RESOLVED_ROOT="$ROOT_DIR"
elif [[ -n "${HARNESS_REPO_ROOT:-}" ]]; then
  RESOLVED_ROOT="$HARNESS_REPO_ROOT"
else
  # Walk upward from $PWD
  CURRENT_DIR="$PWD"
  RESOLVED_ROOT=""
  while [[ "$CURRENT_DIR" != "/" && -n "$CURRENT_DIR" ]]; do
    if [[ -f "$CURRENT_DIR/AGENTS.md" && -d "$CURRENT_DIR/memories/repo" ]]; then
      RESOLVED_ROOT="$CURRENT_DIR"
      break
    fi
    PARENT_DIR="$(dirname "$CURRENT_DIR")"
    if [[ "$PARENT_DIR" == "$CURRENT_DIR" ]]; then
      break
    fi
    CURRENT_DIR="$PARENT_DIR"
  done
  if [[ -z "$RESOLVED_ROOT" ]]; then
    # Fallback to local check if we reached root or are stuck
    if [[ -f "$PWD/AGENTS.md" && -d "$PWD/memories/repo" ]]; then
      RESOLVED_ROOT="$PWD"
    else
      echo "ERROR: Could not resolve repository root. Walked up to / but did not find AGENTS.md and memories/repo/." >&2
      exit 1
    fi
  fi
fi

TELEMETRY_FILE="$RESOLVED_ROOT/memories/repo/harness-telemetry.md"

# Ensure target directory exists
mkdir -p "$(dirname "$TELEMETRY_FILE")"

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create the file if it doesn't exist
if [ ! -f "$TELEMETRY_FILE" ]; then
    echo "# Harness Telemetry" > "$TELEMETRY_FILE"
    echo "Logs of mechanical and behavioral gate failures for diagnostic analysis." >> "$TELEMETRY_FILE"
    echo "" >> "$TELEMETRY_FILE"
fi

# Append the new log entry
NEXT_ID=$(grep -c "id: OBS-" "$TELEMETRY_FILE" 2>/dev/null || echo 0)
NEXT_ID=$(printf "OBS-%03d" $((NEXT_ID + 1)))
CLEAN_DESC=$(echo "$ERROR_MSG" | head -n 1 | tr -d '"' | tr -d "'" | cut -c 1-120)

cat >> "$TELEMETRY_FILE" << EOF

\`\`\`yaml
- id: ${NEXT_ID}
  date: $(date +"%Y-%m-%d")
  classification: "[UNKNOWN: harness | model | spec]"
  severity: medium
  skill: "[UNKNOWN: <active-skill>]"
  description: "${CLEAN_DESC}"
  root_cause: "[UNKNOWN]"
  fix_applied: "none yet"
  recurrence_risk: medium
  promotion_candidate: false
  status: open
\`\`\`
EOF

echo "=> Telemetry logged to $TELEMETRY_FILE"

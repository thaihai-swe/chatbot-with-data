#!/usr/bin/env bash
# telemetry-insights.sh — CoreZero telemetry pattern analyser
# Overwrite file (shipped via kit/manifest.json overwrite array).
# Reads harness-telemetry.jsonl and outputs a summary of:
#   - Top recurring failure types
#   - High-risk open entries
#   - Stale open entries (>7 days)
# Exits 0 always (informational — does not block the harness).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

KIT_ROOT=$(resolve_repo_root) || {
  echo "FAIL: Could not resolve kit root"
  exit 1
}

TELEMETRY_JSONL="$KIT_ROOT/core-zero/memories/repo/harness-telemetry.jsonl"

if [[ ! -f "$TELEMETRY_JSONL" ]]; then
  echo "[telemetry-insights] No harness-telemetry.jsonl found — skipping."
  exit 0
fi

JSON_MODE=false
for arg in "$@"; do
  if [[ "$arg" == "--json" ]]; then
    JSON_MODE=true
  fi
done

if [[ "$JSON_MODE" == "false" ]]; then
  echo "=== Telemetry Insights ==="
  echo ""
fi

python3 - "$KIT_ROOT" "$JSON_MODE" <<'PYEOF'
import sys, os, json
sys.path.insert(0, os.path.join(sys.argv[1], 'scripts/core'))
from _lib.telemetry_store import insights

top, high_risk, stale = insights(sys.argv[1])
json_mode = sys.argv[2] == 'true'

if json_mode:
    # Convert datetime objects to string if needed; insights return plain JSON dicts from JSONL
    print(json.dumps({
        "top_failures": top,
        "high_risk_failures": high_risk,
        "stale_failures": stale
    }, indent=2))
else:
    print("## Top Recurring Failure Types")
    if not top:
        print("  (no open failure records)")
    else:
        for ftype, count in top[:3]:
            print(f"  {count}x  {ftype}")

    print("")

    print("## Open Entries with recurrence_risk: high")
    if not high_risk:
        print("  (none)")
    else:
        for rec in high_risk:
            obs = rec.get('id', '?')
            task = rec.get('task', '?')
            print(f"  {obs}  task={task}  {rec.get('description', '')[:80]}")

    print("")

    print("## Stale Open Entries (> 7 days old)")
    if not stale:
        print("  (none)")
    else:
        for rec in stale:
            obs = rec.get('id', '?')
            task = rec.get('task', '?')
            ts = rec.get('timestamp', '')
            if ts.endswith('Z'):
                ts = ts[:-1] + '+00:00'
            from datetime import datetime, timezone
            rec_dt = datetime.fromisoformat(ts)
            age_days = (datetime.now(timezone.utc) - rec_dt).days
            print(f"  {obs}  task={task}  {age_days}d old  {rec.get('description', '')[:60]}")

    print("")
    print("=== End of Insights ===")
PYEOF

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

echo "=== Telemetry Insights ==="
echo ""

# --- Top recurring failure types (with skip count) ---
echo "## Top Recurring Failure Types"
python3 - "$TELEMETRY_JSONL" <<'PYEOF'
import sys, json, collections
path = sys.argv[1]
counts = collections.Counter()
skipped = 0
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if rec.get("status", "open") != "open":
            continue
        ftype = rec.get("failure_type") or rec.get("category") or "unknown"
        counts[ftype] += 1
if skipped:
    print(f"  ({skipped} malformed records skipped)")
if not counts:
    print("  (no open failure records)")
else:
    for ftype, count in counts.most_common(3):
        print(f"  {count}x  {ftype}")
PYEOF

echo ""

# --- High recurrence-risk entries ---
echo "## Open Entries with recurrence_risk: high"
python3 - "$TELEMETRY_JSONL" <<'PYEOF'
import sys, json
path = sys.argv[1]
found = False
skipped = 0
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if rec.get("status", "open") != "open":
            continue
        if rec.get("recurrence_risk", "").lower() == "high":
            obs = rec.get("id") or rec.get("obs_id") or "?"
            task = rec.get("task") or rec.get("task_id") or "?"
            print(f"  {obs}  task={task}  {rec.get('description','')[:80]}")
            found = True
if skipped:
    print(f"  ({skipped} malformed records skipped)")
if not found:
    print("  (none)")
PYEOF

echo ""

# --- Stale open entries (>7 days) ---
echo "## Stale Open Entries (> 7 days old)"
python3 - "$TELEMETRY_JSONL" <<'PYEOF'
import sys, json
from datetime import datetime, timezone, timedelta
path = sys.argv[1]
cutoff = datetime.now(timezone.utc) - timedelta(days=7)
found = False
skipped = 0
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if rec.get("status", "open") != "open":
            continue
        ts_raw = rec.get("timestamp") or rec.get("created_at") or ""
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts < cutoff:
            obs = rec.get("id") or rec.get("obs_id") or "?"
            task = rec.get("task") or rec.get("task_id") or "?"
            age_days = (datetime.now(timezone.utc) - ts).days
            print(f"  {obs}  task={task}  {age_days}d old  {rec.get('description','')[:60]}")
            found = True
if skipped:
    print(f"  ({skipped} malformed records skipped)")
if not found:
    print("  (none)")
PYEOF

echo ""
echo "=== End of Insights ==="

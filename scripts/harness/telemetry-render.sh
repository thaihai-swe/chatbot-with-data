#!/usr/bin/env bash
# telemetry-render.sh — regenerate harness-telemetry.md from JSONL records
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

ROOT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT_DIR="$2"; shift 2 ;;
    *) echo "Usage: $0 [--root <path>]"; exit 1 ;;
  esac
done

RESOLVED_ROOT=$(resolve_repo_root "${ROOT_DIR:-${HARNESS_REPO_ROOT:-}}") || {
  echo "ERROR: Could not resolve repository root." >&2; exit 1
}

JSONL_FILE="$RESOLVED_ROOT/memories/repo/harness-telemetry.jsonl"
MD_FILE="$RESOLVED_ROOT/memories/repo/harness-telemetry.md"

if [[ ! -f "$JSONL_FILE" ]]; then
  echo "# Harness Telemetry" > "$MD_FILE"
  echo "No records yet." >> "$MD_FILE"
  echo "Rendered empty report to $MD_FILE"
  exit 0
fi

JSONL_FILE="$JSONL_FILE" MD_FILE="$MD_FILE" python3 << 'PYEOF'
import json, os

jsonl_fn = os.environ['JSONL_FILE']
md_fn = os.environ['MD_FILE']

records = []
with open(jsonl_fn) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass

if not records:
    with open(md_fn, 'w') as md:
        md.write('# Harness Telemetry\n\n')
        md.write('No records yet.\n')
    print('Rendered empty report to', md_fn)
else:
    with open(md_fn, 'w') as md:
        md.write('# Harness Telemetry\n\n')
        md.write('> Auto-generated from `harness-telemetry.jsonl` by `telemetry-render.sh`.\n\n')

        total = len(records)
        open_count = sum(1 for r in records if r.get('status') == 'open')
        closed_count = sum(1 for r in records if r.get('status') == 'closed')

        md.write(f'**Total:** {total} &nbsp;|&nbsp; **Open:** {open_count} &nbsp;|&nbsp; **Closed:** {closed_count}\n\n')
        md.write('| ID | Date | Task | Feature | Classification | Status | Description |\n')
        md.write('|---|---|---|---|---|---|---|\n')

        for r in reversed(records):
            rec_id = r.get('id', '???')
            date = r.get('date', '')
            task = r.get('task', '')
            feature = r.get('feature', '')
            cls = r.get('classification', '')
            status = r.get('status', '')
            desc = r.get('description', '')
            if isinstance(desc, str):
                desc = desc.replace('|', '/')[:80]
            md.write(f'| {rec_id} | {date} | {task} | {feature} | {cls} | {status} | {desc} |\n')

        md.write('\n## Detailed Records\n\n')
        for r in reversed(records):
            parts = []
            parts.append('```yaml')
            parts.append(f'- id: {r.get("id","???")}')
            parts.append(f'  date: {r.get("date","")}')
            parts.append(f'  classification: "{r.get("classification","")}"')
            parts.append(f'  severity: {r.get("severity","medium")}')
            parts.append(f'  skill: "{r.get("skill","")}"')
            parts.append(f'  task: "{r.get("task","")}"')
            parts.append(f'  feature: "{r.get("feature","")}"')
            parts.append(f'  description: {json.dumps(r.get("description",""), ensure_ascii=False)}')
            parts.append(f'  root_cause: "{r.get("root_cause","")}"')
            parts.append(f'  fix_applied: "{r.get("fix_applied","")}"')
            parts.append(f'  recurrence_risk: {r.get("recurrence_risk","medium")}')
            parts.append(f'  promotion_candidate: {str(r.get("promotion_candidate",False)).lower()}')
            parts.append(f'  status: {r.get("status","")}')
            parts.append('```')
            md.write('\n'.join(parts) + '\n\n')

    print(f'Rendered {total} records to', md_fn)
PYEOF

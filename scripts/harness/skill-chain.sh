#!/usr/bin/env bash
# skill-chain.sh — Read next_skill from SKILL.md frontmatter, suggest the next command.
# Overwrite file (shipped via kit/manifest.json overwrite array).
#
# Usage:
#   bash scripts/harness/skill-chain.sh <skill-slug>            # print next skill slug(s)
#   bash scripts/harness/skill-chain.sh <skill-slug> --suggest  # print full suggested command
#   bash scripts/harness/skill-chain.sh <skill-slug> --walk     # multi-hop walk; exit 1 on cycle
#   bash scripts/harness/skill-chain.sh --list                  # print the full chain map
#
# Examples:
#   bash scripts/harness/skill-chain.sh spec-implement
#   bash scripts/harness/skill-chain.sh starter-init --walk

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

KIT_ROOT=$(resolve_repo_root) || {
  echo "FAIL: Could not resolve kit root" >&2
  exit 1
}

parse_next() {
  # $1 = path to SKILL.md — print one next_skill per line
  python3 - "$1" <<'PYEOF'
import re, sys
with open(sys.argv[1]) as f:
    content = f.read()
m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
if not m:
    sys.exit(0)
for line in m.group(1).split('\n'):
    if line.strip().startswith('next_skill:'):
        val = line.split(':', 1)[1].strip().strip("'\"").strip()
        if not val:
            break
        if val.startswith('[') and val.endswith(']'):
            for s in [x.strip().strip("'\"") for x in val[1:-1].split(',') if x.strip()]:
                print(s)
        else:
            print(val)
        break
PYEOF
}

parse_context_load() {
  # $1 = path to SKILL.md — print the context_load command if present
  python3 - "$1" <<'PYEOF'
import re, sys
with open(sys.argv[1]) as f:
    content = f.read()
m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
if not m:
    sys.exit(0)
for line in m.group(1).split('\n'):
    if line.strip().startswith('context_load:'):
        val = line.split(':', 1)[1].strip().strip("'\"").strip()
        print(val)
        break
PYEOF
}

# --list flag: show full chain map
if [[ "${1:-}" == "--list" ]]; then
  echo "# Skill Chain Map"
  echo ""
  for skill_dir in "$KIT_ROOT"/skills/*/; do
    slug=$(basename "$skill_dir")
    md="$skill_dir/SKILL.md"
    if [[ ! -f "$md" ]]; then
      continue
    fi
    next=$(parse_next "$md" | paste -sd ',' -)
    next=${next:-'(terminal)'}
    printf "  %-30s → %s\n" "$slug" "$next"
  done
  exit 0
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") <skill-slug> [--suggest | --walk | --list]"
  echo "Example: $(basename "$0") spec-implement --suggest"
  exit 1
fi

SKILL_SLUG="$1"
MODE="${2:-}"
SKILL_MD="$KIT_ROOT/skills/$SKILL_SLUG/SKILL.md"

if [[ ! -f "$SKILL_MD" ]]; then
  echo "FAIL: SKILL.md not found — skills/$SKILL_SLUG/SKILL.md" >&2
  exit 1
fi

if [[ "$MODE" == "--walk" ]]; then
  # Multi-hop walk; first next_skill only per hop (list form: take first). Cycle → exit 1.
  current="$SKILL_SLUG"
  seen="$current"
  path="$current"
  while true; do
    md="$KIT_ROOT/skills/$current/SKILL.md"
    if [[ ! -f "$md" ]]; then
      echo "FAIL: broken chain at '$current' (missing SKILL.md)" >&2
      exit 1
    fi
    next=$(parse_next "$md" | head -n1)
    if [[ -z "$next" ]]; then
      echo "$path → (terminal)"
      exit 0
    fi
    case " $seen " in
      *" $next "*)
        echo "FAIL: cycle detected: $path → $next" >&2
        exit 1
        ;;
    esac
    path="$path → $next"
    seen="$seen $next"
    current="$next"
  done
fi

# Detect active feature slug to locate handoff and session files (EL-003)
ACTIVE_STATUS=$(find "$KIT_ROOT/artifacts/features" -name "status.md" -mtime -1 2>/dev/null | head -n1 || true)
FEATURE_SLUG=""
if [[ -n "$ACTIVE_STATUS" ]]; then
  FEATURE_SLUG=$(basename "$(dirname "$ACTIVE_STATUS")")
fi

if [[ -n "$FEATURE_SLUG" ]]; then
  HANDOFF_FILE="$KIT_ROOT/artifacts/features/$FEATURE_SLUG/handoff.md"
  SESSION_FILE="$KIT_ROOT/.corezero/sessions/$FEATURE_SLUG/session.md"
  if [[ -f "$HANDOFF_FILE" && -f "$SESSION_FILE" ]]; then
    # Only append if not already appended in the last 5 lines
    if ! tail -n 5 "$SESSION_FILE" 2>/dev/null | grep -q "Handoff read: ✓"; then
      echo "" >> "$SESSION_FILE"
      echo "- Handoff read: ✓ ($(date '+%Y-%m-%d %H:%M:%S'))" >> "$SESSION_FILE"
    fi
  fi
fi

# EL-001: emit context_load command as the first line of output
context_load_cmd=$(parse_context_load "$SKILL_MD")
if [[ -n "$context_load_cmd" ]]; then
  echo "$context_load_cmd"
fi

next_skills=$(parse_next "$SKILL_MD")

# EM-001: check if any memory file exceeds breach lines and inject context-compact into next_skills
if [[ "$SKILL_SLUG" == "spec-implement" ]]; then
  BREACH_DETECTED=$(python3 -c "
import os, sys, re
root = '$KIT_ROOT'
cfg_path = os.path.join(root, 'core-zero/project/harness-config.yaml')
breach_lines = 200
if os.path.exists(cfg_path):
    try:
        text = open(cfg_path).read()
        m = re.search(r'memory_breach_lines:\s*(\d+)', text)
        if m:
            breach_lines = int(m.group(1))
    except Exception:
        pass
memory_files = [
    'core-zero/memories/repo/core-policies.md',
    'core-zero/memories/repo/learned-heuristics.md',
    'core-zero/memories/repo/project-knowledge-base.md',
    'core-zero/memories/repo/harness-config.md',
    'core-zero/memories/repo/adr-log.md',
]
breached = False
for f in memory_files:
    p = os.path.join(root, f)
    if os.path.exists(p):
        lines = len(open(p, errors='replace').readlines())
        if lines > breach_lines:
            breached = True
            break
if breached:
    print('yes')
else:
    print('no')
")
  if [[ "$BREACH_DETECTED" == "yes" ]]; then
    next_skills="context-compact"
  fi
fi

if [[ -z "$next_skills" ]]; then
  echo "(terminal — no next skill)" >&2
  exit 0
fi

if [[ "$MODE" == "--suggest" ]]; then
  while IFS= read -r skill; do
    echo "Suggested next command: /$skill"
  done <<< "$next_skills"
else
  echo "$next_skills"
fi

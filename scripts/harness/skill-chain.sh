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

next_skills=$(parse_next "$SKILL_MD")

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

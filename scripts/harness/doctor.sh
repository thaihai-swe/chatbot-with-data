#!/usr/bin/env bash
# doctor.sh — CoreZero kit self-diagnosis
# Checks internal consistency of the installed kit surface.
# Exits 0 if all checks pass, 1 with specific failures otherwise.
# Intended to run after install.sh and on-demand by harness-maintain.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

KIT_ROOT=$(resolve_repo_root) || {
  echo "FAIL: Could not resolve kit root (no AGENTS.md + memories/repo/)"
  exit 1
}

errors=0
warn()  { echo "  WARN: $*"; }
fail()  { echo "  FAIL: $*"; errors=$((errors + 1)); }
pass()  { echo "  PASS: $*"; }

echo "CoreZero doctor — $KIT_ROOT"
echo ""

# --- Check 2: Sections referenced by SKILL.md exist ---
echo "--- Check 2: Referenced sections exist ---"

# ## Security Policy in core-policies.md
if grep -q "^## Security Policy" "$KIT_ROOT/memories/repo/core-policies.md" 2>/dev/null; then
  pass "core-policies.md has ## Security Policy"
else
  fail "core-policies.md missing ## Security Policy"
fi

# # Harness Config in harness-config.md
if grep -q "^# Harness Config" "$KIT_ROOT/memories/repo/harness-config.md" 2>/dev/null; then
  pass "harness-config.md has # Harness Config"
else
  fail "harness-config.md missing # Harness Config"
fi

# ## Promotion Watchlist in MASTER_INDEX.md
if grep -q "^## 5. Promotion Watchlist" "$KIT_ROOT/MASTER_INDEX.md" 2>/dev/null; then
  pass "MASTER_INDEX.md has ## Promotion Watchlist"
else
  fail "MASTER_INDEX.md missing ## Promotion Watchlist"
fi

# ## Memory Tiers in context-memory/SKILL.md
if grep -q "## Memory Tiers" "$KIT_ROOT/skills/context-memory/SKILL.md" 2>/dev/null; then
  pass "context-memory/SKILL.md has ## Memory Tiers"
else
  warn "context-memory/SKILL.md missing ## Memory Tiers (will be added in Pass 3)"
fi

# --- Check 3: No kit/-prefixed paths in installed SKILL.md files ---
echo "--- Check 3: No kit/-prefixed paths in skills ---"
KIT_PREFIX_HITS=$(grep -rn '"kit/' "$KIT_ROOT/skills/" 2>/dev/null || true)
if [[ -z "$KIT_PREFIX_HITS" ]]; then
  pass "No kit/-prefixed paths in skills/"
else
  fail "Found kit/-prefixed paths in skills/ (should be stripped for flat install):"
  echo "$KIT_PREFIX_HITS"
fi

# --- Check 4: MASTER_INDEX.md routes point to existing files ---
echo "--- Check 4: MASTER_INDEX.md routes exist ---"
# Check specific files referenced in MASTER_INDEX.md
for f in \
  "memories/repo/core-policies.md" \
  "memories/repo/harness-config.md" \
  "memories/repo/project-knowledge-base.md" \
  "memories/repo/adr-log.md" \
  "memories/repo/learned-heuristics.md" \
  "memories/repo/harness-telemetry.md" \
  "core-zero/rules/security.md" \
  "core-zero/rules/ponytail.md" \
  "core-zero/policies/code-design.md" \
  "core-zero/index.html" \
  "skills/README.md" \
  "scripts/install.sh" \
  "scripts/harness/gate-runner.sh" \
  "scripts/harness/telemetry-collector.sh"; do
  [[ -f "$KIT_ROOT/$f" ]] || fail "MASTER_INDEX.md route missing: $f"
done


# --- Check 5: Threshold consistency (600/800/1200) ---
echo "--- Check 5: Threshold consistency ---"
check_threshold() {
  local file="$1" val="$2"
  if grep -q "$val" "$KIT_ROOT/$file" 2>/dev/null; then
    return 0
  fi
  return 1
}
# Just check core-policies.md has the canonical thresholds
if grep -q "Memory Promotion Thresholds" "$KIT_ROOT/memories/repo/core-policies.md" && grep -qE "800.1199" "$KIT_ROOT/memories/repo/core-policies.md"; then
  pass "core-policies.md has canonical thresholds table"
else
  fail "core-policies.md missing canonical thresholds"
fi

# --- Check 6: Task ID grammar is TASK-NNN ---
echo "--- Check 6: Task ID grammar (no T-01/T-NN in SKILL.md) ---"
T01_HITS=$(grep -rnE "\bT-[0-9]+\b|\bT-NN\b" "$KIT_ROOT/skills/" --include="SKILL.md" 2>/dev/null || true)
if [[ -z "$T01_HITS" ]]; then
  pass "No T-01/T-NN in SKILL.md files"
else
  fail "Found non-standard task IDs in SKILL.md files:"
  echo "$T01_HITS"
fi

# --- Check 7: ADR status vocabulary is unified ---
echo "--- Check 7: ADR status consistency ---"
if grep -q "Rejected" "$KIT_ROOT/memories/repo/adr-log.md" 2>/dev/null; then
  fail "adr-log.md still has 'Rejected' status (should be Deprecated/Superseded)"
else
  pass "adr-log.md status vocabulary clean"
fi

# --- Check 8: Telemetry pipeline (JSONL) ---
echo "--- Check 8: Telemetry pipeline ---"
if python3 -c "
with open('$KIT_ROOT/scripts/harness/telemetry-collector.sh') as f:
    c = f.read()
assert \"'task':\" in c or '\"task\":' in c, 'telemetry-collector.sh emits task field'
assert \"'feature':\" in c or '\"feature\":' in c, 'telemetry-collector.sh emits feature field'
print('PASS: telemetry-collector.sh emits task/feature fields')
" 2>/dev/null; then
  pass "telemetry-collector.sh emits task/feature fields"
else
  fail "telemetry-collector.sh missing required fields"
fi
for f in telemetry-count.sh telemetry-update.sh telemetry-render.sh; do
  if [[ -f "$KIT_ROOT/scripts/harness/$f" ]]; then
    pass "$f exists"
  else
    fail "$f missing"
  fi
done

# --- Check 9: Version consistency ---
echo "--- Check 9: Version consistency ---"
MANIFEST_VER=$(python3 -c "import json; print(json.load(open('$KIT_ROOT/manifest.json'))['version'])" 2>/dev/null | tr -d ' \n\r')

if [[ -n "$MANIFEST_VER" ]]; then
  pass "Version: $MANIFEST_VER (kit/manifest.json)"
else
  fail "Could not read version from kit/manifest.json"
fi

# --- Check 10: Phase×Guidance Matrix section annotations exist ---
echo "--- Check 10: Phase×Guidance Matrix section annotations ---"
TMPFILE=$(mktemp /tmp/doctor-section-check.XXXXXX 2>/dev/null || mktemp -t doctor-section-check)
cat > "$TMPFILE" << 'CHKPY'
import os, re, sys

root = sys.argv[1]
text = open(os.path.join(root, 'MASTER_INDEX.md')).read()
idx = text.find('## 3. Phase \u00d7 Guidance Matrix')
if idx == -1:
    idx = text.find('Phase \u00d7 Guidance Matrix')
if idx == -1:
    sys.exit(0)

errors = 0
for line in text[idx:].split('\n'):
    s = line.strip()
    if not s.startswith('|'):
        if s:
            break
        continue
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 6:
        continue
    source = parts[1]
    if source in ('Source', '---'):
        continue
    src = source.strip()
    if '(' in src:
        src = src[:src.index('(')].strip()
    if src.startswith('`') and src.endswith('`'):
        src = src[1:-1]
    src_file = os.path.join(root, src)
    if not os.path.exists(src_file):
        for col in parts[2:6]:
            if '{' in col:
                print('  FAIL: Section annotation references missing file: ' + src)
                errors += 1
                break
        continue
    content = open(src_file).read()
    for col in parts[2:6]:
        brace_m = re.search(r'\{([^}]+)\}', col)
        if brace_m:
            for sec_part in brace_m.group(1).split(','):
                sec = sec_part.strip().lstrip('#').strip()
                if sec and '## ' + sec not in content:
                    print('  FAIL: Section "## ' + sec + '" not found in ' + src)
                    errors += 1
if errors > 0:
    sys.exit(1)
CHKPY
if python3 "$TMPFILE" "$KIT_ROOT" 2>/dev/null; then
  pass "Phase×Guidance Matrix section annotations all valid"
else
  fail "Phase×Guidance Matrix section annotations have errors"
fi
rm -f "$TMPFILE"

# --- Check 11: Executable bits assertion ---
echo "--- Check 11: Executable bits for harness scripts ---"
for f in "$KIT_ROOT"/scripts/harness/*.sh; do
  if [[ -f "$f" ]]; then
    if [[ -x "$f" ]]; then
      pass "$(basename "$f") is executable"
    else
      fail "$(basename "$f") is NOT executable"
    fi
  fi
done

# --- Summary ---
echo ""
if [[ $errors -eq 0 ]]; then
  echo "All checks passed."
  exit 0
else
  echo "$errors check(s) failed."
  exit 1
fi

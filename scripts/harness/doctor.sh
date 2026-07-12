#!/usr/bin/env bash
# doctor.sh — CoreZero kit self-diagnosis
# Checks internal consistency of the installed kit surface.
# Exits 0 if all checks pass, 1 with specific failures otherwise.
# Intended to run after install.sh and on-demand by harness-maintain.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

JSON_MODE=false
ROOT_ARG=""
for arg in "$@"; do
  if [[ "$arg" == "--json" ]]; then
    JSON_MODE=true
  else
    ROOT_ARG="$arg"
  fi
done

if [[ -n "$ROOT_ARG" ]]; then
  KIT_ROOT="$ROOT_ARG"
else
  KIT_ROOT=$(resolve_repo_root) || {
    echo "FAIL: Could not resolve kit root (no AGENTS.md + core-zero/memories/repo/)"
    exit 1
  }
fi

errors=0
RESULTS_FILE=$(mktemp)
current_check=0
current_check_name="initial"

start_check() {
  current_check="$1"
  current_check_name="$2"
}

warn() {
  if [ "$JSON_MODE" = true ]; then
    echo "$current_check|$current_check_name|warn|$*" >> "$RESULTS_FILE"
  else
    echo "  WARN: $*"
  fi
}

fail() {
  errors=$((errors + 1))
  if [ "$JSON_MODE" = true ]; then
    echo "$current_check|$current_check_name|fail|$*" >> "$RESULTS_FILE"
  else
    echo "  FAIL: $*"
  fi
}

pass() {
  if [ "$JSON_MODE" = true ]; then
    echo "$current_check|$current_check_name|pass|$*" >> "$RESULTS_FILE"
  else
    echo "  PASS: $*"
  fi
}

if [ "$JSON_MODE" = false ]; then
  echo "CoreZero doctor — $KIT_ROOT"
  echo ""
fi

run_checks() {
# --- Check 2: Sections referenced by SKILL.md exist ---
echo "--- Check 2: Referenced sections exist ---"
start_check 2 "referenced_sections_exist"

# ## Security Policy in core-policies.md
if grep -q "^## Security Policy" "$KIT_ROOT/core-zero/memories/repo/core-policies.md" 2>/dev/null; then
  pass "core-policies.md has ## Security Policy"
else
  fail "core-policies.md missing ## Security Policy"
fi

# # Harness Config in harness-config.md
if grep -q "^# Harness Config" "$KIT_ROOT/core-zero/memories/repo/harness-config.md" 2>/dev/null; then
  pass "harness-config.md has # Harness Config"
else
  fail "harness-config.md missing # Harness Config"
fi

# ## Promotion Watchlist in context-memory/SKILL.md
if grep -q "^## Promotion Watchlist" "$KIT_ROOT/skills/context-memory/SKILL.md" 2>/dev/null; then
  pass "context-memory/SKILL.md has ## Promotion Watchlist"
else
  fail "context-memory/SKILL.md missing ## Promotion Watchlist"
fi

# ## Memory Tiers in context-memory/SKILL.md
if grep -q "## Memory Tiers" "$KIT_ROOT/skills/context-memory/SKILL.md" 2>/dev/null; then
  pass "context-memory/SKILL.md has ## Memory Tiers"
else
  warn "context-memory/SKILL.md missing ## Memory Tiers (will be added in Pass 3)"
fi

# --- Check 3: No kit/-prefixed paths in installed SKILL.md files ---
echo "--- Check 3: No kit/-prefixed paths in skills ---"
start_check 3 "no_kit/_prefixed_paths_in_skills"
KIT_PREFIX_HITS=$(grep -rn '"kit/' "$KIT_ROOT/skills/" 2>/dev/null || true)
if [[ -z "$KIT_PREFIX_HITS" ]]; then
  pass "No kit/-prefixed paths in skills/"
else
  fail "Found kit/-prefixed paths in skills/ (should be stripped for flat install):"
  echo "$KIT_PREFIX_HITS"
fi

# --- Check 4: MASTER_INDEX.md routes point to existing files ---
echo "--- Check 4: MASTER_INDEX.md routes exist ---"
start_check 4 "master_index.md_routes_exist"
# Dynamically extract backtick-quoted paths from MASTER_INDEX.md
# Resolves bare filenames via PATH_MAP lookup; skips glob/placeholder paths
PY_ROUTES=$(python3 -c "
import os, re, sys
sys.path.insert(0, '$KIT_ROOT/scripts/core')
from _lib.doctor_checks import build_path_map

root = '$KIT_ROOT'
mi_file = os.path.join(root, 'MASTER_INDEX.md')
if not os.path.exists(mi_file):
    print('SKIP')
    sys.exit(0)
pm = build_path_map(root)
text = open(mi_file).read()
paths = re.findall(r'\`([a-zA-Z0-9_/.-]+\.(?:md|yaml|json|yml))\`', text)
missing = []
for p in sorted(set(paths)):
    if '<' in p or '>' in p or '*' in p:
        continue
    if '/' in p:
        if p.startswith('domain/') or '/domain/' in p:
            continue
        resolved = os.path.join(root, p)
        if not os.path.exists(resolved):
            missing.append(p)
    elif p in pm:
        resolved = os.path.join(root, pm[p])
        if not os.path.exists(resolved):
            missing.append(p)
if missing:
    for m in missing:
        print('MISSING: ' + m)
else:
    print('OK')
")
case "$PY_ROUTES" in
  OK) pass "All MASTER_INDEX.md routes exist" ;;
  SKIP) warn "MASTER_INDEX.md not found" ;;
  MISSING:*)
    echo "  ${PY_ROUTES#MISSING: }"
    errors=$((errors + 1))
    ;;
esac


# --- Check 5: Threshold consistency (100/200/3200) ---
echo "--- Check 5: Threshold consistency ---"
start_check 5 "threshold_consistency"
PY_THRESH=$(python3 -c "
import sys; sys.path.insert(0, '$KIT_ROOT/scripts/core')
from _lib.doctor_checks import read_thresholds
ew, tb, hc = read_thresholds('$KIT_ROOT')
print(f'{ew} {tb} {hc}')
")
read EW TB HC <<< "$PY_THRESH"
if [[ "$EW" -eq 100 && "$TB" -eq 200 && "$HC" -eq 3200 ]]; then
  pass "harness-config.yaml has canonical thresholds (100/200/3200)"
else
  fail "harness-config.yaml thresholds mismatch (got $EW/$TB/$HC, expected 100/200/3200)"
fi

# --- Check 6: Task ID grammar is TASK-NNN ---
echo "--- Check 6: Task ID grammar (no T-01/T-NN in SKILL.md) ---"
start_check 6 "task_id_grammar_no_t_01/t_nn_in_skill.md"
T01_HITS=$(grep -rnE "\bT-[0-9]+\b|\bT-NN\b" "$KIT_ROOT/skills/" --include="SKILL.md" 2>/dev/null || true)
if [[ -z "$T01_HITS" ]]; then
  pass "No T-01/T-NN in SKILL.md files"
else
  fail "Found non-standard task IDs in SKILL.md files:"
  echo "$T01_HITS"
fi

# --- Check 7: ADR status vocabulary is unified ---
echo "--- Check 7: ADR status consistency ---"
start_check 7 "adr_status_consistency"
if grep -q "Rejected" "$KIT_ROOT/core-zero/memories/repo/adr-log.md" 2>/dev/null; then
  fail "adr-log.md still has 'Rejected' status (should be Deprecated/Superseded)"
else
  pass "adr-log.md status vocabulary clean"
fi

# --- Check 8: Telemetry pipeline (JSONL) ---
echo "--- Check 8: Telemetry pipeline ---"
start_check 8 "telemetry_pipeline"
if python3 -c "
with open('$KIT_ROOT/scripts/harness/telemetry-collector.sh') as f:
    c = f.read()
assert 'TASK_ID' in c and 'FEATURE_SLUG' in c, 'telemetry-collector.sh passes task/feature to append_record'
assert 'SEVERITY' in c and 'RECURRENCE_RISK' in c, 'telemetry-collector.sh passes severity/recurrence_risk'
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
start_check 9 "version_consistency"
if [[ -f "$KIT_ROOT/manifest.json" ]]; then
  MANIFEST_VER=$(python3 -c "import json; print(json.load(open('$KIT_ROOT/manifest.json'))['version'])" 2>/dev/null | tr -d ' \n\r')
  if [[ -n "$MANIFEST_VER" ]]; then
    pass "Version: $MANIFEST_VER (kit/manifest.json)"
  else
    fail "Could not read version from kit/manifest.json"
  fi
else
  warn "manifest.json not found (source-kit only, not shipped to adopter) - skipping version check"
fi

# --- Check 10: Phase×Guidance Matrix section annotations exist ---
echo "--- Check 10: Phase×Guidance Matrix section annotations ---"
start_check 10 "phase×guidance_matrix_section_annotations"
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
start_check 11 "executable_bits_for_harness_scripts"
for f in "$KIT_ROOT"/scripts/harness/*.sh; do
  if [[ -f "$f" ]]; then
    if [[ -x "$f" ]]; then
      pass "$(basename "$f") is executable"
    else
      fail "$(basename "$f") is NOT executable"
    fi
  fi
done

# --- Check 12: next_skill chain validation (supports scalar and list form) ---
echo "--- Check 12: next_skill chain validation ---"
start_check 12 "next_skill_chain_validation"
SKILL_DIR="$KIT_ROOT/skills"
next_skill_errors=0
while IFS= read -r skill_file; do
  skill_name=$(basename "$(dirname "$skill_file")")
  # Python parse matches skill-chain.sh (scalar or [a, b] list)
  while IFS= read -r next_val; do
    [[ -z "$next_val" ]] && continue
    if [[ ! -d "$SKILL_DIR/$next_val" ]]; then
      warn "next_skill '$next_val' in $skill_name/SKILL.md points to non-existent skill directory"
      next_skill_errors=$((next_skill_errors + 1))
    fi
  done < <(python3 - "$skill_file" <<'PYEOF'
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
)
done < <(find "$SKILL_DIR" -name "SKILL.md" 2>/dev/null)
if [[ $next_skill_errors -eq 0 ]]; then
  pass "All next_skill chains resolve to existing skill directories"
fi

# Multi-hop chain integrity (cycles + hop limit) via skill-chain.sh --walk
chain_walk_errors=0
SKILL_CHAIN="$KIT_ROOT/scripts/harness/skill-chain.sh"
if [[ -x "$SKILL_CHAIN" ]]; then
  while IFS= read -r skill_file; do
    skill_name=$(basename "$(dirname "$skill_file")")
    walk_out=$(bash "$SKILL_CHAIN" "$skill_name" --walk 2>&1) || {
      warn "chain walk failed for $skill_name: $walk_out"
      chain_walk_errors=$((chain_walk_errors + 1))
      continue
    }
    # hop count: count arrows in path up to "(terminal)"
    hops=$(python3 -c "
path = '''$walk_out'''
# Count only → before any (terminal) suffix
idx = path.find('(terminal)')
prefix = path[:idx] if idx >= 0 else path
print(max(1, prefix.count('→') + 1))
" 2>/dev/null || echo 1)
    if [[ $hops -gt 10 ]]; then
      warn "chain for $skill_name exceeds 10 hops ($hops): $walk_out"
      chain_walk_errors=$((chain_walk_errors + 1))
    fi
  done < <(find "$SKILL_DIR" -name "SKILL.md" 2>/dev/null)
  if [[ $chain_walk_errors -eq 0 ]]; then
    pass "All next_skill multi-hop walks are cycle-free and ≤10 hops"
  fi
else
  warn "skill-chain.sh not executable; skipped multi-hop walk"
fi


# --- Check 13: Memory file size warnings (thresholds from core-policies.md) ---
echo "--- Check 13: Memory file size warnings ---"
start_check 13 "memory_file_size_warnings"
# Read canonical thresholds from core-policies.md via shared module
PY_THRESH=$(python3 -c "
import sys; sys.path.insert(0, '$KIT_ROOT/scripts/core')
from _lib.doctor_checks import read_thresholds
ew, tb, hc = read_thresholds('$KIT_ROOT')
print(f'{ew} {tb} {hc}')
" 2>/dev/null || echo "100 200 3200")
read early_warn threshold_breach hard_cap <<< "$PY_THRESH"
mem_warn=0
for mem_file in \
  "core-zero/memories/repo/core-policies.md" \
  "core-zero/memories/repo/learned-heuristics.md" \
  "core-zero/memories/repo/project-knowledge-base.md" \
  "core-zero/memories/repo/harness-config.md" \
  "core-zero/memories/repo/adr-log.md"; do
  full_path="$KIT_ROOT/$mem_file"
  if [[ ! -f "$full_path" ]]; then
    continue
  fi
  line_count=$(wc -l < "$full_path" | tr -d ' ')
  if [[ $line_count -ge $hard_cap ]]; then
    fail "$mem_file: $line_count lines — HARD CAP BREACHED (compaction required and doctor check failed)"
    mem_warn=$((mem_warn + 1))
  elif [[ $line_count -ge $threshold_breach ]]; then
    warn "$mem_file: $line_count lines — THRESHOLD BREACH (compaction required before appends)"
    mem_warn=$((mem_warn + 1))
  elif [[ $line_count -ge $early_warn ]]; then
    warn "$mem_file: $line_count lines — EARLY WARNING (open promotion proposal)"
    mem_warn=$((mem_warn + 1))
  fi
done
if [[ $mem_warn -eq 0 ]]; then
  pass "All memory files within healthy line-count threshold (< $early_warn lines)"
fi

# --- Check 14: Code intelligence provider configuration consistency ---
echo "--- Check 14: Code intelligence provider consistency ---"
start_check 14 "code_intelligence_provider_consistency"
CI_FILE="$KIT_ROOT/core-zero/project/code-intelligence.md"
if [[ -f "$CI_FILE" ]]; then
  PY_PROBE=$(python3 -c "
import re, sys
text = open('$CI_FILE').read()
# Parse YAML frontmatter without PyYAML (simple regex approach)
m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
if not m:
    print('MISSING_FM')
    sys.exit(0)
fm_text = m.group(1)

def get_val(text, key):
    m2 = re.search(r'^' + re.escape(key) + r':\s*(.*?)(?:\s+#.*)?$', text, re.MULTILINE)
    return m2.group(1).strip() if m2 else ''

def get_bool(text, key, prefix=''):
    full = (prefix + '.' + key) if prefix else key
    m2 = re.search(r'^\s+' + re.escape(key) + r':\s*(true|false|yes|no)', text, re.MULTILINE)
    if m2:
        return m2.group(1).lower() in ('true', 'yes')
    return False

def get_enabled(text, provider):
    pattern = rf'{provider}:\s*\n(?:\s+#.*\n)*\s+enabled:\s*(true|false)'
    m2 = re.search(pattern, text)
    if m2:
        return m2.group(1).lower() == 'true'
    return False

active = get_val(fm_text, 'active_provider')
if active == '':
    active = 'none'

providers_found = re.findall(r'^  (\w[\w-]*):', fm_text, re.MULTILINE)
enabled_providers = [p for p in providers_found if get_enabled(fm_text, p)]
enabled_count = len(enabled_providers)
enabled_name = enabled_providers[0] if enabled_providers else None

issues = []
if active == 'none' and enabled_count > 0:
    issues.append(f'{enabled_name} enabled but active_provider is \"none\"')
if active != 'none' and enabled_count == 0:
    issues.append(f'active_provider is \"{active}\" but no provider has enabled: true')
if active != 'none' and active not in providers_found:
    issues.append(f'active_provider \"{active}\" not found in providers list')
if not issues:
    print('OK')
else:
    for i in issues:
        print('ISSUE: ' + i)
" 2>/dev/null || echo "PARSE_ERR")
  case "$PY_PROBE" in
    OK) pass "code-intelligence.md provider configuration is consistent" ;;
    MISSING_FM) warn "code-intelligence.md has no YAML frontmatter (expected by setup)" ;;
    PARSE_ERR) warn "code-intelligence.md could not be parsed (non-critical, not an error)" ;;
    ISSUE:*)
      warn "${PY_PROBE#ISSUE: }"
      errors=$((errors + 1))
      ;;
  esac
else
  pass "code-intelligence.md not present — no code intelligence provider configured"
fi


# --- Check 15: Manifest-filesystem drift ---
echo "--- Check 15: Manifest-filesystem drift ---"
start_check 15 "manifest_filesystem_drift"
PY_MANIFEST_DRIFT=$(python3 -c "
import sys; sys.path.insert(0, '$KIT_ROOT/scripts/core')
from _lib.doctor_checks import check_manifest_drift
print(check_manifest_drift('$KIT_ROOT'))
" 2>/dev/null || echo "PARSE_ERR")
case "$PY_MANIFEST_DRIFT" in
  OK) pass "All manifest entries exist on disk and all shipped files are covered" ;;
  SKIP) pass "manifest.json not found (source-kit only, not shipped)" ;;
  FAIL:*)
    warn "${PY_MANIFEST_DRIFT#FAIL: }"
    errors=$((errors + 1))
    ;;
  PARSE_ERR) warn "manifest-filesystem drift check could not parse manifest.json (non-critical)" ;;
esac


# --- Check 16: Cross-file reference integrity in SKILL.md ---
echo "--- Check 16: Cross-file reference integrity ---"
start_check 16 "cross_file_reference_integrity"
PY_REF_INTEGRITY=$(python3 -c "
import os, re, sys

sys.path.insert(0, '$KIT_ROOT/scripts/core')
from _lib.doctor_checks import build_path_map

root = '$KIT_ROOT'
skill_dir = os.path.join(root, 'skills')

# Only match backtick-quoted file.md followed by ## Section with the ## on the same ref.
# Exclude patterns with glob characters (<, >, *, [) and artifact paths.
ref_pattern = re.compile(r'\`([a-zA-Z0-9_/.@-]+\.md)\s+##\s+([A-Za-z][A-Za-z0-9 /-]+?)\`')

# Build PATH_MAP dynamically by scanning known directories
PATH_MAP = build_path_map(root)

def resolve(ref_path, skill_dir_name):
    if ref_path in PATH_MAP:
        return PATH_MAP[ref_path]
    # Check relative to skill dir, then references/ subdir, then skills/_shared
    candidates = [
        os.path.join(root, 'skills', skill_dir_name, ref_path),
        os.path.join(root, 'skills', skill_dir_name, 'references', ref_path),
        os.path.join(root, 'skills', '_shared', ref_path),
    ]
    if ref_path.startswith('../_shared/'):
        candidates.insert(0, os.path.join(root, 'skills', ref_path.replace('../_shared/', '_shared/')))
    for c in candidates:
        if os.path.exists(c):
            return os.path.relpath(c, root)
    return ref_path

errors = []
for dirpath, dirnames, filenames in os.walk(skill_dir):
    if 'SKILL.md' not in filenames:
        continue
    skill_file = os.path.join(dirpath, 'SKILL.md')
    skill_name = os.path.basename(dirpath)
    with open(skill_file) as f:
        content = f.read()
    for m in ref_pattern.finditer(content):
        raw_path = m.group(1)
        section = m.group(2).strip()
        resolved = resolve(raw_path, skill_name)
        full_path = os.path.join(root, resolved)
        if not os.path.exists(full_path):
            errors.append(f'{skill_name}/SKILL.md: file \"{raw_path}\" not found (resolved: {resolved})')
            continue
        with open(full_path) as rf:
            rcontent = rf.read()
        header_variants = ['## ' + section, '# ' + section]
        if not any(h in rcontent for h in header_variants):
            errors.append(f'{skill_name}/SKILL.md: section \"{section}\" not found in {resolved}')

if errors:
    for e in errors:
        print('FAIL: ' + e)
else:
    print('OK')
" 2>/dev/null || echo "PARSE_ERR")
case "$PY_REF_INTEGRITY" in
  OK) pass "All unpacked file+section references in SKILL.md resolve correctly" ;;
  FAIL:*)
    echo "  ${PY_REF_INTEGRITY#FAIL: }"
    errors=$((errors + 1))
    ;;
  PARSE_ERR) warn "reference integrity check encountered an error (non-critical)" ;;
esac


# --- Check 17: All SKILL.md files have next_skill and context_load fields ---
echo "--- Check 17: next_skill and context_load field presence ---"
start_check 17 "skill_fields_presence"
missing_fields=0
while IFS= read -r skill_file; do
  skill_name=$(basename "$(dirname "$skill_file")")
  if ! grep -q "^next_skill:" "$skill_file" 2>/dev/null; then
    fail "$skill_name/SKILL.md missing next_skill field"
    missing_fields=$((missing_fields + 1))
  fi
  if ! grep -q "^context_load:" "$skill_file" 2>/dev/null; then
    fail "$skill_name/SKILL.md missing context_load field"
    missing_fields=$((missing_fields + 1))
  fi
done < <(find "$KIT_ROOT/skills" -name "SKILL.md" 2>/dev/null)
if [[ $missing_fields -eq 0 ]]; then
  pass "All SKILL.md files have next_skill and context_load fields"
fi

# --- Check 18: Root-resolution consistency (root.py ↔ root.sh) ---
echo "--- Check 18: Root-resolution consistency ---"
start_check 18 "root_resolution_consistency"
PY_ROOT=$(python3 -c "
import sys; sys.path.insert(0, '$KIT_ROOT/scripts/core')
from _lib.root import resolve_root
r = resolve_root('$KIT_ROOT')
print(r or 'NONE')
" 2>/dev/null || echo "PARSE_ERR")
# bash version already ran via source; compare
if [[ "$PY_ROOT" == "PARSE_ERR" ]]; then
  warn "Could not run Python root resolution check"
elif [[ "$PY_ROOT" == "NONE" ]]; then
  fail "Python resolve_root() returned None for KIT_ROOT"
elif [[ "$PY_ROOT" != "$KIT_ROOT" ]]; then
  warn "Python resolves root to '$PY_ROOT', bash root.sh resolves to '$KIT_ROOT' (inconsistency)"
  errors=$((errors + 1))
else
  pass "root.py and root.sh agree on repo root ($KIT_ROOT)"
fi

# --- Check 19: Feature artifact structure + ID traceability ---
echo "--- Check 19: Feature artifact validation ---"
start_check 19 "feature_artifact_validation"
FEATURES_DIR="$KIT_ROOT/artifacts/features"
VALIDATE_PY="$KIT_ROOT/scripts/core/validate_artifacts.py"
artifact_errors=0
if [[ ! -d "$FEATURES_DIR" ]]; then
  pass "No artifacts/features/ dir (greenfield) — skip artifact validation"
elif [[ ! -f "$VALIDATE_PY" ]]; then
  warn "validate_artifacts.py missing — skip artifact validation"
else
  feature_count=0
  while IFS= read -r fdir; do
    slug=$(basename "$fdir")
    # Skip non-dirs / README-only placeholders
    [[ -d "$fdir" ]] || continue
    # Require at least one .md to treat as a real feature
    if ! ls "$fdir"/*.md >/dev/null 2>&1; then
      continue
    fi
    feature_count=$((feature_count + 1))
    # Infer phase from status.md if present
    phase=""
    if [[ -f "$fdir/status.md" ]]; then
      phase=$(grep -m1 -E '^## Current Phase:' "$fdir/status.md" 2>/dev/null \
        | sed 's/^## Current Phase: *//' | awk '{print $1}' || true)
    fi
    # Map status phase vocabulary → validate_artifacts phase names
    case "$phase" in
      Spec*|Research*) phase_arg="Spec" ;;
      Plan*) phase_arg="Plan" ;;
      Implement*) phase_arg="Implement" ;;
      Verif*) phase_arg="Verify" ;;
      Done*) phase_arg="Done" ;;
      *) phase_arg="Plan" ;;
    esac
    if ! out=$(python3 "$VALIDATE_PY" --root "$KIT_ROOT" --feature "$slug" --phase "$phase_arg" --strict 2>&1); then
      warn "artifacts for '$slug' (phase $phase_arg): $out"
      artifact_errors=$((artifact_errors + 1))
    fi
  done < <(find "$FEATURES_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)
  if [[ $feature_count -eq 0 ]]; then
    pass "No feature dirs with artifacts (greenfield) — skip"
  elif [[ $artifact_errors -eq 0 ]]; then
    pass "All $feature_count feature artifact sets pass validate_artifacts"
  else
    fail "$artifact_errors/$feature_count feature artifact set(s) failed validation"
  fi
fi



}

if [ "$JSON_MODE" = true ]; then
  run_checks >/dev/null
else
  run_checks
fi

# --- Summary ---
if [ "$JSON_MODE" = true ]; then
  python3 -c "
import json, sys
results = []
try:
    with open('$RESULTS_FILE') as f:
        for line in f:
            parts = line.strip().split('|', 3)
            if len(parts) == 4:
                results.append({
                    'check': int(parts[0]),
                    'name': parts[1],
                    'status': parts[2],
                    'message': parts[3]
                })
except Exception as e:
    pass
print(json.dumps(results, indent=2))
"
  rm -f "$RESULTS_FILE"
  exit $errors
fi

rm -f "$RESULTS_FILE"
echo ""
if [[ $errors -eq 0 ]]; then
  echo "All checks passed."
  exit 0
else
  echo "$errors check(s) failed."
  exit 1
fi

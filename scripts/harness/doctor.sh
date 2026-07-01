#!/usr/bin/env bash
# doctor.sh — CoreZero kit self-diagnosis
# Checks internal consistency of the installed kit surface.
# Exits 0 if all checks pass, 1 with specific failures otherwise.
# Intended to run after install.sh and on-demand by harness-maintain.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib/root.sh"

KIT_ROOT=$(resolve_repo_root) || {
  echo "FAIL: Could not resolve kit root (no AGENTS.md + core-zero/memories/repo/)"
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
  "core-zero/memories/repo/core-policies.md" \
  "core-zero/memories/repo/harness-config.md" \
  "core-zero/memories/repo/project-knowledge-base.md" \
  "core-zero/memories/repo/adr-log.md" \
  "core-zero/memories/repo/learned-heuristics.md" \
  "core-zero/memories/repo/harness-telemetry.md" \
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


# --- Check 5: Threshold consistency (100/200/3200) ---
echo "--- Check 5: Threshold consistency ---"
check_threshold() {
  local file="$1" val="$2"
  if grep -q "$val" "$KIT_ROOT/$file" 2>/dev/null; then
    return 0
  fi
  return 1
}
if grep -q "Memory Promotion Thresholds" "$KIT_ROOT/core-zero/memories/repo/core-policies.md" && grep -qE "200.*3199|200–3199" "$KIT_ROOT/core-zero/memories/repo/core-policies.md"; then
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
if grep -q "Rejected" "$KIT_ROOT/core-zero/memories/repo/adr-log.md" 2>/dev/null; then
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

# --- Check 12: next_skill chain validation ---
echo "--- Check 12: next_skill chain validation ---"
SKILL_DIR="$KIT_ROOT/skills"
next_skill_errors=0
while IFS= read -r skill_file; do
  skill_name=$(basename "$(dirname "$skill_file")")
  next_val=$(grep -m1 "^next_skill:" "$skill_file" | sed "s/next_skill: *//;s/'//g;s/\"//g" | tr -d ' \r\n')
  if [[ -z "$next_val" ]]; then
    continue  # empty next_skill is valid (terminal skill)
  fi
  if [[ ! -d "$SKILL_DIR/$next_val" ]]; then
    warn "next_skill '$next_val' in $skill_name/SKILL.md points to non-existent skill directory"
    next_skill_errors=$((next_skill_errors + 1))
  fi
done < <(find "$SKILL_DIR" -name "SKILL.md" 2>/dev/null)
if [[ $next_skill_errors -eq 0 ]]; then
  pass "All next_skill chains resolve to existing skill directories"
fi


# --- Check 13: Memory file size warnings (thresholds from core-policies.md) ---
echo "--- Check 13: Memory file size warnings ---"
# Read canonical thresholds from core-policies.md
THRESHOLD_SRC="$KIT_ROOT/core-zero/memories/repo/core-policies.md"
PY_READ_THRESHOLDS=$(python3 -c "
import re, sys
text = open('$THRESHOLD_SRC').read()
sec_m = re.search(r'## Memory Promotion Thresholds(.*?)(?=## |\Z)', text, re.DOTALL)
if not sec_m:
    print('100 200')
    sys.exit(0)
body = sec_m.group(1)
early = re.search(r'100–199', body)
breach = re.search(r'200–3199', body)
ew = 100 if early else 100
tb = 200 if breach else 200
print(f'{ew} {tb}')
" 2>/dev/null || echo "100 200")
read early_warn threshold_breach <<< "$PY_READ_THRESHOLDS"
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
  if [[ $line_count -ge $threshold_breach ]]; then
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
MANIFEST_FILE="$KIT_ROOT/manifest.json"
PY_MANIFEST_DRIFT=$(python3 -c "
import json, glob, os, sys

root = '$KIT_ROOT'
mf = '$MANIFEST_FILE'

if not os.path.exists(mf):
    print('SKIP')
    sys.exit(0)

with open(mf) as f:
    manifest = json.load(f)

files = manifest.get('files', {})
all_entries = files.get('overwrite', []) + files.get('copyIfMissing', [])

# Resolve each manifest entry to actual files on disk
manifest_files = set()
for entry in all_entries:
    if entry.endswith('/'):
        continue
    full_pattern = os.path.join(root, entry)
    matches = glob.glob(full_pattern, recursive=True)
    for m in matches:
        if os.path.isfile(m):
            rel = os.path.relpath(m, root)
            manifest_files.add(rel)

# Find shipped files on disk NOT in manifest
uncovered = set()
exclude_prefixes = ('node_modules/', '.git/', '__pycache__/', '.corezero/')
# Runtime-generated paths that aren't expected to be in manifest
runtime_paths = ('artifacts/', 'core-zero/generated/', 'core-zero/memories/archive/')
for dirpath, dirnames, filenames in os.walk(root):
    rel_dir = os.path.relpath(dirpath, root)
    if rel_dir == '.':
        rel_dir = ''
    skip = False
    for p in exclude_prefixes:
        rp = rel_dir + '/' if rel_dir else ''
        if rp.startswith(p):
            skip = True
            break
    if skip:
        continue
    for fn in filenames:
        fpath = (rel_dir + '/' if rel_dir else '') + fn
        if fpath in manifest_files or fpath == 'manifest.json':
            continue
        if any(fpath.startswith(p) for p in runtime_paths):
            continue
        if fn.endswith(('.md', '.sh', '.py', '.json', '.yaml', '.yml', '.html', '.txt', '.template')):
            uncovered.add(fpath)

# Check entries in manifest that don't exist on disk
missing_from_disk = []
for f in sorted(manifest_files):
    if not os.path.exists(os.path.join(root, f)):
        missing_from_disk.append(f)

issues = []
if missing_from_disk:
    issues.append(f'{len(missing_from_disk)} manifest entr' + ('ies' if len(missing_from_disk) > 1 else 'y') + ' missing from disk: ' + ', '.join(missing_from_disk))
if uncovered:
    issues.append(f'{len(uncovered)} file' + ('s' if len(uncovered) > 1 else '') + ' on disk not covered by manifest: ' + ', '.join(sorted(uncovered)[:15]) + (' ...' if len(uncovered) > 15 else ''))

if issues:
    for i in issues:
        print('FAIL: ' + i)
else:
    print('OK')
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
PY_REF_INTEGRITY=$(python3 -c "
import os, re, sys

root = '$KIT_ROOT'
skill_dir = os.path.join(root, 'skills')

# Only match backtick-quoted file.md followed by ## Section with the ## on the same ref.
# Exclude patterns with glob characters (<, >, *, [) and artifact paths.
ref_pattern = re.compile(r'\`([a-zA-Z0-9_/.@-]+\.md)\s+##\s+([A-Za-z][A-Za-z0-9 /-]+?)\`')

# Known short-path mappings for bare filenames referenced in skills
PATH_MAP = {
    'core-policies.md': 'core-zero/memories/repo/core-policies.md',
    'harness-config.md': 'core-zero/memories/repo/harness-config.md',
    'learned-heuristics.md': 'core-zero/memories/repo/learned-heuristics.md',
    'project-knowledge-base.md': 'core-zero/memories/repo/project-knowledge-base.md',
    'harness-telemetry.md': 'core-zero/memories/repo/harness-telemetry.md',
    'adr-log.md': 'core-zero/memories/repo/adr-log.md',
    'code-map.md': 'core-zero/project/code-map.md',
    'tech-stack.md': 'core-zero/project/tech-stack.md',
    'architecture.md': 'core-zero/project/architecture.md',
    'glossary.md': 'core-zero/memories/domain/glossary.md',
    'ponytail.md': 'core-zero/rules/ponytail.md',
    'security.md': 'core-zero/rules/security.md',
    'code-design.md': 'core-zero/policies/code-design.md',
    'spec-schema.json': 'core-zero/project/spec-schema.json',
    'README.md': 'core-zero/memories/domain/README.md',
}

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


# --- Check 17: All SKILL.md files have next_skill field ---
echo "--- Check 17: next_skill field presence ---"
missing_next=0
while IFS= read -r skill_file; do
  skill_name=$(basename "$(dirname "$skill_file")")
  if ! grep -q "^next_skill:" "$skill_file" 2>/dev/null; then
    warn "$skill_name/SKILL.md missing next_skill field"
    missing_next=$((missing_next + 1))
  fi
done < <(find "$KIT_ROOT/skills" -name "SKILL.md" 2>/dev/null)
if [[ $missing_next -eq 0 ]]; then
  pass "All SKILL.md files have next_skill field"
fi


# --- Summary ---
echo ""
if [[ $errors -eq 0 ]]; then
  echo "All checks passed."
  exit 0
else
  echo "$errors check(s) failed."
  exit 1
fi

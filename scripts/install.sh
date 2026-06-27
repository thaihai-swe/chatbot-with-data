#!/usr/bin/env bash
#
# CoreZero installer
#
# Usage:
#   scripts/install.sh <target_dir> [--dry-run]
#
# Behavior:
#   - Reads manifest.json at the kit root.
#   - Backs up existing kit-managed files to <target>/.corezero-backup-<timestamp>/.
#   - Overwrites kit content (skills, scripts, rules, doc references).
#   - Copies user-content files (memory, templates, architecture) only if missing.
#   - Preserves user state (memories/repo content, artifacts/, local settings).
#   - Idempotent. Re-running upgrades the kit and preserves your content.
#
# Curl-pipe support:
#   When piped from curl, the script clones this repo to a temp dir, runs the
#   installer, and cleans up.

set -euo pipefail

REPO_URL="${HARNESS_KIT_REPO_URL:-https://github.com/thaihai-swe/CoreZero.git}"

err() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
log() { printf '%s\n' "$*"; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || err "required command not found: $1"
}

read_manifest_array() {
  local manifest="$1"
  local path="$2"
  python3 - "$manifest" "$path" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
cur = m
for k in sys.argv[2].split('.'):
    cur = cur[k]
if not isinstance(cur, list):
    raise SystemExit("expected list at " + sys.argv[2])
for item in cur:
    print(item)
PY
}

read_manifest_pairs() {
  local manifest="$1"
  local path="$2"
  python3 - "$manifest" "$path" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
cur = m
for k in sys.argv[2].split('.'):
    cur = cur.get(k, []) if isinstance(cur, dict) else cur
    if cur is None:
        cur = []
        break
if not isinstance(cur, list):
    raise SystemExit("expected list at " + sys.argv[2])
for item in cur:
    if not isinstance(item, dict) or "src" not in item or "dst" not in item:
        raise SystemExit("expected {src, dst} object at " + sys.argv[2])
    print(item["src"] + "\t" + item["dst"])
PY
}

read_manifest_string() {
  local manifest="$1"
  local path="$2"
  python3 - "$manifest" "$path" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
cur = m
for k in sys.argv[2].split('.'):
    cur = cur[k]
print(cur)
PY
}

if sed --version >/dev/null 2>&1; then
  SED_INPLACE=(sed -i)
else
  SED_INPLACE=(sed -i '')
fi

expand_glob() {
  local pattern="$1"
  pushd "$SOURCE_DIR" >/dev/null
  if [[ "$pattern" == *"**"* ]]; then
    local base="${pattern%%/\*\**}"
    [[ -d "$base" ]] && find "$base" -type f ! -name ".DS_Store" ! -path "*/test-output/*" ! -path "*/__pycache__/*"
  elif [[ "$pattern" == *"*"* ]]; then
    shopt -s nullglob
    local matches=( $pattern )
    shopt -u nullglob
    local m
    for m in "${matches[@]}"; do
      [[ -f "$m" && "$(basename "$m")" != ".DS_Store" && "$m" != *"/test-output/"* && "$m" != *"/__pycache__/"* ]] && echo "$m"
    done
  else
    [[ -f "$pattern" ]] && echo "$pattern"
  fi
  popd >/dev/null
}

copy_into_target() {
  local rel="$1"
  local src="$SOURCE_DIR/$rel"
  local dst="$TARGET_DIR/$rel"
  [[ -f "$src" ]] || err "manifest references missing source: $rel"
  if [[ "$DRY_RUN" == "true" ]]; then
    log "  [dry-run] would copy: $rel"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

copy_cross_tree() {
  local src_rel="$1"
  local dst_rel="$2"
  local src="$REPO_ROOT/$src_rel"
  local dst="$TARGET_DIR/$dst_rel"
  [[ -f "$src" ]] || err "crossTreeOverwrite references missing source: $src_rel"
  if [[ "$DRY_RUN" == "true" ]]; then
    log "  [dry-run] would copy (cross-tree): $src_rel -> $dst_rel"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

backup_file() {
  local rel="$1"
  local dst="$TARGET_DIR/$rel"
  [[ -f "$dst" ]] || return 0
  if [[ "$DRY_RUN" == "true" ]]; then
    log "  [dry-run] would back up: $rel"
    return
  fi
  local backup_path="$BACKUP_DIR/$rel"
  mkdir -p "$(dirname "$backup_path")"
  cp "$dst" "$backup_path"
  backup_count=$((backup_count + 1))
}

resolve_source_dir() {
  if [[ "${BASH_SOURCE[0]:-}" != "" && -f "${BASH_SOURCE[0]}" ]]; then
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local maybe_root
    maybe_root="$(cd "$script_dir/.." && pwd)"
    if [[ -f "$maybe_root/manifest.json" ]]; then
      SOURCE_DIR="$maybe_root"
      SOURCE_TEMP=""
      return
    fi
  fi
  require_cmd git
  SOURCE_TEMP="$(mktemp -d)"
  log "Cloning kit to temp: $SOURCE_TEMP"
  git clone --depth 1 "$REPO_URL" "$SOURCE_TEMP" >/dev/null 2>&1 \
    || err "could not clone $REPO_URL"
  if [[ -f "$SOURCE_TEMP/manifest.json" ]]; then
    SOURCE_DIR="$SOURCE_TEMP"
  elif [[ -f "$SOURCE_TEMP/kit/manifest.json" ]]; then
    SOURCE_DIR="$SOURCE_TEMP/kit"
  else
    err "manifest.json not found in cloned repository at $SOURCE_TEMP"
  fi
}

cleanup_source_temp() {
  if [[ -n "${SOURCE_TEMP:-}" && -d "$SOURCE_TEMP" ]]; then
    rm -rf "$SOURCE_TEMP"
  fi
}

TARGET_DIR=""
DRY_RUN="false"
TARGET_VERSION=""
SHOW_VERSION="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN="true"; shift
      ;;
    --version)
      SHOW_VERSION="true"; shift
      ;;
    --target-version)
      TARGET_VERSION="$2"; shift 2
      ;;
    -h|--help)
      log "Usage: install.sh <target_dir> [--dry-run] [--target-version <ver>] [--version]"
      exit 0
      ;;
    *)
      [[ -z "$TARGET_DIR" ]] || err "unexpected argument: $1"
      TARGET_DIR="$1"; shift
      ;;
  esac
done

if [[ "$SHOW_VERSION" == "true" ]]; then
  resolve_source_dir
  if [[ -f "$SOURCE_DIR/manifest.json" ]]; then
    VER=$(python3 -c "import json; print(json.load(open('$SOURCE_DIR/manifest.json'))['version'])" 2>/dev/null || echo "[UNKNOWN]")
    echo "$VER"
    exit 0
  else
    err "Could not determine version: manifest.json not found."
  fi
fi

[[ -n "$TARGET_DIR" ]] || err "Usage: install.sh <target_dir> [--dry-run] [--target-version <ver>] [--version]"

require_cmd python3
require_cmd cp
require_cmd find

trap cleanup_source_temp EXIT

resolve_source_dir
MANIFEST="$SOURCE_DIR/manifest.json"
[[ -f "$MANIFEST" ]] || err "manifest.json not found at $MANIFEST"

if [[ -n "$TARGET_VERSION" ]]; then
  VER=$(python3 -c "import json; print(json.load(open('$MANIFEST'))['version'])" 2>/dev/null || echo "[UNKNOWN]")
  if [[ "$VER" != "$TARGET_VERSION" ]]; then
    err "Version mismatch: expected target-version '$TARGET_VERSION' but source kit version is '$VER'"
  fi
fi

REPO_ROOT="$(cd "$SOURCE_DIR/.." && pwd)"

mkdir -p "$TARGET_DIR"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$TARGET_DIR/.corezero-backup-$TIMESTAMP"

log "CoreZero installer"
log "  Source:   $SOURCE_DIR"
log "  Target:   $TARGET_DIR"
log "  Dry run:  $DRY_RUN"
log "  Package:  adopter docs in docs/; maintainer docs stay in the source repo"
log ""

while IFS= read -r dir; do
  [[ -n "$dir" ]] || continue
  if [[ "$DRY_RUN" == "true" ]]; then
    log "  [dry-run] would mkdir: $dir"
  else
    mkdir -p "$TARGET_DIR/$dir"
  fi
done < <(read_manifest_array "$MANIFEST" directories)

log "Installing kit content (overwrite)..."
overwrite_count=0
backup_count=0
cross_tree_count=0

while IFS= read -r pattern; do
  [[ -n "$pattern" ]] || continue
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    if [[ -f "$TARGET_DIR/$rel" ]]; then
      backup_file "$rel"
    fi
    copy_into_target "$rel"
    overwrite_count=$((overwrite_count + 1))
  done < <(expand_glob "$pattern")
done < <(read_manifest_array "$MANIFEST" files.overwrite)

while IFS=$'\t' read -r src_rel dst_rel; do
  [[ -n "$src_rel" && -n "$dst_rel" ]] || continue
  if [[ -f "$TARGET_DIR/$dst_rel" ]]; then
    backup_file "$dst_rel"
  fi
  copy_cross_tree "$src_rel" "$dst_rel"
  cross_tree_count=$((cross_tree_count + 1))
done < <(read_manifest_pairs "$MANIFEST" files.crossTreeOverwrite)

log "Seeding user content (copyIfMissing)..."
seeded_count=0
skipped_count=0

while IFS= read -r rel; do
  [[ -n "$rel" ]] || continue
  if [[ -f "$TARGET_DIR/$rel" ]]; then
    skipped_count=$((skipped_count + 1))
    continue
  fi
  [[ -f "$SOURCE_DIR/$rel" ]] || err "copyIfMissing references missing source: $rel"
  copy_into_target "$rel"
  seeded_count=$((seeded_count + 1))
done < <(read_manifest_array "$MANIFEST" files.copyIfMissing)

if [[ "$DRY_RUN" != "true" ]]; then
  find "$TARGET_DIR/scripts" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} +
fi

warn_orphans() {
  [[ "$DRY_RUN" == "true" ]] && return 0
  local orphans=(
    "docs/system-specs"
    "docs/INSTALL.md"
    "docs/ADOPTION_GUIDE.md"
    "HARNESS_CARD.md"
    "docs/GLOSSARY.md"
    "docs/GOVERNANCE.md"
    "docs/PRODUCT_SENSE.md"
    "docs/PROJECT_CONSTRAINTS.md"
    "docs/QUALITY_POLICY.md"
    "docs/RELIABILITY_POLICY.md"
    "docs/TECH_DEBT_REGISTER.md"
    "docs/TECH_STACK_REFERENCE.md"
    "docs/architecture.md"
    "docs/code-design.md"
    "docs/guides/install.md"
    "docs/guides/adoption-guide.md"
    "memories/domains"
    "scripts/detect-stack.py"
    "scripts/doctor.sh"
    "scripts/parse-observability.py"
    "scripts/check-surface-truth.py"
    ".github/workflows/harness-check.yml"
    "rules/README.md"
    "rules/security.md"
    "skills/context-memory/references/architecture-template.md"
    "skills/context-memory/references/constitution-template.md"
    "skills/context-memory/references/index-template.md"
    "skills/context-memory/references/project-knowledge-base-template.md"
    "skills/context-memory/references/security-policy-template.md"
    "skills/context-memory/references/observability-log-template.md"
    "skills/context-memory/references/adr-log-template.md"
    "skills/starter-init/references/harness-config-template.md"
    "skills/starter-init/references/harness-card-template.md"
    "skills/harness-maintain/references/codemap-template.md"
    "skills/harness-maintain/references/references-index-template.md"
    "docs/generated/references-index.md"
    "memories/repo/security-policy.md"
    "INDEX.md"
    "docs/README.md"
    "skills/context-status/references/dashboard-template.html"
  )
  local orphan
  for orphan in "${orphans[@]}"; do
    if [[ -e "$TARGET_DIR/$orphan" ]]; then
      log "  WARNING: orphan from previous kit version: $orphan (safe to delete)"
    fi
  done
}

warn_orphans

errors=0
validate_path() {
  local path="$1" label="$2"
  if [[ -e "$TARGET_DIR/$path" ]]; then
    log "  [OK]   $label"
  else
    log "  [FAIL] $label — missing: $path"
    errors=$((errors + 1))
  fi
}

if [[ "$DRY_RUN" != "true" ]]; then
  log ""
  log "Post-install validation"
  validate_path "docs/policies/code-design.md" "Code design policy"
  validate_path "skills" "Skills directory"
  validate_path "skills/context-status/SKILL.md" "Context-status skill"
  validate_path "skills/harness-maintain/SKILL.md" "Harness-maintain skill"
  validate_path "skills/spec-adr/SKILL.md" "Spec-ADR skill"
  validate_path "skills/technical-docs/SKILL.md" "Technical-docs skill"
  validate_path "skills/codebase-documenter/SKILL.md" "Codebase-documenter skill"
  validate_path "skills/visualize/SKILL.md" "Visualize skill"
  validate_path "skills/visualize/scripts/validate_mermaid.py" "Visualize Mermaid validator"
  validate_path "skills/visualize/templates/architecture.svg" "Visualize SVG template"
  validate_path "memories/repo" "Memory layer"
  validate_path "memories/repo/core-policies.md" "Core policies"
  validate_path "memories/repo/core-policies.md" "Core policies"
  validate_path "memories/repo/harness-config.md" "Harness config"
  validate_path "AGENTS.md" "Runtime entrypoint"
  validate_path "docs/rules/security.md" "Security rules"
  validate_path "docs/rules/ponytail.md" "Ponytail rules"
  validate_path "skills/ponytail/SKILL.md" "Ponytail skill"
  validate_path "scripts/install.sh" "Installer (self-shipped)"
  validate_path "scripts/harness/gate-runner.sh" "Harness Gate Runner"
  validate_path "scripts/harness/telemetry-collector.sh" "Harness Telemetry Collector"
  validate_path "scripts/harness/telemetry-count.sh" "Harness Telemetry Counter"
  validate_path "scripts/harness/doctor.sh" "Harness Doctor"
  log ""
  log "Running kit doctor..."
  if bash "$TARGET_DIR/scripts/harness/doctor.sh"; then
    log "  [OK]   All doctor checks passed"
  else
    errors=$((errors + 1))
    log "  [FAIL] Doctor check failed"
  fi
fi

log ""
log "Summary"
log "  Files installed:      $overwrite_count"
log "  Cross-tree installed: $cross_tree_count"
log "  Files seeded:         $seeded_count"
log "  Files skipped:        $skipped_count (already present)"
log "  Files backed up:      $backup_count -> $BACKUP_DIR"
log "  Installed docs: docs/ (adopter-facing)"
log "  Not installed by default: documents/ (maintainer-only)"

if [[ $errors -gt 0 ]]; then
  log ""
  err "validation failed with $errors error(s)"
fi

log ""
log "Next steps:"
log "  1. Run /starter-init in your AI agent"
log "  2. Start the first feature with /spec-requirements (or /spec-research for brownfield/unknown behavior)"
log "  3. Use /context-session only after a feature slug and status.md already exist"
log "  4. Deliver through /spec-plan, /spec-implement"
log "  5. Close out with /harness-verify"
log "  6. Governance bundle: /context-status, /harness-maintain, /spec-adr"
log "  7. Docs bundle: /technical-docs, /codebase-documenter"
log "  8. Specialist visualization: /visualize (Mermaid validation bundled; Mermaid render optional with mmdc)"
log "  9. Use documents/ only in the source repository when maintaining the kit itself"
log ""
log "Upgrade later: re-run this command. Memory and artifacts are preserved."

#!/usr/bin/env python3
"""Lightweight feature artifact structure + ID traceability checks.

Stdlib only. No JSON Schema theater — headings + ID greps.
Usage:
  python3 scripts/core/validate_artifacts.py --feature <slug>
  python3 scripts/core/validate_artifacts.py --feature <slug> --trace
  python3 scripts/core/validate_artifacts.py --feature <slug> --phase Plan
"""
import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core._lib.root import resolve_root

# Expected files by delivery phase (cumulative for later phases)
PHASE_FILES = {
    "Spec": ["status.md", "spec.md"],
    "Plan": ["status.md", "spec.md", "plan.md", "tasks.md"],
    "Implement": ["status.md", "spec.md", "plan.md", "tasks.md"],
    "Verify": ["status.md", "spec.md", "plan.md", "tasks.md"],
    "Done": ["status.md", "spec.md", "plan.md", "tasks.md"],
}

# Required H2 headings when file present (subset of templates)
REQUIRED_HEADINGS = {
    "spec.md": ["## Metadata", "## Problem Statement"],
    "plan.md": ["## Metadata"],
    "tasks.md": ["## Metadata"],
    "status.md": [],  # status template varies; existence only
}

ID_PATTERNS = {
    "REQ": re.compile(r"\bREQ-\d+\b"),
    "AC": re.compile(r"\bAC-\d+\b"),
    "TASK": re.compile(r"\bTASK-\d+\b"),
}


def feature_dir(root, slug):
    return Path(root) / "artifacts" / "features" / slug


def extract_ids(text, kind):
    return set(ID_PATTERNS[kind].findall(text or ""))


def check_structure(fdir, phase=None):
    errors = []
    warns = []
    phase = phase or "Plan"
    expected = PHASE_FILES.get(phase, PHASE_FILES["Plan"])
    for name in expected:
        path = fdir / name
        if not path.exists():
            errors.append(f"missing required file for phase {phase}: {name}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for heading in REQUIRED_HEADINGS.get(name, []):
            if heading not in text and heading.lower() not in text.lower():
                # Allow flexible casing of heading text after ##
                bare = heading.lstrip("# ").lower()
                if not re.search(rf"^##\s+{re.escape(bare)}\s*$", text, re.I | re.M):
                    warns.append(f"{name}: missing heading {heading}")
    return errors, warns


def traceability(fdir):
    """Return (report_lines, errors) for REQ/AC/TASK linkage."""
    errors = []
    lines = []
    texts = {}
    for name in ("spec.md", "plan.md", "tasks.md", "status.md"):
        p = fdir / name
        texts[name] = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

    reqs = extract_ids(texts["spec.md"], "REQ")
    acs_spec = extract_ids(texts["spec.md"], "AC")
    acs_tasks = extract_ids(texts["tasks.md"], "AC")
    tasks = extract_ids(texts["tasks.md"], "TASK")
    # ACs may also live only in tasks via Linked acceptance criteria
    all_acs = acs_spec | acs_tasks

    lines.append("# Traceability Report")
    lines.append("")
    lines.append(f"| Kind | Count | IDs |")
    lines.append(f"| --- | --- | --- |")
    lines.append(f"| REQ | {len(reqs)} | {', '.join(sorted(reqs)) or '—'} |")
    lines.append(f"| AC | {len(all_acs)} | {', '.join(sorted(all_acs)) or '—'} |")
    lines.append(f"| TASK | {len(tasks)} | {', '.join(sorted(tasks)) or '—'} |")
    lines.append("")

    # Orphan ACs in tasks that never appear in spec (informational if no ACs in spec)
    orphan_acs = acs_tasks - acs_spec if acs_spec else set()
    # Tasks without any AC mention in their block: best-effort — task IDs whose
    # surrounding 15 lines lack AC-
    task_without_ac = set()
    if texts["tasks.md"]:
        for m in re.finditer(r"TASK-\d+", texts["tasks.md"]):
            start = max(0, m.start() - 200)
            end = min(len(texts["tasks.md"]), m.end() + 400)
            window = texts["tasks.md"][start:end]
            if not ID_PATTERNS["AC"].search(window):
                task_without_ac.add(m.group(0))

    if orphan_acs:
        lines.append(f"**Orphan ACs (in tasks.md, not in spec.md):** {', '.join(sorted(orphan_acs))}")
        errors.append(f"orphan ACs: {', '.join(sorted(orphan_acs))}")
    if task_without_ac:
        lines.append(f"**TASKs without nearby AC link:** {', '.join(sorted(task_without_ac))}")
        errors.append(f"tasks without AC: {', '.join(sorted(task_without_ac))}")
    if not reqs and texts["spec.md"]:
        lines.append("**Note:** no REQ-* IDs found in spec.md")
    if not errors:
        lines.append("**OK:** no orphan AC/TASK linkage issues detected.")
    lines.append("")
    return lines, errors


def main():
    parser = argparse.ArgumentParser(description="Validate feature artifacts")
    parser.add_argument("--root", default="", help="Repo root")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--phase", default="", help="Delivery phase (Spec/Plan/Implement/Verify/Done)")
    parser.add_argument("--trace", action="store_true", help="Emit REQ/AC/TASK traceability report")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on warnings too")
    args = parser.parse_args()

    root = resolve_root(args.root)
    if not root:
        print("ERROR: could not resolve repo root", file=sys.stderr)
        sys.exit(2)
    fdir = feature_dir(root, args.feature)
    if not fdir.is_dir():
        print(f"ERROR: feature dir not found: {fdir}", file=sys.stderr)
        sys.exit(1)

    phase = args.phase or None
    errors, warns = check_structure(fdir, phase)
    for e in errors:
        print(f"FAIL: {e}")
    for w in warns:
        print(f"WARN: {w}")

    if args.trace:
        report, terr = traceability(fdir)
        print("\n".join(report))
        errors.extend(terr)

    if errors or (args.strict and warns):
        sys.exit(1)
    if not errors and not warns:
        print(f"PASS: artifacts OK for '{args.feature}'" + (f" (phase {phase})" if phase else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()

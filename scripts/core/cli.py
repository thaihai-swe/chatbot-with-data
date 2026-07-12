#!/usr/bin/env python3
"""Adopter-facing CoreZero lifecycle CLI."""

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import importlib.util
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core._lib.root import resolve_root
from core.context_engine import ContextEngine
from core.context_engine import build_context_pack, extract_section
from core._lib.token_counter import estimate_tokens
from core._lib.yaml_reader import load as load_yaml
from core.context_state import (
    atomic_write,
    default_session_path,
    load_session,
    update_session_sections,
)
from core.task_graph import (
    ALLOWED_TRANSITIONS,
    detect_cycle,
    feature_tasks_path,
    next_tasks,
    normalize_status,
    parse_tasks,
    update_task_text,
)
from core.validate_artifacts import check_structure, traceability


COMMAND_HELP = {
    "init": "initialize deterministic CoreZero repository scaffolding",
    "status": "report feature status and refresh the dashboard",
    "context-pack": "plan a bounded runtime context pack",
    "context-load": "load the bounded runtime context for the agent",
    "memory-audit": "report memory file size and token costs",
    "phase-check": "check phase preconditions",
    "task-check": "validate the task dependency graph",
    "task-next": "list the next unblocked tasks",
    "task-start": "start an unblocked task",
    "task-update": "update an explicit task status",
    "task-done": "mark a task done with proof evidence",
    "task-block": "mark a task blocked with a reason",
    "artifact-check": "validate feature artifact structure and traceability",
    "verify": "run deterministic verification checks and mechanical gates",
    "session-start": "start or resume a feature session",
    "session-checkpoint": "refresh a feature session checkpoint",
    "session-end": "close a feature session and record its handoff",
    "domain-packs": "list installed domain packs and their trigger keywords",
}


def _parser():
    parser = argparse.ArgumentParser(prog="corezero", description="CoreZero deterministic operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in COMMAND_HELP:
        help_text = COMMAND_HELP[command]
        sub = subparsers.add_parser(command, help=help_text)
        if command == "init":
            _add_output_options(sub)
            sub.add_argument("--root", default="", help="Repository root")
            sub.add_argument("--dry-run", action="store_true", help="Report writes without changing files")
        elif command == "status":
            _add_output_options(sub)
            sub.add_argument("--root", default="", help="Repository root")
            sub.add_argument("--feature", default="", help="Limit report to one feature")
            sub.add_argument("--dry-run", action="store_true", help="Scan without refreshing the dashboard")
        elif command == "domain-packs":
            _add_output_options(sub)
            sub.add_argument("--root", default="", help="Repository root")
            sub.add_argument("--list", action="store_true", help="List installed domain packs")
        elif command in {"context-pack", "context-load", "memory-audit"}:
            _add_output_options(sub)
            sub.add_argument("--root", default="", help="Repository root")
            sub.add_argument("--feature", default="", help="Feature slug")
            sub.add_argument("--phase", default="", help="Delivery phase")
            sub.add_argument("--task", default="", help="Active task ID")
            sub.add_argument("--intent", default="", help="Context routing keywords")
            sub.add_argument("--budget", type=int, default=0, help="Hard token budget")
            sub.add_argument("--dry-run", action="store_true", help="Report without changing files")
        elif command in {"phase-check", "task-check", "task-next", "task-start", "task-update",
                         "task-done", "task-block", "artifact-check", "verify"}:
            _add_output_options(sub)
            sub.add_argument("--root", default="", help="Repository root")
            sub.add_argument("--feature", required=True, help="Feature slug")
            sub.add_argument("--phase", default="", help="Delivery phase")
            sub.add_argument("--task", default="", help="Active task ID")
            sub.add_argument("--dry-run", action="store_true", help="Report actions without changing files")
            if command in {"task-start", "task-update", "task-done", "task-block"}:
                sub.add_argument("--status", choices=["Not Started", "In Progress", "Blocked", "Done", "Deferred"],
                                 help="Explicit target task status")
                sub.add_argument("--evidence", action="append", default=[],
                                 help="Validation evidence (repeatable; required for task-done)")
                sub.add_argument("--evidence-file", type=Path,
                                 help="Markdown file containing validation evidence")
                sub.add_argument("--note", default="", help="Human-authored task note or block reason")
            if command == "artifact-check":
                sub.add_argument("--trace", action="store_true", help="Include requirement/task traceability")
        else:
            _add_common_options(sub)
            sub.add_argument("--objective", default="", help="Session objective")
            sub.add_argument("--next-action", default="", help="Next recommended action")
            sub.add_argument("--blocker", action="append", default=[], help="Active blocker (repeatable)")
            sub.add_argument("--decision", action="append", default=[], help="Locked decision (repeatable)")
            sub.add_argument("--progress", default="", help="Progress section content")
            sub.add_argument("--handoff-file", type=Path, help="Markdown file supplying the Handoff section")
            if command == "session-end":
                sub.add_argument("--candidate", action="append", default=[],
                                 help="Explicit session-extract candidate in Markdown (repeatable)")
                sub.add_argument("--extract-file", type=Path,
                                 help="Markdown file containing explicit session-extract candidates")
    return parser


def _add_output_options(parser):
    parser.add_argument("--json", action="store_true", help="Print a JSON result")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostics")


def _add_common_options(parser):
    parser.add_argument("--root", default="", help="Repository root")
    parser.add_argument("--feature", required=True, help="Existing feature slug")
    parser.add_argument("--phase", default="", help="Current delivery phase")
    parser.add_argument("--task", default="", help="Active task ID")
    parser.add_argument("--intent", default="", help="Context routing keywords")
    parser.add_argument("--budget", type=int, default=0, help="Context token budget")
    parser.add_argument("--resume", action="store_true", help="Resume metadata from the existing session")
    parser.add_argument("--json", action="store_true", help="Print a JSON result")
    parser.add_argument("--verbose", action="store_true", help="Print loaded context and diagnostics")


def _resolve_root(args, allow_uninitialized=False):
    root = resolve_root(args.root)
    if root:
        return Path(root)
    if allow_uninitialized:
        candidate = Path(args.root or os.getcwd()).resolve()
        if candidate.is_dir():
            return candidate
    raise ValueError("Unable to locate an initialized CoreZero repository")


def _result(command, status="ok", feature="", artifacts=None, warnings=None,
            next_action="", details=None):
    return {
        "command": command,
        "status": status,
        "feature": feature,
        "artifacts": artifacts or [],
        "warnings": warnings or [],
        "next_action": next_action,
        "details": details or {},
    }


def _load_dashboard_module(root):
    script = root / "scripts" / "generate-dashboard.py"
    if not script.is_file():
        raise ValueError(f"Dashboard generator missing: {script}")
    spec = importlib.util.spec_from_file_location("corezero_dashboard", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _init(args):
    root = _resolve_root(args, allow_uninitialized=True)
    directories = [
        "core-zero/memories/repo", "core-zero/memories/domain", "core-zero/project",
        "core-zero/generated", "artifacts/features", "scripts/harness",
    ]
    seeds = [
        "core-zero/memories/repo/core-policies.md",
        "core-zero/memories/repo/harness-config.md",
        "core-zero/memories/repo/learned-heuristics.md",
        "core-zero/memories/repo/project-knowledge-base.md",
        "core-zero/memories/repo/harness-telemetry.md",
        "core-zero/memories/repo/adr-log.md",
        "core-zero/project/architecture.md",
        "core-zero/project/product-sense.md",
        "core-zero/project/project-constraints.md",
        "core-zero/project/glossary.md",
        "core-zero/project/tech-stack.md",
        "core-zero/project/code-map.md",
        "core-zero/project/agent-capabilities.md",
    ]
    writes = []
    if not args.dry_run:
        for relative in directories:
            (root / relative).mkdir(parents=True, exist_ok=True)
        for relative in seeds:
            path = root / relative
            if not path.exists():
                atomic_write(path, f"# {path.stem.replace('-', ' ').title()}\n\n[USER REVIEW NEEDED]\n")
                writes.append(relative)
        gitignore = root / ".gitignore"
        existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
        additions = ["core-zero/generated/*", "core-zero/memories/repo/harness-telemetry.md", "scripts/harness/gate-runner.local.sh"]
        missing = [line for line in additions if line not in existing.splitlines()]
        if missing:
            atomic_write(gitignore, existing.rstrip() + "\n" + "\n".join(missing) + "\n")
            writes.append(".gitignore")
    markers = {
        "node": ("package.json",), "python": ("pyproject.toml", "pytest.ini"),
        "go": ("go.mod",), "rust": ("Cargo.toml",),
        "jvm": ("pom.xml", "build.gradle"), "ruby": ("Gemfile",),
    }
    detected = [name for name, paths in markers.items() if any((root / path).exists() for path in paths)]
    initialized = (root / "core-zero/memories/repo/harness-config.md").exists()
    return _result("init", artifacts=writes, next_action="/starter-init", details={
        "root": str(root), "initialized": initialized, "detected_stacks": detected,
        "dry_run": args.dry_run,
    })


def _status(args):
    root = _resolve_root(args)
    dashboard = _load_dashboard_module(root)
    features = dashboard.scan_workspace(root)
    if args.feature:
        features = [item for item in features if item["slug"] == args.feature]
    if not args.dry_run:
        output = root / "core-zero/generated/dashboard.html"
        html = dashboard.get_html_template(json.dumps(features).replace("<", "\\u003c").replace(">", "\\u003e"))
        atomic_write(output, html)
    blockers = [item["slug"] for item in features if item.get("has_blocker")]
    next_action = features[0].get("next_step", "") if len(features) == 1 else "corezero status"
    return _result("status", feature=args.feature, artifacts=["core-zero/generated/dashboard.html"] if not args.dry_run else [],
                   warnings=[f"Blocker: {slug}" for slug in blockers], next_action=next_action,
                   details={"features": features, "dry_run": args.dry_run})


def _context_pack(args):
    root = _resolve_root(args)
    if args.feature:
        _require_feature(root, args.feature)
    pack = build_context_pack(root, phase=args.phase, intent=args.intent,
                              feature=args.feature, budget=args.budget)
    current = {}
    if args.feature and (root / "scripts/generate-dashboard.py").is_file():
        dashboard = _load_dashboard_module(root)
        current = next((item for item in dashboard.scan_workspace(root)
                        if item["slug"] == args.feature), {})
    return _result("context-pack", "ok", args.feature,
                   [item["path"] for item in pack["selected"]],
                   [f"{item['path']}: {item['reason']}" for item in pack["omitted"]],
                   next_action=current.get("next_step", "corezero status"),
                   details={
                       "selected": pack["selected"],
                       "omitted": pack["omitted"],
                       "estimated_tokens": pack["estimated_tokens"],
                       "budget": pack["budget"],
                       "current": {
                           "phase": current.get("phase", args.phase or ""),
                           "task": current.get("active_task", args.task if hasattr(args, "task") else ""),
                           "blockers": current.get("blockers", "None"),
                       },
                       "dry_run": args.dry_run,
                   })


def _context_load(args):
    """Load the exact bounded context selected by the routing engine."""
    root = _resolve_root(args)
    if args.feature:
        _require_feature(root, args.feature)
    pack = build_context_pack(root, phase=args.phase, intent=args.intent,
                              feature=args.feature, budget=args.budget)
    loaded = []
    for item in pack["selected"]:
        path = root / item["path"]
        text = path.read_text(encoding="utf-8", errors="replace")
        if item.get("sections"):
            text = "\n\n".join(
                section for section in
                (extract_section(text, name) for name in item["sections"])
                if section
            )
        elif item.get("partial"):
            lines = text.split("\n")
            headers = [line for line in lines if line.startswith("#")]
            first_lines = lines[:30]
            text = "\n".join(headers[:10]) + "\n\n[... TRUNCATED DUE TO LOW CONFIDENCE INTENT MATCH ...]\n\n" + "\n".join(first_lines)
        loaded.append({**item, "content": text})

    current = {}
    dashboard_path = root / "scripts/generate-dashboard.py"
    if args.feature and dashboard_path.is_file():
        dashboard = _load_dashboard_module(root)
        current = next((item for item in dashboard.scan_workspace(root)
                        if item["slug"] == args.feature), {})
    current_state = {
        "phase": current.get("phase", args.phase or ""),
        "task": current.get("active_task", args.task or ""),
        "blockers": current.get("blockers", "None"),
    }
    omitted = pack["omitted"]
    result = _result(
        "context-load", "ok", args.feature,
        [item["path"] for item in loaded],
        [f"{item['path']}: {item['reason']}" for item in omitted],
        next_action=current.get("next_step", "corezero status"),
        details={
            "selected": [{key: value for key, value in item.items() if key != "content"}
                         for item in loaded],
            "omitted": omitted,
            "estimated_tokens": pack["estimated_tokens"],
            "budget": pack["budget"],
            "current_state": current_state,
            "dry_run": args.dry_run,
        },
    )
    # Keep the stable loader fields at the top level for agent wrappers.
    result.update({
        "selected": loaded,
        "omitted": omitted,
        "estimated_tokens": pack["estimated_tokens"],
        "budget": pack["budget"],
        "current_state": current_state,
    })
    result["_context_text"] = loaded
    return result


def _memory_audit(args):
    root = _resolve_root(args)
    thresholds = {"memory_warn_lines": 100, "memory_breach_lines": 200, "memory_hard_lines": 3200}
    config = root / "core-zero/project/harness-config.yaml"
    if config.is_file():
        configured = (load_yaml(str(config)) or {}).get("thresholds", {})
        for key in thresholds:
            if key in configured:
                thresholds[key] = int(configured[key])
    roots = [
        (root / "core-zero/memories/repo", "repo"),
        (root / "core-zero/project", "project"),
        (root / "core-zero/memories/domain", "domain"),
    ]
    files = []
    for base, tier in roots:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = text.count("\n") + (1 if text else 0)
            tokens = estimate_tokens(text)
            warnings = []
            if lines >= thresholds["memory_hard_lines"]:
                warnings.append("hard-cap")
            elif lines >= thresholds["memory_breach_lines"]:
                warnings.append("threshold-breach")
            elif lines >= thresholds["memory_warn_lines"]:
                warnings.append("early-warning")
            files.append({
                "path": str(path.relative_to(root)), "tier": tier,
                "lines": lines, "tokens": tokens, "warnings": warnings,
            })
    warnings = [f"{item['path']}: {warning}" for item in files for warning in item["warnings"]]
    return _result("memory-audit", "ok", args.feature, [item["path"] for item in files], warnings,
                   next_action="corezero context-pack",
                   details={"files": files, "total_tokens": sum(item["tokens"] for item in files),
                            "total_lines": sum(item["lines"] for item in files),
                            "thresholds": thresholds, "dry_run": args.dry_run})


def _task_data(root, feature):
    path = feature_tasks_path(root, feature)
    if not path.is_file():
        raise ValueError(f"Tasks file not found: {path}")
    tasks = parse_tasks(path.read_text(encoding="utf-8", errors="replace"))
    cycle = detect_cycle(tasks)
    errors = []
    if cycle:
        errors.append("cycle: " + " -> ".join(cycle))
    known = {item["id"] for item in tasks}
    for item in tasks:
        for dependency in item["depends"]:
            if dependency not in known:
                errors.append(f"{item['id']} depends on missing {dependency}")
    return path, tasks, errors


def _task_command(args):
    root = _resolve_root(args)
    path, tasks, errors = _task_data(root, args.feature)
    if args.command == "task-next":
        ready = next_tasks(tasks) if not errors else []
        return _result(args.command, "failed" if errors else "ok", args.feature, [str(path)], errors,
                       details={"tasks": ready})
    if args.command in {"task-start", "task-update", "task-done", "task-block"}:
        return _task_update_command(args, path, tasks, errors)
    return _result(args.command, "failed" if errors else "ok", args.feature, [str(path)], errors,
                   next_action="corezero task-next --feature " + args.feature,
                   details={"task_count": len(tasks), "tasks": tasks})


def _task_update_command(args, path, tasks, errors):
    if errors:
        return _result(args.command, "failed", args.feature, [str(path)], errors)
    if not args.task:
        raise ValueError("--task is required")
    task = next((item for item in tasks if item["id"] == args.task), None)
    if not task:
        raise ValueError(f"task not found: {args.task}")

    target = args.status
    if args.command == "task-start":
        target = "In Progress"
    elif args.command == "task-done":
        target = "Done"
    elif args.command == "task-block":
        target = "Blocked"
    if not target:
        raise ValueError("--status is required for task-update")

    evidence = list(args.evidence)
    if args.evidence_file:
        evidence.append(_read_file(args.evidence_file, "evidence file"))
    if target == "Done" and not any(item.strip() for item in evidence):
        raise ValueError("task completion requires explicit validation evidence")
    if target == "Blocked" and not args.note.strip():
        raise ValueError("task blocking requires --note with the blocker reason")
    current_status = normalize_status(task["status"])
    if target not in ALLOWED_TRANSITIONS.get(current_status, set()):
        raise ValueError(f"invalid task transition: {current_status} -> {target}")
    if args.command == "task-start":
        by_id = {item["id"]: item for item in tasks}
        missing = [dep for dep in task["depends"] if dep not in by_id]
        blocked = [dep for dep in task["depends"] if dep in by_id and not by_id[dep]["done"]]
        if missing or blocked:
            detail = ", ".join(missing or blocked)
            raise ValueError(f"task has unfinished dependencies: {detail}")
    root = _resolve_root(args)
    updated, change = update_task_text(path, args.task, target, evidence=evidence, note=args.note)
    if not args.dry_run:
        atomic_write(path, updated)
    return _result(args.command, "ok", args.feature, [str(path)],
                   next_action="corezero task-next --feature " + args.feature,
                   details={"task": change, "dry_run": args.dry_run})


def _artifact_command(args):
    root = _resolve_root(args)
    feature_dir = root / "artifacts/features" / args.feature
    if not feature_dir.is_dir():
        raise ValueError(f"Feature directory not found: {feature_dir}")
    errors, warnings = check_structure(feature_dir, args.phase or None)
    details = {}
    if args.trace:
        report, trace_errors = traceability(feature_dir)
        details["traceability"] = report
        errors.extend(trace_errors)
    return _result(args.command, "failed" if errors else "ok", args.feature,
                   [str(feature_dir)], errors + warnings, details=details)


def _phase_command(args):
    root = _resolve_root(args)
    if not args.phase:
        raise ValueError("--phase is required")
    engine = root / "scripts/core/harness.py"
    command = [sys.executable, str(engine), "--root", str(root)]
    if args.json:
        command.append("--json")
    if args.dry_run:
        command.append("--dry-run")
    command.extend(["phase-gate", "--phase", args.phase, "--feature", args.feature])
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    payload = {"output": completed.stdout.strip(), "stderr": completed.stderr.strip()}
    return _result(args.command, "ok" if completed.returncode == 0 else "failed", args.feature,
                   [str(root / "core-zero/project/harness-config.yaml")],
                   [] if completed.returncode == 0 else [completed.stdout.strip() or completed.stderr.strip()],
                   details=payload)


def _verify(args):
    phase_values = vars(args).copy()
    phase_values.update(command="phase-check", phase=args.phase or "Verify", json=True)
    phase_args = argparse.Namespace(**phase_values)
    phase = _phase_command(phase_args)
    artifact_values = vars(args).copy()
    artifact_values.update(command="artifact-check", trace=True)
    artifact_args = argparse.Namespace(**artifact_values)
    artifact = _artifact_command(artifact_args)
    root = _resolve_root(args)
    gate = root / "scripts/harness/gate-runner.sh"
    command = [str(gate), "--root", str(root), "--feature", args.feature]
    if args.task:
        command.extend(["--task", args.task])
    if args.dry_run:
        command.append("--dry-run")
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    details = {"phase": phase, "artifacts": artifact, "gate_output": completed.stdout.strip(),
               "gate_stderr": completed.stderr.strip()}
    failed = phase["status"] != "ok" or artifact["status"] != "ok" or completed.returncode != 0
    return _result("verify", "failed" if failed else "ok", args.feature,
                   artifact["artifacts"], phase["warnings"] + artifact["warnings"],
                   next_action="/spec-implement" if failed else "/harness-verify", details=details)


def _require_feature(root, feature):
    status = Path(root) / "artifacts" / "features" / feature / "status.md"
    if not status.is_file():
        raise ValueError(
            f"Feature '{feature}' is not initialized: required artifact is missing: {status}"
        )


def _read_file(path, label):
    if not path:
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError(f"Cannot read {label} {path}: {exc}") from exc


def _section_text(args, title):
    if title == "Handoff":
        file_text = _read_file(args.handoff_file, "handoff file")
        if file_text:
            return file_text
        lines = []
        if args.objective:
            lines.append(f"- Objective: {args.objective}")
        if args.next_action:
            lines.append(f"- Next step: {args.next_action}")
        lines.extend(f"- Blocker: {item}" for item in args.blocker)
        lines.extend(f"- Decision: {item}" for item in args.decision)
        return "\n".join(lines)
    return args.progress or None


def _append_candidates(root, feature, candidates, extract_file):
    content = list(candidates)
    file_text = _read_file(extract_file, "extract file")
    if file_text:
        content.append(file_text)
    appendix = "\n\n".join(item.rstrip() for item in content if item.strip())
    if not appendix:
        return None
    path = Path(root) / "artifacts" / "features" / feature / "session-extracts.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else (
        f"# Session Extracts: {feature}\n<!-- triaged: false -->\n\n## Pending Candidates\n\n"
    )
    triaged = existing.find("\n## Triaged")
    if triaged >= 0:
        updated = existing[:triaged].rstrip() + "\n\n" + appendix + "\n" + existing[triaged:]
    else:
        updated = existing.rstrip() + "\n\n" + appendix + "\n"
    atomic_write(path, updated)
    return str(path)


def _domain_packs(args):
    import re
    root = _resolve_root(args)
    if not root:
        raise ValueError("Unable to locate repository root")
    domain_dir = Path(root) / "core-zero/memories/domain"
    packs = []
    if domain_dir.exists():
        for d in domain_dir.iterdir():
            if d.is_dir():
                glossary_file = d / "glossary.md"
                if glossary_file.exists():
                    triggers = []
                    content = glossary_file.read_text(encoding="utf-8")
                    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                    if m:
                        for line in m.group(1).split("\n"):
                            if line.strip().startswith("triggers:"):
                                val = line.split(":", 1)[1].strip()
                                if val.startswith("[") and val.endswith("]"):
                                    triggers = [t.strip().strip("'\"") for t in val[1:-1].split(",") if t.strip()]
                                else:
                                    triggers = [val]
                                break
                    packs.append({"domain": d.name, "triggers": triggers, "path": str(glossary_file.relative_to(root))})
    
    if getattr(args, "json", False):
        return {"status": "ok", "command": "domain-packs", "packs": packs}
    
    print(f"{'Domain':<20} | Triggers")
    print("-" * 40)
    for p in packs:
        trig_str = ", ".join(p["triggers"])
        print(f"{p['domain']:<20} | {trig_str}")
    return {"status": "ok", "command": "domain-packs"}


def _run(args):
    if args.command == "init":
        return _init(args)
    if args.command == "status":
        return _status(args)
    if args.command == "domain-packs":
        return _domain_packs(args)
    if args.command == "context-pack":
        return _context_pack(args)
    if args.command == "context-load":
        return _context_load(args)
    if args.command == "memory-audit":
        return _memory_audit(args)
    if args.command in {"task-check", "task-next", "task-start", "task-update", "task-done", "task-block"}:
        return _task_command(args)
    if args.command == "artifact-check":
        return _artifact_command(args)
    if args.command == "phase-check":
        return _phase_command(args)
    if args.command == "verify":
        return _verify(args)

    root = _resolve_root(args)
    if not root:
        raise ValueError("Unable to locate an initialized CoreZero repository")
    _require_feature(root, args.feature)

    session_path = default_session_path(root, args.feature)
    engine = ContextEngine(
        root=root,
        intent=args.intent,
        budget=args.budget,
        mode="full" if args.verbose else "summary",
        feature=args.feature,
        phase=args.phase,
        task=args.task,
        session_path=str(session_path),
    )
    if args.resume:
        engine.resume()

    output = io.StringIO()
    with contextlib.redirect_stdout(output) if not args.verbose else contextlib.nullcontext():
        engine.run_session_start(phase=engine.phase or None, mode=engine.mode)
    engine.session_metadata["session_event"] = args.command
    engine.write_session(
        objective=args.objective,
        next_action=args.next_action,
        blockers=args.blocker if args.blocker else None,
        decisions=args.decision if args.decision else None,
    )

    progress = _section_text(args, "Progress")
    handoff = _section_text(args, "Handoff")
    if progress is not None or handoff:
        update_session_sections(session_path, progress=progress, handoff=handoff or None)

    extracts = None
    if args.command == "session-end":
        extracts = _append_candidates(root, args.feature, args.candidate, args.extract_file)

    metadata = load_session(session_path)["metadata"]
    result = {
        "command": args.command,
        "feature": args.feature,
        "session": str(session_path),
        "extracts": extracts,
        "loaded_count": metadata.get("loaded_count", 0),
        "omitted_count": metadata.get("omitted_count", 0),
        "total_tokens": metadata.get("total_tokens", 0),
        "warnings": metadata.get("warnings", []),
    }
    if args.verbose and output.getvalue():
        print(output.getvalue(), end="")
    return result


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        result = _run(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if result.get("status") == "failed":
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['command']}: FAILED", file=sys.stderr)
            for warning in result.get("warnings", []):
                print(warning, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({key: value for key, value in result.items()
                          if key != "_context_text"}, indent=2))
    else:
        if args.command == "context-load":
            for item in result.get("_context_text", []):
                print(f"[{item['path']}{' :: ' + ', '.join(item['sections']) if item.get('sections') else ''}]")
                print(item["content"])
                print()
            for warning in result.get("warnings", []):
                print(f"Omitted: {warning}", file=sys.stderr)
            if args.verbose:
                print(f"Loaded: {len(result.get('selected', []))} source(s); "
                      f"estimated tokens: {result.get('estimated_tokens', 0)}",
                      file=sys.stderr)
            if result.get("next_action"):
                print(f"Next: {result['next_action']}", file=sys.stderr)
            return 0
        print(f"{result['command']}: OK")
        if result.get("session"):
            print(f"Session: {result['session']}")
        if result.get("loaded_count") is not None:
            print(f"Context: {result['loaded_count']} loaded, {result['total_tokens']} estimated tokens")
        if result.get("next_action"):
            print(f"Next: {result['next_action']}")
        if result.get("extracts"):
            print(f"Extracts: {result['extracts']}")
        if result.get("details", {}).get("features"):
            for feature in result["details"]["features"]:
                print(f"{feature['slug']}\t{feature['phase']}\t{feature['progress'].get('completed', 0)}/{feature['progress'].get('total', 0)}\t{feature['next_step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Parse tasks.md Depends-on graph; emit next unblocked tasks; detect cycles.

Stdlib only. Markdown stays source of truth.
Usage:
  python3 scripts/core/task_graph.py --feature <slug>
  python3 scripts/core/task_graph.py --file path/to/tasks.md --all
  python3 scripts/core/task_graph.py --file path/to/tasks.md --check
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core._lib.root import resolve_root

TASK_ID_RE = re.compile(r"\bTASK-(\d+)\b")
# Checkbox task header: - [ ] TASK-001 or - [x] TASK-001-title
TASK_HEADER_RE = re.compile(
    r"^(\s*)[-*]\s+\[([ xX])\]\s+(TASK-\d+)\b(.*)$",
    re.MULTILINE,
)
# Depends-on / Depends on: TASK-001, TASK-002
DEPENDS_RE = re.compile(
    r"(?im)^\s*Depends[- ]on:\s*(.*)$",
)
STATUS_RE = re.compile(r"(?im)^\s*Status:\s*(.+)$")
DONE_STATUSES = {"done", "deferred"}


def _normalize_id(token: str) -> str | None:
    m = TASK_ID_RE.search(token or "")
    if not m:
        return None
    return f"TASK-{int(m.group(1)):03d}" if False else f"TASK-{m.group(1)}"


def parse_tasks(text: str) -> list[dict]:
    """Return list of {id, done, depends, status, header} in file order."""
    if not text:
        return []
    headers = list(TASK_HEADER_RE.finditer(text))
    tasks = []
    for i, m in enumerate(headers):
        start = m.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]
        tid = m.group(3)
        checked = m.group(2).lower() == "x"
        status_m = STATUS_RE.search(block)
        status = (status_m.group(1).strip() if status_m else "").strip()
        done = checked or status.lower() in DONE_STATUSES
        deps = []
        for dm in DEPENDS_RE.finditer(block):
            raw = dm.group(1).strip()
            if not raw or raw in ("—", "-", "n/a", "N/A", "none", "None"):
                continue
            for part in re.split(r"[,;\s]+", raw):
                dep = _normalize_id(part)
                if dep and dep != tid:
                    deps.append(dep)
        # de-dupe preserve order
        seen = set()
        uniq = []
        for d in deps:
            if d not in seen:
                seen.add(d)
                uniq.append(d)
        tasks.append(
            {
                "id": tid,
                "done": done,
                "depends": uniq,
                "status": status or ("Done" if done else "Not Started"),
                "header": m.group(0).strip(),
            }
        )
    return tasks


def detect_cycle(tasks: list[dict]) -> list[str] | None:
    """Return cycle path (ids) if any, else None."""
    graph = {t["id"]: list(t["depends"]) for t in tasks}
    ids = set(graph)
    # ignore deps that are not in this file (external)
    for tid in list(graph):
        graph[tid] = [d for d in graph[tid] if d in ids]

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {t: WHITE for t in graph}
    parent = {}

    def dfs(u):
        color[u] = GRAY
        for v in graph[u]:
            if color[v] == GRAY:
                # reconstruct cycle
                cyc = [v, u]
                x = u
                while x != v and x in parent:
                    x = parent[x]
                    cyc.append(x)
                cyc.reverse()
                return cyc
            if color[v] == WHITE:
                parent[v] = u
                found = dfs(v)
                if found:
                    return found
        color[u] = BLACK
        return None

    for t in graph:
        if color[t] == WHITE:
            found = dfs(t)
            if found:
                return found
    return None


def next_tasks(tasks: list[dict]) -> list[dict]:
    """Incomplete tasks whose Depends-on are all done (or empty).

    If no task has Depends-on filled, fall back to first incomplete in file order.
    """
    by_id = {t["id"]: t for t in tasks}
    any_deps = any(t["depends"] for t in tasks)
    incomplete = [t for t in tasks if not t["done"]]
    if not incomplete:
        return []
    if not any_deps:
        return [incomplete[0]]

    ready = []
    for t in incomplete:
        deps = t["depends"]
        if not deps:
            ready.append(t)
            continue
        if all(by_id.get(d, {}).get("done", False) for d in deps if d in by_id):
            # unknown external deps treated as satisfied only if not in file;
            # already filtered: missing ids → block
            missing = [d for d in deps if d not in by_id]
            if missing:
                continue
            if all(by_id[d]["done"] for d in deps):
                ready.append(t)
    return ready


def feature_tasks_path(root: Path, slug: str) -> Path:
    return root / "artifacts" / "features" / slug / "tasks.md"


def format_next(ready: list[dict]) -> str:
    if not ready:
        return "(no unblocked tasks — all done or all blocked)"
    lines = []
    for t in ready:
        deps = ", ".join(t["depends"]) if t["depends"] else "—"
        lines.append(f"{t['id']}\tdeps={deps}\tstatus={t['status']}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Task dependency graph helpers")
    p.add_argument("--root", default="", help="Repo root")
    p.add_argument("--feature", default="", help="Feature slug")
    p.add_argument("--file", default="", help="Path to tasks.md")
    p.add_argument("--check", action="store_true", help="Exit 1 on cycle or missing deps")
    p.add_argument("--all", action="store_true", help="Print all parsed tasks")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args(argv)

    if args.file:
        path = Path(args.file)
    elif args.feature:
        root = resolve_root(args.root)
        if not root:
            print("ERROR: could not resolve repo root", file=sys.stderr)
            return 2
        path = feature_tasks_path(Path(root), args.feature)
    else:
        p.print_help()
        return 2

    if not path.is_file():
        print(f"ERROR: tasks file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8", errors="replace")
    tasks = parse_tasks(text)
    cycle = detect_cycle(tasks)

    if args.check:
        errors = []
        if cycle:
            errors.append("cycle: " + " → ".join(cycle))
        known = {t["id"] for t in tasks}
        for t in tasks:
            for d in t["depends"]:
                if d not in known:
                    errors.append(f"{t['id']} depends on missing {d}")
        if errors:
            for e in errors:
                print(f"FAIL: {e}")
            return 1
        print(f"PASS: {len(tasks)} task(s), no cycles")
        return 0

    if args.all:
        if args.json:
            import json

            print(json.dumps(tasks, indent=2))
        else:
            for t in tasks:
                mark = "x" if t["done"] else " "
                print(f"[{mark}] {t['id']} deps={t['depends']} status={t['status']}")
        return 0

    if cycle:
        print(f"FAIL: cycle detected: {' → '.join(cycle)}", file=sys.stderr)
        return 1

    ready = next_tasks(tasks)
    if args.json:
        import json

        print(json.dumps(ready, indent=2))
    else:
        print(format_next(ready))
    return 0


if __name__ == "__main__":
    sys.exit(main())

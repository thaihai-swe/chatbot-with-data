#!/usr/bin/env python3
"""Compress markdown table separator rows: replace multi-dash runs with a single `-`.

Usage:
    python3 kit/scripts/compress-table-seps.py [<path>]

If <path> is a file, processes that file.
If <path> is a directory, walks it recursively and processes all .md files.
Defaults to '.' (current directory).
"""

import os
import re
import sys

SEPARATOR_RE = re.compile(r'^\|(?:[\s:-]*\|)+$')
DASH_RUN_RE = re.compile(r'-{2,}')


def compress_table_separators(text: str) -> tuple[str, bool]:
    lines = text.splitlines(keepends=True)
    changed = False
    out = []
    for line in lines:
        if SEPARATOR_RE.match(line.strip()):
            new = DASH_RUN_RE.sub('-', line)
            if new != line:
                changed = True
                out.append(new)
                continue
        out.append(line)
    return ''.join(out), changed


def process_file(path: str) -> bool:
    with open(path) as f:
        content = f.read()
    result, changed = compress_table_separators(content)
    if changed:
        with open(path, 'w') as f:
            f.write(result)
        print(f"  modified: {path}")
    return changed


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    if os.path.isfile(root):
        process_file(root)
        return

    count = 0
    for dirpath, _, fns in os.walk(root):
        for fn in fns:
            if not fn.endswith('.md'):
                continue
            if process_file(os.path.join(dirpath, fn)):
                count += 1

    if count:
        print(f"\n{count} file(s) modified.")
    else:
        print("No table separators found.")


if __name__ == '__main__':
    main()

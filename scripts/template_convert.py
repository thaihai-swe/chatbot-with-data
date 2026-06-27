#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core.template_engine import convert_template, TemplateEngine


def main():
    parser = argparse.ArgumentParser(description="CoreZero Template Converter")
    parser.add_argument("--template", required=True, help="Template file to convert")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without saving")
    parser.add_argument("--batch", default="", help="Directory to batch-convert all .md files")
    args = parser.parse_args()

    if args.batch:
        total = 0
        converted = 0
        for path in sorted(Path(args.batch).rglob("*.md")):
            if "node_modules" in str(path):
                continue
            total += 1
            engine = TemplateEngine()
            text = path.read_text(encoding="utf-8")
            ph = engine.detect_placeholders(text)
            if ph:
                converted += 1
                if args.dry_run:
                    print(f"[dry-run] Would convert {path} ({len(ph)} placeholders)")
                else:
                    for p in ph:
                        text = text.replace(f"<{p}>", f"{{{{{p}}}}}")
                        text = text.replace(f"{{{p}}}", f"{{{{{p}}}}}")
                    path.write_text(text, encoding="utf-8")
                    print(f"Converted {path} ({len(ph)} placeholders)")
        print(f"Scanned {total} files, converted {converted}")
    else:
        convert_template(args.template, args.dry_run)


if __name__ == "__main__":
    main()

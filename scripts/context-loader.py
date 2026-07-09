#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core.context_engine import ContextEngine


def main():
    parser = argparse.ArgumentParser(description="CoreZero Context Loader: Enforces Minimum Viable Context (MVC).")
    parser.add_argument("filepath", nargs="?", help="Path to the markdown file to load")
    parser.add_argument("--mode", choices=["full", "summary", "partial", "scored", "compress", "outline"], default="full",
                        help="Load mode")
    parser.add_argument("--intent", default="", help="Intent keywords for scoring")
    parser.add_argument("--budget", type=int, default=0, help="Token budget")
    parser.add_argument("--route", default="",
                        help="Phase name to load via Phase×Guidance Matrix (spec/plan/implement/verify)")
    parser.add_argument("--section", default="",
                        help="Load only the named ## H2 section (case-insensitive)")
    parser.add_argument("--session-start", action="store_true",
                        help="Load Always-group files (+ optional --route phase matrix)")
    parser.add_argument("--phase", default="",
                        help="With --session-start: also load Phase×Guidance Matrix for this phase")
    args = parser.parse_args()

    if args.session_start:
        mode = args.mode if args.mode != "full" else "summary"
        engine = ContextEngine(root="", intent=args.intent, budget=args.budget, mode=mode)
        engine.run_session_start(phase=args.phase or args.route or None, mode=mode)
    elif args.route:
        engine = ContextEngine(root="", intent=args.intent, budget=args.budget, mode=args.mode)
        engine.run_route(args.route, args.mode)
    elif args.filepath:
        if not os.path.exists(args.filepath):
            print(f"Error: File '{args.filepath}' does not exist.", file=sys.stderr)
            sys.exit(1)
        engine = ContextEngine(root="", intent=args.intent, budget=args.budget, mode=args.mode)
        sections = [args.section] if args.section else None
        engine.process_file(args.filepath, sections=sections)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

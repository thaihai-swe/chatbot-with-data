#!/usr/bin/env python3
import argparse
import sys
import os

def extract_summary(filepath, max_lines=50):
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    in_index_section = False
    index_lines = []
    
    for line in lines:
        if line.startswith("## Index"):
            in_index_section = True
            index_lines.append(line)
            continue
            
        if in_index_section:
            if line.startswith("## "):
                break
            index_lines.append(line)

    if index_lines:
        return "".join(index_lines)
    else:
        # Fallback to first N lines
        return "".join(lines[:max_lines])

def main():
    parser = argparse.ArgumentParser(description="CoreZero Context Loader: Enforces Minimum Viable Context (MVC).")
    parser.add_argument("filepath", help="Path to the markdown file to load")
    parser.add_argument("--mode", choices=["full", "summary"], default="full", 
                        help="Load mode: 'full' reads the entire file, 'summary' extracts the Index or first 50 lines.")
    
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print(f"Error: File '{args.filepath}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.mode == "summary":
        output = extract_summary(args.filepath)
        print(output, end="")
    else:
        try:
            with open(args.filepath, 'r') as f:
                print(f.read(), end="")
        except Exception as e:
            print(f"Error reading {args.filepath}: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()

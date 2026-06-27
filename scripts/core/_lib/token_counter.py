import re
from pathlib import Path

CHARS_PER_TOKEN = 4.0

def estimate_tokens(text):
    if not text:
        return 0
    return int(len(text) / CHARS_PER_TOKEN)

def count_tokens(text):
    return estimate_tokens(text)

def estimate_file_tokens(path):
    return estimate_tokens(Path(path).read_text(encoding="utf-8"))

def process_text(text, budget, mode="summary"):
    tokens = estimate_tokens(text)
    if tokens <= budget:
        return text, tokens
    if mode == "summary":
        lines = text.split("\n")
        summary_lines = []
        seen_index = False
        count = 0
        for line in lines:
            summary_lines.append(line)
            count += 1
            if line.strip().startswith("## Index"):
                seen_index = True
            if seen_index and not line.strip().startswith("## ") and line.strip():
                if count > 60:
                    break
        if not seen_index:
            # No ## Index found; fall back to first 30 lines
            summary_lines = lines[:30]
        truncated = "\n".join(summary_lines)
        return truncated, estimate_tokens(truncated)
    if mode == "partial":
        lines = text.split("\n")
        result = []
        count = 0
        for line in lines:
            result.append(line)
            count += 1
            if line.strip().startswith("## ") and count > 5:
                section_count = 0
                for l in lines[count:]:
                    if l.strip().startswith("## "):
                        section_count += 1
                        if section_count > 3:
                            break
                    result.append(l)
                break
        partial = "\n".join(result)
        tok = estimate_tokens(partial)
        if tok > budget:
            partial = "\n".join(result[:int(len(result) * budget / tok)])
        return partial, estimate_tokens(partial)
    if mode == "head":
        lines = text.split("\n")
        head_budget = int(len(lines) * (budget / tokens))
        truncated = "\n".join(lines[:max(1, head_budget)])
        return truncated, estimate_tokens(truncated)
    return text, tokens

def read_with_budget(path, budget, mode="summary"):
    text = Path(path).read_text(encoding="utf-8")
    return process_text(text, budget, mode)

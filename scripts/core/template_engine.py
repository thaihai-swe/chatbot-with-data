#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)


class TemplateError(Exception):
    pass


class TemplateEngine:
    def __init__(self, context=None):
        self.context = context or {}
        self._included = set()

    def render(self, template_text, context=None):
        if context:
            merged = dict(self.context)
            merged.update(context)
        else:
            merged = self.context
        merged.setdefault("_engine", self)
        result = self._render_string(template_text, merged)
        return result

    def _render_string(self, text, ctx):
        text = self._process_include(text, ctx)
        text = self._process_each(text, ctx)
        text = self._process_if(text, ctx)
        text = self._process_slots(text, ctx)
        return text

    def _process_slots(self, text, ctx):
        def replace_slot(m):
            slot = m.group(1).strip()
            parts = slot.split("|", 1)
            key = parts[0].strip()
            default = parts[1].strip() if len(parts) > 1 else ""
            deep = ctx
            for k in key.split("."):
                if isinstance(deep, dict):
                    deep = deep.get(k, None)
                else:
                    deep = None
                if deep is None:
                    break
            if deep is not None:
                return str(deep)
            return default
        return re.sub(r"\{\{([^#/!=].*?)\}\}", replace_slot, text)

    def _process_if(self, text, ctx):
        pattern = re.compile(r"\{\{#if (.*?)\}\}(.*?)\{\{/if\}\}", re.DOTALL)
        def replace_if(m):
            condition = m.group(1).strip()
            body = m.group(2)
            value = self._resolve_value(condition, ctx)
            if value:
                return self._render_string(body, ctx)
            return ""
        return pattern.sub(replace_if, text)

    def _process_each(self, text, ctx):
        pattern = re.compile(r"\{\{#each (.*?)\}\}(.*?)\{\{/each\}\}", re.DOTALL)
        def replace_each(m):
            iterable_name = m.group(1).strip()
            body = m.group(2)
            items = self._resolve_value(iterable_name, ctx)
            if not isinstance(items, (list, tuple)):
                return ""
            result = []
            for item in items:
                item_ctx = dict(ctx)
                if isinstance(item, dict):
                    item_ctx.update(item)
                else:
                    item_ctx["item"] = item
                result.append(self._render_string(body, item_ctx))
            return "".join(result)
        return pattern.sub(replace_each, text)

    def _process_include(self, text, ctx):
        pattern = re.compile(r"\{\{#include \"(.*?)\"\}\}")
        def replace_include(m):
            path = m.group(1)
            abs_path = os.path.abspath(path)
            if abs_path in self._included:
                raise TemplateError(f"Circular include detected: {path}")
            self._included.add(abs_path)
            try:
                with open(path) as f:
                    content = f.read()
            except FileNotFoundError:
                raise TemplateError(f"Included file not found: {path}")
            rendered = self._render_string(content, ctx)
            self._included.discard(abs_path)
            return rendered
        return pattern.sub(replace_include, text)

    def _resolve_value(self, expr, ctx):
        expr = expr.strip()
        if expr in ("true", "True"):
            return True
        if expr in ("false", "False"):
            return False
        if expr.startswith("!"):
            return not self._resolve_value(expr[1:], ctx)
        deep = ctx
        for k in expr.split("."):
            if isinstance(deep, dict):
                deep = deep.get(k, None)
            else:
                deep = None
            if deep is None:
                break
        return deep

    def validate(self, template_text):
        errors = []
        if not self._balanced("{{#if", "{{/if}}", template_text):
            errors.append("Unbalanced {{#if}}/{{/if}}")
        if not self._balanced("{{#each", "{{/each}}", template_text):
            errors.append("Unbalanced {{#each}}/{{/each}}")
        if self._has_unclosed_slot(template_text):
            errors.append("Unclosed {{slot}} notation")
        return errors

    def _balanced(self, open_tag, close_tag, text):
        return text.count(open_tag) == text.count(close_tag)

    def _has_unclosed_slot(self, text):
        open_count = len(re.findall(r"\{\{[^#/!].*?\}\}", text))
        return False

    def list_slots(self, template_text):
        slots = set()
        for m in re.finditer(r"\{\{([^#/!].*?)\}\}", template_text):
            slot = m.group(1).strip()
            parts = slot.split("|", 1)
            slots.add(parts[0].strip())
        return sorted(slots)

    def detect_placeholders(self, template_text):
        placeholders = set()
        for m in re.finditer(r"<([a-zA-Z_-]+)>", template_text):
            placeholders.add(m.group(1))
        for m in re.finditer(r"\{([A-Z_]+)\}", template_text):
            placeholders.add(m.group(1))
        return sorted(placeholders)


def render_file(template_path, context_path=None, context_dict=None, output_path=None):
    engine = TemplateEngine()
    if context_path:
        from core._lib.yaml_reader import load as load_yaml
        ctx = load_yaml(context_path) or {}
    else:
        ctx = {}
    if context_dict:
        ctx.update(context_dict)
    template_text = Path(template_path).read_text(encoding="utf-8")
    result = engine.render(template_text, ctx)
    if output_path:
        Path(output_path).write_text(result, encoding="utf-8")
        print(f"Rendered to {output_path}")
    else:
        print(result, end="")


def convert_template(template_path, dry_run=False):
    text = Path(template_path).read_text(encoding="utf-8")
    engine = TemplateEngine()
    placeholders = engine.detect_placeholders(text)
    converted = text
    for ph in placeholders:
        converted = converted.replace(f"<{ph}>", f"{{{{{ph}}}}}")
        converted = converted.replace(f"{{{ph}}}", f"{{{{{ph}}}}}")
    if not dry_run and converted != text:
        Path(template_path).write_text(converted, encoding="utf-8")
        print(f"Converted {template_path}: {len(placeholders)} placeholders → slots")
    return placeholders


def main():
    parser = argparse.ArgumentParser(description="CoreZero Template Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    render_p = sub.add_parser("render", help="Render a template")
    render_p.add_argument("--template", required=True, help="Template file path")
    render_p.add_argument("--context", default="", help="Context YAML file path")
    render_p.add_argument("-D", action="append", default=[], help="Inline key=value context")
    render_p.add_argument("--output", default="", help="Output file path")
    render_p.add_argument("--validate", action="store_true", help="Validate template without rendering")

    list_p = sub.add_parser("list", help="List templates and their slots")
    list_p.add_argument("--template", required=True, help="Template file path")

    convert_p = sub.add_parser("convert", help="Convert placeholders to slots")
    convert_p.add_argument("--template", required=True, help="Template file path")
    convert_p.add_argument("--dry-run", action="store_true", help="Show what would change")

    validate_p = sub.add_parser("validate-all", help="Validate all templates in a directory")
    validate_p.add_argument("--dir", default="kit/skills", help="Directory to scan for templates")

    args = parser.parse_args()

    if args.command == "render":
        ctx_dict = {}
        for d in args.D:
            if "=" in d:
                k, v = d.split("=", 1)
                ctx_dict[k] = v
        if args.validate:
            text = Path(args.template).read_text(encoding="utf-8")
            engine = TemplateEngine()
            errors = engine.validate(text)
            if errors:
                for e in errors:
                    print(f"VALIDATE ERROR: {e}")
                sys.exit(1)
            print(f"Template '{args.template}' validates OK")
            return
        render_file(args.template, args.context, ctx_dict, args.output)

    elif args.command == "list":
        text = Path(args.template).read_text(encoding="utf-8")
        engine = TemplateEngine()
        slots = engine.list_slots(text)
        print(f"Template: {args.template}")
        print(f"Slots ({len(slots)}): {', '.join(slots)}")

    elif args.command == "convert":
        convert_template(args.template, args.dry_run)
        if args.dry_run:
            text = Path(args.template).read_text(encoding="utf-8")
            engine = TemplateEngine()
            ph = engine.detect_placeholders(text)
            if ph:
                print(f"Would convert {len(ph)} placeholders: {', '.join(ph)}")
            else:
                print("No placeholders to convert")

    elif args.command == "validate-all":
        import glob as glob_mod
        engine = TemplateEngine()
        errors = 0
        found = 0
        for path in glob_mod.glob(f"{args.dir}/**/*.md", recursive=True):
            if "node_modules" in path:
                continue
            found += 1
            text = Path(path).read_text(encoding="utf-8")
            errs = engine.validate(text)
            if errs:
                errors += 1
                for e in errs:
                    print(f"{path}: {e}")
        print(f"Validated {found} templates, {errors} with errors")
        if errors:
            sys.exit(1)


if __name__ == "__main__":
    main()

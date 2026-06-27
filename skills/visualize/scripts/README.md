# CoreZero Visualize Scripts

Helper scripts for deterministic SVG generation and Mermaid validation.

## Scripts

### `generate-from-template.py`

Style-driven SVG generator backed by `templates/*.svg`.

Usage:

```bash
source .venv/bin/activate
python3 ./skills/visualize/scripts/generate-from-template.py \
  architecture \
  ./out/architecture.svg \
  '{"style":1,"title":"My Diagram","nodes":[],"arrows":[]}'
```

### `validate-svg.sh`

SVG validator with structural checks beyond plain XML parsing.

Usage:

```bash
./skills/visualize/scripts/validate-svg.sh ./out/architecture.svg
```

Checks:
- XML syntax
- tag balance
- quoted attributes
- marker references
- basic arrow-to-component collisions

### `validate_mermaid.py`

Mermaid validator.

Usage:

```bash
source .venv/bin/activate
python3 ./skills/visualize/scripts/validate_mermaid.py ./out/diagram.mmd
```

Behavior:
- fails fast on empty files
- checks basic Mermaid structure
- uses `mmdc` for parser-level validation when installed
- reports clearly when `mmdc` is missing

### `render_mermaid.py`

Optional Mermaid-to-SVG renderer.

Usage:

```bash
source .venv/bin/activate
python3 ./skills/visualize/scripts/render_mermaid.py ./out/diagram.mmd ./out/diagram.svg
```

Requirements:
## Scope

These scripts support the implemented output paths in this repo:
- SVG generation and validation
- Mermaid validation
- Mermaid-to-SVG rendering when `mmdc` is available

They do not support:
- PNG export
- PlantUML generation
- draw.io generation

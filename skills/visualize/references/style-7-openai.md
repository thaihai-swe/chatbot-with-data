# Style 7: OpenAI Official

Clean, modern aesthetic matching OpenAI's documentation and research diagrams — minimal but precise.

## Color Palette

```
Background:     #ffffff  (pure white)
Primary text:   #0d0d0d  (near black)
Secondary text: #6e6e80  (muted gray)
Border:         #e5e5e5  (light gray)

Accent colors (reserved):
  Green accent:   #10a37f  (OpenAI brand green)
  Blue accent:    #1d4ed8  (links, actions)
  Orange accent:  #f97316  (highlights, warnings)
  Gray accent:    #71717a  (secondary elements)
```

## Typography

```
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei',
             'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   16px node labels, 13px descriptions, 12px arrow labels
font-weight: 600 for titles, 500 for labels, 400 for descriptions
letter-spacing: -0.01em (tight)
```

No custom fonts. System font stack only for maximum compatibility.

## Node Boxes

Clean, minimal boxes with subtle borders:

```xml
<!-- Default node -->
<rect x="100" y="100" width="180" height="80" rx="8" ry="8"
      fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>

<!-- Accent node (with green left-border strip) -->
<rect x="100" y="100" width="180" height="80" rx="8" ry="8"
      fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>
<rect x="100" y="100" width="4" height="80" rx="2" ry="2"
      fill="#10a37f"/>

<!-- Section header area (tinted) -->
<rect rx="8" fill="#f7f7f8" stroke="#e5e5e5" stroke-width="1"/>
```

**Key techniques:**
1. White fill with light gray border (no shadows).
2. Optional colored left-border accent strip (4px wide).
3. `rx="8"` for subtle rounding.
4. `stroke-width: 1.5` — thin, precise borders.
5. No gradients, no shadows, no decorative elements.

## Arrows

Thin, precise arrows with subtle colors:

```xml
<defs>
  <!-- Default arrow (gray) -->
  <marker id="arrow-oai" markerWidth="10" markerHeight="7"
          refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#71717a"/>
  </marker>

  <!-- Accent arrow (green) -->
  <marker id="arrow-oai-green" markerWidth="10" markerHeight="7"
          refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#10a37f"/>
  </marker>
</defs>

<!-- Default connection -->
<line stroke="#71717a" stroke-width="1.5" marker-end="url(#arrow-oai)"/>

<!-- Accent connection (primary flow) -->
<line stroke="#10a37f" stroke-width="1.5" marker-end="url(#arrow-oai-green)"/>

<!-- Dashed connection (async/optional) -->
<line stroke="#71717a" stroke-width="1.5" stroke-dasharray="4,3"
      marker-end="url(#arrow-oai)"/>
```

## Containers / Sections

```xml
<!-- Section box (subtle gray background) -->
<rect rx="8" fill="#f7f7f8" stroke="#e5e5e5" stroke-width="1"/>
<!-- Section header inside box -->
<text fill="#6e6e80" font-size="11" font-weight="600" letter-spacing="0.04em">SECTION</text>
```

## Best For

- OpenAI API integration diagrams
- Clean, modern product documentation
- Research paper appendix diagrams
- Enterprise white-label technical content
- Minimal-aesthetic presentations

## Example Title Block

```xml
<!-- Minimal left-aligned title (OpenAI doc style) -->
<text x="40" y="42" fill="#0d0d0d" font-size="20" font-weight="600">
  API Integration Flow
</text>
<text x="40" y="62" fill="#6e6e80" font-size="13">
  Three-section flow: Entry → Model + Tools → Delivery
</text>
<!-- Thin separator line -->
<line x1="40" y1="72" x2="920" y2="72" stroke="#e5e5e5" stroke-width="1"/>
```

# Style 4: Notion Clean

Minimal, documentation-friendly. Designed to embed in Notion, Confluence, or GitHub wikis.

## Colors

```
Background:     #ffffff
Box fill:       #f9fafb  (gray-50) or #ffffff
Box stroke:     #e5e7eb  (gray-200)
Box radius:     4px

Text primary:   #111827  (gray-900)
Text secondary: #374151  (gray-700)
Text muted:     #9ca3af  (gray-400)
Text label:     #6b7280  (gray-500), uppercase, 11px

Accent (subtle, used sparingly):
  Blue:   #3b82f6 (arrows only)
  Gray:   #d1d5db (dividers)
```

## Design Principles

- **No decorative icons** — use geometric shapes only (rect, circle, diamond).
- **Generous whitespace** — 24px+ padding between elements.
- **Single arrow color** — blue (#3b82f6) for all connections.
- **Labels in ALL CAPS** — section headers and node type labels.
- **No drop shadows** — flat only.

## Typography

```
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
             'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei',
             'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   14px labels, 11px uppercase type labels, 18px title
font-weight: 400 normal, 500 medium for node labels
```

## Box Styles

```xml
<!-- Default node -->
<rect rx="4" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1"/>
<text fill="#111827" font-size="14" font-weight="500"/>

<!-- Type label (inside or above box) -->
<text fill="#9ca3af" font-size="10" font-weight="600" letter-spacing="0.08em">TYPE</text>

<!-- Divider line between sections -->
<line stroke="#e5e7eb" stroke-width="1"/>

<!-- Highlighted / active node -->
<rect rx="4" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1"/>
```

## Arrow Styles

```xml
<defs>
  <marker id="arrow-notion" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#3b82f6"/>
  </marker>
</defs>

<!-- All connections use same blue arrow -->
<line stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arrow-notion)"/>

<!-- Dashed arrow (for optional/async flows) -->
<line stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arrow-notion)"/>
```

## Containers

```xml
<!-- Group container (subtle dashed border) -->
<rect rx="6" fill="none" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="4,4"/>
<!-- Section label above container -->
<text fill="#6b7280" font-size="11" font-weight="600" letter-spacing="0.05em">SECTION NAME</text>
```

## Best For

- Notion pages and Confluence wikis
- Internal documentation
- Team knowledge bases
- GitHub repository diagrams
- Minimal product documentation

## Example Title Block

```xml
<!-- Minimal title, no decoration -->
<text x="480" y="40" text-anchor="middle" fill="#111827" font-size="22" font-weight="600">
  Diagram Title
</text>
<!-- Optional subtitle in muted gray -->
<text x="480" y="62" text-anchor="middle" fill="#6b7280" font-size="13">
  Description
</text>
<!-- Thin divider under title -->
<line x1="360" y1="74" x2="600" y2="74" stroke="#e5e7eb" stroke-width="1"/>
```

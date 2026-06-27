# Style 1: Flat Icon (Default)

Inspired by draw.io defaults and Apple documentation style.

## Colors

```
Background:     #ffffff
Box fill:       #ffffff
Box stroke:     #d1d5db  (gray-300)
Box radius:     8px
Text primary:   #111827  (gray-900)
Text secondary: #6b7280  (gray-500)

Semantic arrow colors (pick by flow type):
  Flow A (main):   #2563eb  (blue-600)
  Flow B (alt):    #dc2626  (red-600)
  Flow C (data):   #16a34a  (green-600)
  Flow D (async):  #9333ea  (purple-600)

Icon accent backgrounds:
  Blue tint:   #eff6ff / #dbeafe
  Red tint:    #fef2f2 / #fee2e2
  Green tint:  #f0fdf4 / #dcfce7
  Purple tint: #faf5ff / #ede9fe
  Orange tint: #fff7ed / #fed7aa
  Teal tint:   #f0fdfa / #ccfbf1
```

## Typography

```
font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC',
             'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   14px labels, 12px sub-labels, 16px titles
font-weight: 400 normal, 600 semi-bold for titles
```

## Box Shapes

```xml
<!-- Default node box -->
<rect rx="8" ry="8" fill="#ffffff" stroke="#d1d5db" stroke-width="1.5"/>

<!-- Icon accent box (colored background) -->
<rect rx="8" ry="8" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>

<!-- Database cylinder (use SVG path) -->
<!-- Terminal box: rx=4, fill=#111827, stroke=#374151 -->
<!-- User/actor: circle or rounded rect with icon -->
```

## Arrow Styles

```xml
<defs>
  <marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
  </marker>
  <marker id="arrow-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>
  </marker>
  <marker id="arrow-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#9333ea"/>
  </marker>
</defs>

<!-- Primary flow -->
<line stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>

<!-- Async / event (dashed) -->
<line stroke="#9333ea" stroke-width="1.5" stroke-dasharray="4,2" marker-end="url(#arrow-purple)"/>

<!-- Memory write (dashed) -->
<line stroke="#16a34a" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arrow-green)"/>
```

## Containers (Swim Lanes)

```xml
<!-- Layer container / swim lane -->
<rect rx="6" fill="none" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="6,3"/>
<!-- Layer label (left edge, rotated) -->
<text transform="rotate(-90)" text-anchor="middle" fill="#9ca3af" font-size="11" font-weight="600"
      letter-spacing="0.08em">LAYER NAME</text>
```

## Best For

- Blog posts and technical articles
- Presentation slides
- Product documentation
- API reference diagrams
- Light-mode interfaces

## Example Title Block

```xml
<text x="480" y="40" text-anchor="middle" fill="#111827" font-size="20" font-weight="600">
  Diagram Title
</text>
<text x="480" y="60" text-anchor="middle" fill="#6b7280" font-size="13">
  Subtitle or description
</text>
```

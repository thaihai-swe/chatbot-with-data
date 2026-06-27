# Style 2: Dark Terminal

Neon-on-dark hacker aesthetic. Matches GitHub dark mode and dev-tool aesthetics.

## Colors

```
Background:     #0f0f1a  (near-black)
Panel fill:     #0f172a  (slate-950)
Panel stroke:   #334155  (slate-700)
Box radius:     6px

Text primary:   #e2e8f0  (slate-200)
Text secondary: #94a3b8  (slate-400)
Text muted:     #475569  (slate-600)

Accent palette (use per theme/layer):
  Purple:   #7c3aed / #a855f7
  Orange:   #ea580c / #f97316
  Blue:     #1d4ed8 / #3b82f6
  Green:    #059669 / #10b981
  Gold:     #eab308
  Red:      #dc2626 / #ef4444

Arrow colors: match accent of the source node's theme
```

## Background Gradient

```xml
<defs>
  <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0f0f1a"/>
    <stop offset="100%" stop-color="#1a1a2e"/>
  </linearGradient>
</defs>
<rect width="960" height="600" fill="url(#bg-grad)"/>
```

## Typography

```
font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Courier New',
             'Microsoft YaHei', 'SimHei', monospace
font-size:   13px labels, 11px sub-labels, 15px titles
font-weight: 400 normal, 700 bold for section headers
letter-spacing: 0.02em for labels
```

## Box Styles

```xml
<!-- Default panel -->
<rect rx="6" ry="6" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>

<!-- Active/highlighted panel -->
<rect rx="6" ry="6" fill="#1e293b" stroke="#7c3aed" stroke-width="1.5"/>

<!-- Terminal chrome (top bar with dots) -->
<rect rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
<!-- Title bar -->
<rect rx="6" fill="#2d3748" height="24"/>
<circle cx="x+12" cy="bar_cy" r="4" fill="#ef4444" opacity="0.8"/>
<circle cx="x+24" cy="bar_cy" r="4" fill="#eab308" opacity="0.8"/>
<circle cx="x+36" cy="bar_cy" r="4" fill="#10b981" opacity="0.8"/>
```

## Arrow Styles

```xml
<defs>
  <marker id="arrow-neon" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#a855f7"/>
  </marker>
  <marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6"/>
  </marker>
  <marker id="arrow-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#10b981"/>
  </marker>
</defs>
<!-- Neon arrow -->
<line stroke="#a855f7" stroke-width="1.5" marker-end="url(#arrow-neon)"/>
<!-- Async (dashed) -->
<line stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4,2" marker-end="url(#arrow-blue)"/>
```

## Containers (Swim Lanes)

```xml
<!-- Dark lane container -->
<rect rx="8" fill="#0f172a" stroke="#1e293b" stroke-width="1" stroke-dasharray="8,4"/>
<!-- Lane header -->
<rect rx="4" fill="#1e293b" height="24"/>
<text fill="#94a3b8" font-size="10" font-weight="700" letter-spacing="0.1em">SECTION LABEL</text>
```

## Best For

- GitHub README banners
- Developer blog posts
- CLI tool documentation
- Dark-themed presentations
- API flow diagrams with neon accents

## Example Title Block

```xml
<text x="480" y="36" text-anchor="middle" fill="#e2e8f0" font-size="18" font-weight="700"
      font-family="'SF Mono', monospace" letter-spacing="0.04em">
  DIAGRAM TITLE
</text>
<text x="480" y="56" text-anchor="middle" fill="#64748b" font-size="12"
      font-family="'SF Mono', monospace">
  subtitle · description
</text>
```

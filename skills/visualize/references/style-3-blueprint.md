# Style 3: Blueprint

Engineering blueprint aesthetic with grid background and technical annotation style.

## Colors

```
Background:     #0a1628
Grid color:     #112240  (subtle grid lines)
Panel fill:     #0d1f3c
Panel stroke:   #00b4d8  (cyan/teal)
Box radius:     2px  (sharp corners for technical feel)

Text primary:   #caf0f8  (light cyan)
Text secondary: #90e0ef
Text label:     #00b4d8
Text muted:     #48cae4 at 60% opacity

Accent colors:
  Cyan:    #00b4d8 / #48cae4
  White:   #ffffff (key labels)
  Orange:  #f77f00 (warnings/alerts)
  Green:   #06d6a0 (success/active)
```

## Background with Grid

```xml
<defs>
  <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
    <path d="M 30 0 L 0 0 0 30" fill="none"
          stroke="#112240" stroke-width="0.5"/>
  </pattern>
</defs>
<rect width="960" height="600" fill="#0a1628"/>
<rect width="960" height="600" fill="url(#grid)" opacity="0.6"/>
```

## Typography

```
font-family: 'Courier New', 'Lucida Console', 'Microsoft YaHei', 'SimHei', monospace
font-size:   13px labels, 10px annotations, 16px title
font-weight: 400; titles use 700
text-transform: uppercase for section headers
letter-spacing: 0.05em
```

## Box Styles

```xml
<!-- Technical node box -->
<rect rx="2" ry="2" fill="#0d1f3c" stroke="#00b4d8" stroke-width="1"/>

<!-- Corner-bracket style (no full border) -->
<!-- Top-left bracket -->
<path d="M x+8,y  L x,y  L x,y+8" fill="none" stroke="#00b4d8" stroke-width="1.5"/>
<!-- Top-right bracket -->
<path d="M x+w-8,y  L x+w,y  L x+w,y+8" fill="none" stroke="#00b4d8" stroke-width="1.5"/>
<!-- Bottom-left bracket -->
<path d="M x,y+h-8  L x,y+h  L x+8,y+h" fill="none" stroke="#00b4d8" stroke-width="1.5"/>
<!-- Bottom-right bracket -->
<path d="M x+w-8,y+h  L x+w,y+h  L x+w,y+h-8" fill="none" stroke="#00b4d8" stroke-width="1.5"/>
```

## Numbered Section Headers (Blueprint Style)

```xml
<!-- Section header: "01 // SECTION NAME" -->
<text x="x" y="y" fill="#00b4d8" font-size="11" font-weight="700"
      font-family="'Courier New', monospace" letter-spacing="0.08em">
  01 // EDGE
</text>
```

## Arrow Styles

```xml
<defs>
  <marker id="arrow-cyan" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#00b4d8"/>
  </marker>
  <marker id="arrow-green" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#06d6a0"/>
  </marker>
</defs>
<line stroke="#00b4d8" stroke-width="1" marker-end="url(#arrow-cyan)"/>
<line stroke="#06d6a0" stroke-width="1" stroke-dasharray="5,3" marker-end="url(#arrow-green)"/>
```

## Blueprint Title Block (bottom-right corner)

```xml
<!-- Engineering title block -->
<rect x="720" y="520" width="220" height="60" rx="0" fill="#0d1f3c" stroke="#00b4d8" stroke-width="1"/>
<line x1="720" y1="540" x2="940" y2="540" stroke="#00b4d8" stroke-width="0.5"/>
<line x1="820" y1="520" x2="820" y2="580" stroke="#00b4d8" stroke-width="0.5"/>
<text x="730" y="534" fill="#90e0ef" font-size="9" font-family="'Courier New', monospace">PROJECT</text>
<text x="830" y="534" fill="#90e0ef" font-size="9" font-family="'Courier New', monospace">DATE</text>
<text x="730" y="565" fill="#caf0f8" font-size="12" font-weight="700" font-family="'Courier New', monospace">SYSTEM NAME</text>
<text x="830" y="565" fill="#caf0f8" font-size="11" font-family="'Courier New', monospace">2025-01</text>
```

## Best For

- Architecture documentation for engineering audiences
- Infrastructure diagrams
- Database schema overviews
- Technical specifications
- Deployment topology diagrams

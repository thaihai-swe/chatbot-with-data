# Style 6: Claude Official

Inspired by Anthropic's Claude blog technical diagrams — warm, approachable, professional.

## Colors

```
Background:     #f8f6f3  (warm cream)

Box fills by semantic role:
  Input/Source:    #a8c5e6  (soft blue)
  Agent/Process:   #9dd4c7  (soft teal-green)
  Infrastructure:  #f4e4c1  (warm beige)
  Storage/State:   #e8e6e3  (light gray)

Box stroke:     #4a4a4a  (dark gray)
Box radius:     12px
Box stroke-width: 2.5px (slightly heavier than flat style)

Text primary:   #1a1a1a  (near black)
Text secondary: #6a6a6a  (medium gray)
Text labels:    #5a5a5a  (arrow labels)

Arrow color:    #5a5a5a  (consistent dark gray for all)
```

## Typography

```
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue',
             Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   16px node labels, 14px descriptions, 13px arrow labels
font-weight: 600 for node labels, 400 for descriptions, 700 for titles
```

## Box Shapes

```xml
<!-- Agent node (teal-green) -->
<rect rx="12" ry="12" fill="#9dd4c7" stroke="#4a4a4a" stroke-width="2.5"/>
<text fill="#1a1a1a" font-size="16" font-weight="600" text-anchor="middle"/>

<!-- Input/Source node (soft blue) -->
<rect rx="12" ry="12" fill="#a8c5e6" stroke="#4a4a4a" stroke-width="2.5"/>

<!-- Infrastructure node (warm beige) -->
<rect rx="12" ry="12" fill="#f4e4c1" stroke="#4a4a4a" stroke-width="2.5"/>

<!-- Storage/State node (light gray) -->
<rect rx="12" ry="12" fill="#e8e6e3" stroke="#4a4a4a" stroke-width="2.5"/>
```

## Arrows

```xml
<defs>
  <marker id="arrow-claude" markerWidth="8" markerHeight="8"
          refX="7" refY="4" orient="auto">
    <polygon points="0 0, 8 4, 0 8" fill="#5a5a5a"/>
  </marker>
</defs>

<!-- Primary data flow (solid) -->
<line stroke="#5a5a5a" stroke-width="2" marker-end="url(#arrow-claude)"/>

<!-- Memory write (dashed) -->
<line stroke="#5a5a5a" stroke-width="2" stroke-dasharray="5,3"
      marker-end="url(#arrow-claude)"/>

<!-- Control/trigger (short dash) -->
<line stroke="#5a5a5a" stroke-width="1.5" stroke-dasharray="3,2"
      marker-end="url(#arrow-claude)"/>
```

## Arrow Labels

Arrow labels use small background rects to ensure readability on the warm cream background:

```xml
<!-- Label background (match background color) -->
<rect x="lx-24" y="ly-9" width="48" height="16" rx="3" fill="#f8f6f3" opacity="0.95"/>
<!-- Label text -->
<text x="lx" y="ly+2" text-anchor="middle" fill="#5a5a5a" font-size="11">retrieve</text>
```

## Left Layer Labels (Claude Side-Panel Style)

```xml
<!-- Side label for horizontal layers -->
<text x="28" y="layer_cy" text-anchor="middle" fill="#6a6a6a"
      font-size="11" font-weight="600" letter-spacing="0.06em"
      transform="rotate(-90, 28, layer_cy)">
  LAYER NAME
</text>
<!-- Separator line -->
<line x1="44" y1="layer_top" x2="44" y2="layer_bottom"
      stroke="#d4d0ca" stroke-width="1"/>
```

## Background

```xml
<rect width="960" height="600" fill="#f8f6f3"/>
```

## Best For

- Anthropic/Claude product documentation
- AI/ML research diagrams
- Warm, approachable technical presentations
- Enterprise documentation with a premium feel
- Blog posts for AI-oriented audiences

## Example Title Block

```xml
<text x="480" y="40" text-anchor="middle" fill="#1a1a1a" font-size="22" font-weight="700">
  System Architecture
</text>
<text x="480" y="62" text-anchor="middle" fill="#6a6a6a" font-size="13">
  Component overview and data flow
</text>
```

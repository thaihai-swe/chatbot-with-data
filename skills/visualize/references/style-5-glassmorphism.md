# Style 5: Glassmorphism

Frosted glass cards on dark gradient. Designed for product sites, keynotes, and hero sections.

## Colors

```
Background gradient: #0d1117 → #161b22 → #0d1117 (diagonal)

Glass card:
  fill:           rgba(255,255,255,0.05)
  stroke:         rgba(255,255,255,0.15)
  backdrop-filter: blur(12px)  [SVG: use feGaussianBlur filter]
  box-radius:     12px

Text primary:   #f0f6fc  (near-white)
Text secondary: #8b949e  (muted)
Text gradient:  use linearGradient on text fill for hero labels

Accent glows (one per layer):
  Blue glow:    #58a6ff  / rgba(88,166,255,0.3)
  Purple glow:  #bc8cff  / rgba(188,140,255,0.3)
  Green glow:   #3fb950  / rgba(63,185,80,0.3)
  Orange glow:  #f78166  / rgba(247,129,102,0.3)
```

## Background

```xml
<defs>
  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%"   stop-color="#0d1117"/>
    <stop offset="50%"  stop-color="#161b22"/>
    <stop offset="100%" stop-color="#0d1117"/>
  </linearGradient>
  <!-- Ambient glow spots -->
  <radialGradient id="glow-blue" cx="30%" cy="40%" r="40%">
    <stop offset="0%" stop-color="rgba(88,166,255,0.15)"/>
    <stop offset="100%" stop-color="rgba(88,166,255,0)"/>
  </radialGradient>
  <radialGradient id="glow-purple" cx="70%" cy="60%" r="35%">
    <stop offset="0%" stop-color="rgba(188,140,255,0.12)"/>
    <stop offset="100%" stop-color="rgba(188,140,255,0)"/>
  </radialGradient>
</defs>
<rect width="960" height="600" fill="url(#bg)"/>
<rect width="960" height="600" fill="url(#glow-blue)"/>
<rect width="960" height="600" fill="url(#glow-purple)"/>
```

## Glass Card (Frosted Panel)

```xml
<defs>
  <filter id="blur-bg" x="-10%" y="-10%" width="120%" height="120%">
    <feGaussianBlur stdDeviation="8"/>
  </filter>
</defs>

<!-- Background blur layer -->
<rect x="x" y="y" width="w" height="h" rx="12"
      fill="rgba(255,255,255,0.03)" filter="url(#blur-bg)"/>

<!-- Glass card foreground -->
<rect x="x" y="y" width="w" height="h" rx="12"
      fill="rgba(255,255,255,0.05)"
      stroke="rgba(255,255,255,0.15)"
      stroke-width="1"/>

<!-- Optional top highlight line (shimmer) -->
<line x1="x+20" y1="y+1" x2="x+w-20" y2="y+1"
      stroke="rgba(255,255,255,0.3)" stroke-width="0.5"/>
```

## Typography

```
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
             'PingFang SC', 'Microsoft YaHei', 'SimHei', sans-serif
font-size:   14px labels, 12px sub-labels, 18px titles
font-weight: 400 normal, 600 medium, 700 bold
letter-spacing: -0.01em (tight, modern)
```

## Arrow Styles

```xml
<defs>
  <marker id="arrow-glass" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="rgba(255,255,255,0.6)"/>
  </marker>
  <marker id="arrow-blue-glass" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#58a6ff"/>
  </marker>
  <marker id="arrow-purple-glass" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#bc8cff"/>
  </marker>
</defs>

<!-- Primary flow -->
<line stroke="#58a6ff" stroke-width="1.5" opacity="0.8" marker-end="url(#arrow-blue-glass)"/>
<!-- Secondary / async -->
<line stroke="rgba(255,255,255,0.4)" stroke-width="1"
      stroke-dasharray="4,3" marker-end="url(#arrow-glass)"/>
```

## Glow Effect on Nodes

```xml
<defs>
  <filter id="node-glow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
<!-- Glowing node border -->
<rect rx="12" fill="rgba(88,166,255,0.1)"
      stroke="#58a6ff" stroke-width="1.5"
      filter="url(#node-glow)"/>
```

## Best For

- Product landing pages and hero sections
- Keynote presentations
- Premium documentation sites
- AI/ML product diagrams
- Conference slide decks

## Example Title Block

```xml
<defs>
  <linearGradient id="title-grad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#58a6ff"/>
    <stop offset="100%" stop-color="#bc8cff"/>
  </linearGradient>
</defs>
<text x="480" y="44" text-anchor="middle"
      fill="url(#title-grad)" font-size="22" font-weight="700"
      letter-spacing="-0.02em">
  Diagram Title
</text>
<text x="480" y="66" text-anchor="middle"
      fill="#8b949e" font-size="13">
  Subtitle · description
</text>
```

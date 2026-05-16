# Advanced Mermaid Features

This guide covers theming, styling, and configuration to make your diagrams look professional.

## Theming
You can set a theme using frontmatter configuration at the very top of your Mermaid code block.

```mermaid
---
config:
  theme: forest
---
flowchart TD
    A --> B
```

### Supported Themes
- `default`: The standard theme.
- `forest`: Shades of green.
- `dark`: Dark mode colors.
- `neutral`: Grayscale/professional look.
- `base`: A base theme for custom styling.

## Layout Engines
For complex diagrams, you can switch layout engines.

```mermaid
---
config:
  layout: elk
---
flowchart TD
    A --> B
```

## Styling Classes
Define CSS classes and apply them to multiple nodes.

```mermaid
flowchart LR
    A:::success --> B:::error
    classDef success fill:#9f9,stroke:#333,stroke-width:2px;
    classDef error fill:#f99,stroke:#333,stroke-width:2px;
```

## Interactive Elements (Click events)
*Note: Interactive elements only work in environments that support JavaScript execution for Mermaid.*

```mermaid
flowchart LR
    A-->B
    click A "https://www.github.com" "Open GitHub"
    click B call alert() "Show alert"
```

## Icons and Images
You can use FontAwesome icons if the environment supports them.

```mermaid
flowchart TD
    B["fab:fa-twitter for twitter"]
    B-->C[fa:fa-ban forbidden]
```

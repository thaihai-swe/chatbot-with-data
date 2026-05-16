# Mindmaps

Mindmaps are used for brainstorming, hierarchical information mapping, and organizing thoughts during research or ADR phases.

## Syntax Overview

- **Root:** `mindmap` followed by the root node on a new line.
- **Hierarchy:** Indentation levels define the tree structure.
- **Shapes:**
    - `node`: Default
    - `((node))`: Circle
    - `)node)`: Rounded
    - `[node]`: Square
    - `{{node}}`: Hexagon

## Examples

### Project Brainstorming
```mermaid
mindmap
  root((Project X))
    Frontend
      React
      Tailwind
      Lucide Icons
    Backend
      Node.js
      PostgreSQL
      Redis
    Infrastructure
      Docker
      GitHub Actions
      AWS
```

### Feature Considerations
```mermaid
mindmap
  root((Auth Feature))
    Security
      MFA
      Rate Limiting
      BCrypt hashing
    UX
      Social Login
      Password Reset
      Magic Links
    Compliance
      GDPR
      SOC2
```

## Best Practices
- **Concise Nodes:** Keep node text short; use descriptions in the main document if more detail is needed.
- **Balanced Tree:** Try to balance branches for better readability.
- **Colors & Shapes:** Use different shapes to distinguish between "Categories" and "Leaves".

# Documentation Templates

Compact templates for the standard `docs/` outputs. Fill in the placeholders. Keep prose short and link generously.

## README.md

```markdown
# [Project Name]

[One-sentence description.]

## Overview

[2-3 paragraphs: purpose, key features, target users.]

## Quick Start

### Prerequisites
- [Requirement]

### Installation
\`\`\`bash
# Installation commands
\`\`\`

### Running
\`\`\`bash
# Start commands
\`\`\`

## Architecture

\`\`\`mermaid
graph TD
    A[Component A] --> B[Component B]
\`\`\`

## Key Features

- **Feature 1**: [description]

## Documentation

- [Architecture](./ARCHITECTURE.md)
- [Components](./COMPONENTS.md)
- [Development](./DEVELOPMENT.md)
- [API](./API.md) (if applicable)
- [Deployment](./DEPLOYMENT.md)
```

## ARCHITECTURE.md

```markdown
# Architecture

## System Overview

[High-level description.]

## Design Principles

1. **[Principle]**: [explanation]

## Architecture Diagram

\`\`\`mermaid
graph TB
    subgraph "Frontend"
        UI[User Interface]
    end
    subgraph "Backend"
        API[API Layer]
        DB[(Database)]
    end
    UI --> API
    API --> DB
\`\`\`

## Components

| Component | Responsibility | Key Paths |
|---|---|---|
| [Name] | [What it does] | `src/path/` |

## Data Flow

[Describe how data moves through the system. Use a diagram if it helps.]

## Decisions

- **[Decision]**: [Rationale]. See [ADR](./decisions/).
```

## COMPONENTS.md

```markdown
# Components

## [Component Name]

- **Path**: `src/path/`
- **Responsibility**: [What it does]
- **Public interface**: [Exports / API]
- **Dependencies**: [Internal and external]
- **Extension points**: [How to extend]

[Repeat per major component.]
```

## DATA_MODELS.md

```markdown
# Data Models

## Entity: [Name]

- **Storage**: [Database table / collection]
- **Schema**:
  | Field | Type | Notes |
  |---|---|---|
  | id | uuid | Primary key |

- **Relationships**: [Links to other entities]
- **Validation**: [Rules]
- **Migrations**: [Notable changes]
```

## DEVELOPMENT.md

```markdown
# Development

## Setup

\`\`\`bash
# Setup commands
\`\`\`

## Running Tests

\`\`\`bash
# Test commands
\`\`\`

## Conventions

- Code style: [link to style guide]
- Commit messages: [convention]
- Branch naming: [convention]

## Common Tasks

- **[Task]**: [How to do it]
```

## API.md (if applicable)

```markdown
# API

## Authentication

[Auth scheme]

## Endpoints

### `METHOD /path`

- **Description**: [What it does]
- **Auth**: [Required auth]
- **Request**:
  \`\`\`json
  { "field": "value" }
  \`\`\`
- **Response (200)**:
  \`\`\`json
  { "result": "..." }
  \`\`\`
- **Errors**: [Common error responses]
```

## DEPLOYMENT.md

```markdown
# Deployment

## Environments

| Env | URL | Purpose |
|---|---|---|
| dev | [url] | [purpose] |

## Process

1. [Step 1]
2. [Step 2]

## Rollback

[How to roll back]

## Monitoring

[Monitoring setup and key metrics]
```

## CONTRIBUTING.md

```markdown
# Contributing

## Workflow

1. Fork and branch
2. Make changes with tests
3. Run linter and tests
4. Submit PR

## Code Review

[Review expectations]

## Testing

[Testing requirements]
```

# Project Constraints

> Ownership: `Adopter-owned`

<!-- Non-negotiable rules and budgets that every feature must respect. Commands like /spec-requirements, /spec-plan, and /harness-verify use these as hard boundaries — acceptance criteria and verification gates are checked against them. -->

## Performance Budgets

<!-- Measurable limits that must not be exceeded. -->

| Metric | Budget | Measurement | Enforcement |
|-|-|-|-|
| API response time (p95) | | | |
| Page load time | | | |
| Bundle size | | | |
| Memory usage | | | |
| Database query time | | | |

## Compliance Requirements

<!-- Regulatory or standards compliance that affects implementation. -->

| Standard | Scope | Key Requirements | Verification |
|-|-|-|-|
| | | | |

<!-- Examples: GDPR, SOC2, HIPAA, WCAG 2.1 AA, PCI-DSS -->

## Security Requirements

<!-- Security constraints that apply to all features. -->

- Authentication model:
- Authorization model:
- Data classification:
- Encryption requirements:
- Secret management:
- Audit logging:

## Deployment Model

<!-- How software gets to production. -->

- Environments:
- Release cadence:
- Deployment method:
- Rollback strategy:
- Feature flags:

## Technology Constraints

### Approved

<!-- Technologies and dependencies that are approved for use. -->

| Category | Approved Options |
|-|-|
| Languages | Python 3.13, JavaScript (ESM/Node) |
| Frameworks | FastAPI, React (Vite) |
| Databases | SQLite, Weaviate |
| Infrastructure | Docker Compose (local development) |

### Forbidden

<!-- Technologies explicitly not allowed, with reason. -->

| Technology | Reason |
|-|-|
| Inline secrets | Violates secret scanning policy. Environment variables must be loaded via dotenv. |

### Version Requirements

<!-- Minimum versions or pinning requirements. -->

- Python >= 3.10
- Node.js >= 18
- React ^18.3.1
- Vite ^7.1.12
- Weaviate server ^1.27.0

## Operational Constraints

- Uptime SLA:
- Monitoring:
- Alerting:
- On-call:
- Incident response:

## Accessibility Requirements

<!-- Accessibility standards and testing requirements. -->

- Standard:
- Testing tools:
- Key requirements:

## Budget & Resource Constraints

<!-- Non-technical constraints that affect scope and approach. -->

-

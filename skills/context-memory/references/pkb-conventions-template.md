# PKB: Conventions

## 🖋 Naming Conventions
- **Files**: [kebab-case / PascalCase]
- **Variables/Functions**: [camelCase / snake_case]
- **Classes/Interfaces**: [PascalCase]
- **Constants**: [UPPER_SNAKE_CASE]

## 🤖 AI-Followable Rules
- **Rule**: [Write one explicit instruction agents can follow deterministically]
- **Applies To**: [Backend / Frontend / Tests / Infra]
- **Reference**: [File path, package, or example]

- **Rule**: [Avoid vague advice such as "prefer" when the repository has a clear standard]
- **Applies To**: [Area]
- **Reference**: [Source]

## 🧹 Code Style & Linting
- **Formatter**: [Prettier / internal tool]
- **Linter**: [ESLint / Ruff / RuboCop]
- **Special Rules**: [e.g., "No more than 3 nested callbacks"]

## 🧪 Testing Patterns
- **File Location**: [e.g., `__tests__/` or sibling `.test.ts`]
- **Mocking Strategy**: [Preferred way to mock dependencies]
- **Naming Tests**: [e.g., `describe('feature', () => it('should...'))`]

## 🌳 Git Workflow
- **Branching**: [GitFlow / Trunk-based]
- **Commit Messages**: [Conventional Commits / project specific]
- **PR Requirements**: [e.g., "All tests must pass", "1 approval required"]

## 🏗 Implementation Heuristics
- **[Heuristic 1]**: [Use when...]
- **[Heuristic 2]**: [Use when...]

## 🧱 Architectural Constraints
- **Boundary Rule**: [e.g., "UI components must not call persistence APIs directly"]
- **Why It Exists**: [Repository-specific reason]
- **Reference**: [Module or example]

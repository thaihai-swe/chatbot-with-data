# Documentation Best Practices

This reference provides guidelines for creating high-quality, maintainable documentation.

## Writing Principles

### Clarity Over Cleverness
- Use simple, direct language
- Avoid jargon unless it's domain-specific and necessary
- Define acronyms on first use
- Write for your audience (junior dev vs. architect)

### Show, Don't Just Tell
- Include code examples from the actual codebase
- Use diagrams for complex concepts
- Provide specific file:line references
- Include before/after examples for changes

### Organize for Discovery
- Use clear, descriptive headings
- Include a table of contents for long documents
- Link related sections
- Use consistent structure across documents

### Keep It Current
- Date-stamp documentation
- Remove outdated information
- Update when code changes
- Mark deprecated features clearly

## Structure Guidelines

### README.md
*Purpose*: Entry point for new developers

*Must Include*:
- One-sentence project description
- Quick start instructions that work
- Link to detailed documentation
- How to get help

*Keep It Short*: 200-400 lines max

### ARCHITECTURE.md
*Purpose*: Explain system design and decisions

*Must Include*:
- High-level architecture diagram
- Design principles and patterns
- Component responsibilities
- Data flow diagrams
- Key architectural decisions (with rationale)

*Avoid*: Implementation details (those go in COMPONENTS.md)

### DEVELOPMENT.md
*Purpose*: Get developers productive quickly

*Must Include*:
- Prerequisites (with versions)
- Step-by-step setup instructions
- How to run tests
- How to debug
- Common issues and solutions
- Development workflow

*Test It*: Have someone follow the instructions on a fresh machine

### API.md
*Purpose*: Document all API endpoints

*Must Include*:
- Endpoint list with descriptions
- Request/response formats
- Authentication requirements
- Error codes and meanings
- Rate limiting
- Examples using curl or similar

*Format*: Consistent structure for each endpoint

## Code Examples

### Good Example
```javascript
// From: src/auth/middleware.js:45
// Validates JWT token and attaches user to request
async function authenticateToken(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const user = await jwt.verify(token, process.env.JWT_SECRET);
    req.user = user;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid token' });
  }
}
```

*Why It's Good*:
- Shows actual code from the codebase
- Includes file:line reference
- Has a clear comment explaining purpose
- Shows error handling

### Bad Example
```javascript
// Authenticate user
function auth(req, res, next) {
  // ... authentication logic
}
```

*Why It's Bad*:
- No file reference
- Placeholder instead of real code
- No explanation of how it works
- Missing error handling context

## Diagram Guidelines

### When to Use Diagrams
- *Architecture*: Always use diagrams for system architecture
- *Data Flow*: Use for complex data transformations
- *Sequences*: Use for multi-step processes
- *State*: Use for state machines or workflows
- *Relationships*: Use for entity relationships

### When NOT to Use Diagrams
- Simple linear processes (use a list)
- Single-file components (use code)
- Obvious relationships (use text)

### Diagram Quality Checklist
- [ ] All boxes/nodes are labeled clearly
- [ ] Arrows show direction and are labeled
- [ ] Grouping (subgraphs) adds clarity
- [ ] Diagram matches actual code
- [ ] Renders correctly in target viewer
- [ ] Not too complex (split if needed)

## Common Mistakes

### Mistake 1: Documentation Rot
*Problem*: Docs become outdated as code changes

*Solution*:
- Link docs to code reviews (require doc updates)
- Date-stamp documentation
- Regular doc review cycles
- Automated checks for broken links

### Mistake 2: Too Much Detail
*Problem*: Docs read like code listings

*Solution*:
- Focus on "why" not "what"
- Use diagrams for structure
- Link to code instead of copying it
- Summarize, don't transcribe

### Mistake 3: Missing Context
*Problem*: Assumes reader knows background

*Solution*:
- Explain architectural decisions
- Document gotchas and edge cases
- Include "why we chose X over Y"
- Link to related concepts

### Mistake 4: Inconsistent Terminology
*Problem*: Same concept called different names

*Solution*:
- Create a glossary
- Use project dictionary from `memories/repo/`
- Be consistent across all docs
- Define terms on first use

### Mistake 5: Untested Instructions
*Problem*: Setup instructions don't work

*Solution*:
- Test on a fresh machine
- Include exact commands
- Specify versions
- Document common errors

## Language-Specific Patterns

### JavaScript/Node.js
- Document package.json scripts
- Explain module system (CommonJS vs ESM)
- Document environment variables
- Include npm/yarn commands

### Python
- Document virtual environment setup
- Explain requirements.txt vs setup.py
- Document PYTHONPATH considerations
- Include pip commands

### Java
- Document Maven/Gradle setup
- Explain package structure
- Document build profiles
- Include compilation commands

### Go
- Document module structure
- Explain go.mod and go.sum
- Document build tags
- Include go commands

## Maintenance Strategy

### Regular Reviews
- Quarterly doc review
- Update after major changes
- Remove deprecated content
- Fix broken links

### Ownership
- Assign doc owners per area
- Include docs in code review
- Make docs part of "done"
- Celebrate good documentation

### Metrics
- Time to first contribution (new devs)
- Setup success rate
- Doc feedback/issues
- Search analytics (if available)

## Templates vs. Flexibility

### Use Templates For
- API endpoint documentation
- Component documentation
- ADRs (Architecture Decision Records)
- Runbooks

### Be Flexible For
- Architecture explanations
- Design rationale
- Troubleshooting guides
- Conceptual overviews

## Accessibility

### Make Docs Accessible
- Use semantic HTML/Markdown
- Provide alt text for images
- Use descriptive link text (not "click here")
- Ensure diagrams have text descriptions
- Use sufficient color contrast
- Test with screen readers

## Internationalization

### If Supporting Multiple Languages
- Keep English as source of truth
- Use consistent terminology
- Avoid idioms and colloquialisms
- Consider cultural context
- Use simple sentence structure

## Tools and Automation

### Useful Tools
- *Linters*: markdownlint, write-good
- *Link Checkers*: markdown-link-check
- *Diagram Tools*: Mermaid, PlantUML
- *API Docs*: Swagger/OpenAPI, JSDoc
- *Static Site Generators*: Docusaurus, MkDocs

### Automation Opportunities
- Generate API docs from code
- Extract examples from tests
- Validate code examples compile
- Check for broken links
- Update version numbers

## Success Metrics

### Good Documentation Enables
- New developer productive in < 1 day
- Setup works first try
- Questions answered in docs (not Slack)
- Contributions follow patterns
- Onboarding time decreases

### Warning Signs
- Frequent "how do I..." questions
- Setup issues on every onboarding
- Inconsistent code patterns
- Outdated screenshots/examples
- No one reads the docs

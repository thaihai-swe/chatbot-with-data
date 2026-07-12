# Phase × Guidance Matrix

## 3. Phase × Guidance Matrix

| Source | Spec | Plan | Implement | Verify |
| ------ | ---- | ---- | --------- | ------ |
| `core-policies.md` | Must {## Purpose, ## Normative Rules} | Must {## Amendment Rules, ## Release Guardrails} | Must {## Normative Rules, ## Security Policy} | Must {## Memory Promotion Thresholds, ## Security Policy} |
| `harness-config.md` | Skip | Should {## Artifact Routing, ## Verification Commands} | Should {## Verification Commands, ## Session Defaults} | Skip |
| `core-zero/project/architecture.md` | Should | Should | Skip | Should |
| `core-zero/rules/code-design.md` | Skip | Should | Must {## Read before you write, ## Failures must reach a decision-maker, ## Verify the path you claim to have fixed} | Should {## Failures must reach a decision-maker, ## Verify the path you claim to have fixed} |
| `core-zero/rules/security.md` | Skip | Skip | Must {## Core Rules, ## Shell and Script Safety, ## File and Artifact Boundaries, ## Verification} | Should {## Verification} |
| `core-zero/rules/architecture-principles.md` | Skip | Should | Skip | Should |
| `core-zero/rules/ponytail.md` | Skip | Should {## Decision Matrix: Should You Create an Abstraction?} | Should {## Decision Matrix: Should You Create an Abstraction?} | Should {## Decision Matrix: Should You Create an Abstraction?} |

## Session Lifecycle Steps

- **Bootstrap**: Initial kit setup
- **Session START**: `scripts/corezero session-start --feature <slug>`
- **Memory SYNC**: `/context-memory` post-ship

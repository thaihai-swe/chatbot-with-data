# Intake (Opening Wave)

The intake gate is the first step in `spec-requirements`. It runs **before** any grilling, codebase reading, or spec authoring. Its job is to classify the work in two dimensions — *what kind of work this is* and *what risk it carries* — and produce a one-line classification recorded in `status.md`.

The principle: **classification first.** A misclassified piece of work may skip critical checks it required. The intake step makes that classification explicit and durable.

## Output

Append (or update) the `## 🧪 Intake` section in `artifacts/features/<slug>/status.md`:

```markdown
## 🧪 Intake

- **Input type:** <new_spec | spec_slice | change_request | new_initiative | maintenance | harness_improvement>
- **Risk flags:** <comma-separated list, or `none`>
- **One-line restatement:** <what this work actually is, in your own words>
- **Affected docs/specs:** <paths or `n/a`>
- **Reasoning:** <one sentence — why this classification>
```

## Input Types

Pick the one that fits best. If two seem to fit, pick the one with the heavier downstream artifacts.

| Type | Use when | Typical artifact |
|---|---|---|
| `new_spec` | Turning a user-provided project spec into harness-ready docs from scratch. | Product docs, candidate features, decisions. |
| `spec_slice` | Implementing a selected behavior from an already-accepted spec. | Feature spec under `artifacts/features/<slug>/`. |
| `change_request` | Changing, fixing, or refining an already-accepted behavior. | Feature spec or direct patch. |
| `new_initiative` | Adding a larger product area that needs multiple feature specs. | Initiative notes plus per-feature specs. |
| `maintenance` | Changing technical, operational, or dependency behavior (no product surface change). | Feature spec, validation report, or decision. |
| `harness_improvement` | Improving how humans and agents collaborate (skills, templates, memory, scripts). | Direct kit edit or harness backlog item. |

## Risk Flag Checklist

Mark every flag that applies. Multiple flags are common.

| Flag | Applies when the work touches |
|---|---|
| `auth` | login, logout, sessions, JWT, password, refresh token |
| `authorization` | roles, permissions, tenant or company scope |
| `data_model` | schema, migrations, uniqueness, deletion, retention |
| `provider` | external APIs, payment processors, identity providers |
| `migration` | data backfill, persistent state changes, schema rollouts |
| `cross_boundary` | more than one major architectural boundary |
| `public_api` | endpoints, SDK signatures, or contracts other features depend on |
| `security` | secrets, key handling, audit logs, anything in `core-policies.md` `## Security Policy` |
| `harness-maintain` | this kit's skills, templates, memory schemas, or scripts |
| `none` | none of the above — record explicitly to show you checked |

## Stop Conditions

Stop and ask the user before proceeding when:

- The user prompt does not clearly fit any input type.
- Risk flags are set but the user has not confirmed this work should touch them.
- The request requires cross-boundary changes that the user has not approved.

## Anti-Patterns

- **Proceeding without checking risk flags.** If `auth`, `data_model`, `security`, or `harness-maintain` is touched, the agent must pay extra care during planning and verification.
- **Recording `none` for risk flags without inspecting.** Read at least the affected files first.
- **Skipping intake on `change_request` because "we already have a spec."** A change request still needs a fresh intake classification to check for new risk flags.

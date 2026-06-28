# Code-Design Principles

> Ownership: `Kit-managed`

Principles agents **MUST** apply when writing or changing behavior in this
repository. These rules carry the same weight as the `MUST` / `MUST NOT`
rules in `AGENTS.md` Section 0 and are referenced from there.

Overengineering rarely looks like overengineering at the line level. It
shows up as small, locally-reasonable choices that combine into a system
where features fail silently and bug fixes have to be applied N times. The
principles below are the lessons; if a piece of code violates one, that is
enough reason to fix it even when the local code "works."

## Read before you write

- **MUST** check existing files of a similar type before creating a new file or module. Match their structure, not a generic template.
- **SHOULD** prefer the smallest file that satisfies the task over a boilerplate scaffold. Over-generation of boilerplate sections that the codebase never uses (e.g., full docstrings, empty method stubs, placeholder configs) is an anti-pattern.

## Practical SOLID and Object-Oriented Design

- **Single Responsibility (SRP):** **MUST NOT** mix data fetching, business logic, and presentation in the same class or module. A component should have one primary reason to change.
- **Liskov Substitution (LSP):** **MUST NOT** implement interfaces or extend classes only to throw `NotImplementedException` for methods you don't want to support. If an object cannot fulfill the contract, it should not inherit from it.
- **Interface Segregation (ISP):** **SHOULD** favor small, role-specific interfaces over massive "god interfaces." Callers should only depend on methods they actually invoke.
- **Dependency Inversion (DIP):** **SHOULD** depend on abstractions rather than concrete implementations *when crossing an architectural boundary* (like database access or external APIs), but respect the "No premature seams" rule for internal logic.
- **Encapsulation:** **MUST NOT** expose mutable internal state as public fields. State mutations must pass through methods that validate invariants.
- **Composition over Inheritance:** **MUST NOT** build deep inheritance trees (more than 2 levels). Build complex behavior by composing smaller objects rather than relying on deep subclassing.

## One way to say one thing

- **MUST NOT** accept two spellings of the same intent — e.g. a magic
  sentinel value AND absence-of-field both meaning "use the default." Pick
  one and reject the other.
- **MUST NOT** maintain two entry points that load, construct, or resolve
  the same thing where one does strictly more work than the other. Callers
  will pick the wrong one. Unify them, or encode the difference as a
  required argument on a single entry point.
- **MUST NOT** let each consumer write its own private wrapper around a
  shared helper to make it usable. If three callers each prepend the same
  three lines, those three lines belong in the helper.

## Behavior follows from inputs, not from which path the caller took

- **MUST** ensure a function's result depends on its arguments, not on
  which sibling function the caller happened to invoke first. If "did
  setup step S run?" determines correctness, S belongs INSIDE the function
  that needs it, or its absence **MUST** be a hard error — not a silent
  degradation.
- **SHOULD** centralize runtime resolution. When a value on disk requires
  runtime resolution (start a process, read state, hit a service), the
  resolution belongs in ONE place that every consumer goes through. If
  some consumers get the resolved form and some get the raw form, the
  abstraction is broken.

## Failures must reach a decision-maker

- **MUST NOT** catch an error, log it through a logger that may be a
  no-op, and continue with a null/empty result. The error reaches no one.
  Either surface the failure to the caller (return type, status field,
  stderr line), or throw.
- **MUST** let a caller that receives "no result" distinguish "the input
  legitimately produced nothing" from "a dependency was unavailable" from
  "the operation was skipped." If those three look the same to the user,
  the system is hiding bugs — including this one.
- **MUST** ensure that when a function returns `T | null` (or a "skipped"
  status), at least one caller in the codebase branches on the negative
  case and surfaces it. If every caller treats absence as success, the
  function is laundering errors.

## Don't build seams without a second piece on the other side

- **MUST NOT** introduce an interface, abstract type, or "port" boundary
  with exactly one implementation and no concrete plan for a second.
  Abstractions are paid for with indirection; pay only when you collect.
- **MUST NOT** add an optional dependency-injection slot
  (`deps.X ?? defaultX`) unless at least one test exercises the production
  default. If every test injects a fake, the production codepath is
  type-checked and untested.
- **MUST NOT** add a wrapper "in case" callers later need to extend it.
  Add the wrapper when the second caller arrives.

## Specification and behavior are one artifact

- **MUST** keep schemas, doc comments, and config descriptions in lockstep
  with code. When a schema, doc comment, or config description states a
  default or a meaning, the code **MUST** enforce it. Drift between
  "what the field claims" and "what the code does" is a contract bug
  even if both compile.
- **MUST** update the schema description, the doc, AND the example in the
  same change as the behavior. Not later.

## Verify the path you claim to have fixed

- **MUST** run a command that actually exercises the change end-to-end
  before claiming a feature works, and observe the side effect — the
  file written, the process contacted, the row stored. Type-check passing
  is necessary, not sufficient. A test passing against a fake is not
  evidence the real path works.
- **MUST** grep for the same shape elsewhere before declaring a bug
  fixed. Bugs of the kind described in this section repeat. Fix the
  class, not just the instance.

## Naming asymmetries are bugs in waiting

- **SHOULD** assume callers will pick the wrong one when two related
  identifiers have non-parallel names (`loadX` vs `loadHigherX`,
  `createY` vs `createDefaultY`, `xClient` vs `xService`). Unify, or
  document inline why both must exist.

## Dispatch and contract leaks across per-variant layers

Layers with multiple per-variant implementations (warehouse drivers,
SQL dialects, LLM providers, ingest adapters, payment processors,
storage backends) drift toward parallel switches and informal contracts.
The patterns below look locally reasonable per file but multiply with
the number of variants times the number of consumers — every fix has
to be applied N times, and silent drift between variants is invisible
until a user hits it.

- **MUST NOT** maintain two or more files that switch on the same enum
  or string union to dispatch to per-variant behavior. Promote the
  dispatch to a single registry table keyed by the union, exposed
  through one resolution function. If you find yourself writing the
  third such switch, the second one was already a bug.
- **MUST** put a method on the shared interface when every variant of
  an abstraction implements it. An informal contract that every
  implementation happens to satisfy is a leak waiting to happen —
  callers will reach for the concrete class instead of the contract,
  and the next variant added will silently forget to implement it.
- **MUST** keep the shared interface and per-variant concrete classes
  in agreement when a layer has both. Either widen the interface so
  callers never need the concrete class, or make the concrete class
  internal (visibility modifier, package-private, `@internal` JSDoc,
  or a build-time boundary check). A class that is public AND has
  methods the interface does not expose is the exact configuration
  that produces leaks.

The canonical shape: a single registry table keyed by the variant
identifier, one resolution function every caller goes through, an
interface wide enough that callers never reach for the concrete class,
and an enforced import boundary that keeps the per-variant
implementations from leaking. Apply this shape to any per-variant
layer that grows beyond two implementations.

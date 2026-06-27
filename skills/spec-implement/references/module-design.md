# Module Design

A short reference for refactor and architecture-shaping tasks. Loaded only when `spec-implement` is doing structural work — not on routine bug fixes or feature tasks.

## Deep Modules

A **deep module** has a small interface and lots of behavior behind it. The interface is what callers depend on; the implementation is everything they don't have to know about. The asymmetry is the point: depth = (behavior hidden) ÷ (interface exposed).

A **shallow module** is the opposite — its interface is almost as wide as its implementation. Callers have to know nearly as much to use it as they would to inline the code.

Reach for depth when:

- A subsystem is being touched by many callers, each rebuilding the same incidental detail.
- A small handful of operations capture what callers actually need (e.g., `enqueue` / `drain` / `close` over a queue, not 14 fine-grained accessors).
- The implementation has real complexity worth hiding (state machines, retries, format conversions, race resolution).

Avoid depth when:

- The "module" only forwards calls to one underlying thing. That's a wrapper, not depth.
- The interface is a renaming exercise. If callers still need to understand the underlying API to use yours, you have moved complexity sideways, not hidden it.
- The code is small enough that hiding it costs more in indirection than it saves in cognition.

Reference: John Ousterhout, *A Philosophy of Software Design*. The kit doesn't require Ousterhout's full taxonomy — just the asymmetry test.

## The Deletion Test

Before adding (or keeping) an abstraction layer, ask: **if I deleted this module, would the complexity disappear, or just move?**

- **Disappears (or shrinks):** The abstraction was earning its keep. Callers were genuinely simpler because of it.
- **Moves to callers, ~unchanged in total:** The module was a renaming exercise. Each caller now does the same work the module did. You traded one place to read for many.
- **Concentrates in one caller:** Probably fine — that caller is the only real consumer, and the abstraction was speculative.

Apply the deletion test when:

- Reviewing a refactor proposal that adds a new layer.
- Auditing existing layers during a `Brownfield Map` (`spec-research`).
- Deciding whether to keep a thin adapter, a re-export, or a "convenience" wrapper.

The test is a heuristic, not a proof. If you cannot tell whether deletion would shrink or just move complexity, that uncertainty is itself a signal — usually that the layer is shallow.

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Symptom |
|---|---|---|
| Wrapper that just renames an underlying API | Callers still need to know the underlying behavior, plus your renaming. | "Why does this layer exist?" "Because we wanted our own names." |
| Pass-through with no policy | The wrapper holds no behavior — every method delegates 1:1. | Every method body is `return inner.foo(...args)`. |
| Forced polymorphism for one implementation | Interface + one impl = the interface has no callers benefiting from the abstraction. | The interface and the impl are edited together every time. |
| "Future-proof" abstraction with one current consumer | Speculative layers ossify around assumptions that turn out wrong. | The abstraction's shape was decided before the second use case existed. |

## Rule of Thumb for Refactor Tasks

When `tasks.md` contains a refactor task that adds a layer or extracts a module:

1. State the problem the layer solves in one sentence (what concrete complexity it hides).
2. Run the deletion test mentally. If deletion would just move the complexity, stop and reconsider.
3. Prefer collapsing shallow modules over preserving them. Deletion is a valid refactor outcome.

Refactors that pass these checks belong in the plan. Refactors that don't are usually drive-by churn.

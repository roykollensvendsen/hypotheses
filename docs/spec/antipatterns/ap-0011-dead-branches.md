<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0011 — Dead branches and placeholder TODOs

## Narrative

Code paths that the type system or earlier validation rule out, but
which still appear as `else: raise NotImplementedError` or as
TODO-marked stubs that ship to `main`. The
[per-module definition of done](../12-implementation-constraints.md#per-module-definition-of-done)
is explicit: "no TODO/FIXME/TBD in source." Dead branches and
unfinished placeholders are the LLM-generated variant — they look
defensive but mark unfinished thought, and they leave a trap for
the next reader who has to model paths that cannot fire.

## Bad code

```bad-code
def serve(transport: Literal["stdio", "http"]) -> None:
    if transport == "stdio":
        run_stdio_server()
    elif transport == "http":
        run_http_server()
    else:
        # TODO: handle other transports
        raise NotImplementedError(f"unknown transport: {transport}")

def settle(state: SubmissionState) -> Settlement:
    match state:
        case SubmissionState.PENDING:
            return _tentative()
        case SubmissionState.SETTLED_HONEST_NULL:
            return _final(state)
        case _:
            raise NotImplementedError  # never reached but here for safety
```

## Why

- The `else` branch in `serve` cannot fire — the parameter is a
  closed `Literal`. Pyright proves this; the `raise` is dead code
  with a misleading TODO. A reader has to verify the proof
  themselves, find no real path, then delete the line — friction
  for nothing.
- The `case _:` in `settle` is the same pattern with a match
  statement. If `SubmissionState` adds a member, this branch
  *masks* the omission instead of failing exhaustiveness checking.
- Both shapes carry the failure mode of inviting silent partial
  implementations: an agent told to "add http transport" can drop
  one line into the branch and the test suite passes, but the
  TODO marker stays — the dead branch becomes lived-in scaffolding.

## Correct pattern

```good-code
def serve(transport: Literal["stdio", "http"]) -> None:
    if transport == "stdio":
        run_stdio_server()
    else:
        run_http_server()

def settle(state: SubmissionState) -> Settlement:
    match state:
        case SubmissionState.PENDING:
            return _tentative()
        case SubmissionState.SETTLED_HONEST_NULL:
            return _final(state)
        case SubmissionState.SETTLED_FALSIFIED:
            return _final(state)
```

Two `if`/`else` branches for two values; one `case` per
`SubmissionState` member. Pyright now enforces exhaustiveness; an
unhandled state is a type error, not a runtime surprise. Where a
branch genuinely cannot exist, type the input narrowly enough that
the branch is unreachable *to pyright* — then it does not need to
exist in code.

## Spec reference

- [12 § per-module definition of done](../12-implementation-constraints.md#per-module-definition-of-done)
  — "no TODO/FIXME/TBD in source."
- [12 § code style](../12-implementation-constraints.md#code-style)
  — type hints on every function; closed enums over strings.
- [24 § D-2](../24-design-heuristics.md) — make illegal states
  unrepresentable.

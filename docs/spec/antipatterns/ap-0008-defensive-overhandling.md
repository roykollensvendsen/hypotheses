<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0008 — Defensive over-handling

## Narrative

Wrapping calls in `try`/`except` for failures that cannot reach the
caller, or layering `assert isinstance(...)` checks downstream of a
typed boundary, adds lines without catching anything new. The cost
is real: error attribution is lost, the typed exception taxonomy in
[`12 § fail-fast`](../12-implementation-constraints.md#fail-fast-policy)
is bypassed, and the reader has to model failure paths that never
fire. This is the second-order failure mode of `ap-0003` (bare
`except`): not catching everything, but defending against nothing.

## Bad code

```bad-code
def score_submission(submission: Submission) -> ScoreVector:
    if submission is None:                       # type rules this out
        raise ValueError("submission was None")
    try:
        rigor = compute_rigor(submission.spec)
    except Exception as e:                       # swallows every typed error
        log.warning("rigor failed", exc=e)
        rigor = 0.0
    if not isinstance(rigor, float):             # types rule this out
        rigor = float(rigor)
    return ScoreVector(rigor=rigor, ...)
```

## Why

- The `submission is None` guard is dead code: the type signature
  already rules it out and `pyright --strict` would catch a real
  caller passing `None`. Reading it forces the reviewer to ask
  "where could that come from?" — and the answer is "nowhere".
- `except Exception:` collapses the entire typed-exception
  taxonomy into a silent zero. A `SpecInvalid` and a
  `StorageUnavailable` produce the same observable behaviour;
  operators see no signal, mutation testing finds no kill, the
  fail-fast contract is violated.
- The `isinstance` cast hides a type-shape disagreement that
  should fail at the boundary, not be silently coerced.

## Correct pattern

```good-code
def score_submission(submission: Submission) -> ScoreVector:
    rigor = compute_rigor(submission.spec)
    return ScoreVector(rigor=rigor, ...)
```

Trust the boundary. `submission` is typed; `compute_rigor` returns
the right shape or raises a typed exception that propagates. If a
real failure mode emerges, give it a name in `errors.py` and let
the top-level handler log it once with structured context.

## Spec reference

- [12 § fail-fast](../12-implementation-constraints.md#fail-fast-policy)
- [12 § code style](../12-implementation-constraints.md#code-style)
- [24 § D-3](../24-design-heuristics.md) — validate at boundaries;
  trust internal callers.
- [`ap-0003`](ap-0003-bare-except.md) — bare `except`.

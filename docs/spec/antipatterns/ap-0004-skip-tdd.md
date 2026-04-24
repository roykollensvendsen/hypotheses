<!-- antipattern-content -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0004 — Skipping TDD

## Narrative

The TDD discipline in
[12 § test-driven development](../12-implementation-constraints.md#test-driven-development-mandatory)
requires that tests be written *first*, fail *first*, and only then
turn green under the implementation commit. The `tdd-gate.yml`
workflow enforces commit order, but the gate's intent is **failing
tests first**, not merely "a `test:` commit appears before a `feat:`
commit." Writing the implementation first and then a test that
passes trivially (or no-ops) defeats the gate while technically
satisfying it.

## Bad code

```bad-code
# 1) First commit (feat:) — already-working implementation
def composite(vec: ScoreComponents, w: Weights) -> float:
    return (
        w.rigor * vec.rigor
        + w.reproduction * vec.reproduction
        + w.improvement * vec.improvement
        + w.novelty * vec.novelty
        - w.cost_penalty * vec.cost_penalty
    )

# 2) Later commit (test:) — rubber-stamp test, always passes
def test_composite_runs_without_crashing():
    composite(ScoreComponents.zero(), Weights.default())
```

Worse: re-ordering commits with `git rebase -i` so the `test:`
appears first *after* the `feat:` is already green. The gate passes;
the test is meaningless.

## Why

- The gate is "tests first" as a *development discipline*, not a
  git-log aesthetic. Skipping it produces tests that cover code
  rather than behaviours.
- Mutation scoring (`mutation.yml`, 75% floor per module) catches
  some of these as surviving mutants, but weakly.
- Review signal is lost: reviewers use the red-first commit to see
  what the test *requires* before seeing the code that satisfies it.

## Correct pattern

```good-code
# 1) First commit (test:) — MUST be red on its own
def test_composite_matches_worked_example():
    fx = load_golden("scoring/worked-example.json")
    out = composite(
        ScoreComponents(**fx["input"]["components"]),
        Weights(**fx["input"]["weights"]),
    )
    assert abs(out - fx["expected"]["composite"]) < fx["expected"]["tolerance"]

# 2) Second commit (feat:) — the minimum code to pass
def composite(vec: ScoreComponents, w: Weights) -> float:
    return (
        w.rigor * vec.rigor
        + w.reproduction * vec.reproduction
        + w.improvement * vec.improvement
        + w.novelty * vec.novelty
        - w.cost_penalty * vec.cost_penalty
    )
```

Every module's first `test:` commit predates its first
`feat:`/`fix:` commit *and* that test exercises a behaviour the
implementation must satisfy.

## Spec reference

- [12 § test-driven development](../12-implementation-constraints.md#test-driven-development-mandatory)
- [12 § testing strategy](../12-implementation-constraints.md#testing-strategy)
- `.github/workflows/tdd-gate.yml`
- `.github/workflows/mutation.yml`

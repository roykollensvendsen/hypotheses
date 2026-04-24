<!-- antipattern-content -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0001 — Oracle fallback

## Narrative

When a hypothesis declares an oracle (`oracle.subnet` is non-null),
the scoring pipeline MUST gate on oracle agreement. Skipping the
oracle check on outage — even "temporarily, just for this cycle" —
gives dishonest miners a window to land unverifiable answers while
the oracle subnet is down. The spec is explicit: the oracle is a
hard gate, not a soft check.

## Bad code

```bad-code
def score(submission, spec):
    score = deterministic_core(submission, spec)
    if spec.oracle.subnet is not None:
        try:
            verdict = oracle.query(spec.oracle)
            if not verdict.agrees_with(submission.declared_answer, spec.oracle.tolerance):
                return ScoreVector.zero()
        except OracleUnavailable:
            # Oracle is down; skip the check this cycle.
            pass
    return score
```

## Why

Skipping on outage turns `oracle: required` into `oracle: best-effort`.
The spec in [18 § outage handling](../18-oracle.md#outage-handling)
mandates **pending**, not **skip** — the submission waits for a live
oracle rather than scoring without one.

## Correct pattern

```good-code
def score(submission, spec):
    if spec.oracle.subnet is not None:
        verdict = oracle.query(spec.oracle)  # raises on outage
        if not verdict.agrees_with(submission.declared_answer, spec.oracle.tolerance):
            return ScoreVector.zero()
    return deterministic_core(submission, spec)
```

The pipeline catches `OracleUnavailable` one level up and leaves the
submission `pending`; the next cycle retries.

## Spec reference

- [06 § Oracles](../06-scoring.md#oracles)
- [18 § outage handling](../18-oracle.md#outage-handling)
- [12 § fail-fast](../12-implementation-constraints.md#fail-fast-policy)
  — `OracleUnavailable` is a typed exception, not a silent fallback.

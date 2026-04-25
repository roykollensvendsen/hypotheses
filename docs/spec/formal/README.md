---
name: formal specs
description: quint formalisations of hypothesis-subnet state machines and protocols
tokens: 300
load_for: [implementation, review]
depends_on: [17]
kind: reference
---

# Formal specifications

Mechanically-checkable specifications in [Quint](https://quint-lang.org)
that mirror the prose in the numbered spec docs. The prose is the
source of truth; these files are a machine-verifiable companion. When
they diverge, **it is a bug** — either the prose rule is wrong or the
formalisation is out of date, and the fix lands in the same PR that
flags the divergence.

## Files

| spec | mirrors |
|------|---------|
| [`lifecycle.qnt`](lifecycle.qnt) | [17 — Hypothesis lifecycle](../17-hypothesis-lifecycle.md) |

## Scope

Formalisation is worthwhile for:

- State machines with non-trivial invariants (lifecycle, settlement).
- Concurrency / ordering rules (novelty tiebreak, duplicate
  settlement collapse).

Not worthwhile for:

- Pure functions with clear reference implementations (scoring
  formulas — we verify those with golden fixtures and property
  tests).
- Prose policies without temporal/relational structure (testing
  strategy, commit conventions).

## Running

Quint is optional tooling. A sketch of the CLI flow once the
container image is stable:

```bash
docker run --rm -v $PWD:/w informalsystems/quint:latest \
  typecheck /w/docs/spec/formal/lifecycle.qnt
docker run --rm -v $PWD:/w informalsystems/quint:latest \
  verify /w/docs/spec/formal/lifecycle.qnt --invariant Inv_TerminalsStick
```

A wrapping workflow (`.github/workflows/quint-check.yml`) will land
once the tooling has proven reliable in CI; today the files ship as
documentation.

## Change process

1. Update the prose doc first (e.g. 17-hypothesis-lifecycle.md).
2. Update the matching `.qnt` file in the same PR.
3. If the prose requires an ADR (authority, invariant, or policy
   change), the ADR references both artefacts.

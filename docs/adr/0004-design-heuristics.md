---
name: 0004 design heuristics
description: choice to codify positive structural design rules for human and agent contributors as a separate spec doc
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0004 — Design heuristics

## Context

`docs/spec/12-implementation-constraints.md` locks the *mechanics*
of implementation (toolchain pins, TDD order, fail-fast taxonomy,
SPDX, mutation, coverage) and `docs/spec/antipatterns/` ships a
small corpus of named negative shapes. Neither codifies the
*qualitative* side: when to extract a function, how deep a module
should be, when not to abstract, how to size a PR for review.

Phase 1 implementation is about to begin and will be done
predominantly by autonomous agents. As Stack Overflow's 2026
"Building shared coding guidelines for AI (and people too)" piece
puts it, AI amplifies what already exists in an engineering
system — strong foundations multiply, weak ones collapse faster.
Tacit human conventions don't transfer to agents; only documented
ones do. Without explicit structural rules, agent-written code
defaults to the average of its training data, which is mediocre
("AI slop").

## Decision

Codify a small, opinionated set of **positive design heuristics**
in a new spec doc, `docs/spec/24-design-heuristics.md`, with six
named rules (D-1 … D-6), each backed by a one-paragraph rationale
and a Bad/Good code-pair, plus a tight section on PR shape.
Complement with an LLM-failure-mode antipatterns batch (ap-0008 …
ap-0013) added to the existing corpus in a follow-up PR.

The rule set is deliberately small — six, not fifty. Larger
manifestos age into dogma; tight rules with concrete examples bind
in review.

## Consequences

- **Positive.** PR reviewers (human or agent) have a stable
  citation home for design feedback. Agents writing code can load
  doc 24 alongside doc 12 to get both the mechanics and the
  qualitative guidance. Drift becomes detectable because reviewers
  can point at "D-3" instead of arguing in the abstract.
- **Negative.** Heuristics are normative-by-review, not
  CI-enforced. Mechanical detection of some patterns (bare
  `except`, `raise NotImplementedError` outside `pytest.mark.skip`)
  is possible later but deferred — premature gate engineering
  would lock in dogma before the rules have settled in real PRs.
- **Neutral / deferred.** A future PR may extend `ruff.toml` or
  add a script under `scripts/` to flag specific antipatterns
  mechanically; that requires its own ADR.

## Options considered

- **Extend `12-implementation-constraints.md` directly.** Rejected:
  doc 12 is already 590 lines and tightly mechanical; mixing
  qualitative rules dilutes its purpose and makes it harder to
  load selectively.
- **Add the rules to `AGENTS.md § Non-negotiable rules`.**
  Rejected: AGENTS.md is the entry-point router; expanding it
  pushes content past the routing-table token budget. A
  cross-reference is the right shape there, not the content.
- **Write fifty rules covering every conceivable case.** Rejected:
  rules without concrete examples become platitudes; large rule
  sets become mutually contradictory and age into dogma. Six
  rules with good/bad pairs is the cap.

## Related

- Research informing the rules:
  - John Ousterhout, *A Philosophy of Software Design* (deep
    modules, complexity = "anything that makes the system hard to
    understand and modify").
  - The MAST taxonomy of agentic-system failures (specification
    ambiguity, coordination breakdowns, verification gaps).
  - Stack Overflow Blog (2026-03-26), "Building shared coding
    guidelines for AI (and people too)".
  - Anthropic Claude Code best-practices guidance (2026).
- Spec: [`12-implementation-constraints.md`](../spec/12-implementation-constraints.md),
  [`03-architecture.md`](../spec/03-architecture.md),
  [`23-system-tests.md`](../spec/23-system-tests.md),
  [`antipatterns/`](../spec/antipatterns/).
- ADRs: [0002](0002-test-toolchain.md) for the testing-toolchain
  decision the heuristics build on; [0003](0003-system-test-markers.md)
  for system-test markers.

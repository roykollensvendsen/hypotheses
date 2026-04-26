---
name: 0011 d22 coverage bound
description: name the validator-set floor below which the D2.2 reproduction-by-sampling defence silently degrades
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0011 — D2.2 reproduction-coverage bound

## Context

[`05-validator.md`](../spec/05-validator.md) declares that
validators rerun a deterministic `rerun_fraction = 0.4` sample
of seeds per submission, with the sample seeded by
`(validator_hotkey, epoch, spec_id, version)` so different
validators sample different seeds and "cover more ground
collectively." [`00.5 § B`](../spec/00.5-foundations.md#b-defences-derived-from-each-threat)
names this defence D2.2 against F2 (miner cheating).

The mechanism's claim is statistical, not deterministic: a
miner cheating on `k` of `S` seeds escapes only if every
validator misses every cheated seed. Until this PR the spec
named the *primitive* (uniform-independent sampling) but not
the *bound* — how many validators are required for the claim
to hold at a useful confidence level. The post-strategy-doc
gap-review (see follow-up ADRs after 0010) flagged this as the
most concrete missing piece.

## Decision

Add a new invariant `HM-INV-0030` to
[`05 § Coverage under thin validator sets`](../spec/05-validator.md#coverage-under-thin-validator-sets)
declaring the closed-form coverage formula and pinning the
default validator floor at `min_validators_d22_coverage = 6`,
the smallest `N` for which `1 − (1 − 0.4)^N ≥ 0.95`.

The bound is added to:

- [`05-validator.md`](../spec/05-validator.md) — the formula,
  table, and HM-INV-0030 block-quote.
- [`20-economic-model.md § Parameter inventory`](../spec/20-economic-model.md#parameter-inventory)
  — new parameter row.
- [`20-economic-model.md § Validator registration`](../spec/20-economic-model.md#validator-registration)
  — design note rewritten to reference the floor.
- [`00.5-foundations.md § E "Open bets"`](../spec/00.5-foundations.md#e-empirical-posture--whats-proven-vs-whats-a-bet)
  — validator-concentration bullet acknowledges the partial
  progress.
- [`invariants.md`](../spec/invariants.md) — index row.

## Consequences

- **Positive.** The previously-implicit "thin validator sets
  are vulnerable" claim is now mechanical: a specific `N` and
  a specific cheat-success probability at smaller `N`. Phase
  2 onset has a measurable target (≥6 validators) and a
  testable invariant. A property-based test under
  `tests/properties/test_validator.py::test_coverage_bound`
  will verify the formula end-to-end at Phase 1.
- **Negative.** Pinning a floor exposes the gap between the
  Phase 2 testnet target (3–5 validators per
  [`20 § Validator registration`](../spec/20-economic-model.md#validator-registration))
  and the floor (≥6). The maintainer's response is documented
  here rather than in the spec body: at Phase 2 entry with
  `N < 6`, raise `rerun_fraction` proportionally so coverage
  is preserved (e.g., at `N = 4`, `f = 0.55` keeps coverage
  ≥95%); revisit at the first 6-month foundation review under
  [`00.5 § Review cadence`](../spec/00.5-foundations.md#review-cadence)
  when real validator-count data lands.
- **Neutral / deferred.** Adversarial validator-coverage (a
  coordinated bloc deliberately co-sampling the same seeds to
  leave gaps) is an F1-class threat handled by the white-hat
  programme in
  [`22-security-bounty.md`](../spec/22-security-bounty.md);
  this ADR does not address it. Per-profile / per-`S` floors
  (the edge case `S ≤ 2` requires `N ≥ 5`) are noted in the
  spec but not separately parameterised — `S ≤ 2` submissions
  are already discouraged at the schema level.

## Options considered

- **Leave the floor implicit.** Rejected: silent degradation
  is exactly the failure mode the post-strategy-doc gap review
  named. A rigorous spec gives a number.
- **Pin the floor at 95% per-seed coverage (chosen).** This
  matches the standard "reasonable confidence" threshold and
  yields `N ≥ 6` — close enough to the Phase 2 testnet target
  to be achievable without re-architecting validator
  recruitment.
- **Pin at 99% (`N ≥ 9`).** Rejected: pushes the floor above
  the realistic Phase 2 target; would force `rerun_fraction`
  bumps that aren't yet justified by data.
- **Tie the floor to a per-profile rerun_fraction table.**
  Rejected: per-profile tuning is already a Phase 3 concern
  per [`05 § Pipeline`](../spec/05-validator.md#pipeline)
  step 4. Doing it now adds knobs with no calibration data.

## Related

- Spec: [`05-validator.md § Coverage under thin validator sets`](../spec/05-validator.md#coverage-under-thin-validator-sets);
  [`20-economic-model.md`](../spec/20-economic-model.md) §§
  Parameter inventory, Validator registration;
  [`00.5-foundations.md § E`](../spec/00.5-foundations.md#e-empirical-posture--whats-proven-vs-whats-a-bet);
  [`invariants.md`](../spec/invariants.md) HM-INV-0030.
- ADRs: [0010](0010-economic-strategy.md) — the strategy doc
  whose gap-review surfaced this work.
- Roadmap: validator-count target at Phase 2 onset; first
  measurement against the floor at Phase 2 entry; revisit
  cadence per
  [`00.5 § Review cadence`](../spec/00.5-foundations.md#review-cadence).

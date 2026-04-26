---
name: 0019 viability verdict not viable as designed
description: early viability verdict based on PR-E.2 and PR-E.3 alone; the design fails criteria 2 and 3 jointly at reference numbers; trigger tier-2 pivot
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0019 — Viability verdict: not viable as designed

## Context

[ADR 0016](0016-viability-decision-protocol.md) defined four
numerical viability criteria and a three-verdict decision
protocol; the maintainer commits to publishing a verdict ADR
once the four criteria are measured. The plan in
`/home/roy/.claude/plans/lets-create-a-plan-iridescent-riddle.md`
includes an explicit escape clause: *"if a cheap analysis
shows fundamental non-viability, the maintainer skips ahead
to the decision gate and triggers a tier-2/3 pivot directly.
Don't burn the remaining analyses if the answer is already
clear."*

After ADRs 0017 (validator unit economics) and 0018
(participation equilibrium), the answer is clear. The two
analyses, taken together, show the design fails criteria 2
and 3 jointly at reference numbers — and the failure is
*structural*, not a sensitivity edge case. PR-E.4 (sensitivity
tables), PR-E.5 (calibration ratchet), and the simulator (ADR
0021) would refine the magnitude but not change the verdict.

This ADR returns the verdict early per the escape clause.

## Decision

### Verdict: **not viable as designed at reference numbers**

ADR 0016's three-verdict taxonomy maps as follows on the
evidence so far:

| criterion | status | evidence |
|-----------|--------|----------|
| 1 — Miner median break-even ≥ 80 % of profiles | **Pass** at the threshold | [§ C](../spec/29-economic-survival.md#c-miner-unit-economics) — 4 of 5 profiles break even; `multi-gpu-4x80gb` is the documented duopoly (`N ≈ 2`). |
| 2 — Validator break-even at `N ≥ 6` | **Fail** | [ADR 0017](0017-validator-unit-economics.md) — heavy profiles unprofitable at any `N`; even `cpu-small` requires `N_miners ≤ 50` to keep `V_max ≥ 6`. |
| 3 — Stable, attracting equilibrium reachable from Phase 2.0 | **Formal pass, coupled fail** | [ADR 0018](0018-participation-equilibrium.md) — fixed point exists and attracts but lands at `(410, 1.1)` for `cpu-small`, below the D2.2 floor. The two criteria are coupled. |
| 4 — Robustness across `t_TAO ∈ [0.5, 2 ×]`, `E_epoch ∈ [0.5, 2 ×]` | **Not yet measured (PR-E.4)** | Criteria 2–3 fail at reference; criterion 4 cannot save them. |

Criterion 2 fails outright; criterion 3 passes formally but
the attractor lands in a regime that violates D2.2's own
precondition. The verdict per ADR 0016 is therefore
**"not viable as designed"** — multiple criteria fail or
coupled-fail at reference numbers.

### Why this is structural, not a sensitivity edge case

The asymmetric break-even shape is the root cause: validator
revenue is fixed per epoch (`E_epoch · f_validator · t_TAO`)
while validator cost grows with `N_miners` (every validator
reruns every submission). No combination of `(t_TAO, E_epoch,
f_miner, rerun_fraction)` within ADR 0016's `[0.5, 2 ×]`
robustness range lifts the attractor above the D2.2 floor for
mid-or-heavier-profile workloads:

- Lifting `f_validator` from 0.18 to its theoretical ceiling
  of 1.0 leaves `V_max(N_m_max) ≈ 6` for `cpu-small` only —
  *just* meets the floor at the boundary, fails everywhere
  else.
- Lifting `t_TAO` to 2 × reference (`$600`) lifts both sides
  of the break-even formula proportionally; the *ratio*
  doesn't change the attractor's relationship to the floor.
- Lowering `rerun_fraction` from 0.4 to 0.2 (lever 1) cuts
  validator cost in half but also halves D2.2's coverage
  (per [HM-INV-0030](../spec/05-validator.md#coverage-under-thin-validator-sets)),
  forcing a new floor at `N ≥ 11`. Net: no improvement in the
  combined criterion.

Tier-1 levers cannot lift the attractor above the floor. The
verdict therefore mandates a **tier-2 pivot**.

### Recommended pivot: lever 4 + lever 5 combined

The cleanest tier-2 response, executed in PR-X (forthcoming
ADR 0020):

1. **Classify hypothesis profiles into tiers.**
   - **Safe tier:** `cpu-small`, `cpu-large`. Submission
     economics work at moderate `N_miners` without
     supplementation.
   - **Gated tier:** all `single-gpu-*` and `multi-gpu-*`
     profiles. Validator break-even requires either a
     bounded miner count (impractical) or external subsidy.
2. **Gated hypotheses require a `sponsorship` block.** The
   block names a counterparty per
   [`27 § C.1`](../spec/27-economic-strategy.md#c1-sponsored-hypotheses)
   and a bounty that funds the gap between emission-side
   validator break-even and the actual workload cost. The
   placeholder split is `60 / 30 / 10` (miner / validators /
   subnet treasury) per
   [`27 § G open question 2`](../spec/27-economic-strategy.md#g-open-questions);
   the validator share covers the rerun-cost shortfall.
3. **Hypotheses without a sponsorship block default to the
   safe tier.** A gated-profile hypothesis without
   sponsorship is rejected at acceptance.

This combines lever 4 (acceptance gate based on break-even)
with lever 5 (treasury / sponsor inflow) such that:

- Safe-tier workloads run on emission-side economics alone.
- Gated-tier workloads carry their own funding.
- The validator workload mix stays bounded by the
  sponsorship pipe's volume.

Trade-off: heavy-GPU hypotheses are no longer freely
permissionless — they require a counterparty. This narrows
the market for that subset. Acceptable: § C of doc 29 already
documented heavy-profile workloads as a duopoly, and ADR 0010
named sponsorship as the intended path for that class anyway.

### Status of PR-E.4, PR-E.5, and PR-S

These remain scheduled but **no longer block Phase 2 onset**:

- **PR-E.4 (sensitivity tables).** Still useful: quantifies
  the safe-tier ceiling (where does `cpu-small` workload
  start failing at scale even after the pivot?) and informs
  follow-up tier-1 adjustments. Recommended for landing
  before Phase 2 testnet onset; not blocking.
- **PR-E.5 (calibration ratchet).** Required machinery for
  Phase 2 retrospective. Blocking Phase 3, not Phase 2.
- **PR-S (simulator, ADR 0021).** Validates the analytic
  results numerically and supports tier-3 lever 6 modelling
  if the network ever needs it. Blocking neither Phase 2 nor
  Phase 3 in the current path.

The maintainer's commitment is to land all three before the
Phase 2 mid-point review, regardless.

## Consequences

- **Positive.** The "is this subnet viable?" question is
  resolved with a documented answer and a documented response.
  The maintainer is no longer blocked on indefinite
  uncertainty. Phase 2 onset can proceed with the pivot in
  place rather than waiting on three more analytical PRs that
  the math shows cannot change the verdict. The pivot
  (lever 4 + 5) leverages mechanisms the spec already has
  scaffolding for (the
  [`27 § C.1`](../spec/27-economic-strategy.md#c1-sponsored-hypotheses)
  sponsorship path and the
  [`28 § E`](../spec/28-treasury.md#e-outflow-rules)
  treasury rules).
- **Negative.** Heavy-GPU hypotheses are no longer
  permissionless. Contributors who want to run a
  `multi-gpu-4x80gb` hypothesis must find a sponsor. This is
  a real reduction in the design's permissionless-market
  framing for that hypothesis class. The strategy doc
  ([`27 § C.1`](../spec/27-economic-strategy.md#c1-sponsored-hypotheses))
  already implied this; making it explicit costs some of the
  "flat market" narrative.
- **Negative.** The early verdict means the maintainer is
  acting on partial evidence. PR-E.4's sensitivity sweep
  *could* surface a counter-example (some
  `(t_TAO, E_epoch, f_miner, rerun_fraction)` combination
  inside the `[0.5, 2 ×]` range that lifts the attractor
  above the floor). The structural argument in § "Why this
  is structural" makes that unlikely, but it's not proven.
  Mitigation: PR-E.4 still ships before Phase 2 mid-point
  review; if it surfaces a counter-example, this verdict ADR
  is superseded by a corrected one.
- **Neutral / deferred.** The cycle-time / capacity ceiling
  per
  [`19 § Validator SLIs`](../spec/19-operations.md#validator-slis)
  imposes an additional hard cap on validator workload that
  the pivot doesn't address; PR-E.4 folds it into the
  sensitivity surfaces. Does not change this verdict.

## Options considered

- **Wait for PR-E.4 + PR-E.5 + PR-S before publishing a
  verdict.** Rejected: the plan's escape clause exists
  precisely for this case. The structural finding from
  ADRs 0017 + 0018 is not a sensitivity edge case; the
  remaining analyses cannot overturn it short of a counter-
  example that the structural argument rules out a priori.
- **Return "marginal" instead of "not viable as
  designed".** Rejected: ADR 0016 defines marginal as "one
  or two criteria fail by < 30 %". Criterion 2 fails by
  ~100 % for heavy profiles (no break-even at any `N`);
  criterion 3 fails because the attractor is at ~1
  validator vs the floor of 6 (~83 % gap). Both exceed the
  30 % threshold. "Not viable as designed" is the honest
  verdict.
- **Skip the tier-2 pivot and go straight to tier-3
  (strategic redesign).** Rejected: tier-2 lever 4 + 5
  combined uses existing spec scaffolding and is reversible.
  Tier-3 is the right escalation if PR-X (forthcoming) shows
  the sponsorship pipe is itself non-viable; that is a Phase
  2 empirical finding, not an a-priori one.
- **Trigger lever 2 (raise `f_validator`) only.** Rejected:
  the math in § "Why this is structural" shows lifting
  `f_validator` to its theoretical maximum of 1.0 only just
  meets the floor for `cpu-small` at the attractor, and is
  insufficient for non-trivial profile mixes.
- **Trigger lever 1 (raise `rerun_fraction`) only.**
  Rejected: cuts both ways — raising fraction cuts validator
  cost but raises D2.2 floor proportionally. Net change in
  the combined criterion is zero.

## Related

- Spec: [`29 § E`](../spec/29-economic-survival.md#e-viability-criteria)
  — the criteria this verdict resolves;
  [§ C](../spec/29-economic-survival.md#c-miner-unit-economics),
  [§ D.1](../spec/29-economic-survival.md#d1-validator-unit-economics),
  [§ D.2](../spec/29-economic-survival.md#d2-participation-equilibrium)
  — the analyses the verdict cites;
  [§ D.3](../spec/29-economic-survival.md#d3-sensitivity-tables-pr-e4),
  [§ D.4](../spec/29-economic-survival.md#d4-calibration-ratchet-pr-e5)
  — placeholders for the analyses still scheduled.
- Spec: [`27 § C.1`](../spec/27-economic-strategy.md#c1-sponsored-hypotheses)
  — sponsorship path the lever 4 + 5 pivot leverages;
  [`28 § E`](../spec/28-treasury.md#e-outflow-rules) —
  treasury rules that absorb the bounty residual.
- ADRs: [0016](0016-viability-decision-protocol.md) —
  defined the criteria + verdict taxonomy this ADR uses;
  [0017](0017-validator-unit-economics.md),
  [0018](0018-participation-equilibrium.md) — the structural
  findings the verdict cites.
- Forthcoming: ADR 0020 (PR-X — sponsor-gated heavy
  profiles), ADR 0021 (simulator), and the corrected verdict
  ADR after PR-E.4 if a counter-example appears.

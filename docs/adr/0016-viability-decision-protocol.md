---
name: 0016 viability decision protocol
description: name four numerical viability criteria, a three-verdict decision protocol, and the seven-lever pivot ladder triggered by a non-viable verdict
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0016 — Viability decision protocol + pivot ladder

## Context

ADRs 0011–0015 closed the five gaps surfaced by the
post-strategy-doc gap review and opened the quantitative
work stream in
[`29-economic-survival.md`](../spec/29-economic-survival.md).
The maintainer remained uncertain about whether the subnet's
economics actually work: § C of doc 29 already showed
`multi-gpu-4x80gb` profiles are a structural duopoly
(`N_break-even ≈ 2`) at reference numbers, and the four
follow-up PRs (E.2–E.5) hadn't landed yet.

The right response is not "do more economic spec PRs forever"
but **make viability decidable**: define what "viable" means
numerically, run the analyses that resolve the question,
publish a decision, and pivot if the answer is no. This ADR
captures the protocol that converts the analyses into a
decision and the response to a "not viable" verdict.

## Decision

### Four numerical viability criteria

Added in
[`29 § E — Viability criteria`](../spec/29-economic-survival.md#e-viability-criteria):

1. **Miner median break-even.** `s_miner = 1/N_miners`
   profitable for ≥ 80 % of supported hypothesis profiles at
   reference parameters.
2. **Validator break-even.** Validator dividend share covers
   rerun cost + overhead at the
   [HM-INV-0030](../spec/05-validator.md#coverage-under-thin-validator-sets)
   floor of `N ≥ 6`.
3. **Stable participation equilibrium.** A locally-attracting
   fixed point exists, reachable from the
   [Phase 2.0 cold-start position](../spec/11-roadmap.md#phase-20-cold-start).
4. **Robustness.** Criteria 1–3 hold under
   `t_TAO ∈ [0.5, 2.0] · reference` and
   `E_epoch ∈ [0.5, 2.0] · reference`.

Viable = all four pass. The ±2× sensitivity range matches the
plausible Q2 2026 → Q3 2027 swing observed across mature
crypto-asset price histories; tighter would be optimistic,
wider would force spurious "non-viable" verdicts on every
single-shot black-swan day.

### Three-verdict decision protocol

After PR-E.2 through PR-E.5 + the simulator (ADR 0021) land,
the maintainer publishes a **viability ADR** with one of:

- **Viable.** All four criteria pass. Proceed to Phase 2
  testnet onset without further pivot.
- **Marginal.** One or two criteria fail by < 30 %. Enact a
  tier-1 pivot (levers 1–3 below) and re-evaluate.
- **Not viable as designed.** Multiple criteria fail or any
  fail by ≥ 30 %. Enact a tier-2 (levers 4–5) or tier-3
  (levers 6–7) pivot.

The decision is not purely numerical — the maintainer weighs
Phase 2 onboarding cost against verification confidence — but
the criteria provide a defensible base case and prevent
indefinite uncertainty.

### Seven-lever pivot ladder

Ranked by reversibility / disruption. Each lever is its own
≤ 500-LoC PR triggered by the viability verdict.

| # | tier | lever | what changes |
|---|------|-------|--------------|
| 1 | 1 | Adjust `rerun_fraction` | Raise to compensate for thin validator set; trade compute cost for coverage. Range 0.4 → 0.7. |
| 2 | 1 | Adjust emission split | Currently 82/18; range 70/30 to 90/10 to rebalance miner / validator break-even. |
| 3 | 1 | Cost-table adjustments | Per-profile budget changes per [`06 § Cost penalty`](../spec/06-scoring.md#cost-penalty); subsidise tight profiles. |
| 4 | 2 | Tighten hypothesis-acceptance gates | Reject profiles below break-even N at current network size. Lands as a new schema rule in [`02-hypothesis-format.md`](../spec/02-hypothesis-format.md). |
| 5 | 2 | Treasury thin-network subsidy | Tap [`28 § E`](../spec/28-treasury.md#e-outflow-rules) per-cycle to bridge break-even gap until `N` grows. |
| 6 | 3 | Strategic pivot | Subnet becomes primarily sponsorship-funded rather than emission-funded; rewrites [`27 § D`](../spec/27-economic-strategy.md#d-phase-by-phase-trajectory) and adds a new C-row. |
| 7 | 3 | Subnet redefinition | Foundation-review-class change; engages [`26-external-review.md`](../spec/26-external-review.md) reviewer ahead of schedule. |

The maintainer commits to escalating only after the prior
tier failed empirically — cheaper levers first, redesign-class
last.

## Consequences

- **Positive.** "Is the subnet viable?" stops being a vibe
  and becomes a question with measurable evidence and a
  defined decision protocol. The maintainer cannot
  indefinitely defer Phase 2 onset on grounds of
  unquantified worry; the four PRs E.2–E.5 + the simulator
  (ADR 0021) produce the evidence, the verdict ADR locks in
  the answer. The pivot ladder gives the maintainer a
  pre-specified response to a "not viable" finding rather
  than improvising under pressure.
- **Negative.** The four criteria are themselves a design
  choice (e.g., "why 80 % of profiles, not 100 %?"). A future
  reviewer who disagrees with the thresholds can argue the
  whole protocol misses the question. Mitigation: the criteria
  cite specific spec sections that defend each threshold, and
  the
  [`26-external-review.md`](../spec/26-external-review.md)
  review explicitly includes scope to challenge them.
- **Neutral / deferred.** The actual viability ADR (with
  measured values + verdict) is *not* this ADR — it lands
  separately once PR-E.2 through PR-E.5 + ADR 0021's
  simulator merge. This ADR sets up the framework; the
  verdict ADR fills it in.

## Options considered

- **No criteria, just keep iterating.** Rejected: was the
  status quo, and the user's "I'm still not sure" framing
  proved it. Indefinite uncertainty is the failure mode the
  protocol exists to close.
- **Tighter robustness range (`t_TAO ∈ [0.7, 1.5]`).**
  Rejected: too narrow to claim survival of typical
  crypto-asset volatility cycles; would force trivial
  "viable" verdicts that don't generalise.
- **Wider robustness range (`t_TAO ∈ [0.1, 10]`).** Rejected:
  no emission-funded subnet survives a 100× swing; testing
  for it would force universal "not viable" verdicts that
  don't differentiate this subnet's design from a hypothetical
  better one.
- **Demand 100 % of profiles pass criterion 1.** Rejected:
  § C already documents `multi-gpu-4x80gb` as a known narrow
  market; demanding viability there would force a spurious
  verdict on a finding the spec acknowledges.
- **Different verdict taxonomy (binary go/no-go).** Rejected:
  the marginal case is real and warrants tier-1 levers; a
  binary verdict would either over-pivot at small failures or
  under-respond at moderate ones.
- **Combine the criteria into a single weighted score.**
  Rejected: opaque to reviewers, and conceals which specific
  failure mode triggered a verdict. Four explicit criteria
  make the failure attributable.
- **Pivot ladder that names every parameter change as
  reversible.** Rejected: tier-3 redesign is genuinely
  hard to reverse — admitting that up front is honest
  governance.

## Related

- Spec: [`29-economic-survival.md § E — Viability criteria`](../spec/29-economic-survival.md#e-viability-criteria)
  (the canonical home for the criteria).
- Spec: [`27-economic-strategy.md`](../spec/27-economic-strategy.md)
  §§ C, D — strategy whose viability the criteria test;
  lever 6 rewrites § D.
- Spec: [`28-treasury.md § E — Outflow rules`](../spec/28-treasury.md#e-outflow-rules)
  — lever 5 ties into.
- Spec: [`05 § Coverage under thin validator sets`](../spec/05-validator.md#coverage-under-thin-validator-sets)
  — HM-INV-0030 referenced by criterion 2; lever 1 modifies
  `rerun_fraction`.
- Spec: [`20 § Parameter inventory`](../spec/20-economic-model.md#parameter-inventory)
  — every tier-1 lever updates a row here.
- Spec: [`11-roadmap.md § Phase 2.0`](../spec/11-roadmap.md#phase-20-cold-start)
  — equilibrium reachability anchor for criterion 3.
- ADRs: [0010](0010-economic-strategy.md) — set the strategy
  whose viability is now testable;
  [0011](0011-d22-coverage-bound.md) — D2.2 floor referenced
  by criterion 2 and lever 1;
  [0013](0013-cold-start-contingency.md) — Phase 2.0 starting
  position for criterion 3;
  [0014](0014-treasury-pre-dao.md) — treasury machinery lever
  5 taps;
  [0015](0015-economic-survival-scope.md) — opens the work
  stream this ADR makes decidable.
- The viability *verdict* ADR (forthcoming): published after
  PR-E.2 through PR-E.5 + the ADR-0021 simulator land; reports
  measured values and returns one of the three verdicts.

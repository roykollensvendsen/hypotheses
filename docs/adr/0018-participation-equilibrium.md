---
name: 0018 participation equilibrium
description: prove the miner-validator participation fixed point exists and attracts but lands below the D2.2 floor at reference numbers, coupling viability criteria 2 and 3
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0018 — Participation equilibrium

## Context

ADR 0017 (validator unit economics) revealed an asymmetric
break-even shape: miner break-even is bounded *below* by
`N_miners`; validator break-even is bounded *above* by
`1/N_miners`. Whether the system settles into a stable
participation steady state — and where it lands — is
[viability criterion 3](../spec/29-economic-survival.md#e-viability-criteria).

The verdict ADR cannot return "viable" without resolving
criterion 3 jointly with criterion 2. Until this analysis,
the question was open.

## Decision

Land § D.2 in
[`29-economic-survival.md`](../spec/29-economic-survival.md)
with three components:

1. **Replicator dynamics.** Standard two-population system
   with response rates `ε_m, ε_v > 0` and profit functions
   from § C and § D.1.
2. **Fixed-point existence + local stability proof.** A
   simultaneous zero `(N_m_max, V_max(N_m_max))` exists for
   each profile mix. The Jacobian at the fixed point has
   both eigenvalues negative; the fixed point is locally
   attracting.
3. **Reachability + landing zone.** From the
   [Phase 2.0 cold-start position](../spec/11-roadmap.md#phase-20-cold-start)
   (`≥ 3` miners, `≥ 2` validators) trajectories converge to
   the fixed point. At reference numbers and an
   all-`cpu-small` workload the fixed point lands at
   `≈ (410, 1.1)` — *below* the
   [HM-INV-0030](../spec/05-validator.md#coverage-under-thin-validator-sets)
   floor of `N ≥ 6`.

### The criterion-coupling finding

Criterion 3 in § E passes formally: a stable, reachable
fixed point exists. But the attractor lands in a regime
where criterion 2 (validator break-even at the D2.2 floor)
fails — D2.2 silently degrades when the equilibrium
N_validator is below 6.

**The two criteria are coupled.** The verdict ADR cannot
return "viable" on criteria 2 + 3 together at reference
numbers. This is the second mechanism-level deficit (after
ADR 0017) the analysis surfaces.

### Pivot implications

- **Tier-1 levers (parameter adjustments) are insufficient.**
  Lifting `f_validator` from 0.18 to its theoretical maximum
  of 1.0 only just meets the floor at the all-`cpu-small`
  fixed point; realistic adjustments leave the attractor
  below.
- **Tier-2 lever 4 (hypothesis-acceptance gate) works.**
  Capping `N_miners ≤ 50` keeps the attractor at
  `(50, 8.85)` — viable. Trade-off: the market becomes a
  constrained-supply oligopoly.
- **Tier-3 lever 6 (sponsor-funded subsidy) restructures
  the dynamic.** Adding sponsor inflow as a third
  population changes the validator profit equation;
  PR-E.4's sensitivity tables will quantify the subsidy
  required.

## Consequences

- **Positive.** Criterion 3 is now mechanical — existence,
  stability, reachability are proven (under the simple
  replicator-dynamics model). The criterion-coupling finding
  is concrete and cites the ADRs and spec sections that
  carry the math. The verdict ADR has unambiguous evidence
  to act on.
- **Negative.** The reference-number verdict on criteria 2
  and 3 is **fail**. Phase 2 cannot ship at reference numbers
  with heavy-profile hypotheses and the current
  `f_validator = 0.18` and no compensating mechanism. This
  is a real constraint on Phase 2 onboarding choices and may
  force a tier-2 or tier-3 pivot before Phase 2 entry.
- **Neutral / deferred.** The cycle-time / capacity ceiling
  per [`19 § Validator SLIs`](../spec/19-operations.md#validator-slis)
  imposes an additional hard cap on `N_validator` at heavy
  workloads, beyond the dollar-economic ceiling here. PR-E.4
  folds it into the sensitivity surfaces. PR-S's simulator
  (ADR 0021, forthcoming) validates this analytic result
  numerically at intermediate parameter values.

## Options considered

- **Use a richer dynamic (e.g., heterogeneous-skill miners,
  validator-stake distribution).** Rejected: the simple
  replicator-dynamics model is sufficient to prove the
  qualitative finding. Adding heterogeneity would refine
  the fixed-point location but not change the criterion-
  coupling structure. Future PRs can refine if needed.
- **Combine D.2 with the worked-example sensitivity tables
  (PR-E.4).** Rejected: combined PR exceeds the 500-LoC cap
  and conflates the analytic existence proof with the
  numerical sensitivity sweep.
- **Defer the analysis until the simulator (PR-S) lands.**
  Rejected: analytic existence + stability is needed before
  the simulator has anything specific to validate. Order is
  analytic → numerical, not the reverse.
- **Restate criterion 3 to require the attractor be above
  the D2.2 floor.** Rejected: ADR 0016's criteria are
  intentionally minimal; coupling them at the criterion
  level would obscure that two structurally distinct
  questions (existence-and-stability vs floor-respecting)
  both have to hold. Better to surface the coupling in the
  analysis and let the verdict ADR weight them jointly.

## Related

- Spec: [`29 § D.2`](../spec/29-economic-survival.md#d2-participation-equilibrium)
  — the canonical home;
  [`29 § E criterion 3`](../spec/29-economic-survival.md#e-viability-criteria)
  — the criterion this analysis closes;
  [`29 § C`](../spec/29-economic-survival.md#c-miner-unit-economics),
  [`29 § D.1`](../spec/29-economic-survival.md#d1-validator-unit-economics)
  — the profit formulas this dynamic uses.
- Spec: [`05 § Coverage under thin validator sets`](../spec/05-validator.md#coverage-under-thin-validator-sets)
  — HM-INV-0030 floor that criterion 2 enforces;
  [`11 § Phase 2.0`](../spec/11-roadmap.md#phase-20-cold-start)
  — initial condition for the trajectory.
- ADRs: [0011](0011-d22-coverage-bound.md) — D2.2 floor;
  [0015](0015-economic-survival-scope.md) — opens work
  stream;
  [0016](0016-viability-decision-protocol.md) — criteria
  this analysis closes;
  [0017](0017-validator-unit-economics.md) — supplies the
  validator-side profit function.

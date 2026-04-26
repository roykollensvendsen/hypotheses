---
name: 0017 validator unit economics
description: pin the per-cycle validator break-even formula and surface the asymmetric cost-revenue shape that drives the equilibrium analysis in PR-E.3
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0017 — Validator unit economics

## Context

ADR 0015 opened the economic-survival work stream and named
PR-E.2 as validator unit economics. The miner side (§ C of
[`29-economic-survival.md`](../spec/29-economic-survival.md))
landed in ADR 0015 with an explicit break-even formula `(*)`.
Validator break-even was deferred — but it is the second
viability criterion in § E (per ADR 0016), so until it lands
the decision protocol cannot return a verdict.

The asymmetry between the two sides was suspected but not
written down: validators rerun what miners submit, so
validator workload (and thus cost) scales with miner output,
while validator emission is fixed per-epoch. This means more
miners → more validator cost → fewer validators can break
even.

## Decision

Land § D.1 in
[`29-economic-survival.md`](../spec/29-economic-survival.md)
with three components:

1. **Per-cycle revenue.** Median validator dividend share
   `(E_epoch · f_validator · t_TAO) / N_validators`.
2. **Per-cycle cost.** Workload-proportional cost
   `k · N_miners · rerun_fraction · c_compute` plus an
   assumed `c_overhead_validator = $0.10/epoch`. The
   `S_seeds_avg` factor cancels because per-seed cost scales
   inversely with seed count.
3. **Break-even ceiling formula `(**)`.**
   `N_validators ≤ (E_epoch · f_validator · t_TAO) / (k · N_miners · rerun_fraction · c_compute + c_overhead_validator)`.

### Worked example findings

At Q2 2026 reference numbers and `c_overhead_validator = $0.10`:

- `N_miners = 50, all-cpu-small`: break-even `N_validators ≈ 9`
  — just above the
  [HM-INV-0030](../spec/05-validator.md#coverage-under-thin-validator-sets)
  floor of 6.
- `N_miners = 50, single-gpu-24gb`: **no** validator count is
  profitable.
- `N_miners = 100, cpu-small`: break-even `N_validators ≈ 4`
  — *below* the D2.2 floor.

This is **the first criterion in [§ E](../spec/29-economic-survival.md#e-viability-criteria)
that fails at reference numbers** outside the cheap-profile
thin-network corner. ADR 0016's three-verdict protocol cannot
return "viable" without one of:

- (a) Recalibration (PR-E.5) showing `c_overhead_validator`
  dramatically lower than assumed.
- (b) Lever 2 — raise `f_validator` from 0.18 to ~0.30, lifting
  validator revenue ~67%.
- (c) Lever 4 — hypothesis-acceptance gate enforcing a
  cheap-profile floor on the workload mix.
- (d) PR-E.3's equilibrium analysis showing dynamics the
  analytic ceiling here misses.

The verdict is therefore **not yet "viable"** — but also not
yet "not viable" either, since PR-E.3, PR-E.4, PR-E.5, and
ADR 0021 remain. This ADR does not return a verdict; it
records the criterion-2 deficit so the eventual verdict ADR
has the data.

## Consequences

- **Positive.** Validator break-even is now mechanical, not
  hand-waved. The asymmetric `(*) / (**)` shape — miner
  break-even bounded *below* by `N_miners`, validator
  break-even bounded *above* by `1/N_miners` — is the load-
  bearing structure for PR-E.3's fixed-point analysis. The
  finding that heavy-profile workloads break the validator
  side is concrete, attributable, and pivot-actionable per
  the levers in ADR 0016.
- **Negative.** The criterion-2 deficit at reference numbers
  is real and might force a tier-1 or tier-2 pivot before
  Phase 2 onset. The maintainer cannot ship Phase 2 with
  heavy-profile hypotheses *and* the current `f_validator =
  0.18` *and* no compensating mechanism. That's a constraint
  on Phase 2 onboarding choices.
- **Neutral / deferred.** `c_overhead_validator = $0.10` is
  assumed, not measured; PR-E.5's calibration ratchet
  refines it. The validator-side cycle-duration cap (cycle
  must complete in 20 minutes per
  [`19 § Validator SLIs`](../spec/19-operations.md#validator-slis))
  imposes an additional ceiling beyond pure cost — a
  validator can't profitably take a workload that exceeds
  its compute capacity even if it's profitable on dollars.
  PR-E.3 introduces this constraint explicitly.

## Options considered

- **Different revenue model (proportional to weight-vector
  alignment, not stake share).** Rejected: validator
  dividends on Bittensor are stake-bonded per
  [`20 § Emission flow`](../spec/20-economic-model.md#emission-flow);
  modelling them as alignment-bonded would diverge from chain
  reality.
- **Treat `c_overhead_validator` as zero.** Rejected: even at
  zero, the criterion-2 deficit appears at heavier profiles —
  the overhead doesn't change the qualitative finding. Pinning
  `$0.10` is an honest placeholder.
- **Defer the worked example until calibration data exists.**
  Rejected: the existing miner-economics § C already used a
  worked example at reference numbers; symmetry is right.
  Calibration via PR-E.5 updates both sides simultaneously.
- **Combine D.1 with PR-E.3's equilibrium analysis in one
  PR.** Rejected: combined PR would exceed the 500-LoC cap
  and conflate two different analyses (validator unit
  economics vs the miner-validator joint fixed point).
- **Add an explicit cycle-time / capacity ceiling here.**
  Rejected: that's a different constraint shape (workload
  capacity, not break-even); cleaner to introduce in PR-E.3
  where the equilibrium has to handle multiple constraints.

## Related

- Spec: [`29 § D.1`](../spec/29-economic-survival.md#d1-validator-unit-economics)
  — the canonical home;
  [§ C miner economics](../spec/29-economic-survival.md#c-miner-unit-economics)
  — the symmetric miner-side analysis;
  [§ E viability criteria 2](../spec/29-economic-survival.md#e-viability-criteria)
  — the criterion this ADR's deficit feeds into.
- Spec: [`05 § Pipeline`](../spec/05-validator.md#pipeline)
  — `rerun_fraction = 0.4` and per-cycle cadence;
  [`05 § Coverage under thin validator sets`](../spec/05-validator.md#coverage-under-thin-validator-sets)
  — HM-INV-0030 floor of 6;
  [`19 § Validator SLIs`](../spec/19-operations.md#validator-slis)
  — cycle-duration cap.
- Spec: [`06 § Cost penalty`](../spec/06-scoring.md#cost-penalty)
  — per-profile `c_compute` table.
- Spec: [`20 § The 82/18 split`](../spec/20-economic-model.md#the-8218-split)
  — `f_miner` / `f_validator` defaults; lever 2 modifies
  these.
- ADRs: [0011](0011-d22-coverage-bound.md) — D2.2 floor;
  [0015](0015-economic-survival-scope.md) — opens the work
  stream;
  [0016](0016-viability-decision-protocol.md) — the criteria
  this analysis feeds.

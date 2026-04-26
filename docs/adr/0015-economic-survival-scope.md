---
name: 0015 economic survival scope
description: open the quantitative survival-analysis work stream with a scope doc and the first sub-section (miner unit economics)
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0015 — Economic survival scope + miner economics

## Context

[`0010-economic-strategy.md`](0010-economic-strategy.md) and the
strategy doc it landed
([`27-economic-strategy.md`](../spec/27-economic-strategy.md))
explicitly deferred quantitative survival analysis as a
"separate multi-PR work stream … worth doing before mainnet but
not blocking [the strategy] PR."

The post-strategy-doc gap-review re-listed it as the largest
remaining gap. ADRs 0011, 0012, 0013, 0014 closed the four
structural gaps (D2.2 floor, c7 measurement, cold-start
contingency, treasury custody). Quantitative survival is the
fifth and structurally last one.

### Predecessor ADRs in the gap-fix sequence

The post-strategy-doc gap-review surfaced five economic-
feasibility gaps that the strategy doc 27 did not close. The
five ADRs that close them are sequenced cheapest-first so the
structural foundations land before the quantitative work
stream needs them. This ADR opens the fifth.

| gap | ADR | landed in |
|-----|-----|-----------|
| Validator-set thin regime — N below which D2.2 silently degrades | [0011](0011-d22-coverage-bound.md) | HM-INV-0030, `min_validators_d22_coverage = 6` |
| C7 (ground-truth latency < 12 months) untested | [0012](0012-c7-measurement.md) | settlement-latency p50/p95 SLI + HM-REQ-0070 revision trigger |
| Cold-start at Phase 2 entry — no thin-period plan | [0013](0013-cold-start-contingency.md) | Phase 2.0 sub-phase, c4a/c4b split, 60-day abort trigger |
| No subnet treasury — no fiduciary mechanism for non-TAO revenue | [0014](0014-treasury-pre-dao.md) | [`28-treasury.md`](../spec/28-treasury.md), c12-pre-dao-custody |
| Quantitative survival analysis (this ADR) | [0015](0015-economic-survival-scope.md) | [`29-economic-survival.md`](../spec/29-economic-survival.md), miner unit economics |

The four follow-up PRs (E.2–E.5) named in
[`29 § D — Sub-PR roadmap`](../spec/29-economic-survival.md#d-sub-pr-roadmap)
extend the fifth row over time; ADRs 0011–0014 are one-shot.

This ADR opens the work stream. It is intentionally *not* the
whole work stream — that needs four more PRs (E.2–E.5). The
purpose of this PR is to pin the modelling contract (variables,
units, calibrated-vs-assumed taxonomy) so the follow-ups slot in
without reinventing.

## Decision

Add new spec doc
[`29-economic-survival.md`](../spec/29-economic-survival.md)
with five sections:

- **A. Scope** — what's in this PR vs deferred to E.2–E.5.
- **B. Modelling contract** — variables and units table,
  calibrated/observable/assumed taxonomy, epoch baseline.
- **C. Miner unit economics** — break-even formula:
  `N_miners ≤ (E_epoch · f_miner · t_TAO) / (k · C_sub)`. A
  worked-example table at Q2 2026 reference numbers shows
  break-even `N_miners` per profile (≈410 on `cpu-small`, ≈2 on
  `multi-gpu-4x80gb`).
- **D. Sub-PR roadmap** — names the four follow-ups: validator
  unit economics, Nash equilibrium, sensitivity tables,
  calibration ratchet.
- **E. Open questions** — `E_epoch` real value at registration;
  `c_overhead` calibration; multi-profile portfolios;
  miner-skill heterogeneity.

The miner-economics sub-section connects the existing pinned
parameters
([`06 § Cost penalty`](../spec/06-scoring.md#cost-penalty),
[`20 § The 82/18 split`](../spec/20-economic-model.md#the-8218-split))
to the c4a / c4b assumption split landed in PR-C. The break-even
math reveals that `multi-gpu-4x80gb` hypotheses behave like a
duopoly at reference numbers — a real implication for
hypothesis-design discussions.

## Consequences

- **Positive.** The modelling contract is now pinned, so PR-E.2
  through E.5 don't re-invent variables. The miner-economics
  numbers immediately surface a structural finding (heavy-GPU
  profiles are economically narrow) that the strategy doc 27
  hand-waved past. c4a / c4b now have at least one quantitative
  pressure-test path.
- **Negative.** Pinning the modelling contract before the
  follow-ups land exposes a gap if a follow-up needs a variable
  not in the table — a small future ADR amends. Reference
  numbers (`E_epoch = 1`, `t_TAO = $300`) carry the same
  caveat as the cost-table USD values; if they shift in a way
  that invalidates the worked example, an interim ADR updates
  the example without re-opening the modelling contract.
- **Neutral / deferred.** The four follow-up PRs are scoped
  (each ≤ 500 LoC) but not yet committed to a calendar. The
  Phase 3 exit criterion in
  [`11-roadmap.md`](../spec/11-roadmap.md) is the deadline; the
  6-month foundation review per
  [`00.5 § Review cadence`](../spec/00.5-foundations.md#review-cadence)
  is the cadence trigger.

## Options considered

- **Land all five sections in one PR.** Rejected: would blow
  the 500-LoC cap and mix concerns. Each follow-up has its own
  reviewer focus.
- **Skip the modelling contract; let each follow-up invent
  variables.** Rejected: the mismatched-units bug is
  exactly what kills multi-PR analysis. One contract now is
  cheaper than four bilateral reconciliations later.
- **Use a different baseline (e.g., per-day instead of
  per-epoch).** Rejected: every existing spec doc denominates
  in epochs (rate limits, pipeline cadence, weight-set window).
  Following the existing convention costs nothing.
- **Defer until Phase 2 produces real numbers.** Rejected:
  Phase 2 onboarding is when sponsors first allocate dTAO; the
  modelling contract needs to exist before they form theses,
  not after.
- **Land miner economics without the worked-example numbers.**
  Rejected: a formula without numbers doesn't close the gap.
  The Q2 2026 reference numbers are imperfect but they make
  the implications (duopoly heavy-GPU profiles) legible.

## Related

- Spec: [`29-economic-survival.md`](../spec/29-economic-survival.md);
  [`00.5-foundations.md § C c4a / c4b`](../spec/00.5-foundations.md#c4a-emission-sufficient-steady-state);
  [`06 § Cost penalty`](../spec/06-scoring.md#cost-penalty);
  [`20 § Parameter inventory`](../spec/20-economic-model.md#parameter-inventory);
  [`27 § D — Phase 2.0`](../spec/27-economic-strategy.md#d-phase-by-phase-trajectory);
  [`28 § C — Operating-cost catalogue`](../spec/28-treasury.md#c-operating-cost-catalogue).
- ADRs: [0010](0010-economic-strategy.md) — surfaced the gap;
  [0011](0011-d22-coverage-bound.md) — D2.2 floor referenced;
  [0013](0013-cold-start-contingency.md) — c4a / c4b split;
  [0014](0014-treasury-pre-dao.md) — operating-cost catalogue
  the calibration ratchet (E.5) ties into.
- Roadmap: PR-E.2 through E.5 each their own ≤ 500-LoC PR;
  full survival analysis lands before Phase 3 mainnet exit
  criteria per [`11`](../spec/11-roadmap.md).

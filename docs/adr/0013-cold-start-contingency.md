---
name: 0013 cold-start contingency
description: name a bounded Phase 2.0 cold-start sub-phase with explicit exit criteria and a 60-day abort-and-revise trigger
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0013 — Cold-start contingency at Phase 2 entry

## Context

The post-strategy-doc gap-review surfaced cold-start as the
third concrete gap. Phase 2's stated goal in
[`11-roadmap.md`](../spec/11-roadmap.md) — `≥ 3` external
miners and `≥ 2` external validators participating — read as
both *target* and *precondition*. There was no plan for the
period between netuid registration and "steady-enough"
participation, and no defined response if recruitment stalled.

Three structural problems with leaving it implicit:

1. The Phase 2 goal numbers (3 miners, 2 validators) are below
   `min_validators_d22_coverage = 6` from
   [HM-INV-0030](../spec/05-validator.md#coverage-under-thin-validator-sets).
   D2.2 (reproduction-by-sampling) silently degrades during this
   period.
2. The pre-split `c4-emission-sufficient` assumption (now
   [c4a-emission-sufficient-steady-state](../spec/00.5-foundations.md#c4a-emission-sufficient-steady-state)
   per this ADR) was written for steady state. The thin-network
   economics during cold-start are honestly weaker, but the
   foundation table didn't say so.
3. There was no abort-and-revise trigger. A subnet that fails to
   recruit participants for months would silently drift, with no
   defined point at which the maintainer commits to revising
   defaults.

## Decision

Name **Phase 2.0 (Cold-start)** as a bounded sub-phase of Phase
2 with three exit criteria (any one suffices, all measured over
a 14-day trailing window):

1. `≥ 5` external miners and `≥ 3` external validators
   registered, at least one of each producing daily
   `validator.cycle.end` events.
2. `≥ 1` settled hypothesis end-to-end on testnet.
3. `≥ 1` concierge-sponsorship transaction per
   [`27 § C.1`](../spec/27-economic-strategy.md#c1-sponsored-hypotheses).

Add a **60-day abort-and-revise trigger** in
[`11 § Phase 2`](../spec/11-roadmap.md#phase-2--testnet-subnet):
if 60 days after netuid registration none of the three exit
criteria is satisfied, the maintainer opens an ADR revising
either Phase 2 exit criteria, the cost-side defaults in
[`20 § Parameter inventory`](../spec/20-economic-model.md#parameter-inventory),
or the strategy in [`27`](../spec/27-economic-strategy.md).

Split the prior `c4-emission-sufficient` row in
[`00.5 § C`](../spec/00.5-foundations.md#c-assumptions-the-defences-require)
into:

- **c4a-emission-sufficient-steady-state** — the original
  Phase 3 mainnet assumption.
- **c4b-emission-sufficient-cold-start** — the honestly weaker
  Phase 2.0 assumption, supported by either unaided thin-network
  economics or the cold-start contingency in `27 § D`.

Add a Phase 2.0 sub-bullet to
[`27 § D — Phase-by-phase trajectory`](../spec/27-economic-strategy.md#d-phase-by-phase-trajectory)
explaining the investment thesis during cold-start (allocators
absorb participation-recruitment risk).

Cross-reference HM-INV-0030's "raise rerun_fraction
proportionally" remediation from
[`docs/adr/0011-d22-coverage-bound.md`](0011-d22-coverage-bound.md)
as the maintainer's response when validator count is below the
D2.2 floor during 2.0.

## Consequences

- **Positive.** The cold-start period now has named exit
  criteria, a measurable abort trigger, and an honest assumption
  declaration (c4b is weaker than c4a). The maintainer's options
  during a stalled cold-start are pre-specified rather than
  improvised under pressure.
- **Negative.** Adds a sub-phase boundary the maintainer must
  track. The 60-day clock is a real commitment — failure to
  open the revision ADR by day 60 breaches the foundation
  review cadence in
  [`00.5 § Review cadence`](../spec/00.5-foundations.md#review-cadence).
  Mitigation: the same cadence already commits the maintainer
  to a 6-month review; the 60-day cold-start review is a
  tightening of that for one specific window, not a new
  unconnected commitment.
- **Neutral / deferred.** The concrete contingency tools
  (treasury-funded thin-period subsidy, temporary score-weight
  rebalance) are NOT specified here — that is PR-D's
  (treasury) and a future score-weights ADR's job. This ADR
  names the sub-phase, the exit criteria, and the trigger;
  follow-ups specify the levers.

## Options considered

- **Treat cold-start as informal.** Rejected: was the status
  quo. Drift over months without a named trigger is exactly
  the failure mode the post-strategy-doc gap-review flagged.
- **Pin cold-start exit at participant counts only (≥ 5 / ≥
  3).** Rejected: a subnet that lands a paying sponsor before
  hitting the participant target has *already* satisfied the
  thesis the cold-start phase exists to test. The
  earnings-side and settlement-side exits are equally valid
  evidence.
- **Tighter abort window (30 days).** Rejected: 30 days
  doesn't account for normal recruitment friction. 60 days is
  long enough that a stall is information, not noise.
- **Looser window (90 days).** Rejected: a 90-day stall costs
  the maintainer 50 % more attention before the trigger fires.
  60 days hits the inflection between "give it time" and
  "respond before drift compounds."
- **Define the contingency tools in this ADR.** Rejected:
  treasury-funded subsidy is PR-D; rerun-fraction adjustment
  is in ADR 0011. This ADR's job is the *boundary* and
  *trigger*, not the levers.

## Related

- Spec:
  [`11-roadmap.md § Phase 2.0`](../spec/11-roadmap.md#phase-20-cold-start);
  [`00.5-foundations.md § C c4a / c4b`](../spec/00.5-foundations.md#c4a-emission-sufficient-steady-state);
  [`27-economic-strategy.md § D — Phase 2.0`](../spec/27-economic-strategy.md#d-phase-by-phase-trajectory).
- ADRs: [0010](0010-economic-strategy.md) — surfaced the gap;
  [0011](0011-d22-coverage-bound.md) — D2.2 floor referenced
  for the rerun_fraction-bump remediation;
  [0012](0012-c7-measurement.md) — the SLI machinery extended
  here.
- Roadmap: 60-day abort-and-revise clock starts at netuid
  registration. First Phase 2.0 exit criterion satisfied →
  Phase 2 proper begins.

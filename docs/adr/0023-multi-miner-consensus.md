---
name: 0023 multi-miner consensus
description: handle hypotheses that need multiple independent miners to settle by adding min_settling_miners and min_refuting_miners thresholds
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0023 — Multi-miner consensus settlement

## Context

The pre-existing settlement mechanism is per-submission: the
first miner whose submission passes all gates and meets the
`success_criteria` (or `falsification_criteria`) flips the
hypothesis to `settled-*`, attributed by HM-REQ-0021's
deterministic ordering rule (block height → in-block index →
SS58 lex). This works well for single-miner experiments where
the protocol pins determinism end-to-end.

It does not work well for **replication-class** hypotheses:
claims that genuinely require multiple independent miners to
test before the result is trusted — e.g., "this finding from
paper X replicates across labs," "method M outperforms
baseline B in 60 % of conditions," or any high-stakes scientific
claim where one miner's pass alone is insufficient evidence.
The closest current behaviour is novelty-decay (1.0 / 0.5 /
0.0), which mathematically incentivises multi-miner
participation but doesn't *gate* settlement on consensus.

This ADR adds a settlement-gate mechanism so hypotheses can
declare a minimum independent-miner threshold for settlement.

## Decision

Add two optional fields to the hypothesis schema in
[`02 § min_settling_miners / min_refuting_miners`](../spec/02-hypothesis-format.md#min_settling_miners--min_refuting_miners):

```yaml
min_settling_miners: 3        # require 3 independent confirmations
min_refuting_miners: 2        # 2 independent refutations to refute
```

Both default to `1` (current behaviour). Higher values gate
settlement on consensus across distinct `miner_hotkey` values.

### HM-REQ-0150 (settlement gate)

> When `min_settling_miners > 1` (or `min_refuting_miners > 1`),
> the hypothesis transitions to `settled-supported` (or
> `settled-refuted`) only after that many distinct
> `miner_hotkey` values have each independently submitted a
> result that passes its corresponding criteria under
> validator consensus. The 70 % first-settlement payout
> splits equally across the qualifying miners at the
> threshold-met moment; the deferred 30 % follows the same
> split. Validators MUST reject a candidate consensus
> contributor whose `miner_hotkey` matches one already
> counted.

### Lifecycle integration

The T-SUP / T-REF transition rules in
[`17 § Transition table`](../spec/17-hypothesis-lifecycle.md#transition-table)
update to: "transition fires when `min_settling_miners`
distinct submissions have each passed under validator
consensus." For `min_settling_miners = 1` (the default), this
collapses to the existing rule.

The two-tier settlement section in
[`17 § Two-tier settlement`](../spec/17-hypothesis-lifecycle.md#two-tier-settlement)
clarifies that the 70 % first-settlement payout is split
equally across the N qualifying miners at the threshold-met
moment, and the deferred 30 % follows the same split at T-CON.

### Novelty mechanics (unchanged)

Novelty decays as today: first qualifying miner gets 1.0,
second 0.5, third+ 0.0. This applies *independently* of the
threshold. A `min_settling_miners = 5` hypothesis sees the
first 2 qualifying miners earn novelty 1.0 / 0.5 even though
the hypothesis stays `running` until the 5th confirmation
lands. The settlement payout then splits 70 % equally across
all 5; novelty is part of that payout, so the first 2 contribute
their novelty bonuses to the pool.

### Sybil defence

"Independent" is enforced as *distinct on-chain
`miner_hotkey`*. The same defences that protect F5 (Sybil
farming) per
[`00.5 § F5`](../spec/00.5-foundations.md#f5--sybil-farming)
apply unchanged: per-hotkey registration cost, per-hotkey
rate limit, per-hotkey storage quota, validator rerun on
each individual submission. An operator running multiple
hotkeys to manufacture fake consensus pays N registration
fees, N compute costs, and risks N rerun failures — the
arithmetic per
[`20 § Sybil cost for novelty gaming`](../spec/20-economic-model.md#sybil-cost-for-novelty-gaming)
applies, scaled by N.

## Consequences

- **Positive.** Replication-class hypotheses are now
  first-class. A claim like "Anthropic's circuit-discovery
  finding replicates" can declare `min_settling_miners: 5`
  and only flip status when 5 independent miners confirm —
  meaningful evidence for a scientific community, not just
  one miner's run. The mechanism is a strict superset of the
  existing single-submission flow; nothing breaks for
  defaults.
- **Positive.** The mechanism couples cleanly with ADR 0022's
  community bounty pool: a community-funded replication-class
  hypothesis attracts both demand-side signal (sponsors
  staking on it) and supply-side multi-miner evidence
  (5 confirmations to settle), which together is the
  strongest evidence the design can produce per submission.
- **Negative.** Settlement latency grows. A
  `min_settling_miners = 5` hypothesis takes longer to
  finalise than a single-miner one — exactly the point, but
  this couples with c7 (ground-truth latency) and may push
  some hypotheses past the 6-month deferred-settlement
  window. Mitigation: PR-E.5's calibration ratchet measures
  actual settlement latency for multi-miner hypotheses
  separately and recommends per-class adjustments.
- **Negative.** Novelty mechanics may feel less rewarding to
  the third+ miners on a high-threshold hypothesis. Their
  reproduction + improvement components still pay, and their
  share of the settlement payout (1/N of the 70 % + 30 %) is
  meaningful, but they don't get the novelty bonus. This is
  the cost of the consensus model.
- **Neutral / deferred.** The threshold is per-hypothesis;
  no global default beyond 1 is set. Authors / sponsors
  decide. PR-E.5 may surface that some hypothesis classes
  default to thresholds > 1 (e.g., security-hypotheses or
  high-stakes-policy claims); a follow-up ADR could codify
  per-class defaults.

## Options considered

- **Mechanism A (this ADR — consensus-required settlement).**
  Smallest extension; reuses existing rigor + reproduction +
  novelty machinery; no new statistical modelling.
- **Mechanism B — cross-miner statistical meta-analysis.**
  Define an `aggregation: meta-analysis` mode where the
  improvement metric combines multiple submissions
  (mean / weighted / Mantel–Haenszel). Rejected for now:
  per-metric aggregation rules are nontrivial to spec
  generically; a hypothesis that genuinely needs meta-
  analysis can be modelled today as several
  `min_settling_miners > 1` hypotheses on different
  variable ranges.
- **Mechanism C — distributed-experiment sharding.**
  Different miners take different shards of a too-big
  experiment. Rejected: significant coordination complexity;
  no Phase-1 use case justifies it.
- **Aggregate within a single submission via `seeds`.**
  Already supported (a miner declares 100 seeds; statistical
  test runs over them). Rejected as a *replacement* for
  multi-miner consensus because seed-aggregation is
  same-miner same-environment; replication needs different
  miners on potentially different infrastructure.
- **No threshold; rely on novelty-decay incentive alone.**
  Rejected: novelty-decay rewards multi-miner participation
  but doesn't *gate* settlement. A high-stakes claim could
  flip status on the first miner alone, which is exactly
  the failure mode replication-class hypotheses need to
  avoid.

## Related

- Spec: [`02 § min_settling_miners / min_refuting_miners`](../spec/02-hypothesis-format.md#min_settling_miners--min_refuting_miners);
  [`02 § Schema validation`](../spec/02-hypothesis-format.md#schema-validation)
  (HM-REQ-0150);
  [`17 § Transition table`](../spec/17-hypothesis-lifecycle.md#transition-table)
  (T-SUP / T-REF triggers updated);
  [`17 § Two-tier settlement`](../spec/17-hypothesis-lifecycle.md#two-tier-settlement)
  (split-payout clarification);
  [`requirements.md`](../spec/requirements.md),
  [`traceability.md`](../spec/traceability.md) — HM-REQ-0150
  rows.
- Spec (unchanged but relevant): [`06 § Novelty`](../spec/06-scoring.md#novelty)
  (HM-INV-0011 decay is independent of the threshold);
  [`05 § Pipeline`](../spec/05-validator.md#pipeline)
  (validator rerun applies per-submission as before);
  [`20 § Sybil cost for novelty gaming`](../spec/20-economic-model.md#sybil-cost-for-novelty-gaming)
  (Sybil arithmetic scales with N).
- ADRs: [0010](0010-economic-strategy.md);
  [0022](0022-community-bounty-pool.md) — community pools
  couple naturally with multi-miner consensus.
- Roadmap: PR-E.5 calibration ratchet measures multi-miner
  settlement latency; follow-up ADR may add per-class
  defaults if data warrants.

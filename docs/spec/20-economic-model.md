---
name: economic model
description: emission flow, parameter inventory, stake, sybil cost, governance over economic parameters
tokens: 3200
load_for: [governance, review, implementation]
depends_on: [06, 07]
---

# 20 — Economic model

The subnet's value to participants is economic: TAO flows from the
chain to validators, from validators to miners they scored, and from
staked holders through validator dividends. This document specifies
the flow, enumerates every parameter that shapes it, and documents
what is calibrated, what is deferred to simulation, and who can
change the numbers.

This doc complements, not replaces:

- [06 — Scoring](06-scoring.md) — how scores are computed.
- [07 — Incentive](07-incentive.md) — the qualitative incentive
  story.

Here we are quantitative where we can be and honest where we can't
be yet.

## Emission flow

```
  Bittensor chain
        │  (global emission schedule; subnet-agnostic)
        │
        ▼
  Subnet `netuid`
        │  (emission allocated to this netuid by root-subnet consensus)
        │
        │  split 82/18
        │
        ├──▶ miners (82%)
        │     │  distributed by validator-consensus weight vector
        │     │  (YUMA)
        │     │
        │     ▼
        │   miner hotkeys, proportional to their composite score
        │
        └──▶ validators (18%, as dividends)
              │  distributed by stake bonded to each validator
              │
              ▼
            validator hotkey + delegators
```

### Inputs to the flow

- **Global emission schedule** — set by Bittensor root; the subnet
  has no control. Assume constant-per-block for modelling.
- **Subnet netuid** — assigned at registration (Phase 2 kick-off).
  Prior to registration, everything below is dry-run.
- **Validator-consensus weight vector** — produced each epoch per
  [05 — Validator](05-validator.md); YUMA aggregates across
  validators, down-weighting persistent outliers.
- **Stake bonded to each validator** — determines validator
  dividend share; delegators stake to validators they trust.

### The 82/18 split

Initial values match Bittensor defaults. Rationale:

- **Miners at 82%** — miners do the bulk of the compute (running
  experiments). Rewarding them more aligns with where work
  concentrates.
- **Validators at 18%** — validators rerun a sampled fraction
  (`rerun_fraction = 0.4` per [05](05-validator.md)) and do
  orchestration. Not zero; not the majority.

The split is a parameter, not a universal truth. A rebalance toward
validators would be justified if reruns become the bottleneck (e.g.,
during heavy-GPU-profile hypotheses where validator rerun cost
approaches miner submission cost). Phase 2 simulation data decides;
Phase 0 ships at the Bittensor default.

## Parameter inventory

Every economic knob the subnet controls. Columns: default value,
who can change it, how.

| parameter | default | location | changed by | change mechanism |
|-----------|---------|----------|------------|------------------|
| miner / validator emission split | 82 / 18 | [07 § emission flow](07-incentive.md#emission-flow) | maintainer | spec PR + ADR |
| score weight — rigor | 0.20 | [06 § composite score](06-scoring.md#composite-score) | maintainer | spec PR + ADR |
| score weight — reproduction | 0.35 | same | maintainer | spec PR + ADR |
| score weight — improvement | 0.30 | same | maintainer | spec PR + ADR |
| score weight — novelty | 0.15 | same | maintainer | spec PR + ADR |
| cost penalty coefficient | 0.10 | same | maintainer | spec PR + ADR |
| per-profile wallclock budget (USD) | table in [06 § cost penalty](06-scoring.md#cost-penalty) | same | maintainer | spec PR + ADR |
| per-profile storage budget (USD) | table in [06 § cost penalty](06-scoring.md#cost-penalty) | same | maintainer | spec PR + ADR |
| rerun fraction | 0.40 | [05 § pipeline](05-validator.md#pipeline) | maintainer | spec PR + ADR |
| rerun tolerance (default) | 1% accuracy-like, 5% wallclock/FLOPs | [05 § pipeline](05-validator.md#pipeline) | maintainer | spec PR + ADR |
| announcement rate limit | 3 per hotkey per epoch | [05 § discover](05-validator.md#pipeline) | maintainer | spec PR + ADR |
| per-hotkey storage quota | 10 GiB | [03 § failure modes](03-architecture.md#failure-modes-the-architecture-must-resist) | maintainer | spec PR + ADR |
| per-artifact cap | 500 MiB | same | maintainer | spec PR + ADR |
| per-manifest cap | 1 MiB | same | maintainer | spec PR + ADR |
| novelty-tier bonuses | 1.0 / 0.5 / 0.0 | [06 § novelty](06-scoring.md#novelty) | maintainer | spec PR + ADR |

Every parameter has an ADR requirement on change (enforced by
[`adr-required.yml`](../../.github/workflows/adr-required.yml) for
the subset that lives in tooling configs; enforced socially for
the spec-only ones).

## Registration economics

### Subnet registration

- **One-time** chain-set cost at subnet registration (Phase 2
  kick-off). Burn in TAO; no subnet-side control.
- **Recurring** per-block validator-registration cost determined by
  Bittensor dynamics (not under subnet control).

### Miner registration

Registering as a miner costs TAO burned to the chain. The fee is
**Bittensor-dynamic** (not this subnet's decision). Current
structure (subject to change at the chain level):

- Burn amount scales with recent registration activity.
- Registered slots are finite per subnet.

Implications for the economics:

- **Sybil cost scales with registration fees.** Running N miner
  hotkeys burns N × (current fee) in TAO. Combined with the per-
  hotkey compute cost to actually run experiments, Sybil farming is
  economically unattractive vs. consolidating on one honest hotkey.
- **Low-activity miners risk deregistration** (Bittensor bumps
  inactive hotkeys). This couples naturally with the subnet's
  reproducibility requirements: a miner whose reruns fail earns
  nothing and gets pushed out.

### Validator registration

Validators have higher stake requirements than miners (Bittensor-
dynamic; typically ≥ 1000 TAO to be "effective" at weight-setting).
The subnet does not set this — the chain does — but the threshold
shapes validator-set size and therefore YUMA consensus dynamics.

**Design note.** Small validator sets (N < 5) are vulnerable to
collusion even with the self-scoring ban. The subnet design
anticipates a validator set growing from 3–5 in Phase 2 testnet to
≥ 10 at mainnet launch. Economic parameters assume the larger set;
a thin validator set is an operational concern, not a spec-level
failure mode.

## Scoring weight justification

The default weights `rigor=0.20, reproduction=0.35, improvement=0.30,
novelty=0.15` and `cost_penalty=0.10` encode specific priorities:

- **Reproduction is the largest component (0.35).** The subnet's
  value proposition is defensible knowledge. A claim that doesn't
  reproduce is worse than no claim.
- **Improvement (0.30) is second.** A reproducible claim that
  doesn't beat its baseline is a null; a reproducible claim that
  does is the point.
- **Rigor (0.20) is baseline.** A well-formed spec with seeds, a
  baseline, and a statistical test — any spec meeting these bars
  gets the rigor floor. This is deliberately easy to achieve;
  sloppy hypotheses fail other gates.
- **Novelty (0.15) is a tiebreaker.** Rewards first-to-settle
  without letting novelty alone dominate the score.
- **Cost penalty (0.10) keeps waste off.** Small enough to not
  penalise legitimate work; large enough that a wasteful run is
  outscored by an efficient one of equal rigor + reproduction +
  improvement.

**Sensitivity.** These numbers sum to 1 (excluding cost penalty).
Any rebalance requires:

1. A Phase 2+ simulation run showing the rebalance doesn't invert
   the ranking of known good vs. known bad submission archetypes.
2. An ADR documenting the empirical or analytical argument.

**Calibrated vs. assumed.** All five numbers are *assumed*, not
*calibrated*. No simulation data yet exists to defend them against
reasonable alternatives. Phase 2 exit criteria include the
calibration run (see [Known open questions](#known-open-questions)).

## Novelty economics

### Baseline novelty math

A miner's expected emission per submission breaks down as:

```
E = emission_per_epoch
  × composite_score / total_network_composite
```

Novelty contributes ≤ 0.15 to the composite score, so a first-
settling submission earns (very roughly) 18% more than the second
settler and 30% more than later settlers at equal other components.

Over a hypothesis's lifetime — typically one first, one second, many
thirds — the novelty flow concentrates on the first two miners.
This is intentional: posing and settling a new question is the
productive act; reruns after settlement keep the reproduction signal
alive but don't advance knowledge.

### Sybil cost for novelty gaming

**Threat.** Attacker registers N hotkeys, submits near-simultaneously,
hopes to capture novelty on N hypotheses at once.

**Defence mechanics:**

1. Novelty is per-hypothesis. Registering N hotkeys doesn't
   multiply novelty on any single hypothesis — only one hotkey can
   be "first".
2. Each submission requires real compute: ~$2 per submission on
   `single-gpu-24gb`, higher on larger profiles.
3. Each hotkey requires a registration fee in TAO (Bittensor-
   dynamic).
4. Each submission is subject to rerun verification; dishonest
   submissions produce zero emission.

**Cost to capture novelty on K hypotheses:**

```
cost ≈ K × (registration_fee_per_hotkey + compute_per_submission)
expected revenue ≈ K × (emission × novelty_bonus / total_network_composite)
```

Unless the attacker can corrupt the reproduction step (which
requires sandbox escape, dataset hash collision, or validator
collusion — all specifically defended in
[16 § threat model](16-threat-model.md)), the economic arithmetic
does not favour the attack.

### Novelty-race game theory

When multiple miners target the same hypothesis, the tiebreak in
[06 § ordering](06-scoring.md#ordering-tiebreak-for-simultaneous-settlements)
forces attribution by on-chain block height. A miner cannot pick
their block beyond ±inclusion latency, so races decay into "whoever
finishes the experiment first" — which is the healthy competitive
outcome.

## Cost penalty calibration

The cost penalty prevents wasteful submissions without penalising
honest work. The current budgets (from
[06 § cost penalty](06-scoring.md#cost-penalty)):

| profile | `budget_wallclock` | `budget_storage` |
|---------|-------------------:|-----------------:|
| `cpu-small`        | $0.10 | $0.05 |
| `cpu-large`        | $0.50 | $0.20 |
| `single-gpu-24gb`  | $2.00 | $0.50 |
| `single-gpu-80gb`  | $8.00 | $1.00 |
| `multi-gpu-4x80gb` | $40.00 | $2.00 |

**Calibration rule.** A submission that spends ≥ 100% of both
budgets gets `cost_penalty = 1.0` (the maximum deduction). A
submission that spends < 10% gets `cost_penalty ≈ 0`. The scaling
is linear, capped at 1.

**Implications.** On `cpu-small`, $0.15 wallclock spend (1.5× the
budget) yields `cost_penalty = min(1.0, 1.5 + 0) = 1.0`. At
`composite_weight_cost = 0.10`, that's a 10-point composite score
deduction — meaningful but not dominant.

**Pricing source.** The `cost.py` module carries a single USD-per-
hour table (see [06 § cost penalty](06-scoring.md#cost-penalty));
operators don't re-price per call. The table is maintainer-updated
on spec PR. Pricing noise matters less than relative ordering
between profiles.

## Incentive compatibility

The claim the economic model must defend: **honest play dominates
dishonest play for every rational miner**. This is structural, not
empirical.

### Honest-play arithmetic

For a miner with a working, well-formed hypothesis:

```
E_honest =
  emission × (rigor + reproduction + improvement + novelty - cost_penalty)
          / total_network_composite
```

For typical good submissions (rigor=1.0, reproduction=1.0,
improvement=0.7, novelty=1.0 on first, cost_penalty=0.05):

```
composite = 0.20 + 0.35 + 0.7*0.30 + 1.0*0.15 - 0.10*0.05 ≈ 0.91
```

### Dishonest-play arithmetic

For a miner trying to shortcut reproduction (e.g., cherry-picking
seeds):

```
composite =
  if rerun agrees (probability ≈ 0.4 in a single 5-seed attempt,
                   much lower on repeated attempts):
      rigor + reproduction + cherry-picked_improvement + novelty - cost_penalty
      ≈ 0.91 × P(rerun agrees)
  else: 0
```

Expected payoff ≈ 0.4 × 0.91 = 0.36 per attempt, vs. 0.91 for an
honest attempt. Honest play pays 2.5× in expectation even before
factoring in the reputational cost of public failed reruns.

### Regime where dishonest play is rational

Only if either:

1. The miner has no working hypothesis (reproduction = 0 regardless)
   — in which case they're not really mining anything.
2. The rerun tolerance is too loose (an open risk for consensus-
   answer oracles or noisy metrics); tightened per
   [05 § pipeline](05-validator.md#pipeline) and
   [18 § disagreement](18-oracle.md#disagreement-handling-same-oracle-cross-cycle).
3. The validator-consensus rerun-sample size falls (a single-validator
   regime). Mitigated by growing the validator set past 5.

None of these are intended steady-state regimes.

## Governance over economic parameters

All parameters in the inventory are maintainer-controlled in Phase
0–2 per [`GOVERNANCE.md`](../../GOVERNANCE.md). Changes require:

1. Spec PR editing the relevant doc (usually 06, 07, or this one).
2. ADR under `docs/adr/` explaining the rationale; quantitative
   changes ideally include either a simulation run or a published
   analytical argument.
3. Normal review + merge.

**What the maintainer cannot do:**

- Shift emission toward their own hotkey (`self-scoring ban`
  prevents this mechanically, not politically).
- Retroactively change weights to invalidate a settled hypothesis
  (version-bump-invalidates-prior-results rule applies, so the
  path exists — but would be a governance incident).
- Modify the 82/18 emission split beyond Bittensor's own mechanism
  (currently subnet-configurable; a large swing would trigger ADR
  + public discussion before PR).

Phase 3+ transitions governance to multi-maintainer or staked-voting
per [07 § governance](07-incentive.md#governance). Until then, the
maintainer is the economic authority and the AGPL fork-escape-hatch
is the continuity defence.

## Known open questions

Where the spec is honestly unsure and what Phase 2 simulation is
expected to resolve:

1. **Score weight calibration.** The 0.20/0.35/0.30/0.15 numbers
   are plausible-on-reflection, not calibrated. Phase 2 simulation
   runs a population of submission archetypes (honest high, honest
   low, dishonest high, dishonest low, honest null, spec-breakers)
   and tunes weights so the ranking matches intuition within
   reasonable bounds.
2. **Cost-table pricing.** USD values are approximate spot-market
   references for Q2 2026. Long-term the table needs periodic
   review; when it last moved and why should be recorded in
   `docs/adr/`.
3. **Novelty-decay curve.** `1.0 → 0.5 → 0.0` is a step function.
   An exponential decay (`e^(-k × block_gap)`) would reward fast
   seconds more gracefully; simulation needed.
4. **Rerun fraction 0.4 is plausible, not calibrated.** The
   security vs. compute-cost tradeoff hasn't been measured.
5. **Emission split 82/18 is Bittensor-default.** Not specifically
   calibrated for a research-market subnet where validator rerun
   cost may be relatively larger than a typical Bittensor subnet.
6. **Stake thresholds and Sybil arithmetic assume Bittensor
   dynamics that may change.** Re-validate when the chain updates
   its registration fee formula.

Each open question will land as an ADR when it resolves — positive
or negative. If Phase 2 simulation shows the weights are wrong in a
specific direction, the ADR documents that, the spec PR implements
the change, and this doc updates.

## Out of scope

- **Predicting TAO price.** The subnet's mechanism design is
  price-agnostic; what emission buys the operator in fiat is their
  problem.
- **Designing Bittensor's global emission schedule.** Not our
  authority.
- **Preventing users from giving away their TAO.** Delegation and
  staking decisions are external to the subnet mechanism.

## References

- [06 — Scoring](06-scoring.md) — formulas referenced here.
- [07 — Incentive](07-incentive.md) — qualitative incentive framing.
- [05 — Validator](05-validator.md) — rerun-fraction, rate limits.
- [16 — Threat model § A](16-threat-model.md#a-economic-attacks--dishonest-rewards)
  — economic attacks formally enumerated.
- [18 — Oracle](18-oracle.md) — oracle-disagreement tolerances
  relevant to incentive compatibility.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) — change process for
  economic parameters.

## Self-audit

This doc is done when:

- Every tunable parameter is in the inventory table with default,
  location, changer, and change mechanism.
- Every parameter's default is either calibrated (with cite) or
  explicitly labelled assumed.
- The incentive-compatibility arithmetic produces a concrete
  honest / dishonest payoff ratio.
- Every open question has a named resolution path (Phase X
  simulation / ADR trigger / external-dependency event).
- Sybil-cost claims reference the specific defences in
  [16 § A](16-threat-model.md#a-economic-attacks--dishonest-rewards).

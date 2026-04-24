---
name: incentive
description: weight setting, emission flow, anti-gaming countermeasures
---

# 07 — Incentive

## Weight setting

Each validator, at the end of its cycle, holds a score vector:

```
V = { miner_hotkey → composite_score in [0, 1] }
```

This is normalised to sum to 1 and committed on-chain via the standard
Bittensor `set_weights` extrinsic. YUMA consensus aggregates validator
vectors into the emission distribution.

Validators that disagree persistently with consensus are down-weighted by
YUMA; no subnet-side logic is required for that.

## Emission flow

Emission per epoch (Bittensor default: 360 blocks ≈ 72 minutes):

- 82% to miners, weighted by validator-consensus score.
- 18% to validators, as standard subnet dividends on their bond.

Numbers match Bittensor defaults; we may revisit after Phase 2 if
the balance of work warrants it (e.g. reruns are a larger share of
compute than proposing).

The quantitative model — parameter inventory, Sybil-cost
arithmetic, scoring-weight justification, calibration plan, and
governance over every tunable — is in
[20 — Economic model](20-economic-model.md).

## What emission rewards, concretely

- Proposing a well-formed, accepted hypothesis → zero direct emission.
  (Proposal without a result is unscored.)
- Submitting results that pass reproduction and either support or refute
  the claim → positive emission, scaled by the composite score.
- Being the first to settle an open hypothesis at the current version →
  novelty bonus.
- Being honest about a negative result → rigor + reproduction still score.

## What emission does not reward

- Flashy essays with no runnable protocol.
- Cherry-picked single-seed runs.
- "I got 99% accuracy" submissions without a declared baseline.
- Reruns of already-settled hypotheses (novelty = 0).
- Self-scored validator → own-miner loops (hard zero).

## Anti-gaming measures

### Preregistration

The single most important mechanism. A spec must be merged (with its
`success_criteria` and `falsification_criteria` frozen) before any results
referencing that `(id, version)` can be announced. Attempting to tune
thresholds post-hoc requires a `version` bump, which invalidates all
prior results — no advantage gained.

### Rerun sampling

Validators rerun a random sample of declared seeds. A dishonest miner does
not know which seeds will be rerun, so every declared seed must be honest.
The expected cost of submitting even one fabricated seed is `(1 −
(1 − rerun_fraction) ** 1) × submission_value + rerun_cost`.

### Open code

`experiments/<id>/` must be in `main` before results announce. A closed
"secret sauce" hypothesis is unsubmittable by construction.

### Hotkey-identity binding

`miner_hotkey` on a submission must match the signing key. Farms of
hotkeys still buy no advantage, because each hotkey is scored
independently and the validator rerun cost is per-submission.

### Self-scoring ban

Validators cannot score their own miner hotkey. Enforced: a validator's
weight vector must have `0` for its own miner hotkey. Validators that
violate this are anomalous and get down-weighted.

### Economic penalty for bad submissions

A submission that fails reproduction costs the miner its compute and earns
it zero. A miner whose submissions fail reproduction repeatedly will emit
nothing while burning wallclock and faces a reputational penalty (all
submissions are public, signed, on-chain).

## Governance

Initial governance is a trusted-maintainer list that controls:

- Merges into `hypotheses/` and `experiments/`.
- Scoring weight constants (`w_rigor`, …).
- Runtime image allow-list.
- Oracle registrations.

**Decision:** transition to decentralised governance is a post-mainnet
(post-Phase-3) concern and explicitly out of scope for the autonomous
implementation. The trusted-maintainer model ships to mainnet. A
dedicated post-mainnet spec PR will propose the transition when the
subnet has demonstrated stable operation for an extended period; values
like "≥ N miners, ≥ M weeks" are left for that PR.

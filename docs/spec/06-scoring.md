---
name: scoring
description: composite score rubric, statistical tests, oracle integration
tokens: 1500
load_for: [implementation, review, governance]
depends_on: [02, 18]
---

# 06 — Scoring

## Composite score

For a submission `s` against spec `H` at version `v`:

```
S(s) = w_rigor        * rigor(s)
     + w_reproduction * reproduction(s)
     + w_improvement  * improvement(s, H)
     + w_novelty      * novelty(H)
     - w_cost         * cost_penalty(s)
```

Each component is in `[0, 1]` except `cost_penalty`, which is in `[0, 1]`
and subtracts. Weights sum to 1 excluding the cost penalty, which is
applied additively on top. Initial values:

| component    | weight | source |
|--------------|--------|--------|
| rigor        | 0.20   | spec-quality check |
| reproduction | 0.35   | rerun agreement |
| improvement  | 0.30   | vs declared baseline |
| novelty      | 0.15   | first-to-settle bonus |
| cost penalty | 0.10   | compute + artifact storage |

Weights are reviewable via subnet governance. **Decision:** the
repo-maintainer holds governance authority for Phase 0–2. Any change to
these weights is a spec PR + ADR. Post-mainnet governance transition is
a Phase 3+ concern (see [07](07-incentive.md)).

## Components

### Rigor

A discrete checklist evaluated on the spec at the time of submission:

| check | points |
|-------|-------:|
| At least one baseline declared | 0.10 |
| ≥3 seeds declared | 0.15 |
| Both success and falsification criteria present | 0.15 |
| Statistical test named | 0.10 |
| `dataset_revision` pinned | 0.10 |
| Oracle declared (if one is applicable to the family) | 0.15 |
| `code_ref` exists and contains entrypoint | 0.15 |
| No free-form TBD in front matter | 0.10 |

Rigor is identical for all miners submitting against the same spec version
(it is a property of the spec, not the submission).

### Reproduction

Fraction of sampled rerun seeds whose metrics agree with the
miner-declared metrics within tolerance:

```
reproduction = (# seeds reproduced) / (# seeds sampled)
```

A submission with even one out-of-tolerance seed receives a hard zero on
this component. This is deliberate: partial reproduction rewards noisy or
dishonest miners.

### Improvement

Evaluated from the full miner-declared metric set, one value per declared
success criterion:

```
improvement = min(1.0, observed_effect / target_effect)
```

where `observed_effect` is the change in the candidate metric vs the
baseline, and `target_effect` is the change implied by the success
criterion's `threshold_ratio`. The statistical test in the criterion
(e.g. Welch's t-test across seeds) must pass at `p_max` for the effect to
count; otherwise `improvement = 0`.

If the hypothesis's falsification criterion is met instead, `improvement =
0` but rigor and reproduction are scored normally. A clean falsification
still earns score from the other components; a *honest null* is not a loss.

### Novelty

First miner to settle a hypothesis (pass reproduction + either
`success_criteria` or `falsification_criteria` at the current
version):

```
novelty = 1.0 for the first settling submission
        = 0.5 for the second
        = 0.0 thereafter
```

Novelty decays to zero for reruns of an already-settled hypothesis,
which keeps emission flowing to new questions rather than rehashing
old ones.

#### Ordering (tiebreak for simultaneous settlements)

"First" is resolved deterministically — no ambiguity, no judgement
call:

1. **Primary key:** the block height of the on-chain
   `ResultsAnnouncement` extrinsic that carried the submission.
   Earlier block = earlier settlement.
2. **Secondary key** (same block): the in-block extrinsic index.
3. **Tertiary key** (same block, same extrinsic index — effectively
   impossible on Bittensor but defined for completeness): lex
   ordering of the submitting `miner_hotkey` in its SS58 string
   form.

Two announcements in the same block thus receive novelty `1.0` and
`0.5` respectively under the tertiary rule; a third announcement in
the same block receives `0.0`.

Chain block height cannot be chosen by the miner beyond ±a few
blocks of inclusion latency — this makes the tiebreak
game-resistant. The rule is also independent of which validator
scores first, so validators agree on novelty without coordination.

### Cost penalty

Computed from the manifest's `wallclock_seconds` sum + artifact storage:

```
cost_penalty = min(1.0,
  wallclock_cost_usd / budget_wallclock +
  storage_cost_usd   / budget_storage)
```

Budgets are per-hardware-profile. **Initial values** (USD, revisit after
Phase 2):

| profile | `budget_wallclock` | `budget_storage` |
|---------|-------------------:|-----------------:|
| `cpu-small`        | $0.10 | $0.05 |
| `cpu-large`        | $0.50 | $0.20 |
| `single-gpu-24gb`  | $2.00 | $0.50 |
| `single-gpu-80gb`  | $8.00 | $1.00 |
| `multi-gpu-4x80gb` | $40.00 | $2.00 |

Wallclock cost is priced at a spot-market reference set in
`src/hypotheses/scoring/cost.py` (MANDATORY: a single constant table,
not per-call lookups). Storage is priced per GiB-month.

## Oracles

When a hypothesis declares `oracle.subnet`, the scoring pipeline adds a
hard gate:

```
if oracle.subnet is set:
    oracle_answer = query_oracle(oracle.subnet, oracle.task_ref)
    if abs(declared_answer - oracle_answer) > oracle.tolerance:
        return ScoreVector.zero()
```

The initial supported oracle is **SN42 (omron)**. **Decision:** Phase 1
ships with a stub that raises `NotImplementedError` for any non-null
oracle; the SN42 adapter is implemented before the Phase 2 exit and
documented in an ADR. A hypothesis whose claim cannot be phrased as a
known-answer question on an oracle subnet sets `oracle: null` and
relies on reproduction + improvement alone.

The full oracle adapter contract — interface, classes
(known-answer vs. consensus-answer), registration process,
disagreement handling, outage semantics, and the SN42 adapter
specifics — is in [18 — Oracle contract](18-oracle.md).

## Statistical tests

Supported in v1:

- `welch_t`: Welch's t-test across seeds. For metrics where higher or
  lower is the target direction, the test is one-sided.
- `bootstrap`: nonparametric bootstrap on the difference of medians,
  10k resamples, BCa CIs.
- `mann_whitney`: for non-normal metric distributions.

New tests require a spec update and a corresponding implementation in
`src/hypotheses/scoring/stats/`.

## Per-metric aggregation

When a spec declares multiple `success_criteria`, all must pass for the
improvement component to be non-zero. This is deliberately strict: if a
hypothesis says "faster AND at least as accurate", a win on speed that
regresses accuracy does not count.

## Worked example

Spec `H-0001` declares:

- baselines: `sparse_dense_default`
- success: `flops_to_target_loss` ≤ 0.80 × baseline at `p<0.01`, seeds=5
- falsification: `flops_to_target_loss` ≥ 1.00 × baseline at `p<0.05`
- oracle: null

Miner submits 5 seeds. Validator reruns 2; both within tolerance. Declared
median FLOPs: 0.72× baseline, Welch's t p=0.004.

- rigor = 1.0 (all checks pass)
- reproduction = 1.0 (2/2 reruns within tolerance)
- improvement = min(1.0, 0.28 / 0.20) = 1.0
- novelty = 1.0 (first settling submission at this version)
- cost_penalty = 0.08

Composite: `0.20 + 0.35 + 0.30 + 0.15 − 0.10*0.08 = 0.992`.

## Self-audit

This doc is done when:

- Every formula here is implementable as a pure function (no I/O,
  no LLM) per [05 § two layers](05-validator.md#two-layers-deterministic-core-and-operator-layer).
- The worked example's composite (0.992) recomputes from the
  component numbers without additional context.
- Every statistical test named is listed in the schema's
  `statistical_test` enum.
- The ordering rule for simultaneous settlements is unambiguous in
  every corner (block height, extrinsic index, hotkey lex order).
- Weights cross-reference
  [20-economic-model.md § scoring weight justification](20-economic-model.md#scoring-weight-justification)
  for calibration status.
- Oracle integration links to [18](18-oracle.md) for the full
  contract rather than restating it.

---
name: adversarial simulator
description: contract for the coalition-level attack simulator that must catch every threat in 16
tokens: 2000
load_for: [implementation, review, governance]
depends_on: [16, 12]
---

# 21 — Adversarial simulator

The unit, integration, and property tests in `tests/` cover
individual functions and small interactions. They do not cover
*coalition-level* attacks: a stake-weighted bloc of validators
colluding across cycles, a corrupted oracle paired with a patient
miner, a Sybil cluster gaming novelty.

This document specifies the contract for an adversarial simulator
that does. The simulator is **Phase 2+ implementation**; this
contract is **Phase 0**. Scenarios accumulate in
`tests/golden/adversarial/` ahead of the simulator's existence;
once it ships, every scenario must run nightly.

## Why this exists

[`00.5-foundations.md § E`](00.5-foundations.md#e-empirical-posture--whats-proven-vs-whats-a-bet)
admits that several defences are unverified — the 70/30 settlement
split, the 6-month overturn window, the external-anchor requirement,
the composition rules. Calibration requires either a Phase 2
production retrospective or a working simulator.

The simulator is also the only practical way to discover *new*
threats before adversaries do. Every fixture under
`tests/golden/adversarial/` is a hypothesis that the design defends
against the named coalition; failing fixtures surface real holes
before mainnet.

## Coverage requirement

> **HM-REQ-0090** Every threat in
> [`16-threat-model.md`](16-threat-model.md) MUST have at least
> one fixture under `tests/golden/adversarial/` declaring an
> expected outcome by the end of Phase 2. The simulator runs
> nightly against each fixture; failures block release per
> [`15-ci-cd.md`](15-ci-cd.md). Each `F1`–`F6` foundation threat
> in [`00.5-foundations.md`](00.5-foundations.md) MUST have at
> least one scenario before then.

The Phase 2 task graph (drafted when Phase 1 closes) includes a
task `T-P2-NNN` that wires the simulator into `mutation.yml`'s
nightly slot. Until Phase 2, the directory grows but no CI gate
enforces it; foundation-review cadence (00.5 § review cadence)
catches missing coverage at the 6-month checkpoint.

## Scenario fixture format

Each scenario is a JSON file under `tests/golden/adversarial/`,
named `<threat-id>-<short-slug>.json` (e.g.
`F1-stake-collusion.json`, `T-021-rate-limit-spam.json`).

```json
{
  "name": "<filename without .json>",
  "threat": "F1 | F2 | ... | T-NNN",
  "source": "<spec section that motivates the scenario>",
  "actors": {
    "validators": [
      { "hotkey": "V-1", "stake_share": 0.45, "behaviour": "colluding" },
      { "hotkey": "V-2", "stake_share": 0.45, "behaviour": "colluding" },
      { "hotkey": "V-3", "stake_share": 0.10, "behaviour": "honest" }
    ],
    "miners": [
      { "hotkey": "M-1", "behaviour": "honest", "submission": "..." },
      { "hotkey": "M-2", "behaviour": "fabricated_seeds" }
    ]
  },
  "inputs": {
    "hypothesis": "H-0001 v1",
    "oracle_responses": "...",
    "rerun_seed": "..."
  },
  "expected_outcome": {
    "settlements": [
      { "miner": "M-1", "status": "settled-supported", "novelty": 1.0 }
    ],
    "rejections": [
      { "miner": "M-2", "reason": "FabricatedSeeds" }
    ],
    "validator_penalties": [
      { "hotkey": "V-1", "yuma_outlier_distance": 0.0,
        "comment": "collusion succeeds because both colluders agree" }
    ],
    "cost_of_attack_usd": 4200,
    "cost_of_attack_under_budget": true
  },
  "tolerance": {
    "novelty": 1e-9,
    "cost_of_attack_usd": 100
  },
  "notes": "free-form for humans"
}
```

### Field semantics

- `threat` — must be a `T-NNN` row from doc 16 OR an `F1`–`F6`
  foundation threat. Validated mechanically by
  `check_spec_consistency.py` once it knows about
  `tests/golden/adversarial/`.
- `actors.validators[].stake_share` — fraction of total subnet
  stake; sums to 1.0 across the validator set. Behaviour profiles:
  `honest`, `lazy`, `colluding`, `weight_copying`, `selective_reveal`.
- `actors.miners[].behaviour` — `honest`, `fabricated_seeds`,
  `cherry_picked`, `replay`, `forged_signature`, `oracle_collusion`,
  `sybil_cluster`. Each maps to a specific T-NNN row.
- `expected_outcome.settlements[]` — what the deterministic core
  must conclude per submission, *given* the colluding behaviour.
  For threats the design *defends* against, the settlements list
  the honest outcome; the colluders should be rejected. For threats
  the design only *partially* mitigates, the expected outcome
  documents the residual harm — this is the contract for
  "acceptable damage."
- `cost_of_attack_under_budget` — boolean; true means the design
  prices the attack out of feasibility under modelled cloud
  costs. False is acceptable for partial mitigations and triggers
  a follow-up ADR explaining why the residual cost gap is okay.

## Pass criteria

Each scenario passes when ALL of:

1. The deterministic-core output matches `expected_outcome.settlements`
   byte-equal (per HM-REQ-0010 determinism).
2. Each `expected_outcome.rejections[]` fires with exactly the
   declared reason; no spurious additional rejections.
3. T-OVR overturn events fire iff the scenario expects them — no
   false positives, no false negatives.
4. `cost_of_attack_usd` is within `tolerance.cost_of_attack_usd`
   of the modelled value.
5. No scenario hangs the simulator past a per-scenario wallclock
   cap (default 60s; declarable per fixture for slow scenarios).

## Implementation hooks (Phase 2+)

Phase 2 task graph (separate file, not yet drafted) adds:

- `T-P2-NNN simulator/core.py` — runs a fixture, reports pass/fail.
- `T-P2-NNN simulator/actors.py` — implements each behaviour
  profile. Honest is the trivial case; the others are fakes.
- `T-P2-NNN simulator/cost_model.py` — converts wallclock + storage
  into USD using the per-profile budgets in
  [`06-scoring.md § cost penalty`](06-scoring.md#cost-penalty).
- `T-P2-NNN .github/workflows/adversarial.yml` — nightly job that
  runs every fixture and posts a SARIF report on failure.

Until then, the fixtures stand as documentation. Reviewers can
manually trace each fixture against the spec and confirm the
expected outcome is what the spec predicts.

## What the simulator is NOT

- **Not a fuzzer.** Fixtures are hand-written, named, and
  reviewed. Random-input fuzzing of the protocol layer is a
  Phase 3 idea and lives elsewhere.
- **Not a substitute for property tests.** `HM-INV-NNNN`
  invariants are still enforced via Hypothesis-library property
  tests under `tests/properties/`. The simulator covers the
  multi-actor attack space those tests can't reach.
- **Not a replacement for mainnet observation.** Phase 3 retro
  metrics (actual settlement rates, observed validator
  divergence, real cost-of-attack data) still ground the
  parameters. The simulator is faster and earlier; the retro is
  slower and ground-truth.

## Cross-references

- [`00.5-foundations.md`](00.5-foundations.md) § A and § E — every
  F1–F6 threat will list its fixture(s) once written.
- [`16-threat-model.md`](16-threat-model.md) — every T-NNN row will
  list its fixture(s) once written.
- [`12-implementation-constraints.md § testing strategy`](12-implementation-constraints.md#testing-strategy)
  — the simulator is a fourth tier alongside unit, integration,
  property tests.
- [`tests/golden/adversarial/`](../../tests/golden/adversarial/) —
  the fixtures themselves.

## Self-audit

This doc is done when:

- HM-REQ-0090 is in [`requirements.md`](requirements.md) and
  cross-referenced from [`16-threat-model.md`](16-threat-model.md).
- The fixture format above is precise enough that an
  implementing agent can write `simulator/core.py` from this doc
  alone.
- At least one seed fixture exists under
  [`tests/golden/adversarial/`](../../tests/golden/adversarial/)
  demonstrating the format with one `F1`–`F6` threat covered.
- Phase 2 task graph (when drafted) references this doc for the
  simulator implementation tasks.
- The simulator's "what is NOT" section makes clear it does not
  replace property tests, fuzzing, or retro observation.

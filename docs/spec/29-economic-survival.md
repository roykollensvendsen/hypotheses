---
name: economic survival
description: scope doc for the quantitative survival-analysis work stream; first sub-section pins miner unit economics
tokens: 2400
load_for: [governance, review]
depends_on: ["00.5", "06", "11", "20", "27"]
kind: contract
evidence: reasoned-design
---

# 29 — Economic survival

[`27-economic-strategy.md`](27-economic-strategy.md) names *what*
the four non-Bittensor revenue paths are and *why* they
plausibly work. [`20-economic-model.md`](20-economic-model.md)
catalogues *which knobs* the subnet controls. Neither answers
whether the numbers actually work — whether the honest
[miner](04-miner.md) population breaks even, whether
[validator](05-validator.md) reruns pay for themselves, whether
the steady-state participation level is reachable.

This doc opens that work stream within the
[spec](README.md). It is `kind: contract,
evidence: reasoned-design`: the variables, units, and modelling
discipline are pinned now so the four follow-up PRs (E.2–E.5)
slot in cleanly. The first quantitative section — miner unit
economics — lands here. The rest follow as separate PRs each
≤ 500 LoC.

## A. Scope

**This doc covers.** The modelling contract (variables, units,
calibrated-vs-assumed taxonomy), the sub-PR roadmap, and the
**miner unit economics** sub-section in full.

**Out of scope.** Validator unit economics (PR-E.2),
Nash-equilibrium analysis (PR-E.3), sensitivity tables across
TAO price and emission rate (PR-E.4), calibration-from-Phase-2-
data ratchet (PR-E.5). Each is a follow-up PR; landing them
together would blow the 500-LoC cap and mix concerns.

[`00.5 § C c4a-emission-sufficient-steady-state`](00.5-foundations.md#c4a-emission-sufficient-steady-state)
is the load-bearing assumption this doc starts to pressure-test.
A breach surfaces as a failed break-even bound below.

## B. Modelling contract

### Variables and units

| symbol | unit | meaning | source |
|--------|------|---------|--------|
| `E_epoch` | TAO/epoch | total subnet emission per Bittensor epoch (~72 minutes) | Bittensor root, external |
| `f_miner` | unitless | miner share of subnet emission | [`20 § The 82/18 split`](20-economic-model.md#the-8218-split), default 0.82 |
| `f_validator` | unitless | validator share | default 0.18 |
| `t_TAO` | USD/TAO | TAO spot price | external; modelled, not predicted (see [`20 § Out of scope`](20-economic-model.md#out-of-scope)) |
| `s_miner` | unitless | this miner's fraction of network composite | [`06 § Composite score`](06-scoring.md#composite-score) |
| `N_miners` | count | active miners on subnet | observable |
| `submissions_per_epoch` | count | network-wide submissions per epoch | observable |
| `c_compute` | USD/submission | hardware cost from [`06 § Cost penalty`](06-scoring.md#cost-penalty) per profile | calibrated table |
| `c_storage` | USD/submission | [artifact](01-glossary.md#artifact) storage cost | calibrated table |
| `c_overhead` | USD/submission | operator time, network, hotkey rotation | **assumed**, default $0.05/submission |

### Calibrated vs assumed

- **Calibrated** (numbers from a published or measurable
  source): `f_miner`, `f_validator`, `c_compute`, `c_storage`.
  These already live in
  [`20 § Parameter inventory`](20-economic-model.md#parameter-inventory).
- **Observable** (numbers from chain or ops data):
  `E_epoch`, `s_miner`, `N_miners`,
  `submissions_per_epoch`, `t_TAO`.
- **Assumed** (numbers we pin until Phase 2 produces data):
  `c_overhead`. Follow-up PRs add more variables as needed;
  each new assumed variable lands a row in
  [`00.5 § C`](00.5-foundations.md#c-assumptions-the-defences-require).

### Epoch baseline

For uniform reasoning across this doc and the follow-ups:

- One Bittensor epoch ≈ 72 minutes (360 blocks × 12 s) per the
  rate-limit calculation in
  [`05 § Pipeline`](05-validator.md#pipeline) step 1.
- Epochs per day ≈ 20.
- Total miner emission per epoch:
  `E_miner = E_epoch · f_miner` (TAO).

### Why this modelling discipline

The post-strategy-doc gap-review surfaced quantitative survival
analysis as the largest deferred work stream. The strategy doc
(27) and operational doc (20) both list "calibration"
open-questions; until a modelling contract exists, each
follow-up would invent its own variables and units. Pinning the
contract now makes the follow-ups composable.

## C. Miner unit economics

### Per-submission honest revenue

For a miner submitting `k` submissions per epoch, honest play
gives an expected revenue per submission:

```text
R_sub_TAO    = (E_miner · s_miner) / k
             = (E_epoch · f_miner · s_miner) / k

R_sub_USD    = R_sub_TAO · t_TAO
```

Where `s_miner` is this miner's share of network composite
score. In a healthy steady state with `N_miners` miners of
near-uniform skill (treated as identical for the median-case
calculation; PR-E.3 introduces a skill distribution),
`s_miner ≈ 1 / N_miners`. The honest-play
arithmetic in
[`20 § Honest-play arithmetic`](20-economic-model.md#honest-play-arithmetic)
already gives `composite ≈ 0.91` for a typical good submission,
so `s_miner ≈ 0.91 / Σ_composite`.

### Per-submission cost

```text
C_sub = c_compute + c_storage + c_overhead
```

`c_compute` and `c_storage` are read off the per-profile table
in
[`06 § Cost penalty`](06-scoring.md#cost-penalty);
`c_overhead = $0.05` is the assumed default.

### Honest break-even

A miner is profitable per submission when `R_sub_USD ≥ C_sub`:

```text
(E_epoch · f_miner · s_miner) / k · t_TAO  ≥  C_sub
```

Solving for the break-even network size at `s_miner = 1/N_miners`:

```text
N_miners ≤ (E_epoch · f_miner · t_TAO) / (k · C_sub)        (*)
```

Higher `k` → smaller break-even `N_miners`; TAO price rises →
larger break-even `N_miners`; heavier profile (larger `C_sub`)
→ smaller break-even `N_miners`.

### Worked example (Q2 2026 reference)

Pinning illustrative numbers:

- `E_epoch` = 1 TAO/epoch (Bittensor root allocation, conservative
  Phase 2 estimate; revisit at registration)
- `f_miner` = 0.82
- `t_TAO` = $300/TAO (spot reference; same caveat as the
  cost-table USD values per
  [`20 § Cost penalty calibration`](20-economic-model.md#cost-penalty-calibration))
- `k` = 3 submissions/epoch (the rate-limit ceiling per
  [`05 § Pipeline`](05-validator.md#pipeline) step 1)

Break-even `N_miners` per profile (from `(*)`):

| profile | `c_compute` | `c_storage` | `C_sub` | `N_miners` break-even |
|---------|------------:|------------:|--------:|----------------------:|
| `cpu-small` | $0.10 | $0.05 | $0.20 | ≈ 410 |
| `cpu-large` | $0.50 | $0.20 | $0.75 | ≈ 109 |
| `single-gpu-24gb` | $2.00 | $0.50 | $2.55 | ≈ 32 |
| `single-gpu-80gb` | $8.00 | $1.00 | $9.05 | ≈ 9 |
| `multi-gpu-4x80gb` | $40.00 | $2.00 | $42.05 | ≈ 2 |

Read: at the reference numbers, `cpu-small` profiles support
hundreds of miners profitably; `multi-gpu-4x80gb` profiles
collapse to ≤ 2 miners — economically, those hypotheses behave
like a duopoly.

### Implications

- **Heavy-GPU hypotheses are de-facto narrow markets.** A spec
  declaring `multi-gpu-4x80gb` will never have a wide healthy
  miner population at these emission and price levels. The spec
  can still ship (the [`27 § C.1`](27-economic-strategy.md#c1-sponsored-hypotheses)
  sponsorship path subsidises the gap), but the operator
  shouldn't expect organic emission to cover it.
- **Phase 2 cold-start (per
  [`11 § Phase 2.0`](11-roadmap.md#phase-20-cold-start)) and
  c4b** are particularly tight on heavy profiles: with `≥ 5`
  miners as a Phase 2.0 exit criterion, only `cpu-small` and
  `cpu-large` are above break-even at the reference numbers.
- **TAO price drops** halve the break-even `N_miners`. At
  $150/TAO `cpu-small` falls to `N ≈ 205`; at $50/TAO it
  collapses to `N ≈ 68`. Below $20/TAO, even `cpu-small`
  hypotheses are unprofitable for `N > 30` miners.
- **The
  [`20 § Sybil cost for novelty gaming`](20-economic-model.md#sybil-cost-for-novelty-gaming)
  arithmetic that asserts honest play wins** assumes the
  miner is *above* break-even on at least one path. At
  reference numbers this holds for `cpu-small` and `cpu-large`
  with comfortable margin; for heavy GPUs the margin is too
  narrow to defend the claim. The honest-play arithmetic in 20
  inherits a c4b caveat: it depends on either
  steady-state pricing or the cold-start contingency in
  [`27 § D — Phase 2.0`](27-economic-strategy.md#d-phase-by-phase-trajectory).

## D. Sub-PR roadmap

The four follow-up PRs build on this one:

### PR-E.2 — Validator unit economics

Per-submission rerun cost (`rerun_fraction · c_compute_per_seed`),
validator dividend share (`f_validator / N_validators`),
break-even validator-set size factoring in
`min_validators_d22_coverage = 6` (see
[HM-INV-0030](05-validator.md#coverage-under-thin-validator-sets)).
Lands as § D.1 of this doc plus an ADR.

### PR-E.3 — Equilibrium / Nash analysis

Whether the participation point where miners and validators
both break even is stable. Identifies regimes where
participation collapses or runs away. Probably uses the
two-population replicator dynamics frame plus a fixed-point
existence proof. Lands as § D.2 plus ADR.

### PR-E.4 — Sensitivity tables

Combined miner + validator break-even surfaces over
`(t_TAO, E_epoch, f_miner)`, identifying the regimes where the
mechanism is robust vs fragile. Lands as § D.3 plus ADR.

### PR-E.5 — Calibration ratchet

Phase 2 produces real `s_miner`, `submissions_per_epoch`, and
`c_overhead` data. PR-E.5 establishes the cadence (quarterly
re-fit), the trigger condition (any reference number outside
the model's predicted range by ≥ 50 % opens a recalibration ADR),
and the link to the operating-cost catalogue in
[`28 § C`](28-treasury.md#c-operating-cost-catalogue).

## E. Viability criteria

The decision protocol that says "this subnet's economics work"
or "they don't." Four numerical pass/fail thresholds. Viable
means **all four** hold simultaneously across the reference
parameter ranges.

| # | criterion | threshold | source / measured by |
|---|-----------|-----------|----------------------|
| 1 | Miner median break-even | `s_miner = 1/N_miners` is profitable for ≥ 80 % of supported [hypothesis](02-hypothesis-format.md) profiles at reference `t_TAO`, `E_epoch`, `k` | § C miner economics formula `(*)` |
| 2 | Validator break-even | `f_validator · E_epoch · t_TAO / N_validators ≥ rerun_cost(N_validators) + c_overhead_validator` at `N ≥ 6` (the [HM-INV-0030](05-validator.md#coverage-under-thin-validator-sets) floor) | § D.1 (PR-E.2) |
| 3 | Stable participation equilibrium | At least one fixed point where `dN_miner/dt = dN_validator/dt = 0` exists and is locally attracting from the [Phase 2.0 cold-start position](11-roadmap.md#phase-20-cold-start) | § D.2 (PR-E.3) |
| 4 | Robustness | Criteria 1–3 hold under `t_TAO ∈ [0.5, 2.0] · reference` and `E_epoch ∈ [0.5, 2.0] · reference` | § D.3 (PR-E.4) |

### What "viable" does NOT mean

- **Not a guarantee under adversarial conditions.** The four
  criteria assume honest play. F1–F6 adversarial scenarios are
  covered by [`16-threat-model.md`](16-threat-model.md) and
  [`21-adversarial-simulator.md`](21-adversarial-simulator.md);
  adversarial viability is a separate question.
- **Not robust to single-shot black-swan TAO crashes.** A
  100× sudden price drop breaks every emission-funded subnet;
  the criteria don't claim immunity.
- **Not robust to specific miner-skill heterogeneity.** Beyond
  the median-case `s_miner ≈ 1/N_miners`, individual miners
  with above- or below-median skill are not separately
  modelled here. PR-E.3 introduces a skill distribution under
  criterion 3.

### Why 80 %, not 100 %, of profiles

§ C already shows `multi-gpu-4x80gb` is a duopoly (`N ≈ 2`) at
reference numbers — known and documented as a narrow market.
Demanding viability across **every** profile would force a
spurious "not viable" verdict on a finding the spec already
acknowledges. The 80 % threshold lets `cpu-small`,
`cpu-large`, `single-gpu-24gb`, `single-gpu-80gb` carry the
viability claim while heavy-GPU profiles remain
sponsorship-dependent per
[`27 § C.1`](27-economic-strategy.md#c1-sponsored-hypotheses).

### Decision protocol

After PR-E.2 through PR-E.5 + the simulation infrastructure in
[ADR 0021](../adr/0021-economic-survival-simulator.md) land,
the maintainer publishes a **viability ADR** that:

1. Reports each criterion's measured value.
2. Returns one of three verdicts:
   - **Viable** — all four pass; proceed to Phase 2 testnet
     onset without further pivot.
   - **Marginal** — one or two fail by < 30 %; enact a tier-1
     pivot (rerun_fraction adjustment, emission-split tweak,
     or cost-table refresh per
     [`20 § Parameter inventory`](20-economic-model.md#parameter-inventory))
     and re-evaluate.
   - **Not viable as designed** — multiple fail or any fail
     by ≥ 30 %; enact a tier-2 / tier-3 pivot (hypothesis-
     acceptance gate tightening, treasury thin-network
     subsidy per
     [`28 § E`](28-treasury.md#e-outflow-rules), strategic
     re-pivot, or subnet redefinition).
3. The ADR is the canonical "go / no-go" for Phase 2.

The decision is not purely numerical — the maintainer weighs
Phase 2 onboarding cost against verification confidence — but
the criteria provide a defensible base case. ADR
[0016](../adr/0016-viability-decision-protocol.md) captures
the rationale for these specific thresholds and the verdict
taxonomy.

### Pivot ladder reference

The maintainer's response to a "marginal" or "not viable"
verdict follows the pivot ladder in ADR 0016 — seven levers
ranked by reversibility / disruption. Tier-1 levers are
parameter adjustments (no new spec docs); tier-2 introduces
new mechanisms (hypothesis-acceptance gates, treasury
subsidy); tier-3 is redesign-class (strategy rewrite or
foundation review). Each lever lands as its own ≤ 500-LoC PR
when the verdict mandates it.

## F. Open questions

1. **`E_epoch` real value.** Today this is a placeholder; at
   netuid registration the Bittensor root allocation gives the
   real number. ADR at registration locks the
   [baseline](01-glossary.md#baseline).
2. **`c_overhead` calibration.** The $0.05 default is plausible
   but not measured. PR-E.5 establishes the calibration
   pipeline; the first measurement lands in the Phase 2 exit
   ADR.
3. **Multi-profile portfolios.** A miner running multiple
   hardware profiles is not modelled here; PR-E.3 addresses it
   under the equilibrium analysis.
4. **Miner-skill heterogeneity.** The `s_miner ≈ 1/N_miners`
   simplification assumes uniform skill. Real miners differ;
   PR-E.3 introduces a skill distribution. Until then the
   numbers in `(*)` are the median, not every miner.

## G. References

- [`00.5-foundations.md § C c4a / c4b`](00.5-foundations.md#c4a-emission-sufficient-steady-state),
  [§ D](00.5-foundations.md#d-what-we-explicitly-give-up).
- [`06 § Cost penalty`](06-scoring.md#cost-penalty),
  [§ Composite score](06-scoring.md#composite-score).
- [`11 § Phase 2.0`](11-roadmap.md#phase-20-cold-start).
- [`20 § The 82/18 split`](20-economic-model.md#the-8218-split),
  [§ Parameter inventory](20-economic-model.md#parameter-inventory),
  [§ Honest-play arithmetic](20-economic-model.md#honest-play-arithmetic),
  [§ Out of scope](20-economic-model.md#out-of-scope).
- [`27 § C, D`](27-economic-strategy.md#c-non-bittensor-revenue-paths).
- [`28 § C`](28-treasury.md#c-operating-cost-catalogue),
  [§ E](28-treasury.md#e-outflow-rules).
- ADRs: [0010](../adr/0010-economic-strategy.md),
  [0011](../adr/0011-d22-coverage-bound.md),
  [0013](../adr/0013-cold-start-contingency.md),
  [0014](../adr/0014-treasury-pre-dao.md),
  [0015](../adr/0015-economic-survival-scope.md),
  [0016](../adr/0016-viability-decision-protocol.md).

## Self-audit

Done when:

- The variables-and-units table in § B names every symbol used
  in § C, with a unit and a calibrated/observable/assumed tag.
- The break-even formula `(*)` resolves to the
  [c4a-emission-sufficient-steady-state](00.5-foundations.md#c4a-emission-sufficient-steady-state)
  / [c4b](00.5-foundations.md#c4b-emission-sufficient-cold-start)
  assumptions explicitly.
- Each of the four follow-up PRs (E.2–E.5) has a named scope
  and the section it will populate.
- § E names four numerical viability criteria, each
  cross-referenced to the section / PR that measures it, plus
  a three-verdict decision protocol citing ADR 0016.
- Reference numbers carry the same Q2 2026 caveat as the
  cost-table USD values in `20 § Cost penalty calibration`.
- Cross-refs resolve under
  `scripts/check_spec_consistency.py` and
  `scripts/check_grounding.py`.

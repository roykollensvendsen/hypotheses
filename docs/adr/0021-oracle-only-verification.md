---
name: 0021 oracle-only verification
description: introduce a verification mode that skips validator rerun for oracle-verifiable hypotheses, lifting the asymmetric break-even ceiling for that class
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0021 — Oracle-only verification mode

## Context

ADR 0019 returned the verdict "not viable as designed at
reference numbers." ADR 0020 installed a tier-2 pivot —
sponsor-gated heavy profiles — that restored viability for
GPU workloads by routing them through paid bounties.

The pivot leaves an open question: *do we have a viability
path that depends on neither emission economics alone (which
fails for non-trivial workload mixes) nor sponsor inflows
(which depend on c8-sponsorship-demand)?* If c8 fails to
materialise at Phase 2, the safe-tier emission economics
collapse at scale; the subnet is then constrained to
N_miners ≤ 50 on `cpu-small` workloads (per
[`29 § D.1`](../spec/29-economic-survival.md#d1-validator-unit-economics)).

A third escape hatch exists in the spec scaffolding but is
not yet declared. Hypotheses with externally-observable
ground truth — prediction markets, sports outcomes, sensor
measurements, public benchmarks — do not require validator
rerun. The oracle is the trust primitive; reproducing seeds
adds nothing because the oracle's verdict IS the canonical
answer.

This ADR introduces that escape hatch as a new verification
mode.

## Decision

Add a new optional field `verification` to the hypothesis
schema in
[`02 § verification`](../spec/02-hypothesis-format.md#verification)
with two values:

- **`full-rerun`** *(default)* — unchanged behaviour.
- **`oracle-only`** — validator skips reruns, scores
  reproduction from a single oracle query.

Add **HM-REQ-0130** to
[`02 § Schema validation`](../spec/02-hypothesis-format.md#schema-validation):

> A hypothesis declaring `verification: oracle-only` MUST
> declare an `oracle` block (or
> `external_anchor.type=oracle`).

Pipeline branch in
[`05 § Oracle-only branch`](../spec/05-validator.md#oracle-only-branch):
oracle-only submissions skip steps 4–6 (rerun sample / rerun
/ reconcile) and route directly through step 8 (oracle check)
into scoring. The reproduction component for oracle-only
hypotheses is binary (1.0 / 0.0 / pending) per
[`06 § Reproduction`](../spec/06-scoring.md#reproduction).

### Why this restores viability for a third class

Validator cost for oracle-only hypotheses is bounded by oracle-
query overhead alone (~ $0.001 / query), independent of
`c_compute` and `rerun_fraction`. The asymmetric break-even
shape from ADR 0017 — where validator cost scales with
`N_miners · rerun_fraction · c_compute` — does not apply.

At reference numbers, oracle-only validator break-even
exceeds the [HM-INV-0030](../spec/05-validator.md#coverage-under-thin-validator-sets)
floor of 6 across every plausible `N_miners`:

| `N_miners` | oracle-only break-even `N_validators` |
|-----------:|--------------------------------------:|
| 50 | ≈ 216 |
| 500 | ≈ 36 |
| 1000 | ≈ 17 |

The viability protocol's criterion 2 passes outright for this
class; criterion 3 (equilibrium attractor) lands well above
the D2.2 floor. The class is genuinely emission-funded with
no sponsorship dependency.

### Trade-off

**Lost.** The validator's independent compute on the artifact
is gone for oracle-only submissions. This means cherry-picking
defences that derive from full-rerun (D2.2 reproduction-by-
sampling) do not protect this class — but they don't need to,
because the oracle's verdict makes seed-level dishonesty
irrelevant. A miner can run zero seeds and submit a guess; if
the oracle agrees, they earn full reproduction; if not, zero.

**F3 oracle-corruption risk** is the binding constraint. A
single-oracle declaration carries the F3 risk per
[`00.5 § F3`](../spec/00.5-foundations.md#f3--oracle-corruption);
[HM-REQ-0080](../spec/18-oracle.md#composition) requires
composition for `oracle.oracles` length ≥ 2 hypotheses, and
this requirement applies unchanged to oracle-only mode.

**When to use.** Hypotheses where the truth is externally
observable and the oracle is canonical — prediction markets,
sports outcomes, sensor measurements, content-hashed public
benchmarks. **When NOT to use.** Hypotheses about
computational properties of an artifact (training-run
efficiency, pruning ratio, loss-trajectory shape) — those
need full rerun because the artifact's behaviour is the claim.

## Consequences

- **Positive.** A third viability path opens that depends on
  neither emission scaling well at heavy profiles nor sponsor
  willingness-to-pay. For oracle-verifiable hypotheses (a
  large fraction of plausible Phase 2 submissions:
  prediction markets, public benchmarks, oracle-anchored
  scientific predictions), the design is now structurally
  viable at any scale. Combined with safe-tier emission
  economics + sponsor-gated heavy profiles, the
  Phase 2 design has three independent viability paths.
- **Negative.** Adds a verification dimension to the
  hypothesis schema. Reviewers and authors must now reason
  about which mode applies. Mitigation: `full-rerun` is the
  default; oracle-only is opt-in and constrained by
  HM-REQ-0130 to hypotheses with declared oracles. The
  template in
  [`hypotheses/HYPOTHESIS_TEMPLATE.md`](../../hypotheses/HYPOTHESIS_TEMPLATE.md)
  carries `full-rerun` as the implicit default; oracle-only
  authors set it explicitly.
- **Negative.** Concentrates F3 risk for that class. The
  spec already names F3 as a load-bearing threat with two
  documented Polymarket exploits ({ref:polymarket-uma-ukraine-2025},
  {ref:polymarket-paris-weather-2026}). Oracle-only
  hypotheses are F3-exposed by design; HM-REQ-0080
  composition is the structural defence and should be the
  *recommended* form for high-stakes oracle-only
  hypotheses.
- **Neutral / deferred.** The rigor component is unchanged
  (rigor is a property of the spec, not the submission, per
  [`06 § Rigor`](../spec/06-scoring.md#rigor)). Improvement
  is computed from declared metrics as today; the oracle's
  binary verdict does not replace it. Novelty tiebreak rules
  are unchanged. The reproduction-by-sampling primitive
  (D2.2) continues to apply to full-rerun hypotheses.

## Options considered

- **Per-rerun validator fee.** Pay validators per-work-unit
  on top of stake-bonded dividends. Restructures the dividend
  mechanism; restores symmetric break-even. Rejected for now:
  significant change to the emission flow, requires Bittensor-
  level support that doesn't exist as a primitive. Could
  ship as a follow-up if oracle-only proves insufficient.
- **Sample-deduplication across validators.** Validators
  coordinate which seeds each runs to avoid redundant work.
  Rejected: breaks D1.2 (deterministic pure-function scoring)
  by introducing inter-validator coordination, which is the
  collusion vector D1.1 is designed to foreclose.
- **Reduce `rerun_fraction` at scale.** At high `N_validators`
  a lower fraction maintains coverage per HM-INV-0030. The
  parameter inventory already supports this; the viability
  ceiling shifts somewhat but not enough to fix
  heavy-profile fail. Rejected as primary fix; remains
  available as a tier-1 lever from ADR 0016.
- **Tiered emission via submission age.** Older submissions
  get less validator work. Rejected: complicates the lifecycle
  state machine in [`17`](../spec/17-hypothesis-lifecycle.md);
  doesn't help fresh heavy-profile hypotheses which is the
  binding case.
- **Defer to Phase 2 data.** Rejected: the structural
  argument is independent of empirical c8 — the oracle-only
  class works on the existing oracle infrastructure
  immediately and doesn't depend on sponsor uptake.

## Related

- Spec: [`02 § verification`](../spec/02-hypothesis-format.md#verification);
  [`02 § Schema validation`](../spec/02-hypothesis-format.md#schema-validation)
  (HM-REQ-0130);
  [`05 § Oracle-only branch`](../spec/05-validator.md#oracle-only-branch);
  [`06 § Reproduction`](../spec/06-scoring.md#reproduction);
  [`29 § D.1 Oracle-only economics`](../spec/29-economic-survival.md#oracle-only-economics);
  [`requirements.md`](../spec/requirements.md),
  [`traceability.md`](../spec/traceability.md) (HM-REQ-0130);
  [`23 § Mine`](../spec/23-system-tests.md) — new S-MINE-14
  scenario.
- Spec (unchanged but relevant): [`18 § Composition`](../spec/18-oracle.md#composition)
  (HM-REQ-0080) — oracle composition still applies;
  [`00.5 § F3`](../spec/00.5-foundations.md#f3--oracle-corruption)
  — oracle-corruption threat oracle-only hypotheses are
  exposed to.
- ADRs: [0017](0017-validator-unit-economics.md) — the
  asymmetric ceiling this ADR sidesteps;
  [0019](0019-viability-verdict-not-viable-as-designed.md) —
  the verdict that motivated this third path;
  [0020](0020-sponsor-gated-heavy-profiles.md) — the
  complementary tier-2 pivot for full-rerun heavy profiles.

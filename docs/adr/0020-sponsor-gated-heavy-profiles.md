---
name: 0020 sponsor-gated heavy profiles
description: tier-2 pivot per ADR 0019 — classify hypothesis profiles into safe and gated tiers; gated profiles require a sponsorship block to be accepted
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0020 — Sponsor-gated heavy profiles (lever 4 + lever 5 combined)

## Context

[ADR 0019](0019-viability-verdict-not-viable-as-designed.md)
returned the verdict "not viable as designed at reference
numbers" and recommended a tier-2 pivot combining ADR 0016's
lever 4 (hypothesis-acceptance gate) and lever 5 (treasury /
sponsor inflow) into a single mechanism: gated heavy profiles
that require sponsor-funded bounties to be accepted.

This ADR ships that pivot. The implementation reuses
mechanisms the spec already had scaffolding for:

- [`27 § C.1`](../spec/27-economic-strategy.md#c1-sponsored-hypotheses)
  — the sponsorship path was previously framed as an
  *additional* revenue path; now it becomes load-bearing for
  one tier of hypotheses.
- [`28 § E`](../spec/28-treasury.md#e-outflow-rules) —
  treasury outflow rules absorb the bounty residual.
- [`02 § Optional fields`](../spec/02-hypothesis-format.md#optional-fields)
  — the schema's existing pattern for optional declarations
  extends to a `sponsorship` block.

## Decision

### Profile tiers (new)

Add a profile-tier classification to
[`06 § Profile tiers`](../spec/06-scoring.md#profile-tiers):

| profile | tier |
|---------|------|
| `cpu-small` | safe |
| `cpu-large` | safe |
| `single-gpu-24gb` | gated |
| `single-gpu-80gb` | gated |
| `multi-gpu-4x80gb` | gated |

Safe-tier profiles have validator break-even on emission
alone at moderate `N_miners`. Gated-tier profiles do not, per
[ADR 0017](0017-validator-unit-economics.md).

### `sponsorship` block (new optional field)

Add a `sponsorship` optional field to the hypothesis schema
in [`02 § sponsorship`](../spec/02-hypothesis-format.md#sponsorship):

```yaml
sponsorship:
  sponsor_id: "researchhub:0xABC..."
  bounty_tao: 5.0
  split:
    miner: 0.60
    validators: 0.30
    treasury: 0.10
  escrow_block: 1234567
```

The default split `(0.60, 0.30, 0.10)` matches the
placeholder in
[`27 § G open question 2`](../spec/27-economic-strategy.md#g-open-questions);
declaring it explicitly per-hypothesis allows per-sponsor
variation while keeping the audit trail visible.

### HM-REQ-0120 (the gate, normative)

> **HM-REQ-0120** A hypothesis whose `hardware_profile` is in
> the gated tier MUST declare a `sponsorship` block; otherwise
> it is rejected at acceptance.

Lands inline at
[`02 § Schema validation`](../spec/02-hypothesis-format.md#schema-validation)
and indexed in
[`requirements.md`](../spec/requirements.md) +
[`traceability.md`](../spec/traceability.md).

### How this restores viability

For safe-tier hypotheses: emission-side economics work at
moderate `N_miners` per § C of doc 29. The mechanism continues
unchanged.

For gated-tier hypotheses: the validator share of the
sponsorship bounty (placeholder 30 %) supplements the
per-cycle dividend. Validator break-even formula `(**)` from
[`29 § D.1`](../spec/29-economic-survival.md#d1-validator-unit-economics)
gains a sponsor-residual term:

```text
R_val_USD_with_sponsor = R_val_USD + sponsor_residual
sponsor_residual       = bounty_tao · split.validators · t_TAO
                         / N_validators
                         / N_settled_per_epoch
```

A sponsor offering `bounty_tao = 5` per gated hypothesis with
the default split puts ~ $1500 / `N_validators` /
`N_settled_per_epoch` extra at validators per gated hypothesis
settlement — comfortably more than enough to cover the rerun
shortfall at typical scales.

### Foundation update

c4a-emission-sufficient-steady-state is annotated as
*conditional on c8-sponsorship-demand*: the gate enforces the
bound mechanically, but the bound only holds if sponsors
actually deliver bounties. The strategy doc's c8 admonition
expands accordingly.

## Consequences

- **Positive.** The criterion-2/3 fail surfaced by ADR 0019
  is closed for safe-tier workloads and rerouted to the
  sponsorship path for gated-tier workloads. Phase 2 onset
  is unblocked. The pivot uses spec scaffolding that already
  existed (sponsorship in 27, treasury in 28); no new
  cross-cutting mechanism is invented.
- **Positive.** The mechanism is reversible. If Phase 2 data
  shows safe-tier alone is sufficient, gated-tier acceptance
  can be re-opened by retiring HM-REQ-0120 (a spec PR).
  Equally, if PR-E.5's calibration finds the underlying
  break-even shifts, the per-profile tier table updates by
  parameter-inventory ADR.
- **Negative.** Heavy-GPU hypotheses are no longer
  permissionless. A contributor who wants to run a
  `multi-gpu-4x80gb` hypothesis must engage a counterparty.
  This narrows the design's "permissionless market"
  framing for that hypothesis class. The strategy doc 27
  already implied sponsorship was the path for heavy
  workloads; making the gate normative removes any
  ambiguity.
- **Negative.** The pivot couples viability to
  c8-sponsorship-demand. If sponsors don't materialise at
  Phase 2, gated-tier hypotheses don't ship at all (the gate
  rejects them). Mitigation: cold-start contingency in
  [`27 § D — Phase 2.0`](../spec/27-economic-strategy.md#d-phase-by-phase-trajectory)
  already names "no sponsor materialises" as a
  60-day-abort-and-revise trigger.
- **Negative.** The default split `(0.60, 0.30, 0.10)` is
  still a placeholder; PR-E.4's sensitivity sweep refines
  the validator share if 30 % proves insufficient at heavier
  profiles. If a sponsor proposes a custom split, the
  declared values in the `sponsorship` block override.
- **Neutral / deferred.** The dynamic version of lever 4
  ("reject profiles below break-even at *current* N_miners")
  is more sensitive but harder to implement (requires
  on-chain N_miners observability). The static
  safe / gated split shipped here is the pragmatic
  approximation; PR-E.5's calibration ratchet may upgrade
  it later if needed.

## Options considered

- **Static binary safe / gated split (chosen).** Pragmatic;
  reversible; minimal new mechanism.
- **Dynamic per-profile gate based on current `N_miners`.**
  Rejected for now: requires on-chain `N_miners` query in
  the acceptance gate, which doesn't exist as a primitive in
  Phase 1; adds operational complexity for a refinement that
  the worked example doesn't yet justify. PR-E.5 may
  upgrade.
- **Lever 5 alone (treasury-funded subsidy without
  sponsorship).** Rejected: pre-DAO treasury has no inflow
  source other than sponsorship per
  [`28 § D`](../spec/28-treasury.md#d-inflow-paths); a
  pure subsidy has no funding source. Coupling to
  sponsorship is mandatory before DAO incorporation.
- **Lever 2 alone (raise `f_validator` sharply).**
  Rejected per ADR 0019: structurally insufficient.
- **Lever 4 alone without lever 5.** Rejected: a hard cap on
  heavy profiles without an alternative funding path simply
  removes a hypothesis class from the design; combining with
  lever 5 keeps heavy-profile hypotheses viable through
  sponsorship.
- **Tier-3 strategic pivot (lever 6) — make the subnet
  primarily sponsorship-funded.** Rejected as premature: the
  tier-2 pivot here is reversible and minimal; tier-3 is the
  right escalation if Phase 2 shows the sponsorship pipe
  itself is non-viable.

## Related

- Spec: [`02 § sponsorship`](../spec/02-hypothesis-format.md#sponsorship);
  [`02 § Schema validation`](../spec/02-hypothesis-format.md#schema-validation)
  (HM-REQ-0120);
  [`06 § Profile tiers`](../spec/06-scoring.md#profile-tiers);
  [`27 § C.1`](../spec/27-economic-strategy.md#c1-sponsored-hypotheses)
  — sponsorship now load-bearing for gated tier;
  [`00.5 § c4a-emission-sufficient-steady-state`](../spec/00.5-foundations.md#c4a-emission-sufficient-steady-state)
  — annotated conditional on c8;
  [`requirements.md`](../spec/requirements.md),
  [`traceability.md`](../spec/traceability.md) — HM-REQ-0120
  rows.
- ADRs: [0010](0010-economic-strategy.md) — strategy doc;
  [0014](0014-treasury-pre-dao.md) — treasury rules the
  bounty-residual flow uses;
  [0016](0016-viability-decision-protocol.md) — defined
  lever 4 and lever 5;
  [0017](0017-validator-unit-economics.md),
  [0018](0018-participation-equilibrium.md) — surfaced the
  failure this pivot addresses;
  [0019](0019-viability-verdict-not-viable-as-designed.md) —
  the verdict that mandates this pivot.

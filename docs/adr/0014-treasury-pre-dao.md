---
name: 0014 treasury pre-dao
description: rationale for a separate treasury spec doc covering pre-DAO custody, operating-cost catalogue, and Phase 3 transition
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0014 — Treasury, pre-DAO custody

## Context

The post-strategy-doc gap-review surfaced the absence of a
treasury contract as the fourth concrete gap.
[`27-economic-strategy.md`](../spec/27-economic-strategy.md)
named four non-Bittensor revenue paths (sponsored hypotheses,
registry licensing, reproducibility-as-a-service,
credentialing). Each implies a counterparty paying the *subnet*.
The subnet is not yet a legal entity. Nothing in the spec said
where that money lands or who controls it.

Three structural problems with leaving it implicit:

1. **No pre-DAO custody.** The first sponsor (Phase 2 onset)
   would need to know which wallet receives funds and what
   guards exist against maintainer misappropriation. No spec
   answer.
2. **No operating-cost catalogue.** ADRs 0011, 0012, and 0013
   each implied costs (rerun-fraction telemetry, SLI dashboards,
   sponsorship concierge integration) without naming a budget
   or a payer.
3. **No transition contract.** Phase 3 DAO incorporation per
   [`11-roadmap.md § Phase 3`](../spec/11-roadmap.md#phase-3--mainnet)
   would inherit an unknown set of obligations and an unknown
   ledger.

Strategy doc 27 § F explicitly listed treasury / fiduciary
structure as out of scope — that exclusion now has to come down
because PR-A through PR-C have introduced obligations that need
funding.

## Decision

Add new spec doc
[`28-treasury.md`](../spec/28-treasury.md) covering:

- **Custody contract (pre-DAO).** 2-of-3 multisig with two
  maintainer-controlled keys and one external-trustee recovery
  key. Quarterly signed attestation. No commingling.
- **Operating-cost catalogue.** Every spec section that implies
  a recurring or one-off cost lands a row here.
- **Inflow paths.** Sponsorship-bounty residual (placeholder
  60 / 30 / 10 split per
  [`27 § G`](../spec/27-economic-strategy.md#g-open-questions)),
  audit-product fees, voluntary contributions.
- **Outflow rules.** Per-quarter cap (no more than previous
  closing balance), per-line-item cap (25 % single-line ADR
  threshold), no maintainer personal disbursement.
- **Phase 3 DAO transition.** Single batched transfer to DAO
  contract, attestation freeze, custody supersession.
- **Audit posture.** Quarterly attestation ADRs; monthly
  one-line diffs; treasury ledger in scope of the
  [`26-external-review.md`](../spec/26-external-review.md)
  reviewer on request.

Add a new C-row in
[`00.5 § C`](../spec/00.5-foundations.md#c-assumptions-the-defences-require):
`c12-pre-dao-custody` (the bet that first sponsors accept
multisig + attestation custody during Phase 2).

Withdraw the "Treasury / fiduciary structure" out-of-scope line
in
[`27 § F`](../spec/27-economic-strategy.md#f-out-of-scope) for
the pre-DAO period; the strategy doc continues to defer
post-DAO governance.

## Consequences

- **Positive.** First sponsors have a known custody answer
  before they wire any funds. The four ADRs landed under the
  gap-fix sequence (0011, 0012, 0013, 0014) all have a real
  budget line in § C of the new doc rather than implicit
  maintainer self-funding. Phase 3 DAO transition has a
  defined inheritance contract.
- **Negative.** Adds a 29th spec doc the implementer / agent
  may load. Mitigated by `load_for: [governance, review]` —
  invisible to implementer-role context routing. Adds a real
  maintainer commitment: quarterly attestation ADR landings
  starting at the first inflow.
- **Neutral / deferred.** Concrete multisig signers, wallet
  addresses, tax domicile — operational, recorded in the
  bootstrap ADR (a follow-up to this one) when the multisig is
  created. The bootstrap is gated on the first paying
  counterparty; pre-revenue, no multisig is required.

## Options considered

- **Fold into `27-economic-strategy.md`.** Rejected: doc 27 is
  revenue-focused and should remain so. Custody is a
  governance / fiduciary concern with different reviewers.
  Folding bloats 27 past its current 2400-token budget.
- **Fold into `GOVERNANCE.md`.** Rejected: that doc is
  org-governance (who can merge, who can speak for the
  project), not financial. Treasury is its own discipline.
- **Defer until Phase 3 DAO incorporation.** Rejected — was
  the status quo. The first sponsor lands at Phase 2 and needs
  a custody answer at that point, not after Phase 3.
- **Use a single-key maintainer wallet.** Rejected: trust
  surface is too narrow; a compromised maintainer key drains
  the treasury. The 2-of-3 multisig with external recovery is
  the smallest contract that defends against compromise without
  blocking routine operations.
- **Use a 3-of-5 or larger multisig.** Rejected pre-DAO: the
  signer pool is small (one maintainer + one recovery trustee).
  3-of-5 would require fictitious extra signers. The DAO
  inherits a larger multisig at Phase 3.

## Related

- Spec: [`28-treasury.md`](../spec/28-treasury.md);
  [`27-economic-strategy.md § F`](../spec/27-economic-strategy.md#f-out-of-scope)
  (treasury exclusion withdrawn for pre-DAO period);
  [`00.5 § C c12-pre-dao-custody`](../spec/00.5-foundations.md#c12-pre-dao-custody);
  [`11-roadmap.md § Phase 3`](../spec/11-roadmap.md#phase-3--mainnet)
  (DAO transition target);
  [`GOVERNANCE.md`](../../GOVERNANCE.md) (wider governance
  frame).
- ADRs: [0010](0010-economic-strategy.md) — surfaced the gap;
  [0011](0011-d22-coverage-bound.md), [0012](0012-c7-measurement.md),
  [0013](0013-cold-start-contingency.md) — the obligations
  whose costs are now catalogued.
- **Bootstrap (follow-up).** A separate ADR will record the
  multisig wallet address, signer keys, and recovery trustee
  identity once the first counterparty triggers creation.

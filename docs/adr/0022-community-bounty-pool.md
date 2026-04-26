---
name: 0022 community bounty pool
description: extend the sponsorship mechanism to allow a community pool of multiple small sponsors per hypothesis; widen the c8 funnel
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0022 — Community bounty pool

## Context

ADR 0020 introduced the `sponsorship` block as a single-
counterparty bounty mechanism; gated-tier hypotheses (per
[HM-REQ-0120](../spec/02-hypothesis-format.md#schema-validation))
require sponsorship to be accepted. The verdict (ADR 0019)
made `c8-sponsorship-demand` load-bearing — if no big sponsor
materialises at Phase 2, gated hypotheses don't ship.

A natural generalisation: instead of one big counterparty per
hypothesis, allow a **pool** of small sponsors. A community
member can stake 0.5 TAO toward a hypothesis they want to see
tested; the pool aggregates contributions until the
`escrow_block` cutoff and pays out to the settling miner per
the existing 60/30/10 split.

This widens the c8 funnel from "find one big sponsor" to "find
many small ones." Comparable evidence: ResearchHub's RSC bounty
mechanism distributes ~$1.9M across many small bounties
({ref:researchhub-tokenomics-2025}); Gitcoin quadratic-funding
has channelled ~$50M cumulative through small contributors.
The mechanism shape is well-validated externally.

## Decision

### Schema relaxation

[`02 § sponsorship`](../spec/02-hypothesis-format.md#sponsorship)
admits two shapes:

- **Single sponsor** (legacy, unchanged): `sponsor_id`,
  `bounty_tao`, `split`, `escrow_block`.
- **Community pool** (new): `sponsors` array of
  `{sponsor_id, bounty_tao}` entries plus the same `split` and
  `escrow_block`. Pool total is the sum of `sponsors[].bounty_tao`.

Both forms feed the same `split` distribution to miner /
validators / treasury; sponsors do not directly track
per-sponsor recipients — the protocol distributes the pool
total per the split, not per-sponsor.

### HM-REQ-0140 (anti-manipulation)

> A `sponsorship` block declaring `sponsors` (community-pool
> form) MUST satisfy: (a) every entry has a non-empty
> `sponsor_id` and `bounty_tao > 0`; (b) no single
> `sponsor_id` contributes more than 50 % of the sum after
> the `escrow_block` cutoff; (c) at least 2 distinct
> `sponsor_id` values are present.

The single-sponsor form is unconstrained by HM-REQ-0140. The
50 % cap is a placeholder calibrated against intuition and the
small ResearchHub-comparable bounties; Phase 2 pool data may
relax (toward 60–70 % if community pools are routinely
dominated by one anchor sponsor + many small contributors) or
tighten (toward 30 % if whale-steering proves common).

### F7 threat (curation manipulation)

[`00.5 § F7`](../spec/00.5-foundations.md#f7--curation-manipulation)
adds a 7th foundational threat: a whale or sybil cluster
dominating a pool to steer miner attention. Defences D7.1
(per-sponsor cap), D7.2 (≥ 2 distinct sponsors), and D7.3
(rigor floor unchanged) are documented in `00.5 § B`.
Threat-model row T-080 lands in
[`16 § I — Curation attacks`](../spec/16-threat-model.md#i-curation-attacks).

### c13-community-funded-demand (new C-row)

[`00.5 § C`](../spec/00.5-foundations.md#c13-community-funded-demand)
adds the commercial assumption: a meaningful fraction of
would-be hypothesis funders contribute via small TAO stakes
rather than as a single counterparty. ResearchHub and
Gitcoin-QF are the comparables.

## Consequences

- **Positive.** The c8 funnel widens substantially. A subnet
  that fails to attract ResearchHub-scale single sponsors at
  Phase 2 may still attract ~10 individual contributors per
  hypothesis at much smaller stakes. The mechanism is a
  superset of the existing single-sponsor form (single
  sponsor still works); no existing flow breaks.
- **Positive.** Community pools serve as a passive curation
  signal: hypotheses with strong community support self-
  identify by attracting larger pools, helping miners pick
  which open hypotheses to work on first. This addresses an
  open question that was previously unaddressed —
  *which hypotheses are worth a miner's time?*
- **Negative.** Adds F7 as a new threat. The mitigation
  (HM-REQ-0140's 50 % cap + ≥ 2 distinct sponsors) is
  mechanical but not exhaustive — a whale can still steer
  attention by registering multiple sponsor-IDs (sybil),
  which costs registration fees but isn't structurally
  prevented. Phase 2 fixture under HM-REQ-0090 quantifies
  the residual risk. Tier-1 lever (raise the cap from 50 %
  to a tighter bound) is available if Phase 2 data shows
  whale behaviour.
- **Negative.** Mechanism complexity grows. Authors and
  reviewers must now reason about which sponsorship form a
  hypothesis declares; validators must check the
  HM-REQ-0140 invariants on community pools. Mitigation:
  default form (single sponsor) covers the legacy case;
  community pool is opt-in. The schema makes the choice
  explicit.
- **Neutral / deferred.** Withdrawal mechanics (can a
  contributor withdraw before settlement?) are not specified
  here; the default is "no — sponsors are committed once the
  pool closes at `escrow_block`." Quadratic-funding match
  amplification (mechanism 3 from the original menu) is also
  deferred; this PR ships only mechanism 1 as the smallest
  step. Curation-market yield (mechanism 2) is also deferred.

## Options considered

- **Mechanism 2 — curation market with stake-and-yield.**
  Stake to signal interest, earn yield from validator
  dividends if the hypothesis settles, get slashed if it
  withdraws. Rejected for now: token-curated registries have
  largely failed empirically; the staking-yield logic
  introduces lifecycle complexity (HM-INV-0005 withdrawal
  semantics interact with stake-return) that the simpler
  community-pool form avoids.
- **Mechanism 3 — quadratic-funding match.** Maintainer /
  treasury fund matches community contributions sub-linearly.
  Rejected for now: requires sybil-resistant identity
  infrastructure (Gitcoin Passport-equivalent) the subnet
  doesn't have. Worth revisiting at Phase 3+.
- **Strict per-hypothesis cap on total pool size.** Rejected:
  caps the upside without addressing the F7 concentration
  risk. The per-sponsor cap targets the actual threat;
  total-pool cap addresses neither cause nor symptom.
- **No anti-manipulation cap; rely on rigor floor.** Rejected:
  rigor protects against unrigorous hypotheses being merged,
  but does not prevent rigorous-but-unimportant hypotheses
  from capturing miner attention via whale steering.
  HM-REQ-0140 is the explicit defence.
- **Voting mechanism (1-account-1-vote) instead of pool
  staking.** Rejected: introduces new sybil surface
  (1-account-many-wallets) without the wallet-stake skin in
  the game. Pool staking aligns the curation signal with
  actual TAO commitment — voters bear cost.

## Related

- Spec: [`02 § sponsorship`](../spec/02-hypothesis-format.md#sponsorship)
  (schema relaxation);
  [`02 § Schema validation`](../spec/02-hypothesis-format.md#schema-validation)
  (HM-REQ-0140);
  [`00.5 § F7`](../spec/00.5-foundations.md#f7--curation-manipulation)
  (new threat);
  [`00.5 § B Defences against F7`](../spec/00.5-foundations.md#defences-against-f7-curation-manipulation);
  [`00.5 § C c13`](../spec/00.5-foundations.md#c13-community-funded-demand);
  [`16 § I — Curation attacks`](../spec/16-threat-model.md#i-curation-attacks)
  (T-080);
  [`requirements.md`](../spec/requirements.md),
  [`traceability.md`](../spec/traceability.md) — HM-REQ-0140
  rows.
- ADRs: [0010](0010-economic-strategy.md) — strategy doc;
  [0019](0019-viability-verdict-not-viable-as-designed.md) —
  the verdict that made c8 load-bearing;
  [0020](0020-sponsor-gated-heavy-profiles.md) — single-
  sponsor form this ADR generalises;
  [0021](0021-oracle-only-verification.md) — third viability
  path that ALSO benefits from community pools (oracle-only
  hypotheses can be community-funded).
- Roadmap: c13 first-evidence point at Phase 2 onset; F7
  fixture under HM-REQ-0090 lands by Phase 2 mid-point
  review.

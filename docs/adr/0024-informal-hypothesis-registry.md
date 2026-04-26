---
name: 0024 informal hypothesis registry
description: add a parallel I-NNNN registry for informal hypotheses (brainstorming layer) and route a small ideator slice of sponsor pools to cited proposers
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0024 — Informal hypothesis registry

## Context

The subnet rewards execution (running preregistered experiments) and,
through the 0.15 novelty weight, the first miner to formalise a
question that someone else has already merged. It does not reward
the upstream act of *proposing* a question. Every entry under
[`/hypotheses/`](../../hypotheses/) is already a fully preregistered,
falsifiable claim with a runnable protocol — i.e. **formal**. The
schema's `depends_on` / `contradicts` fields capture formal-to-formal
lineage but carry no economic flow.

Consequence: an idea-haver who is not also a miner has no reason to
share an unformalised question. They can't run it themselves; the
person who *can* (a miner-formaliser) faces zero attribution
obligation. The pipeline narrows to questions that originate inside
the small set of contributors who can write a full preregistered
hypothesis.

ADR 0022 widened the c8 demand funnel by admitting community
sponsorship pools. This ADR widens the *supply* funnel
symmetrically: anyone can post a cheap, schema-validated seed
question; the formal author who picks it up cites it; the sponsor
pool reserves a small slice for the originator on settlement.

## Decision

### A new artifact class — `I-NNNN` informal hypothesis

A parallel registry under `/informal/` (created in PR 2) holds
**informal hypotheses**: cheap-to-post seed questions without a
runnable protocol. IDs are monotonic, immutable, and never recycled —
same discipline as `H-NNNN` and `HM-REQ-NNNN`. Schema is the contract
(`02b-informal-hypothesis-format.md`, PR 2): claim, domain, proposer
hotkey, chain-anchored block, optional motivating evidence, optional
non-binding protocol sketch.
Posting requires a small TAO bond (`ideator_min_stake`); the bond
returns when any formal hypothesis cites the I-NNNN at acceptance
(T-ACC) or expires to treasury after `ideator_expiry_blocks` if
unclaimed. Bond + expiry together discipline volume-spam (D8.1).

The moment an informal hypothesis acquires an analysis plan,
falsification criteria, and a runnable protocol, it becomes a formal
H-NNNN. The two registries don't overlap — converting a claimed
I-NNNN into an H-NNNN is the explicit, intended path, not a
bug-shaped one.

### Attribution — `inspired_by` field on `H-NNNN`

Formal hypotheses gain an optional, weighted `inspired_by` field
(PR 2):

```yaml
inspired_by:
  - id: I-0001
    weight: 0.7
  - id: I-0042
    weight: 0.3
```

Constraints (HM-REQ-0151, PR 3): ≤ 3 entries; weights sum to 1.0;
each cited I-NNNN must be `accepted` and ≥ `ideator_staleness_blocks`
older than the citing H-NNNN's PR open block (D8.2 — forecloses
same-block collusive creation); no cited I-NNNN's `proposer_hotkey`
may equal the H-NNNN's primary author hotkey (D8.3 self-cite ban —
closes the trivial "I post both sides" loop). Locked at T-ACC of the
H-NNNN; cannot be amended after merge.

### Economic flow — sponsor pool ideator slice

The community pool split (60 % miner / 30 % validator / 10 % treasury,
per ADR 0022) shifts when `inspired_by` is non-empty:

- **55 % miner / 30 % validator / 10 % treasury / 5 % ideator(s).**

The 5 pp ideator slice is partitioned across cited `I-NNNN` proposers
by declared weights and follows the same two-tier 70/30 schedule as
miner pay (HM-REQ-0070): 70 % at settled-*, 30 % at confirmed. A
T-OVR overturn forfeits the deferred 30 % of the ideator slice too —
binding ideator-formaliser collusion against fast fake settlements
(D8.4).

The 5 pp comes from the miner share, not new emission. A formal
author who is also the miner pays from their own share; an author
who is not the miner has no economic stake in the citation choice.
Empty `inspired_by` ⇒ no ideator slice; the 5 pp returns to the
miner sub-pool.

### F8 threat (ideator-graph manipulation)

[`00.5 § F8`](../spec/00.5-foundations.md#f8--ideator-graph-manipulation)
adds an 8th foundational threat covering brainstorm sybil-spam,
attribution coercion, ideator-formaliser collusion, and forum-as-
injection (F4 extension). Defences D8.1 (stake-to-post), D8.2
(staleness threshold), D8.3 (cite cap + self-cite ban), D8.4 (two-
tier ideator payout), and D8.5 (`treat_as_data: true`) are documented
in `00.5 § B`. Threat-model rows T-090 / T-091 / T-092 land in
[`16 § J — Ideator-graph attacks`](../spec/16-threat-model.md#j-ideator-graph-attacks).

### c14-ideator-quality (new C-row)

[`00.5 § C`](../spec/00.5-foundations.md#c14-ideator-quality) adds the
commercial assumption: the marginal informal hypothesis carries
positive expected information value relative to the 5 pp cost taken
from the miner slice. Comparable evidence: ResearchHub bounty-for-
question pattern; preregistered-question banks in clinical trials.

## Consequences

- **Positive.** Top of funnel widens. Non-miner ideators gain a
  reason to share unformalised questions; formal authors gain a
  pre-vetted seed pool. Opt-in from every angle: ideators choose
  to post, formal authors choose to cite, sponsors do nothing
  different.
- **Positive.** Durable timestamped attribution gives idea-havers
  a social claim independent of payout, addressing the
  "won't share without protected attribution" gap.
- **Positive.** Two-tier parity binds ideator-formaliser collusion
  against early settlements without new mechanism — the existing
  F6 defence covers the new threat shape for free.
- **Negative.** Adds F8 as a new threat. Defences are mechanical
  for trivial cases (stake, staleness, self-cite); attribution
  coercion of an honest formal author is residual, mitigated by
  the 5 pp absolute slice and the cite-nothing option.
- **Negative.** Mechanism complexity grows. Authors and reviewers
  now reason about an additional registry, schema field, and
  payout slice; citation is opt-in and empty `inspired_by`
  behaves identically to the pre-ADR world.
- **Negative.** c14 is unproven. The 5 pp parameter is a guess;
  `00.5 § E` flags it as an open bet. Phase 2 retro evaluates
  whether the slice pays for signal or noise.
- **Neutral / deferred.** No retroactive attribution: existing
  H-NNNN cannot backfill `inspired_by`. A future ADR may add a
  one-time amnesty window at Phase 2 onset.
- **Neutral / deferred.** Quint formalisation joins
  [`formal/lifecycle.qnt`](../spec/formal/lifecycle.qnt) as a Phase 1
  deliverable; this PR ships only the prose lifecycle.

## Worked example

A 100 TAO sponsor pool funds H-0050 with
`inspired_by: [I-0001 (0.6), I-0002 (0.4)]`. On `settled-supported`
the 70 % first-tier pays 38.5 / 21.0 / 7.0 / 2.1 / 1.4 TAO to
miner sub-pool / validators / treasury / I-0001 proposer / I-0002
proposer; on `confirmed` six months later the deferred 30 % pays
16.5 / 9.0 / 3.0 / 0.9 / 0.6 TAO. A T-OVR overturn before
confirmation forfeits the deferred column across all rows
including ideators.

## Options considered

- **Cut from miner emission rather than sponsor pool.** Rejected:
  pool-only keeps the cost local to the hypothesis that benefited.
  Emission cuts would dilute every honest miner across every
  hypothesis, including those without informal upstreams.
- **Treasury-funded ideator pool.** Rejected for now: treasury
  funds are pre-DAO and earmarked per
  [28-treasury.md](../spec/28-treasury.md); a new draw needs
  governance the subnet doesn't have at Phase 0. Revisit at Phase 3+.
- **Ideator self-stake with multiplier on success.** Rejected for
  now: parallel staking-yield mechanism with its own slashing
  surface; bond-and-expiry achieves spam-resistance at lower
  complexity. Revisit if the bond proves too weak.
- **Off-chain forum with hash-anchor commitments.** Rejected: the
  spec's discipline (immutable IDs, schema validation, threat-
  traceable defences) only works when the artifact is first-class.
  An off-chain forum cannot back a 5 pp economic flow.
- **No new artifact — reuse `proposed` H-NNNN status.** Rejected:
  the current `proposed` is "PR open for a fully-formed hypothesis";
  informal hypotheses must be cheap to post precisely *because*
  they aren't fully formed.
- **Validator-scored attribution.** Rejected: introduces judgment
  into the score path, which violates D1.2 (deterministic pure-
  function scoring). Self-declared + locked-at-T-ACC keeps
  attribution mechanical.

## Related

- Spec (this PR): F8 threat + D8.x defences + c14 assumption in
  [`00.5`](../spec/00.5-foundations.md); T-090/091/092 in
  [`16 § J`](../spec/16-threat-model.md#j-ideator-graph-attacks);
  HM-REQ-0151..0154 in [`requirements.md`](../spec/requirements.md).
- Spec (subsequent PRs): `inspired_by` field on the formal
  hypothesis schema, `02b-informal-hypothesis-format.md` for the
  I-NNNN schema, an informal-hypothesis lifecycle in
  `17-hypothesis-lifecycle.md`, and the sponsor-pool ideator slice
  in `07-incentive.md`.
- ADRs: [0019](0019-viability-verdict-not-viable-as-designed.md) —
  the verdict that made c8 load-bearing;
  [0022](0022-community-bounty-pool.md) — the community-pool
  mechanism this ADR extends with an ideator slice.
- Roadmap: c14 first-evidence point at Phase 2 onset; F8 fixture
  under HM-REQ-0090 lands by Phase 2 mid-point review.

---
name: 0025 threshold-gated execution
description: gate miner execution on a per-hypothesis sponsor-pool threshold, with a funding window and exact-bounty refund on expiry; turns c8-sponsorship-demand into a per-hypothesis empirical signal
kind: decision
status: accepted
date: 2026-04-27
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0025 — Threshold-gated execution

## Context

ADR 0019's viability verdict made
[c8-sponsorship-demand](../spec/00.5-foundations.md#c8-sponsorship-demand)
load-bearing: heavy-profile hypotheses must carry their own bounty
or they don't ship. ADR 0022 widened the c8 funnel from "find one
big sponsor" to "find a community pool of small sponsors." ADR 0024
widened the supply funnel symmetrically with the informal-hypothesis
layer. None of those PRs produced a calibration primitive for c8 —
they made the plumbing more flexible without giving the maintainer a
way to *measure* c8 at the per-hypothesis level.

Today, sponsorship is a binary gate at acceptance:
[HM-REQ-0120](../spec/02-hypothesis-format.md#schema-validation)
requires a `sponsorship` block for gated-tier profiles, but once the
hypothesis merges, miners may run it regardless of pool size. A
half-funded hypothesis ties up miner attention without the economic
signal a fully-funded one would carry; a no-sponsor hypothesis on
safe-tier may sit unmined indefinitely with no clean read on whether
the absence reflects no-demand or no-discovery.

Consequence: we have no way to distinguish "demand exists at the
spec's asking price" from "this hypothesis attracted partial
attention and stalled." Every c8 datum is mixed.

## Decision

### Threshold-gated execution

A formal hypothesis declares a `sponsorship.min_pool_tao` floor and
a `sponsorship.funding_window_blocks` window. Between merge and
threshold-clear, the hypothesis sits in a new `pending-funding`
lifecycle state: sponsors may contribute, miners may NOT submit. On
the first block where `sponsorship.sum ≥ min_pool_tao`, T-FUND fires
and the hypothesis transitions to `accepted` (mining-eligible). If
the funding window elapses without clearing, T-FEXP fires; the pool
refunds each sponsor their `bounty_tao` exactly, and the hypothesis
enters terminal `expired-funding` (the `id` cannot be reused).

The default `min_pool_tao` is the profile-formula
`2 × budget_wallclock_usd(profile) × seeds_required × usd_per_tao`
with `usd_per_tao` pinned at PR-merge block (single value, frozen).
Authors may override with explicit justification at PR review; the
maintainer's audit reference is the formula default.

The default `funding_window_blocks` is 216 000 (~30 days at 12 s
blocks); maximum is 540 000 (~90 days). 30 days is the empirical
modal duration on Kickstarter / Experiment.com; shorter windows
correlate with higher success rates per
{ref:sauermann-crowdfunding-2018}.

### Refund mechanics

T-FEXP refunds each sponsor exactly their committed `bounty_tao`.
No pro-rata haircut, no slashing, no loss to honest sponsors.
Sponsors may NOT withdraw before T-FEXP — once committed, the bond
is locked until either T-FUND (paid out at settlement per the
existing 55/30/10/5 or 60/30/10 split) or T-FEXP (refunded). This
forecloses the "withdraw at the last block before threshold-clear"
griefing pattern.

The terminality of `expired-funding` is deliberate. A hypothesis
that fails its funding window is discarded; reuse of the `id` is
forbidden. The author opens a new spec PR with a new `id` to retry.
This makes funding failure a hard signal rather than a soft retry
loop, and matches the all-or-nothing discipline of every comparable
platform (Experiment.com, Kickstarter, SciFund).

### F7 threat extension (curation manipulation)

The mechanism opens two new attack surfaces. Both are folded into
[`00.5 § F7`](../spec/00.5-foundations.md#f7--curation-manipulation)
rather than introduced as a new F-row, because the threat shape is
the same — adversaries steering miner attention via the funding
mechanism.

- **F7.4 Funding-stall DoS.** Adversary creates many high-threshold
  hypotheses, never funds them, ties up sponsor mindshare or
  maintainer review attention. Mitigation: T-FEXP automates the
  abandonment; refund mechanics make stalls cost-free for honest
  sponsors; spec-PR review at maintainer time catches obvious
  patterns; per-author rate limits are inherited from existing
  registration economics.
- **F7.5 Threshold gaming via lowball.** Author sets implausibly low
  `min_pool_tao` to bootstrap fast execution at zero economic
  signal. Mitigation: profile-formula default; maintainer review of
  any override; `min_pool_tao` is fixed at PR merge time (no
  post-acceptance adjustment).

T-row updates in
[`16 § I — Curation attacks`](../spec/16-threat-model.md#i-curation-attacks):
T-081 (funding-stall DoS) and T-082 (threshold gaming).

### c15-funding-velocity (new C-row, shape claim)

[`00.5 § C`](../spec/00.5-foundations.md#c15-funding-velocity) adds
the assumption that funding-window outcomes are bimodal:
front-loaded fills for hypotheses that reach T-FUND, exponential
decay (not late rally) for those that don't. This is empirically
supported across Experiment.com (48 % AON success on 728 science
campaigns), Kickstarter (~40 %), SciFund (62–70 %), and confirmed
by the UCLA Anderson "stampede to threshold" finding (2.5× longer
100→105 % than 95→100 %). The claim is deliberately about
*distribution shape*, not absolute T-FUND rate — Polymarket
cold-start (63 % of short-term markets fail to find any liquidity)
is the cautionary anchor for thin-audience subnets.

If c15 is false (drip-funded campaigns dominate), T-FUND becomes a
noisy proxy rather than a clean bimodal signal; the diagnostic
value of the gate collapses. Phase 2 SLI tracks the funding-curve
shape, not just the count.

### Composition with ADR 0024

An ideator (HM-REQ-0152 bond holder on an `I-NNNN`) cited in a
formal hypothesis's `inspired_by` MAY contribute to that
hypothesis's `sponsorship` pool. No new mechanism is needed —
`sponsor_id` already accepts any SS58 hotkey. The "I'll put 0.5
TAO behind my own idea" dynamic is empirically the strongest
single predictor of crowdfunding success
({ref:bi-self-pledge-2025}); making it explicit in the schema's
sponsorship section is a documentation pass, not a new feature.

## Worked example

H-0050 declares `single-gpu-24gb` profile (`budget_wallclock_usd =
2.00`), `seeds_required = 5`, `min_pool_tao = 20.0` (profile-formula
default at `usd_per_tao = 1.0`):

| t (blocks) | event | pool | state |
|------------|-------|------|-------|
| 0 | author opens PR | — | (off-registry) |
| 100 | maintainer merges; T-PFUND fires | 0 | `pending-funding` |
| 500 | sponsor A contributes 5 TAO | 5 | `pending-funding` |
| 1 200 | I-0001 ideator (cited via `inspired_by`) contributes 3 TAO | 8 | `pending-funding` |
| 8 500 | sponsor B contributes 12 TAO | 20 | T-FUND fires → `accepted` |
| 8 600 | first miner submits → T-RUN | 20 | `running` |
| 12 000 | settled-supported → 70 % of 20 TAO paid per 55/30/10/5 split | 20 | `settled-supported` |

Counter-example: same H-0050 but only 12 TAO accumulates by block
100 + 216 000:

- T-FEXP fires → `expired-funding` (terminal)
- 12 TAO refunded to sponsors (5 to A, 3 to ideator, 4 to B)
- Author opens a new PR with new `id` to retry

## Consequences

- **Positive.** c8 becomes a per-hypothesis empirical signal. Phase
  2 onset gives a clean read on funding distribution shape and rate
  rather than a binary "did anything happen."
- **Positive.** The ideator self-pledge dynamic gets explicit
  schema-level support, which the crowdfunding literature shows is
  the strongest single predictor of campaign success.
- **Positive.** Refund mechanics protect sponsors against stalls,
  encouraging participation in early / risky pools.
- **Negative.** Adds two new lifecycle states and three new
  transitions, growing the state machine. Mitigated by Quint
  formalisation as a Phase 1 deliverable.
- **Negative.** F7 attack surface widens (F7.4 / F7.5). Both have
  mechanical mitigations but residual risk — coordinated stalls
  could be used as curation-by-omission.
- **Negative.** c15 is unproven for thin-audience cold start.
  Polymarket comparison suggests a 30–50 % T-FUND rate ceiling at
  Phase 2 onset.
- **Negative.** A failed funding window is terminal; retry requires
  a new `id`. This is deliberate (matches AON discipline) but adds
  friction for hypotheses that need iteration.
- **Neutral.** Composition with HM-REQ-0150 multi-miner consensus:
  T-FUND must fire before any submission counts toward
  `min_settling_miners`. The two gates compose without
  modification.

## Options considered

- **Partial-fill execution at lower seed count.** Rejected: every
  comparable platform uses strict all-or-nothing; partial fills
  introduce multi-dimensional pricing the spec lacks machinery
  for.
- **Pro-rata refund (haircut on T-FEXP).** Rejected: punishes
  honest early backers; exact-bounty refund matches industry
  standard.
- **Withdrawals allowed before T-FEXP.** Rejected: opens
  last-block griefing pattern. Sponsors keep timing optionality
  by contributing later; commits are locked.
- **Author-set threshold with no formula default.** Rejected:
  enables F7.5 lowball gaming.
- **Maintainer-curated thresholds.** Rejected: governance
  bottleneck; formula-default + override-with-justification
  achieves the same audit at lower cost.
- **Reusable `id` after T-FEXP.** Rejected: makes failure a
  soft signal; the new-PR retry is itself a quality filter.
- **`usd_per_tao` pinned at funding-clear time.** Deferred: PR-
  merge pinning is auditable and predictable. Phase 2 revisits
  if intra-window TAO volatility becomes material.

## Related

- Spec (this PR — A): F7.4 / F7.5 sub-threats + D7.4 / D7.5
  defences + c15 in
  [`00.5`](../spec/00.5-foundations.md);
  T-081 / T-082 in
  [`16 § I`](../spec/16-threat-model.md#i-curation-attacks);
  `pending-funding` / `expired-funding` states + T-PFUND / T-FUND
  / T-FEXP in
  [`17`](../spec/17-hypothesis-lifecycle.md);
  HM-REQ-0160..0162 in [`requirements.md`](../spec/requirements.md).
- Spec (subsequent PR — B): `min_pool_tao` and
  `funding_window_blocks` fields on `02 § sponsorship`; parameter
  inventory entries in `20-economic-model.md`; pending-funding
  submission rejection note in `06-scoring.md`; S-MINE scenarios
  in `23-system-tests.md`; glossary entries.
- ADRs: [0019](0019-viability-verdict-not-viable-as-designed.md) —
  the verdict that made c8 load-bearing;
  [0020](0020-sponsor-gated-heavy-profiles.md) — single-sponsor
  form; [0022](0022-community-bounty-pool.md) — community-pool
  form this ADR gates; [0024](0024-informal-hypothesis-registry.md)
  — ideator self-pledge composition.
- Roadmap: c15 first-evidence point at Phase 2 onset; F7 fixture
  under HM-REQ-0090 lands by Phase 2 mid-point review (extended
  to cover F7.4 / F7.5).

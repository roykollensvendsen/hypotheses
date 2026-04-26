---
name: 0012 c7 measurement
description: make c7 (ground-truth latency under 12 months) falsifiable by pinning the SLI thresholds and the HM-REQ-0070 revision trigger
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0012 — C7 measurement plan

## Context

HM-REQ-0070's two-tier settlement (70 % at first
`settled-*`, 30 % deferred for 6 months) is the design's
defence against F6 (long-latency rent extraction). The defence
only works if
[c7-ground-truth-latency](../spec/00.5-foundations.md#c7-ground-truth-latency)
holds — most hypotheses settle in weeks-to-months, with the long
tail under 12 months.

Until this PR, c7 was an admonition with no measurement plan.
[`19-operations.md`](../spec/19-operations.md) listed
"settlement latency | time from `accepted` to first `settled-*`,
per hypothesis" as a subnet-wide SLI but did not name a healthy
range, percentiles, or a trigger that turns a real-world latency
distribution into a defence revision.

The post-strategy-doc gap-review surfaced this as the second
concrete gap to close after the D2.2 coverage bound (ADR 0011).

## Decision

Add p50 and p95 settlement-latency thresholds to the subnet-wide
SLI table in
[`19-operations.md`](../spec/19-operations.md#subnet-wide-slis-for-the-maintainer)
with the healthy ranges:

- **p50 ≤ 90 days** (3 months) — median.
- **p95 ≤ 12 months** — long-tail.

Window: trailing 90 days of `settled-*` hypotheses.

Define the **HM-REQ-0070 revision trigger**: when the SLI breach
is observed across **≥ 10 settled hypotheses** (the minimum
sample for the percentile to be meaningful), the maintainer
opens an ADR revising HM-REQ-0070's 6-month deferred-settlement
window. Either of the following fires the trigger:

- p50 > 6 months — the typical hypothesis is settling slower
  than the deferred window; the 30 % retention does nothing
  because settlement hasn't completed.
- p95 > 12 months — the long-tail blew through the c7
  assumption; the deferred window is too short to defend
  against rent extraction in that tail.

Cross-reference the SLI from
[`00.5 § C c7-ground-truth-latency`](../spec/00.5-foundations.md#c7-ground-truth-latency)
as a "Measurement" sub-bullet so the bet is now falsifiable from
the foundation table inward.

## Consequences

- **Positive.** c7 is no longer a free assumption — it has a
  numerical threshold, a sample-size floor, and a named follow-up
  ADR if it breaks. F6 defence either keeps holding (continue at
  the 6-month window) or gets revised (longer window or
  per-hypothesis class), but the decision is data-driven instead
  of optimistic.
- **Negative.** Adds a maintainer commitment to monitor the SLI
  starting at Phase 2 onset. The SLI is unmeasurable until ≥ 10
  hypotheses settle — that's a real Phase 2 milestone, not just
  netuid registration. The 6-month foundation review cadence per
  [`00.5 § Review cadence`](../spec/00.5-foundations.md#review-cadence)
  absorbs the monitoring overhead.
- **Neutral / deferred.** Per-hypothesis-class latency models
  (oracle-gated vs reproducibility-gated, ML-research vs
  empirical-claim) are not introduced here. If the simple
  network-wide p50/p95 turns out to be misleading because of
  class composition, a follow-up ADR adds the breakdown. The
  oracle-verdict-latency SLI in the same table covers the
  oracle-specific portion separately.

## Options considered

- **Single threshold (p50 ≤ 6 months).** Rejected: a long-tail
  outlier at 18 months is exactly what HM-REQ-0070 needs to
  defend against, and a p50-only check misses it.
- **No sample-size floor (trigger on first breach).** Rejected:
  one slow hypothesis can blow the percentile in a small window;
  spurious triggers waste maintainer attention. The ≥ 10
  threshold is the smallest sample where p95 carries useful
  information.
- **Tighter healthy range (p95 ≤ 6 months).** Rejected: c7
  itself says "rare" hypotheses go beyond 12 months; pinning the
  threshold below the assumption's own boundary would force
  spurious revisions.
- **Defer measurement to Phase 3.** Rejected: Phase 2 is when
  HM-REQ-0070 is first exposed to live miner / validator
  incentives. Measuring then is the whole point.

## Related

- Spec:
  [`19-operations.md`](../spec/19-operations.md#subnet-wide-slis-for-the-maintainer)
  — the SLI table this ADR extends;
  [`00.5-foundations.md § C c7-ground-truth-latency`](../spec/00.5-foundations.md#c7-ground-truth-latency)
  — the assumption now annotated with measurement;
  [`requirements.md` HM-REQ-0070](../spec/requirements.md);
  [`17-hypothesis-lifecycle.md`](../spec/17-hypothesis-lifecycle.md)
  — `accepted` → `settled-*` transitions the SLI tracks;
  [`00.5 § F6`](../spec/00.5-foundations.md#f6--long-latency-rent-extraction).
- ADRs: [0010](0010-economic-strategy.md) — surfaced the gap;
  [0011](0011-d22-coverage-bound.md) — first PR in the gap-fix
  sequence.
- Roadmap: SLI arms at Phase 2 onset, fires once ≥ 10
  hypotheses settle. Maintainer opens revision ADR within the
  60-day commitment from
  [`26-external-review.md § Reviewer profile`](../spec/26-external-review.md#reviewer-profile).

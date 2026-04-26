---
name: 0009 external review plan
description: decision to specify a one-shot adversarial review of the foundation as a separate spec doc, rather than folding into 22-security-bounty or deferring entirely
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0009 — External adversarial review plan

## Context

In-house threat modelling has known blind spots. The standing
white-hat programme in
[`22-security-bounty.md`](../spec/22-security-bounty.md) addresses
ongoing discovery during operation, but does not exercise the
foundation before Phase 2 launches. By the time the white-hat
programme is producing findings at scale, the foundation will
already be in production with external miners and validators
relying on its defences — at which point revising a defence
costs coordination, not just a spec PR.

The cheapest way to surface foundation gaps is a one-shot
adversarial review by an invited reviewer with security or
mechanism-design background, before Phase 2. This is a known
practice in security engineering (pre-deployment audits) and in
mechanism design (referee review before a market launches).

## Decision

Specify the review's scope, criteria, output format, and
trigger condition in a new spec doc,
[`docs/spec/26-external-review.md`](../spec/26-external-review.md).
Do not yet book a reviewer — that's a one-shot human action
gated on Phase 2 prep. Locking the spec now means when the
trigger fires, the review is well-defined; the maintainer
doesn't have to redesign the review under time pressure.

The doc is `kind: contract` because it describes a normative
process (what every external review must produce, how findings
are triaged, what the maintainer commits to), and
`evidence: reasoned-design` because the process is a design
choice with stated rationale (the trigger condition argument,
the severity scale, the reviewer-profile criteria), not a claim
about external research.

## Consequences

- **Positive.** The review's scope, criteria, and severity
  scale are fixed before the reviewer is engaged, so the
  maintainer can engage on a known framework rather than
  improvising. The cheaper LLM-ensemble parallel variant is
  documented as a complement, not a substitute, so the review
  pipeline can start producing findings now without waiting on
  a human engagement.
- **Negative.** Adds a 27th spec doc the implementer / agent
  may load. Mitigated by the narrow `load_for: [governance,
  review]` — the doc is invisible to the implementer-role
  context routing. Also adds a process commitment (14-day
  acknowledge / 60-day decide) that the maintainer must keep,
  but the cost of a missed commitment is loss of reviewer
  trust, which is the right incentive.
- **Neutral / deferred.** Actually engaging a reviewer is the
  human action this doc enables; that's still future work. A
  follow-up `/schedule` reminder firing in 8–12 weeks (or at a
  Phase-1-progress milestone) keeps the action from sliding.

## Options considered

- **Fold into `22-security-bounty.md`.** Rejected: doc 22
  describes an *ongoing* community programme keyed on operation;
  this doc describes a *one-shot* pre-launch review by an
  invited expert. Different audience (external vs broad),
  different cadence (one-shot vs continuous), different output
  format (single document vs hypothesis-shaped advisory).
  Folding would dilute both.
- **Defer entirely; just open an issue when the time comes.**
  Rejected: by Phase 2 prep the maintainer is already busy with
  testnet onboarding. Pre-specifying the review's shape now,
  while the maintainer has bandwidth, prevents a sloppy
  improvised review later.
- **Skip the human review; rely on the LLM ensemble alone.**
  Rejected: LLMs share training-data blind spots that a human
  with real-world incident experience would find. The ensemble
  is complementary, not a substitute.

## Related

- Spec: [`26-external-review.md`](../spec/26-external-review.md)
  — the contract this ADR justifies;
  [`00.5-foundations.md`](../spec/00.5-foundations.md) — the
  primary review target;
  [`22-security-bounty.md`](../spec/22-security-bounty.md) —
  the ongoing programme this review complements;
  [`21-adversarial-simulator.md`](../spec/21-adversarial-simulator.md)
  — secondary review target;
  [`25-rigor-framework.md`](../spec/25-rigor-framework.md) —
  the evidence taxonomy review findings adopt.
- Roadmap trigger: Phase 2 onset per
  [`11-roadmap.md`](../spec/11-roadmap.md) (testnet with ≥3
  external miners and ≥2 external validators).

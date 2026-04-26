---
name: 0010 economic strategy
description: rationale for a separate spec doc covering investment thesis and non-Bittensor revenue paths, distinct from the operational economics doc
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0010 — Economic strategy

## Context

A triage of the spec's economic dimension surfaced an
asymmetry. [`20-economic-model.md`](../spec/20-economic-model.md)
treats *operational* economics rigorously (parameters,
governance flow, anti-gaming) but is silent on *revenue* and
only implicitly addresses *investment*. The investment story
today is the standard Bittensor one: hold dTAO, allocate to
this subnet's Alpha believing emission share will grow.
[`00.5 § D`](../spec/00.5-foundations.md#d-what-we-explicitly-give-up)
states the subnet has no revenue of its own;
[`20-economic-model.md § Out of scope`](../spec/20-economic-model.md#out-of-scope)
calls TAO price prediction out of scope. Nowhere are
non-Bittensor revenue paths specified.

Investors and external sponsors form their own theses
regardless of whether the spec articulates one. The choice is
between articulating it explicitly so reviewers and the
upcoming review (see
[`26-external-review.md`](../spec/26-external-review.md)) can
pressure-test it, or letting it solidify as folklore. Web
survey conducted before this ADR — dTAO live since 2025;
ResearchHub RSC ($1.9M distributed); VitaDAO IP-NFT ($55.8M
treasury, $1B+ Gero / Chugai); DeSci ecosystem ~$329M cap —
supports that non-Bittensor revenue paths are real surfaces.

## Decision

Add [`27-economic-strategy.md`](../spec/27-economic-strategy.md)
as the canonical home for the investment thesis and the four
non-Bittensor revenue paths. Each carries status, mechanism,
comparable evidence, and an explicit `> **assumption:**`
admonition resolving to a new C-row in
[`00.5 § C`](../spec/00.5-foundations.md#c-assumptions-the-defences-require).
Four C-rows (`c8-sponsorship-demand`, `c9-registry-ip-value`,
`c10-audit-demand`, `c11-credential-demand`) ship in the same
PR.

The doc is `kind: contract, evidence: reasoned-design`.
Strategic claims rest on comparable-model evidence and stated
rationale; each commercial assumption is unproven for *this
subnet's specific question domain*, even where the comparable
evidence is strong for an adjacent domain.

The doc deliberately excludes quantitative survival analysis
(unit economics, equilibrium modelling, sensitivity tables) —
a separate multi-PR work stream worth doing before mainnet but
not blocking this PR. It inherits the existing TAO-price and
treasury-management exclusions.

## Consequences

- **Positive.** Investment narrative now exists in a
  reviewable form before Phase 2 onset. The four commercial
  assumptions are declared in the canonical `00.5 § C` table
  so Phase 2 retrospectives can update them. Writing the
  strategy surfaced c8–c11, which the foundation needed
  regardless of revenue-path decisions.
- **Negative.** Adds a 28th spec doc; mitigated by narrow
  `load_for: [governance, review]` (invisible to
  implementer-role context routing). Adds a process commitment
  to keep comparables / phase trajectory current; mitigated by
  the existing 6-month foundation review cadence per
  [`00.5 § Review cadence`](../spec/00.5-foundations.md#review-cadence)
  which now extends to c8–c11.
- **Neutral / deferred.** Quantitative survival analysis
  remains unscheduled; this ADR does not block on it. Treasury
  / fiduciary structure deferred to DAO incorporation
  (Phase 3+). Pre-Phase-2 external review now has one more doc
  in scope.

## Options considered

- **Fold into `20-economic-model.md`.** Rejected: doc 20 is
  operational with an audience of implementers and validators;
  commercial strategy has a different audience (allocators,
  sponsors, partners) and cadence. Folding dilutes both
  audiences and bloats doc 20 past its 3200-token budget.
- **Skip until Phase 2 prep.** Rejected: by Phase 2 prep the
  maintainer is busy with testnet onboarding and reviewer
  engagement. Pre-specifying while bandwidth exists prevents a
  sloppy improvised version later. Crucially, writing the
  strategy surfaced c8–c11 — the foundation needs them
  declared before Phase 2 regardless of when the strategy
  ships.
- **Quantitative survival analysis in the same PR.** Rejected:
  3–5 PR work stream that should not block the strategic
  narrative. The strategic doc establishes *what* the paths
  are; survival analysis answers *whether the numbers work*.
  Sequence them.

## Related

- Spec: [`27-economic-strategy.md`](../spec/27-economic-strategy.md);
  [`00.5-foundations.md`](../spec/00.5-foundations.md) §§ C
  (c8–c11), D, E;
  [`20-economic-model.md`](../spec/20-economic-model.md) —
  operational complement;
  [`26-external-review.md`](../spec/26-external-review.md) —
  pre-Phase-2 review whose scope now includes doc 27;
  [`references.md`](../spec/references.md) — six new entries.
- ADRs: [0007](0007-foundations-gap-fix.md) — C-row H3 format
  precedent; [0009](0009-external-review-plan.md).
- Roadmap: c8 first-evidence at Phase 2 concierge sponsorship;
  c9–c11 first-evidence at Phase 3 mainnet.

---
name: 0005 rigor framework
description: choice to mechanise the 00.5-foundations rigor pattern as a project-wide spec convention with central bibliography, evidence taxonomy, and ratchet CI gate
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0005 — Rigor framework

## Context

[`docs/spec/00.5-foundations.md`](../spec/00.5-foundations.md)
already contains a sophisticated rigor framework — sections C
("Assumptions") and E ("Empirical posture") — distinguishing
proven from bet-on claims, with arXiv / DOI / RFC citations.
But that framework is isolated to one doc. The other 24 spec
docs make design assertions without flagging whether they rest
on proven ground or unproven assumptions, no central
bibliography exists, no schema metadata captures evidence
level, and no CI gate verifies any of it.

The user's framing is sharp: Phase 0 should iterate until the
spec is well-grounded in research, with clear markers wherever
claims are assumptions rather than evidence-backed facts. As
agents do most of the writing in Phase 1+, unproven assumptions
silently encoded in normative HM-REQs become silently encoded
in code; later reversal requires unwinding both.

## Decision

Mechanise the `00.5` pattern as a project-wide standard,
delivered as three sequenced PRs:

1. **This PR** — new `docs/spec/25-rigor-framework.md` defining
   the four-level evidence taxonomy (`well-supported`,
   `reasoned-design`, `assumption`, `tbd`), citation
   conventions (`{ref:slug}` / `[^slug]`), assumption
   admonitions, and the rule for when each level is required;
   new `docs/spec/references.md` central bibliography seeded
   with the ~10 sources already cited; new optional `evidence:`
   field on the spec-doc front-matter schema.
2. **Demo rigor pass** on `00.5-foundations.md` — convert
   inline citations to `{ref:...}`, add `evidence:
   well-supported` to front matter, format C-row assumptions
   with the standard admonition. Companion ADR 0006.
3. **CI gate** `scripts/check_grounding.py` +
   `.github/workflows/grounding.yml` — ratchet-style enforcement
   mirroring `glossary-links.yml`: new `{ref:...}` must resolve;
   coverage of `evidence:` declaration ratchets monotonically
   upward.

Subsequent per-doc rigor passes follow the standard ADR template
defined in PR-1 § "How to add a new normative claim" and ship
one at a time at the maintainer's pace.

## Consequences

- **Positive.** Honesty by default: a reader (human or agent)
  can tell at a glance whether a claim is research-backed,
  reasoned-design, an explicit assumption with an "if false"
  consequence, or a deferred TBD. The bibliography survives URL
  rot and gives a single audit point. The schema field makes
  evidence level *queryable* (find all `assumption`-level docs
  in one grep). The ratchet gate catches regressions without
  blocking PRs that haven't yet been through their rigor pass.
- **Negative.** Adds friction to introducing new normative
  claims — every HM-REQ that rests on empirical-external
  ground now requires a citation or a `00.5 § C` row. That is
  the friction the user explicitly asked for; calibration: the
  framework specifies *only* normative claims need this rigor,
  not narrative prose.
- **Neutral / deferred.** Mechanical citation verification
  (resolving DOIs, archiving arXiv versions) is out of scope;
  the gate verifies internal consistency only. A periodic
  re-validation cadence may be worth adding after several rigor
  passes give a sense of citation drift rate.

## Options considered

- **Per-doc footnotes instead of a central bibliography.**
  Rejected: same source cited from multiple docs would drift in
  format; no audit point; conflicts the HM-REQ-0110
  single-source rule which favours focused canonical homes.
- **Strict CI gate (block PRs with any unbacked claim).**
  Rejected for now: existing inline citations across the spec
  haven't been format-converted; a strict gate on day one would
  block every PR until a sweep happened. Ratchet model lets
  rigor passes ship incrementally without a flag day.
- **Fold the framework into `00.5-foundations.md`.** Rejected:
  `00.5` is about the threats and assumptions of the *subnet
  design*; the rigor framework governs how *every doc* writes.
  Different scopes, different audiences. A separate numbered
  spec doc is the right home.
- **Skip the schema field, infer evidence level from doc
  content.** Rejected: not queryable without parsing every doc;
  brittle; loses the clear "this is the doc author's
  declaration" signal.

## Related

- Source pattern: [`00.5-foundations.md`](../spec/00.5-foundations.md)
  §§ C and E — the existing framework this codifies.
- Spec: [`25-rigor-framework.md`](../spec/25-rigor-framework.md),
  [`references.md`](../spec/references.md),
  [`12-implementation-constraints.md § Documentation
  discipline`](../spec/12-implementation-constraints.md#documentation-discipline).
- Reference implementation for the ratchet gate:
  `scripts/check_glossary_links.py`,
  `.vale/glossary-baseline.json`.
- ADRs: [0004](0004-design-heuristics.md) for the prior
  research-cited ADR shape this one mirrors.

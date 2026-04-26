---
name: 0007 foundations gap fix
description: close the two gaps surfaced by the demo rigor pass (ADR 0006) — F3 polymarket exploit citations and section C row anchors
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0007 — Foundations gap fix

## Context

[ADR 0006](0006-rigor-pass-foundations.md) recorded the first
rigor pass on
[`00.5-foundations.md`](../spec/00.5-foundations.md) and named two
unresolved gaps:

1. **Section A § F3 (oracle corruption)** described two real-world
   Polymarket exploit examples (Ukraine mineral-deal market;
   Paris weather-sensor exploit, ~$37k) without citation. The
   framework requires either a citation or an explicit
   `assumption` flag for empirical-external claims.
2. **Section C** was a markdown table whose rows lacked
   kebab-case slugs. Other docs that wanted to cite a specific
   assumption from the inline `> **assumption: name** —`
   admonition had no per-row anchor to point at; only the loose
   section anchor
   `00.5-foundations.md#c-assumptions-the-defences-require`.

This PR closes both gaps. They surfaced in the demo pass and are
mechanical rather than research-heavy, so they ship as one
cleanup ADR rather than waiting for a per-doc rigor pass.

## Decision

### F3 citations

Both Polymarket exploits had reliable post-mortems available;
both are now cited via `{ref:slug}`:

- **Ukraine mineral-deal market (March 2025).** A UMA
  governance-token whale used three accounts holding 5M tokens
  to cast 25 % of votes and force premature "Yes" resolution on
  a $7M market. UMA later transitioned the oracle to a managed
  variant with whitelisted proposers. Cited as
  `{ref:polymarket-uma-ukraine-2025}` (The Block, 2025-03-26).
- **Paris weather-sensor exploit (April 2026).** A
  battery-powered hairdryer applied to a public Météo France
  sensor at Charles-de-Gaulle airport produced two coordinated
  temperature spikes (21 °C and 22 °C) that won ~$37k across
  two markets. Polymarket relocated the resolution source but
  the underlying single-point-of-failure remains. Cited as
  `{ref:polymarket-paris-weather-2026}` (Le Monde / Euronews,
  2026-04-23).

Both rows are added to
[`references.md`](../spec/references.md). The doc-level
`evidence: assumption` declaration is unchanged — the existence
of these exploits supports F3 as a real threat class, but the
generalisation "the same class of attack applies to any subnet
that defers to a single oracle" is a pattern claim that remains
a `reasoned-design`-level extrapolation.

### Section C — table to H3 subsections

The seven C-rows (C1 through C7) are converted from a single
markdown table into seven H3 subsections, each headed by its
kebab-case slug:

| C-row (old) | H3 anchor (new) |
|-------------|-----------------|
| C1 | `c1-compute-cost` |
| C2 | `c2-llm-paps` |
| C3 | `c3-external-anchor` |
| C4 | `c4-emission-sufficient` |
| C5 | `c5-stake-external` |
| C6 | `c6-maintainer-honest` |
| C7 | `c7-ground-truth-latency` |

Body content is preserved verbatim, restructured as
`**Assumption (CN).**` / `**Defences supported.**` /
`**If false.**` lines. The visible "C1 / C7 / etc." identifier is
retained inside the body so existing prose references like "per
C7" still scan, while the heading slug provides the stable URL
fragment.

[`25-rigor-framework.md`](../spec/25-rigor-framework.md) §
"Assumption-marker conventions" is updated to point its example
admonition at the new per-row anchor format
(`00.5-foundations.md#c7-ground-truth-latency`) rather than the
loose section anchor.

## Consequences

- **Positive.** F3 now satisfies the framework's "empirical-
  external claim needs citation or assumption flag" rule. The
  `> **assumption: c7-ground-truth-latency**` admonition pattern
  the framework documents is now usable end-to-end: every C-row
  has a clean per-row URL fragment, and assumption admonitions
  in other docs can link directly back to the canonical row.
- **Negative.** The C-section grows from ~10 lines (table) to
  ~50 lines (seven H3 subsections × ~7 lines each). The visual
  "scan all assumptions at a glance" benefit of the table
  format is reduced; readers who want a one-look summary now
  need to scroll through the H3s. Acceptable: cross-link
  resolution is the more valuable property.
- **Neutral / deferred.** Future C-row additions follow the
  same H3 pattern; ADR 0006's recommendation that the
  `00.5 § C` section auto-generate a summary table from H3s
  could land as a follow-up if the at-a-glance view turns out
  to be missed.

## Related

- [ADR 0005](0005-rigor-framework.md) — rigor framework.
- [ADR 0006](0006-rigor-pass-foundations.md) — the audit that
  surfaced both gaps.
- Spec: [`00.5-foundations.md`](../spec/00.5-foundations.md)
  §§ A § F3 and C; [`25-rigor-framework.md`](../spec/25-rigor-framework.md)
  § "Assumption-marker conventions";
  [`references.md`](../spec/references.md) (two new rows).

---
name: 0006 rigor pass foundations
description: audit findings and conversion record for the first rigor pass — applying the framework to docs/spec/00.5-foundations.md
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0006 — Rigor pass on `00.5-foundations.md`

## Context

[`docs/spec/25-rigor-framework.md`](../spec/25-rigor-framework.md)
landed in PR-1 of the rigor-hardening sequence (ADR 0005). This
ADR records the first rigor pass — applied to
[`00.5-foundations.md`](../spec/00.5-foundations.md), the doc
whose informal pattern the framework codifies. The pass proves
the framework is mechanical to apply and seeds the bibliography
with the citations `00.5` already carries.

## Decision

Convert every inline citation in `00.5-foundations.md` to the
`{ref:slug}` form resolving to
[`references.md`](../spec/references.md), and declare the
doc-level `evidence:` field. The conversion is purely format —
no claim text changes, no citations added or removed.

## Audit findings

### What was already grounded

- **Section A § F1** cited two sources inline (arXiv:2507.02951
  on Bittensor stake concentration; an Inference Labs 2025 blog
  on weight-copy mitigations).
- **Section B § D2.1 / D2.4** cited the JPE 2024 p-hacking study
  with DOI.
- **Section B § DS.1** cited the OSC 2015 replication-crisis
  Science paper with DOI.
- **Section E § "What's reasonably well-supported"** cited the
  same JPE 2024 paper, plus a Behavior Research Methods 2024
  paper, plus an arXiv preprint on LLM-as-judge reliability.
- Total: **7 inline citations** spanning **6 distinct external
  sources** (one source cited twice).

All six sources were seeded into `references.md` in PR-1; this
pass converts the inline forms to brace-form `{ref:slug}`
references.

### What was reformatted

| inline form | converted to |
|-------------|--------------|
| `[Bittensor Protocol critical analysis, arXiv 2507.02951, July 2025](https://arxiv.org/html/2507.02951v1)` | `{ref:bittensor-stake-2025}` |
| `[Inference Labs, 2025](https://blog.inferencelabs.com/...)` | `{ref:inference-labs-weight-copy-2025}` |
| `[JPE 2024 on 15,992 test statistics](https://www.journals.uchicago.edu/doi/10.1086/730455)` (twice) | `{ref:phacking-jpe-2024}` |
| `[replication-crisis literature](https://www.science.org/doi/10.1126/science.aac4716)` | `{ref:replication-osc-2015}` |
| `[Behavior Research Methods 2024](https://link.springer.com/article/10.3758/s13428-023-02277-0)` | `{ref:behavior-research-2024}` |
| `[LLM-as-judge empirical study, 2025](https://arxiv.org/html/2506.13639v1)` | `{ref:llm-judge-2025}` |

### Doc-level `evidence:` declaration

`00.5-foundations.md` was annotated `evidence: assumption`. Per
the framework rule "one assumption-level claim drops the whole
doc to assumption", this is correct: section E explicitly admits
five "open bets" the design rests on (token-funded reproducible
science at scale, validator-concentration defences on hostile
Bittensor, long-tail research compatible with epoch-paid
validators, the white-hat-as-hypothesis recursion, agent-first
operation actually working). Honest declaration over inflated
claim.

### Newly-discovered gaps

The pass surfaced two grounding gaps that were not addressed by
the conversion (deferred to follow-up rigor work):

1. **Section A § F3 (oracle corruption).** The Polymarket
   exploit examples (Ukraine mineral-deal market; Paris
   weather-sensor ~$37k) are factual claims about real-world
   exploits but carry no citation. They are well-known industry
   facts, but the framework requires either a citation or an
   `assumption` flag. Suggested fix in a follow-up: cite the
   relevant post-mortems (Polymarket UMA dispute reports) or
   re-flag as `assumption: oracle-exploit-precedent`.
2. **Section C § C-rows.** The current table format gives each
   assumption a `C1`…`C7` ID but no kebab-case slug for inline
   admonition cross-linking from other docs. Other docs that
   want to use the standard `> **assumption: name** — ...`
   block pointing back to a specific row currently have to use
   the loose section anchor
   `00.5-foundations.md#c-assumptions-the-defences-require`
   rather than a per-row anchor. A follow-up rigor pass should
   either add `name:` slugs as a column or convert the table
   into per-row H3 subsections that GitHub anchors
   automatically.

Both are noted for follow-up; neither blocks PR-3 (the CI gate)
since the gate only enforces what the framework currently
specifies.

## Consequences

- **Positive.** `00.5-foundations.md` is now the worked example
  of the framework. Every external source it cites lives at a
  stable bibliography ID; the doc's empirical posture is
  declared in front matter and queryable. URL rot in the
  citation now affects exactly one row (in `references.md`),
  not seven inline links.
- **Negative.** `{ref:slug}` is not a clickable link in standard
  markdown renderers; readers see the bare brace form until the
  CI gate (PR-3) ships and a future enhancement adds rendered
  resolution (e.g., a pre-render step or a dedicated viewer).
  Acceptable for a spec audience that's reading the source.
- **Neutral / deferred.** Two grounding gaps surfaced but not
  closed in this PR (F3 oracle exploits, C-row anchors).
  Captured above.

## Related

- ADR 0005 — rigor framework rationale.
- Spec: [`00.5-foundations.md`](../spec/00.5-foundations.md),
  [`25-rigor-framework.md`](../spec/25-rigor-framework.md),
  [`references.md`](../spec/references.md).
- PR-3 (next): CI gate `scripts/check_grounding.py` enforcing
  `{ref:slug}` resolution and ratcheting `evidence:`
  declaration coverage.

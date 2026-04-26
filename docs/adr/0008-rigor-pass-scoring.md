---
name: 0008 rigor pass scoring
description: audit findings and conversion record for the second rigor pass — applying the framework to docs/spec/06-scoring.md
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0008 — Rigor pass on `06-scoring.md`

## Context

The second per-doc rigor pass under
[`docs/spec/25-rigor-framework.md`](../spec/25-rigor-framework.md)
(ADR 0005). `06-scoring.md` is the load-bearing math doc — every
component formula, every weight, every bound, every statistical
test that drives the validator's deterministic scoring lives
here. It carried zero external citations before this pass.

Targeted as the first content-rich rigor pass (after the
foundations conversion in PR-A) because (a) statistical methods
have clean textbook citations available, (b) the doc is small
enough to audit in a single sitting (~320 LoC, 9 normative
claims), and (c) it's the most-cross-referenced contract doc —
every other module touches scoring.

## Decision

Apply the framework to `06-scoring.md`. The doc-level evidence
posture is **`reasoned-design`**: most normative claims are
internal-mechanism design choices with stated rationale; the
statistical-test references are now grounded in the original
papers; no claim required an `assumption` flag because the few
empirical-feeling claims (hardware-cost budgets, block-height
uncontrollability) already carry inline rationale that resolves
the "because Y" clause without invoking unproven world-state.

## Audit findings

### Claims by evidence level

| claim | level | grounding |
|-------|-------|-----------|
| HM-REQ-0020 composite formula | reasoned-design | weights are governance values; formula structure is a design choice with stated component-by-component rationale |
| HM-INV-0010 composite bounds | reasoned-design | mathematical consequence of the formula |
| HM-INV-0011 novelty non-increasing | reasoned-design | design choice; first-mover incentive |
| HM-INV-0012 improvement bounds | reasoned-design | mathematical consequence of `min(1.0, observed/target)` |
| HM-REQ-0021 novelty tiebreak ordering | reasoned-design | block-height + extrinsic-index + lex-SS58 chain — fully deterministic |
| HM-REQ-0060 external-verifiability anchor | reasoned-design | inherits empirical grounding from `00.5 § F1` (cited via `{ref:bittensor-stake-2025}`); the anchor rule is the design response |
| Welch's t-test (line 232) | well-supported | now cites `{ref:welch-1947}` |
| BCa bootstrap (line 234) | well-supported | now cites `{ref:efron-tibshirani-1993}` |
| Mann–Whitney U (line 236) | well-supported | now cites `{ref:mann-whitney-1947}` |

The doc-level value is `reasoned-design` because per the
framework, doc-level is the *ceiling* — every normative claim
must be at-or-above the declared level. With three statistical
tests at `well-supported` and the rest at `reasoned-design`, the
doc as a whole declares the lower bound: `reasoned-design`.

### What was reformatted

Only the "Statistical tests" section. Each named test (Welch's
t-test, bootstrap with BCa CIs, Mann–Whitney U) now carries an
inline `{ref:slug}` resolving to the original paper. The
implementation-tolerance reference (1e-9 against scipy.stats)
got an explicit cross-link to T-P1-012 for traceability.

### Newly-discovered grounding gaps

Reviewed during the pass; none required a new admonition or
assumption flag:

1. **Hardware cost budgets** (lines 168–177). The USD figures
   (e.g., `cpu-small: $0.10/$0.05`) are empirical insofar as
   they reflect spot-market pricing as of 2026, but the doc
   explicitly labels them "Initial values, revisit after
   Phase 2" — that is itself the stated rationale, and the
   "revisit after Phase 2" phrase is the named trigger. They
   are governance values like the score weights, not research
   claims requiring backing.
2. **Block-height game-resistance** (line 153). "Chain block
   height cannot be chosen by the miner beyond ±a few blocks
   of inclusion latency" is an empirical claim about Bittensor
   chain mechanism, but the surrounding text gives the chain-
   determinism rationale ("validators agree on novelty without
   coordination"); demonstrable from inspection of any
   Substrate-based chain. Treated as `reasoned-design`.
3. **Reproduction hard-zero rule** (line 81–83). "A submission
   with even one out-of-tolerance seed receives a hard zero…
   This is deliberate: partial reproduction rewards noisy or
   dishonest miners." The "deliberate" + game-theoretic
   rationale resolves the "because Y" clause without
   empirical backing.

### What was NOT done in this pass

- No structural changes to `06-scoring.md` body (no claims
  rewritten, no formulas changed, no thresholds adjusted).
- No citation added for the SN42 oracle adapter (deferred to
  the rigor pass on `18-oracle.md` — that doc is the canonical
  home for oracle-class claims).
- No rerun-fraction citation. The 40% number lives in
  `05-validator.md`, not here. It will be addressed in the
  `05-validator` rigor pass.

## Consequences

- **Positive.** Every statistical test in the scoring pipeline
  now resolves to its original paper. The doc-level
  `evidence: reasoned-design` declaration is honest: scoring
  is not "research-backed" as a whole (no paper proves the
  composite-formula coefficients), but every individual claim
  has either a citation or a stated rationale legible from
  surrounding text.
- **Negative.** The doc-level posture is `reasoned-design`,
  not `well-supported`, even after this pass. That's an
  honest declaration but means the scoring formula itself
  remains a design choice the maintainer is on the hook to
  defend; future PRs that change weights or component
  structures should still cite or flag novel claims.
- **Neutral / deferred.** The 40 % rerun-fraction sampling
  rationale needs a citation when `05-validator.md` gets its
  pass. Likely the ML-reproducibility literature mentioned in
  the original sizing report (Pierpont et al., or similar).

## Related

- ADR 0005 — rigor framework.
- ADR 0006 — first rigor pass (foundations).
- ADR 0007 — foundations gap fix.
- Spec: [`06-scoring.md`](../spec/06-scoring.md),
  [`25-rigor-framework.md`](../spec/25-rigor-framework.md),
  [`references.md`](../spec/references.md) (three new rows for
  Welch 1947, Mann–Whitney 1947, Efron–Tibshirani 1993).
- Baseline: `.vale/grounding-baseline.json` — `06-scoring.md`
  is removed from the list.

---
name: external review
description: scope, criteria, and output format for a one-shot adversarial review of the foundation by an outside reviewer
tokens: 1700
load_for: [governance, review]
depends_on: ["00.5"]
kind: contract
evidence: reasoned-design
---

# 26 — External adversarial review

In-house threat modelling has known blind spots: the people who
designed a defence find it harder to spot the case where their
defence doesn't actually work. The standing white-hat programme
in [`22-security-bounty.md`](22-security-bounty.md) addresses
*ongoing* discovery during operation. This doc specifies a
*one-shot* adversarial review of the foundation before Phase 2
ships — the moment when defences become hard to revise because
external actors are now using them.

The review's goal is to find at least one of:

- A 9th threat the in-house process missed.
- A failure mode where two F-rows in
  [`00.5 § A`](00.5-foundations.md#a-the-eight-threats-the-design-must-survive)
  interact in a way no single F-row anticipates.
- A `00.5 § C` assumption that's stronger than admitted (a "C-row
  that's actually a wish").
- A defence in
  [`00.5 § B`](00.5-foundations.md#b-defences-derived-from-each-threat)
  that doesn't actually mitigate the named threat under stated
  assumptions.
- A scoring or [oracle](18-oracle.md) composition rule that
  admits an attack the threat-model rows don't cover.

A null result (the reviewer finds nothing new) is itself
information — it's evidence the in-house process is rigorous,
weighted by the reviewer's track record.

## Scope

### In scope

- [`docs/spec/00.5-foundations.md`](00.5-foundations.md) — the
  eight threats, the defences derived from them, the assumptions
  the defences require, and what the mechanism gives up.
- [`docs/spec/16-threat-model.md`](16-threat-model.md) — the
  full T-NNN catalogue and per-row mitigations.
- [`docs/spec/21-adversarial-simulator.md`](21-adversarial-simulator.md)
  — the simulator contract; reviewers assess whether this
  contract, when implemented, would actually exercise the
  threats it claims to.
- [`docs/spec/22-security-bounty.md`](22-security-bounty.md) —
  the white-hat programme; reviewers assess whether the embargo
  gate (HM-REQ-0100) and the
  [security-hypothesis](02-hypothesis-format.md) recursion are
  well-formed.

### Out of scope

- Implementation code under `src/hypotheses/` — that's a
  different review track (a code audit follows once Phase 1 is
  largely done).
- Economic-parameter calibration (weights, deferral period,
  emission curves) — that's a governance review track.
  Reviewers can flag a parameter that is structurally
  load-bearing in a way the [spec](README.md) doesn't acknowledge,
  but parameter values themselves are not the question.
- The vision and research framing in
  [`/VISION.md`](../../VISION.md) and the topology-evolution
  research bet in `00.5 § E` — those are entrepreneurial
  bets, not security claims.

## What we want

Each finding carries:

- **Section reference.** The exact spec anchor the finding
  applies to (e.g. `00.5#f1--stake-concentrated-validator-collusion`,
  `16#t-015`, `00.5#c7-ground-truth-latency`).
- **Severity.** One of:
  - `informational` — the finding is correct but does not
    change the defence calculus.
  - `minor` — the finding identifies a defence weakness that
    requires a documentation tightening or a `00.5 § C`
    assumption update.
  - `major` — the finding identifies a defence weakness that
    requires a new HM-REQ or HM-INV, or invalidates an existing
    one.
  - `blocker` — the finding identifies a failure mode that
    must be addressed before Phase 2 launches with real value
    at stake.
- **Proposed defence shape** (for `minor` / `major` /
  `blocker`). Not a full design, but enough that the maintainer
  can convert into a spec PR.
- **Evidence level.** Per
  [`25-rigor-framework.md`](25-rigor-framework.md): is this a
  cited claim, a reasoned-design argument, or an empirical
  assumption the reviewer is making? The framework's evidence
  taxonomy applies to the review itself.

The output is a single document keyed by section reference,
delivered as a markdown file or PDF. The maintainer triages each
finding into a follow-up PR or an ADR.

## Reviewer profile

The reviewer brings at least two of:

- **Security background.** Cryptographic protocol review,
  blockchain audit, or red-team operations experience.
- **Mechanism-design background.** Familiarity with incentive
  design, adversarial market dynamics, or game-theoretic
  analysis of distributed systems.
- **Bittensor / decentralised-AI familiarity.** Knowledge of
  YUMA consensus, dTAO, [validator](05-validator.md) and
  [miner](04-miner.md) economics, or prior subnet exploits.
- **Replication-crisis / meta-science familiarity.** Background
  in [preregistration](01-glossary.md#preregistration),
  p-hacking, publication bias, or research
  reproducibility.

The reviewer signs a confidentiality agreement covering any
finding flagged `major` or `blocker` until the embargo period in
[`22-security-bounty.md`](22-security-bounty.md) elapses or the
finding lands as a public spec PR — whichever comes first.

The maintainer commits to:

- Acknowledging every finding within 14 days.
- Either accepting (with a follow-up PR opened) or formally
  rejecting (with reasoning in an ADR) every finding within 60
  days.
- Crediting the reviewer in the resulting PRs and any
  associated security advisory.

## Trigger condition

The review ships **before** Phase 2 onset. Phase 2 is defined in
[`11-roadmap.md`](11-roadmap.md) as testnet subnet with ≥3
external miners and ≥2 external validators. Until that
threshold, the spec is still revisable without coordination
cost; after it, every defence change has to coordinate with
external operators.

A second review before mainnet (Phase 3) is a governance
decision, not a Phase-0 commitment.

## Cheaper parallel variant: LLM red-team ensemble

Until a human reviewer is engaged, an LLM ensemble pass is the
cheapest way to surface candidate findings. Approach:

1. Load `00.5-foundations.md`, `16-threat-model.md`, and the
   role prompt in
   [`agents/prompts/red-team-system.md`](../../agents/prompts/red-team-system.md)
   into N independent frontier-model sessions (Claude Opus,
   GPT-5, Gemini 2.5 Pro, etc.).
2. Each session is asked to produce one of the five findings
   shapes from §"What we want".
3. Findings are deduplicated and triaged by the maintainer.
   Anything surviving triage becomes a candidate for the
   eventual human reviewer.

The ensemble is *complementary* to the human review, not a
substitute. LLMs share training-data blind spots; a human with
real-world incident experience finds different things. Ship both.

## Why not fold this into 22

[`22-security-bounty.md`](22-security-bounty.md) describes an
*ongoing* programme keyed on community discovery during
operation. This doc describes a *one-shot* pre-launch review by
an invited expert. Different audiences (one external, one
broad), different cadences (one-shot vs continuous), different
output formats (single document vs hypothesis-shaped advisory).
Folding them would dilute both. The two interact: any finding
the external reviewer surfaces that meets the criteria in
HM-REQ-0100 also lands as a security-hypothesis on the registry
once embargo elapses.

## References

- [`00.5-foundations.md`](00.5-foundations.md) — the doc the
  review primarily targets.
- [`16-threat-model.md`](16-threat-model.md) — the T-NNN
  catalogue.
- [`21-adversarial-simulator.md`](21-adversarial-simulator.md)
  — the simulator contract reviewers assess.
- [`22-security-bounty.md`](22-security-bounty.md) — the
  ongoing programme this review complements.
- [`25-rigor-framework.md`](25-rigor-framework.md) —
  the evidence taxonomy the review's findings adopt.
- [`docs/adr/0009-external-review-plan.md`](../adr/0009-external-review-plan.md)
  — rationale for this doc.

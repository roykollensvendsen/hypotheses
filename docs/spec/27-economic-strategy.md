---
name: economic strategy
description: investment thesis, revenue paths beyond Bittensor emission, phase-by-phase commercial trajectory, comparable-model evidence
tokens: 2400
load_for: [governance, review]
depends_on: ["00.5", "07", "20", "11"]
kind: contract
evidence: reasoned-design
---

# 27 — Economic strategy

[`20-economic-model.md`](20-economic-model.md) treats the
**operational** economics (emissions, parameters, governance,
Sybil arithmetic, incentive compatibility) but leaves the
**commercial** story out: how investors form a thesis on this
subnet, and how revenue flows from outside the Bittensor block
reward. This doc closes that gap — investors and external
sponsors form their own theses regardless of whether the
[spec](README.md) articulates one; the choice is between
articulating it explicitly so it can be reviewed and
pressure-tested, or letting it float as folklore.

## A. Purpose & scope

**This doc covers.** The investment thesis for someone
allocating dTAO; the catalogue of non-Bittensor revenue paths
the subnet adds across Phase 2–3, with comparable-model
evidence and the assumptions each rests on; the phase-by-phase
trajectory matching [`11-roadmap.md`](11-roadmap.md); a
four-row comparables matrix.

**Explicitly out of scope** (see [§ F](#f-out-of-scope) for
detail): quantitative survival analysis (separate work
stream); treasury / fiduciary structure (until DAO
incorporation, Phase 3+); TAO / Alpha price prediction
(inherited exclusion from
[`20-economic-model.md § Out of scope`](20-economic-model.md#out-of-scope));
empirical validation of c8–c11 (Phase 2+ retrospectives
generate it); external-reviewer booking (gated by
[`26-external-review.md`](26-external-review.md)).

This doc is `kind: contract, evidence: reasoned-design`.
Strategic claims rest on comparable-model evidence and stated
rationale, not on equilibrium proofs. The four revenue paths
each rest on a specific commercial assumption (`c8`–`c11`)
declared in
[`00.5 § C`](00.5-foundations.md#c-assumptions-the-defences-require).

## B. The dTAO investment thesis

Bittensor's dynamic-TAO mechanism (live across the network
since 2025) gives every subnet its own Alpha token; emissions
flow from net TAO inflows ("Taoflow") rather than
[validator](05-validator.md)-set weighting alone
({ref:bittensor-dtao-whitepaper-2025}). Total Alpha-token
market cap reached ~$1.12B as of March 2026, ≈27% of TAO's
own cap; 128 subnets are active
({ref:bittensor-grayscale-2025}). An allocator picking this
subnet's Alpha is making three coupled bets:

1. **Durable findings produce a self-reinforcing emission
   story.** Each preregistered, reproduced, externally-anchored
   finding adds to a corpus that research labs, pharma, and ML
   benchmark vendors want access to; inflows track real value
   capture rather than speculative narrative.
2. **The adversarial-first foundation in
   [`00.5-foundations.md`](00.5-foundations.md) holds.** A
   leveraged bet on the design surviving F1–F6 under live
   operation; if the foundation fails, the corpus is noise.
3. **The commercial revenue paths in § C come online.**
   Without them, the subnet stays a pure infrastructure bet
   priced on emission-share growth alone.

**Why this subnet specifically.** Permissionless scientific
market with adversarial-first defences (the threat-model and
rigor-framework discipline of
[`16-threat-model.md`](16-threat-model.md) and
[`25-rigor-framework.md`](25-rigor-framework.md) is unusual
across subnets); D1.1 external-verifiability anchor rejects
consensus-only hypotheses at scoring time; falsification pays
(DS.1) so a correctly-refuted
[hypothesis](02-hypothesis-format.md) earns rigor +
reproduction + novelty, accumulating the negative findings
historically missing from the literature
({ref:replication-osc-2015}).

**Why this thesis differs from the standard Bittensor one.**
Most subnets pitch on inference / training throughput plus
emission share, in continuous re-pricing. This subnet's pitch
is durability: preregistered + reproduced findings compound
because they retain meaning — closer to an academic-publishing
/ patent-registry analogue than a teraflops marketplace.

## C. Non-Bittensor revenue paths

Four paths, sequenced across Phases 2 and 3. Each lists status,
mechanism, comparable evidence, and the underlying commercial
assumption from
[`00.5 § C`](00.5-foundations.md#c-assumptions-the-defences-require).

### C.1 Sponsored hypotheses

**Status.** Phase 2 onset; aspirational at Phase 1.
**Mechanism.** External organisations (research labs, pharma,
AI labs, foundations) fund specific questions — TAO bridged
from fiat or direct sponsorship of a hypothesis with a bounty
payable on settlement. Bounty supplements emission; miners
earn both. The hypothesis follows the standard
[preregistration](01-glossary.md#preregistration) +
reproduction discipline — sponsorship buys attention, not
score control.
**Comparable.** ResearchHub's RSC bounty + tip on Base ERC-20:
~$1.9M distributed, $7M raised across three rounds, partnered
with Endaoment for institutional flows
({ref:researchhub-tokenomics-2025}). The mechanism shape is
validated; the open question is whether this subnet's
preregistration discipline attracts a different sponsor
profile or repels them.

> **assumption: c8-sponsorship-demand** — external
> organisations will pay for specific scientific questions
> when the cost / answer-quality ratio is favourable.
> **If false:** revenue path 3.1 collapses; the subnet remains
> funded by Bittensor emissions alone.
> See [00.5 § c8-sponsorship-demand](00.5-foundations.md#c8-sponsorship-demand).

### C.2 Registry / data licensing

**Status.** Phase 3 (mainnet); aspirational earlier.
**Mechanism.** The corpus of preregistered + reproduced ML
findings is licensable IP under three tiers: public read
(every settled hypothesis on-chain, free); bulk export with
provenance (research lab or pharma replication library
subscribes to a periodic, schema-stable export with
cryptographic provenance attestation); targeted partnership
(counterparty engages a hypothesis or hypothesis-cluster with
right of first refusal, mirroring the IP-NFT model).
**Comparable.** VitaDAO's IP-NFT model: $55.8M treasury (Jan
2026), $4.7M deployed across 31 projects, Gero spun out with a
$1B+ Chugai partnership, Turn.bio licensed $300M+ to HanAll
({ref:vitadao-pfizer-gero-2025}). Closest direct analogue to
registry-as-licensable-IP.

> **assumption: c9-registry-ip-value** — a corpus of
> preregistered + reproduced findings has licensable IP value.
> **If false:** revenue path 3.2 collapses; the corpus remains
> a public good without monetisation.
> See [00.5 § c9-registry-ip-value](00.5-foundations.md#c9-registry-ip-value).

### C.3 Reproducibility-as-a-service

**Status.** Phase 2 case study; Phase 3 productised.
**Mechanism.** Validators already do reruns as standard
operation (see [`05-validator.md`](05-validator.md)). An
external counterparty (journal, regulator, industry consortium)
engages validators for an audit-with-SLA above in-subnet
scoring: defined sample size, fixed turnaround, signed report
keyed by validator hotkeys with known stake. Per-audit pricing;
fees split between subnet treasury and participating validators.
**Comparable.** The audit-firm landscape for code (Trail of
Bits, NCC Group, Cure53 and peers) demonstrates
willingness-to-pay for third-party assurance with named
liability; the ML-reproducibility variant is less developed —
the path with the thinnest external precedent.

> **assumption: c10-audit-demand** — external researchers /
> publishers / industry pay for ML reproducibility audits
> above what in-subnet scoring already provides.
> **If false:** revenue path 3.3 collapses; validators do
> reruns purely as part of in-subnet scoring.
> See [00.5 § c10-audit-demand](00.5-foundations.md#c10-audit-demand).

### C.4 Credentialing / reputation

**Status.** Phase 3+; speculative.
**Mechanism.** Miners accumulate machine-verifiable track
records — reproduced-findings count, Brier score across
settled hypotheses, refuted-vs-confirmed ratio — public,
signed, tied to hotkey identity. External job markets,
academic institutions, or industry consortia treat the record
as a referenceable credential ("trusted ML engineer with N
reproduced findings"); the subnet earns referral or framework
fees.
**Comparable.** Gitcoin Passport (machine-verifiable reputation
across heterogeneous sources), ENS reputation graphs (on-chain
identity travelling outside its origin system), academic
citation indices (h-index, ORCID — machine-aggregable
scholarly metrics carrying weight in hiring and grant
decisions). None is a direct analogue; the path with the most
extrapolation.

> **assumption: c11-credential-demand** — external job markets
> / institutions treat verified [miner](04-miner.md) track
> records as a referenceable credential. **If false:** revenue
> path 3.4 collapses; miner reputation remains internal to the
> subnet.
> See [00.5 § c11-credential-demand](00.5-foundations.md#c11-credential-demand).

## D. Phase-by-phase trajectory

Aligned with [`11-roadmap.md`](11-roadmap.md). Each phase
tightens the investment thesis from "infrastructure bet"
toward "earnings-backed valuation."

**Phase 1 — Offline reference.** No revenue; single-operator
local round-trip. Investment thesis: pure infrastructure bet.
Evidence generated: whether the mechanism is mechanically
sound. No commercial signal.

**Phase 2 — Testnet.** C.1 (sponsored hypotheses) goes live
as a concierge integration with one or two external sponsors,
manually onboarded; C.3 (reproducibility-as-a-service) starts
as a single case study with one external counterparty and one
audit, lessons captured in an ADR; C.2 and C.4 remain
aspirational. Investment thesis: pre-revenue plus first
earnings signal — concierge sponsorship demonstrates whether
c8 survives contact with a real counterparty. A null result
(no sponsor materialises) is itself information that triggers
an ADR per
[`00.5 § How this document evolves`](00.5-foundations.md#how-this-document-evolves).
Evidence generated: first commercial datapoint; the two-week
stable-operation criterion (per
[`11-roadmap.md § Phase 2`](11-roadmap.md#phase-2--testnet-subnet))
validates the mechanism; sponsorship outcome validates or
falsifies c8.

**Phase 3 — Mainnet.** All four paths live: C.1 productised
(self-service surface replacing concierge); C.2 tiered
licensing rolled out per the VitaDAO IP-NFT model, first
targeted-partnership engagement is the analogue of VitaDAO's
Gero / Chugai spinout; C.3 productised audit product, SLAs
and pricing public; C.4 first external partnership with a
job market or academic institution. Investment thesis:
earnings-backed valuation — dTAO allocators model expected
revenue from each path against its underlying commercial
assumption. Evidence generated: each path either compounds
(distinguishing revenue line) or atrophies (triggers an ADR
moving its `c-NN` assumption to
[`00.5 § E`](00.5-foundations.md#e-empirical-posture--whats-proven-vs-whats-a-bet)
"open bets that failed").

## E. Comparables matrix

| comparable | scale (latest) | mechanism | what this subnet borrows |
|------------|----------------|-----------|--------------------------|
| ResearchHub / RSC ({ref:researchhub-tokenomics-2025}) | ~$1.9M distributed; $7M raised; Endaoment partnership | ERC-20 bounty + tip on Base | Sponsored-hypothesis mechanism (C.1) |
| VitaDAO / BIO Protocol ({ref:vitadao-pfizer-gero-2025}) | $55.8M treasury; $4.7M deployed across 31 projects; $1B+ Gero spinout; $300M+ Turn.bio licensing | IP-NFT model — exclusive licensing of decentralised research IP | Registry / data licensing (C.2) |
| BIO Protocol / DeSci ecosystem ({ref:bio-protocol-desci-2026}, {ref:desci-berkeley-cmr-2025}) | ~50 active projects; ~$60M+ combined funding; ecosystem cap $329M (March 2026) | Replication-bounty mechanisms emerging across multiple projects | Validates the broader category — DeSci durable enough to host this commercial model |
| ClawdLab / Science Beach (no archived report yet) | Prototype; not productised | Fully autonomous AI-scientist-swarm research orgs | Validates the agent-first posture; comparable for c11 (credentialing) |

The four span the maturity range: ResearchHub demonstrates the
bounty mechanism at production scale; VitaDAO demonstrates IP
licensing at industry scale; the DeSci ecosystem demonstrates
that decentralised science is a durable category; AI-scientist-
swarm prototypes show the agent-first posture is not unique
to this subnet.

## F. Out of scope

- **Quantitative survival analysis.** Unit-economics modelling
  of miner / validator break-even, sensitivity tables for
  cost-budget obsolescence, Nash-equilibrium analysis,
  fixed-point modelling of participation rates. Separate 3–5
  PR work stream tracked against Phase 3 exit criteria in
  [`11-roadmap.md`](11-roadmap.md); does not block this PR.
- **Treasury / fiduciary structure.** Until DAO incorporation
  (Phase 3+), at which point the doc gains a section on
  treasury governance for non-TAO revenue.
- **TAO / Alpha price prediction.** Inherited exclusion from
  [`20-economic-model.md § Out of scope`](20-economic-model.md#out-of-scope);
  mechanism design is price-agnostic.
- **Empirical validation of c8–c11.** Phase 2+ retrospective
  ADRs generate the data, not this doc.
- **Booking the external reviewer.** Engagement gated by
  [`26-external-review.md`](26-external-review.md)'s trigger
  condition.

## G. Open questions

Each lands as an ADR when it resolves — positive or negative.

1. **Phase-2-onset trigger for C.1.** Coupled to "≥3 external
   miners and ≥2 external validators" per
   [`11-roadmap.md`](11-roadmap.md), with maintainer discretion
   to onboard the first concierge sponsor earlier when a
   counterparty is ready. Maintainer judgement at Phase 2
   entry, recorded in an ADR.
2. **Bounty splits.** Miner who settles / validators who
   reproduce / subnet treasury. Placeholder 60 / 30 / 10;
   deferred to the first concierge integration.
3. **Registry-licensing tier prices.** Public read free;
   bulk-export and targeted-partnership pricing deferred to
   Phase 3 launch ADR.
4. **Audit-product SLA shape.** Sample size, turnaround,
   liability framework deferred to the Phase 2 case study's
   retrospective ADR.
5. **Credentialing partnership format.** Job market vs
   academic institution vs industry consortium; first partner
   determines the first surface. Deferred to Phase 3+.

## H. References

[`00.5-foundations.md`](00.5-foundations.md) §§ A, C, D — the
foundation; C-rows c8–c11 declare the commercial assumptions.
[`07-incentive.md`](07-incentive.md), [`11-roadmap.md`](11-roadmap.md),
[`20-economic-model.md`](20-economic-model.md) (operational
complement), [`22-security-bounty.md`](22-security-bounty.md),
[`26-external-review.md`](26-external-review.md),
[`docs/adr/0010-economic-strategy.md`](../adr/0010-economic-strategy.md).
External: {ref:bittensor-grayscale-2025},
{ref:bittensor-dtao-whitepaper-2025},
{ref:researchhub-tokenomics-2025}, {ref:vitadao-pfizer-gero-2025},
{ref:desci-berkeley-cmr-2025}, {ref:bio-protocol-desci-2026}.

## Self-audit

Done when: each path in § C carries status / mechanism /
comparable / `> **assumption:**` resolving to a `c8`–`c11` row;
§ D names path-per-phase and evidence; § E cites four
comparables with scale numbers; § F lists the five out-of-scope
items; cross-refs resolve under
`scripts/check_spec_consistency.py` and `check_grounding.py`.

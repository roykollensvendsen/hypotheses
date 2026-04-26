---
name: treasury
description: pre-DAO custody, operating-cost catalogue, and transition contract for non-TAO revenue and operational spend
tokens: 1800
load_for: [governance, review]
depends_on: ["00.5", "11", "27"]
kind: contract
evidence: reasoned-design
---

# 28 — Treasury

[`27-economic-strategy.md`](27-economic-strategy.md) names four
non-Bittensor revenue paths — sponsored hypotheses (each one a
preregistered [hypothesis](02-hypothesis-format.md) with a
bounty), registry licensing, reproducibility-as-a-service,
credentialing. Each implies a counterparty paying the *subnet*.
The subnet is not yet a legal entity; nothing in the
[spec](README.md) says where that money lands or who controls
it. This doc closes that gap for the pre-DAO period and names
the transition contract at Phase 3 DAO incorporation.

It also catalogues the **operational costs** the spec already
implies (cost-table USD refresh, SLI tooling, audit-product
launch, sponsorship concierge integration) and names where the
money to pay them comes from.

## A. Scope

**This doc covers.** Pre-DAO custody (the multisig +
maintainer-attestation contract), the operating-cost catalogue,
the transition contract at Phase 3 incorporation, and the
audit posture (what the maintainer must publish about treasury
state).

**Out of scope.**

- **Concrete multisig signers / wallet addresses.** Operational,
  recorded in
  [`docs/adr/0014-treasury-pre-dao.md`](../adr/0014-treasury-pre-dao.md)
  rather than the spec.
- **Tax / legal jurisdiction.** Maintainer's responsibility per
  [`GOVERNANCE.md`](../../GOVERNANCE.md); the spec does not
  prescribe a domicile.
- **Investment thesis or revenue mechanics.** Those live in
  [`27-economic-strategy.md`](27-economic-strategy.md); this
  doc is custody-and-spend only.

`kind: contract, evidence: reasoned-design`. Pre-DAO custody is
a design choice, not a research finding. The
[c12-pre-dao-custody](00.5-foundations.md#c12-pre-dao-custody)
assumption captures the bet that maintainer-multisig custody is
acceptable to the first sponsors.

## B. Custody contract (pre-DAO)

Until Phase 3 DAO incorporation, the subnet has no legal entity
of its own. Funds the subnet receives — sponsorship payments
under [`27 § C.1`](27-economic-strategy.md#c1-sponsored-hypotheses),
audit fees under
[`27 § C.3`](27-economic-strategy.md#c3-reproducibility-as-a-service),
or any other path that lands money before Phase 3 — are held
under the **maintainer-multisig + attestation** model:

1. **Multisig wallet.** A 2-of-3 multisig holds all non-TAO
   revenue. The three keys are: the maintainer's primary
   identity key, a second maintainer-controlled hardware-wallet
   backup, and a recovery key held by an external trustee
   (named in the wallet-bootstrap ADR, not in the spec).
2. **Attestation.** Every quarterly cycle the maintainer
   publishes a signed attestation listing: opening balance,
   inflows by counterparty + path, outflows by line item,
   closing balance. Attestations land as ADRs under
   [`docs/adr/`](../adr/) named
   `NNNN-treasury-attestation-YYYY-QN.md`.
3. **No commingling.** Treasury funds never enter the
   maintainer's personal wallets. A breach of this rule is a
   governance incident under
   [`GOVERNANCE.md`](../../GOVERNANCE.md).

The custody model is intentionally minimal. It is not a
substitute for DAO governance — it is a *bridge* until the DAO
exists. Sponsors who want stronger custody before Phase 3 are
welcome to wait.

## C. Operating-cost catalogue

Costs the spec already implies, named here so the treasury has
a real budget rather than a wish list. Each line cites the spec
section that introduced the obligation.

| line | source | cadence | rough magnitude |
|------|--------|---------|-----------------|
| Cost-table USD refresh | [`20 § Cost penalty calibration`](20-economic-model.md#cost-penalty-calibration), [`06 § cost penalty`](06-scoring.md#cost-penalty) | quarterly | maintainer time; no cash if maintainer self-funds |
| Settlement-latency SLI dashboard | [`19 § Subnet-wide SLIs`](19-operations.md#subnet-wide-slis-for-the-maintainer), [ADR 0012](../adr/0012-c7-measurement.md) | one-off + ongoing hosting | < $50 / month for hosted Grafana or self-hosted equivalent |
| Sponsorship concierge integration | [`27 § C.1`](27-economic-strategy.md#c1-sponsored-hypotheses) | per-sponsor | maintainer time; no cash for the integration itself |
| Audit-product launch | [`27 § C.3`](27-economic-strategy.md#c3-reproducibility-as-a-service) | one-off (Phase 3 prep) | legal review + SLA drafting; estimate Phase 2-exit ADR |
| External adversarial review | [`26-external-review.md`](26-external-review.md) | one-off (pre-Phase 2) | reviewer fee per the engagement ADR; range stated there, not here |
| Pre-Phase-2 cold-start contingency | [`27 § D Phase 2.0`](27-economic-strategy.md#d-phase-by-phase-trajectory), [ADR 0013](../adr/0013-cold-start-contingency.md) | conditional | thin-period subsidy if needed; magnitude set when triggered |

The catalogue is a **floor**, not a ceiling. Any new spec
obligation that implies money landing or money leaving the
subnet must add a row here as part of the same PR — the
[`docs/CONTRIBUTING-DOCS.md`](../CONTRIBUTING-DOCS.md)
discipline applies.

## D. Inflow paths

Where money can enter the treasury today:

1. **Sponsorship-bounty residual.** When a counterparty funds a
   hypothesis bounty under
   [`27 § C.1`](27-economic-strategy.md#c1-sponsored-hypotheses),
   the placeholder split is `60 / 30 / 10`
   ([miner](04-miner.md) / [validator](05-validator.md) cohort /
   subnet treasury) per
   [`27 § G open question 2`](27-economic-strategy.md#g-open-questions).
   The 10 % treasury cut lands in the multisig.
2. **Audit-product fees.** Fees for engagements under
   [`27 § C.3`](27-economic-strategy.md#c3-reproducibility-as-a-service)
   split between the participating validators and the subnet
   treasury; the validator share is per-engagement, the
   treasury share covers cost-table refresh and dashboard
   hosting.
3. **Voluntary contributions.** Anyone can donate TAO, Alpha,
   or other tokens to the multisig. Donations are recorded in
   the next quarterly attestation.

Inflow paths from registry licensing
([`27 § C.2`](27-economic-strategy.md#c2-registry--data-licensing))
and credentialing
([`27 § C.4`](27-economic-strategy.md#c4-credentialing--reputation))
land at Phase 3+ and are catalogued by the same mechanism when
they go live.

## E. Outflow rules

Maintainer-controlled discretionary outflows are bounded:

- **Per-quarter cap.** Total outflows in any rolling 90-day
  window MUST NOT exceed the previous quarter's closing
  balance, except via an explicit ADR ratifying the
  exceedance.
- **Per-line cap.** Single-line-item outflows above 25 % of the
  closing balance require an ADR before disbursement.
- **No outflows to maintainer personal wallets.** Maintainer
  reimbursement for incurred operating costs is allowed but
  must be itemised in the quarterly attestation; salary or
  retainer is not.

The 25 % single-line / 100 % per-quarter caps are conservative
defaults. The DAO transition (§ F) is the cleanest path to
relaxing them; pre-DAO relaxation requires a governance ADR.

## F. Transition contract (Phase 3 DAO incorporation)

At Phase 3 the subnet incorporates as a DAO under
[`GOVERNANCE.md § Phase 3+`](../../GOVERNANCE.md). Treasury
transition:

1. **Asset transfer.** All funds in the maintainer multisig
   transfer to the DAO treasury contract in a single batched
   transaction signed by the multisig.
2. **Attestation freeze.** The final pre-DAO quarterly
   attestation is published; no new pre-DAO attestations land
   thereafter.
3. **Custody contract supersession.** This doc's `B` (custody)
   section is marked *superseded by Phase 3 DAO governance*;
   the DAO's own governance docs replace it. § C (operating
   costs) and § D / E (inflow / outflow) carry forward,
   re-grounded against DAO governance instead of maintainer
   discretion.
4. **Audit handoff.** A final external audit of the multisig
   ledger lands as an ADR before transfer; the DAO inherits a
   clean accounting [baseline](01-glossary.md#baseline).

The transition is one-way. There is no path that returns
treasury custody from the DAO to the maintainer.

## G. Audit posture

Maintainer obligations that defend trust in the multisig:

- **Quarterly attestation** signed with the maintainer's
  primary identity key (same key used for spec signing in
  [`HM-REQ-0030 / HM-REQ-0031`](requirements.md)).
- **Public read.** Every attestation lands as a public ADR;
  the multisig is a public on-chain entity (`0x...` address
  recorded in the bootstrap ADR).
- **Monthly state diff.** Between quarterly attestations, the
  maintainer publishes a one-line monthly diff (opening,
  inflow total, outflow total, closing) as a comment on the
  most recent attestation ADR.
- **Independent verification.** The
  [`26-external-review.md`](26-external-review.md) reviewer
  can elect to include a treasury-ledger audit in scope; the
  maintainer commits to producing the on-chain transaction
  log on request.

## H. Open questions

1. **Bootstrap ADR.** The wallet address, the three multisig
   signers, and the recovery trustee are recorded in
   [`docs/adr/0014-treasury-pre-dao.md`](../adr/0014-treasury-pre-dao.md)'s
   "Related" section once the multisig is created. Until then
   the bootstrap is not yet executed.
2. **Tax domicile.** Maintainer-chosen and maintainer-disclosed
   in the bootstrap ADR. Not a spec decision.
3. **Sponsor-acceptable custody.** c12 captures the assumption.
   First-sponsor data (Phase 2) tells us if it holds; if not,
   an ADR before that sponsor's first transaction either
   tightens the custody contract or aborts the path.

## References

- [`27-economic-strategy.md`](27-economic-strategy.md) §§ C, D
  — the revenue paths whose proceeds land here.
- [`00.5-foundations.md § C c12-pre-dao-custody`](00.5-foundations.md#c12-pre-dao-custody)
  — the underlying commercial assumption.
- [`11-roadmap.md`](11-roadmap.md) — Phase 3 DAO transition the
  custody contract supersedes against.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) — the wider
  governance frame this doc is bounded by.
- [`docs/adr/0014-treasury-pre-dao.md`](../adr/0014-treasury-pre-dao.md)
  — rationale, bootstrap.

## Self-audit

Done when the custody contract names the multisig threshold
(2-of-3) and the three key roles; the operating-cost catalogue
has a row for every spec section that implies a recurring or
one-off cost; the inflow paths cite the strategy doc's revenue
sub-sections; the outflow caps are concrete; the transition
contract names what supersedes which section at Phase 3; the
audit posture commits the maintainer to quarterly attestations
plus monthly diffs.

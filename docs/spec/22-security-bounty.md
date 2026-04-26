---
name: security bounty
description: white-hat program — vulnerability disclosures are first-class hypotheses on the registry
tokens: 2500
load_for: [implementation, agent-operator, governance, review]
depends_on: [00.5, 16, 17, 21]
kind: contract
---

# 22 — Security bounty

## A. Why this exists

[`00.5-foundations.md § E`](00.5-foundations.md#e-empirical-posture--whats-proven-vs-whats-a-bet)
admits that several defences are unverified or partial. Two
threats are documented as having known residual damage:

- [F1 — stake-concentrated validator collusion](00.5-foundations.md#f1--stake-concentrated-validator-collusion).
  Top 1% holds ~90% of stake on Bittensor; the seed adversarial
  fixture in
  [`tests/golden/adversarial/F1-stake-collusion.json`](../../tests/golden/adversarial/F1-stake-collusion.json)
  documents how the design *fails* under coordinated 90% stake
  collusion.
- [F6 — long-latency rent extraction](00.5-foundations.md#f6--long-latency-rent-extraction).
  Two-tier settlement (HM-REQ-0070) blunts but does not eliminate
  the rational validator incentive to extract early-cycle emission
  and exit before slow truth invalidates the consensus.

Maintainer review alone cannot close gaps the maintainer cannot
imagine. The natural next mechanism is the same one the rest of
the subnet uses: **pay people to do useful work**. Applied to
security, that is a white-hat bounty.

The recursive insight is what makes this cheap to ship: **a
vulnerability disclosure IS a hypothesis on the registry**. The
claim is "attack X succeeds against the spec at version Y." The
artifact is an adversarial-simulator fixture per
[HM-REQ-0090](21-adversarial-simulator.md). The settlement pays
the discoverer the existing novelty + improvement components —
same scoring formula as any other settled hypothesis. No new
economic primitive; no new payout pipeline.

The **timing is unusually good**:

- Phase 0 / pre-runtime. No production system, no real TAO at
  stake, lowest-possible legal complexity.
- The spec is mostly written; the cryptoeconomic surface is large
  enough to attack at the spec level.
- HM-REQ-0090 already defines what a "finding" looks like —
  fixtures under `tests/golden/adversarial/`.
- The foundation-review cadence (every 6 months) gives a recurring
  forum for evaluating accepted findings.

Wait until Phase 2/3 and the program becomes "audit a deployed
adversarial system" — much harder, much riskier, much more
expensive.

## B. Phased scope

The bounty program ships in three phases mirroring the roadmap.
Each phase scopes what counts as a finding and how rewards are
paid.

### Phase 0–1 (current)

- **Scope:** spec-level findings only. The runtime under
  `src/hypotheses/` does not exist yet; there is nothing else to
  attack.
- **Reward mechanism:** the standard scoring formula applied to the
  public security-hypothesis. No separate funding pool. No real
  TAO at stake yet — credit is on-record via the public
  hypothesis.
- **Disclosure flow:** existing
  [`SECURITY.md`](../../SECURITY.md) private advisory, then public
  hypothesis after embargo (see § D).

### Phase 2 (testnet)

- **Scope adds:** implementation findings against the runtime
  (`src/hypotheses/` once it exists). Must be non-destructive:
  fixtures and proof-of-concept, not live exploits against
  testnet validators / miners.
- **Reward mechanism:** governance ADR earmarks a small emission
  slice (typically 1–3%) for security-hypothesis settlements.
  Decision deferred to a Phase 2 governance plan; out of scope
  here.

### Phase 3 (mainnet)

- **Scope adds:** the full mechanism, including coordinated-
  disclosure rules backed by stake slashing for embargo
  violations. Requires `src/hypotheses/scoring/` to enforce
  HM-REQ-0100 at scoring time.
- **Reward mechanism:** governance-allocated emission slice;
  payouts via on-chain settlement of the public security-
  hypothesis.

This document specifies Phase 0–1 normatively. Phase 2 and Phase 3
are descriptive scope notes; their normative spec lands in
follow-up plans.

## C. What counts as a security finding

A finding is a security-hypothesis if **all** of the following
hold:

1. It targets at least one **F1–F7** threat from
   [`00.5-foundations.md § A`](00.5-foundations.md#a-the-seven-threats-the-design-must-survive)
   or one **T-NNN** row in
   [`16-threat-model.md`](16-threat-model.md). Unmitigated and
   partial threats are preferred targets — see § A.
2. It includes an **adversarial-simulator fixture** under
   [`tests/golden/adversarial/`](../../tests/golden/adversarial/)
   per [HM-REQ-0090](21-adversarial-simulator.md), demonstrating
   the attack against the current spec / code. The fixture's
   `expected_outcome` must reflect the actual exploit succeeding
   under the current design.
3. The attack is **coalition-level or design-level**, not a
   transcription bug. A typo in a regex is a normal `bug.yml`
   issue, not a security-hypothesis.
4. The hypothesis is **independently reproducible** by validators
   running the deterministic core against the fixture.

Examples of in-scope findings:

- A new coalition shape that defeats HM-REQ-0080 (multi-oracle
  composition) — e.g., a `weighted_majority` exploit where weights
  add to less than 0.5 plus 0.5 minus epsilon.
- A spec-injection variant the
  [`scripts/check_prompt_injection.py`](../../scripts/check_prompt_injection.py)
  scanner doesn't catch.
- A T-OVR overturn-trigger gaming pattern that drains a
  legitimate settler's deferred 30% (HM-REQ-0070).
- A novelty-tiebreak race (HM-REQ-0021) the current rules don't
  resolve deterministically.

Examples explicitly **not** in scope:

- Typos, broken links, formatting bugs.
- "I disagree with the spec design" without a concrete
  reproducible attack.
- Proof-of-concepts against systems the subnet does not own
  (Bittensor itself, oracle subnets, GitHub).

## D. Disclosure mechanics (Phase 0–1)

The disclosure timeline reuses
[`SECURITY.md`](../../SECURITY.md) verbatim. Do not duplicate
those numbers in this doc; if SECURITY.md changes, this doc
follows.

The flow:

1. **Discoverer files a private GitHub Security Advisory** per
   [SECURITY.md](../../SECURITY.md). Include the adversarial
   fixture inline or as an attachment. The advisory is the
   T-DISC-EMBARGO transition into the `embargoed` state per
   [17 § security-hypothesis variant](17-hypothesis-lifecycle.md).
2. **Maintainer triages within 14 days** (per SECURITY.md). Either
   confirms the finding (proceeds to fix) or rejects it (T-DISC-
   WITHDRAW; advisory closed `not-applicable`).
3. **Fix lands as a separate spec PR.** New defences, new
   `HM-REQ-NNNN` if needed, threat-model row updates. The fix PR
   does NOT cite the still-embargoed advisory in the public commit
   message; it cites only the abstract defence.
4. **Embargo lifts** when the fix lands OR after the SECURITY.md
   default 90 days, whichever is earlier. T-DISC-LIFT transitions
   the security-hypothesis from `embargoed` to `proposed`; the
   advisory becomes a public GitHub Security Advisory linking the
   public hypothesis file.
5. **Public hypothesis enters the standard lifecycle.** Validators
   reproduce the fixture. The hypothesis settles per the standard
   T-SUP / T-CON two-tier mechanism (HM-REQ-0070). Reward pays the
   discoverer through the standard scoring formula.

A discoverer who skips step 1 (publishes a security-hypothesis
directly without going through SECURITY.md) is governed by
HM-REQ-0100 — the bounty is voided.

## E. HM-REQ-0100 — embargo before public disclosure

> **HM-REQ-0100** A security-hypothesis whose first appearance on
> `main` or in any public registry was NOT preceded by a private
> SECURITY.md advisory has its `improvement` component zeroed at
> scoring time. The `rigor` and `reproduction` components still
> pay (the public fixture is still useful coverage), and the
> hypothesis still proceeds through the standard lifecycle. The
> `improvement` zeroing is the bounty incentive against premature
> disclosure: the *bounty* is paid only for honest coordinated
> disclosure; the *fixture coverage* is paid for unconditionally.

This is the falsification-pays principle (DS.1 in
[`00.5 § B`](00.5-foundations.md#b-defences-derived-from-each-threat))
applied to security findings: an honest contribution always
earns rigor and reproduction; the *outcome-conditional* component
(here, improvement, which represents the bounty payout) gates on
disclosure discipline.

The mechanism is binary by design. Time-decayed alternatives, an
explicit penalty component, or a rigor-zeroing version were
considered and rejected (see the open question in the plan that
shipped this doc).

## F. What this is NOT

- **Not a CFAA-violating "attack our production system" pen-
  test.** No production system exists yet. Phase 2/3 add
  non-destructive testnet/mainnet rules.
- **Not a substitute for [SECURITY.md](../../SECURITY.md) private
  disclosure.** The bounty *builds on* the existing flow; private
  advisory is step 1.
- **Not a replacement for the adversarial simulator
  (HM-REQ-0090).** The simulator runs the fixtures the bounty
  produces. The bounty is the *upstream*, the simulator is the
  *downstream* test bed.
- **Not a bounty for typos or trivial findings.** Use
  `bug.yml` for those. § C is normative on what counts.
- **Not an open invitation to attack live oracles, mirror
  benchmarks, or any external system the subnet references.**
  Those have their own disclosure programs.

## G. Cross-references

- [`00.5-foundations.md § F1`](00.5-foundations.md#f1--stake-concentrated-validator-collusion),
  [§ F6](00.5-foundations.md#f6--long-latency-rent-extraction),
  and the "open bets" list in
  [§ E](00.5-foundations.md#e-empirical-posture--whats-proven-vs-whats-a-bet)
  — the partial threats this program is designed to close.
- [`16-threat-model.md § T-076`](16-threat-model.md#h-governance--process-attacks)
  — the governance-process threat that motivates HM-REQ-0100.
- [`17-hypothesis-lifecycle.md § security-hypothesis variant`](17-hypothesis-lifecycle.md)
  — the lifecycle states and transitions (`embargoed`,
  `T-DISC-EMBARGO`, `T-DISC-LIFT`, `T-DISC-WITHDRAW`).
- [`21-adversarial-simulator.md`](21-adversarial-simulator.md) —
  the fixture format every security finding produces.
- [`SECURITY.md`](../../SECURITY.md) — the private-disclosure
  timeline this doc is layered on top of.
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — the contribution
  on-ramp surfaces this program in its "Security findings"
  section.
- `agents/prompts/red-team-system.md` (added in a follow-up PR) —
  the role prompt for an adversarial agent that hunts findings.

## H. Self-audit

This doc is done when:

- Every defence and incentive in this doc traces to an existing
  mechanism (HM-REQ-0070 for two-tier settlement of the public
  hypothesis, HM-REQ-0090 for fixtures, falsification-pays for
  the rigor + reproduction floor) plus the one new requirement
  (HM-REQ-0100).
- A reader can identify, for any candidate finding, whether it is
  in scope (§ C) and what the disclosure flow is (§ D).
- The doc does NOT duplicate SECURITY.md's timeline numbers; if
  SECURITY.md is updated, this doc still reads correctly.
- The "what this is NOT" section (§ F) makes clear the program is
  not a CFAA escape hatch and not a substitute for private
  disclosure.
- Cross-references in § G all resolve under
  [`scripts/check_spec_consistency.py`](../../scripts/check_spec_consistency.py).

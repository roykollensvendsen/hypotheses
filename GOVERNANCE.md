<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Governance

Who decides what, and how. Written before it matters so it isn't
drafted under pressure later.

## Current model: trusted maintainer

During Phase 0 through Phase 2 (see
[`docs/spec/11-roadmap.md`](docs/spec/11-roadmap.md)), this project
is governed by a single trusted maintainer: **Roy Kollen Svendsen**
(repo owner, @roykollensvendsen).

This model is intentional for a project at this stage: decisions
need to be fast, the blast radius is small, and bikeshedding
governance before we have contributors is the kind of ceremony this
spec explicitly rejects.

## What the maintainer can do

- **Merge PRs** against any path.
- **Cut releases** via release-please.
- **Revert commits** on `main` (prefer a forward-fix commit when
  possible; `git revert` when a mistake is user-visible or load-
  bearing).
- **Change any spec document** via a normal PR (self-approval is
  acceptable during Phase 0–1; starts requiring a review in Phase 2+
  once contributors join).
- **Ship CI/automation changes** — hooks, workflows, labels,
  dependabot config.
- **Enforce the Code of Conduct** per the ladder in
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Recurring duties

These are obligations, not capabilities — the maintainer is on the
hook to do each one on its cadence.

- **Foundation review.** Per
  [`docs/spec/00.5-foundations.md § review cadence`](docs/spec/00.5-foundations.md#review-cadence):
  every 6 months, OR sooner if a `C`-section assumption flips, the
  maintainer reads `00.5 § C / D / E` end-to-end and either
  confirms each item still holds or opens a foundation-review ADR
  (`docs/adr/NNNN-foundation-review-YYYY-MM.md`). Skipping a
  review without an ADR explaining why is itself an audit-flag at
  the next review.
- **Threat-model curation.** When new threats are surfaced
  (security research, adversarial-simulator failures, real
  incidents), they go into [`docs/spec/16-threat-model.md`](docs/spec/16-threat-model.md)
  and get an adversarial fixture per
  [HM-REQ-0090](docs/spec/21-adversarial-simulator.md) in the same
  PR.

## What the maintainer cannot do unilaterally

- **Change the license.** AGPL-3.0-or-later is fixed. Relicensing
  requires the consent of every contributor who holds copyright on
  non-trivially-modified code.
- **Change the vision.** [`VISION.md`](VISION.md) can be refined
  but its core commitments — permissionless, agent-first,
  preregistered, AGPL — are non-negotiable until a formal governance
  transition.
- **Revert or rewrite a successfully-settled hypothesis.** Once a
  hypothesis reaches `settled-supported` or `settled-refuted` on
  mainnet, its record stays.
- **Remove a contributor's attribution.** SPDX copyright lines
  contributors add are preserved.

## Decision process

- **Trivial changes** (typos, formatting, clearly correct fixes):
  merge without ceremony.
- **Spec changes**: open a PR. Discussion in the PR thread. The
  maintainer merges when satisfied. If a change is non-obvious and
  no contributors weigh in within a reasonable window, the
  maintainer proceeds; others can follow up with a counter-PR.
- **Ambiguous or contentious changes**: maintainer may open a GitHub
  Discussion to gather input before merging.
- **ADRs**: any decision about pinned toolchain, architecture, or
  scope requires an ADR under `docs/adr/`. CI enforces this for
  dep/toolchain changes (`adr-required.yml`).

## Scope boundaries

The maintainer does NOT decide:

- **Validator scoring outcomes.** Scoring is a deterministic pure
  function over artifacts; the maintainer cannot intervene to change
  a score.
- **Emission weights.** The chain decides via YUMA consensus; the
  maintainer is not privileged.
- **Hypothesis validity.** Falsification or support flows from the
  protocol and CI; the maintainer cannot declare a result.

## Code of Conduct enforcement

CoC issues are routed to the maintainer (see
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and
[`SECURITY.md`](SECURITY.md) for contact). The Contributor Covenant
enforcement ladder (Correction → Warning → Temporary Ban →
Permanent Ban) applies.

## Revert policy

A commit may be reverted for any of the following:

- Breaks CI on `main` and cannot be fixed within 2 hours.
- Introduces a security issue (coordinate via
  [`SECURITY.md`](SECURITY.md) flow).
- Violates a non-negotiable from [`VISION.md`](VISION.md).

Reverts always use `git revert <sha>` (a forward commit), never
force-push history rewrites on `main`. Phase 0 exception — the
maintainer has performed one force-push during project setup; future
force-pushes to `main` require a post-mortem ADR.

## Transition to broader governance

Phase 3+ (post-mainnet) triggers a deliberate transition to a
multi-maintainer model, likely with a small council + dTAO-style
staked voting for economically meaningful decisions (scoring
weights, emission split, oracle registrations). The transition plan
is deferred to a Phase 3 spec PR — we won't pre-commit to a
structure before we see the community that forms.

Trigger signals to start drafting the transition:

- More than one person is routinely merging PRs.
- The subnet has been stable on mainnet for three months.
- More than 10 settled hypotheses in the registry.

## Conflicts of interest

If the maintainer is also a miner or validator operator (they are,
for reference implementations), the validator's enforcement of
"cannot score own hotkey" is what keeps the roles separable. The
maintainer's commit access does not give them scoring privileges.

## Getting in touch

- **Code / spec**: open an issue or a PR.
- **Discussion**: GitHub Discussions.
- **Security**: [`SECURITY.md`](SECURITY.md).
- **Code of Conduct**: see [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
- **Anything else**: roykollensvendsen@gmail.com.

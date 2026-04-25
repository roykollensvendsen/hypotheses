---
name: threat model
description: actors, assets, threats, and mitigations for the subnet
tokens: 3800
load_for: [implementation, agent-operator, governance, review]
depends_on: [03]
---

# 16 — Threat model

The subnet's value rests on three integrity claims: hypotheses are
honestly preregistered, results honestly reflect artifacts, and
emission honestly rewards both. This document enumerates the attacks
that would break those claims, maps each to the spec mechanism that
prevents or detects it, and records accepted residual risk.

This is a living document. When the architecture changes, a threat
row changes with it.

## Scope

- **In scope:** attacks that affect registry integrity, scoring
  integrity, emission distribution, artifact integrity, validator
  operation, or code supply chain. Subnet-level concerns.
- **Not in scope here** (handled elsewhere or out of scope entirely):
  - Vulnerabilities in Bittensor itself — report to the Bittensor
    security team.
  - Vulnerabilities in pinned upstream deps — `pip-audit` weekly
    catches known CVEs; the project reports upstream rather than
    patching forked copies.
  - Pure social-layer attacks (narrative, reputational) — the
    project doesn't structurally defend against these; see
    [`SECURITY.md`](../../SECURITY.md) for the disclosure process
    that exists.
  - User-laptop compromise — an operator whose machine is
    compromised has already lost; the subnet can't recover that
    ground.

## Assets

What an attacker could degrade or steal, ordered by severity:

| # | asset | why it matters |
|---|-------|----------------|
| A1 | **Scoring integrity** | Every claim the subnet makes about "who did useful work" dissolves if scores can be forged. |
| A2 | **Registry integrity** | Hypotheses merged to `main` are the contract between miners and validators. Tampering invalidates everything downstream. |
| A3 | **Artifact reproducibility** | Miner artifacts must yield the same metrics when rerun. Without this, honest reruns can't distinguish dishonest miners. |
| A4 | **Emission flow** | Emission landing on dishonest hotkeys destroys economic incentive for honest participation. |
| A5 | **Key custody** | Miner/validator hotkeys are the only credentials; loss or theft transfers their earnings. |
| A6 | **Supply chain (code + actions + deps)** | Compromised dependencies can silently rewrite behaviour without being visible in PR review. |
| A7 | **Subnet availability** | Validators unable to keep up with the announcement stream leave submissions unverified; miners who can't publish artifacts get zero. |

## Trust model

Restating
[03-architecture § trust model](03-architecture.md#trust-model) with
threat framing:

- **Miners are untrusted.** Every number a miner reports is
  verifiable from artifacts + a validator rerun. Nothing is taken on
  faith.
- **Validators are semi-trusted.** Any individual validator can be
  dishonest. Defences are (a) consensus via YUMA, (b) deterministic
  pure scoring so validators can't legitimately disagree, (c) self-
  scoring ban, (d) public on-chain score-vector attribution.
- **The repo is trusted.** `main` is the source of truth. Protecting
  it is the single most important governance act.
- **Datasets are semi-trusted.** Pinned by revision hash; verified on
  fetch.
- **Actions and pinned deps are trusted at the pinned SHA and no
  further.** Any floating reference is a supply-chain hole.

## Actors

| actor | goal | capability |
|-------|------|------------|
| Dishonest miner | claim emission for work they didn't do | forge numbers, cherry-pick seeds, train on the eval set, withhold artifacts |
| Sybil miner | amplify novelty or self-delegate | register many hotkeys, coordinate submissions |
| Dishonest validator | bias scores toward a bonded miner | skew reruns, refuse to audit, collude with miners |
| Colluder (miner+validator) | maintain an artificial reputation | coordinate submissions and scoring within a shared operator |
| Spam/DoS actor | flood the registry or artifact store | many announcements, oversize artifacts, fake PRs |
| Supply-chain attacker | insert code via compromised action or dep | hijack an action tag, push a malicious release of a pinned lib |
| Oracle manipulator | game SN42 (or future oracles) to claim false positives | control enough of the oracle's inputs to skew its answer |
| Repo attacker | merge a bypass into `main` | compromise a maintainer account, forge a PR review |
| Network adversary | MITM synapses or artifact transfers | tamper with announcement content or substitute artifacts in flight |

## Attack surfaces

- Git repository (`main`, `hypotheses/`, `experiments/`, CI
  workflows, hooks).
- Bittensor chain (synapses, weight-set extrinsics).
- Artifact store (IPFS manifests + bulk-artifact retrieval).
- Validator sandbox (podman, GPU passthrough, egress allowlist).
- Python runtime (determinism settings, dataset adapter).
- CI/CD (actions, secrets, workflow triggers).
- Wallet directory (hotkey file on an operator's machine).
- External oracle subnet (SN42 and future additions).

## Threats and mitigations

Threat IDs are stable (`T-NNN`). New threats get the next free
number; resolved threats keep their ID with `status: mitigated`.

Per [HM-REQ-0090](21-adversarial-simulator.md), every row below
must have at least one fixture under
[`tests/golden/adversarial/`](../../tests/golden/adversarial/) by
end of Phase 2; the column is implicit until the simulator lands.
A `simulator_fixture` column will be added to these tables in the
PR that ships the simulator.

### A. Economic attacks — dishonest rewards

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-001 | Miner cherry-picks seeds: declares 5 seeds but runs only the good ones | `seeds` list frozen in the hypothesis spec; validator reruns a random 40% sample by default; a single out-of-tolerance seed zeros the submission | [05 § rerun sample](05-validator.md#pipeline), [06 § reproduction](06-scoring.md#reproduction) | mitigated |
| T-002 | Miner tunes thresholds post-hoc to fit their numbers | preregistration: spec committed to `main` and hashed before results announce; `version` bump invalidates prior results; `code_commit` in manifest must predate `submitted_at` | [02 § versioning](02-hypothesis-format.md#versioning-and-immutability), [05 § structural validate](05-validator.md#pipeline), [07 § preregistration](07-incentive.md#preregistration) | mitigated |
| T-003 | Miner trains on the evaluation set to inflate accuracy | validator rerun uses the pinned `dataset_revision`; the runtime dataset adapter is the only network path allowed in-sandbox; egress allowlist enforces this at the container level | [08 § dataset handling](08-experiment-runtime.md#dataset-handling), [08 § sandbox](08-experiment-runtime.md#sandbox) | mitigated |
| T-004 | Fabricated single-seed submission (`seeds: [0]`) to shortcut rerun probability | spec requires `seeds_required` in every success criterion; hypotheses below the floor fail rigor; `hypo` miner client refuses to submit single-seed runs | [06 § rigor](06-scoring.md#rigor), [04 § miner etiquette](04-miner.md#miner-etiquette-and-gotchas) | mitigated |
| T-005 | Novelty-bonus race — two miners settle the same hypothesis in the same block | novelty = 1.0 first, 0.5 second, 0.0 thereafter. Tiebreak order: (1) block height of the `ResultsAnnouncement` extrinsic, (2) in-block extrinsic index, (3) miner-hotkey SS58 lex order | [06 § ordering](06-scoring.md#ordering-tiebreak-for-simultaneous-settlements) | mitigated |
| T-006 | Sybil farming — one operator registers many miner hotkeys to capture novelty multiple times | per-hotkey scoring is independent, but novelty is per-hypothesis so a Sybil cluster still only gets one novelty bonus per hypothesis per version; compute cost to run experiments doesn't drop at scale; validator rerun sampling is per-hotkey | [07 § hotkey-identity binding](07-incentive.md#hotkey-identity-binding), [06 § novelty](06-scoring.md#novelty) | mitigated |

### B. Scoring / registry integrity

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-010 | Validator biases scoring toward a bonded miner | validator scoring is a deterministic pure function over artifacts; two validators on the same inputs produce the same score vector; consensus via YUMA down-weights outliers | [05 § two layers](05-validator.md#two-layers-deterministic-core-and-operator-layer), [07 § weight setting](07-incentive.md#weight-setting) | mitigated |
| T-011 | Validator scores their own miner hotkey | self-scoring ban enforced in validator code; weight vector anomaly detection across validators | [05 § anti-collusion](05-validator.md#anti-collusion), [07 § self-scoring ban](07-incentive.md#self-scoring-ban) | mitigated |
| T-012 | LLM agent in the operator layer inserts judgment into scoring | spec forbids it: scoring core is pure, agent-free; operator layer decides *when* or *whether* to rerun, never *what score* | [05 § two layers](05-validator.md#two-layers-deterministic-core-and-operator-layer), [13 § role × surface matrix](13-agent-integration.md) | mitigated |
| T-013 | Miner submits a manifest referencing a `code_commit` that didn't exist at submit time or doesn't contain the entrypoint | validator checks commit exists in the repo, was reachable before `submitted_at`, and contains `experiments/<id>/` | [05 § what kills a submission](05-validator.md#what-kills-a-submission) | mitigated |
| T-014 | Hypothesis merged with a schema-invalid front matter | JSON Schema validation in CI via [`spec-validate.yml`](../../.github/workflows/spec-validate.yml) + [`scripts/validate_hypotheses.py`](../../scripts/validate_hypotheses.py); schema/doc consistency via [`check_schema_matches_doc.py`](../../scripts/check_schema_matches_doc.py) | [02 § schema validation](02-hypothesis-format.md#schema-validation) | mitigated |
| T-015 | Colluding miner+validator pair routinely submits and self-validates within budget | YUMA consensus penalises validators whose score vectors are persistent outliers; self-scoring ban catches the direct case; cross-validator anomaly detection catches the indirect case | [07 § anti-gaming](07-incentive.md#anti-gaming-measures) | **partial — cross-validator anomaly detection is an observation, not a coded check; document the expectation in a follow-up ADR** |
| T-016 | Forged or replayed announcement | every announcement signed by miner hotkey using ed25519; canonical JSON (RFC 8785) before signing prevents re-encoding tricks; validators reject invalid signatures | [09 § synapses](09-protocol.md#synapse-resultsannouncement), [12 § signing](12-implementation-constraints.md) | mitigated |
| T-017 | Dishonest miner submits identical manifest as another miner (copy-paste) | announcements are signed by the submitting hotkey; duplicate `(spec_cid, artifact_cid, miner_hotkey)` fails on uniqueness; the validator operator-layer flags clusters of identical `declared_summary` for review | [13 § validator operator role](13-agent-integration.md) | mitigated (flagging is an operator-layer duty) |

### C. Availability — DoS and artifact unreachability

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-020 | Miner uploads huge bundles to exhaust validator storage | 10 GiB per-hotkey quota, 500 MiB per-artifact cap, 1 MiB per-manifest cap; validators refuse oversize `GetArtifact` requests | [03 § failure modes](03-architecture.md#failure-modes-the-architecture-must-resist), [04 § artifact contract](04-miner.md#submit-artifact-contract) | mitigated |
| T-021 | Announcement-stream flooding | per-hotkey rate limit: 3 announcements per Bittensor epoch (~72 min). Excess dropped, logged. Duplicate submissions per `(spec_id, version, hotkey)` within an epoch collapse to the first | [05 § discover](05-validator.md#pipeline) | mitigated |
| T-022 | Miner takes artifact offline after submission | validators cache artifacts on successful rerun; the subnet operator pins manifest CIDs centrally; miners who drop bulk artifacts lose reproduction score on recounts, which caps their reputational value | [09 § storage](09-protocol.md#storage) | mitigated (miner-risk model) |
| T-023 | IPFS gateway outage across validators at once | validators use their own IPFS node; fetch failures degrade gracefully (submission stays pending, not failed); retries on next cycle | [09 § storage](09-protocol.md#storage) | accepted — single-IPFS-provider risk is operational |
| T-024 | Validator sandbox starved by a slow experiment | wallclock cap per profile (5m–4h depending on profile); kill-on-cap with metrics-absent outcome = validator records the submission failed reproduction | [08 § hardware profiles](08-experiment-runtime.md#hardware-profiles), [08 § failure policy](08-experiment-runtime.md#failure-policy) | mitigated |

### D. Supply-chain attacks

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-030 | Tag-moved GitHub Action pushes malicious code (the 2025 `tj-actions/changed-files` class of attack) | all action refs MUST be 40-char SHAs, verified by [`check_action_pins.sh`](../../scripts/check_action_pins.sh) via `action-pin-check.yml` | [15 § pinning policy](15-ci-cd.md#pinning-policy) | mitigated |
| T-031 | Compromised Python dep ships a malicious version between reviews | `uv.lock` hash-pinned; Dependabot opens review-required PRs; `pip-audit` weekly flags known CVEs; no direct-to-main merges of dep PRs | [12 § dependencies policy](12-implementation-constraints.md#dependencies-policy), [15 § tier 2 planned](15-ci-cd.md#tier-2--land-as-phase-1-begins-when-src-exists) | partial (awaiting Phase 1 `pyproject.toml`) |
| T-032 | Secret leaked in a commit | GitHub native secret scanning + push protection enabled at the repo level; maintainer reviews every PR that touches secrets-adjacent files | — (repo setting) | mitigated |
| T-033 | Typosquatted package name pulled into deps | deps are only added via spec-reviewed PR + ADR (`adr-required.yml`); names reviewed at add-time | [12 § dependencies policy](12-implementation-constraints.md#dependencies-policy) | mitigated |
| T-034 | Unsafe workflow with excessive permissions or template-injection | `zizmor.yml` runs weekly + on `.github/**` PRs, fails on medium+; every workflow has least-privilege `permissions:` block | [15 § workflow hardening](15-ci-cd.md#workflow-hardening-conventions) | mitigated |
| T-035 | Runner compromise exfiltrates via network | `step-security/harden-runner` runs first step in every job, `egress-policy: audit` today, `block` with allow-list scheduled for Phase 2 | [15 § deferred](15-ci-cd.md#deferred--planned) | partial (audit mode; block mode deferred) |

### E. Runtime / sandbox attacks

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-040 | Experiment code escapes sandbox | podman non-root, readonly code layer, writable `/artifacts` only, dropped capabilities, no host filesystem mount, no sudo | [08 § sandbox](08-experiment-runtime.md#sandbox) | mitigated |
| T-041 | Experiment exfiltrates data via unexpected URL | egress allow-list (HF mirror, PyPI, github raw, configured storage); violation = hard kill + submission zero | [08 § sandbox](08-experiment-runtime.md#sandbox), [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy) | mitigated |
| T-042 | Non-deterministic training lets a miner submit a lucky run they can't reproduce | runtime pins `PYTHONHASHSEED`, CUDA flags, OMP/MKL threads, `torch.use_deterministic_algorithms(True)`; RNG state dumped at start/end; `rerun_tolerance` is declared in the spec — disagreement beyond tolerance kills the submission | [08 § determinism](08-experiment-runtime.md#determinism), [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy) | mitigated |
| T-043 | Dataset hash drift — attacker swaps data under declared revision | adapter verifies revision hash on fetch; mismatch raises `DatasetHashMismatch` and kills the run | [08 § dataset handling](08-experiment-runtime.md#dataset-handling), [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy) | mitigated |

### F. Key / identity attacks

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-050 | Agent exfiltrates a miner hotkey | agents never hold hotkeys; the MCP server signs and returns opaque signed objects | [13 § identity and key handling](13-agent-integration.md#identity-and-key-handling) | mitigated |
| T-051 | Operator hotkey loss (disk failure, stolen laptop) | operational concern; Bittensor wallet best practices apply — store encrypted, back up keys. Subnet can't compensate | — | accepted |
| T-052 | Maintainer account compromise merges a malicious change | current single-maintainer governance is thin on this; mitigation is maintainer's personal opsec (2FA, signed commits recommended); transition to multi-maintainer in Phase 3+ reduces blast radius | [`GOVERNANCE.md`](../../GOVERNANCE.md) | partial — single-maintainer bus factor is Phase 0 design |
| T-053 | Spoofed identity in PR attribution | AGPL license does not require signed commits; `commit-msg` hook blocks bot trailers; GitHub's attribution + branch-protection rules (Phase 2+) provide the real signal | — | partial (signed commits not required yet) |

### G. Oracle attacks

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-060 | Miner games SN42 oracle to claim a false positive | oracle check is a hard gate: beyond tolerance = score vector zero regardless of other components. Oracle answers come from the oracle subnet's consensus | [06 § oracles](06-scoring.md#oracles) | mitigated |
| T-061 | Oracle disagrees with itself across validator cycles | N consecutive consistent verdicts required before the verdict is final (default N=3 for consensus-answer; N=1 for known-answer where self-disagreement is itself an error). Persistent disagreement >24h triggers operator alert. **Multi-oracle composition** ([18 § composition](18-oracle.md#composition), HM-REQ-0080) raises the bar further: a `majority` or `weighted_majority` rule tolerates one disagreeing oracle without zeroing the score | [18 § disagreement](18-oracle.md#disagreement-handling-same-oracle-cross-cycle) | mitigated |
| T-062 | Oracle subnet itself goes down | submission scored without the oracle check — but fails if oracle was declared. This aligns with fail-fast: no degraded-scoring-with-missing-oracle path. **Multi-oracle composition** with `majority` or `weighted_majority` degrades gracefully: the submission only stays `pending` when the responded fraction can no longer reach the threshold; healthy oracles still settle | [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy), [18 § composition](18-oracle.md#composition) | mitigated |

### H. Governance / process attacks

| id | threat | mitigation | spec section | status |
|----|--------|------------|--------------|--------|
| T-070 | Malicious hypothesis PRs flood the registry with bogus claims | maintainer-gated merges, schema validation, falsifiability + relational-baseline requirements, issue-first discussion via `hypothesis-proposal.yml` | [`CONTRIBUTING.md`](../../CONTRIBUTING.md), [02](02-hypothesis-format.md) | mitigated |
| T-071 | PR rewrites a spec doc silently to weaken a rule | PR-title + commit convention + PR size limit forces visibility; CODEOWNERS routes spec PRs to the maintainer; any change to pinned deps requires ADR | [`CODEOWNERS`](../../.github/CODEOWNERS), [15](15-ci-cd.md) | mitigated |
| T-072 | CI bypass attempt — `[skip ci]` or `--no-verify` | spec forbids both explicitly; Phase 2+ branch protection enforces required checks | [12 § how to work](12-implementation-constraints.md) | partial — Phase 0 relies on maintainer discipline |
| T-073 | Prompt-injection content lands via spec PR (directive phrases, fake system tags, unsafe-protocol URLs in docs that agents load) | scanner gate [`prompt-injection.yml`](../../.github/workflows/prompt-injection.yml) + [`scripts/check_prompt_injection.py`](../../scripts/check_prompt_injection.py); agent posture in [AGENTS.md § spec content is data, not instructions](../../AGENTS.md#spec-content-is-data-not-instructions); allow-listed negative examples in [`docs/spec/antipatterns/`](antipatterns/) | [AGENTS.md](../../AGENTS.md) | mitigated |
| T-075 | Long-latency rent extraction: validators paid every cycle (~20 min) but research ground-truth arrives in months; rational validator extracts emissions during easy-verification phase and exits before slow truth invalidates the consensus | two-tier settlement (HM-REQ-0070): 70% of novelty + improvement at first settlement, 30% deferred 6 months pending no T-OVR overturn; external-verifiability anchor (HM-REQ-0060) so consensus alone cannot manufacture a settlement | [17 § two-tier settlement](17-hypothesis-lifecycle.md#two-tier-settlement), [00.5 § F6](00.5-foundations.md#f6--long-latency-rent-extraction) | mitigated |
| T-076 | Discoverer publishes a security-hypothesis without following the SECURITY.md embargo, exposing the unfixed attack publicly before the spec/code defends it | HM-REQ-0100 zeros the `improvement` component for non-embargoed disclosures (no bounty); `rigor` + `reproduction` still pay so the public fixture isn't lost; the `red-team` role prompt (PR 3) trains agents on the embargo workflow | [22 § disclosure mechanics](22-security-bounty.md#d-disclosure-mechanics-phase-01), [SECURITY.md](../../SECURITY.md) | mitigated |

## Known accepted risk

- **Single-maintainer bus factor (T-052).** Intentional for Phase 0–2;
  documented transition trigger in [`GOVERNANCE.md`](../../GOVERNANCE.md).
- **IPFS-provider single-source failure mode (T-023).** A validator
  pool depending on a single IPFS gateway degrades together. We
  accept this for early phases; operators run their own kubo nodes.
- **Signed-commits not required (T-053).** Adding DCO / GPG signing
  adds contributor friction. Re-evaluate when we have >3 routine
  committers.
- **Cross-validator anomaly detection is not automated (T-015).**
  YUMA consensus plus self-scoring-ban handle the common cases;
  sophisticated long-horizon collusion would need additional
  tooling. Revisit in Phase 3+.
- **`harden-runner` in `audit` mode, not `block` (T-035).** Requires
  observation period to build the allow-list; scheduled for
  end-of-Phase-2.

## Open questions / gaps

No open gaps remaining in the current threat table; each entry has
a concrete mitigation or an explicit accepted-risk entry. New
threats get filed as they're discovered; the "partial" entries
continue to move toward "mitigated" as deferred work lands per
[15 § deferred / planned](15-ci-cd.md#deferred--planned).

## References

- [`SECURITY.md`](../../SECURITY.md) — disclosure process for
  vulnerabilities found here.
- [03 § failure modes](03-architecture.md#failure-modes-the-architecture-must-resist)
  — one-line summary table intended for readers of the architecture
  doc.
- [07 § anti-gaming](07-incentive.md#anti-gaming-measures) — the
  economic framing of the same threats.
- [15 § pinning policy](15-ci-cd.md#pinning-policy) — supply-chain
  enforcement.
- [`docs/adr/0001-phase-zero-foundation.md`](../adr/0001-phase-zero-foundation.md)
  — why each non-obvious mitigation was chosen.

## Self-audit

This doc is done when:

- Every threat row has a stable ID, a mitigation, a spec-link, and
  a status (`mitigated` / `partial` / `accepted` / `deferred`).
- No threat row is `mitigated` without a corresponding mechanism
  in a spec doc, a CI gate, or a code module.
- Every `partial` threat names the path to full mitigation
  (usually a Phase-exit item or an ADR trigger).
- Every `accepted` risk is explicit about why the project chose
  not to mitigate.
- Attack surfaces cover every external-facing interface: git, chain,
  IPFS, sandbox, runtime, CI, wallet.

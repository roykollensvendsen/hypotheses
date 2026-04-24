---
name: roadmap
description: phased plan from spec freeze to mainnet
tokens: 900
load_for: [implementation, governance, review]
depends_on: []
---

# 11 — Roadmap

Four phases. Each has exit criteria that must hold before moving on.

## Phase 0 — Spec freeze (current)

**Goal:** the spec documents in `docs/spec/` are internally consistent,
reviewed, and ready to implement against.

**Exit criteria:**

- All spec documents merged.
- Every TBD in the spec has an issue filed or an explicit "defer to
  Phase N" annotation.
- One worked-example hypothesis (e.g. `H-0001`) lives in `hypotheses/`
  at `status: proposed`, with a populated (but possibly stub)
  `experiments/H-0001/` directory.
- License chosen and LICENSE file committed. **Decision:** AGPL-3.0-or-later.
  Chosen to enforce the "bottom-up, not top-down" ethos from the founding
  discussion: prevents proprietary SaaS forks of the subnet and ensures
  network-service derivatives ship source to their users. AGPL retains a
  patent grant. Adoption friction with corporate compliance regimes is an
  accepted tradeoff.

**What lands:** docs, template, placeholder experiment. No runnable code.

## Phase 1 — Offline reference implementation

**Goal:** a single operator can run the full miner→validator round-trip
on one machine, with no Bittensor chain involvement.

**Exit criteria:**

- `hypo propose`, `hypo run`, `hypo submit` work against a local
  filesystem-backed storage.
- `hypo validate serve` can pull a local submission, rerun, and
  produce a score vector written to a local file.
- `hypotheses.client` SDK exposes the full surface documented in
  [13](13-agent-integration.md).
- `hypo mcp serve` ships with the read-only tool set enabled.
- JSON schema for hypotheses is authored and CI-enforced.
- Runtime sandbox runs `experiments/H-0001/` deterministically on at
  least `cpu-small` and `single-gpu-24gb` profiles.
- Integration test `tests/integration/smoke_submit_score.py` passes on
  CI.
- At least one honest-null and one settling result validate end-to-end.
- Mutation score ≥ 75% per module on the nightly mutation job for two
  consecutive runs.
- Every module's git history shows a `test:` commit preceding the
  first `feat:` commit that touches it.

**What lands:** `src/hypotheses/` fleshed out, dataset adapters, sandbox
runtime, scoring, local IPC stubs for synapses.

## Phase 2 — Testnet subnet

**Goal:** the subnet runs on Bittensor testnet with ≥3 external miners
and ≥2 external validators participating.

**Exit criteria:**

- Testnet subnet registered (netuid assigned at registration; record
  in `docs/adr/` when assigned).
- `synapses.py` wired up to actual Bittensor axon/dendrite.
- IPFS mirroring and retrieval working in anger.
- SN42 oracle adapter implemented and exercised by at least one
  hypothesis.
- `hypo mcp serve` write tools enabled; at least one reference agent
  under `agents/examples/` submits an accepted hypothesis end-to-end
  on testnet.
- Two weeks of stable operation without a validator getting stuck,
  without a manifest-hash mismatch bug, without a sandbox escape
  incident.
- Economic sim confirms composite score weights produce the intended
  emission distribution under plausible miner strategies.

**What lands:** chain integration, IPFS integration, oracle integration,
public onboarding docs.

## Phase 3 — Mainnet

**Goal:** mainnet subnet registered and operating, with a trusted-
maintainer governance model and a documented transition path to
decentralised governance.

**Exit criteria:**

- External security review of the runtime sandbox and signing code
  completed.
- Wire-schema is frozen and backwards-compat policy documented.
- ≥5 settled hypotheses in the registry.
- Public docs site (the `docs/spec/` rendered via MkDocs or similar).
- Launch announcement and onboarding guide published.

## Cadence and ownership

Until a second committer joins, owner of every phase is the repo
maintainer. After that, each phase gets a tracked issue with a named
owner and a weekly checkpoint.

**Decision:** trunk-based. Phase 0–1 allows direct commits to `main`
by the maintainer (solo development, speed > ceremony). Phase 2+ is
PR-based with CI gating and no direct pushes to `main`. Releases are
annotated tags (`v0.1.0`, `v0.2.0`) per subnet CLI version; no
long-lived release branches.

## Self-audit

This doc is done when:

- Every phase has explicit, check-off-able exit criteria.
- Every criterion is either a CI-verifiable state, a filesystem
  fact, or an operator-attested milestone — nothing subjective.
- Phase boundaries match the conditional guards in CI workflows
  (e.g. `if src/ exists then run mutation`).
- No TBD except external-dependency items (`netuid assigned at
  registration`).
- Ownership + branching decisions align with
  [`GOVERNANCE.md`](../../GOVERNANCE.md).

---
name: roadmap
description: phased plan from spec freeze to mainnet
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
- License chosen and LICENSE file committed. **TBD**: MIT vs Apache-2.0;
  default Apache-2.0 for the patent grant.

**What lands:** docs, template, placeholder experiment. No runnable code.

## Phase 1 — Offline reference implementation

**Goal:** a single operator can run the full miner→validator round-trip
on one machine, with no Bittensor chain involvement.

**Exit criteria:**

- `hypo-miner propose`, `run`, `submit` work against a local
  filesystem-backed storage.
- `hypo-validator` can pull a local submission, rerun, and produce a
  score vector written to a local file.
- JSON schema for hypotheses is authored and CI-enforced.
- Runtime sandbox runs `experiments/H-0001/` deterministically on at
  least `cpu-small` and `single-gpu-24gb` profiles.
- Integration test `tests/integration/smoke_submit_score.py` passes on
  CI.
- At least one honest-null and one settling result validate end-to-end.

**What lands:** `src/hypotheses/` fleshed out, dataset adapters, sandbox
runtime, scoring, local IPC stubs for synapses.

## Phase 2 — Testnet subnet

**Goal:** the subnet runs on Bittensor testnet with ≥3 external miners
and ≥2 external validators participating.

**Exit criteria:**

- Testnet subnet registered (netuid TBD).
- `synapses.py` wired up to actual Bittensor axon/dendrite.
- IPFS mirroring and retrieval working in anger.
- SN42 oracle adapter implemented and exercised by at least one
  hypothesis.
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

**TBD**: branching and release model. Current lean: trunk-based with
tagged releases per subnet CLI version; no long-lived release branches.

---
name: architecture
description: components, data flow, and trust model for the subnet
tokens: 1200
load_for: [implementation, agent-operator, review]
depends_on: [00, 01]
kind: explanation
---

# 03 — Architecture

## Components

```text
 ┌────────────────────┐         ┌────────────────────┐
 │ Hypothesis Registry│◀──PR───▶│   GitHub (this     │
 │  hypotheses/*.md   │         │   repo, mirrored   │
 └─────────┬──────────┘         │   to content-addr  │
           │                    │   storage)         │
           │                    └────────────────────┘
           │
     ┌─────▼──────┐       announces       ┌────────────┐
     │   Miner    │──────spec/result─────▶│ Validator  │
     │  (neuron)  │                       │  (neuron)  │
     └─────┬──────┘                       └─────┬──────┘
           │                                    │
           │ runs in                             │ reruns in
      ┌────▼─────┐                          ┌────▼─────┐
      │ Runtime  │                          │ Runtime  │
      │ (sandbox)│                          │ (sandbox)│
      └────┬─────┘                          └─────┬────┘
           │                                      │
           │     artifacts (content-addressed)    │
           └──────────────▶ Storage ◀─────────────┘
                                │
                                │   weights
                                ▼
                          ┌──────────┐
                          │Bittensor │
                          │  chain   │
                          └──────────┘
```

### Hypothesis Registry

The authoritative list of hypotheses is `hypotheses/*.md` in this repo. Merged
= accepted into the registry. The registry is mirrored into content-addressed
storage so validators do not need to pull git to verify an ID → spec mapping;
see [09 Protocol](09-protocol.md).

### Miner

A Bittensor neuron that does one or both of:

- **Propose**: open a PR adding a new hypothesis file, or bumping a version.
- **Run**: execute an accepted hypothesis's protocol and publish signed
  artifacts.

A single hotkey may do both. See [04 Miner](04-miner.md).

### Validator

A Bittensor neuron that, on a cadence:

1. Discovers new submissions on-chain via `ResultsAnnouncement` synapses.
2. Fetches the referenced spec (by CID) and artifacts (by CID).
3. Validates the spec against schema and the artifacts against declared
   hashes.
4. Reruns a sampled subset of seeds in its own sandbox.
5. Computes the composite score and sets weights.

See [05 Validator](05-validator.md).

### Runtime

A sandboxed execution environment (containerised, resource-limited) that both
miners and validators use to run experiment code deterministically. See
[08 Experiment Runtime](08-experiment-runtime.md).

### Storage

Content-addressed storage for specs and artifacts. **Decision:** IPFS
(kubo 0.29+) for artifacts, with the CID embedded in the on-chain
synapse. Specs are content-addressable via git blob hash and mirrored to
IPFS on merge by the `spec-mirror.yml` workflow. S3-compatible fallback
is deferred to Phase 3+ if needed.

## Data flow

### Proposing a hypothesis

1. Miner opens a PR: new file under `hypotheses/`, plus matching
   `experiments/H-NNNN/` directory containing the entrypoint.
2. CI runs the schema validator and a dry-run of the entrypoint under the
   smallest hardware profile (smoke check only).
3. Human reviewers merge. Merge assigns the final `id` if it was a
   placeholder.
4. Status: `proposed` → `accepted`.

### Submitting results

1. Miner runs the experiment locally in the runtime; produces an artifact
   bundle (metrics, seeds, env lock, rng state, code commit hash).
2. Miner uploads the bundle to storage; gets an artifact CID.
3. Miner broadcasts a `ResultsAnnouncement` synapse on-chain, signed by
   hotkey, carrying `(spec_id, spec_version, artifact_cid, declared_metrics)`.
4. Validators pick it up on their next cycle.

### Validating results

1. Validator pulls the spec (by id@version) and the artifact (by CID).
2. Structural validation: schema ok, hashes match, code_ref commit matches.
3. Sample seeds: validator picks a configurable fraction of the declared
   seeds and reruns them locally.
4. Compare: rerun metrics within rerun tolerance vs. miner-declared metrics.
5. Score: see [06 Scoring](06-scoring.md).
6. Commit weights via YUMA.

## Trust model

- **Miners are untrusted.** Every number a miner reports must be verifiable
  from artifacts + a validator rerun.
- **Validators are semi-trusted.** Consensus across validators is the
  primary defence against a single dishonest validator. Validators cannot
  score their own miner hotkey.
- **The repo is trusted.** `hypotheses/` merged on `main` is the source of
  truth. Protecting `main` is the subnet's most important governance act.
  **Decision:** single trusted-maintainer (repo owner) for Phase 0–2.
  Transition to multi-sig or a maintainer council is a Phase 3 exit item.
- **External datasets are semi-trusted.** Datasets are pinned by revision
  hash; validators verify the hash on fetch.

## Failure modes the architecture must resist

Short summary; the canonical enumeration lives in
[16 — Threat model](16-threat-model.md).

| Failure | Mitigation | Threat ID |
| --- | --- | --- |
| Miner cherry-picks seeds | `seeds` in spec is fixed; reruns sample from the declared set | [T-001](16-threat-model.md) |
| Miner tunes thresholds post-hoc | `success_criteria` is preregistered and hashed before submit | [T-002](16-threat-model.md) |
| Miner trains on the evaluation set | Validators rerun with pinned dataset revision in sandbox | [T-003](16-threat-model.md) |
| Validator collusion with miner | Validators cannot self-score; weight normalisation across validators | [T-010](16-threat-model.md), [T-015](16-threat-model.md) |
| Spec drift (code doesn't match claim) | `code_ref` and `entrypoint` are committed before results submit | [T-013](16-threat-model.md) |
| Non-determinism | Runtime pins seeds, BLAS threads, CUDA flags; tolerance explicit | [T-042](16-threat-model.md) |
| Large artifact DOS | Per-hotkey quota: 10 GiB. Per-artifact cap: 500 MiB. Per-manifest cap: 1 MiB. | [T-020](16-threat-model.md) |

<!-- canonical:per_hotkey_storage_gb=10 -->
<!-- canonical:per_artifact_cap_mib=500 -->

## What is explicitly *out* of architecture scope

- Inference serving. This is not an inference subnet.
- General compute rental. Miners run hypotheses, not arbitrary user code.
- Model hosting. If a hypothesis produces a useful model, that's a result
  artifact, not a service.

## Self-audit

This doc is done when:

- Every component in the diagram maps to a directory or module in
  [10-repo-layout.md](10-repo-layout.md).
- Every arrow in the data-flow section names the synapse, git path,
  or storage CID that carries it.
- Every failure-mode table row links to a threat ID in
  [16-threat-model.md](16-threat-model.md).
- Trust-model claims match the attacker capabilities in
  [16 — Actors](16-threat-model.md#actors).
- No storage, chain, or runtime behaviour is described here that
  isn't the canonical home — link instead.

---
name: miner
description: miner responsibilities, CLI, synapse interfaces, artifact contract
tokens: 900
load_for: [implementation, agent-operator, review]
depends_on: [02, 03, 09]
---

# 04 — Miner

A miner is a Bittensor neuron that proposes and/or runs hypotheses. All
miners speak the same protocol; specialisation is a matter of how they
allocate their own compute.

## Responsibilities

1. **Propose** new hypotheses via git PR (off-chain).
2. **Run** accepted hypotheses in the runtime.
3. **Publish** signed artifact bundles to storage.
4. **Announce** submissions on-chain via the `ResultsAnnouncement` synapse.
5. **Respond** to validator challenges (artifact resend, metadata queries).

## CLI

Miner operations are surfaced through the unified `hypo` command (see
[14](14-cli.md)):

```
hypo register miner        # register hotkey on the subnet
hypo propose <path>        # validate and scaffold a hypothesis spec
hypo run <id>              # run an accepted hypothesis locally
hypo submit <run-handle>   # upload artifacts and broadcast announcement
```

The miner also runs a long-lived axon to serve validator queries; that
process is started by `hypo register miner` and supervised by the
operator's init system (systemd, launchd, or equivalent). There is no
separate `hypo serve` verb — serving is a consequence of being
registered, not an explicit operator action.

`run` and `submit` are separated deliberately: a miner can run, inspect
the result, and decide not to submit. Once submitted, withdrawals are
impossible and a dishonest submission is penalised.

## Run: what happens

1. Pull spec for `id` at current version from the registry.
2. Materialise the runtime image for the declared `hardware_profile`.
3. For each seed in `protocol.seeds`:
   a. Copy `experiments/<id>/` into the sandbox.
   b. Run `entrypoint` with the seed and the variable assignment for each
      baseline + candidate condition.
   c. Capture stdout, stderr, `metrics.jsonl`, `env.lock`, `rng.state`.
4. Verify all declared metrics are present and numeric.
5. Write a local `run.manifest.json` pointing at all artifacts.

## Submit: artifact contract

An artifact bundle is a directory that hashes to a single CID. Required
layout:

```
run.manifest.json          # top-level manifest (signed)
spec.md                    # exact copy of the spec at submission time
spec.cid                   # CID of spec.md
code.commit                # git commit hash of this repo at submit time
env.lock                   # pinned environment (pip/conda/nix)
hardware.json              # detected GPU/CPU/memory
seeds/<seed>/<condition>/
    metrics.jsonl
    stdout.log
    stderr.log
    rng.state
    weights/               # optional; hashed and referenced in manifest
```

`run.manifest.json` schema (abridged):

```json
{
  "schema_version": 1,
  "hypothesis_id": "H-0001",
  "hypothesis_version": 1,
  "spec_cid": "bafy...",
  "code_commit": "<git-sha>",
  "miner_hotkey": "5F...",
  "submitted_at": "2026-04-24T10:00:00Z",
  "runs": [
    {
      "seed": 0,
      "condition": {"init_topology": "fully_connected", "edge_dynamics": "gradient_decay"},
      "metrics": {"flops_to_target_loss": 1.23e9, "final_test_accuracy": 0.912},
      "wallclock_seconds": 842.1,
      "artifacts": {"metrics": "cid:bafy...", "weights": "cid:bafy..."}
    }
  ],
  "declared_summary": {
    "flops_to_target_loss": {"median": 1.25e9, "stdev": 0.04e9, "n": 5},
    "final_test_accuracy":  {"median": 0.910,  "stdev": 0.004, "n": 5}
  },
  "signature": "<ed25519 signature of the above over canonical JSON>"
}
```

Signature covers everything except the `signature` field itself, serialised
via canonical JSON (RFC 8785).

### Schema

The full `run.manifest.json` structure is machine-checkable via
[`src/hypotheses/spec/schema/run-manifest.schema.json`](../../src/hypotheses/spec/schema/run-manifest.schema.json).
Additions (new artifact kinds, new summary statistics) land in the
schema first; the manifest writer in `src/hypotheses/miner/submitter.py`
(Phase 1) is expected to validate against this schema before signing.

## Synapses the miner exposes

- `GetManifest(spec_id, spec_version) -> run.manifest.json`
- `GetArtifact(cid) -> bytes` (streamed, validator-capped)
- `Heartbeat() -> { version, storage_backend, free_gb }`

Exact synapse definitions live in [09 Protocol](09-protocol.md).

## Miner etiquette and gotchas

- **Never edit a spec after running.** Propose a new version instead.
- **Don't submit a single-seed run.** Minimum `seeds_required` is declared
  in the spec; anything less will score 0 on rigor.
- **Re-runs are free to the ecosystem.** A validator's rerun costing the
  miner zero is by design; a rerun that disagrees with the miner's numbers
  is expensive for the miner.
- **Artifact size.** Keep weights out of the bundle unless the hypothesis
  explicitly requires them. The manifest can reference weight CIDs hosted
  separately.

## Self-audit

This doc is done when:

- Every CLI command listed exists as a verb in
  [14-cli.md](14-cli.md) and an MCP tool in
  [13-agent-integration.md](13-agent-integration.md).
- The artifact contract matches the manifest fields checked in
  [05 § structural validate](05-validator.md#pipeline).
- Every synapse listed exists in [09-protocol.md](09-protocol.md).
- Etiquette rules map to economic or integrity mechanisms in
  [07-incentive.md](07-incentive.md) or
  [16-threat-model.md](16-threat-model.md).

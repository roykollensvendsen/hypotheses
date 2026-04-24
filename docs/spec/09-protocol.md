---
name: protocol
description: on-chain synapses, storage contract, versioning
---

# 09 — Protocol

The on-chain wire protocol consists of a small number of Bittensor
synapses. The payloads are canonical JSON (RFC 8785), signed by the
sender's hotkey.

## Synapse: `ResultsAnnouncement`

Broadcast by a miner to announce a completed submission.

```json
{
  "type": "ResultsAnnouncement",
  "schema_version": 1,
  "hypothesis_id": "H-0001",
  "hypothesis_version": 1,
  "spec_cid": "bafy...",
  "artifact_cid": "bafy...",
  "miner_hotkey": "5F...",
  "declared_summary": {
    "flops_to_target_loss": {"median": 1.25e9, "n": 5},
    "final_test_accuracy":  {"median": 0.910,  "n": 5}
  },
  "submitted_at": "2026-04-24T10:00:00Z",
  "signature": "..."
}
```

The announcement itself contains only the CID and a summary; validators
fetch the full manifest from storage.

## Synapse: `GetManifest`

Validator → miner, to retrieve the full `run.manifest.json` for a
previously announced submission.

Request:

```json
{
  "type": "GetManifest",
  "hypothesis_id": "H-0001",
  "hypothesis_version": 1,
  "miner_hotkey": "5F..."
}
```

Response: the `run.manifest.json` payload. Signed.

## Synapse: `GetArtifact`

Validator → miner, streaming fetch of a single artifact by CID.

Request:

```json
{
  "type": "GetArtifact",
  "cid": "bafy...",
  "max_bytes": 104857600
}
```

Response: octet stream, capped by `max_bytes`. Miner may refuse oversized
artifacts; validator marks the submission failed.

## Synapse: `Heartbeat`

Validator → miner, lightweight liveness and capability check.

Response:

```json
{
  "type": "Heartbeat",
  "miner_version": "0.1.0",
  "storage_backend": "ipfs",
  "free_storage_gb": 150.3,
  "supported_profiles": ["cpu-small", "single-gpu-24gb"]
}
```

## Storage

Two separately content-addressed corpora:

- **Specs.** The `hypotheses/` directory on the `main` branch of this
  repo. CIDs are git blob hashes. Mirrored to IPFS by a periodic CI job
  so validators do not require git access to verify a spec CID.
- **Artifacts.** IPFS (default) or S3-compatible with CID-as-key. Miners
  are responsible for artifact availability until the submission settles
  and is cached by enough validators.

**TBD**: exact IPFS pinning story — whether we run a subnet-operated
pinning service for critical artifacts (manifests + metrics), or rely on
miner uptime. Lean: the subnet operates a minimal pinning service for
manifests only; miners keep bulk artifacts (weights) themselves.

## Versioning

- `schema_version` on every synapse payload. Validators reject
  unrecognised versions.
- Hypothesis format schema version lives in
  `src/hypotheses/spec/schema/hypothesis.schema.json#version`. Changes to
  that schema trigger a spec-level upgrade sweep (**TBD: migration
  policy**).
- Miner and validator CLI ship with a semver; minor bumps are
  backwards-compatible over the wire.

## Backwards compatibility

For the duration of Phase 2 (testnet), no backwards compatibility is
promised. Phase 3 (mainnet) freezes the on-wire schema at whatever is
shipping, and future changes are additive (new synapses / new optional
fields) unless a subnet-wide version bump is explicitly coordinated.

## What is NOT on the wire

- Full artifact bundles. Announcements carry CIDs only; transfer is
  out-of-band (IPFS / HTTP).
- Hypothesis specs. The canonical location is git; CIDs are what
  validators verify against.
- Code. The `experiments/<id>/` directory lives only in git; the
  `code_commit` in the manifest is the pointer.

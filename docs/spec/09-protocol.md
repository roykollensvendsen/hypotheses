---
name: protocol
description: on-chain synapses, storage contract, versioning
tokens: 800
load_for: [implementation, agent-operator, review]
depends_on: [03, 04, 05]
---

# 09 — Protocol

The on-chain wire protocol consists of a small number of Bittensor
synapses. The payloads are canonical JSON (RFC 8785), signed by the
sender's hotkey.

> **HM-REQ-0030** Every synapse payload is signed by the sending
> hotkey using ed25519 over the canonical JSON body (exclusive of the
> `signature` field). Unsigned or invalidly-signed payloads are
> rejected at the transport boundary.

> **HM-REQ-0031** Canonical JSON (RFC 8785) is the only serialisation
> admissible for signing and verification. A different byte-exact
> encoding of the same logical payload is a signature failure, not a
> tolerated variant.

## Schema

All four synapses are machine-checkable via
[`src/hypotheses/spec/schema/synapses.schema.json`](../../src/hypotheses/spec/schema/synapses.schema.json).
Each subtype is published as a `$def` (`ResultsAnnouncement`,
`GetManifest`, `GetArtifact`, `Heartbeat`) and the top-level schema is
a `oneOf` dispatch keyed on `type`. Additions go schema-first: new
fields in an existing synapse are a schema patch; new synapses are a
new `$def`. Unknown synapse `type` values are rejected per the
versioning policy below.

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

**Decision:** the subnet operator runs a kubo node that pins all
manifest CIDs (manifests are small, cap 1 MiB). Bulk artifacts (weights,
per-seed logs) are pinned only by the submitting miner and by any
validator that caches them. If a miner's bulk artifact becomes
unavailable before enough validators have cached it, subsequent
validators cannot rerun and the submission's reproduction score is
zero on cycles where the artifact is missing. This is the miner's risk
to manage.

## Versioning

- `schema_version` on every synapse payload. Validators reject
  unrecognised versions.
- Hypothesis format schema version lives in
  `src/hypotheses/spec/schema/hypothesis.schema.json#version`. **Decision:**
  no automatic spec migration. A schema-breaking change is a spec PR +
  CLI release; existing hypotheses stay at their original schema version
  and are evaluated by the CLI release that matches them. Clients refuse
  to score specs whose schema version they do not recognise.
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

## Self-audit

This doc is done when:

- Every synapse has a canonical JSON example showing all required
  fields.
- `schema_version` handling is consistent across all synapses.
- Storage semantics (manifest pinning, bulk artifact hosting) match
  [03 § storage](03-architecture.md#storage).
- Versioning policy is compatible with the decisions in
  [12 § implementation constraints](12-implementation-constraints.md).
- Every synapse the miner exposes matches
  [04 § synapses](04-miner.md#synapses-the-miner-exposes) and vice
  versa.

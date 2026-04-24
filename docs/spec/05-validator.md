---
name: validator
description: validator pipeline, rerun policy, score commitment
---

# 05 — Validator

A validator is a Bittensor neuron that verifies miner submissions, reruns a
sampled fraction, scores, and sets weights.

## Pipeline

Per validator cycle (cadence: **20 minutes**, aligned to Bittensor
epochs — revisit if an epoch changes length):

1. **Discover.** Read recent `ResultsAnnouncement` synapses from the chain.
   Filter out announcements whose `(spec_id, spec_version, miner_hotkey)`
   has already been scored in the current epoch.
2. **Fetch.** Pull the spec from the registry and `run.manifest.json` from
   the miner. Verify the miner's signature.
3. **Structural validate.**
   - Schema-validate the spec.
   - Ensure `spec_cid` in the manifest matches the current registry entry.
   - Ensure `code_commit` matches a commit that existed before
     `submitted_at` and contains `experiments/<id>/`.
   - Ensure every declared seed and condition is present in the manifest.
4. **Rerun sample.** Pick `rerun_fraction` of the declared seeds uniformly
   without replacement. **Decision:** `rerun_fraction = 0.4` uniform across
   profiles for Phase 1–2, minimum 1 seed. Per-profile tuning is a
   Phase 3 concern. The sample is seeded deterministically by
   `(validator_hotkey, epoch, spec_id, version)` so two validators
   sampling the same submission disagree about which seeds to rerun (and
   thus cover more ground collectively).
5. **Rerun.** Execute the sampled seeds in the validator's own sandbox using
   the same runtime image and env.lock. Collect metrics.
6. **Reconcile.** For each rerun metric, compare to miner-declared metric.
   Reproduction passes if
   `|validator - miner| / max(|miner|, eps) <= rerun_tolerance`.
   `rerun_tolerance` is per-metric; default 1% for accuracy-like, 5% for
   wallclock/FLOPs. Per-spec overrides allowed in the protocol section.
7. **Baseline compare.** Using the full miner-declared metric set, evaluate
   `success_criteria` and `falsification_criteria`. Statistical tests run
   against the baseline condition declared in the spec.
8. **Oracle check.** If `oracle.subnet` is set, run the oracle query and
   compare to the claimed answer within `oracle.tolerance`.
9. **Score.** Compute the composite score (see [06](06-scoring.md)).
10. **Commit weights.** Normalise scores per-miner-hotkey, set weights via
    YUMA.

## What kills a submission

A submission receives a **zero** (not just a low) score if any of these
hold:

- Manifest signature invalid.
- `code_commit` does not exist or does not contain the declared
  `experiments/<id>/`.
- Any declared seed is missing from the manifest.
- Any rerun seed falls outside `rerun_tolerance` on any declared metric.
- The entrypoint fails to run in the validator's sandbox with the declared
  env.lock.
- The oracle check, if required, fails beyond tolerance.
- The miner hotkey is the same as the validator hotkey (self-scoring).

Zeros are sticky for the `(spec_id, spec_version, miner_hotkey)` tuple
within the current epoch: a miner cannot reset a failed submission by
re-announcing.

## Validator CLI

Validator operations live under the unified `hypo` command (see
[14](14-cli.md)):

```
hypo register validator
hypo validate serve                    # long-running validator loop
hypo validate rescore <ann-cid>        # debug single submission
hypo validate audit <hotkey>           # history of a miner
```

## State each validator keeps

- Local cache of fetched specs and manifests (cleared after epoch settles).
- Sandbox image cache per hardware profile.
- `scores.db`: append-only log of `(cycle, spec_id, miner, score_vector)`.
- `weights.db`: last-committed weight vector and the inputs used to build it.

## Determinism requirement for validators

A validator's rerun of seed `s` must produce metrics within
`rerun_tolerance` of another validator's rerun of the same `s`. If
validators disagree with each other more often than with miners, either the
runtime is non-deterministic (bug in runtime) or the hypothesis's protocol
admits too much floating-point drift (the hypothesis is ill-specified and
should not have been accepted). Both are addressable: see
[08 Runtime](08-experiment-runtime.md) for the first, and tightening the
protocol-level tolerance for the second.

## Anti-collusion

- A validator MUST NOT score a submission whose `miner_hotkey` matches any
  hotkey controlled by the validator operator (enforced by the operator,
  verified by weight-vector anomaly detection across validators).
- Validators whose score vectors are persistent outliers vs consensus are
  down-weighted by the chain's YUMA mechanism. No additional subnet-side
  logic required initially; revisit after Phase 2.

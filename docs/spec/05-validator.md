---
name: validator
description: validator pipeline, rerun policy, score commitment
tokens: 1400
load_for: [implementation, agent-operator, review]
depends_on: [02, 03, 06]
---

# 05 — Validator

A validator is a Bittensor neuron that verifies miner submissions, reruns
a sampled fraction, scores, and sets weights.

## Two layers: deterministic core and operator layer

The validator splits cleanly into two layers:

### Deterministic core (pure, agent-free)

> **HM-REQ-0010** Validator scoring is a deterministic pure function
> over artifacts. Two validators on the same inputs (same manifest,
> same rerun sample) produce the same score vector.

> **HM-REQ-0011** No LLM output participates in the scoring pipeline,
> neither in rigor evaluation, reproduction tolerance checks,
> improvement calculations, nor composite aggregation.

Everything that influences the score vector. Pure functions over
artifacts: schema validation, signature verification, artifact
integrity, sandboxed rerun, statistical tests, score composition, and
weight-vector normalisation. Two validators running the same core
against the same inputs MUST produce the same score vector (modulo
validator-specific rerun sampling). **No LLM participates in this
layer.** Replacing a deterministic score with an LLM's opinion is a
spec violation.

### Operator layer (agent-orchestrated)

The process around scoring: monitoring the announcement stream,
queueing work, deciding when to sleep / resume, triaging failed
reruns, explaining score deltas to the operator, flagging anomalies
(e.g. "five miners submitted identical manifests — possible copy-
paste farm"), filing operator runbook actions. **This is where
agents live.** An agent may decide *when* or *whether* to rerun a
submission now or later, but it may not decide *what score* the
submission receives.

The interface between layers is typed: the core exposes pure functions
the operator layer calls; the operator layer never reaches into the
core to adjust a number.

## Pipeline

Per validator cycle (cadence: **20 minutes**, aligned to Bittensor
epochs — revisit if an epoch changes length):

1. **Discover.** Read recent `ResultsAnnouncement` synapses from the
   chain. Filter out announcements whose
   `(spec_id, spec_version, miner_hotkey)` has already been scored
   in the current epoch.

   <!-- canonical:announcement_rate_limit=3 -->
   **Per-hotkey rate limit:** at most **3 announcements per
   miner_hotkey per Bittensor epoch** (~72 minutes at 360 blocks
   × 12 s). Any fourth announcement in the same epoch is dropped —
   the validator records it in `events.jsonl` with reason
   `rate_limit_exceeded` and does not score it. The limit applies
   to announcements the validator observes, so a miner splitting
   across validators gains nothing; announcements hit every
   validator.

   Rationale: entry-level hypotheses on `cpu-small` take roughly an
   hour end-to-end; a miner legitimately submitting more than 3
   times per epoch is almost certainly re-announcing the same
   submission or farming novelty attempts. The limit is tuned
   generously enough that honest operators never hit it and low
   enough that spam is capped before validator cycles stall.
   Revisit once we have per-profile submission-latency data from
   Phase 2.
2. **Fetch.** Pull the spec from the registry and `run.manifest.json` from
   the miner. Verify the miner's signature.
3. **Structural validate.**
   - Schema-validate the spec.
   - Ensure `spec_cid` in the manifest matches the current registry entry.
   - Ensure `code_commit` matches a commit that existed before
     `submitted_at` and contains `experiments/<id>/`.
   - Ensure every declared seed and condition is present in the manifest.
4. **Rerun sample.** Pick `rerun_fraction` of the declared seeds uniformly
   without replacement. **Decision:** <!-- canonical:rerun_fraction=0.4 --> `rerun_fraction = 0.4` uniform across
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

```bash
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

> **HM-REQ-0012** A validator MUST NOT produce a non-zero score for
> any submission whose `miner_hotkey` matches a hotkey under the same
> operator. Self-scoring is rejected before the deterministic core
> runs.

- A validator MUST NOT score a submission whose `miner_hotkey` matches any
  hotkey controlled by the validator operator (enforced by the operator,
  verified by weight-vector anomaly detection across validators).
- Validators whose score vectors are persistent outliers vs consensus are
  down-weighted by the chain's YUMA mechanism. No additional subnet-side
  logic required initially; revisit after Phase 2.

## Acceptance scenarios

```gherkin
Scenario: Valid submission scored non-zero
  # spec: HM-REQ-0010
  Given hypothesis H-0001 at status accepted
  And a miner submits a signed manifest with 5 seeds
  And every rerun-sampled seed reproduces within rerun_tolerance
  When the validator runs its cycle
  Then the submission's composite score is non-zero
  And the score vector is byte-equal to what another validator
      running the same core with the same rerun sample would produce
```

```gherkin
Scenario: Out-of-tolerance rerun zeros the submission
  # spec: HM-REQ-0010
  Given a miner declares metric X with median 1.25e9 over 5 seeds
  And the validator reruns 2 sampled seeds
  And one rerun metric lies outside rerun_tolerance
  When the validator completes the cycle
  Then the submission's reproduction component is 0
  And the composite is computed without propagating partial credit
```

```gherkin
Scenario: Self-scoring is rejected before the core runs
  # spec: HM-REQ-0012
  Given validator V is operated by the same principal as miner hotkey M
  When the validator receives an announcement signed by M
  Then the deterministic core is not invoked for that submission
  And the rejection reason is logged as "SelfScoringRejected"
```

## Self-audit

This doc is done when:

- The "deterministic core vs. operator layer" split is referenced
  (or enforced) by every section mentioning agents.
- Every pipeline step has a named outcome and a clear next step.
- Every "what kills a submission" row maps to a typed exception in
  [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy).
- Rerun-sampling determinism is specified as a function of
  `(validator_hotkey, epoch, spec_id, version)`.
- Anti-collusion rules match the threats in
  [16 § B](16-threat-model.md#b-scoring--registry-integrity).

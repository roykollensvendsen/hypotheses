---
id: H-0003
title: "Plain SGD matches AdamW's FLOPs-to-target on a 2-layer MLP"
authors:
  - name: "repo-maintainer"
    hotkey: null
status: proposed
version: 1
created: 2026-04-24
updated: 2026-04-24

claim: >
  Plain SGD with momentum reaches 60% CIFAR-10 test accuracy in no more
  FLOPs than AdamW on a 2-layer MLP across 5 seeds.

motivation: >
  Deliberately strict claim designed to settle as `refuted` more often
  than `supported`. Demonstrates that the scoring pipeline pays rigor
  and reproduction for an honest null — refutation is not a penalty.
  Readers learning the spec see the `falsification_criteria` pathway
  exercised by a plausible hypothesis.

variables:
  - name: optimizer
    values: [sgd_momentum, adamw]
  - name: learning_rate_schedule
    values: [constant, cosine]

metrics:
  - name: flops_to_target_acc
    units: flops
    target_direction: minimize
  - name: final_test_accuracy
    units: ratio
    target_direction: maximize

baselines:
  - name: adamw_cosine
    optimizer: adamw
    learning_rate_schedule: cosine

protocol:
  dataset: cifar10
  dataset_revision: "huggingface:uoft-cs/cifar10@0b2714987fa478483af9968de7c934580d0bb9a2"
  model_family: mlp-2-layer
  model_config_ref: experiments/H-0003/model.yaml
  seeds: [0, 1, 2, 3, 4]
  max_steps: 20000
  hardware_profile: cpu-small
  code_ref: experiments/H-0003/
  entrypoint: experiments/H-0003/run.py

success_criteria:
  - metric: flops_to_target_acc
    operator: lte
    vs_baseline: adamw_cosine
    threshold_ratio: 1.00
    statistical_test: welch_t
    p_max: 0.01
    seeds_required: 5

falsification_criteria:
  - metric: flops_to_target_acc
    operator: gte
    vs_baseline: adamw_cosine
    threshold_ratio: 1.15
    statistical_test: welch_t
    p_max: 0.05

oracle:
  subnet: null
  task_ref: null
  tolerance: null

depends_on: []
contradicts: []
---

# Discussion

## Purpose

H-0003 is the canonical refutation-pathway example. The claim
("plain SGD matches AdamW") is something most ML practitioners would
expect to fail on a 2-layer MLP with CIFAR-10 in 20K steps — AdamW's
adaptive learning rates typically produce faster convergence to the
same target.

The hypothesis exists so readers see:

- `success_criteria` and `falsification_criteria` as mirror images,
- the scoring pipeline's treatment of a submission that meets the
  falsification criterion (rigor and reproduction still pay; the
  claim is simply marked `settled-refuted`),
- `oracle: null` at the object level — explicit, not omitted.

## Why it should refute

AdamW on a well-normalized MLP typically reaches 60% CIFAR-10 test
accuracy in 10–15k steps at reasonable learning rates. Plain SGD
with momentum at a carefully-tuned learning rate can match *in
wallclock* but typically requires more total FLOPs because of
smaller effective per-step progress on complex loss surfaces.

A miner who submits this hypothesis honestly will likely observe
refutation: `flops_to_target_acc` for SGD ≥ 1.15 × AdamW's baseline
FLOPs at p < 0.05.

## Why it might not refute

There are optimizer-configuration choices under which SGD outscales
AdamW on this task — especially short-horizon training with
aggressive learning-rate tuning. A miner who cares about the
positive result would sweep learning rates; one who cares about
the honest null would use canonical defaults.

Either outcome settles the hypothesis honestly. The spec requires
preregistration of the criteria, not of a specific result.

## Scoring interaction

From [`06-scoring.md § improvement`](../docs/spec/06-scoring.md#improvement):

- If `success_criteria` is met → `settled-supported`, improvement
  scores per the formula.
- If `falsification_criteria` is met → `settled-refuted`,
  improvement = 0 but rigor + reproduction + novelty still pay.
- If neither → the submission scores normally against current
  composite but doesn't transition the hypothesis state.

The key point: a miner who runs this in good faith and observes
refutation still earns (rigor + reproduction + novelty - cost)
without the improvement component. A documented null is not a
zero score.

## Known limitations

- The specific `threshold_ratio: 1.15` in the falsification
  criterion is plausible-on-reflection, not simulation-calibrated.
- The 20K-step budget is tight; either optimizer might fail to hit
  60% in all seeds on `cpu-small`. In that case the run itself
  fails (no `flops_to_target_acc` emitted) and the submission
  scores zero regardless of optimizer choice — a design flaw in
  this hypothesis that a real submitter would bump to a larger
  profile or a longer budget before claiming anything.

## Follow-ups

If H-0003 settles refuted on the initial 5-seed run, a version-2
hypothesis could narrow the claim: "SGD matches AdamW on the subset
of the hyperparameter space where both optimizers receive
equivalent tuning compute" — with a stricter protocol defining
what "equivalent tuning compute" means.

---
id: H-0004
kind: hypothesis
title: "SNIP-pruned init beats gradient-magnitude edge decay at matched final density on a 2-layer MLP"
authors:
  - name: "repo-maintainer"
    hotkey: null
status: proposed
version: 1
created: 2026-04-25
updated: 2026-04-25

claim: >
  A 2-layer MLP whose connectivity is selected once at initialisation by
  SNIP (single-shot pruning by |g·w| saliency) to target final density d
  reaches 60% CIFAR-10 test accuracy in fewer training FLOPs than the
  H-0001 mechanism (gradient-magnitude edge decay from fully-connected,
  masked to the same d) across 5 seeds.

motivation: >
  Addresses reviewer feedback on H-0001 that `sparse_random` is too weak
  a baseline to draw conclusions from. SNIP is widely cited, deterministic
  on fixed seeds, and runs inside `cpu-small` because the saliency score
  is computed once at init from a single mini-batch's gradient. Either
  outcome is informative: if H-0001's edge-decay rule beats SNIP at
  matched density, the rule earns credibility against a real opponent;
  if SNIP wins, the registry has surfaced a stronger sparsification
  starting point and H-0001 v2 (or a successor) can adopt it.

variables:
  - name: connectivity_method
    values: [snip, edge_decay]

metrics:
  - name: flops_to_target_acc
    units: flops
    target_direction: minimize
  - name: final_test_accuracy
    units: ratio
    target_direction: maximize

baselines:
  - name: edge_decay_baseline
    connectivity_method: edge_decay

protocol:
  dataset: cifar10
  dataset_revision: "huggingface:uoft-cs/cifar10@0b2714987fa478483af9968de7c934580d0bb9a2"
  model_family: mlp-2-layer
  model_config_ref: experiments/H-0004/model.yaml
  seeds: [0, 1, 2, 3, 4]
  max_steps: 20000
  hardware_profile: cpu-small
  code_ref: experiments/H-0004/
  entrypoint: experiments/H-0004/run.py

success_criteria:
  - metric: flops_to_target_acc
    operator: lte
    vs_baseline: edge_decay_baseline
    threshold_ratio: 0.80
    statistical_test: welch_t
    p_max: 0.01
    seeds_required: 5

falsification_criteria:
  - metric: flops_to_target_acc
    operator: gte
    vs_baseline: edge_decay_baseline
    threshold_ratio: 1.00
    statistical_test: welch_t
    p_max: 0.05

oracle:
  subnet: null
  task_ref: null
  tolerance: null

depends_on: [H-0001]
contradicts: []
---

# Discussion

## Purpose

H-0004 stress-tests H-0001's mechanism against a *real* sparsification
opponent rather than `sparse_random`. SNIP — Single-shot Network
Pruning at initialisation (Lee et al., 2019) — is the canonical
"pick the connections once, then train" method: it scores each weight
by `|g · w|` against a single mini-batch's gradient at init, keeps
the top fraction by saliency, and trains the masked subnetwork to
convergence.

H-0001's claim ("edge decay beats sparse-random") and H-0004's claim
("SNIP beats edge decay") can both be true; together they imply the
ranking `SNIP > edge_decay > sparse_random`. The hypothesis carries
`depends_on: [H-0001]` to anchor the family relationship.

## Why SNIP is the right opponent for cpu-small

- **Deterministic.** Given a seeded data-loader, the saliency batch
  and resulting mask are byte-reproducible across runs, so the
  validator's rerun-tolerance budget is comfortable.
- **Cheap.** One forward+backward at init, top-k by saliency, fix
  mask. All overhead is amortised before training begins.
- **A real opponent.** Unlike `sparse_random`, SNIP carries gradient
  information from the actual loss landscape at init. The result
  isn't trivially predictable.
- **Fits the wallclock cap.** The training cost is identical to the
  H-0001 sparse_random condition at the same final density (same
  number of active edges per step), so the per-seed wallclock is in
  range for `cpu-small`.

## What "matched final density" means

Both conditions train at the same final density `d` (set in
`model.yaml`, default 0.25 to match H-0001's `target_final_density`):

- **`snip` condition**: at init, score every weight by `|g · w|`
  using one mini-batch of size `saliency_batch_size`; keep the top
  `d * |W|` by score; mask is fixed for training; standard SGD on
  the survivors.
- **`edge_decay` condition**: identical to the H-0001 fully-connected
  plus gradient-decay condition, masked to the same `d` via threshold.

FLOPs accounting is per `08-experiment-runtime.md`: masked edges
count zero. SNIP's one-shot gradient batch is included in
`flops_to_target_acc` for fairness — it is part of the cost of
selecting the topology.

## Expected outcome

The literature is mixed. SNIP performs comparably to magnitude
pruning at moderate densities (d ≥ 0.1) on CNN/ResNet benchmarks;
on small MLPs the gap is task-dependent. We do not predict the
outcome — that is the point of preregistration. What we *do* predict
is that the result will be informative either way:

- **SNIP wins (success criterion met):** Random's intuition is
  validated; a successor hypothesis (or H-0001 v2) should adopt
  SNIP-style init.
- **Edge decay wins (falsification criterion met):** H-0001's rule
  earns credibility against a real opponent; the "training-time
  destruction" framing in `VISION.md` pillar 1 has empirical support.
- **Neither (statistical test fails to reject at the chosen p):**
  honest null; the rule choice is not the bottleneck on this
  problem at this scale.

## Known limitations

- Same scale limitation as H-0001 (CIFAR-10 + 2-layer MLP is far
  below interesting scale). Conclusions transfer only weakly to
  ConvNets, transformers, or larger MLPs.
- `saliency_batch_size` is a hyperparameter SNIP is sensitive to;
  `model.yaml` pins one value — sweeping it would require a v2.
- The `0.80` success threshold is plausible-on-reflection rather
  than calibrated by simulation.

## Follow-ups

- H-0007 (sketch): same comparison at multiple densities (`d ∈
  {0.1, 0.25, 0.5}`) to see whether the verdict flips with sparsity
  level.
- H-0008 (sketch): SNIP vs IMP (iterative magnitude pruning), to
  see whether iterative refinement matters once you start from a
  good init.

## Reviewer note

This hypothesis is the "stop racing sleeping turtles" half of
reviewer feedback against H-0001. The internal-rule half ships as
H-0005 (L1, literal interpretation of the suggestion) and H-0006
(RigL, the more vision-aligned variant).

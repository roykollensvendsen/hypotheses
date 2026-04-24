---
id: H-0001
title: "Connectivity-first training: pruning beats sparse init on a 2-layer MLP"
authors:
  - name: "repo-maintainer"
    hotkey: null
status: proposed
version: 1
created: 2026-04-24
updated: 2026-04-24

claim: >
  A fully-connected 2-layer MLP trained on CIFAR-10 with gradient-magnitude
  edge decay, pruned to a target final density, reaches 60% test accuracy in
  fewer training FLOPs than a sparse-random initialisation of the same final
  density trained to the same accuracy.

motivation: >
  Establishes a small, tractable first test of the connectivity-first frame.
  The hypothesis is deliberately modest (small model, weak accuracy bar) to
  serve as the end-to-end test fixture for the subnet implementation. If it
  holds at all, a stronger version belongs in a follow-up hypothesis.

variables:
  - name: init_topology
    values: [fully_connected, sparse_random]
  - name: edge_dynamics
    values: [none, gradient_decay]

metrics:
  - name: flops_to_target_acc
    units: flops
    target_direction: minimize
  - name: final_test_accuracy
    units: ratio
    target_direction: maximize

baselines:
  - name: sparse_baseline
    init_topology: sparse_random
    edge_dynamics: none

protocol:
  dataset: cifar10
  dataset_revision: "huggingface:uoft-cs/cifar10@0b2714987fa478483af9968de7c934580d0bb9a2"
  model_family: mlp-2-layer
  model_config_ref: experiments/H-0001/model.yaml
  seeds: [0, 1, 2, 3, 4]
  max_steps: 20000
  hardware_profile: cpu-small
  code_ref: experiments/H-0001/
  entrypoint: experiments/H-0001/run.py

success_criteria:
  - metric: flops_to_target_acc
    operator: lte
    vs_baseline: sparse_baseline
    threshold_ratio: 0.80
    statistical_test: welch_t
    p_max: 0.01
    seeds_required: 5

falsification_criteria:
  - metric: flops_to_target_acc
    operator: gte
    vs_baseline: sparse_baseline
    threshold_ratio: 1.00
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

This hypothesis doubles as the subnet's canonical end-to-end fixture. Its
design goals, in order:

1. **Runs on `cpu-small`** — so CI can execute it.
2. **Deterministic enough** to rerun within tolerance without a GPU.
3. **Plausibly falsifiable** in either direction.
4. **Cheap** — whole sweep fits in the profile's wallclock cap.

It is not designed to produce new research insight; a stronger experiment
belongs in H-0002+ once the subnet can run bigger profiles reliably.

## What the experiment does

- **MLP**: input (3072) → hidden (256) → output (10), ReLU, no bias on the
  hidden layer (keeps the "edges" clean).
- **Full-connected condition**: every hidden-unit-to-input edge exists at
  init. Gradient decay multiplies each edge's weight by
  `(1 − η · |∇L/∇w|)` every optimizer step (decoupled from the optimizer
  update itself). Edges below magnitude threshold `τ` are masked out
  permanently. Sweep picks the final density to match
  `sparse_random`'s density for a fair comparison.
- **Sparse-random condition**: the same final density is sampled uniformly
  at init and fixed.
- **Target accuracy**: 60% on the held-out test split.
- **FLOPs counter**: ptflops-equivalent, masked edges count zero.

## Why it is a useful fixture

- Reproduction test: two validators running seed 2 should get
  `flops_to_target_acc` within 5% of each other.
- Rigor test: all eight checks in the rigor table evaluate to 1.0 on
  this spec.
- Scoring test: covers support, falsification, and tie paths depending
  on the concrete numbers the harness produces.

## Known limitations

- CIFAR-10 + a 2-layer MLP is far below interesting scale.
- Gradient-magnitude decay is one of many possible decay rules; picking
  it here is arbitrary but documented.
- A fully-connected input layer on CIFAR-10 is ~790K edges, which on
  `cpu-small` is tight. If the runtime can't hit the wallclock cap, bump
  the hardware profile to `cpu-large` and bump `version`.

## Follow-ups (not part of this hypothesis)

- H-0002: same, but gradient-decay vs magnitude pruning at a fixed budget.
- H-0003: add attention-gated edges as a third condition.
- H-0004: move to convolutional models; connectivity becomes filter-level.

---
id: H-0006
title: "RigL-style coupled grow/drop edge dynamics beat gradient-magnitude edge decay at matched final density on a 2-layer MLP"
authors:
  - name: "repo-maintainer"
    hotkey: null
status: proposed
version: 1
created: 2026-04-25
updated: 2026-04-25

claim: >
  A 2-layer MLP trained with RigL (Rigging the Lottery: periodic drop
  of low-magnitude active edges + grow of high-gradient-magnitude
  inactive edges, maintaining target density d throughout training)
  reaches 60% CIFAR-10 test accuracy in fewer training FLOPs than the
  H-0001 mechanism (gradient-magnitude edge decay from fully-connected,
  masked to the same d) across 5 seeds.

motivation: >
  The vision-aligned half of reviewer feedback against H-0001. RigL
  (Evci et al., 2020) is an internal sparsification rule that
  maintains a fixed sparsity budget and *both* destroys and constructs
  edges during training — exactly the "coupled dynamical system of
  construction and destruction" framing in `VISION.md` pillar 1. L1
  (H-0005) only shrinks; RigL grows and shrinks. If RigL settles
  supported, the connectivity-first framing has its first piece of
  empirical support inside this registry. If it settles refuted,
  H-0001's external manager is harder to dismiss.

variables:
  - name: connectivity_method
    values: [rigl, edge_decay]

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
  model_config_ref: experiments/H-0006/model.yaml
  seeds: [0, 1, 2, 3, 4]
  max_steps: 20000
  hardware_profile: cpu-small
  code_ref: experiments/H-0006/
  entrypoint: experiments/H-0006/run.py

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

H-0006 is the most-faithful instantiation of the connectivity-first
framing in `VISION.md` pillar 1: a single local rule that
simultaneously *constructs* and *destructs* connectivity during
training, treating the topology as a first-class state variable
that evolves alongside the weights.

Where L1 (H-0005) only ever shrinks, and where H-0001's edge decay
runs as a separate manager on top of the optimizer, RigL is one
coherent procedure that:

1. trains the active subnetwork normally for `update_interval`
   steps,
2. drops the bottom `drop_fraction` of active edges by `|w|`,
3. grows the same number of currently-inactive edges chosen by
   `|gradient|` (computed dense for the grow step only),
4. repeats.

Density is held at the target `d` throughout — there is no "train
dense then prune" phase, no smooth-shrinkage approximation, no
external mask manager.

## Why this is the right vision-aligned variant

`VISION.md` pillar 1: "Construction and destruction of connectivity
are a coupled dynamical system. Classical methods can be reframed
as special cases: gradient descent = edge-strength adjustment,
dropout = stochastic edge removal, attention = dynamic flow routing,
pruning = destructive edge selection."

L1 captures destruction-only. RigL captures both halves with a
local rule. It is the simplest published method that meets the
"coupled" criterion at training time — most others (lottery-ticket
rewinding, IMP) require multiple full training passes and would
not fit the cpu-small wallclock cap.

## What "matched final density" means

Both conditions land at the same final density `d` (default 0.25
in `model.yaml`):

- **`rigl` condition**: at init, sample a uniform random mask at
  density `d`. Every `update_interval` steps, drop the bottom
  `drop_fraction` of active edges by `|w|` and grow the top
  `drop_fraction * |W_active|` currently-inactive edges by
  `|gradient|` (the grow step computes a dense gradient once for
  this purpose, then returns to sparse training). The mask schedule
  decays `drop_fraction` over training so late-training topology
  changes are smaller.
- **`edge_decay` condition**: identical to H-0001's fully-connected
  + gradient-decay condition.

FLOPs accounting per `08-experiment-runtime.md`: dense gradient
computations during grow steps count fully. The active subnetwork's
sparse forward+backward counts at the active-edge cost. RigL's grow
overhead is one dense gradient every `update_interval` steps — small
relative to the wall of sparse forward+backwards in between.

## Expected outcome

Honest priors:

- **RigL wins:** the published RigL paper (Evci et al., 2020)
  reports matching dense baselines at d ≤ 0.1 on ResNet-50 / CIFAR-
  10, and beating IMP at the same FLOPs budget. On a 2-layer MLP
  the relative advantage is likely smaller — fewer "lottery
  tickets" to rotate through — but a non-trivial improvement over
  edge-decay-from-dense is the median expectation.
- **Edge decay wins:** plausible if the dense gradient cost per
  grow step dominates on a small MLP, or if the random init
  topology drags down early training enough that RigL never
  recovers within 20k steps.
- **Honest null:** the threshold/falsification zone where the
  Welch's-t test cannot reject either direction.

## Known limitations

- `update_interval`, `drop_fraction`, and the drop-fraction decay
  schedule are RigL hyperparameters known to be non-trivially
  tuned. `model.yaml` pins one set; a v2 would sweep them.
- Same MLP-on-CIFAR-10 scale caveat as H-0001 / H-0004 / H-0005.
- The grow step's "dense gradient" requirement is the most
  expensive part of RigL on this profile. If wallclock is tight,
  using a sub-batch for the grow gradient is a published shortcut
  but introduces noise — left out of v1 to keep the comparison
  clean.

## Comparison to L1 (H-0005)

- **L1**: destruction-only, smooth-shrinkage during dense training,
  external mask at end.
- **RigL**: construction + destruction, sparse training throughout,
  internal grow + drop with no separate masking phase.

If both H-0005 and H-0006 settle, the comparison is informative on
its own: a parity result for L1 with a dominance result for RigL
would imply that the *coupled* aspect (not just being "internal")
is what matters.

## Follow-ups

- H-0010 (sketch) — same RigL comparison at multiple densities to
  see whether the verdict flips with sparsity level.
- H-0011 (sketch) — RigL vs H-0001's edge-decay rule on a small
  ConvNet; tests whether the grow/drop story generalises beyond
  fully-connected layers.

## Reviewer note

H-0006 is the vision-aligned successor to the literal-L1 hypothesis
H-0005. Both depend_on: [H-0001]. H-0004 addresses the orthogonal
"stronger baseline" feedback. None of the three contradict H-0001.

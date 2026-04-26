---
id: H-0005
kind: hypothesis
title: "L1-induced sparsification matches gradient-magnitude edge decay at matched final density on a 2-layer MLP"
authors:
  - name: "repo-maintainer"
    hotkey: null
status: proposed
version: 1
created: 2026-04-25
updated: 2026-04-25

claim: >
  A 2-layer MLP trained with an L1 weight penalty (λ * Σ|w|) and a
  final magnitude mask to density d reaches 60% CIFAR-10 test accuracy
  in no more training FLOPs than the H-0001 mechanism (gradient-
  magnitude edge decay from fully-connected, masked to the same d)
  across 5 seeds.

motivation: >
  Addresses reviewer feedback that the sparsification rule should be
  baked into the loss function rather than imposed by a separate
  edge-dynamics manager. L1 is the most direct interpretation of
  "let the network decide which connections to drop" — it is a
  classical regulariser, well understood, and produces a smoothly-
  varying density profile during training. The claim is phrased as
  parity (`<= 1.00`) rather than dominance because L1 is the *least*
  topology-shaped internal rule (see discussion); a stronger
  internal-rule hypothesis (RigL) ships separately as H-0006.

variables:
  - name: connectivity_method
    values: [l1_then_mask, edge_decay]

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
  model_config_ref: experiments/H-0005/model.yaml
  seeds: [0, 1, 2, 3, 4]
  max_steps: 20000
  hardware_profile: cpu-small
  code_ref: experiments/H-0005/
  entrypoint: experiments/H-0005/run.py

success_criteria:
  - metric: flops_to_target_acc
    operator: lte
    vs_baseline: edge_decay_baseline
    threshold_ratio: 1.00
    statistical_test: welch_t
    p_max: 0.05
    seeds_required: 5

falsification_criteria:
  - metric: flops_to_target_acc
    operator: gte
    vs_baseline: edge_decay_baseline
    threshold_ratio: 1.20
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

H-0005 addresses the "let the network decide" half of reviewer
feedback against H-0001 — specifically, the suggestion that the
sparsification rule should sit inside the loss function rather than
on top of the optimizer.

The literal reading is **L1 weight regularisation**: add `λ * Σ|w|`
to the loss; gradient descent then naturally shrinks weights with
small contribution to loss. Apply a final magnitude mask to convert
the smooth shrinkage into a discrete topology. No external edge-
dynamics manager runs during training.

## Why a parity claim, not a dominance claim

L1 is the most-classical internal sparsification rule, but it has
two properties that make it a *weak* candidate for "topology
evolution":

1. **L1 never actually removes edges during training.** It drives
   weights toward zero asymptotically, but never crosses zero
   without an external thresholding operation. Realising the
   topology change still requires a "mask weights below ε" step at
   the end. The external step is just hidden inside the optimiser
   loop.
2. **L1 is destruction-only.** No mechanism for *constructing*
   connectivity exists in the rule. The vision pillar in
   `VISION.md` frames topology evolution as a *coupled* dynamical
   system of construction + destruction; L1 captures only one half.

The dominance claim ("L1 beats edge decay") would over-promise. The
parity claim ("L1 matches edge decay") is the honest framing: if it
holds, the simpler rule is preferable for engineering reasons; if
it fails by a wide margin, the engineered edge-dynamics manager has
an empirical advantage worth preserving.

## What "matched final density" means

Both conditions land at the same final density `d` (default 0.25
in `model.yaml`):

- **`l1_then_mask` condition**: training loss is
  `cross_entropy(model(x), y) + lambda_l1 * sum(|w|)`; at end of
  training, mask all weights with `|w| < magnitude_threshold` to
  reach `d`. `lambda_l1` is calibrated so the natural distribution
  of magnitudes at the end of training already implies density `d`
  at the threshold; the threshold is sweep-tuned per seed during
  development, not at scoring time.
- **`edge_decay` condition**: identical to H-0001's fully-connected
  plus gradient-decay condition.

FLOPs accounting per `08-experiment-runtime.md`: for the
`l1_then_mask` condition, all edges are active during training (the
network is dense throughout), which means the per-step FLOPs cost
is **higher** than the `edge_decay` condition's masked cost. This
is the central tension the claim tests: does the simpler rule pay
its way despite running denser for longer?

## Expected outcome

Honest priors:

- **L1 wins narrowly:** plausible if the magnitude distribution at
  end-of-training cleanly bimodal-separates the survivors from the
  victims. Cross-entropy + L1 on simple MLPs has a long history of
  producing this shape at moderate `lambda_l1`.
- **Edge decay wins:** plausible if the per-step FLOPs cost of
  training dense for 20k steps exceeds the savings from the simpler
  rule. The edge-decay condition starts dense but reaches its
  target density quickly, then trains masked.
- **Honest null:** the `>= 1.00` and `< 1.20` zone where the
  Welch's-t test cannot reject either the null or the falsification
  criterion. A documented null is still a useful settlement.

## Known limitations

- L1 with weight magnitude masking at `d = 0.25` requires careful
  `lambda_l1` calibration to actually realise density 0.25 at a
  reasonable `magnitude_threshold`. `model.yaml` pins values; a
  miner who finds the calibration unstable across seeds should bump
  `version` rather than tweak per submission.
- Same MLP-on-CIFAR-10 scale caveat as H-0001 / H-0004.
- The `0.20` falsification margin is plausible-on-reflection, not
  simulation-calibrated.

## Follow-ups

- H-0006 (already drafted) — RigL coupled grow/drop, the more
  vision-aligned internal rule. If L1 settles supported and RigL
  also settles supported, the next interesting question is which
  internal rule generalises to ConvNets / transformers.
- H-0009 (sketch) — same comparison with `lambda_l1` swept across
  a small grid, treating the sweep itself as the variable.

## Reviewer note

H-0005 is the literal "L1" interpretation of the reviewer's
suggestion. H-0006 is the more vision-aligned RigL variant. H-0004
addresses the orthogonal feedback (stronger baseline). All three
carry `depends_on: [H-0001]` and none contradict it.

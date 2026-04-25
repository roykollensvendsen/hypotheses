# H-0006 experiment

Executable experiment for the `H-0006` hypothesis (see
`../../hypotheses/H-0006-rigl-vs-edge-decay.md`).

## Files

- `run.py` — entrypoint; implements the contract in
  `../../docs/spec/08-experiment-runtime.md#entrypoint-contract`.
- `model.yaml` — MLP architecture, optimiser config, and per-method
  connectivity hyperparameters (`rigl.update_interval`,
  `rigl.drop_fraction_initial`, `rigl.drop_fraction_decay`,
  `edge_decay.eta` / `mask_threshold`).
- `pyproject.toml` — pinned experiment-local deps.

## Running locally

Not runnable until the `hypotheses` runtime package is implemented.
Invocation contract (from Phase 1 onward):

```bash
hypo run H-0006 --seed 0
```

## What it does

Trains a 2-layer MLP on CIFAR-10 to a 60% test-accuracy target,
under one of two `connectivity_method` conditions at the same final
density `d`:

- `rigl` — uniform random sparse mask at init; every
  `update_interval` steps, drop the bottom `drop_fraction` of
  active edges by `|w|` and grow the same number of inactive edges
  by `|gradient|` (gradient is computed dense for this step only).
  `drop_fraction` decays over training.
- `edge_decay` — H-0001's mechanism: fully-connected init, gradient-
  magnitude edge decay each step, threshold mask.

Reports `flops_to_target_acc` (per the FLOPs accounting in
`08-experiment-runtime.md`; dense gradient steps during RigL grow
phases count fully) and `final_test_accuracy`.

## Why this is the vision-aligned variant

RigL is the simplest published method that maintains a fixed
sparsity budget while *both* destroying and constructing edges
during training — matching `VISION.md` pillar 1's "coupled
dynamical system of construction and destruction" framing. L1
(H-0005) is destruction-only; H-0001's edge decay runs as an
external manager on top of the optimizer.

## Calibration note

`update_interval` and `drop_fraction_initial` are RigL hyper-
parameters that affect the wallclock cost on cpu-small. The values
in `model.yaml` are conservative starting points; a v2 hypothesis
could sweep them. Per-submission tuning is not the contract — the
spec freezes the values at scoring time.

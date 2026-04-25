# H-0005 experiment

Executable experiment for the `H-0005` hypothesis (see
`../../hypotheses/H-0005-l1-vs-edge-decay.md`).

## Files

- `run.py` — entrypoint; implements the contract in
  `../../docs/spec/08-experiment-runtime.md#entrypoint-contract`.
- `model.yaml` — MLP architecture, optimiser config, and per-method
  connectivity hyperparameters (`l1.lambda`, `l1.magnitude_threshold`,
  `edge_decay.eta` / `mask_threshold`).
- `pyproject.toml` — pinned experiment-local deps.

## Running locally

Not runnable until the `hypotheses` runtime package is implemented.
Invocation contract (from Phase 1 onward):

```bash
hypo run H-0005 --seed 0
```

## What it does

Trains a 2-layer MLP on CIFAR-10 to a 60% test-accuracy target,
under one of two `connectivity_method` conditions at the same final
density `d`:

- `l1_then_mask` — adds `lambda_l1 * sum(|w|)` to the loss, trains
  dense throughout, then applies a final magnitude mask at
  `magnitude_threshold` to realise the topology change.
- `edge_decay` — H-0001's mechanism: fully-connected init, gradient-
  magnitude edge decay each step, threshold mask.

Reports `flops_to_target_acc` (per the FLOPs accounting in
`08-experiment-runtime.md`) and `final_test_accuracy`. Note that
the `l1_then_mask` condition is dense throughout training so its
per-step FLOPs are higher than the `edge_decay` condition's masked
cost.

## Calibration note

`lambda_l1` and `magnitude_threshold` are jointly responsible for
realising `target_final_density = 0.25` at the end of training.
Calibration is a development-time concern, not a per-submission
tweak — a miner who finds the calibration unstable across seeds
should bump `version` and revise rather than tune at scoring time.

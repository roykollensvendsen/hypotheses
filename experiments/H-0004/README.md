# H-0004 experiment

Executable experiment for the `H-0004` hypothesis (see
`../../hypotheses/H-0004-snip-vs-edge-decay.md`).

## Files

- `run.py` — entrypoint; implements the contract in
  `../../docs/spec/08-experiment-runtime.md#entrypoint-contract`.
- `model.yaml` — MLP architecture, optimiser config, and per-method
  connectivity hyperparameters (`snip.saliency_batch_size`,
  `edge_decay.eta` / `mask_threshold`).
- `pyproject.toml` — pinned experiment-local deps.

## Running locally

Not runnable until the `hypotheses` runtime package is implemented.
Invocation contract (from Phase 1 onward):

```
hypo run H-0004 --seed 0
```

## What it does

Trains a 2-layer MLP on CIFAR-10 to a 60% test-accuracy target,
under one of two `connectivity_method` conditions at the same final
density `d`:

- `snip` — single-shot pruning by `|g·w|` saliency at init, mask
  fixed for training.
- `edge_decay` — H-0001's mechanism: fully-connected init, gradient-
  magnitude edge decay each step, threshold mask.

Reports `flops_to_target_acc` (masked edges count zero) and
`final_test_accuracy`. The validator's scoring pipeline interprets
these per the success and falsification criteria in the hypothesis
spec.

## Relation to H-0001

H-0004 reuses H-0001's MLP architecture and optimiser exactly; the
only deliberate difference is the `connectivity_method` variable.
This keeps the comparison clean.

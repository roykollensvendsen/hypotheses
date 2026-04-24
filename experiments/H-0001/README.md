# H-0001 experiment

Executable fixture for the `H-0001` hypothesis (see
`../../hypotheses/H-0001-connectivity-first-training.md`).

## Files

- `run.py` — entrypoint; implements the contract in
  `../../docs/spec/08-experiment-runtime.md#entrypoint-contract`.
- `model.yaml` — MLP architecture and optimiser config.
- `pyproject.toml` — pinned experiment-local deps.

## Running locally

Not runnable until the `hypotheses` runtime package is implemented.
Invocation contract (from Phase 1 onward):

```
hypo-miner run H-0001 --seed 0
```

The runtime materialises the env from this directory's `pyproject.toml`,
mounts the directory into the sandbox, and executes `run.py` via
`Run.from_env().execute(main)`.

## Role in the codebase

This experiment is the canonical end-to-end fixture: the smoke test in
`tests/integration/smoke_submit_score.py` runs the full
miner→validator→scoring loop against it. Changes here affect CI.

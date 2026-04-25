<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# H-0003 experiment

Executable scaffold for the `H-0003` hypothesis (see
`../../hypotheses/H-0003-sgd-matches-adam-on-mlp.md`).

H-0003 is the canonical **refutation-pathway** example. The
experiment's code is symmetric in the two optimizer choices and
reports FLOPs-to-target and final test accuracy so the scoring
pipeline can evaluate both success and falsification criteria.

## Files

- `run.py` — entrypoint stub, symmetric on `optimizer` and
  `learning_rate_schedule`.
- `model.yaml` — the MLP + optimizer configs.
- `pyproject.toml` — experiment-local deps.

## Running locally

Not runnable until Phase 1. When the runtime exists:

```bash
hypo run H-0003 --seeds all
```

The miner submits whatever metrics the run produces, honestly. The
scoring pipeline then either flips the hypothesis to
`settled-supported` (if success criteria met) or `settled-refuted`
(if falsification criteria met).

See the
[hypothesis file](../../hypotheses/H-0003-sgd-matches-adam-on-mlp.md)
for the full claim and the
[scoring spec](../../docs/spec/06-scoring.md) for the payoff
breakdown in either outcome.

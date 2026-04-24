<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# H-0002 experiment

Executable scaffold for the `H-0002` hypothesis (see
`../../hypotheses/H-0002-oracle-verified-distillation.md`).

Oracle-backed hypotheses have an additional dependency: the oracle
adapter. This experiment cannot run end-to-end until the SN42
adapter ships (Phase 2). The hypothesis spec validates today; the
experiment's `run.py` is a stub matching the Phase-0 `H-0001`
pattern.

## Files

- `run.py` — entrypoint stub.
- `model.yaml` — student and teacher MLP configs.
- `pyproject.toml` — experiment-local deps.

## Interaction with the oracle

The entrypoint produces predictions on the SN42 task-0 test split;
it does NOT query the oracle directly. Validator scoring pulls the
manifest, extracts the `declared_answer` for each seed, and the
oracle adapter (in `src/hypotheses/oracle/sn42.py` — Phase 2)
queries SN42 for agreement.

See [`docs/spec/18-oracle.md`](../../docs/spec/18-oracle.md) for
the full contract.

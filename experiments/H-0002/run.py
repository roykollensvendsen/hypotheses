# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Entrypoint for hypothesis H-0002 (oracle-verified distillation).

Design stub. Compiles once the `hypotheses.runtime` package is
implemented in Phase 1 and the SN42 adapter ships in Phase 2.

Reports per-seed predictions on SN42 task-0's test split; the
validator's oracle adapter compares them against SN42's ground
truth independently.
"""

from __future__ import annotations

from hypotheses.runtime import Run, metrics


def main(run: Run) -> None:
    cfg = run.load_config("model.yaml")
    cond = run.condition
    data = run.load_dataset()

    teacher = train_teacher(cfg["teacher"], cfg["training"], run.seed, data)
    student = distill_student(
        teacher,
        cfg["student"],
        cfg["training"],
        cfg["distillation"][cond["distillation_method"]],
        run.seed,
        data,
    )

    predictions = predict_on_sn42_task0(student, run)
    run.attach_declared_answer(predictions)

    agreement_rate, abs_err_mean = compute_agreement_offline(student, data)
    metrics.report("oracle_agreement_rate", agreement_rate)
    metrics.report("absolute_answer_error_mean", abs_err_mean)


def train_teacher(cfg, training_cfg, seed, data):
    raise NotImplementedError


def distill_student(teacher, student_cfg, training_cfg, method_cfg, seed, data):
    raise NotImplementedError


def predict_on_sn42_task0(model, run):
    raise NotImplementedError


def compute_agreement_offline(model, data):
    raise NotImplementedError


if __name__ == "__main__":
    Run.from_env().execute(main)

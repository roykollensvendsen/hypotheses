# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Entrypoint for hypothesis H-0003 (SGD vs AdamW FLOPs-to-target).

Design stub. Compiles once the `hypotheses.runtime` package is
implemented in Phase 1.

Runs one (optimizer, schedule) condition and reports
`flops_to_target_acc` + `final_test_accuracy`. The scoring pipeline
uses these metrics to either support or refute the hypothesis's
claim. The implementing agent is expected to fill in the training
loop symmetrically for both optimizers.
"""

from __future__ import annotations

from hypotheses.runtime import Run, metrics


def main(run: Run) -> None:
    cfg = run.load_config("model.yaml")
    cond = run.condition
    optim_cfg = cfg["optimizers"][cond["optimizer"]]
    sched_cfg = cfg["schedules"][cond["learning_rate_schedule"]]
    data = run.load_dataset()

    model = build_mlp(cfg, run.seed)
    optimizer = build_optimizer(model, optim_cfg)
    scheduler = build_scheduler(optimizer, sched_cfg)
    flops = FlopsCounter(model)

    reached = False
    for step in range(cfg["training"]["max_steps"]):
        batch = next(data.train_iter)
        loss, grads = forward_backward(model, batch)
        apply_optimizer_step(optimizer, model, grads)
        scheduler.step()
        flops.tick(model)

        if step % 200 == 0:
            acc = evaluate(model, data.test_iter)
            if acc >= cfg["training"]["target_accuracy"] and not reached:
                metrics.report("flops_to_target_acc", flops.total)
                reached = True

    final_acc = evaluate(model, data.test_iter)
    metrics.report("final_test_accuracy", final_acc)
    if not reached:
        metrics.report("flops_to_target_acc", float("inf"))


def build_mlp(cfg, seed):
    raise NotImplementedError


def build_optimizer(model, cfg):
    raise NotImplementedError


def build_scheduler(optimizer, cfg):
    raise NotImplementedError


def forward_backward(model, batch):
    raise NotImplementedError


def apply_optimizer_step(optimizer, model, grads):
    raise NotImplementedError


def evaluate(model, test_iter):
    raise NotImplementedError


class FlopsCounter:
    def __init__(self, model):
        raise NotImplementedError

    def tick(self, model):
        raise NotImplementedError

    @property
    def total(self) -> float:
        raise NotImplementedError


if __name__ == "__main__":
    Run.from_env().execute(main)

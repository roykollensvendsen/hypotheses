# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Entrypoint for hypothesis H-0001.

This file is a design stub. It encodes the entrypoint contract from
docs/spec/08-experiment-runtime.md and will compile once the
`hypotheses.runtime` package is implemented in Phase 1. The implementing
agent is expected to fill in the MLP training loop and connectivity
dynamics to match the hypothesis spec.
"""

from __future__ import annotations

from hypotheses.runtime import Run, metrics


def main(run: Run) -> None:
    seed = run.seed
    cond = run.condition
    cfg = run.load_config("model.yaml")
    data = run.load_dataset()

    model = build_mlp(cfg, cond, seed)
    flops_counter = FlopsCounter(model)

    reached_target = False
    for step in range(cfg["training"]["max_steps"]):
        batch = next(data.train_iter)
        loss, grads = forward_backward(model, batch)
        apply_optimizer_step(model, grads, cfg)

        if cond["edge_dynamics"] == "gradient_decay":
            apply_gradient_decay(model, grads, cfg)
            apply_mask_threshold(model, cfg)

        flops_counter.tick(model)

        if step % 200 == 0:
            acc = evaluate(model, data.test_iter)
            if acc >= cfg["training"]["target_accuracy"] and not reached_target:
                metrics.report("flops_to_target_acc", flops_counter.total)
                reached_target = True

    final_acc = evaluate(model, data.test_iter)
    metrics.report("final_test_accuracy", final_acc)
    if not reached_target:
        metrics.report("flops_to_target_acc", float("inf"))


def build_mlp(cfg: dict, cond: dict, seed: int):
    raise NotImplementedError


def forward_backward(model, batch):
    raise NotImplementedError


def apply_optimizer_step(model, grads, cfg):
    raise NotImplementedError


def apply_gradient_decay(model, grads, cfg):
    raise NotImplementedError


def apply_mask_threshold(model, cfg):
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

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Entrypoint for hypothesis H-0005 (L1-induced sparsification vs edge decay).

Design stub. Compiles once the `hypotheses.runtime` package is
implemented in Phase 1.

Runs one (`connectivity_method`) condition at matched final density
and reports `flops_to_target_acc` + `final_test_accuracy`. The
`l1_then_mask` condition trains dense throughout with an L1 weight
penalty in the loss, then applies a final magnitude mask to reach
the target density. The `edge_decay` condition mirrors H-0001.
"""

from __future__ import annotations

from hypotheses.runtime import Run, metrics


def main(run: Run) -> None:
    cfg = run.load_config("model.yaml")
    cond = run.condition
    data = run.load_dataset()

    model = build_mlp(cfg, run.seed)
    flops = FlopsCounter(model)

    reached = False
    for step in range(cfg["training"]["max_steps"]):
        batch = next(data.train_iter)
        loss, grads = forward_backward(
            model,
            batch,
            l1_lambda=cfg["connectivity"]["l1"]["lambda"]
            if cond["connectivity_method"] == "l1_then_mask"
            else 0.0,
        )
        apply_optimizer_step(model, grads, cfg)

        if cond["connectivity_method"] == "edge_decay":
            apply_gradient_decay(model, grads, cfg)
            apply_mask_threshold(model, cfg)

        flops.tick(model)

        if step % 200 == 0:
            acc = evaluate(model, data.test_iter)
            if acc >= cfg["training"]["target_accuracy"] and not reached:
                metrics.report("flops_to_target_acc", flops.total)
                reached = True

    if cond["connectivity_method"] == "l1_then_mask":
        # Final magnitude mask realises the topology change L1 only
        # hinted at during training.
        apply_magnitude_mask(model, cfg["connectivity"]["l1"]["magnitude_threshold"])

    final_acc = evaluate(model, data.test_iter)
    metrics.report("final_test_accuracy", final_acc)
    if not reached:
        metrics.report("flops_to_target_acc", float("inf"))


def build_mlp(cfg, seed):
    raise NotImplementedError


def forward_backward(model, batch, l1_lambda: float):
    raise NotImplementedError


def apply_optimizer_step(model, grads, cfg):
    raise NotImplementedError


def apply_gradient_decay(model, grads, cfg):
    raise NotImplementedError


def apply_mask_threshold(model, cfg):
    raise NotImplementedError


def apply_magnitude_mask(model, threshold: float):
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

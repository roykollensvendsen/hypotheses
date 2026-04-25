# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Entrypoint for hypothesis H-0004 (SNIP vs gradient-magnitude edge decay).

Design stub. Compiles once the `hypotheses.runtime` package is
implemented in Phase 1.

Runs one (`connectivity_method`) condition at matched final density
and reports `flops_to_target_acc` + `final_test_accuracy`. The
implementing agent fills in `select_snip_mask` and reuses H-0001's
`apply_gradient_decay` / `apply_mask_threshold` for the edge-decay
condition.
"""

from __future__ import annotations

from hypotheses.runtime import Run, metrics


def main(run: Run) -> None:
    cfg = run.load_config("model.yaml")
    cond = run.condition
    data = run.load_dataset()

    model = build_mlp(cfg, run.seed)
    flops = FlopsCounter(model)

    if cond["connectivity_method"] == "snip":
        # Single-shot: score |g·w| against one mini-batch, keep top-k.
        saliency_batch = next(data.train_iter)
        mask = select_snip_mask(model, saliency_batch, cfg)
        apply_mask(model, mask)
        flops.tick(model)  # SNIP's selection batch counts toward FLOPs.

    reached = False
    for step in range(cfg["training"]["max_steps"]):
        batch = next(data.train_iter)
        loss, grads = forward_backward(model, batch)
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

    final_acc = evaluate(model, data.test_iter)
    metrics.report("final_test_accuracy", final_acc)
    if not reached:
        metrics.report("flops_to_target_acc", float("inf"))


def build_mlp(cfg, seed):
    raise NotImplementedError


def select_snip_mask(model, batch, cfg):
    raise NotImplementedError


def apply_mask(model, mask):
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

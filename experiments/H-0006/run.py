# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Entrypoint for hypothesis H-0006 (RigL coupled grow/drop vs edge decay).

Design stub. Compiles once the `hypotheses.runtime` package is
implemented in Phase 1.

Runs one (`connectivity_method`) condition at matched final density
and reports `flops_to_target_acc` + `final_test_accuracy`. The
`rigl` condition starts from a uniform random sparse mask at
density d, then every `update_interval` steps drops the bottom
`drop_fraction` of active edges and grows the same number of
inactive edges by `|gradient|`. The `edge_decay` condition mirrors
H-0001.
"""

from __future__ import annotations

from hypotheses.runtime import Run, metrics


def main(run: Run) -> None:
    cfg = run.load_config("model.yaml")
    cond = run.condition
    data = run.load_dataset()

    model = build_mlp(cfg, run.seed)
    flops = FlopsCounter(model)

    if cond["connectivity_method"] == "rigl":
        # Init at target density via uniform random mask.
        mask = init_random_mask(model, cfg["connectivity"]["target_final_density"])
        apply_mask(model, mask)

    update_interval = cfg["connectivity"]["rigl"]["update_interval"]
    reached = False
    for step in range(cfg["training"]["max_steps"]):
        batch = next(data.train_iter)
        loss, grads = forward_backward(model, batch)
        apply_optimizer_step(model, grads, cfg)

        if (
            cond["connectivity_method"] == "rigl"
            and step > 0
            and step % update_interval == 0
        ):
            # Coupled grow/drop step. The grow gradient is computed
            # dense for this step only; flops counter accounts for it.
            dense_grads = compute_dense_gradient(model, batch)
            flops.tick_dense(model)
            mask = rigl_update(
                model,
                mask,
                dense_grads,
                step,
                cfg["connectivity"]["rigl"],
                cfg["training"]["max_steps"],
            )
            apply_mask(model, mask)

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


def init_random_mask(model, density: float):
    raise NotImplementedError


def apply_mask(model, mask):
    raise NotImplementedError


def forward_backward(model, batch):
    raise NotImplementedError


def apply_optimizer_step(model, grads, cfg):
    raise NotImplementedError


def compute_dense_gradient(model, batch):
    raise NotImplementedError


def rigl_update(model, mask, dense_grads, step: int, rigl_cfg, max_steps: int):
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

    def tick_dense(self, model):
        raise NotImplementedError

    @property
    def total(self) -> float:
        raise NotImplementedError


if __name__ == "__main__":
    Run.from_env().execute(main)

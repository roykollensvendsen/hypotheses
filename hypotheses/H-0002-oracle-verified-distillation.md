---
id: H-0002
kind: hypothesis
title: "Distilled 2-layer MLP preserves SN42 task-0 accuracy within oracle tolerance"
authors:
  - name: "repo-maintainer"
    hotkey: null
status: proposed
version: 1
created: 2026-04-24
updated: 2026-04-24

claim: >
  A 2-layer MLP distilled from a 3-layer teacher produces predictions on
  SN42 task-0's public test split that agree with the SN42 oracle's
  ground-truth answers within 0.05 absolute error across 5 seeds.

motivation: >
  Canonical example of an oracle-backed hypothesis. Demonstrates the
  `oracle` field and the SN42 adapter's task-ref format. Pedagogically
  useful even before the adapter is implemented; the spec validates,
  the structure is correct, and the hypothesis settles once the SN42
  adapter ships (Phase 2).

variables:
  - name: distillation_method
    values: [vanilla_logits, feature_matching]

metrics:
  - name: oracle_agreement_rate
    units: ratio
    target_direction: maximize
  - name: absolute_answer_error_mean
    units: ratio
    target_direction: minimize

baselines:
  - name: teacher_only
    distillation_method: vanilla_logits

protocol:
  dataset: cifar10
  dataset_revision: "huggingface:uoft-cs/cifar10@0b2714987fa478483af9968de7c934580d0bb9a2"
  model_family: mlp-2-layer
  model_config_ref: experiments/H-0002/model.yaml
  seeds: [0, 1, 2, 3, 4]
  max_steps: 20000
  hardware_profile: cpu-small
  code_ref: experiments/H-0002/
  entrypoint: experiments/H-0002/run.py

success_criteria:
  - metric: oracle_agreement_rate
    operator: gte
    vs_baseline: teacher_only
    threshold_ratio: 1.00
    statistical_test: welch_t
    p_max: 0.01
    seeds_required: 5

falsification_criteria:
  - metric: absolute_answer_error_mean
    operator: gte
    vs_baseline: teacher_only
    threshold_ratio: 1.10
    statistical_test: welch_t
    p_max: 0.05

oracle:
  subnet: 42
  task_ref: "sn42:0"
  tolerance: 0.05

depends_on: []
contradicts: []
---

# Discussion

## Purpose

H-0002 is the canonical oracle-backed example. It exists so readers
of the spec see:

- a non-null `oracle` block with all three required fields,
- a claim phrased as "answers match the oracle within tolerance"
  rather than as "metric X lower than baseline,"
- how the hypothesis interacts with
  [18 — Oracle contract](../docs/spec/18-oracle.md) semantics.

## SN42 specifics

The SN42 adapter lands in Phase 2 (see
[`docs/spec/18-oracle.md#sn42-adapter-first-implementation`](../docs/spec/18-oracle.md#sn42-adapter-first-implementation)).
Until then, validators reject this hypothesis's oracle queries with
`NotImplementedError`; the submission remains `pending` per
[`18-oracle.md § outage-handling`](../docs/spec/18-oracle.md#outage-handling).
The spec itself still validates today.

## Tolerance

`oracle.tolerance = 0.05` is the absolute-error envelope. For a
numeric classification task this means the answer's predicted
probability may differ from the oracle's ground truth by at most
0.05 and still agree. Interpretation is the SN42 adapter's
responsibility; see
[`18-oracle.md § SN42 adapter`](../docs/spec/18-oracle.md#sn42-adapter-first-implementation).

## Expected outcome

If the distillation captures enough of the teacher's behaviour, the
student's agreement rate on SN42 task-0 approaches the teacher's
baseline. If distillation drifts, absolute-error grows and the
falsification criterion fires. Either settlement is a valid
research outcome.

## Known limitations

- SN42 task-0's specifics are TBD until the adapter exists; the
  protocol's `dataset` and `dataset_revision` reflect CIFAR-10 as a
  placeholder training split. The oracle query itself is SN42's
  responsibility, independent of how the student was trained.
- On `cpu-small`, distillation of a 3-layer teacher into a 2-layer
  student finishes inside the 5-minute wallclock cap per seed only
  for small hidden dimensions. `model.yaml` picks a dim that fits.

## Follow-ups

- H-0004: same claim, consensus-answer oracle class once one exists.
- H-0005: distillation with stochastic teachers (would require
  oracle-composition to rule out variance in the teacher itself).

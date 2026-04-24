---
id: H-XXXX
title: "short sentence describing the hypothesis"
authors:
  - name: "your handle"
    hotkey: null
status: proposed
version: 1
created: YYYY-MM-DD
updated: YYYY-MM-DD

claim: >
  One sentence, falsifiable, relational to a declared baseline.

motivation: >
  Why the answer matters. Keep it short.

variables:
  - name: example_variable
    values: [value_a, value_b]

metrics:
  - name: example_metric
    units: ratio
    target_direction: maximize

baselines:
  - name: default_baseline
    example_variable: value_a

protocol:
  dataset: TBD
  dataset_revision: TBD
  model_family: TBD
  model_config_ref: experiments/H-XXXX/model.yaml
  seeds: [0, 1, 2]
  max_steps: TBD
  hardware_profile: TBD
  code_ref: experiments/H-XXXX/
  entrypoint: experiments/H-XXXX/run.py

success_criteria:
  - metric: example_metric
    operator: gte
    vs_baseline: default_baseline
    threshold_ratio: 1.05
    statistical_test: welch_t
    p_max: 0.01
    seeds_required: 3

falsification_criteria:
  - metric: example_metric
    operator: lte
    vs_baseline: default_baseline
    threshold_ratio: 1.00
    statistical_test: welch_t
    p_max: 0.05

oracle:
  subnet: null
  task_ref: null
  tolerance: null

depends_on: []
contradicts: []
---

# Discussion

Replace this section with the free-form body: background, prior art,
intuition, risks, expected follow-ups if the claim is supported or refuted.

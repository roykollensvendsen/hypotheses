---
name: hypothesis format
description: preregistration-style schema for hypothesis specs stored in hypotheses/
---

# 02 — Hypothesis format

## File location and naming

One hypothesis per file under `hypotheses/`:

```
hypotheses/H-0001-connectivity-first-training.md
hypotheses/H-0002-gradient-decay-edge-pruning.md
```

Filename: `H-<4-digit id>-<kebab-slug>.md`. IDs are allocated in PR order
(first merged PR gets the next free ID). Slugs are informational; the id is
canonical.

## File structure

Each hypothesis file has YAML front matter followed by a markdown body:

```markdown
---
<spec fields>
---

# Discussion

<free-form markdown>
```

Only the front matter is consumed by miners/validators. The body is for human
reviewers.

## Spec fields

All fields are required unless marked optional.

```yaml
id: H-0001
title: "Connectivity-first training: pruning as the generative act"
authors:
  - name: "handle or real name"
    hotkey: "5F..."           # Bittensor SS58; optional on proposals, required on results
status: proposed
  # proposed | accepted | running | settled-supported | settled-refuted | withdrawn
version: 1                    # bump on any post-acceptance change; resets results
created: 2026-04-24
updated: 2026-04-24

# The falsifiable claim. One sentence. No hedging.
claim: >
  A fully-connected MLP pruned by gradient-magnitude edge decay reaches 90%
  CIFAR-10 test accuracy with fewer training FLOPs than a sparse-random
  initialisation of the same final edge count.

motivation: >
  Short paragraph. Why does the answer matter? What broader question does it
  illuminate? References allowed; no essay.

# Independent variables — what the experiment sweeps over.
variables:
  - name: init_topology
    values: [fully_connected, sparse_random, lottery_ticket]
  - name: edge_dynamics
    values: [none, gradient_decay, attention_gated]

# Dependent variables — what is measured.
metrics:
  - name: flops_to_target_loss
    units: flops
    target_direction: minimize
  - name: final_test_accuracy
    units: ratio
    target_direction: maximize

# At least one baseline is required. Baselines are points in the variable
# space, not separate hypotheses.
baselines:
  - name: sparse_dense_default
    init_topology: sparse_random
    edge_dynamics: none

# Exact execution parameters. Enough to rerun without questions.
protocol:
  dataset: cifar10
  dataset_revision: "huggingface:uoft-cs/cifar10@<commit>"
  model_family: mlp-2-layer
  model_config_ref: experiments/H-0001/model.yaml
  seeds: [0, 1, 2, 3, 4]
  max_steps: 50000
  hardware_profile: single-gpu-24gb   # see runtime spec for allowed profiles
  code_ref: experiments/H-0001/       # path in this repo; must exist at submit time
  entrypoint: experiments/H-0001/run.py

# What counts as support for the claim.
success_criteria:
  - metric: flops_to_target_loss
    operator: lte
    vs_baseline: sparse_dense_default
    threshold_ratio: 0.80
    statistical_test: welch_t
    p_max: 0.01
    seeds_required: 5

# What counts as refutation. Non-empty; at least one condition.
falsification_criteria:
  - metric: flops_to_target_loss
    operator: gte
    vs_baseline: sparse_dense_default
    threshold_ratio: 1.00
    statistical_test: welch_t
    p_max: 0.05

# Optional: ground-truth oracle check. Null when no oracle applies.
oracle:
  subnet: null                # e.g. 42
  task_ref: null              # oracle-specific task identifier
  tolerance: null

# Optional: hypotheses this one builds on or challenges.
depends_on: []
contradicts: []
```

## Schema validation

- Front matter is validated against the JSON Schema at
  [`src/hypotheses/spec/schema/hypothesis.schema.json`](../../src/hypotheses/spec/schema/hypothesis.schema.json).
- Every PR that touches `hypotheses/` runs
  [`scripts/validate_hypotheses.py`](../../scripts/validate_hypotheses.py)
  in CI via
  [`.github/workflows/spec-validate.yml`](../../.github/workflows/spec-validate.yml).
- [`scripts/check_schema_matches_doc.py`](../../scripts/check_schema_matches_doc.py)
  extracts the worked-example YAML block below and confirms it
  validates against the schema. If the doc and schema drift, CI
  fails.
- Any hypothesis MUST pass validation to merge, regardless of
  `status`. `HYPOTHESIS_TEMPLATE.md` is excluded from validation
  (it carries placeholder enum values that are not valid hypothesis
  values).

## Versioning and immutability

- The `id` is immutable.
- Any change to `claim`, `variables`, `metrics`, `baselines`, `protocol`,
  `success_criteria`, `falsification_criteria`, or `oracle` requires
  `version` to increment. All prior results for that hypothesis are
  invalidated and must be re-run against the new version.
- Status transitions (`proposed → accepted → running → settled-*`) do not
  bump version.
- `withdrawn` is terminal; a withdrawn hypothesis may be replaced by a new
  one that lists it in `contradicts`.

## The template

A copy-paste starter lives at `hypotheses/HYPOTHESIS_TEMPLATE.md`.

## What a hypothesis is *not*

- A general research question. ("What if connectivity is the ground state?")
  These are valuable but belong in `docs/research-notes/`, not `hypotheses/`.
- A benchmark leaderboard entry. The claim must be *relational* (vs. a
  declared baseline), not absolute.
- A method paper. Methods come in via the `code_ref` + discussion body; the
  spec is the contract, not the implementation.

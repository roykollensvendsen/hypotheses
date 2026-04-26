---
name: hypothesis format
description: preregistration-style schema for hypothesis specs stored in hypotheses/
tokens: 2700
load_for: [implementation, proposal, review]
depends_on: [01]
kind: contract
---

# 02 — Hypothesis format

## File location and naming

One hypothesis per file under `hypotheses/`:

```text
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
kind: hypothesis
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

## Optional fields

The schema admits two further optional fields. Both default to "absent
= mechanical default applies"; agents and parsers treat missing values
as no-op rather than as schema errors. They become *effectively
required* under [HM-REQ-0050](#schema-validation) and
[HM-REQ-0060](#schema-validation) at scoring time once Phase 1 ships.

### `analysis_plan`

A pre-analysis plan, in the [JPE 2024 sense](https://www.journals.uchicago.edu/doi/10.1086/730455):
generic preregistration without an analysis plan does not reduce
p-hacking; detailed analysis plans do. Every analytic decision the
miner will make is preregistered here.

```yaml
analysis_plan:
  pre_processing: "metrics computed from the last evaluation step only; no smoothing"
  exclusion_criteria:
    - "any seed whose run was sandbox-killed before reaching max_steps is excluded"
  multiple_comparisons: bonferroni      # none | bonferroni | holm | fdr_bh | fdr_by
  missing_seed_policy: fail             # fail | exclude | impute_median
```

### `external_anchor`

An explicit external-verifiability anchor. Defaults to the implicit
mechanical case (the metrics in `success_criteria` are computable
from artifacts alone). Declare explicitly only when the anchor is
an oracle reference or a public benchmark.

```yaml
# implicit default; equivalent to no field
external_anchor:
  type: mechanical
```

```yaml
# oracle reference (mirrors the existing `oracle` block)
external_anchor:
  type: oracle
  subnet: 42
  task_ref: "sn42:0"
  tolerance: 0.05
```

```yaml
# public benchmark with content-hash pinning
external_anchor:
  type: public_benchmark
  url: "https://paperswithcode.com/sota/image-classification-on-cifar-10"
  content_hash: "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  metric: top1_accuracy
```

### `verification`

Verification mode declares how validators check the
submission. Two values:

- **`full-rerun`** *(default)* — the standard model.
  Validator reruns a `rerun_fraction` sample of the declared
  seeds in its own sandbox and compares metrics within
  tolerance. The reproduction component scores agreement.
- **`oracle-only`** — the validator skips the rerun and
  scores the reproduction component from a single oracle
  query. Available only when the hypothesis declares an
  `oracle` block (or `external_anchor.type=oracle`); the
  oracle's verdict IS the ground truth, so reproducing
  seeds adds nothing.

```yaml
verification: oracle-only
```

The mode trades two things for one. Lost: the validator's
independent compute on the [artifact](01-glossary.md#artifact)
(sampling + reruns); the ability to detect dishonest
single-seed runs from the artifact alone. Gained: validator workload independent of
`N_miners`, so the asymmetric break-even ceiling from
[ADR 0017](../adr/0017-validator-unit-economics.md) does not
apply to this class. The oracle is the trust boundary;
[HM-REQ-0080](18-oracle.md#composition) (oracle composition)
still applies, and a single-oracle declaration carries the
F3 oracle-corruption risk per
[`00.5 § F3`](00.5-foundations.md#f3--oracle-corruption).

**When to use.** Hypotheses where the truth is externally
observable and the oracle is the canonical source —
prediction markets, sports outcomes, sensor measurements,
public benchmarks with content-hash pinning. **When not
to use.** Hypotheses about computational properties of an
artifact (training-run efficiency, pruning ratio,
loss-trajectory shape) — those need full rerun because the
artifact's behaviour is the claim.

### `sponsorship`

A counterparty-funded bounty paid on settlement. **Required**
for hypotheses whose `hardware_profile` is in the
[gated tier](06-scoring.md#profile-tiers); optional for safe-
tier hypotheses (which are funded by emission alone). The
gate exists because validator break-even at heavy profiles
fails outside the cheap-profile regime — see
[ADR 0017](../adr/0017-validator-unit-economics.md) and
[ADR 0019](../adr/0019-viability-verdict-not-viable-as-designed.md).

The block admits two shapes: **single sponsor** (legacy form)
and **community pool** (multiple sponsors). The community
form is introduced by ADR 0022 and widens the funnel of
[c8-sponsorship-demand](00.5-foundations.md#c8-sponsorship-demand)
satisfiers from a single counterparty to a pool of
≥ 2 contributors per HM-REQ-0140.

#### Single sponsor

```yaml
sponsorship:
  sponsor_id: "researchhub:0xABC..."   # opaque identifier; counterparty-defined
  bounty_tao: 5.0                      # paid on settlement
  split:                                # (miner, validators, treasury); sums to 1.0
    miner: 0.60
    validators: 0.30
    treasury: 0.10
  escrow_block: 1234567                 # block height bounty was locked
```

#### Community pool

```yaml
sponsorship:
  sponsors:                            # array form; one or more contributors
    - sponsor_id: "5F1abc..."          # SS58 hotkey is the canonical identifier
      bounty_tao: 1.0
    - sponsor_id: "5G2def..."
      bounty_tao: 0.5
    - sponsor_id: "researchhub:0xABC..."
      bounty_tao: 3.5
  split:
    miner: 0.60
    validators: 0.30
    treasury: 0.10
  escrow_block: 1234567                 # cutoff after which contributions close
```

`bounty_tao` (single form) or the sum of
`sponsors[].bounty_tao` (community form) determines the total
pool. Splits and the `escrow_block` cutoff apply identically.
After settlement, the miner / validators / treasury shares
are computed from the total and distributed; sponsors do not
directly track per-sponsor recipients.

**F7 anti-manipulation cap.** No single `sponsor_id`
contributes more than 50 % of the total `bounty_tao` after
the `escrow_block` cutoff fires. A community pool that fails
this check is rejected per HM-REQ-0140 below. The cap defends
against whale-steering per
[`00.5 § F7`](00.5-foundations.md#f7--curation-manipulation);
PR-E.5's calibration ratchet revises the threshold based on
Phase 2 pool data.

The split defaults to `(0.60, 0.30, 0.10)` per
[`27 § G open question 2`](27-economic-strategy.md#g-open-questions);
declared explicitly here so per-sponsor variations remain
auditable. The validator share of the bounty supplements
emission-side dividends, restoring break-even at heavy
profiles.

## Schema validation

> **HM-REQ-0001** Hypothesis front matter is governed by
> [`src/hypotheses/spec/schema/hypothesis.schema.json`](../../src/hypotheses/spec/schema/hypothesis.schema.json).
> The schema is the contract; a hypothesis that does not validate
> does not merge.

> **HM-REQ-0050** A hypothesis MUST declare an `analysis_plan`
> object specifying every analytic decision the miner will make
> (pre-processing, exclusion criteria, multiple-comparisons
> correction, missing-seed policy). Generic preregistration without
> analysis-plan detail does not reduce p-hacking
> ([JPE 2024](https://www.journals.uchicago.edu/doi/10.1086/730455));
> the analysis plan operationalises the finding. Phase 0 hypotheses
> grandfather without the field; Phase 1 scoring rejects submissions
> against hypotheses that lack one.

> **HM-REQ-0120** A hypothesis whose `hardware_profile` is in the
> [gated tier](06-scoring.md#profile-tiers) (`single-gpu-*` or
> `multi-gpu-*`) MUST declare a `sponsorship` block. A gated-tier
> hypothesis lacking sponsorship is rejected at acceptance.
> Safe-tier hypotheses (`cpu-small`, `cpu-large`) declare
> sponsorship only when a counterparty wishes to fund them
> additionally. The gate operationalises ADR 0019's
> tier-2 pivot: validator break-even at heavy profiles fails on
> emission alone, so heavy profiles must carry their own
> bounty per
> [`27 § C.1`](27-economic-strategy.md#c1-sponsored-hypotheses).

> **HM-REQ-0130** A hypothesis declaring `verification:
> oracle-only` MUST declare an `oracle` block (or
> `external_anchor.type=oracle`). A hypothesis with
> `verification: oracle-only` and no oracle reference is
> rejected at acceptance — the verification mode requires the
> oracle that defines its trust boundary. The default
> `verification: full-rerun` carries no such constraint.
> Operationalises ADR 0021's third viability path beyond the
> safe-tier and sponsor-gated tier.

> **HM-REQ-0140** A `sponsorship` block declaring `sponsors`
> (community-pool form) MUST satisfy: (a) every entry has a
> non-empty `sponsor_id` and `bounty_tao > 0`; (b) no single
> `sponsor_id` contributes more than 50 % of the sum of
> `sponsors[].bounty_tao` after the `escrow_block` cutoff;
> (c) at least 2 distinct `sponsor_id` values are present.
> A community pool that fails any condition is rejected at
> acceptance. Defends F7 (curation manipulation) per
> [`00.5 § F7`](00.5-foundations.md#f7--curation-manipulation).
> The single-sponsor form is unconstrained by HM-REQ-0140.

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

> **HM-REQ-0002** A `ResultsAnnouncement` against `(id, version)` is
> valid only if the spec at that version was committed to `main`
> strictly before the announcement's `submitted_at`. Results
> "announced against a future spec" are rejected by the validator.

> **HM-REQ-0003** Incrementing `version` invalidates every prior
> submission against the earlier version; reruns under the new
> version start novelty, rigor, reproduction, and improvement
> accounting from scratch.

- The `id` is immutable.
- Any change to `claim`, `variables`, `metrics`, `baselines`, `protocol`,
  `success_criteria`, `falsification_criteria`, or `oracle` requires
  `version` to increment. All prior results for that hypothesis are
  invalidated and must be re-run against the new version.
- Status transitions (`proposed → accepted → running → settled-*`) do not
  bump version.
- `withdrawn` is terminal; a withdrawn hypothesis may be replaced by a new
  one that lists it in `contradicts`.

The full state machine — every transition, who can trigger it, side
effects, edge cases — is specified in
[17 — Hypothesis lifecycle](17-hypothesis-lifecycle.md).

## The template

A copy-paste starter lives at `hypotheses/HYPOTHESIS_TEMPLATE.md`.

## What a hypothesis is *not*

- A general research question. ("What if connectivity is the ground state?")
  These are valuable but belong in `docs/research-notes/`, not `hypotheses/`.
- A benchmark leaderboard entry. The claim must be *relational* (vs. a
  declared baseline), not absolute.
- A method paper. Methods come in via the `code_ref` + discussion body; the
  spec is the contract, not the implementation.

## Acceptance scenarios

Machine-readable Gherkin cases exercising this doc's normative
statements. Phase 1 parses these via
`tests/acceptance/test_hypothesis_format.py` into parametrised cases.

```gherkin
Scenario: Valid hypothesis validates against the schema
  # spec: HM-REQ-0001
  Given a hypothesis file hypotheses/H-0001-connectivity-first-training.md
  And the file's front matter matches the worked example in § spec fields
  When scripts/validate_hypotheses.py runs against the repository
  Then the hypothesis validates with exit code 0
```

```gherkin
Scenario: Missing required field is rejected
  # spec: HM-REQ-0001
  Given a hypothesis with protocol.seeds removed from front matter
  When scripts/validate_hypotheses.py runs against the file
  Then the exit code is non-zero
  And the error references the missing "seeds" field
```

```gherkin
Scenario: Version bump invalidates prior settlement
  # spec: HM-REQ-0003
  Given hypothesis H-0001 is at version 1 and settled-supported
  And the maintainer bumps version to 2 with a changed protocol.max_steps
  When a validator scores a new submission against version 2
  Then the submission's novelty accounting starts from scratch for version 2
  And prior settled-supported status on version 1 does not populate novelty
```

## Self-audit

This doc is done when:

- Every field documented here has a corresponding entry in the
  JSON Schema at `src/hypotheses/spec/schema/hypothesis.schema.json`
  (enforced by `scripts/check_schema_matches_doc.py`).
- The worked-example YAML block validates against the schema
  (CI-enforced).
- Versioning + lifecycle behaviour link to
  [17-hypothesis-lifecycle.md](17-hypothesis-lifecycle.md) rather
  than restating it.
- Every field in the example either exercises a schema constraint
  or is necessary for a miner to understand the format.
- The `HYPOTHESIS_TEMPLATE.md` matches the fields listed here.

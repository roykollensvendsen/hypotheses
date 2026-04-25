---
name: invariants index
description: catalogue of HM-INV properties the implementation must preserve
tokens: 600
load_for: [implementation, review]
depends_on: []
kind: reference
---

# Invariants index

Every **HM-INV-NNNN** tag names a property the implementation must
preserve. Unlike HM-REQ normative statements (which describe what
the system must do), invariants describe what must *remain true* as
the system evolves under its allowed transitions.

Phase 1 test code uses the [Hypothesis](https://hypothesis.readthedocs.io)
library to enforce each HM-INV as a property-based test; the tests
live under `tests/properties/` and link back via a
`# spec: HM-INV-NNNN` comment.

## Index

| ID | Doc | Short statement | Phase 1 test location |
|----|-----|-----------------|------------------------|
| HM-INV-0001 | [17](17-hypothesis-lifecycle.md) | Preregistration: no announcement for `(id, version)` scored before that `(id, version)` exists on `main` | `tests/properties/test_lifecycle.py::test_preregistration` |
| HM-INV-0002 | [17](17-hypothesis-lifecycle.md) | Immutability: fields at `(id, version)` never change post-merge except `status` and `updated` | `tests/properties/test_lifecycle.py::test_immutability` |
| HM-INV-0003 | [17](17-hypothesis-lifecycle.md) | Version ordering: `version` is strictly increasing per `id` | `tests/properties/test_lifecycle.py::test_version_ordering` |
| HM-INV-0004 | [17](17-hypothesis-lifecycle.md) | Terminal per version: `settled-*` is terminal within its own `(id, version)` | `tests/properties/test_lifecycle.py::test_terminal_per_version` |
| HM-INV-0005 | [17](17-hypothesis-lifecycle.md) | Withdrawal absorbing: `withdrawn` is terminal across all versions of that `id` | `tests/properties/test_lifecycle.py::test_withdrawal_absorbing` |
| HM-INV-0006 | [17](17-hypothesis-lifecycle.md) | Author-can-withdraw: an author can withdraw a not-yet-settled hypothesis without maintainer approval | `tests/properties/test_lifecycle.py::test_author_withdraw` |
| HM-INV-0010 | [06](06-scoring.md) | Composite bounds: composite(s) ∈ [−w_cost, w_rigor + w_reproduction + w_improvement + w_novelty] for any legal component vector | `tests/properties/test_scoring.py::test_composite_bounds` |
| HM-INV-0011 | [06](06-scoring.md) | Novelty non-increase: for a fixed `(id, version)`, novelty is strictly non-increasing in settlement order (1.0 → 0.5 → 0.0) | `tests/properties/test_scoring.py::test_novelty_non_increase` |
| HM-INV-0012 | [06](06-scoring.md) | Improvement saturation: `improvement(s, H) ∈ [0, 1]` for any spec H and submission s; 0 when the statistical test fails, 1 when observed effect ≥ target effect | `tests/properties/test_scoring.py::test_improvement_saturation` |
| HM-INV-0020 | [08](08-experiment-runtime.md) | Determinism: for identical `(spec, seed, hardware_profile, env.lock)`, `metrics.jsonl` is byte-identical across runs | `tests/properties/test_runtime.py::test_determinism_bytes` |
| HM-INV-0021 | [08](08-experiment-runtime.md) | Dataset pin: declared `dataset_revision` matches the fetched blob's content hash on every load | `tests/properties/test_runtime.py::test_dataset_hash_pin` |

## How to add

1. Pick the next free HM-INV ID in the relevant cluster (00xx
   lifecycle, 01xx scoring, 02xx runtime, 03xx protocol, ...).
2. Insert a block-quote at the invariant's canonical home in the
   spec: `> **HM-INV-NNNN** <one-sentence statement>`.
3. Add a row here.
4. Reference it from the Hypothesis-library property test via a
   `# spec: HM-INV-NNNN` comment.

## Interaction with HM-REQ

Some invariants implement specific requirements (e.g. HM-INV-0010
derives bounds from HM-REQ-0020's formula). The checker does not
enforce parent→child links today — that structure may land in a
later PR if it earns its keep.

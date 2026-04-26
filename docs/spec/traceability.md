---
name: traceability matrix
description: HM-REQ-NNNN to test-id mapping; populated as Phase 1 ships tests
tokens: 400
load_for: [implementation, review]
depends_on: []
kind: reference
---

# Traceability matrix

Each normative requirement (HM-REQ-NNNN) maps to a test that
asserts it. Phase 0 ships the spec but no tests; every row
here therefore has `test_id = TBD-Phase-1` and `status = pending`.

When `tests/test_*.py` first ships in Phase 1, the
`scripts/check_requirements.py` extension promotes
`TBD-Phase-1` from "the only valid value" to "a failure" and
the maintainer fills in the real test IDs.

See [requirements.md](requirements.md) for the canonical statement
of each ID; the table below adds only the test-id mapping column.

| HM-REQ | Spec section | Test ID | Status |
|--------|--------------|---------|--------|
| HM-REQ-0001 | [02](02-hypothesis-format.md) Schema validation | tests/unit/test_spec_schema.py::test_schema_rejects_invalid_hypothesis | pending |
| HM-REQ-0002 | [02](02-hypothesis-format.md) Versioning and immutability | tests/properties/test_lifecycle.py::test_immutability | pending |
| HM-REQ-0003 | [02](02-hypothesis-format.md) Versioning and immutability | tests/properties/test_lifecycle.py::test_version_ordering | pending |
| HM-REQ-0010 | [05](05-validator.md) Two layers | tests/integration/test_scoring_pipeline.py::test_scoring_deterministic | pending |
| HM-REQ-0011 | [05](05-validator.md) Two layers | tests/integration/test_scoring_pipeline.py::test_no_llm_in_scoring | pending |
| HM-REQ-0012 | [05](05-validator.md) Anti-collusion | tests/integration/test_scoring_pipeline.py::test_anti_collusion | pending |
| HM-REQ-0020 | [06](06-scoring.md) Composite score | tests/integration/test_scoring_pipeline.py::test_composite_formula | pending |
| HM-REQ-0021 | [06](06-scoring.md) Novelty / Ordering | tests/integration/test_scoring_pipeline.py::test_novelty_tiebreak | pending |
| HM-REQ-0030 | [09](09-protocol.md) Synapses | tests/unit/test_signing.py::test_synapse_signed | pending |
| HM-REQ-0031 | [09](09-protocol.md) Synapses | tests/unit/test_signing.py::test_canonical_json_signing | pending |
| HM-REQ-0040 | [12](12-implementation-constraints.md) Test-driven development | tests/integration/test_meta_gates.py::test_tdd_gate | pending |
| HM-REQ-0041 | [15](15-ci-cd.md) Pinning policy | tests/integration/test_meta_gates.py::test_action_pin_check | pending |
| HM-REQ-0042 | [12](12-implementation-constraints.md) License headers | tests/integration/test_meta_gates.py::test_spdx_headers | pending |
| HM-REQ-0050 | [02](02-hypothesis-format.md) Schema validation | tests/unit/test_spec_schema.py::test_analysis_plan_required | pending |
| HM-REQ-0060 | [06](06-scoring.md) External-verifiability anchor | tests/integration/test_external_anchor.py::test_anchor_required | pending |
| HM-REQ-0070 | [17](17-hypothesis-lifecycle.md) Two-tier settlement | tests/properties/test_lifecycle.py::test_two_tier_settlement | pending |
| HM-REQ-0080 | [18](18-oracle.md) Composition | tests/unit/test_oracle.py::test_composition_required_for_multi_oracle | pending |
| HM-REQ-0090 | [21](21-adversarial-simulator.md) Coverage requirement | tests/integration/test_meta_gates.py::test_adversarial_coverage | pending |
| HM-REQ-0100 | [22](22-security-bounty.md) Embargo before public disclosure | tests/integration/test_meta_gates.py::test_security_bounty_embargo | pending |
| HM-REQ-0110 | [12](12-implementation-constraints.md) Documentation discipline | tests/integration/test_meta_gates.py::test_single_source_principle | pending |

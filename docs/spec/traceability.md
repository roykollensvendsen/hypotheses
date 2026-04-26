---
name: traceability matrix
description: HM-REQ-NNNN to test-id mapping; populated as Phase 1 ships tests
tokens: 700
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
| HM-REQ-0120 | [02](02-hypothesis-format.md) Schema validation | tests/unit/test_spec_schema.py::test_gated_profile_requires_sponsorship | pending |

## System-test scenarios

Black-box scenarios from
[`23-system-tests.md`](23-system-tests.md). Each scenario traces to
≥1 HM-REQ in the table above. Scenario IDs are stable forever, like
HM-REQ IDs; once assigned they are never renamed or recycled.

| Scenario | HM-REQ refs | Test path | Status |
|----------|-------------|-----------|--------|
| S-MINE-01 | HM-REQ-0010, HM-REQ-0020 | tests/system/mine/test_happy_path_cli.py::test_happy_path_cli | pending |
| S-MINE-02 | HM-REQ-0030 | tests/system/mine/test_bad_signature.py::test_bad_signature | pending |
| S-MINE-03 | HM-REQ-0031 | tests/system/mine/test_non_canonical_json.py::test_non_canonical_json | pending |
| S-MINE-04 | HM-REQ-0001, HM-REQ-0050 | tests/system/mine/test_schema_rejects.py::test_schema_rejects | pending |
| S-MINE-05 | HM-REQ-0050 | tests/system/mine/test_seed_required.py::test_seed_required | pending |
| S-MINE-06 | HM-REQ-0010 | tests/system/mine/test_rate_limit.py::test_rate_limit | pending |
| S-MINE-07 | HM-REQ-0002, HM-REQ-0003 | tests/system/mine/test_version_bump.py::test_version_bump | pending |
| S-MINE-08 | HM-REQ-0030 | tests/system/mine/test_unregistered_hotkey.py::test_unregistered_hotkey | pending |
| S-MINE-09 | HM-REQ-0001 | tests/system/mine/test_sdk_cli_parity.py::test_sdk_cli_parity | pending |
| S-MINE-10 | HM-REQ-0001 | tests/system/mine/test_mcp_list.py::test_mcp_list | pending |
| S-MINE-11 | HM-REQ-0060 | tests/system/mine/test_external_anchor_required.py::test_external_anchor_required | pending |
| S-MINE-12 | HM-REQ-0080 | tests/system/mine/test_oracle_composition.py::test_oracle_composition | pending |
| S-MINE-13 | HM-REQ-0120 | tests/system/mine/test_gated_profile_sponsorship.py::test_gated_profile_sponsorship | pending |
| S-VAL-01 | HM-REQ-0010, HM-REQ-0020 | tests/system/validate/test_discover_score.py::test_discover_score | pending |
| S-VAL-02 | HM-REQ-0010, HM-REQ-0011 | tests/system/validate/test_deterministic_score.py::test_deterministic_score | pending |
| S-VAL-03 | HM-REQ-0010, HM-REQ-0020 | tests/system/validate/test_rerun_tolerance.py::test_rerun_tolerance | pending |
| S-VAL-04 | HM-REQ-0012 | tests/system/validate/test_no_self_score.py::test_no_self_score | pending |
| S-VAL-05 | HM-REQ-0021 | tests/system/validate/test_novelty_tiebreak.py::test_novelty_tiebreak | pending |
| S-VAL-06 | HM-REQ-0010 | tests/system/validate/test_mcp_score_parity.py::test_mcp_score_parity | pending |
| S-VAL-07 | HM-REQ-0070 | tests/system/validate/test_two_tier_settlement.py::test_two_tier_settlement | pending |
| S-VAL-08 | HM-REQ-0100 | tests/system/validate/test_security_embargo.py::test_security_embargo | pending |
| S-DEV-01 | HM-REQ-0001 | tests/system/develop/test_doctor_clean.py::test_doctor_clean | pending |
| S-DEV-02 | HM-REQ-0001 | tests/system/develop/test_doctor_broken.py::test_doctor_broken | pending |
| S-DEV-03 | HM-REQ-0001 | tests/system/develop/test_init_layout.py::test_init_layout | pending |
| S-DEV-04 | HM-REQ-0001 | tests/system/develop/test_client_from_env.py::test_client_from_env | pending |

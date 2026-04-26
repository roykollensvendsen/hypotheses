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
| HM-REQ-0001 | [02](02-hypothesis-format.md) Schema validation | TBD-Phase-1 | pending |
| HM-REQ-0002 | [02](02-hypothesis-format.md) Versioning and immutability | TBD-Phase-1 | pending |
| HM-REQ-0003 | [02](02-hypothesis-format.md) Versioning and immutability | TBD-Phase-1 | pending |
| HM-REQ-0010 | [05](05-validator.md) Two layers | TBD-Phase-1 | pending |
| HM-REQ-0011 | [05](05-validator.md) Two layers | TBD-Phase-1 | pending |
| HM-REQ-0012 | [05](05-validator.md) Anti-collusion | TBD-Phase-1 | pending |
| HM-REQ-0020 | [06](06-scoring.md) Composite score | TBD-Phase-1 | pending |
| HM-REQ-0021 | [06](06-scoring.md) Novelty / Ordering | TBD-Phase-1 | pending |
| HM-REQ-0030 | [09](09-protocol.md) Synapses | TBD-Phase-1 | pending |
| HM-REQ-0031 | [09](09-protocol.md) Synapses | TBD-Phase-1 | pending |
| HM-REQ-0040 | [12](12-implementation-constraints.md) Test-driven development | TBD-Phase-1 | pending |
| HM-REQ-0041 | [15](15-ci-cd.md) Pinning policy | TBD-Phase-1 | pending |
| HM-REQ-0042 | [12](12-implementation-constraints.md) License headers | TBD-Phase-1 | pending |
| HM-REQ-0050 | [02](02-hypothesis-format.md) Schema validation | TBD-Phase-1 | pending |
| HM-REQ-0060 | [06](06-scoring.md) External-verifiability anchor | TBD-Phase-1 | pending |
| HM-REQ-0070 | [17](17-hypothesis-lifecycle.md) Two-tier settlement | TBD-Phase-1 | pending |
| HM-REQ-0080 | [18](18-oracle.md) Composition | TBD-Phase-1 | pending |
| HM-REQ-0090 | [21](21-adversarial-simulator.md) Coverage requirement | TBD-Phase-1 | pending |
| HM-REQ-0100 | [22](22-security-bounty.md) Embargo before public disclosure | TBD-Phase-1 | pending |
| HM-REQ-0110 | [12](12-implementation-constraints.md) Documentation discipline | TBD-Phase-1 | pending |

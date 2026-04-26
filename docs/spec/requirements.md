---
name: requirements index
description: catalogue of normative HM-REQ statements and the spec section that defines each
tokens: 1000
load_for: [implementation, review]
depends_on: []
kind: reference
internal_only:
  - HM-REQ-0040
  - HM-REQ-0041
  - HM-REQ-0042
  - HM-REQ-0090
  - HM-REQ-0110
---

# Requirements index

Every **HM-REQ-NNNN** tag is a normative statement the implementation
must satisfy. IDs are stable forever: once assigned, they are never
renamed or recycled, even if the text they tag is revised.

The implementation links back with a `# spec: HM-REQ-NNNN` comment in
the relevant test or module. The
[`scripts/check_requirements.py`](../../scripts/check_requirements.py)
checker enforces one-way invariants:

- Every ID in this index has an inline definition in a spec doc.
- Every inline ID in a spec doc has a row here.
- Every ID in this index has a row in
  [`traceability.md`](traceability.md), and vice versa.
- IDs are unique.

## Index

| ID | Doc | Section | Short statement | Status |
|----|-----|---------|-----------------|--------|
| HM-REQ-0001 | [02](02-hypothesis-format.md) | Schema validation | Hypothesis front matter is governed by the JSON Schema; the schema is the contract | normative |
| HM-REQ-0002 | [02](02-hypothesis-format.md) | Versioning and immutability | Results announced against a given `(id, version)` are valid only if the spec at that version was committed before `submitted_at` | normative |
| HM-REQ-0003 | [02](02-hypothesis-format.md) | Versioning and immutability | A version bump invalidates every prior submission against the earlier version | normative |
| HM-REQ-0010 | [05](05-validator.md) | Two layers | Validator scoring is deterministic pure functions over artifacts; two validators on the same inputs produce the same score vector | normative |
| HM-REQ-0011 | [05](05-validator.md) | Two layers | No LLM output participates in the scoring pipeline | normative |
| HM-REQ-0012 | [05](05-validator.md) | Anti-collusion | A validator cannot score its own miner hotkey | normative |
| HM-REQ-0020 | [06](06-scoring.md) | Composite score | Composite score is `w_rigor*rigor + w_reproduction*reproduction + w_improvement*improvement + w_novelty*novelty − w_cost*cost_penalty` | normative |
| HM-REQ-0021 | [06](06-scoring.md) | Novelty / Ordering | Novelty tiebreak is (1) announcement block height, (2) in-block extrinsic index, (3) hotkey SS58 lex order | normative |
| HM-REQ-0030 | [09](09-protocol.md) | Synapses | Every synapse payload is signed by the sender's hotkey (ed25519) | normative |
| HM-REQ-0031 | [09](09-protocol.md) | Synapses | Signing is over canonical JSON (RFC 8785); non-canonical encoding fails verification | normative |
| HM-REQ-0040 | [12](12-implementation-constraints.md) | Test-driven development | Each module's first `test:` commit precedes its first `feat:`/`fix:` commit; the `test:` is red on its own | normative |
| HM-REQ-0041 | [15](15-ci-cd.md) | Pinning policy | Every `uses:` in `.github/workflows/**` is a 40-char SHA | normative |
| HM-REQ-0042 | [12](12-implementation-constraints.md) | License headers | Every new `.py`/`.sh` under `src/`, `scripts/`, `tests/`, `experiments/` carries SPDX identifier + copyright lines in the first 10 lines | normative |
| HM-REQ-0050 | [02](02-hypothesis-format.md) | Schema validation | A hypothesis MUST declare an `analysis_plan` (pre-processing, exclusion criteria, multiple-comparisons correction, missing-seed policy); generic preregistration without analysis-plan detail does not reduce p-hacking | normative |
| HM-REQ-0060 | [06](06-scoring.md) | External-verifiability anchor | Every scored hypothesis must have at least one external anchor — mechanical (metrics from artifacts), oracle, or public_benchmark — to foreclose closed-system validator-consensus collusion | normative |
| HM-REQ-0070 | [17](17-hypothesis-lifecycle.md) | Two-tier settlement | Settlement is tentative; 70% of novelty + improvement at first settled-* transition, 30% deferred 6 months pending no T-OVR overturn; defends against long-latency rent extraction | normative |
| HM-REQ-0080 | [18](18-oracle.md) | Composition | When `oracle.oracles` array length ≥ 2, `oracle.composition` (one of `all_agree` / `majority` / `weighted_majority`) MUST be declared and must resolve disagreement deterministically; defends against single-oracle corruption | normative |
| HM-REQ-0090 | [21](21-adversarial-simulator.md) | Coverage requirement | Every threat in 16 must have at least one fixture under `tests/golden/adversarial/` by end of Phase 2; simulator runs nightly and failures block release | normative |
| HM-REQ-0100 | [22](22-security-bounty.md) | Embargo before public disclosure | A security-hypothesis whose first appearance on `main` was NOT preceded by a private SECURITY.md advisory has its `improvement` component zeroed at scoring time; rigor + reproduction still pay (the public fixture is still useful coverage) | normative |
| HM-REQ-0110 | [12](12-implementation-constraints.md) | Documentation discipline | Every fact, contract, parameter, or list in this repository has exactly one canonical home; other docs link rather than restate; drift between a canonical statement and a restatement is a bug in the restatement | normative |
| HM-REQ-0120 | [02](02-hypothesis-format.md) | Schema validation | A hypothesis declaring a gated-tier `hardware_profile` (any `single-gpu-*` or `multi-gpu-*` profile) MUST include a `sponsorship` block; without it the hypothesis is rejected at acceptance. Operationalises ADR 0019's tier-2 pivot | normative |
| HM-REQ-0130 | [02](02-hypothesis-format.md) | Schema validation | A hypothesis declaring `verification: oracle-only` MUST declare an `oracle` block (or `external_anchor.type=oracle`); without one the hypothesis is rejected at acceptance. Operationalises ADR 0021's third viability path | normative |

## How to add

1. Pick the next free ID (`HM-REQ-NNNN`, four digits, monotonic by
   cluster: 00xx hypothesis format, 00xx–01xx validator, 02xx
   scoring, 03xx protocol, 04xx implementation).
2. Insert an inline block-quote at the normative statement's
   canonical home in the spec, e.g.
   `> **HM-REQ-0099** The checker rejects …`
3. Add a row to this index.
4. Reference it from any relevant test / ADR as `# spec: HM-REQ-0099`.

Removing an ID is only permissible if the requirement itself is
withdrawn — mark the row `withdrawn` rather than deleting, so
historical references stay resolvable.

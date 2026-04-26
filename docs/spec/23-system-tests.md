---
name: system tests
description: black-box harness contract for the full Phase-1 subnet across CLI, SDK, and MCP surfaces
tokens: 3500
load_for: [implementation, agent-operator, review]
depends_on: [04, 05, 11, 13, 14]
kind: contract
---

# 23 — System tests

This document is the contract for the **black-box system-test
harness**. The harness boots the full Phase-1 subnet on a single
machine, drives it through its public surfaces using simulated role
clients, and asserts observable behaviour against the [spec](01-glossary.md#spec).
It is the safety net that lets humans and agents change the spec, code, or
tests without silently regressing what the running subnet does.

The harness itself is not in scope here — it lands as a follow-up
PR (`tests/system/` skeleton). This doc fixes the contract: what
"system test" means in this repo, which scenarios are required,
which surfaces they exercise, and how the spec/test/code triple
stays in sync.

## Why this exists

`13` defines the role × surface matrix abstractly. Property and unit
tests under `tests/properties/` and `tests/unit/` cover individual
invariants and modules. Neither answers the question:

> *Does the running subnet, viewed only through its public surfaces,
> behave the way the spec says it does, end-to-end, for every role?*

Answering that requires a separate test layer. Without it, every
spec/code change is a leap of faith that internal-unit-test green
implies system green. With it, the running subnet is the source of
truth and the spec is a living contract that the test suite enforces
on every PR.

The intended audience is broad: human developers, the implementing
agent (Phase 1+), reviewers, and operators planning a deployment.
Writing this contract before the harness exists keeps the harness
honest — there is a target shape to build to.

## Black-box contract

System tests interact with the subnet **only through its three
public surfaces**: the `hypo` CLI, the `hypotheses.client` SDK, and
the MCP server (stdio transport for v1). Tests:

- **MUST** call surfaces as a real consumer would. CLI tests shell
  out to `hypo`; SDK tests `import hypotheses.client`; MCP tests speak
  the wire protocol.
- **MUST NOT** import from `hypotheses.miner.*`, `hypotheses.validator.*`,
  or any other internal module. The one allowed import outside the
  client surface is `hypotheses.testing` (a thin fixtures package
  introduced in PR-B; it builds artifacts and signs payloads, but
  exposes nothing the SDK does not already expose).
- **MUST NOT** read or mutate [validator](05-validator.md) state directly. State checks
  go through MCP read tools (`get_score_history`, `list_submissions`)
  or the SDK's read methods, the same way a real operator agent
  would.
- **MUST NOT** mock the storage backend, the scoring core, or the
  signing module. The full subnet runs; only the *outside world*
  (chain, IPFS, [oracle](18-oracle.md)) is replaced by the simulated drivers
  described below.

The black-box property is what makes these tests load-bearing:
they verify the contract a downstream agent, operator, or reviewer
actually depends on. Internal refactors that preserve surface
behaviour stay green; surface changes break them loudly.

## Phase gating

v1 of this contract covers **Phase 1 only**: the local single-machine
roundtrip per [`11`](11-roadmap.md) §Phase 1. That phase is offline,
filesystem-backed, and chain-free. The corresponding scenarios
(catalogued below) are runnable on a developer laptop in seconds-to-
minutes, with no external services and no GPU required (the
`single-gpu-24gb` runtime profile is exercised separately by the
Phase-1 smoke test, not by this harness).

The following are **deferred to v2** and are out of scope for this
spec until their named triggers are met:

| capability | trigger to land in v2 |
|------------|----------------------|
| chain (axon/dendrite) | `synapses.py` wired to real Bittensor IO ([`11`](11-roadmap.md) Phase 2) |
| IPFS / kubo | IPFS adapter merged ([`11`](11-roadmap.md) Phase 2) |
| SN42 oracle | oracle adapter merged ([`18`](18-oracle.md)) |
| MCP write tools | `--allow-writes` enabled by default ([`13`](13-agent-integration.md)) |
| performance / load | not in scope for any version of this doc; lives in `19-operations.md` |
| security fuzzing | covered by [`21`](21-adversarial-simulator.md) and [`22`](22-security-bounty.md), not here |

When a trigger fires, the corresponding scenarios are added to this
doc behind the `system_chain` pytest marker (see §Local developer
workflow); v1 leaves room for them in the table headers but no rows.

## Harness architecture

The harness has two sides — the **system under test** (SUT) and the
**drivers** — both running in the same process tree under pytest's
control.

### SUT

The SUT is whichever subset of the subnet the scenario requires:

- `hypo validate serve` — long-running validator daemon; supervised
  by a subprocess fixture, signalled with SIGTERM at teardown.
- `hypo mcp serve` — read-only MCP server (Phase 1 default per
  [`13`](13-agent-integration.md) §Tool surface); spawned with stdio
  transport and a per-test working directory.
- The on-disk registry that backs both, rooted at `tmp_path` — no
  global state, no shared cache between tests.
- The scoring core ([`06`](06-scoring.md)), exercised through the
  validator's normal pipeline. Tests do not invoke it directly.

The SUT runs as real subprocesses. There is no "test mode" flag, no
import-time monkeypatch, no in-process shortcut. If a scenario
needs the validator to advance epochs faster than wall clock, that
goes through whatever clock-injection surface the validator already
exposes (see [`05`](05-validator.md) §Two layers); the harness does
not reach inside.

### Drivers

Drivers are **simulated role clients**. Each scenario picks one
driver and one surface; the driver acts as a single role
([miner](04-miner.md), validator-operator, or developer) and
exercises that role's surface contract.

| driver kind | how it talks to the SUT |
|-------------|------------------------|
| CLI driver | `subprocess.run(["hypo", ...])`, capture stdout/stderr/exit code |
| SDK driver | `from hypotheses.client import Client` and call methods |
| MCP driver | spawn an MCP client over stdio, send JSON-RPC, parse responses |

Drivers live under `tests/system/drivers/` (PR-B). Each driver is
deliberately thin: it shapes inputs and parses outputs but does not
re-implement subnet logic. A driver that grows policy is a smell;
the policy belongs in the SUT.

### Fixtures

Declared shape (concrete code lands in PR-B):

- `tmp_registry` — fresh on-disk registry for the test, rooted at
  pytest's `tmp_path`; teardown removes it.
- `fake_hotkey` — deterministic ed25519 keypair derived from the
  test's nodeid; never collides across xdist workers.
- `system_seed` — an integer seed pinned per scenario so flakes are
  caught immediately rather than papered over by retry.
- `clock` — a controllable clock object for scenarios that touch
  epoch boundaries; pulls through whatever clock seam
  [`05`](05-validator.md) defines, never wall-clock-`sleep()`.
- `mcp_client`, `validator_proc`, `mcp_proc` — supervised subprocess
  fixtures with structured-log capture and clean signal handling.
- `port_pool` — per-worker port allocator for HTTP-MCP scenarios
  (Phase-2 only; declared here so v1 reserves the seam).

### Isolation

Every scenario gets its own registry, its own hotkey, its own
subprocess tree. Nothing is shared. The harness is `pytest-xdist`
safe: scenarios run in parallel without fixture collisions. Any
scenario that requires global state is a bug in the scenario, not a
relaxation the harness accommodates.

## Role × surface scenario matrix

Each row is a **scenario**: one driver, one surface, one observable
outcome. Scenarios cite at least one HM-REQ from
[`requirements.md`](requirements.md) and name the test path under
`tests/system/` they will land at (paths created in PR-B).

Scenario IDs follow the shape `S-<ROLE>-<NN>` and are stable
forever, like HM-REQ IDs: once assigned, never renamed or recycled.
The numbering is per-role, monotonic.

### Mine

| ID | scenario | surface | HM-REQ | target test |
|----|----------|---------|--------|-------------|
| S-MINE-01 | Happy-path: propose H-0001 → run with declared seed set → submit; validator scores composite > 0 | CLI | HM-REQ-0010, HM-REQ-0020 | `tests/system/mine/test_happy_path_cli.py` |
| S-MINE-02 | Bad-signature: malformed ed25519 signature on submit; rejected with non-zero exit and a structured error | CLI | HM-REQ-0030 | `tests/system/mine/test_bad_signature.py` |
| S-MINE-03 | Non-canonical JSON: signature over RFC-8785-violating bytes; rejected at verification | CLI | HM-REQ-0031 | `tests/system/mine/test_non_canonical_json.py` |
| S-MINE-04 | Missing `analysis_plan`: schema-invalid [hypothesis](02-hypothesis-format.md) at `propose`; rejected with field-level diagnostics | CLI | HM-REQ-0001, HM-REQ-0050 | `tests/system/mine/test_schema_rejects.py` |
| S-MINE-05 | Single-seed run when spec demands more: client refuses with actionable message | CLI | HM-REQ-0050 | `tests/system/mine/test_seed_required.py` |
| S-MINE-06 | Duplicate submission within an epoch: validator rate-limits to the documented cap; the over-the-cap submission is dropped without scoring | CLI | HM-REQ-0010 | `tests/system/mine/test_rate_limit.py` |
| S-MINE-07 | Version bump: submission against `(id, v1)` is invalidated when the spec rolls to `v2` mid-epoch | SDK | HM-REQ-0002, HM-REQ-0003 | `tests/system/mine/test_version_bump.py` |
| S-MINE-08 | Unregistered hotkey: `propose` without a registered hotkey exits non-zero with a `hypo init` pointer | CLI | HM-REQ-0030 | `tests/system/mine/test_unregistered_hotkey.py` |
| S-MINE-09 | SDK ↔ CLI parity: `client.propose_hypothesis(...)` produces the same on-disk artifacts as `hypo propose` for the same input | SDK | HM-REQ-0001 | `tests/system/mine/test_sdk_cli_parity.py` |
| S-MINE-10 | MCP read-only listing: `list_hypotheses` returns the same set as `hypo ls`, with the same shape | MCP | HM-REQ-0001 | `tests/system/mine/test_mcp_list.py` |
| S-MINE-11 | External-anchor required: `propose` rejects a hypothesis whose front matter declares neither a mechanical metric, an oracle, nor a public benchmark | CLI | HM-REQ-0060 | `tests/system/mine/test_external_anchor_required.py` |
| S-MINE-12 | Oracle composition required: `propose` rejects a hypothesis with `oracle.oracles` length ≥ 2 that omits `oracle.composition` | CLI | HM-REQ-0080 | `tests/system/mine/test_oracle_composition.py` |

### Validate

| ID | scenario | surface | HM-REQ | target test |
|----|----------|---------|--------|-------------|
| S-VAL-01 | Discover and score: `validate serve` picks up a fresh local submission, reruns it, and writes a score vector | CLI | HM-REQ-0010, HM-REQ-0020 | `tests/system/validate/test_discover_score.py` |
| S-VAL-02 | Determinism: two independent runs over the same submission produce byte-identical score vectors (any LLM in the path would break this, so HM-REQ-0011 is covered transitively) | CLI | HM-REQ-0010, HM-REQ-0011 | `tests/system/validate/test_deterministic_score.py` |
| S-VAL-03 | Rerun-tolerance miss: a submission whose miner-declared metric falls outside the rerun band has its reproduction component zeroed; other components still pay | CLI | HM-REQ-0010, HM-REQ-0020 | `tests/system/validate/test_rerun_tolerance.py` |
| S-VAL-04 | Anti-collusion: a validator's own miner hotkey is skipped at scoring time; the run leaves an audit-trail entry | CLI | HM-REQ-0012 | `tests/system/validate/test_no_self_score.py` |
| S-VAL-05 | Novelty tiebreak: two submissions with identical composite are ordered by announcement block height, then in-block index, then SS58 lex | CLI | HM-REQ-0021 | `tests/system/validate/test_novelty_tiebreak.py` |
| S-VAL-06 | MCP score query parity: `get_score_history(...)` returns the same records as `hypo scores` for the same hotkey/window | MCP | HM-REQ-0010 | `tests/system/validate/test_mcp_score_parity.py` |
| S-VAL-07 | Two-tier settlement: a settling submission earns 70 % of novelty + improvement at the first `settled-*` transition, with the remaining 30 % deferred for the documented six-month T-OVR window | CLI | HM-REQ-0070 | `tests/system/validate/test_two_tier_settlement.py` |
| S-VAL-08 | Security-embargo gate: a security-flavoured hypothesis whose first appearance on `main` was not preceded by a SECURITY.md advisory has its improvement component zeroed at scoring time; rigor and reproduction still pay | CLI | HM-REQ-0100 | `tests/system/validate/test_security_embargo.py` |

### Develop

| ID | scenario | surface | HM-REQ | target test |
|----|----------|---------|--------|-------------|
| S-DEV-01 | `hypo doctor` exits 0 on a clean Phase-1 install | CLI | HM-REQ-0001 | `tests/system/develop/test_doctor_clean.py` |
| S-DEV-02 | `hypo doctor` exits non-zero with a structured diagnostic when the registry is unwritable | CLI | HM-REQ-0001 | `tests/system/develop/test_doctor_broken.py` |
| S-DEV-03 | `hypo init` produces the directory layout documented in [`14`](14-cli.md), idempotently | CLI | HM-REQ-0001 | `tests/system/develop/test_init_layout.py` |
| S-DEV-04 | SDK `Client.from_env()` honours env-var precedence over default config | SDK | HM-REQ-0001 | `tests/system/develop/test_client_from_env.py` |

The matrix is **not exhaustive** by design. New scenarios are added
as new HM-REQs land or new surface behaviours are specified. Every
addition follows §Spec-test sync workflow.

## Pass/fail criteria

A scenario is **green** iff the assertion against the spec holds
exactly. The harness has zero flake budget:

- Every assertion is an equality, an inclusion, or an explicit range
  against a documented bound. No `assert result is not None` placeholders.
- Every scenario pins a seed (`system_seed`); a non-deterministic
  scenario is a contradiction in terms.
- Retries are forbidden. A scenario that "passes when re-run" is a
  bug in the harness or in the SUT, not a transient.

A scenario is **red** when the SUT's observable behaviour diverges
from the spec. The fix is one of three:

1. The spec was right and the code is wrong: open a `feat`/`fix`
   PR against the code; the scenario stays unchanged.
2. The spec was right and the test was wrong: open a `test` PR
   updating the test; spec and code unchanged.
3. The spec was wrong: open a `docs(spec)` PR updating the spec
   AND the affected scenario AND the linked test, in the same PR
   (see §Spec-test sync workflow).

Anything else — silencing the test, marking it `xfail`, lowering an
assertion's strictness without a paired spec change — is a spec
violation.

## Spec-test sync workflow

The contract that keeps spec, code, and tests honest:

1. **Every HM-REQ MUST be linked** to ≥ 1 scenario in this doc, OR
   marked `internal-only` in [`requirements.md`](requirements.md).
   Internal-only is for requirements that have no surface-observable
   manifestation (e.g. HM-REQ-0040 TDD commit order, enforced by a
   CI gate). The `internal-only` flag is a single-word annotation in
   the requirements row.

2. **Every scenario MUST cite ≥ 1 HM-REQ** in its row. The cited
   HM-REQs anchor the scenario to spec text; if the HM-REQ moves,
   the scenario row must move with it.

3. **Spec changes ride with test changes.** A PR that edits a
   normative paragraph in any `docs/spec/*.md` MUST update the
   linked scenarios in this doc AND the corresponding tests under
   `tests/system/` in the same PR. Reviewers reject spec PRs that
   leave the matrix stale.

4. **New HM-REQs trigger new scenarios.** A PR introducing
   HM-REQ-NNNN MUST add at least one scenario row here citing it,
   or mark it `internal-only` with a one-line justification.

5. **Withdrawn HM-REQs leave their scenarios as historical.**
   Mirror the rule in `requirements.md`: mark the scenario row
   `withdrawn`, do not delete it, so historical references stay
   resolvable.

The first three rules are enforced by review in v1. A CI gate
(`scripts/check_system_test_traceability.py`) lands in a follow-up
PR; until then the rules read as "reviewer obligations".

## Local developer workflow

Target shape; concrete `Makefile` and `conftest.py` land in PR-B:

```bash
make system-test            # Phase-1 local scenarios; the default
make system-test-watch      # ptw equivalent for the system layer
make system-test PROFILE=chain  # Phase 2; gated on $BITTENSOR_TESTNET=1
```

- Default profile runs only `@pytest.mark.system_local` scenarios.
  The `system_chain` marker is registered in `pyproject.toml` and is
  skipped unless `BITTENSOR_TESTNET=1` is exported.
- Parallelism is on by default via `pytest-xdist`. Per-test resources
  (registries, hotkeys, ports) are isolated; a clean `make
  system-test` run is reproducible bit-for-bit given the same
  toolchain pin.
- The harness emits structured logs to a per-test file under
  `tmp_path`; on failure pytest dumps the SUT's stderr alongside the
  test traceback so the diagnostic is one screen, not a hunt.
- No Docker. Subprocesses run on the developer's host. Podman, the
  [experiment](08-experiment-runtime.md)-runtime sandbox per
  [`12`](12-implementation-constraints.md), is exercised by the
  scenario itself, not by the harness wrapping it.

## Out of scope

Repeated explicitly because they are the most common temptations:

- **Chain integration** — Phase 2; v2 of this doc.
- **IPFS / kubo** — Phase 2; v2 of this doc.
- **SN42 oracle** — Phase 2; v2 of this doc.
- **MCP write tools** — Phase 2; v2 of this doc.
- **Performance and load testing** — separate concern, see
  [`19`](19-operations.md).
- **Security fuzzing and adversarial coverage** — see
  [`21`](21-adversarial-simulator.md) and
  [`22`](22-security-bounty.md). System tests are spec-conformance,
  not attack synthesis.
- **Mutation testing** — separate gate, nightly, scoped to unit and
  integration layers.
- **Internal property tests** — `tests/properties/` enforces
  invariants against in-process code; system tests enforce contracts
  against running surfaces. The two layers are complementary and not
  redundant.

## References

- [`04 — Miner`](04-miner.md) — miner CLI verbs and synapse contracts.
- [`05 — Validator`](05-validator.md) — validator pipeline, two-layer
  architecture, scoring determinism.
- [`06 — Scoring`](06-scoring.md) — composite formula, anchors,
  novelty tiebreak.
- [`09 — Protocol`](09-protocol.md) — synapse signatures, RFC-8785
  canonical JSON.
- [`11 — Roadmap`](11-roadmap.md) §Phase 1 — what the harness
  targets in v1.
- [`13 — Agent integration`](13-agent-integration.md) — the role ×
  surface matrix this doc operationalises.
- [`14 — CLI`](14-cli.md) — full `hypo` command surface.
- [`requirements.md`](requirements.md) — the HM-REQ catalogue every
  scenario traces to.
- [`traceability.md`](traceability.md) — gets a system-test column
  in PR-B.

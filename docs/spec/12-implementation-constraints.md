---
name: implementation constraints
description: rules for an autonomous Claude agent implementing the subnet from this spec
tokens: 3400
load_for: [implementation, review]
depends_on: [10, 11, 16]
---

# 12 — Implementation constraints

This document is addressed to the implementing agent (Claude, working
autonomously). It exists so the agent can make progress without
interaction and stay inside bounded scope.

## How to work

### Autonomous operation

- **Resolve TBDs yourself.** If a TBD is still open when you reach it,
  pick the simplest option that satisfies the stated constraints,
  commit the spec edit that resolves it in the same PR as the code that
  depends on it, and proceed.
- **Document non-trivial choices** as ADRs in `docs/adr/NNNN-title.md`.
  Four sections: context, options, chosen, consequences. Half a page.
  Not every choice needs one — only those a reader would second-guess.
- **Stop and ask only for:** (a) destructive operations against shared
  state (force-push, mainnet transactions, deleting data), (b) spec
  ambiguity you cannot resolve by applying the stated constraints,
  (c) discoveries that invalidate a phase exit criterion.
- **Build in the order given below.** Later modules' tests depend on
  earlier modules.
- **If the spec is wrong, update the spec first, then change the code.**
  Never let code and spec diverge silently.

### Scope discipline

- No synapses, metrics, CLI subcommands, config flags, or top-level
  directories not in the spec.
- No speculative features. No "we might want X later" hooks.
- No fallbacks for paths that shouldn't fail (see fail-fast policy).
- No swapping pinned tools or adding top-level deps without a spec
  update + ADR.

### Agent / CLI parity

The subnet is agent-first (see
[13](13-agent-integration.md)). That imposes a hard rule:

- **Every capability exposed by `hypo` is also exposed by MCP and the
  SDK, and vice versa.** The three surfaces dispatch to the same
  underlying modules; they never branch behaviour.
- **CLI flags that affect behaviour have MCP / SDK equivalents.** If
  `hypo run --seed N` exists, `run_hypothesis(seed=N)` exists. If
  not, remove the CLI flag.
- **Validator scoring is deterministic.** Operator-layer code
  (announcement polling, triage, explanation, runbook suggestions)
  may be agent-driven; scoring itself is pure and agent-free. See
  [05 — Validator](05-validator.md).
- **No "human-only" paths.** If an operation is too risky for an
  agent, gate it with the confirmation modes from 13 — never with a
  CLI-only branch.

## Toolchain (pinned)

| tool | version | notes |
|------|---------|-------|
| Python | 3.12 | no older; no newer until a release has been out 3 months |
| `uv` | latest stable | package + env manager; `uv.lock` is authoritative |
| `ruff` | latest stable | format + lint; config in `pyproject.toml`; no separate formatter |
| `pyright` | latest stable | strict mode; type errors fail CI |
| `pytest` | latest stable | plus `pytest-xdist`, `pytest-cov` |
| `mutmut` | latest stable | nightly mutation gate; 75% min per module |
| `torch` | 2.5.x | CPU wheel in base; GPU via `[gpu]` extra |
| `bittensor` SDK | latest stable at Phase 2 kick-off | exact version pinned then; ADR required |
| `pydantic` | v2.x | no v1 shims |
| `structlog` | latest stable | |
| `rfc8785` | latest stable | canonical JSON |
| `cryptography` | latest stable | ed25519 |
| podman | 4.x | container runtime; no Docker |
| `nvidia-container-toolkit` | latest stable | GPU passthrough |
| kubo (IPFS) | 0.29+ | reference node |

## Code style

- Type hints on every function and method, including tests.
  `Any` requires a `# pyright: ignore[reportExplicitAny]` with a reason.
- No comments unless WHY is non-obvious. Never restate what the code
  does.
- No module-level mutable state except `Final` constants.
- No `print` in `src/`. A ruff rule enforces this.
- No bare `except`. No `except Exception: pass`. Always raise a typed
  exception from `src/hypotheses/errors.py`.
- Public API is what `__all__` declares. Anything else is private.
- Docstrings on public classes and functions only; one-line summary.

## License headers

> **HM-REQ-0042** Every tracked `.py` or `.sh` file under `src/`,
> `scripts/`, `tests/`, or `experiments/` carries the SPDX license
> identifier `AGPL-3.0-or-later` and an `SPDX-FileCopyrightText` line
> within the first 10 lines of the file. Enforced by
> [`scripts/check_spdx_headers.py`](../../scripts/check_spdx_headers.py)
> via [`spdx.yml`](../../.github/workflows/spdx.yml).

Every tracked `.py` and `.sh` file under `src/`, `scripts/`, `tests/`,
and `experiments/` MUST carry both markers within the first 10 lines:

```
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: <year> <holder>
```

Python style (two comment lines before the docstring):

```python
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Module docstring."""
```

Shell style (immediately after the shebang):

```bash
#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
```

The collective holder string `The hypotheses subnet contributors`
is the project default. Individual contributors may add their own
`SPDX-FileCopyrightText` line above or below if they want named
attribution.

Enforcement: `.github/workflows/spdx.yml` runs
`scripts/check_spdx_headers.py` on every PR and push, checking
every tracked `.py` and `.sh` under the protected roots. Missing
headers fail CI. YAML, TOML, JSON, and markdown are NOT checked —
the root `LICENSE` covers them under AGPL's standard "work as a
whole" clause.

When `pyproject.toml` lands in Phase 1, it MUST include:

```toml
[project]
license = "AGPL-3.0-or-later"
classifiers = [
  "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
]
```

## Testing strategy

Pyramid:

- **Unit** — one `tests/<module>/` per `src/hypotheses/<module>`. Mock
  I/O boundaries only (filesystem, network, subprocess). Do not mock
  pure logic, cryptography, canonical JSON, or the spec parser.
- **Integration** — `tests/integration/`. Real sandbox, real local IPC,
  real filesystem. No mocking. Slower, separate CI job.
- **Smoke** — `tests/integration/smoke_submit_score.py` runs the full
  miner→validator loop against `H-0001`. This is the canonical
  end-to-end check.

Chain-dependent tests are tagged `@pytest.mark.chain` and run only
against Bittensor testnet, not in default CI.

Coverage: package ≥ 85% statements; per-module floor 75%. A module
below its floor fails CI.

### Golden fixtures

Static input/output fixtures live under
[`tests/golden/`](../../tests/golden/) as JSON files only — never
`.py`. Unit tests parametrise over these files for any behaviour
whose expected output comes directly from the spec (composite score,
parsed hypothesis front matter, wire-format dispatch, etc.).

Rules:

- Phase 1 adds `pytest --update-golden` for scaffolding; a PR that
  regenerates a pre-existing fixture must cite the spec change or
  bug that justifies the update. Silent drift is a review-blocker.
- Every fixture that has a schema in
  `src/hypotheses/spec/schema/` also validates against that schema.
- No test fixture is a `.py` file. If the fixture needs code to
  generate, the generator lives in `scripts/` and writes the JSON;
  tests read the JSON.

## Test-driven development (mandatory)

> **HM-REQ-0040** Each module's first `test:` commit strictly
> precedes its first `feat:` or `fix:` commit. The first `test:`
> commit is red when run against the pre-implementation tree —
> "tests first" is a discipline, not a commit-log aesthetic (see
> [AP-0004](antipatterns/ap-0004-skip-tdd.md)).

Every module in `src/hypotheses/` is built test-first. The required
discipline per slice of behaviour:

1. **Red.** Write the tests. Commit as
   `test: <describe the behaviour under test>`. `pytest` MUST be
   failing on the new tests at this commit.
2. **Green.** Write the minimum code to make them pass. Commit as
   `feat:` or `fix:`. `pytest` MUST pass at this commit.
3. **Refactor.** Improve structure without changing behaviour.
   `pytest` stays green. Commit as `refactor:`.

### Enforcement

- **Commit-order gate** (`.github/workflows/tdd-gate.yml`) — fails a
  PR if any `feat:` / `fix:` commit touching `src/` is not preceded
  by at least one `test:` commit in the PR range. Script:
  `scripts/check_tdd_order.py`.
- **Mutation gate** (`.github/workflows/mutation.yml`) — nightly
  `mutmut` run with per-module minimum mutation score **75%**. A
  module below the floor fails the job. Script:
  `scripts/check_mutation_score.py`.
- **PR template** — TDD checklist in `.github/PULL_REQUEST_TEMPLATE.md`
  sets the cultural norm in addition to the mechanical gate.
- **Module DoD** — the git history for each module's test file must
  show its first `test:` commit preceding its first
  `feat:`/`fix:` commit.

### Exemptions (no TDD requirement)

- `docs:`, `chore:`, `style:`, `ci:`, `build:`, `perf:`, `revert:`.
- `refactor:` — by definition runs under green with no new behaviour.
- Changes that touch only configuration, assets, or non-`src/` paths.

### Why both coverage and mutation

Coverage catches untested *code*. Mutation catches tests that pass
*regardless of behaviour* — the silent-failure mode where a test runs
the code path but doesn't actually assert anything meaningful. Both
gates are required for a module to count as done.

## Logging & observability

- `structlog`, line-delimited JSON on stderr.
- Required fields: `ts` (ISO-8601 UTC), `level`, `msg`, `component`
  (e.g. `miner.runner`), plus `cycle_id`, `hypothesis_id`,
  `miner_hotkey` when applicable.
- Miner and validator each append an `events.jsonl` alongside their
  data directory for offline replay.
- `INFO` for lifecycle, `WARNING` for recoverable anomalies, `ERROR`
  for failures ending the current action. No debug-level chatter in
  production paths.
- Operator-facing SLIs, alert names, and runbooks live in
  [19 — Operations](19-operations.md). That doc consumes the log
  schema specified above; adding a new required field here is a
  breaking change to operators' dashboards.

## Fail-fast policy

Prefer raising over falling back. Every case below maps to an
exception type defined in `src/hypotheses/errors.py`:

| situation | exception |
|-----------|-----------|
| IPFS unreachable when publishing | `StorageUnavailable` |
| Missing declared metric in a run | `MetricMissing` |
| Spec schema validation failure | `SpecInvalid` |
| Manifest signature invalid | `SignatureInvalid` |
| Rerun disagreement beyond tolerance | `ReproductionFailed` |
| Env lock mismatch miner↔validator | `EnvMismatch` |
| Unknown synapse schema version | `UnsupportedSchema` |
| Artifact hash mismatch | `ArtifactCorrupt` |
| Sandbox wallclock or memory breach | `SandboxLimit` |
| Dataset revision hash mismatch | `DatasetHashMismatch` |

Each exception carries a `details: dict[str, object]` field with
structured context. No generic `RuntimeError`.

## Dependencies policy

- Runtime deps: minimal, patch-pinned, listed in
  `[project.dependencies]`.
- Dev deps in `[project.optional-dependencies].dev`.
- Experiment-local deps in `experiments/<id>/pyproject.toml` only; do
  NOT leak into the base package.
- New dep ⇒ ADR.

## Build order

Each step's tests pass before the next begins.

1. `src/hypotheses/errors.py`
2. `src/hypotheses/spec/` (parser, JSON schema, validator)
3. `src/hypotheses/protocol/signing.py`
4. `src/hypotheses/protocol/synapses.py`
5. `src/hypotheses/storage/local_cache.py`
6. `src/hypotheses/storage/ipfs.py`
7. `src/hypotheses/runtime/metrics.py`
8. `src/hypotheses/runtime/data/`
9. `src/hypotheses/runtime/sandbox/`
10. `src/hypotheses/runtime/run.py`
11. `src/hypotheses/scoring/stats/`
12. `src/hypotheses/scoring/` (rigor, reproduction, improvement,
    novelty, cost, composite)
13. `src/hypotheses/miner/`
14. `src/hypotheses/validator/`
15. `src/hypotheses/cli/`
16. `src/hypotheses/client/` (typed SDK wrapping miner + validator)
17. `src/hypotheses/mcp/` (read-only tools in Phase 1; write tools in
    Phase 2)
18. `src/hypotheses/oracle/` (base in Phase 1; sn42 adapter in Phase 2)

## Per-module definition of done

A module is done when:

- Its public API matches the spec doc that covers it.
- Unit tests pass at ≥ 75% coverage.
- Any integration tests that use the module pass against the bundled
  `H-0001` fixture.
- Public names appear in `__all__`.
- No `TODO`, `FIXME`, or `TBD` remain in the module source.

Module-specific acceptance:

### `errors.py`
- One exception class per row of the fail-fast table.
- All inherit from a single `HypothesisError`.
- Each accepts `**details` and exposes `.details` dict.

### `spec/`
- Parses `hypotheses/*.md` via front-matter + body split.
- JSON Schema at `src/hypotheses/spec/schema/hypothesis.schema.json`.
- Round-trip: parse → serialise → parse equal.
- Tests: `H-0001` pass + ≥ 5 malformed fixtures fail correctly.

### `protocol/signing.py`
- Canonical JSON via `rfc8785`.
- Ed25519 sign/verify via `cryptography`.
- Known-answer test vectors.

### `protocol/synapses.py`
- One pydantic model per synapse in 09-protocol.
- Unknown `schema_version` raises `UnsupportedSchema`.

### `storage/`
- Interface: `put(bytes) -> cid`, `get(cid) -> bytes`, `has(cid) -> bool`.
- Local cache: SHA-256 CIDv1 ∷ `sha2-256`.
- IPFS: use kubo HTTP API; CID is whatever kubo returns.
- Tests: missing cid, corrupt cid, over-cap size.

### `runtime/metrics.py`
- `metrics.report(name, value)` appends one JSONL line to
  `/artifacts/metrics.jsonl`.
- Summariser returns median + n per metric.

### `runtime/data/`
- Hugging Face adapter only in Phase 1.
- Hash-pinned by `dataset_revision`, cache keyed by hash.
- Tests use a tiny fixture dataset, not CIFAR-10.

### `runtime/sandbox/`
- podman invocation with: egress allow-list, wallclock timeout,
  memory cap, readonly code layer, writable `/artifacts`.
- Tests: happy path, wallclock-kill, egress-kill.

### `runtime/run.py`
- `Run.from_env().execute(main)` emits a manifest per 04-miner.
- Determinism: two runs with same seed produce byte-identical
  `metrics.jsonl`.

### `scoring/stats/`
- `welch_t`, `bootstrap` (BCa, 10k resamples), `mann_whitney`.
- Compared against `scipy.stats` reference outputs within tolerance.

### `scoring/`
- Each component a pure function matching 06-scoring signatures.
- `composite.score()` returns a `ScoreVector` dataclass.
- Tests include the worked example (composite = 0.992 ± 0.001).

### `miner/`
- `propose` runs schema validation + dry-run entrypoint on
  `cpu-small`.
- `run` emits artifact bundle matching 04-miner exactly.
- `submit` signs and uploads, returns announcement.

### `validator/`
- Pipeline processes a submission against `H-0001` end-to-end.
- Rerun sample deterministic in
  `(validator_hotkey, epoch, spec_id, version)`.
- Weight vector sums to 1 (± float eps).

### `cli/`
- Single `hypo` entry point per [14](14-cli.md). Subcommands match
  04-miner, 05-validator, and 13-agent-integration exactly.
- CLI is a thin dispatcher; no business logic here.
- `hypo --help`, `hypo help`, and `hypo help <topic>` all work and
  collectively surface the complete command tree.
- Global flags (`--wallet`, `--hotkey`, `--endpoint`, `--profile`,
  `--json`, `--verbose`, `--quiet`) are accepted at any level.
- `--json` switches every command's output to structured JSON.
- Tests: every documented subcommand is exercised with `--help` (for
  surface discoverability) and with a happy-path invocation.

### `client/`
- Public typed SDK per 13-agent-integration.
- `Client` (sync) and `AsyncClient` mirror each other method-for-method.
- Models in `client/models.py` are the single source of truth for the
  public Python surface; internal types are NOT re-exported.
- Tests: a fake backend exercising every public method.

### `mcp/`
- Implements the tool surface in 13-agent-integration.
- Read-only tools in Phase 1; write tools behind `--allow-writes` in
  Phase 2.
- Both stdio-MCP and HTTP-MCP transports from the same tool
  implementations.
- Tests: every tool invoked with a valid call and an invalid call;
  write gating enforced in tests.

### `oracle/`
- Base class: `query(task_ref, declared_answer) -> OracleVerdict`.
- `sn42` stub raises `NotImplementedError` in Phase 1; real adapter
  before Phase 2 exit.

## CI gates

A PR merges only if:

- `ruff check`, `ruff format --check` pass.
- `pyright --strict` passes.
- `pytest` unit+integration passes.
- Coverage thresholds hold (≥ 85% package, ≥ 75% per module).
- `scripts/check_schema_matches_doc.py` passes (spec ↔ schema
  consistency, via `spec-validate.yml`).
- The hypothesis schema validator accepts every file in `hypotheses/`.
- Commitlint passes on every commit in the PR range
  (conventional commits, lowercase subject, ≤72 chars, no
  Claude/Anthropic references). Local `.git/hooks/commit-msg`
  enforces the same rules at commit time.
- TDD gate passes: `feat:` / `fix:` commits touching `src/` are
  preceded by `test:` commits in the PR range
  (`tdd-gate.yml`).
- Bandit passes on `src/` and `scripts/` (`bandit.yml`).
- Vulture reports no dead code ≥ 80% confidence
  (`vulture.yml`).
- Lychee finds no broken links in docs (`link-check.yml`).
- ADR present when `pyproject.toml` or `uv.lock` changes
  (`adr-required.yml`).

Out-of-band gates:

- **Weekly:** `pip-audit` against pinned deps (`pip-audit.yml`).
- **Weekly:** Lychee full-docs scheduled scan.
- **Nightly:** `mutmut` mutation score ≥ 75% per module
  (`mutation.yml`). Regressions block the next release tag, not
  individual PRs.
- **Daily:** `actions/stale` — 30 days to stale, 60 to close
  (`stale.yml`).

Other automations:

- **Dependabot** opens grouped weekly pip PRs and monthly
  actions PRs.
- **Release-please** opens a release PR on every push to `main`,
  deriving the version bump and CHANGELOG from conventional commits.
- **PR labeler** auto-applies labels from changed paths per
  `.github/labeler.yml`.
- **CODEOWNERS** routes reviews by path.

No `[skip ci]` shortcuts, no bypassing hooks.

## Commit messages

Format (enforced by both the local hook and the CI workflow):

```
<type>[(scope)]: <subject>
```

Types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
`refactor`, `revert`, `style`, `test`. Subject lowercase (matches the
`@commitlint/config-conventional` default), ≤ 72 chars, no trailing
period. No bot trailers (no `Co-Authored-By:` lines referencing AI
assistants).

Body and footer are free-form; use them for context that doesn't fit
in the subject.

## Self-audit

This doc is done when:

- Every rule has a corresponding CI gate, hook, or lint rule —
  nothing aspirational.
- The build order covers every module in
  [10](10-repo-layout.md#package-surface).
- Every module's definition-of-done is concrete enough that an
  agent can decide "done / not done" without asking.
- The fail-fast table covers every failure mode referenced
  elsewhere in the spec.
- Tool pins match `pyproject.toml` (once it exists) or the
  matching ADR resolving the discrepancy.

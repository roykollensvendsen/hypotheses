<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AGENTS.md

You're an autonomous agent — a Claude Code session, a Cursor agent,
an OpenAI Agents instance, or something else — reading this repo.
This file is your entry point.

## What this project is

A permissionless scientific hypothesis market on Bittensor. Read
[`VISION.md`](VISION.md) first; everything else is implementation.

**Agent-first operation** is a core commitment: the three active
roles (developing, mining, validating) are designed to be driven by
agents, with humans dropping into the CLI only as an escape hatch.
The spec — not this file — is the contract.

## Where to read, in order

1. [`VISION.md`](VISION.md) — what and why.
2. [`docs/spec/README.md`](docs/spec/README.md) — index of spec docs.
3. [`docs/spec/12-implementation-constraints.md`](docs/spec/12-implementation-constraints.md)
   — the rules you operate under when writing code. This is
   **addressed to you**. Obey it.
4. [`docs/spec/13-agent-integration.md`](docs/spec/13-agent-integration.md)
   — the agent-surface spec (MCP tools, SDK surface, starter agents).
5. [`docs/spec/11-roadmap.md`](docs/spec/11-roadmap.md) — what phase
   we're in and what phase-exit looks like.

Read the rest of the spec as needed; it's in numbered order.

## Which role are you playing?

Pick one. Each has a prompt under [`agents/prompts/`](agents/prompts/):

| role | prompt | purpose |
|------|--------|---------|
| **implementer** | [`agents/prompts/implementer-system.md`](agents/prompts/implementer-system.md) | Build the codebase in `src/hypotheses/` following the spec. |
| **miner** | [`agents/prompts/miner-system.md`](agents/prompts/miner-system.md) | Propose and run hypotheses as a Bittensor miner. |
| **validator operator** | [`agents/prompts/validator-operator-system.md`](agents/prompts/validator-operator-system.md) | Run the validator loop. NEVER touches scoring — scoring is deterministic. |
| **hypothesis proposer** | [`agents/prompts/proposer-system.md`](agents/prompts/proposer-system.md) | Draft new hypotheses from open research notes. |
| **reviewer** | [`agents/prompts/reviewer-system.md`](agents/prompts/reviewer-system.md) | Review incoming spec / hypothesis PRs for rigor. |

If you're in plain Claude Code kicking off Phase 1 implementation,
go to [`docs/implementation-handoff.md`](docs/implementation-handoff.md)
instead; it's the concrete starting prompt.

## How to verify your work

Every gate runs in CI — see
[`docs/spec/15-ci-cd.md`](docs/spec/15-ci-cd.md) for the catalog. The
ones you hit most:

- `ruff check`, `ruff format --check`, `pyright --strict`, `pytest`
  with ≥ 85% coverage ([`ci.yml`](.github/workflows/ci.yml)).
- Conventional commit subjects ([`commitlint.yml`](.github/workflows/commitlint.yml));
  the local `commit-msg` hook rejects violations before push.
- TDD commit order ([`tdd-gate.yml`](.github/workflows/tdd-gate.yml)).
- Per-module mutation score ≥ 75%
  ([`mutation.yml`](.github/workflows/mutation.yml)) — nightly, not
  per-PR.
- SPDX headers on every new `.py`/`.sh`
  ([`spdx.yml`](.github/workflows/spdx.yml)).
- All actions pinned by full SHA
  ([`action-pin-check.yml`](.github/workflows/action-pin-check.yml)).
- PR size ≤ 500 LoC ([`pr-size.yml`](.github/workflows/pr-size.yml)).
- PR title matches conventional-commits
  ([`pr-title.yml`](.github/workflows/pr-title.yml)).

Before opening a PR, run locally:
- `ruff check . && ruff format --check .`
- `pytest` (once there's code)
- `bash scripts/check_action_pins.sh`
- `python3 scripts/check_spdx_headers.py`

## Non-negotiable rules

These come from the spec but are worth repeating up front:

- **No scoring judgment.** Validator scoring is deterministic pure
  functions over artifacts. You operate the validator; you do not
  score. Any LLM output used in scoring is a spec violation.
- **Spec first.** If the code contradicts the spec, the code is wrong
  unless you're fixing a spec bug — in which case the spec PR is in
  the same change.
- **TDD.** Tests committed first (as `test:`), implementation after
  (`feat:`/`fix:`). See [`docs/spec/12-implementation-constraints.md`](docs/spec/12-implementation-constraints.md).
- **Scope discipline.** No speculative features. No "we might want X
  later" hooks. If the spec doesn't say it, don't add it.
- **AGPL-3.0-or-later.** Every new `.py`/`.sh` file under `src/`,
  `scripts/`, `tests/`, `experiments/` needs SPDX headers in its
  first 10 lines. See [`docs/spec/12-implementation-constraints.md#license-headers`](docs/spec/12-implementation-constraints.md#license-headers).

## Escape hatches

You can stop and ask the human operator when:

1. You hit a destructive operation against shared state (force-push,
   mainnet transactions, deleting data).
2. The spec is ambiguous in a way you cannot resolve by applying its
   stated constraints.
3. You discover something that invalidates a phase exit criterion.

Everything else: resolve TBDs autonomously and document your choice
in a `docs/adr/` entry.

## Commit conventions for agents

- Conventional commits, lowercase subject, ≤ 72 chars.
- **No `Co-Authored-By: Claude …`, `Generated with …`, or any
  AI-referencing trailer.** Enforced by the `commit-msg` hook and
  by `commitlint.yml`.
- Types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
  `refactor`, `revert`, `style`, `test`.

## If you get stuck

Open a `spec-question` issue from
[`.github/ISSUE_TEMPLATE/spec-question.yml`](.github/ISSUE_TEMPLATE/spec-question.yml)
— or, in an interactive session, ask the operator.

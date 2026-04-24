<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Contributing

Thanks for being here. This project is built bottom-up, in public, and
every contribution — hypothesis, spec patch, agent prompt, code, bug
report — is welcome under AGPL-3.0-or-later.

Before anything else, read [`VISION.md`](VISION.md). If you disagree
with the vision, open a Discussion rather than a PR; we'd rather
argue about direction in the open than merge-and-revert.

## Three contribution tracks

### 1. Propose a hypothesis (primary on-ramp)

The highest-leverage contribution is a **good hypothesis**.

1. Open a
   [hypothesis-proposal issue](.github/ISSUE_TEMPLATE/hypothesis-proposal.yml)
   first. Sketch the claim, motivation, baseline, and metric in a few
   sentences. This is where we discuss whether the hypothesis is
   well-formed before you spend time drafting the full spec.
2. If the sketch gets buy-in, open a PR adding a file under
   `hypotheses/H-NNNN-<slug>.md` that matches the schema in
   [`docs/spec/02-hypothesis-format.md`](docs/spec/02-hypothesis-format.md).
3. Include the runnable experiment under `experiments/H-NNNN/`. See
   [`experiments/H-0001/`](experiments/H-0001/) for the layout.
4. CI validates the spec; a maintainer reviews for falsifiability,
   non-duplication, and rigor.

A good hypothesis is:

- **Falsifiable** — someone running your protocol could make the
  claim fail.
- **Relational** — "better than <declared baseline>" or "equivalent
  to <declared baseline>", not an absolute accuracy number.
- **Runnable on `cpu-small`** for your first one — save the big
  hypotheses for after you've settled a small one.
- **Not a paper-mill restatement** — if the answer is already in the
  literature, link it and move on.

### 2. Change the spec

The spec is the source of truth. Code that contradicts the spec is a
bug in the code.

1. Open a PR under `docs/spec/`.
2. If the change affects any mechanism that the CI or runtime
   implements, update both in the same PR. CI has a schema-consistency
   gate; divergence fails.
3. PRs changing `pyproject.toml` or `uv.lock` MUST include a new ADR
   under `docs/adr/` (enforced by
   [`adr-required.yml`](.github/workflows/adr-required.yml)).

### 3. Change the code

**Phase 0 has no `src/` yet.** Code contributions open once Phase 1
begins; see [`docs/spec/11-roadmap.md`](docs/spec/11-roadmap.md). When
the code tree exists, the rules from
[`docs/spec/12-implementation-constraints.md`](docs/spec/12-implementation-constraints.md)
are binding:

- **TDD is mandatory.** Failing `test:` commit first; `feat:`/`fix:`
  commit makes it green. The TDD-gate CI job enforces the order.
- **Coverage ≥ 85% package, ≥ 75% per module.**
- **Mutation score ≥ 75% per module** (nightly).
- **Bandit and vulture must pass.**
- **SPDX headers** on every new `.py` and `.sh` file.
- **No speculative features.** No "we might want X later" hooks.
- **The spec and code never diverge** — update the spec in the same
  PR.

## Commit messages

Conventional commits, lowercase subject, ≤ 72 chars, no
`Co-Authored-By: Claude …` or similar AI trailers. See the
[`commit-msg` hook](.git/hooks/commit-msg). The hook is installed
per-clone; a CI job (`commitlint.yml`) catches violations.

Types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
`refactor`, `revert`, `style`, `test`.

## PR size

PRs over 500 LoC changed fail CI via `pr-size.yml`. Decompose. One
concern per PR.

## PR template

Fill out every checkbox in
[`PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md). CI can
only verify some of them; reviewers verify the rest.

## CI gates

Landing a PR requires all of these pass — see
[`docs/spec/15-ci-cd.md`](docs/spec/15-ci-cd.md) for the full catalog:

- `ruff` (lint + format), `pyright --strict`, `pytest` ≥ 85% coverage
- conventional commits (commit-msg hook + CI)
- TDD-order gate for code PRs
- `bandit`, `vulture`, `typos`, lychee link check
- SPDX headers, action-pin check, zizmor workflow lint
- PR title + PR size limits

## Setting up a local clone

Hooks live in `.git/hooks/`; install them by copying from a working
clone. The `pre-commit` hook runs `ruff` on staged Python, and
`commit-msg` enforces the commit convention + AI-reference block.

Full dev-setup docs land with Phase 1.

## Code of Conduct

[Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Enforcement is the
maintainer's job; see [`GOVERNANCE.md`](GOVERNANCE.md).

## Security

Report privately via GitHub's security advisory flow. See
[`SECURITY.md`](SECURITY.md).

## Agents

If you're an LLM agent: start at [`AGENTS.md`](AGENTS.md). The spec
is the contract; if it's not in the spec, it isn't in scope.

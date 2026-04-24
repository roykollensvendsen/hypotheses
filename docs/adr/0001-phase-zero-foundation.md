<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0001 — Phase zero foundation

- **Status:** accepted
- **Date:** 2026-04-24
- **Deciders:** @roykollensvendsen

## Context

Phase 0 is the period before any code lands in `src/`. A set of
interlinked decisions were made during Phase 0 spec-writing that are
load-bearing for everything else. They exist in commit messages and
spec docs but not in a single paper-trail document. This ADR bundles
those decisions into one ledger so future readers (and future Claude
agents) can see what the project committed to early, and when.

Splitting these into individual ADRs would be purer, but six separate
single-decision ADRs for a pre-code project is ceremony we don't need.
If any of these decisions gets revisited, the revisit gets its own
ADR and this one is marked as superseded-in-part.

## Decision

### A. License: AGPL-3.0-or-later

Copyleft, SaaS-loophole-closing, patent-grant-preserving. Chosen over
Apache-2.0 (originally selected) because the project's "bottom-up, not
top-down" ethos (from the originating Discord conversation) benefits
more from enforced source-sharing of network derivatives than from
the Apache patent grant by itself. Accepts that some enterprises will
not adopt the subnet code; treats that as feature, not bug.

### B. Governance: single trusted maintainer through Phase 2

One person (`@roykollensvendsen`) holds merge / tag / revert
authority. Documented in [`GOVERNANCE.md`](../../GOVERNANCE.md).
Transition to multi-maintainer / dTAO-style governance is a Phase 3+
concern with named trigger signals (more than one routine merger,
three months of mainnet stability, ≥10 settled hypotheses).

### C. Operating mode: agent-first

Developing, mining, and validating are driven by autonomous agents by
default; humans drop into the `hypo` CLI as the escape hatch.
Concretely this means: the MCP server + typed Python SDK are first-
class, the CLI cannot offer a capability the agent path lacks, and
validator scoring stays as deterministic pure functions (no LLM
judgment in the scoring path — only in the operator layer around it).
See [`docs/spec/13-agent-integration.md`](../spec/13-agent-integration.md)
and the Mission pillar in [`VISION.md`](../../VISION.md).

### D. Conventional commits with lowercase subject

Commitlint `@commitlint/config-conventional` default (lowercase
subject), 72-char max. Sentence-case was used briefly; switched to
lowercase as the global defacto standard to match the international-
contributor audience the project targets. No Claude/Anthropic
trailers on commits — project history should read as human-authored
to avoid boilerplate.

### E. TDD enforced via commit order

For every `feat:`/`fix:` commit touching `src/`, a prior `test:`
commit must exist in the PR range. Enforced by
[`.github/workflows/tdd-gate.yml`](../../.github/workflows/tdd-gate.yml)
via [`scripts/check_tdd_order.py`](../../scripts/check_tdd_order.py).
Supplemented by nightly `mutmut` with a 75%-per-module floor and a
TDD checkbox on the PR template. Picks the process-level + mechanical
approach over after-the-fact "were these TDD'd?" review.

### F. Action pinning by full SHA (not tags)

Every action reference — first- and third-party — must be a 40-char
commit SHA with a trailing `# vN.N.N` comment. Enforced by
[`.github/workflows/action-pin-check.yml`](../../.github/workflows/action-pin-check.yml)
via [`scripts/check_action_pins.sh`](../../scripts/check_action_pins.sh).
Driven by the 2025 `tj-actions/changed-files` compromise where
malicious code was pushed under existing tags.

## Consequences

### Positive

- Single paper trail for the Phase 0 commitments future agents would
  otherwise re-derive.
- The "bottom-up" ethos has a concrete license mechanism backing it.
- Agents have a clear operating rule (no scoring judgment, full
  capability parity with the CLI).
- Supply-chain risk from action tags is closed.
- TDD is enforceable without manual review effort.

### Negative

- AGPL reduces corporate adoption surface.
- Single-maintainer governance is a bus-factor-of-one risk; mitigated
  only by the fact that the spec, once landed, contains enough context
  to let a new maintainer step in.
- SHA pinning means dependabot must keep actions fresh — a stale SHA
  is a security risk the same way a stale dep is.

### Neutral / deferred

- Multi-maintainer governance, decentralised scoring-weight
  adjustments, and AGPL enforcement policy (we don't have one yet
  for mainnet violators) all deferred to post-mainnet ADRs.
- REUSE spec compliance deferred — conventional SPDX headers in use
  instead.
- `harden-runner` egress policy deferred from `audit` to `block`
  until the egress surface stabilises (Phase 2).

## Related

- Spec: [`VISION.md`](../../VISION.md),
  [`GOVERNANCE.md`](../../GOVERNANCE.md),
  [`docs/spec/12-implementation-constraints.md`](../spec/12-implementation-constraints.md),
  [`docs/spec/13-agent-integration.md`](../spec/13-agent-integration.md),
  [`docs/spec/15-ci-cd.md`](../spec/15-ci-cd.md).
- Hooks: `.git/hooks/pre-commit`, `.git/hooks/commit-msg`.
- Workflows: `.github/workflows/commitlint.yml`,
  `.github/workflows/tdd-gate.yml`,
  `.github/workflows/mutation.yml`,
  `.github/workflows/action-pin-check.yml`,
  `.github/workflows/spdx.yml`.

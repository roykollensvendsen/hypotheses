---
name: 0002 test toolchain
description: choice of pytest + pyright + dev-extras for the Phase-1 test scaffold
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0002 — Test toolchain

## Context

Phase 0 ends with a `pyproject.toml` and an empty
`src/hypotheses` package. The Phase-1 implementing agent needs
a test toolchain already wired so the first PR writes a failing
test in seconds, not configuring pytest.

## Decision

Dev-extras pin: `pytest>=8.0`, `pytest-cov>=5.0`,
`pytest-xdist>=3.6`, `pytest-watcher>=0.4`,
`pyright>=1.1.380`, plus `jsonschema>=4.20` and `pyyaml>=6.0`
(reused by existing `scripts/`).

Coverage threshold lives in `pyproject.toml`
(`fail_under = 0` initially) and ratchets toward 85 per
`HM-REQ-0040` as Phase 1 lands real source code.

## Consequences

- **Positive.** `make test` / `make test-watch` from a fresh
  clone with no extra config; pyright strict and TDD-gate
  already align with `12-implementation-constraints.md`; small
  Python-only toolchain.
- **Negative.** Coverage threshold of 0 is weaker than the
  spec target during the Phase-0 → Phase-1 transition; ratchet
  upward in a single PR per package.
- **Neutral / deferred.** `mutmut` stays a CI-only `uvx` tool
  (per `mutation.yml`), not a dev-extra. `hypothesis` and
  `pytest-asyncio` deferred until the property tests and
  validator pipeline introduce them.

## Related

- Spec: [`12-implementation-constraints.md`](../spec/12-implementation-constraints.md),
  [`15-ci-cd.md`](../spec/15-ci-cd.md),
  [`traceability.md`](../spec/traceability.md).
- ADRs: [0001](0001-phase-zero-foundation.md).
- Workflows: `.github/workflows/{ci,mutation,pip-audit,tdd-gate}.yml`.

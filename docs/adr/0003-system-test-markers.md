---
name: 0003 system-test markers
description: pytest markers and strict-markers mode for the black-box system-test harness
kind: decision
status: accepted
date: 2026-04-26
deciders: ["@roykollensvendsen"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# 0003 — System-test markers

## Context

`docs/spec/23-system-tests.md` defines a black-box system-test
harness with two profiles: a Phase-1 local profile (no external
services) and a Phase-2 chain profile (Bittensor testnet, gated on
`$BITTENSOR_TESTNET=1`). The harness needs a way to select between
profiles in `make system-test` and to keep chain scenarios from
running by default.

## Decision

Register two custom pytest markers in `pyproject.toml`:

- `system_local` — the default profile; runs on a developer laptop.
- `system_chain` — Phase-2 chain scenarios; skipped unless the env
  var is set.

Turn on `--strict-markers` so a typo in a marker name fails
collection rather than silently selecting the wrong test set.
`make system-test` selects `-m system_local`; the chain profile is
opt-in via `make system-test PROFILE=chain` once PR-C lands the
dispatcher.

## Consequences

- **Positive.** Phase-1 scenarios run on a clean clone with no extra
  setup; chain scenarios stay dormant until they have implementations
  to back them; marker typos surface at collection time.
- **Negative.** `--strict-markers` retroactively enforces every
  pre-existing test that uses a custom marker; today no such tests
  exist, so this is a no-op cost. Future PRs that introduce a marker
  must register it here in the same change.
- **Neutral / deferred.** A future `system_perf` marker for
  performance/load tests is out of scope per `23-system-tests.md`
  §Out of scope.

## Related

- Spec: [`23-system-tests.md`](../spec/23-system-tests.md),
  [`11-roadmap.md`](../spec/11-roadmap.md) §Phase 1.
- ADRs: [0002](0002-test-toolchain.md) for the broader pytest
  toolchain choice.
- PRs: [#28](https://github.com/roykollensvendsen/hypotheses/pull/28)
  (spec doc), this PR (harness skeleton).

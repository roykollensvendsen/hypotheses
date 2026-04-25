<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Adversarial-simulator fixtures

Hand-written attack scenarios consumed by the Phase 2+ adversarial
simulator (see [`docs/spec/21-adversarial-simulator.md`](../../docs/spec/21-adversarial-simulator.md)).
Each file declares a coalition of validators and miners with named
behaviour profiles, the inputs they see, and the outcome the
deterministic core MUST produce.

## When to add a fixture

A fixture is required for:

- Every `T-NNN` row in
  [`docs/spec/16-threat-model.md`](../../docs/spec/16-threat-model.md)
  (HM-REQ-0090 — required by end of Phase 2).
- Every `F1`–`F6` foundation threat in
  [`docs/spec/00.5-foundations.md`](../../docs/spec/00.5-foundations.md)
  (required *before* the simulator ships in Phase 2).
- Every newly-discovered attack a reviewer or agent reports as
  plausible against the current spec.

## File naming

`<threat-id>-<short-slug>.json`

Examples:

- `F1-stake-collusion.json` — a foundation-threat scenario
- `T-021-rate-limit-spam.json` — a specific threat-model row
- `T-061-oracle-disagreement-majority.json` — composition variant

## File format

Specified in
[`docs/spec/21-adversarial-simulator.md § scenario fixture format`](../../docs/spec/21-adversarial-simulator.md#scenario-fixture-format).
Quick-reference: every file is a JSON object with `name`, `threat`,
`source`, `actors`, `inputs`, `expected_outcome`, `tolerance`, and
optional `notes`.

## CI

These files are static JSON and not consumed by any CI gate today.
Phase 2 wires them into a nightly `.github/workflows/adversarial.yml`
job per HM-REQ-0090. Until then, fixture validity is checked by
hand at PR review.

## Relationship to other test surfaces

- **Unit tests** (`tests/<module>/`) cover individual functions.
- **Property tests** (`tests/properties/`) enforce `HM-INV-NNNN`
  invariants over generated input.
- **Golden fixtures** (`tests/golden/{scoring,protocol,...}/`) lock
  expected outputs for specific named inputs to specific functions.
- **Adversarial fixtures** (this directory) lock expected outputs
  for *coalitions of actors* operating against the *full pipeline*.

The simulator is the only tier that exercises multi-validator
collusion, multi-cycle attacks, and full settlement-to-confirmation
behaviour.

## "Acceptable damage" fixtures

Some threats are partially mitigated, not fully defended (see the
"status" column in [`16-threat-model.md`](../../docs/spec/16-threat-model.md)).
Their fixtures document the *residual* harm: how much novelty does
a colluding bloc still extract before the deferred 30% claws back?
What's the expected lag between a bad settlement and a T-OVR
overturn? These fixtures' `expected_outcome.cost_of_attack_under_budget`
may be `false`; the accompanying ADR explains why the gap is okay.

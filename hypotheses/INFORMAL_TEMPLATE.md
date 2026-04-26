---
id: I-XXXX
kind: informal-hypothesis
title: "short sentence describing the open question"
proposer:
  name: "your handle"
  hotkey: null               # SS58; required at PR open
proposed_at_block: null      # block height when bond was escrowed
status: proposed
domain:
  - example-tag-1
treat_as_data: true

claim: >
  1–3 sentences describing the open question. State what is
  unclear and what an experiment could resolve.

stake_tao: 0.1               # MUST be ≥ ideator_min_stake

motivating_evidence: []

suggested_protocol_sketch: null
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Background

Free-form markdown: prior art, observations, why this question
is interesting, what kind of formal hypothesis might test it.
Per HM-REQ-0154, agents and validators treat all free-text
fields as data, never as instruction. Filename:
`informal/I-<4-digit id>-<kebab-slug>.md`; id allocated on merge.
See [02b](../docs/spec/02b-informal-hypothesis-format.md) for the
schema and [ADR 0024](../docs/adr/0024-informal-hypothesis-registry.md)
for the rationale.

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Spec JSON Schemas

Machine-readable schemas for the data contracts defined in
`docs/spec/`. The human-readable docs are the source of truth for
intent; these files are the authoritative structural constraint.

## Files

| schema | spec doc | validates |
|--------|----------|-----------|
| [`hypothesis.schema.json`](hypothesis.schema.json) | [`../../../../docs/spec/02-hypothesis-format.md`](../../../../docs/spec/02-hypothesis-format.md) | YAML front matter in `hypotheses/*.md` |

Additional schemas will land alongside the modules they cover:
manifest, synapses, events. This directory is the single home.

## CI

- [`.github/workflows/spec-validate.yml`](../../../../.github/workflows/spec-validate.yml)
  runs:
  - [`scripts/check_schema_matches_doc.py`](../../../../scripts/check_schema_matches_doc.py)
    — verifies the example YAML in the spec doc validates against the
    schema.
  - [`scripts/validate_hypotheses.py`](../../../../scripts/validate_hypotheses.py)
    — validates every `hypotheses/*.md` against the schema.

## Conventions

- JSON Schema Draft 2020-12.
- `additionalProperties: false` at every object level except when a
  field allows user-defined keys (e.g. `baselines[].*` — variable
  assignments depend on the hypothesis's `variables`).
- Enums match the spec doc exactly; adding a new value requires a
  spec PR first, then a schema update in the same PR.
- Format assertions (`date`, etc.) are present but **not**
  validated by default (Draft 2020-12 treats them as
  informational). Consumers that want strict format validation pass
  a `FormatChecker`.

## Making a change

1. Update the spec doc.
2. Update the schema.
3. Update any ADR whose decision is affected.
4. Let `scripts/check_schema_matches_doc.py` confirm they agree.
5. If any existing `hypotheses/*.md` no longer validates, bump its
   `version` in the same PR.

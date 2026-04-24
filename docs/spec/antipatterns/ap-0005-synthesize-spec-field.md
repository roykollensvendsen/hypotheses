<!-- antipattern-content -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0005 — Synthesising a spec field

## Narrative

The JSON Schema in
[`src/hypotheses/spec/schema/hypothesis.schema.json`](../../../src/hypotheses/spec/schema/hypothesis.schema.json)
is the contract for what a hypothesis front matter may contain. Its
sibling schemas for synapses, manifests, and events are likewise
authoritative. Inventing a field because "it would be convenient" —
either in the spec doc, a parser, or a miner — splits the contract
between whoever writes the field and whoever reads it.

## Bad code

```bad-code
# Miner adds a `priority` hint to its manifest, hoping validators
# will weight it. No such field exists in the schema.
manifest = {
    "schema_version": 1,
    "hypothesis_id": "H-0001",
    "hypothesis_version": 1,
    "priority": "urgent",   # not in run-manifest.schema.json
    "runs": [...],
    ...
}
```

Or in the parser:

```bad-code
def parse_hypothesis(front_matter: dict) -> Hypothesis:
    # Tolerantly accept an undocumented `priority` field.
    priority = front_matter.get("priority", "normal")
    return Hypothesis(..., priority=priority)
```

## Why

- Validators ignore unknown fields today but MAY reject them
  tomorrow — the schema uses `additionalProperties: false` at every
  object level except the designated-variable slot.
- Two implementations of "priority" will diverge: one miner's
  `"urgent"` is another's `"high"`, and no contract settles it.
- Schema-first means there is a single place to debate the
  addition: the schema PR. Skipping that PR is bypassing review.

## Correct pattern

If a new field is genuinely useful, add it to the schema **first**
(with a spec-doc PR describing intent), then update producers and
consumers in the same or a follow-up PR. The
[`scripts/check_schema_matches_doc.py`](../../../scripts/check_schema_matches_doc.py)
check is the ratchet: if the doc and schema disagree, CI fails.

```good-code
# 1) Schema PR — extend hypothesis.schema.json
# 2) Spec doc PR — update 02-hypothesis-format.md § Spec fields
# 3) Parser / producer PR — land the typed surface
```

## Spec reference

- [02 § schema validation](../02-hypothesis-format.md#schema-validation)
- [`src/hypotheses/spec/schema/README.md`](../../../src/hypotheses/spec/schema/README.md)
  — "Making a change" section.

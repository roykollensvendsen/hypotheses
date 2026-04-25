<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Golden I/O fixtures

This directory holds **frozen** input→output pairs for the scoring
pipeline, the spec parser, and the wire protocol. Every file is a
JSON document: no Python, no executable code, no tests. Phase 1
test modules under `tests/scoring/`, `tests/spec/`, and
`tests/protocol/` load these files as parametrised cases.

The fixtures are the canonical answers the implementation must
reproduce. When the implementation and a fixture disagree, one of
them is wrong — and the disagreement is resolved through a PR, not
by ad-hoc mutation of the fixture.

## Layout

```text
tests/golden/
├── scoring/
│   ├── worked-example.json
│   ├── rigor-only.json
│   └── falsification.json
├── hypothesis-parsing/
│   └── h-0001.json
└── protocol/
    └── results-announcement-valid.json
```

Each subdirectory maps 1:1 to a consumer module in `src/hypotheses/`
(e.g. `tests/golden/scoring/` → `src/hypotheses/scoring/`). New
fixture categories land alongside the module they exercise.

## File shape

Fixtures are self-describing. Every file is an object with:

| key | required | purpose |
|-----|----------|---------|
| `name` | yes | short, filename-matching identifier |
| `source` | yes | spec doc + section the expected output comes from |
| `input` | yes | arguments to the function under test |
| `expected` | yes | the expected return value (or a shape to assert against) |
| `notes` | no | free-form commentary for humans |

Consumers are allowed to add fields for their own use (e.g. a
tolerance), but removing or reshaping the above breaks every Phase 1
test at once and demands an intentional PR.

## The `--update-golden` convention

Phase 1 test runners support `pytest --update-golden` to overwrite
fixture files from live output. This flag exists for **scaffolding
new fixtures**, not for papering over regressions. A PR that runs
with `--update-golden` and changes a pre-existing file must:

1. Show the diff in the PR description.
2. Cite the spec change (or the bug being fixed) that justified the
   update.
3. Be reviewed by a maintainer who verified the new values by hand.

Silent fixture drift is treated as a spec violation at review time.

## Relationship to the schemas

Every fixture that lives alongside a JSON Schema should also
validate against that schema — e.g. `protocol/results-announcement-valid.json`
parses cleanly against
`src/hypotheses/spec/schema/synapses.schema.json#/$defs/ResultsAnnouncement`.
Phase 1 test code is expected to assert this wherever relevant.

## CI interaction

The golden corpus is static JSON; no CI job consumes it today. Phase 1
lights up the pytest job (see `.github/workflows/ci.yml`), which is
still guarded on the presence of actual test files (`test_*.py` /
`*_test.py`) — not merely on the presence of `tests/`.

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Implementation task graphs

This directory holds YAML task graphs for the implementing agent.
Each phase gets one file; every task carries:

- `id` — stable `T-P<phase>-NNN` identifier.
- `title` — short imperative.
- `path` — the file the task lands at.
- `depends_on` — ordered prerequisites by `id`.
- `reqs` — list of `HM-REQ-NNNN` / `HM-INV-NNNN` ids the task
  must satisfy.
- `dod` — definition-of-done bullets that an independent reviewer
  can check.
- `sibling_tests` — the path tests for this task land at (to keep
  TDD attribution unambiguous).
- `size_budget_loc` — soft LoC ceiling (excluding tests); the
  PR-size gate is 500 LoC hard.

The graph is **ordered** — tasks are landed in the order listed,
with `depends_on` enforcing strict prerequisites. The implementing
agent walks the list top-to-bottom, lands one task per PR, and
checks every DoD bullet before moving on.

## Files

| phase | file |
|-------|------|
| Phase 1 | [`phase-1.yml`](phase-1.yml) |

Later phases get their own files as they kick off.

## How `dod` is evaluated

A task is done when *every* `dod` bullet is true on `main` after the
task's PR merges. Mechanical bullets (test passes, file exists, CI
gate green) are checkable without judgement; prose bullets ("matches
the spec doc") are the PR reviewer's job.

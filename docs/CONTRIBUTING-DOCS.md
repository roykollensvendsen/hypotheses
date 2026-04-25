<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Documentation contribution guide

This file is the rulebook for *documentation* changes — what front
matter is required where, which CI gates a docs PR must pass, and
how to keep the single-source-documentation principle
([`HM-REQ-0110`](spec/12-implementation-constraints.md))
mechanically true.

For non-doc contributions (hypotheses, code, security disclosures)
see [`CONTRIBUTING.md`](../CONTRIBUTING.md). For the agent-side
entry point see [`AGENTS.md`](../AGENTS.md).

## What lives where

| place | purpose | front-matter |
|-------|---------|--------------|
| `docs/spec/NN-*.md`, `docs/spec/NN.5-*.md` | numbered spec docs in a fixed reading order | required (see below) |
| `docs/spec/{requirements,invariants,traceability,load-for-index}.md` | cross-cutting indexes | required |
| `docs/spec/README.md`, `docs/spec/formal/README.md` | spec-tree indexes | required |
| `docs/spec/antipatterns/ap-*.md` | "do NOT do this" corpus | line 1 must be `<!-- antipattern-content -->` |
| `docs/spec/_schemas/*.json` | JSON Schemas the front-matter validator loads | not markdown |
| `docs/adr/NNNN-*.md` | architecture decision records | not yet validated; future PR adds `kind: decision` |
| `docs/CONTRIBUTING-DOCS.md` (this file), `docs/implementation-handoff.md`, `docs/initial-discord-conversation.md` | narrative docs outside the spec tree | none |
| `hypotheses/H-NNNN-*.md` | preregistered hypothesis specs | validated by `validate_hypotheses.py` |
| `agents/prompts/*-system.md` | role prompts, model-neutral | validated by `check_agent_prompts.py` |
| `llms.txt`, `llms-full.txt`, `docs/spec/load-for-index.md` | **generated**; do not edit by hand | header `<!-- generated:by=... -->` |

## Front-matter schema for spec docs

Every file under `docs/spec/` (excluding `antipatterns/` and
`_schemas/`) carries this YAML block at the very start of the file:

```yaml
---
name: short identifier
description: one-line summary; also used in llms.txt
tokens: 1500            # rounded measurement; the auditor warns at 40% drift
load_for: [implementation, review]   # task tags; controlled vocabulary
depends_on: ["02", "18"]              # NN strings; quote to keep the leading zero
kind: contract                        # contract | explanation | reference
---
```

The schema lives at
[`docs/spec/_schemas/spec-frontmatter.schema.json`](spec/_schemas/spec-frontmatter.schema.json)
and is enforced by `scripts/check_frontmatter.py`. The `load_for`
enum is locked to `agent-operator`, `governance`, `implementation`,
`proposal`, `review`; new tags require a schema PR.

## The three `kind:` values

The taxonomy is Diátaxis-derived but reduced to three values that
match how this project actually writes docs:

- `contract` — **normative** spec doc. Carries `HM-REQ-NNNN` or
  `HM-INV-NNNN` blockquotes. Code that contradicts a `contract`
  doc is a bug in the code (the spec wins; see
  [`HM-REQ-0110`](spec/12-implementation-constraints.md)).
- `explanation` — narrative *why*-docs. Examples:
  [`00-overview`](spec/00-overview.md),
  [`00.5-foundations`](spec/00.5-foundations.md),
  [`03-architecture`](spec/03-architecture.md),
  [`11-roadmap`](spec/11-roadmap.md). Not normative, not a contract.
- `reference` — catalogs, glossaries, indexes. Examples:
  [`01-glossary`](spec/01-glossary.md),
  [`requirements`](spec/requirements.md),
  [`invariants`](spec/invariants.md), the spec
  [`README`](spec/README.md). Descriptive, look-up-shaped.

Two further kinds are reserved for future use but not yet emitted:

- `decision` — for ADRs once they grow YAML front-matter.
- `hypothesis` — for `hypotheses/H-*.md` once their schema
  acquires a `kind:` field.

`tutorial` and `how-to` (the canonical Diátaxis pair) are not used
yet because the project doesn't ship those genres at this phase.

## The single-source rule (HM-REQ-0110)

Every fact, contract, parameter, or list in this repo has exactly
**one** canonical home. Other documents that need it MUST link to
the canonical home rather than restate it. Drift between a
canonical statement and a restatement is a bug in the restatement.

Canonical homes by topic:

- *Vision and mission* → [`VISION.md`](../VISION.md).
- *Agent role catalogue and trust boundary* → [`AGENTS.md`](../AGENTS.md).
- *Contribution paths* → [`CONTRIBUTING.md`](../CONTRIBUTING.md).
- *Decision authority and process* → [`GOVERNANCE.md`](../GOVERNANCE.md).
- *Vulnerability disclosure flow* → [`SECURITY.md`](../SECURITY.md).
- *Hypothesis schema* → [`docs/spec/02-hypothesis-format.md`](spec/02-hypothesis-format.md)
  and [`src/hypotheses/spec/schema/hypothesis.schema.json`](../src/hypotheses/spec/schema/hypothesis.schema.json).
- *Lifecycle states and transitions* → [`docs/spec/17-hypothesis-lifecycle.md`](spec/17-hypothesis-lifecycle.md).
- *Constants like `rerun_fraction=0.4`* → marked
  `<!-- canonical:KEY=VALUE -->` in their owning doc; checked by
  [`scripts/check_spec_consistency.py`](../scripts/check_spec_consistency.py).

Worked example:

> The 70/30 deferred-settlement split lives in
> [`docs/spec/17-hypothesis-lifecycle.md`](spec/17-hypothesis-lifecycle.md)
> as `HM-REQ-0070`.
>
> [`docs/spec/00.5-foundations.md`](spec/00.5-foundations.md)
> needs to talk about it (it's a defence against F6 long-latency
> rent extraction). Foundations links — `cf. HM-REQ-0070` —
> rather than restating the percentages.
>
> [`docs/spec/22-security-bounty.md`](spec/22-security-bounty.md)
> also references it. Same: link, never restate the numbers.
>
> If a future PR changes the 70/30 split, only `17-…md` updates.
> Restatements are bugs in the restatements.

### Generated files

`llms.txt`, `llms-full.txt`, and `docs/spec/load-for-index.md` are
**derived** — they restate by quoting whole bodies (llms-full) or
by joining metadata (llms.txt, load-for-index). They carry
`<!-- generated:by=scripts/X.py from=Y -->` headers and are
snapshot-checked in CI (`git diff --exit-code`). Edit the
generator, not the output.

`.vale/baseline.json` records pre-existing offence counts the
project has agreed to live with; it is data, not spec content,
and is monotonically non-increasing.

## Adding a new spec doc

To add `docs/spec/23-foo.md`:

1. Create the file with the front-matter block above. Pick a
   `kind:`, declare `tokens:` (rough wc-based estimate), enumerate
   `load_for:`, list `depends_on:`.
2. Add an index entry in [`docs/spec/README.md`](spec/README.md).
3. If the doc is referenced from a context-routing row, update the
   row in [`AGENTS.md`](../AGENTS.md) and recompute the row total.
   `.github/workflows/agents-routing.yml` checks the arithmetic.
4. If the doc introduces new `HM-REQ-NNNN` or `HM-INV-NNNN`
   statements, add rows in
   [`docs/spec/requirements.md`](spec/requirements.md) /
   [`invariants.md`](spec/invariants.md) and matching rows in
   [`docs/spec/traceability.md`](spec/traceability.md).
5. Run `make docs-check` locally; commit when green.

## CI gate catalog

Doc-quality gates that block merge:

| gate | enforces |
|------|----------|
| `frontmatter.yml` | spec front-matter schema, `depends_on` resolution |
| `agents-routing.yml` | every routing-table summand resolves; arithmetic sane |
| `token-budget.yml` | declared `tokens:` within ±100 % of measurement (warn at 40 %) |
| `orphan-docs.yml` | every `.md` reachable from a root |
| `hypothesis-status.yml` | `hypotheses/H-*.md` `status:` is in the lifecycle enum |
| `agent-prompts.yml` | role prompts ≤200 lines and model-neutral |
| `vale.yml` | prose-style ratchet against `.vale/baseline.json` |
| `markdownlint.yml` | markdown syntax (per `.markdownlint.jsonc`) |
| `link-check.yml` | lychee link validation |
| `typos.yml` | spell-checker |
| `spec-consistency.yml` | cross-reference integrity, canonical-constant check |
| `requirements.yml` | HM-REQ/HM-INV index ↔ inline tags ↔ traceability matrix |
| `spec-validate.yml` | hypothesis YAML against the JSON Schema |
| `prompt-injection.yml` | spec content is data, not directives |
| `llms-txt.yml`, `load-for-index.yml` | generated files committed and current |
| `citation-validate.yml` | `CITATION.cff` schema valid |

Each one mirrors a script under `scripts/check_*.py` or
`scripts/gen_*.py`. Run the full suite locally with
`make docs-check` (which calls `scripts/docs_doctor.py`).

## Running locally

```bash
make precommit-install   # one-time; wires .pre-commit-config.yaml
make docs-check          # everything CI runs (skips optional tools if absent)
```

Optional tooling for full coverage: `lychee`, `vale`, `typos`,
`npx markdownlint-cli2`. The orchestrator skips silently if a tool
is missing.

## Changes deferred

Open improvements that are spec'd but not yet implemented:

- **Antipattern `protects:` tags** — each `ap-*.md` should declare
  which `HM-REQ`/`HM-INV` it protects. Editorial work.
- **ADR `kind:` field** — ADRs need YAML front-matter introduced.
- **Hypothesis `kind:` field** — `hypothesis.schema.json` needs to
  allow/require `kind: hypothesis`.
- **Glossary-link enforcement** — depends on the glossary
  acquiring per-term heading anchors.
- **Docs-impact PR comment bot** — `scripts/docs_impact_comment.py`
  needs git-diff context that is awkward to test outside a real
  PR runtime. Lands in a follow-up.
- **Test-docstring → `HM-REQ` reverse scanner** — activates when
  `tests/test_*.py` first ships in Phase 1.
- **Static documentation site (mkdocs-material)** — explicitly
  deferred per the documentation-quality sprint scoping decision.

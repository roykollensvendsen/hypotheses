---
name: ci and automations
description: catalog of `.github/` workflows, configs, templates, and scripts
---

# 15 — CI / CD and repo automations

Everything in `.github/` has a purpose. This doc is the catalog: what
each file does, when it runs, what it blocks, and how to change it.
When `.github/` and this doc disagree, the disagreement is a bug — fix
the spec or the config so they match.

## Pinning policy

All third-party GitHub Actions MUST be referenced by full commit SHA
with a trailing `# vN.N.N` comment naming the version:

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2
```

Reason: tag references (`@v4`) can be moved by the action publisher to
point at new code without notice. SHA references cannot. This is the
same property we enforce on Python deps.

Current violations (tag-pinned, to be SHA-pinned in a follow-up PR;
each requires its own ADR):

- `lycheeverse/lychee-action@v2` (link-check.yml)
- `googleapis/release-please-action@v4` (release-please.yml)
- `actions/labeler@v5` (labeler.yml)
- `actions/stale@v9` (stale.yml)

**TBD** — add a CI workflow (`check-action-pins.yml`) that greps for
`@v` patterns and fails the PR. Once added, the follow-up that
SHA-pins the four above is a single-PR chore.

## Workflow catalog

Sorted by when it fires. `Gate` = blocks PR merge on failure.

### On every PR (blocking gates)

| workflow | purpose | guard |
|----------|---------|-------|
| `ci.yml` | `ruff check`, `ruff format --check`, `pyright --strict`, `pytest` with ≥85% coverage | skip pyright/pytest until `pyproject.toml` / `tests/` exist |
| `commitlint.yml` | conventional commits, ≤72 chars, no Claude/Anthropic references; skipped for dependabot | always |
| `tdd-gate.yml` | `test:` commits precede `feat:` / `fix:` commits touching `src/` | always; trivially passes with no `src/` |
| `bandit.yml` | Python security lint on `src/` and `scripts/` | skip until any python source exists |
| `vulture.yml` | dead-code detector at 80% confidence | skip until `src/` exists |
| `spec-validate.yml` | JSON Schema ↔ hypothesis doc consistency; per-hypothesis schema validation | skip until schema file and script exist |
| `link-check.yml` | `lychee` on every markdown file | always |
| `adr-required.yml` | `docs/adr/*.md` required when `pyproject.toml` or `uv.lock` changes | always |

### On every push to `main`

| workflow | purpose |
|----------|---------|
| `ci.yml`, `commitlint.yml`, `bandit.yml`, `vulture.yml`, `spec-validate.yml`, `link-check.yml` | same gates as PR, catches direct pushes |
| `release-please.yml` | opens / updates a release PR with version bump + generated CHANGELOG from conventional commits |
| `spec-mirror.yml` | mirrors merged spec files to IPFS (planned; not yet implemented) |

### On schedule

| workflow | cadence | purpose |
|----------|---------|---------|
| `pip-audit.yml` | weekly (Mon 05:00 UTC) + PR on dep files + manual dispatch | CVE scan on pinned deps |
| `link-check.yml` | weekly (Mon 06:00 UTC) | re-verify external links |
| `mutation.yml` | nightly (04:00 UTC) + manual dispatch | `mutmut` ≥75% per module |
| `stale.yml` | daily (03:00 UTC) + manual dispatch | mark / close inactive issues and PRs |

### On PR target (labeler only)

| workflow | purpose |
|----------|---------|
| `labeler.yml` | auto-apply labels from changed paths per `.github/labeler.yml` |

## Configs

### `.github/dependabot.yml`

Two ecosystems:

- **pip**, weekly, grouped: `security` group (all security updates, any
  type) and `minor` group (minor + patch). Prefix `chore`, scope
  included, label `deps`. Cap 5 open PRs.
- **github-actions**, monthly. Prefix `ci`, scope included, labels
  `ci` + `deps`.

Dependabot commit subjects are capitalized ("Bump X from Y to Z"),
which fails our lowercase commitlint rule. The `commitlint.yml`
workflow skips `github.actor == 'dependabot[bot]'`. Dependabot PRs
are intended to be squash-merged with a human-edited conventional
title.

### `.github/labeler.yml`

Maps path patterns to labels used for triage: `spec`, `hypothesis`,
`experiment`, `ci`, `miner`, `validator`, `runtime`, `scoring`,
`protocol`, `client`, `mcp`, `agents`, `docs`, `deps`.

Add a new label only when a new top-level area appears (e.g. a new
`src/hypotheses/<area>/`); keep the list short.

### `.github/CODEOWNERS`

Defaults all paths to `@roykollensvendsen`. Spec, hypothesis registry,
experiments, `.github/`, and `scripts/` are explicitly owned by the
same handle for clarity. Ownership expands when contributors join;
adding a new area means a new CODEOWNERS line in the same PR that
introduces the directory.

## Templates

### `.github/PULL_REQUEST_TEMPLATE.md`

Two checklists: **TDD** (tests committed first, impl made them pass,
refactor under green, mutation score check) and **Spec alignment**
(spec updated in-PR for behaviour changes; schema ↔ doc agree).

### Issue templates (planned, not yet created)

The collaboration kit will add:

- `hypothesis-proposal.yml` — the primary on-ramp; collects the same
  fields as a full hypothesis spec but at a lower fidelity so new
  contributors can sketch before drafting.
- `spec-question.yml` — "why does doc N say X?" form.
- `bug.yml` — standard bug report.

Until those exist, GitHub falls back to a free-form issue — acceptable
for Phase 0.

## Scripts

Shell- and Python-only, invoked by workflows or by operators.

| script | purpose | used by |
|--------|---------|---------|
| `scripts/check_tdd_order.py` | PR gate: `test:` before `feat:`/`fix:` touching `src/` | `tdd-gate.yml` |
| `scripts/check_mutation_score.py` | parse `mutmut results`; enforce ≥75% | `mutation.yml` |
| `scripts/check_adr_required.py` | require ADR when `pyproject.toml`/`uv.lock` changes | `adr-required.yml` |
| `scripts/check_schema_matches_doc.py` | spec ↔ JSON Schema consistency (not yet implemented) | `spec-validate.yml` |
| `scripts/validate_hypotheses.py` | JSON Schema validate every file in `hypotheses/` (not yet implemented) | `spec-validate.yml` |
| `scripts/register_subnet.sh` | one-off Bittensor registration (Phase 2+) | operator |
| `scripts/dev-miner.sh` / `dev-validator.sh` | local dev helpers (Phase 1) | operator |

Every workflow invokes scripts via `python3 scripts/<name>.py` or
`uv run …`; no inline logic beyond orchestration.

## Adding a new automation

Decision flow:

1. **Is it a PR gate?** If yes — add to the catalog under "on every
   PR"; ensure it has a guard for Phase 0 (no-op until the path it
   checks exists); update `12-implementation-constraints.md`'s CI
   gates section.
2. **Is it scheduled?** If yes — add cadence and purpose to the
   schedule table; prefer UTC times staggered ≥1h apart from the
   others; include `workflow_dispatch` for manual runs.
3. **Does it change any existing workflow?** Update this doc first,
   then the YAML, in the same PR. CI will fail if they disagree for
   the fields we enforce mechanically.
4. **Does it use a new action?** SHA-pin it; add to the pinning policy
   section if the action becomes a repeat user; ADR if the action is
   doing anything beyond trivial orchestration.

## Removing an automation

A workflow may be removed only when the capability it enforces is
covered by another gate. A removal PR updates this doc (removes the
row) and includes a one-line rationale in the commit message.

## Non-goals

- **Matrix builds across Python versions.** We pinned 3.12.
- **Matrix across OS.** Linux-only by spec.
- **DCO / CLA bots.** AGPL doesn't need either.
- **Welcome bots, all-contributors bots.** Low signal.

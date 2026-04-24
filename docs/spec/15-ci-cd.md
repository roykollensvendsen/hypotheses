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

All GitHub Actions (first-party and third-party) MUST be referenced by
full commit SHA (40 hex chars) with a trailing `# vN.N.N` comment
naming the version:

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2
```

Reason: tag references (`@v4`) can be moved by the action publisher to
point at new code without notice. SHA references cannot. The
`tj-actions/changed-files` compromise of 2025 pushed malicious code
under existing tags; SHA pinning would have prevented it.

Enforcement: `.github/workflows/action-pin-check.yml` runs
`scripts/check_action_pins.sh` on every PR and push, greps every
`uses:` line in `.github/workflows/**` and `.github/actions/**`, and
fails if any ref is not a 40-char SHA. Dependabot (in the
`github-actions` ecosystem) opens monthly PRs that bump SHAs to the
latest release — the SHA-pinning policy does NOT mean stale deps.

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
| `action-pin-check.yml` | every action ref is a 40-char SHA | always; runs on `.github/**` changes |
| `zizmor.yml` | static-analysis of workflows; fail on medium+ findings | always; runs on `.github/**` changes |
| `typos.yml` | spell-check all tracked files | always |
| `pr-title.yml` | PR title is a conventional-commit subject (needed for squash merges) | always |
| `pr-size.yml` | label by size; fail PRs >500 LOC | always (excludes `uv.lock`, LICENSE, CHANGELOG) |
| `spdx.yml` | SPDX license + copyright header on every `.py`/`.sh` under `src/`, `scripts/`, `tests/`, `experiments/` | runs on source-path changes |

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
| `zizmor.yml` | weekly (Mon 07:00 UTC) + `.github/**` PRs + push | workflow-security lint |
| `scorecard.yml` | weekly (Mon 08:00 UTC) + push to main | OpenSSF Scorecard → code-scanning SARIF |
| `mutation.yml` | nightly (04:00 UTC) + manual dispatch | `mutmut` ≥75% per module |
| `stale.yml` | daily (03:00 UTC) + manual dispatch | mark / close inactive issues and PRs |

### On PR target

| workflow | purpose |
|----------|---------|
| `labeler.yml` | auto-apply labels from changed paths per `.github/labeler.yml` |
| `pr-size.yml` | size label + >500 LoC gate |
| `pr-title.yml` | conventional-commit PR title (edited events also trigger) |

## Workflow hardening conventions

Every workflow follows the same conventions:

- **Top-level `permissions:`** — defaults to `contents: read`; write
  scopes granted only to the job that needs them (e.g. `pull-requests:
  write` on the labeler, `contents: write` on release-please,
  `security-events: write` on scorecard).
- **Concurrency groups** — PR-triggered workflows set
  `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` to
  kill superseded runs without affecting pushes to `main`. Schedule-
  and push-only workflows do not set concurrency.
- **`step-security/harden-runner`** runs first in every job with
  `egress-policy: audit`. This logs outbound connections from the
  runner; we may switch to `block` with an explicit allow-list once
  the egress surface stabilises in Phase 2.
- **`astral-sh/setup-uv`** with `enable-cache: true` is the canonical
  way to install `uv` — caches wheels across jobs, invalidates on
  `uv.lock` changes, and replaces manual `curl | sh` installs.
- **`actions/setup-python`** pins to `3.12.7` (patch version, not
  major). Patch-level drift has caused real CI breakage in the past.
- **Tool invocation via `uvx`** where possible (ruff, bandit,
  vulture, pip-audit) — no separate install steps, cached by uv.

## License marking

The project is AGPL-3.0-or-later. License is marked in three places:

1. **`LICENSE` at repo root** — full license text.
2. **SPDX headers on every source file** — see
   [12-implementation-constraints § License headers](12-implementation-constraints.md#license-headers).
3. **`pyproject.toml` metadata** — `license = "AGPL-3.0-or-later"` +
   AGPL classifier (lands in Phase 1).

CI enforcement is `.github/workflows/spdx.yml` +
`scripts/check_spdx_headers.py`. The approach is what the research
classified as "conventional" — SPDX headers + package metadata, but
not the rigorous REUSE spec (no `REUSE.toml`, no `LICENSES/`
directory). Upgrading to REUSE is a one-PR change if EU CRA or
mixed-license content forces it.

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

### Issue templates

Live under `.github/ISSUE_TEMPLATE/`:

- `config.yml` — disables blank issues; adds contact links for
  Discussions and security advisories.
- `hypothesis-proposal.yml` — primary on-ramp; low-fidelity sketch
  of a hypothesis with required falsifiability and relational-
  baseline checkboxes. PR with the full spec file follows.
- `spec-question.yml` — "why does doc N say X?" form with a doc
  picker.
- `bug.yml` — standard bug report with repro + env fields.

Blank issues are disabled — everything enters via a template, keeping
triage scannable.

## Scripts

Shell- and Python-only, invoked by workflows or by operators.

| script | purpose | used by |
|--------|---------|---------|
| `scripts/check_tdd_order.py` | PR gate: `test:` before `feat:`/`fix:` touching `src/` | `tdd-gate.yml` |
| `scripts/check_mutation_score.py` | parse `mutmut results`; enforce ≥75% | `mutation.yml` |
| `scripts/check_adr_required.py` | require ADR when `pyproject.toml`/`uv.lock` changes | `adr-required.yml` |
| `scripts/check_action_pins.sh` | fail if any action ref is not a 40-char SHA | `action-pin-check.yml` |
| `scripts/check_spdx_headers.py` | SPDX license + copyright header on every source file | `spdx.yml` |
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

## Deferred / planned

These were considered during the Phase 0 CI hardening and deliberately
deferred. Each has a named trigger for when to pick it up.

### Tier 2 — Land as Phase 1 begins (when `src/` exists)

| item | rationale | trigger |
|------|-----------|---------|
| **CodeQL for Python** (`github/codeql-action@v3`) | Free SAST for public repos, catches what `bandit` misses (SQLi, path traversal, insecure deserialization). | First `src/hypotheses/**/*.py` commit. |
| **`pip-audit` → official action with SARIF upload** (`pypa/gh-action-pip-audit`) | Findings land in the Security tab with triage UI rather than raw logs. | `pyproject.toml` exists. |
| **JUnit XML + test summary** (`pytest --junitxml=junit.xml` + `mikepenz/action-junit-report`) | Gives agents structured failure data rather than scraped logs. | First `tests/` file. |
| **Codecov with OIDC** (`codecov/codecov-action@v5`, `use_oidc: true`) | No secret to rotate; coverage-diff PR comment; visibility drives the norm. | First `tests/` file. |
| **`pytest-benchmark` regression gate** (`benchmark-action/github-action-benchmark`, alert >20% regression) | Performance cliffs are the class of bug LLM agents most frequently introduce. | First `tests/benchmark/`. |

### Tier 3 — Land at first release (Phase 3)

| item | rationale | trigger |
|------|-----------|---------|
| **PyPI trusted publishing via OIDC** (`pypa/gh-action-pypi-publish`) | No long-lived API tokens; PyPI's default path. | First `release-please` release PR merged. |
| **SLSA Level 3 build provenance + `actions/attest-build-provenance`** | Downstream consumers verify artifacts came from this repo+workflow. | Same as above. |
| **SBOM on release** (`anchore/sbom-action`, CycloneDX) | NIST SSDF / EO 14028; enterprise downstream adoption. | Same as above. |

### Other deferred work

| item | rationale | trigger |
|------|-----------|---------|
| **`harden-runner` `egress-policy: block`** (currently `audit`) | Audit mode logs outbound; block mode enforces an allow-list. Requires stable egress surface. | End of Phase 2 — after observation period is long enough to build the allow-list. |
| **`spec-mirror.yml`** (IPFS mirror of `hypotheses/`) | Referenced in 03-architecture; kubo-node-based mirroring. | IPFS pinning service stood up (Phase 2). |
| **`scripts/check_schema_matches_doc.py`** | Consistency between `docs/spec/02-hypothesis-format.md` and the JSON Schema. | JSON Schema file exists (early Phase 1). |
| **`scripts/validate_hypotheses.py`** | JSON Schema validation of every `hypotheses/*.md`. | Same as above. |
| **AI-generated-code attestation** | Emerging 2026 pattern; no canonical action yet. | Canonical tooling exists. |
| **Branch protection rules as code** (Rulesets + settings-as-code) | Declarative branch protection, reviewable in PRs. | Phase 2 (move off direct pushes). |

### Explicit non-goals (will not implement)

- **Matrix builds across Python versions.** We pinned 3.12.
- **Matrix across OS.** Linux-only by spec.
- **DCO / CLA bots.** AGPL doesn't need either.
- **Welcome bots, all-contributors bots.** Low signal.
- **`probot/settings`** for repo settings. Unmaintained. If
  settings-as-code becomes necessary, use GitHub Rulesets or
  Terraform's `github_repository_ruleset`.

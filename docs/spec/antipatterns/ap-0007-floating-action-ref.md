<!-- antipattern-content -->
<!-- protects: HM-REQ-0041 -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0007 — Floating action reference

## Narrative

Every `uses:` reference in `.github/workflows/**` and
`.github/actions/**` MUST be a 40-character commit SHA, with the
human-readable tag in a trailing comment. Tag references (or even
`@main`) allow the upstream maintainer (or an attacker who compromises
their account) to replace the action's code under the tag — the
2025 `tj-actions/changed-files` class of attack.

## Bad code

```bad-code
# .github/workflows/some.yml
- uses: actions/checkout@v6          # tag can be moved
- uses: actions/setup-python@main    # even worse — branch
- uses: astral-sh/setup-uv@v8        # same problem
```

## Why

- `action-pin-check.yml` fails the PR immediately.
- Tag-moved action = arbitrary code execution on our runner, with
  our `GITHUB_TOKEN` and any secrets the workflow has access to.
- Every past workflow-compromise incident in the wild used this
  exact class of bug.
- This is threat [T-030](../16-threat-model.md#d-supply-chain-attacks)
  — "tag-moved GitHub Action pushes malicious code".

## Correct pattern

```good-code
# .github/workflows/some.yml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2
- uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405  # v6.2.0
- uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b  # v8.1.0
- uses: step-security/harden-runner@8d3c67de8e2fe68ef647c8db1e6a09f647780f40  # v2.19.0
```

Dependabot opens PRs to bump the SHA when a new tag is published;
the review step verifies the new SHA matches the tag the maintainer
has published (double-check via the GitHub API or the mirror the
action publishes).

## Spec reference

- [15 § pinning policy](../15-ci-cd.md#pinning-policy)
- [`scripts/check_action_pins.sh`](../../../scripts/check_action_pins.sh)
- [`.github/workflows/action-pin-check.yml`](../../../.github/workflows/action-pin-check.yml)
- Threat [T-030](../16-threat-model.md#d-supply-chain-attacks)

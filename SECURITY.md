<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Security policy

## Reporting a vulnerability

**Do not open a public issue.** Use GitHub's
[private security advisory](https://github.com/roykollensvendsen/hypotheses/security/advisories/new)
flow. This goes directly to the maintainer. Expect a first response
within 7 days and a triage decision within 14.

If the advisory UI is not available to you, email
**roykollensvendsen@gmail.com** with subject line
`SECURITY: hypotheses: <short description>`.

## What to include

- Affected commit or tag.
- Reproducer — minimal steps.
- Impact — what an attacker can do.
- Suggested mitigation if you have one.

## Our response

1. Acknowledge receipt within 7 days.
2. Confirm or dispute the finding within 14 days.
3. Coordinate a disclosure timeline with you — default embargo 90
   days from confirmation, negotiable based on severity and your
   preference.
4. Publish a GitHub Security Advisory alongside the fix, with
   credit if you want it.

## Scope

In scope:

- **Runtime sandbox escape** (when Phase 1+ code exists) — a miner's
  experiment reading host filesystem, escaping network egress
  limits, or elevating privileges.
- **Signature / signing-key handling** in the miner and MCP server.
- **Validator score integrity** — any path that produces a score
  vector a pure function of inputs wouldn't produce.
- **Hypothesis registry tampering** — ways to have a hypothesis
  accepted without passing schema validation.
- **Supply chain** — a pinned dep we missed, an action SHA we
  didn't verify, a dependabot PR that shouldn't have been
  auto-merged.

Out of scope:

- Vulnerabilities in Bittensor itself (report to their security
  team).
- Vulnerabilities in pinned third-party deps (report upstream;
  we will track via `pip-audit`).
- Denial-of-service from submitting large but honest artifacts
  within the declared quotas.
- Social-engineering attacks outside the repo.

## Disclosure

We publish confirmed vulnerabilities as
[GitHub Security Advisories](https://github.com/roykollensvendsen/hypotheses/security/advisories)
after the fix ships or the embargo ends, whichever comes first. The
AGPL license does not change your reporting obligations here.

### Confirmed findings can become security-hypotheses

A confirmed finding may, with the discoverer's consent, be
published as a **security-hypothesis** on the registry per
[`docs/spec/22-security-bounty.md`](docs/spec/22-security-bounty.md).
The discoverer's hotkey then earns the standard scoring components
(rigor + reproduction + novelty + improvement) when the public
hypothesis settles. The private-disclosure timeline above
(7-day ack, 14-day triage, 90-day default embargo) is unchanged;
the bounty mechanism is layered on top and rewards honest
coordinated disclosure. HM-REQ-0100 zeros the `improvement`
component for findings that bypass this private flow.

## Public fix timeline

1. Private advisory created.
2. Fix developed on a private branch.
3. Fix merged and tagged.
4. Advisory published with CVE (requested from GitHub if warranted).
5. Notification to downstream consumers — for subnet operators this
   means an issue in `hypotheses` plus a note in the release notes.

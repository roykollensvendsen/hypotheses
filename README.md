<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# hypotheses

A permissionless scientific hypothesis market on Bittensor. Miners
preregister falsifiable claims about machine learning, run the
experiments themselves, and earn TAO when validators confirm their
results reproduce and improve on declared baselines.

**Read first:** [`VISION.md`](VISION.md) — what we're building and why.

## Stage

Phase 0 — *spec freeze*. No code in `src/` yet; the spec, CI, and
collaboration infrastructure land before implementation begins. See
[`docs/spec/11-roadmap.md`](docs/spec/11-roadmap.md).

## Four ways to contribute

- **Mine** — propose a hypothesis, run it, submit. Entry tier runs on
  `cpu-small`; a laptop is enough to start. See
  [`docs/spec/04-miner.md`](docs/spec/04-miner.md) and the
  [hypothesis template](hypotheses/HYPOTHESIS_TEMPLATE.md).
- **Validate** — run a validator, rerun miner submissions, score them.
  See [`docs/spec/05-validator.md`](docs/spec/05-validator.md).
- **Stake** — delegate TAO to validators whose scoring you trust.
- **Develop** — improve the spec, the SDK, the MCP server, starter
  agents, the runtime. See
  [`CONTRIBUTING.md`](CONTRIBUTING.md).

See [`VISION.md`](VISION.md#four-ways-to-contribute) for the longer
version.

## Finding your way around

| you want to… | go to |
|--------------|-------|
| understand the why | [`VISION.md`](VISION.md) |
| read the full spec | [`docs/spec/`](docs/spec/README.md) |
| draft a hypothesis | [`hypotheses/HYPOTHESIS_TEMPLATE.md`](hypotheses/HYPOTHESIS_TEMPLATE.md) |
| see an example hypothesis | [`hypotheses/H-0001-connectivity-first-training.md`](hypotheses/H-0001-connectivity-first-training.md) |
| contribute code or docs | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| report a security issue | [`SECURITY.md`](SECURITY.md) |
| understand who decides what | [`GOVERNANCE.md`](GOVERNANCE.md) |
| use this repo as an agent | [`AGENTS.md`](AGENTS.md) |

## Agent-first

This subnet's three active roles — **developing**, **mining**,
**validating** — are designed to be driven by autonomous agents.
Humans drop into the CLI as the escape hatch. The repo ships with a
full MCP server + typed Python SDK alongside the `hypo` CLI so agent
and human paths have equal capability. See
[`docs/spec/13-agent-integration.md`](docs/spec/13-agent-integration.md).

If you're an agent that just walked in: start at
[`AGENTS.md`](AGENTS.md).

## License

[AGPL-3.0-or-later](LICENSE). Source must accompany any distribution,
including derivatives operated as a network service.

## Code of Conduct

Participation is governed by the
[Contributor Covenant 2.1](CODE_OF_CONDUCT.md).

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# hypotheses

A permissionless scientific hypothesis market on Bittensor. Miners
preregister falsifiable claims about machine learning, run the
experiments themselves, and earn TAO when validators confirm their
results reproduce and improve on declared baselines.

**Read first:**
[`VISION.md`](VISION.md) (what we're building and why), then
[`docs/spec/00.5-foundations.md`](docs/spec/00.5-foundations.md)
(the *why* behind every design decision — threats the subnet must
survive, defences derived from them, assumptions those defences
require, and what the mechanism gives up).

## Stage

Phase 0 — *spec freeze*. The runtime under `src/hypotheses/` is not
yet implemented; only the JSON Schema contracts under
[`src/hypotheses/spec/schema/`](src/hypotheses/spec/schema/) ship
today. The spec, CI, and collaboration infrastructure land before
implementation begins. See
[`docs/spec/11-roadmap.md`](docs/spec/11-roadmap.md) for phase
boundaries and [`docs/tasks/phase-1.yml`](docs/tasks/phase-1.yml)
for the ordered task graph the Phase 1 implementing agent walks.

## Five ways to contribute

- **Mine** — propose a hypothesis, run it, submit. Entry tier runs on
  `cpu-small`; a laptop is enough to start. See
  [`docs/spec/04-miner.md`](docs/spec/04-miner.md) and the
  [hypothesis template](hypotheses/HYPOTHESIS_TEMPLATE.md).
- **Validate** — run a validator, rerun miner submissions, score them.
  See [`docs/spec/05-validator.md`](docs/spec/05-validator.md).
- **Stake** — delegate TAO to validators whose scoring you trust.
- **Develop** — improve the spec today; in Phase 1, build out the
  SDK, MCP server, starter agents, and runtime per
  [`docs/tasks/phase-1.yml`](docs/tasks/phase-1.yml). See
  [`CONTRIBUTING.md`](CONTRIBUTING.md).
- **Red-team** — find unmitigated coalition-level attacks against
  the spec; submit security-hypotheses through the
  [`SECURITY.md`](SECURITY.md) embargo and earn the standard
  scoring components when they settle. See
  [`docs/spec/22-security-bounty.md`](docs/spec/22-security-bounty.md)
  and the role prompt at
  [`agents/prompts/red-team-system.md`](agents/prompts/red-team-system.md).

See [`VISION.md`](VISION.md#five-ways-to-contribute) for the
longer version.

## Finding your way around

| you want to… | go to |
|--------------|-------|
| understand the why | [`VISION.md`](VISION.md) |
| understand the *foundations* (threats / defences / assumptions / what we give up) | [`docs/spec/00.5-foundations.md`](docs/spec/00.5-foundations.md) |
| read the full spec | [`docs/spec/`](docs/spec/README.md) |
| draft a hypothesis | [`hypotheses/HYPOTHESIS_TEMPLATE.md`](hypotheses/HYPOTHESIS_TEMPLATE.md) |
| see example hypotheses | [`hypotheses/`](hypotheses/) — H-0001 (connectivity-first fixture), H-0002 (oracle-backed), H-0003 (refutation pathway), H-0004/H-0005/H-0006 (depends_on family) |
| recognise antipatterns | [`docs/spec/antipatterns/`](docs/spec/antipatterns/) |
| trace a normative requirement | [`docs/spec/requirements.md`](docs/spec/requirements.md) (HM-REQ index) |
| trace a property invariant | [`docs/spec/invariants.md`](docs/spec/invariants.md) (HM-INV index) |
| read the formal lifecycle (Quint) | [`docs/spec/formal/`](docs/spec/formal/) |
| understand the adversarial-simulator contract | [`docs/spec/21-adversarial-simulator.md`](docs/spec/21-adversarial-simulator.md) |
| disclose a security finding (paid) | [`docs/spec/22-security-bounty.md`](docs/spec/22-security-bounty.md) + [`SECURITY.md`](SECURITY.md) |
| see what Phase 1 will build | [`docs/tasks/phase-1.yml`](docs/tasks/phase-1.yml) |
| contribute code or docs | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| report a security issue | [`SECURITY.md`](SECURITY.md) |
| understand who decides what | [`GOVERNANCE.md`](GOVERNANCE.md) |
| use this repo as an agent | [`AGENTS.md`](AGENTS.md) |

## Agent-first

This subnet's three active roles — **developing**, **mining**,
**validating** — are designed to be driven by autonomous agents.
Humans drop into the CLI as the escape hatch. The agent-surface
contract — MCP server + typed Python SDK + `hypo` CLI with full
parity across all three — is specified in
[`docs/spec/13-agent-integration.md`](docs/spec/13-agent-integration.md);
implementation lands in Phase 1 (tasks T-P1-016 / T-P1-017 /
T-P1-018 in [`docs/tasks/phase-1.yml`](docs/tasks/phase-1.yml)).

If you're an agent that just walked in: start at
[`AGENTS.md`](AGENTS.md).

## License

[AGPL-3.0-or-later](LICENSE). Source must accompany any distribution,
including derivatives operated as a network service.

## Code of Conduct

Participation is governed by the
[Contributor Covenant 2.1](CODE_OF_CONDUCT.md).

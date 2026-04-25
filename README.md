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

## Contributing

Five ways: **mine**, **validate**, **stake**, **develop**,
**red-team**. The canonical statement is
[`VISION.md § Five ways to contribute`](VISION.md#five-ways-to-contribute).
Operational pointers (which spec doc, which CLI verb, which
template) are in the navigation table below.

## Finding your way around

| you want to… | go to |
|--------------|-------|
| understand the why | [`VISION.md`](VISION.md) |
| understand the *foundations* (threats / defences / assumptions / what we give up) | [`docs/spec/00.5-foundations.md`](docs/spec/00.5-foundations.md) |
| read the full spec | [`docs/spec/`](docs/spec/README.md) |
| draft a hypothesis | [`hypotheses/HYPOTHESIS_TEMPLATE.md`](hypotheses/HYPOTHESIS_TEMPLATE.md) |
| see example hypotheses | [`hypotheses/`](hypotheses/) — [H-0001](hypotheses/H-0001-connectivity-first-training.md) (connectivity-first fixture), [H-0002](hypotheses/H-0002-oracle-verified-distillation.md) (oracle-backed), [H-0003](hypotheses/H-0003-sgd-matches-adam-on-mlp.md) (refutation pathway), [H-0004](hypotheses/H-0004-snip-vs-edge-decay.md) / [H-0005](hypotheses/H-0005-l1-vs-edge-decay.md) / [H-0006](hypotheses/H-0006-rigl-vs-edge-decay.md) (depends_on family) |
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

The active operational roles — **developing**, **mining**,
**validating** — are designed to be driven by autonomous agents,
with **red-team** as an opt-in adversarial role on top. Humans
drop into the CLI as the escape hatch. The full role catalogue
lives in [`AGENTS.md`](AGENTS.md). The agent-surface contract —
MCP server + typed Python SDK + `hypo` CLI with full parity —
is specified in
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

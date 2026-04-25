---
name: spec index
description: entry point for the full subnet specification
kind: reference
tokens: 200
load_for: [agent-operator, governance, implementation, proposal, review]
depends_on: []
---

# Subnet Specification

This directory is the source of truth for what the subnet does, how the code is
organised, and how miners and validators interact. The code in `src/` must
conform to these documents; when they disagree, the spec wins and the code gets
a PR.

Before the spec, read the vision: [`/VISION.md`](../../VISION.md). It
is the canonical statement of what the subnet is and why. Everything
here builds on that.

If you are an LLM agent, start at [`/AGENTS.md`](../../AGENTS.md) —
that's the entry point with links to the role-specific prompts under
[`/agents/prompts/`](../../agents/prompts/). For kicking off Phase 1
implementation, see
[`../implementation-handoff.md`](../implementation-handoff.md).

Read in order:

1. [00 — Overview](00-overview.md) — operational mechanics (vision is in /VISION.md)
2. [00.5 — Foundations](00.5-foundations.md) — adversarial-first
   threats / defences / assumptions / what we give up; the *why*
   behind every other doc
3. [01 — Glossary](01-glossary.md) — terms used throughout
4. [02 — Hypothesis format](02-hypothesis-format.md) — the preregistration schema
5. [03 — Architecture](03-architecture.md) — components, data flow, trust model
6. [04 — Miner](04-miner.md) — miner responsibilities and interfaces
7. [05 — Validator](05-validator.md) — validator pipeline
8. [06 — Scoring](06-scoring.md) — rubric, baselines, oracles
9. [07 — Incentive](07-incentive.md) — weight setting, anti-gaming
10. [08 — Experiment runtime](08-experiment-runtime.md) — sandbox, reproducibility
11. [09 — Protocol](09-protocol.md) — wire format, synapses, versioning
12. [10 — Repo layout](10-repo-layout.md) — target code structure
13. [11 — Roadmap](11-roadmap.md) — phased plan to ship
14. [12 — Implementation constraints](12-implementation-constraints.md) —
    rules for the autonomous implementing agent
15. [13 — Agent integration](13-agent-integration.md) — MCP server,
    typed SDK, and starter agents for LLM-driven miners
16. [14 — CLI](14-cli.md) — the unified `hypo` command, one entry
    point for humans and scripts
17. [15 — CI / CD and repo automations](15-ci-cd.md) — catalog of
    `.github/` workflows, configs, templates, scripts
18. [16 — Threat model](16-threat-model.md) — actors, assets,
    threats, and mitigations; the security audit trail
19. [17 — Hypothesis lifecycle](17-hypothesis-lifecycle.md) — states,
    transitions, authorities, edge cases
20. [18 — Oracle contract](18-oracle.md) — oracle interface,
    classes, composition, outage, SN42 adapter
21. [19 — Operations](19-operations.md) — observability, SLIs,
    alerts, runbooks, disaster recovery
22. [20 — Economic model](20-economic-model.md) — emission flow,
    parameter inventory, stake, Sybil cost, governance
23. [21 — Adversarial simulator](21-adversarial-simulator.md) —
    contract for the coalition-level attack simulator that catches
    every threat in 16 (Phase 2+ implementation; Phase 0 contract)
24. [22 — Security bounty](22-security-bounty.md) — white-hat
    program; vulnerability disclosures are first-class hypotheses
    on the registry; HM-REQ-0100 embargo gate; F1 and F6 are the
    canonical targets

Cross-cutting references:

- [`antipatterns/`](antipatterns/) — machine-readable corpus of "do
  NOT do this" shapes the implementing agent must recognise.
- [`formal/`](formal/) — Quint specifications mirroring prose state
  machines (lifecycle today; more will follow).
- [`requirements.md`](requirements.md) — stable `HM-REQ-NNNN`
  normative statements; inline in their owning doc, indexed here,
  cross-checked in CI.
- [`invariants.md`](invariants.md) — stable `HM-INV-NNNN`
  properties; Phase 1 property-based tests enforce each one.

Implementation model: this spec is written to be implemented by an
autonomous Claude agent without human interaction. [Document 12](
12-implementation-constraints.md) is addressed directly to that agent
and defines: toolchain pins, code style, testing strategy, logging
standards, fail-fast policy, build order, and per-module
definition-of-done.

Remaining TBDs in the spec are intentional deferrals — either
"implementer-chooses within these constraints" or "decision deferred to
a later phase with a named trigger." They are not blockers for Phase 0
or Phase 1.

Status: **draft, pre-implementation**.

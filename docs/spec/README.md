---
name: spec index
description: entry point for the full subnet specification
---

# Subnet Specification

This directory is the source of truth for what the subnet does, how the code is
organised, and how miners and validators interact. The code in `src/` must
conform to these documents; when they disagree, the spec wins and the code gets
a PR.

Read in order:

1. [00 — Overview](00-overview.md) — what the subnet is and why
2. [01 — Glossary](01-glossary.md) — terms used throughout
3. [02 — Hypothesis format](02-hypothesis-format.md) — the preregistration schema
4. [03 — Architecture](03-architecture.md) — components, data flow, trust model
5. [04 — Miner](04-miner.md) — miner responsibilities and interfaces
6. [05 — Validator](05-validator.md) — validator pipeline
7. [06 — Scoring](06-scoring.md) — rubric, baselines, oracles
8. [07 — Incentive](07-incentive.md) — weight setting, anti-gaming
9. [08 — Experiment runtime](08-experiment-runtime.md) — sandbox, reproducibility
10. [09 — Protocol](09-protocol.md) — wire format, synapses, versioning
11. [10 — Repo layout](10-repo-layout.md) — target code structure
12. [11 — Roadmap](11-roadmap.md) — phased plan to ship
13. [12 — Implementation constraints](12-implementation-constraints.md) —
    rules for the autonomous implementing agent
14. [13 — Agent integration](13-agent-integration.md) — MCP server,
    typed SDK, and starter agents for LLM-driven miners

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

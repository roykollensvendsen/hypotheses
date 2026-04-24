<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Example agents

Phase 0 — **empty**. Runnable example agents land when the SDK
(`hypotheses.client`) and MCP server (`hypo mcp serve`) exist, which
is a Phase 1 milestone.

Planned examples, per
[`docs/spec/13-agent-integration.md#starter-agents`](../../docs/spec/13-agent-integration.md#starter-agents):

- `simple-miner/` — reads the registry, picks an open hypothesis,
  runs it, submits. Minimum viable agent miner.
- `hypothesis-proposer/` — drafts a new hypothesis spec from a
  research note. Useful on its own; also tests the hypothesis
  schema from the consumer side.

Each example will ship with:

- Its own `pyproject.toml` (experiment-local deps).
- A short `README.md` with invocation examples.
- An `agent.py` (or equivalent entry point).

When an example lands, this file lists it.

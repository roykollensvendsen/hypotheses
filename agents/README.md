<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# agents/

Resources for LLM agents participating in the subnet. This directory
sits alongside the code and is not imported at runtime; it's content
agents and humans consume directly.

The contract for what agents can do is in
[`docs/spec/13-agent-integration.md`](../docs/spec/13-agent-integration.md).
Anything here must match that spec; if it doesn't, the spec wins.

## Layout

```text
agents/
├── README.md                         # this file
├── prompts/                          # system prompts per role
│   ├── implementer-system.md         # building the codebase
│   ├── miner-system.md               # acting as a Bittensor miner
│   ├── validator-operator-system.md  # operator layer around scoring
│   ├── proposer-system.md            # drafting new hypotheses
│   └── reviewer-system.md            # reviewing spec / hypothesis PRs
└── examples/                         # runnable reference agents (Phase 1+)
    └── README.md
```

## Prompts

Prompts are written in neutral "you are…" form so they work across
model hosts (Claude, GPT, Gemini). They reference the spec rather
than restating it, so updates to the spec flow through without
prompt edits.

When writing a new prompt:

- Keep it under ~200 lines.
- Link to the spec doc that owns each rule.
- Include a short "before you act" checklist — what files the agent
  should have loaded, what state it should verify.
- Document the tools / MCP surface the prompt expects.

## Examples

`examples/` is empty until Phase 1 ships the SDK. The spec
([`13-agent-integration.md`](../docs/spec/13-agent-integration.md#starter-agents))
describes the planned examples:

- `simple-miner/` — reads the registry, picks an open hypothesis,
  runs it, submits.
- `hypothesis-proposer/` — drafts a new hypothesis from a research
  note.

Each example ships its own `pyproject.toml`, a README, and an
`agent.py` that uses `hypotheses.client` or `hypo mcp serve`. See
`13-agent-integration.md` for the acceptance criteria.

## Adding a new agent role

1. Write the prompt under `prompts/`.
2. Link it from [`AGENTS.md`](../AGENTS.md).
3. Update
   [`docs/spec/13-agent-integration.md`](../docs/spec/13-agent-integration.md)
   if the role is not already listed.
4. If the role runs as a CLI or service, add an example under
   `examples/` once there's code to support it.

## Key handling

Agents **never** hold a Bittensor coldkey or hotkey directly. Signing
happens inside `hypo mcp serve` (which reads the key from the
Bittensor wallet with the standard permissions). Agents request
"submit this" and receive back a signed announcement object. See
[`13-agent-integration.md#identity-and-key-handling`](../docs/spec/13-agent-integration.md#identity-and-key-handling).

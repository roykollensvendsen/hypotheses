---
name: agent integration
description: mcp server, typed sdk, and starter agents for llm-driven miners
---

# 13 — Agent integration

The subnet is designed to be run by humans, by autonomous LLM agents, or
by anything in between. Agents are not a separate role in the incentive
model — they operate as miners. What this document specifies is the
integration surface that makes it easy to drop an agent in.

## Why this matters

- The founding frame of the subnet — generating and testing hypotheses
  about ML — is a natural agent task. Making agent participation easy
  is aligned with the subnet's purpose, not a side feature.
- Humans running experiments by hand will not keep up with the pace of
  hypothesis generation the subnet incentivises.
- Retrofitting a clean agent surface onto a CLI-first codebase is
  expensive; designing for it from day one is cheap.

## Integration layers

Three layers, from highest-level to lowest:

1. **MCP server** (`hypo mcp serve`) — exposes subnet operations as
   Model Context Protocol tools. Any MCP-capable agent host (Claude
   Code, Claude Desktop, Cursor, custom hosts using the MCP SDK)
   attaches and can act. Primary integration point for LLM agents.
2. **Python SDK** (`hypotheses.client`) — typed, importable surface
   that wraps the same operations. For agents built as Python
   services or frameworks (e.g. LangGraph, custom orchestrators).
3. **CLI** (`hypo`) — the single unified command per
   [14](14-cli.md). The MCP server and SDK are both built on top of
   the same `hypotheses.miner` and `hypotheses.validator` modules
   the CLI dispatches to; there is no divergence.

All three layers are thin wrappers over the same core. Changes to
behaviour are made in `src/hypotheses/miner/` or
`src/hypotheses/validator/`; the three surfaces then expose them.

## MCP server

### Invocation

```
hypo mcp serve [--hotkey NAME] [--allow-writes] [--transport stdio|http]
```

- `--hotkey NAME` binds the server to a named Bittensor wallet hotkey.
  Without this, only read-only tools are available.
- `--allow-writes` enables tools that broadcast on-chain or upload
  artifacts. Off by default.
- `--transport` selects stdio-MCP (default, for Claude Code-style
  hosts) or HTTP-MCP (for long-running hosts). Both transports expose
  the same tool set.

### Tool surface

Read-only tools (always available):

- `list_hypotheses(status?: string) -> list[HypothesisSummary]`
- `get_hypothesis(id: string) -> Hypothesis`
- `list_submissions(id?: string, hotkey?: string) -> list[SubmissionSummary]`
- `get_submission(announcement_cid: string) -> Submission`
- `get_score_history(hotkey?: string, epochs: int = 10) -> list[ScoreRecord]`
- `search_registry(query: string) -> list[HypothesisSummary]`

Write tools (require `--allow-writes` and a hotkey):

- `propose_hypothesis(spec: HypothesisSpec) -> ProposalResult`
  - Creates a local draft under `hypotheses/` and a matching
    `experiments/<id>/` scaffold, runs schema validation, opens a
    git branch. Does NOT push or PR.
- `run_hypothesis(id: string, seeds: list[int] | "all") -> RunHandle`
  - Invokes the runtime locally; returns a handle the agent can
    poll.
- `get_run_status(handle: RunHandle) -> RunStatus`
- `submit_run(handle: RunHandle) -> Announcement`
  - Signs and broadcasts. This is the only tool that touches the
    chain; it is gated by `--allow-writes` AND by the server's
    confirmation mode (see below).

### Write-gating

Write operations respect a confirmation mode:

| mode | behaviour |
|------|-----------|
| `auto` | tool returns immediately after broadcast |
| `dry-run` | tool computes and returns what would be submitted, without broadcasting |
| `confirm` | tool blocks until operator approves in the attached CLI or HTTP console (default) |

Default is `confirm`. An operator who trusts their agent can flip to
`auto`. Private keys never leave the MCP server process; agents
receive signed announcements as opaque objects.

### Example Claude Desktop / Claude Code config

```json
{
  "mcpServers": {
    "hypotheses": {
      "command": "hypo",
      "args": ["mcp", "serve", "--hotkey", "miner-a", "--allow-writes"]
    }
  }
}
```

## Python SDK

### Module

`from hypotheses.client import Client`

### Core types

All types are pydantic v2 models, mirroring the spec schemas exactly:

```python
class HypothesisSummary(BaseModel):
    id: str
    title: str
    status: Literal["proposed", "accepted", "running", "settled-supported",
                    "settled-refuted", "withdrawn"]
    version: int

class Hypothesis(HypothesisSummary):
    claim: str
    variables: list[Variable]
    metrics: list[Metric]
    baselines: list[Baseline]
    protocol: Protocol
    success_criteria: list[Criterion]
    falsification_criteria: list[Criterion]
    oracle: Oracle | None
    body_markdown: str

class Submission(BaseModel):
    announcement_cid: str
    hypothesis_id: str
    hypothesis_version: int
    miner_hotkey: str
    declared_summary: dict[str, MetricSummary]
    submitted_at: datetime

class ScoreRecord(BaseModel):
    epoch: int
    hypothesis_id: str
    miner_hotkey: str
    vector: ScoreVector   # rigor, reproduction, improvement, novelty, cost, composite
```

### Minimal agent loop

```python
from hypotheses.client import Client

client = Client.from_env()        # reads wallet path + endpoint from env

for hyp in client.list_hypotheses(status="accepted"):
    if client.has_submission(hyp.id, hotkey=client.hotkey):
        continue
    handle = client.run_hypothesis(hyp.id, seeds="all")
    result = client.wait_for_run(handle)
    client.submit_run(handle)
```

### Async variant

`hypotheses.client.aio.AsyncClient` provides the same surface as
`asyncio` coroutines for agents running inside event loops.

## Starter agents

The repo ships a small set of starter agents under `agents/`:

```
agents/
├── README.md                       # overview, model choices, safety notes
├── prompts/
│   ├── miner-system.md             # system prompt: "you are a subnet miner"
│   ├── reviewer-system.md          # system prompt: "you review hypothesis PRs"
│   └── proposer-system.md          # system prompt: "you draft new hypotheses"
├── examples/
│   ├── simple-miner/               # reads registry, picks one, runs, submits
│   │   ├── agent.py
│   │   ├── README.md
│   │   └── pyproject.toml
│   └── hypothesis-proposer/        # drafts a new hypothesis from a research note
│       ├── agent.py
│       ├── README.md
│       └── pyproject.toml
└── eval/                           # scoring the agents themselves
    └── bench_proposer.py
```

Requirements for an example agent to ship:

- Uses `hypotheses.client` (or MCP, via a reference host).
- Self-contained: own `pyproject.toml`, own README, runnable with
  `uv run`.
- Respects the write-gating policy — defaults to dry-run.
- Emits the same `events.jsonl` as a CLI miner, so monitoring
  infrastructure sees no difference.

Starter agents are not part of the incentive mechanism. They are
reference code. Anyone can run them, extend them, or replace them
with their own.

## Identity and key handling

- An agent NEVER holds a Bittensor coldkey or hotkey directly.
- Hotkey signing happens in the MCP server (or in the SDK when
  invoked by a human-configured service), which reads the key from
  the Bittensor wallet directory with the standard permissions.
- Agents request "submit this" and receive back a signed
  announcement object. They cannot forge or replay.
- For fully autonomous operation, the operator flips the MCP server
  to `auto` confirmation mode, which trusts the agent to the extent
  the operator chooses. This is a local operator decision, not a
  subnet-level one.

## Spec/code consistency

Adding or renaming an MCP tool OR an SDK public method is a spec
change to this document. The JSON schemas for tool arguments live
under `src/hypotheses/mcp/schema/` and CI checks that every tool
surfaced by the server is documented here and vice versa.

## Phase alignment

- Phase 1: SDK ships alongside the CLI. MCP server ships as a
  minimal read-only implementation (the read-only tool set above).
  Write operations are CLI-only during Phase 1.
- Phase 2: MCP write tools enabled. One or more starter agents
  running on testnet.
- Phase 3: starter agents are part of the onboarding documentation.

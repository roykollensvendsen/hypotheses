<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0006 — CLI-only path

## Narrative

The agent-integration contract in [13](../13-agent-integration.md)
requires agent / CLI parity: every capability exposed as a `hypo`
subcommand is also exposed as an MCP tool and as an SDK method, and
vice versa. Shipping a feature only on the CLI means the miner
agent, validator-operator agent, and proposer agent have to shell
out — defeating agent-first operation — and the SDK surface
implicitly forks.

## Bad code

```bad-code
# src/hypotheses/cli/validator.py — one-off CLI verb with no
# corresponding MCP tool or SDK method.
@app.command("rescore-batch")
def rescore_batch(since: datetime) -> None:
    """Rescore every submission whose manifest changed after `since`."""
    for cid in db.submissions_since(since):
        validator.pipeline.rescore(cid)
```

And then nothing in `src/hypotheses/mcp/tools.py` or
`src/hypotheses/client/sync.py` exposes the same capability.

## Why

- Validator-operator agents operating via MCP can't call it.
- SDK consumers have to subprocess `hypo rescore-batch`, which
  breaks typed error handling and logging attribution.
- Two parallel implementations of "how to rescore a batch" will
  inevitably drift.

## Correct pattern

Ship the three surfaces in the same PR:

```good-code
# 1) SDK method (hypotheses.client.sync)
class Client:
    def rescore_batch(self, since: datetime) -> RescoreReport:
        ...

# 2) MCP tool (hypotheses.mcp.tools) — thin wrapper over the SDK
@mcp.tool()
def rescore_batch(since: str) -> RescoreReport:
    return Client().rescore_batch(datetime.fromisoformat(since))

# 3) CLI verb (hypotheses.cli.validator) — also thin
@app.command("rescore-batch")
def rescore_batch(since: datetime) -> None:
    print(Client().rescore_batch(since).to_json())
```

A single `RescoreReport` type, a single code path, three surfaces.

## Spec reference

- [13 § role × surface matrix](../13-agent-integration.md)
- [14](../14-cli.md) — the CLI verbs, mirrored 1:1 with MCP tools.

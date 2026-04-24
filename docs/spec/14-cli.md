---
name: cli
description: the single hypo command — unified entry point for humans and scripts
---

# 14 — `hypo` — the one command

The CLI is the **escape hatch**. Agent-first is the default operating
mode (see [13](13-agent-integration.md)); `hypo` exists for humans
setting policy, responding to incidents, and running one-off tasks.
Every capability `hypo` offers is also reachable through MCP and the
SDK — the CLI never confers a privilege that agents lack.

`hypo` replaces what earlier drafts of the spec called `hypo-miner`,
`hypo-validator`, and `hypo-mcp`; those are internal modules behind
this one entry point.

Why one command (when humans do use it):

- Discoverable. `hypo --help` prints every operation; tab-completion
  reveals the full surface.
- Fewer things to remember. One binary covers every role.
- Role-free. A single node can act as miner, validator, and MCP host
  at once; there is no reason to split the CLI by role.

## Shape

Commands are `hypo <verb> [object] [args]`. Verbs are the primary axis;
nouns cluster under verbs where it helps.

```
hypo                                # welcome screen (tty) / help (non-tty)
hypo help [topic]                   # long-form help per topic
hypo version
hypo doctor                         # environment + dependency health checks
hypo init                           # first-time setup (wallet, config, profile)

# read — available to any user, no hotkey required
hypo ls [--status STATUS]           # list hypotheses
hypo show <id>                      # show a hypothesis
hypo search <query>
hypo submissions [--id ID] [--hotkey HK]
hypo scores [--hotkey HK] [--epochs N]

# miner — requires a hotkey
hypo propose <path>                 # validate and scaffold a new hypothesis
hypo run <id> [--seed N | --seeds all]
hypo submit <run-handle>

# validator — requires a hotkey, validator-registered
hypo validate serve                 # long-running validator loop
hypo validate rescore <ann-cid>
hypo validate audit <hotkey>

# mcp — agent integration
hypo mcp serve [--allow-writes] [--hotkey NAME] [--transport stdio|http]

# registration
hypo register miner
hypo register validator
```

## Help surface

- `hypo` with no arguments on a TTY prints a short welcome and lists
  the top-level verbs as a table with one-line descriptions. On a
  non-TTY (scripts, CI) it prints the same content as `hypo help`.
- `hypo help` prints the full command tree.
- `hypo help <topic>` prints long-form documentation for a topic.
  Topics include every verb and also conceptual entries (`hypothesis`,
  `scoring`, `oracle`, `mcp`).
- Every subcommand has `--help`.

## Conventions

- Global flags: `--wallet`, `--hotkey`, `--endpoint`, `--profile`,
  `--json`, `--verbose`, `--quiet`. These are accepted at any level.
- Output defaults to human-readable tables/text. `--json` switches
  every command to line-delimited or structured JSON so scripts and
  agents can consume it.
- Exit codes: `0` success, `1` user error (bad args, missing file),
  `2` validation failure (spec/schema/signature), `3` runtime failure
  (sandbox, network), `4` subnet-state failure (e.g. self-scoring
  attempt).
- No interactive prompts by default except in `init` and `doctor`.
  All other commands are script-safe.

## Configuration

- Config file: `~/.config/hypo/config.toml` (XDG-compliant).
- Profiles: named sections in the config; `hypo --profile NAME …`
  picks one. A profile binds wallet name, hotkey, endpoint, and
  default hardware profile.
- Environment variables: every config key has a `HYPO_*` env
  equivalent that overrides the file.

## Package wiring

```toml
[project.scripts]
hypo = "hypotheses.cli:main"
```

Internally the CLI dispatches to:

- `hypotheses.miner` for `propose`, `run`, `submit`, `register miner`
- `hypotheses.validator` for `validate *`, `register validator`
- `hypotheses.mcp.server` for `mcp *`
- `hypotheses.client` for `ls`, `show`, `search`, `submissions`,
  `scores`
- `hypotheses.cli.doctor` and `hypotheses.cli.init` for operator
  tooling

No business logic lives in `src/hypotheses/cli/`; it remains a thin
dispatcher.

## Interactive TUI (optional, Phase 3+)

`hypo tui` may ship later — a Textual-based menu that exposes the same
commands with live status panes. Not in scope for Phase 0–2.

## Deprecation note

Earlier spec drafts referenced `hypo-miner`, `hypo-validator`, and
`hypo-mcp` as three separate entry points. Those names are gone. If
you see them in historical text, read `hypo …`. No shim scripts; the
three names never shipped.

## Self-audit

This doc is done when:

- Every CLI verb maps to a module under `src/hypotheses/cli/` per
  [10](10-repo-layout.md).
- Every verb has a matching MCP tool and SDK method in
  [13](13-agent-integration.md) — agent / CLI parity.
- Global flags, exit codes, and JSON-mode semantics are specified
  without "should" hedging.
- Role-specific verbs (validator, miner, mcp) match their
  respective role docs ([04](04-miner.md), [05](05-validator.md),
  [13](13-agent-integration.md)).

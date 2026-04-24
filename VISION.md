<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Vision

A permissionless scientific hypothesis market on Bittensor. Anyone with
a good hypothesis and modest compute can mine; anyone can contribute
by staking, developing, mining, or validating. Agent-first by design,
with a human CLI as the escape hatch.

This file is the canonical statement of what we're building and why.
Any other document that talks about *why the subnet exists* links
back here; it does not restate the vision.

## What we're building

This subnet turns scientific hypothesis generation into a
permissionless, incentivized activity. The bar to mine is a good
hypothesis and modest compute — no affiliation, no GPU required for
the entry-level profile, no invitation. Miners preregister falsifiable
claims about machine learning, run the experiments themselves, and
publish signed artifacts. Validators reproduce a sample of every run
and score on rigor, reproducibility, improvement over declared
baselines, and novelty. TAO flows to hypotheses that are honest,
reproducible, and either settle a question or produce a clean null.

The mission is bottom-up: make high-quality ML research cheaper to do
and harder to fake, without privileging any particular institution or
framework.

## Four pillars

### 1. Research frame — topology evolution

The seed hypothesis — from which the subnet gets its name — is that
learning is a **topology-evolution** problem rather than a pure
parameter-optimisation problem. Construction and destruction of
connectivity are a coupled dynamical system. Classical methods can be
reframed as special cases:

- gradient descent = edge-strength adjustment
- dropout = stochastic edge removal
- attention = dynamic flow routing
- pruning = destructive edge selection
- lottery tickets = initial-topology hypothesis

If this frame is productive, the subnet should surface *rules* — small
local dynamical rules over connectivity graphs — whose emergent
behaviour produces better specialisation, faster adaptation, or
cheaper training than the status quo. The infrastructure itself must
not privilege that framing; it must only make any falsifiable ML
hypothesis cheap to state, run, and score.

### 2. Mechanism — preregistered falsifiable hypotheses

Spec before results. Reproducibility before novelty. Validators
spot-check every submission. Composite scoring: rigor + reproduction
+ improvement + novelty − cost. Honest nulls score; paper mills
don't. No leaderboard games, no closed methods, no post-hoc threshold
tuning.

### 3. Ethos — bottom-up, AGPL, permissionless

Code under AGPL-3.0-or-later. Bottom-up participation: no whitelist,
no KYC, no gatekeeping beyond the minimum governance needed to
prevent attacks. Enforcement through copyleft, cryptographic
signatures, and validator consensus — not through institutional
control.

### 4. Operating mode — agent-first, CLI as escape hatch

All three active roles — **developing**, **mining**, and
**validating** — are designed to be driven by autonomous agents as
the default mode. Humans drop into direct CLI interaction as the
*escape hatch*, not the primary path.

- **Mining** — an LLM agent (via MCP or SDK) reads the registry,
  picks an open hypothesis, runs it, submits. The operator's job is
  policy (which hypotheses, which budget, write-gating mode) and
  intervening on failures.
- **Validating** — an agent orchestrates the validator loop:
  monitors announcements, triages failed reruns, explains scores,
  flags anomalies. **Scoring itself stays deterministic** — pure
  functions over artifacts. The agent is the *operator layer*, not
  the judgment layer.
- **Developing** — the codebase is built, extended, and maintained
  by agents reading the spec. The spec is written for that audience.
  Humans review, redirect, and resolve ambiguity.

The CLI (`hypo`), the SDK (`hypotheses.client`), and the MCP server
(`hypo mcp serve`) expose the same surface. MCP + SDK are the
agent-facing defaults; the CLI is the escape hatch humans use for
policy changes, incident response, and one-off tasks. The agent path
must never be less capable than the CLI path.

## Four ways to contribute

1. **Mine** — propose a hypothesis, run it, submit. Entry tier runs
   on `cpu-small`; a laptop is enough to start. The `hypo` command
   and the hypothesis template carry a new miner from zero to first
   submission without requiring the full spec.
2. **Validate** — run a validator, rerun miner submissions, score
   them. This is where subnet integrity lives; validators are the
   reproducibility layer.
3. **Stake** — delegate TAO to validators whose scoring you trust.
   Earn yield; amplify honest validation.
4. **Develop** — improve the spec, the SDK, the MCP server, starter
   agents, the runtime. Contribute new hypothesis templates, new stat
   tests, new dataset adapters, new oracle adapters.

## Accessibility promises

These are the vision-derived guarantees the spec and code must
deliver. They are non-negotiable:

- **Zero gatekeeping.** No whitelist, no approval step, no KYC. A
  Bittensor hotkey is the only credential needed to mine or validate.
- **CPU-only viable.** At least one hardware profile (`cpu-small`) is
  usable for real submissions.
- **Time-to-first-submission under 1 hour** on commodity hardware,
  from a fresh checkout, for a new miner with a working hypothesis.
- **Agent parity.** Every capability reachable via the CLI is also
  reachable via MCP and the SDK; the human escape hatch confers no
  privilege the agent path lacks.
- **Self-contained template.** A new miner should be able to draft a
  valid hypothesis using only the hypothesis-format spec and the
  template, without reading the full spec tree.

## What this subnet is NOT

- **Not a model marketplace.** Miners are paid for producing
  defensible knowledge about training, not for inference.
- **Not a leaderboard.** Scoring rewards preregistered, reproducible,
  relational claims — not absolute accuracy rankings.
- **Not a paper mill.** Hypotheses must be falsifiable and
  machine-checkable.
- **Not a gated research club.** Anyone. Anywhere. At any hour.

## Pointers

- Spec tree: [`docs/spec/`](docs/spec/README.md)
- Mechanics overview: [`docs/spec/00-overview.md`](docs/spec/00-overview.md)
- Hypothesis format: [`docs/spec/02-hypothesis-format.md`](docs/spec/02-hypothesis-format.md)
- Hypothesis template: [`hypotheses/HYPOTHESIS_TEMPLATE.md`](hypotheses/HYPOTHESIS_TEMPLATE.md)
- Canonical fixture (H-0001): [`hypotheses/H-0001-connectivity-first-training.md`](hypotheses/H-0001-connectivity-first-training.md)
- Originating Discord conversation: [`docs/initial-discord-conversation.md`](docs/initial-discord-conversation.md)

---
name: overview
description: what the subnet is, why it exists, and the vision it's built around
---

# 00 — Overview

## One-line

A permissionless scientific hypothesis market on Bittensor. Anyone with
a good hypothesis and modest compute can mine; anyone can contribute by
staking, developing, mining, or validating. Agent-first by design, with
a human CLI as the escape hatch.

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
behaviour produces better specialisation, faster adaptation, or cheaper
training than the status quo. The infrastructure itself must not
privilege that framing; it must only make any falsifiable ML hypothesis
cheap to state, run, and score.

### 2. Mechanism — preregistered falsifiable hypotheses

Spec before results. Reproducibility before novelty. Validators
spot-check every submission. Composite scoring (rigor + reproduction +
improvement + novelty − cost). Honest nulls score; paper mills don't.
No leaderboard games, no closed methods, no post-hoc threshold tuning.

### 3. Ethos — bottom-up, AGPL, permissionless

Code under AGPL-3.0-or-later. Bottom-up participation: no whitelist, no
KYC, no gatekeeping beyond the minimum governance needed to prevent
attacks. Enforcement through copyleft, cryptographic signatures, and
validator consensus — not through institutional control.

### 4. Operating mode — agent-first, CLI as escape hatch

All three active roles — **developing**, **mining**, and **validating**
— are designed to be driven by autonomous agents as the default mode.
Humans drop into direct CLI interaction as the *escape hatch*, not the
primary path.

- **Mining** — an LLM agent (via MCP or SDK) reads the registry, picks
  an open hypothesis, runs it, submits. The operator's job is policy
  (which hypotheses, which budget, write-gating mode) and intervening
  on failures.
- **Validating** — an agent orchestrates the validator loop: monitors
  announcements, triages failed reruns, explains scores, flags
  anomalies. **Scoring itself stays deterministic** — pure functions
  over artifacts. The agent is the *operator layer*, not the judgment
  layer.
- **Developing** — the codebase is built, extended, and maintained by
  agents reading this spec. The spec is written for that audience.
  Humans review, redirect, and resolve ambiguity.

The CLI (`hypo`), the SDK (`hypotheses.client`), and the MCP server
(`hypo mcp serve`) expose the same surface. MCP + SDK are the
agent-facing defaults; the CLI is the escape hatch humans use for
policy changes, incident response, and one-off tasks. The agent path
must never be less capable than the CLI path.

## Four ways to contribute

1. **Mine** — propose a hypothesis, run it, submit. Entry tier runs on
   `cpu-small`; a laptop is enough to start. The `hypo` command and
   the hypothesis template carry a new miner from zero to first
   submission without requiring the full spec.
2. **Validate** — run a validator, rerun miner submissions, score
   them. This is where subnet integrity lives; validators are the
   reproducibility layer.
3. **Stake** — delegate TAO to validators whose scoring you trust.
   Earn yield; amplify honest validation.
4. **Develop** — improve the spec, the SDK, the MCP server, starter
   agents, the runtime. Contribute new hypothesis templates, new stat
   tests, new dataset adapters, new oracle adapters. AGPL-3.0.

## What the subnet does

1. A miner writes a hypothesis spec (preregistration-style; see
   [02](02-hypothesis-format.md)) and commits it to the repo.
2. The miner runs the experiment (typically via an agent through MCP
   or SDK) and publishes artifacts (metrics, logs, weights,
   environment lock, code commit hash).
3. Validators verify the spec is well-formed, re-run a sampled
   fraction of seeds to check reproducibility, compare against the
   declared baselines, and — where applicable — query a ground-truth
   oracle (e.g. SN42) to check that the hypothesis resolves a
   known-answer question correctly.
4. Validators score along several axes (rigor, reproduction,
   improvement, novelty, cost efficiency) via deterministic pure
   functions and set weights accordingly.
5. Emission flows to miners whose hypotheses produce verifiable,
   reproducible improvements — and penalises miners whose reruns
   disagree with their submitted numbers.

## What the subnet is not

- **Not a model marketplace.** Miners are not paid for inference; they
  are paid for producing defensible knowledge about training.
- **Not a leaderboard.** Scoring is not "highest accuracy wins"; it is
  "hypothesis was preregistered, is reproducible, and its claim is
  supported against declared baselines."
- **Not a paper mill.** Hypotheses must be falsifiable and
  machine-checkable. Narrative essays without a runnable protocol do
  not score.
- **Not a gated research club.** No whitelist, no KYC, no invitation.

## Non-negotiables

Substantive (about the knowledge produced):

- **Preregistration.** Spec is committed and hashed before results.
- **Open code.** Experiment code is in this repo under
  `experiments/<id>/` before results are submitted.
- **Determinism.** Seeds pinned, environment locked. Stochastic
  elements are declared and averaged over a declared seed set.
- **Honest null.** A falsification that is preregistered and executed
  cleanly scores non-zero — negative results are valuable.
- **Deterministic scoring.** Scoring functions are pure and agent-free;
  only the operator layer around scoring is agent-driven.

Accessibility (about who can participate):

- **Zero gatekeeping.** No whitelist, no approval step, no KYC. A
  hotkey is the only credential to mine or validate.
- **CPU-only viable.** At least one hardware profile (`cpu-small`) is
  usable for real submissions.
- **Time-to-first-submission < 1 hour** on commodity hardware, from a
  fresh checkout, for a new miner with a working hypothesis.
- **Agent parity.** Every capability reachable via the CLI is also
  reachable via MCP and the SDK; the human escape hatch confers no
  privilege the agent path lacks.
- **Self-contained template.** A new miner should be able to draft a
  valid hypothesis using only
  [02](02-hypothesis-format.md) and the template, without reading the
  full spec.

## Relationship to SN42

The user's original framing was: "test the hypotheses on SN42 where the
answer is known, and get TAO for posing the right questions." SN42
serves as a **ground-truth oracle** for the subset of hypotheses whose
claims can be expressed as questions with a known answer on a
known-answer subnet. Not all hypotheses have an SN42-shaped oracle;
for the rest, scoring falls back to reproducibility + baseline
comparison. See [06](06-scoring.md).

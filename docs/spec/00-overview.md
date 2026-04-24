---
name: overview
description: what the subnet is, why it exists, and the research frame it sits in
---

# 00 — Overview

## One-line

A Bittensor subnet that treats scientific hypotheses about machine learning as
first-class, tradeable artifacts: miners propose and run hypotheses, validators
reproduce and score them, and emission flows to the hypotheses that measurably
improve training or models.

## The research frame

The seed hypothesis — from which the subnet gets its name — is that learning is
a **topology-evolution** problem rather than a pure parameter-optimisation
problem. Construction and destruction of connectivity are a coupled dynamical
system. Classical methods can be reframed as special cases:

- gradient descent = edge-strength adjustment
- dropout = stochastic edge removal
- attention = dynamic flow routing
- pruning = destructive edge selection
- lottery tickets = initial-topology hypothesis

If this frame is productive, the subnet should surface *rules* — small local
dynamical rules over connectivity graphs — whose emergent behaviour produces
better specialisation, faster adaptation, or cheaper training than the status
quo. The subnet infrastructure must not privilege that framing; it must only
make any falsifiable ML hypothesis cheap to state, run, and score.

## What the subnet does

1. A miner writes a hypothesis spec (preregistration-style; see
   [02](02-hypothesis-format.md)) and commits it to the repo.
2. The miner runs the experiment and publishes artifacts (metrics, logs,
   weights, environment lock, code commit hash).
3. Validators verify the spec is well-formed, re-run a sampled fraction of
   seeds to check reproducibility, compare against the declared baselines, and
   — where applicable — query a ground-truth oracle (e.g. SN42) to check that
   the hypothesis resolves a known-answer question correctly.
4. Validators score along several axes (rigor, reproducibility, improvement,
   novelty, cost efficiency) and set weights accordingly.
5. Emission flows to miners whose hypotheses produce verifiable, reproducible
   improvements — and penalises miners whose reruns disagree with their
   submitted numbers.

## What the subnet is not

- **Not a model marketplace.** Miners are not paid for inference; they are
  paid for producing defensible knowledge about training.
- **Not a leaderboard.** Scoring is not "highest accuracy wins"; it is
  "hypothesis was preregistered, is reproducible, and its claim is supported
  against declared baselines."
- **Not a paper mill.** Hypotheses must be falsifiable and machine-checkable.
  Narrative essays without a runnable protocol do not score.

## Non-negotiables

- **Preregistration.** Spec is committed and hashed before results.
- **Open code.** Experiment code is in this repo under `experiments/<id>/`
  before results are submitted.
- **Determinism.** Seeds pinned, environment locked. Stochastic elements must
  be declared and averaged over a declared seed set.
- **Honest null.** A falsification that is preregistered and executed cleanly
  scores non-zero — negative results are valuable.

## Relationship to SN42

The user's original framing was: "test the hypotheses on SN42 where the answer
is known, and get TAO for posing the right questions." SN42 serves as a
**ground-truth oracle** for the subset of hypotheses whose claims can be
expressed as questions with a known answer on a known-answer subnet. Not all
hypotheses have an SN42-shaped oracle; for the rest, scoring falls back to
reproducibility + baseline comparison. See [06](06-scoring.md).

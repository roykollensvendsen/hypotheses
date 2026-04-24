---
name: overview
description: mechanics overview — what the subnet does operationally and what it is not
tokens: 500
load_for: [implementation, agent-operator, proposal, governance, review]
depends_on: []
---

# 00 — Overview

**Vision: see [`/VISION.md`](../../VISION.md).** That file is the
canonical statement of why this subnet exists, what we're building,
and who we're building it for. This document covers the operational
mechanics only.

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

## Substantive non-negotiables

The vision-derived accessibility promises live in
[`/VISION.md`](../../VISION.md). The rules below are about the
*knowledge the subnet produces*:

- **Preregistration.** Spec is committed and hashed before results.
- **Open code.** Experiment code is in this repo under
  `experiments/<id>/` before results are submitted.
- **Determinism.** Seeds pinned, environment locked. Stochastic
  elements are declared and averaged over a declared seed set.
- **Honest null.** A falsification that is preregistered and executed
  cleanly scores non-zero — negative results are valuable.
- **Deterministic scoring.** Scoring functions are pure and
  agent-free; only the operator layer around scoring is
  agent-driven. See [05](05-validator.md).

## Relationship to SN42

The user's original framing was: "test the hypotheses on SN42 where
the answer is known, and get TAO for posing the right questions."
SN42 serves as a **ground-truth oracle** for the subset of hypotheses
whose claims can be expressed as questions with a known answer on a
known-answer subnet. Not all hypotheses have an SN42-shaped oracle;
for the rest, scoring falls back to reproducibility + baseline
comparison. See [06](06-scoring.md).

## Self-audit

This doc is done when:

- The flow under "What the subnet does" matches the pipeline in
  [05](05-validator.md).
- Every substantive non-negotiable is enforced by a CI gate,
  runtime rule, or scoring function — no aspirational claims.
- The accessibility promises in `VISION.md` are covered here or
  linked, never contradicted.
- No vision content is restated; `VISION.md` is the single source.

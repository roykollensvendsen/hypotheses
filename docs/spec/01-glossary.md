---
name: glossary
description: definitions of terms used across the specification
tokens: 500
load_for: [implementation, agent-operator, proposal, review]
depends_on: []
---

# 01 — Glossary

**Hypothesis**
  A preregistered, falsifiable claim about an ML training or model behaviour,
  plus the protocol to test it. See [02](02-hypothesis-format.md).

**Spec**
  The machine-readable front matter of a hypothesis (YAML).

**Body**
  The free-form markdown discussion attached to a hypothesis.

**Experiment**
  A concrete execution of a hypothesis's protocol. One hypothesis has many
  experiments (one per seed, per submitter, per rerun).

**Artifact**
  Any file produced by an experiment: metrics log, weights, stdout, env lock,
  rng state. Content-addressed.

**Spec CID**
  Content identifier (hash) of a hypothesis spec at a given version. Changes
  when any field in the front matter changes.

**Artifact CID**
  Content identifier of an artifact bundle.

**Miner**
  A Bittensor neuron that proposes hypotheses and/or submits experimental
  results against them.

**Validator**
  A Bittensor neuron that verifies submissions, reruns a sample, scores, and
  sets weights.

**Oracle**
  A trusted source of ground truth for a claim. Canonical example: SN42
  (known-answer subnet). A hypothesis without an oracle is scored on
  reproducibility + baseline comparison only.

**Baseline**
  A named reference run, declared in the spec, against which the candidate
  method is compared. Every hypothesis must declare at least one baseline.

**Preregistration**
  Committing a hypothesis spec to the repo *before* results are submitted, so
  success/falsification criteria are frozen and cannot be tuned post-hoc.

**Rerun tolerance**
  Numerical bounds within which a validator's rerun of a miner-declared seed
  must fall for the submission to count as reproduced.

**Rigor score / reproducibility score / improvement score / novelty score /
cost score**
  The five scalar components of the composite hypothesis score; see
  [06](06-scoring.md).

**Topology evolution**
  The research frame motivating this subnet: training as a coupled
  construction/destruction dynamical system over a connectivity graph.

**Connectivity dynamics**
  Rules — usually local — governing how edges are added, removed, or reweighted
  during training.

## Self-audit

This doc is done when:

- Every capitalised term used elsewhere in the spec has an entry
  here (or is an industry-standard term that doesn't need one).
- Every entry here is used at least once in another spec doc.
- No entry defines a term in terms of another undefined term.
- Entries are sorted logically (not strictly alphabetical —
  related terms cluster).

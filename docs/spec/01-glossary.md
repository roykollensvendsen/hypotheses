---
name: glossary
description: definitions of terms used across the specification
tokens: 700
load_for: [implementation, agent-operator, proposal, review]
depends_on: []
kind: reference
---

# 01 — Glossary

Each term is a heading; the heading slug is the term's anchor
(e.g. [`#hypothesis`](#hypothesis), [`#spec-cid`](#spec-cid)).
Other spec docs link first-use back to the canonical definition;
[`scripts/check_glossary_links.py`](../../scripts/check_glossary_links.py)
ratchets that discipline.

## Terms

### Hypothesis

A preregistered, falsifiable claim about an ML training or model
behaviour, plus the protocol to test it. See
[02](02-hypothesis-format.md). Also called a **formal hypothesis**
when distinguished from an [informal hypothesis](#informal-hypothesis).

### Informal hypothesis

A cheap-to-post seed question without a runnable protocol or
falsification criteria, registered under `informal/` with an
immutable `I-NNNN` ID. Posting requires a TAO bond
(`ideator_min_stake`, default 0.1 TAO per
[20 § parameter inventory](20-economic-model.md#parameter-inventory)).
Formal hypotheses cite informal ones via
[Inspired-by](#inspired-by); on settlement, a 5 pp slice of the
sponsor pool flows to cited [Ideators](#ideator). See
[02b](02b-informal-hypothesis-format.md) and ADR 0024.

### Ideator

The proposer of an [informal hypothesis](#informal-hypothesis),
identified by `proposer.hotkey`. Ideators earn a share of the
sponsor pool of any formal hypothesis whose
[Inspired-by](#inspired-by) cites their I-NNNN, paid under the
same two-tier 70 / 30 schedule as miners.

### Inspired-by

An optional, weighted field on a formal hypothesis declaring which
informal hypotheses inspired it. Locked at acceptance (T-ACC); ≤ 3
entries; weights sum to 1.0. See
[02 § inspired_by](02-hypothesis-format.md#inspired_by).

### Spec

The machine-readable front matter of a hypothesis (YAML).

### Body

The free-form markdown discussion attached to a hypothesis.

### Experiment

A concrete execution of a hypothesis's protocol. One hypothesis
has many experiments (one per seed, per submitter, per rerun).

### Artifact

Any file produced by an experiment: metrics log, weights, stdout,
env lock, rng state. Content-addressed.

### Spec CID

Content identifier (hash) of a hypothesis spec at a given version.
Changes when any field in the front matter changes.

### Artifact CID

Content identifier of an artifact bundle.

### Miner

A Bittensor neuron that proposes hypotheses and/or submits
experimental results against them.

### Validator

A Bittensor neuron that verifies submissions, reruns a sample,
scores, and sets weights.

### Oracle

A trusted source of ground truth for a claim. Canonical example:
SN42 (known-answer subnet). A hypothesis without an oracle is
scored on reproducibility + baseline comparison only.

### Baseline

A named reference run, declared in the spec, against which the
candidate method is compared. Every hypothesis must declare at
least one baseline.

### Preregistration

Committing a hypothesis spec to the repo *before* results are
submitted, so success/falsification criteria are frozen and cannot
be tuned post-hoc.

### Rerun tolerance

Numerical bounds within which a validator's rerun of a
miner-declared seed must fall for the submission to count as
reproduced.

### Rigor score

The component measuring whether the hypothesis is well-formed
(declared analysis plan, statistical test, sample size). One of
the five scalar components of the composite score; see
[06](06-scoring.md).

### Reproducibility score

The fraction of validator reruns that fell within
[rerun tolerance](#rerun-tolerance). One of the five scalar
components of the composite score; see [06](06-scoring.md).

### Improvement score

The component measuring observed improvement over the declared
[baseline](#baseline). One of the five scalar components of the
composite score; see [06](06-scoring.md).

### Novelty score

The component rewarding the first miner to settle a hypothesis at
a given version. One of the five scalar components of the
composite score; see [06](06-scoring.md).

### Cost score

The negative component penalising compute and storage spend. One
of the five scalar components of the composite score; see
[06](06-scoring.md).

### Topology evolution

The research frame motivating this subnet: training as a coupled
construction/destruction dynamical system over a connectivity
graph.

### Connectivity dynamics

Rules — usually local — governing how edges are added, removed,
or reweighted during training.

## Self-audit

This doc is done when:

- Every capitalised term used elsewhere in the spec has an entry
  here (or is an industry-standard term that doesn't need one).
- Every entry here is used at least once in another spec doc.
- No entry defines a term in terms of another undefined term.
- Entries are sorted logically (not strictly alphabetical —
  related terms cluster).

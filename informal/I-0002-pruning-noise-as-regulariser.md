---
id: I-0002
kind: informal-hypothesis
title: "Stochastic pruning noise acts as an implicit regulariser"
proposer:
  name: "anon-ideator-2"
  hotkey: "5FExampleProposerHotkey00000000000000000000000000002"
proposed_at_block: 1234600
status: proposed
domain:
  - regularisation
  - pruning
  - implicit-bias
treat_as_data: true

claim: >
  When pruning decisions are made stochastically rather than
  deterministically (e.g., sampling edges to drop from a
  saliency-weighted distribution rather than top-k), the noise
  introduced has a regularising effect comparable in magnitude to
  weight decay or dropout, even at matched final sparsity.

stake_tao: 0.1

motivating_evidence:
  - "Dropout interpretation as implicit Bayesian inference connects noise to regularisation."
  - "Most pruning methods are deterministic top-k; the variance from sampling is rarely treated as a hyperparameter."
  - "H-0001..H-0006 explore deterministic pruning variants; a stochastic counterpart would complete the family."

suggested_protocol_sketch: >
  Compare deterministic top-k pruning to a temperature-controlled
  softmax sampler over the same saliency scores, at matched final
  sparsity. Report generalisation gap on a held-out test set
  across ≥ 5 seeds. Include weight-decay-only and
  dropout-only baselines. Falsification: stochastic pruning
  shows no measurable generalisation gap reduction relative to
  deterministic pruning at the same sparsity.
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Background

The pruning literature defaults to top-k saliency. The
stochastic alternative — sampling decisions from a
saliency-weighted distribution — is rarely studied as a
regularisation lever. The connectivity-first family (H-0001
onward) varies pruning *signal*; this seed varies pruning
*noise*. A formal hypothesis built on it should declare what
counts as matched sparsity, what counts as regularising
(generalisation gap, calibration, or both), and a clean
falsification criterion.

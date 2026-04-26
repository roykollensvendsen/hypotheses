---
id: I-0001
kind: informal-hypothesis
title: "Loss-landscape curvature correlates with curriculum difficulty"
proposer:
  name: "anon-ideator-1"
  hotkey: "5FExampleProposerHotkey00000000000000000000000000001"
proposed_at_block: 1234567
status: proposed
domain:
  - optimisation
  - curriculum-learning
treat_as_data: true

claim: >
  Loss-landscape curvature (largest eigenvalue of the Hessian, or a
  cheaper proxy) tracks curriculum difficulty during training: harder
  curricula sit on sharper minima at convergence, easier ones on
  flatter. The relationship may be monotonic and may generalise
  across architectures.

stake_tao: 0.1

motivating_evidence:
  - "Sharpness-aware-minimisation literature implicates curvature in generalisation."
  - "Curriculum-learning literature characterises difficulty operationally but rarely measures landscape geometry."
  - "Connectivity-first training (H-0001) varies an adjacent geometric quantity; the same toolchain could measure both."

suggested_protocol_sketch: >
  Train identical small models on curricula of declared difficulty
  rank. Estimate top eigenvalue at convergence via Hessian-vector
  products. Plot rank-vs-curvature for ≥ 3 seeds per curriculum.
  A formal hypothesis would need to declare what counts as
  "harder", what counts as "sharper", and a falsification
  criterion (e.g., rank correlation < 0.3 over the curricula
  tested).
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Background

Curriculum learning is usually framed in terms of optimisation
trajectory, not landscape geometry. The sharpness-vs-flatness
debate is a separate long-running thread in generalisation theory.
The two have not been systematically combined.

A clean formal hypothesis would test whether a single landscape
statistic (e.g. top Hessian eigenvalue) acts as a difficulty
meter when curriculum order is unknown. The
`suggested_protocol_sketch` is one operationalisation; a formal
author may pick a different cut.

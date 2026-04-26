---
name: ADR index
description: index and template for architecture decision records under docs/adr/
kind: reference
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Architecture Decision Records

This directory captures non-obvious decisions that future readers
would otherwise have to reverse-engineer from code or guess at.

## When to write one

Write an ADR when:

- You pin a new tool or dep (enforced by
  [`adr-required.yml`](../../.github/workflows/adr-required.yml)).
- You make a choice that contradicts common practice.
- You resolve a TBD from the spec.
- You pick one of several plausible architectures and want the
  reasoning preserved.

Skip an ADR for:

- Trivial bug fixes.
- Restating what's already in the spec.
- Style preferences without functional impact.

## File format

Use [MADR](https://adr.github.io/madr/) 3 lite. One decision per
file. Filename: `NNNN-kebab-case-title.md` where `NNNN` is a
four-digit sequence number (allocate in PR order — first merged gets
the next free number).

YAML front-matter (validated by
[`scripts/check_frontmatter.py`](../../scripts/check_frontmatter.py))
carries the structured fields:

- `name`, `description` — short identifier and one-line summary.
- `kind: decision`.
- `status` — `proposed` | `accepted` | `superseded` | `deprecated`.
- `date` — `YYYY-MM-DD`.
- `deciders` — list of GitHub handles.

Body sections:

- **Context** — what problem or situation prompts the decision.
- **Decision** — the chosen option in one paragraph.
- **Consequences** — positive, negative, and neutral. Be honest
  about the downsides.

Optional body sections:

- **Options considered** — if picking between alternatives mattered.
- **Related ADRs / spec sections** — links.

Keep each ADR under ~1 page. ADRs are a paper trail, not an essay.

## Template

```markdown
---
name: NNNN title-in-lower-kebab
description: one-line summary of the decision
kind: decision
status: proposed
date: YYYY-MM-DD
deciders: ["@handle"]
---

<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: YYYY The hypotheses subnet contributors
-->

# NNNN — Title

## Context

What situation or problem is this addressing?

## Decision

What did we decide?

## Consequences

- **Positive:**
- **Negative:**
- **Neutral / deferred:**

## Related

- Spec section(s): …
- ADRs: …
```

## Existing ADRs

- [0001 — Phase zero foundation](0001-phase-zero-foundation.md)
- [0002 — Test toolchain](0002-test-toolchain.md)
- [0003 — System-test markers](0003-system-test-markers.md)
- [0004 — Design heuristics](0004-design-heuristics.md)
- [0005 — Rigor framework](0005-rigor-framework.md)
- [0006 — Rigor pass: foundations](0006-rigor-pass-foundations.md)
- [0007 — Foundations gap fix](0007-foundations-gap-fix.md)
- [0008 — Rigor pass: scoring](0008-rigor-pass-scoring.md)
- [0009 — External review plan](0009-external-review-plan.md)
- [0010 — Economic strategy](0010-economic-strategy.md)
- [0011 — D2.2 coverage bound](0011-d22-coverage-bound.md)
- [0012 — C7 measurement](0012-c7-measurement.md)
- [0013 — Cold-start contingency](0013-cold-start-contingency.md)
- [0014 — Treasury pre-DAO](0014-treasury-pre-dao.md)
- [0015 — Economic survival scope](0015-economic-survival-scope.md)
- [0016 — Viability decision protocol](0016-viability-decision-protocol.md)
- [0017 — Validator unit economics](0017-validator-unit-economics.md)
- [0018 — Participation equilibrium](0018-participation-equilibrium.md)
- [0019 — Viability verdict (not viable as designed)](0019-viability-verdict-not-viable-as-designed.md)
- [0020 — Sponsor-gated heavy profiles](0020-sponsor-gated-heavy-profiles.md)

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

Required sections:

- **Status** — `proposed`, `accepted`, `rejected`, `superseded by
  NNNN`, or `deprecated`.
- **Context** — what problem or situation prompts the decision.
- **Decision** — the chosen option in one paragraph.
- **Consequences** — positive, negative, and neutral. Be honest
  about the downsides.

Optional:

- **Options considered** — if picking between alternatives mattered.
- **Related ADRs / spec sections** — links.

Keep each ADR under ~1 page. ADRs are a paper trail, not an essay.

## Template

```markdown
---
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: YYYY The hypotheses subnet contributors
---

# NNNN — Title

- **Status:** proposed | accepted | rejected | superseded by NNNN | deprecated
- **Date:** YYYY-MM-DD
- **Deciders:** @handle(s)

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

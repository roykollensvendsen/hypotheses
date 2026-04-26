---
name: references
description: central bibliography of external sources cited by the spec; stable IDs for in-doc citation
tokens: 700
load_for: [governance, review]
depends_on: []
kind: reference
evidence: well-supported
---

# References

Central bibliography. Every external source cited anywhere in
the [spec](README.md), ADRs, or
[hypothesis](02-hypothesis-format.md) files lives here under a
stable ID; in-doc citations use the brace form `{ref:slug}` or
the footnote form `[^slug]` per
[`25-rigor-framework.md`](25-rigor-framework.md). Sources span
[validator](05-validator.md) collusion patterns,
[preregistration](01-glossary.md#preregistration) methodology,
ML reproducibility, and protocol standards (RFC, IETF).

IDs are append-only: once assigned, never recycled (mirrors
`HM-REQ-NNNN`). If a source is withdrawn or superseded, mark
the row but do not delete it — historical references must stay
resolvable.

## Index

| ID | Citation | First cited in |
|----|----------|----------------|
| `[ref:bittensor-stake-2025]` | Anonymous, *Stake concentration and validator collusion in Bittensor subnets*, arXiv:2507.02951, 2025 | [00.5](00.5-foundations.md) |
| `[ref:llm-judge-2025]` | Anonymous, *On the limits of LLM-as-judge for adversarial inputs*, arXiv:2506.13639, 2025 | [00.5](00.5-foundations.md) |
| `[ref:phacking-jpe-2024]` | Brodeur, Cook, & Heyes, *p-Hacking and false discovery in the social sciences*, Journal of Political Economy, 2024 (DOI: 10.1086/730455) | [00.5](00.5-foundations.md), [02](02-hypothesis-format.md) |
| `[ref:replication-osc-2015]` | Open Science Collaboration, *Estimating the reproducibility of psychological science*, Science 349, 2015 (DOI: 10.1126/science.aac4716) | [00.5](00.5-foundations.md) |
| `[ref:behavior-research-2024]` | Anonymous, *Preregistration and analysis-plan rigor*, Behavior Research Methods, 2024 (Springer) | [00.5](00.5-foundations.md) |
| `[ref:rfc-8785]` | Rundgren, Jordan, & Erdtman, *JSON Canonicalization Scheme (JCS)*, RFC 8785, IETF, June 2020 | [09](09-protocol.md), [00.5](00.5-foundations.md) |
| `[ref:inference-labs-weight-copy-2025]` | Inference Labs, *Mitigating weight-copy attacks on Bittensor subnets*, blog post, 2025 (archived) | [00.5](00.5-foundations.md) |
| `[ref:polymarket-uma-ukraine-2025]` | Knight, *Polymarket says governance attack by UMA whale to hijack a bet's resolution is 'unprecedented'*, The Block, 2025-03-26 | [00.5](00.5-foundations.md) |
| `[ref:polymarket-paris-weather-2026]` | Le Monde / Euronews, *Hair dryer trick behind ~€25,000 win? France probes potential weather data scam linked to Polymarket*, 2026-04-23 | [00.5](00.5-foundations.md) |
| `[ref:ousterhout-posd-2021]` | John Ousterhout, *A Philosophy of Software Design*, 2nd edition, Yaknyam Press, 2021 (ISBN 978-1732102217) | [adr/0004](../adr/0004-design-heuristics.md), [24](24-design-heuristics.md) |
| `[ref:mast-taxonomy-2025]` | Anonymous, *MAST: a taxonomy of failure modes in agentic AI systems* (primary source link in the entry text); used in this repo as shorthand for the agent-failure-mode catalogue | [adr/0004](../adr/0004-design-heuristics.md) |
| `[ref:stackoverflow-shared-coding-2026]` | Stack Overflow Blog, *Building shared coding guidelines for AI (and people too)*, 2026-03-26 (archived) | [adr/0004](../adr/0004-design-heuristics.md) |
| `[ref:anthropic-claude-code-2026]` | Anthropic, *Claude Code best practices*, code.claude.com/docs, accessed 2026 | [adr/0004](../adr/0004-design-heuristics.md) |

## How to add a new source

1. Pick a stable slug: `author-year-shortlabel` in lowercase
   kebab-case. Examples: `munafo-2017`, `roughgarden-mech-2010`.
   The slug must be unique across the whole index.
2. Append a row to the table above. Keep the citation field
   resolvable on its own (author, title, venue, year, identifier
   like DOI or arXiv).
3. Cite from the spec doc using `{ref:slug}` (brace form) or
   `[^slug]` (footnote form). Use whichever flows in prose; the
   CI gate accepts both.
4. If the source is withdrawn or superseded later, mark the row
   `withdrawn: see {ref:replacement-slug}` rather than deleting.

## What does NOT belong here

- **Cross-references to other spec docs** — those use the
  existing `[NN-doc](NN-doc.md)` form, not `{ref:...}`.
- **Internal repo files** (CONTRIBUTING.md, AGENTS.md,
  GOVERNANCE.md) — link directly.
- **Hypotheses** under `hypotheses/H-*.md` — they have their
  own preregistration-spec citation flow per
  [`02-hypothesis-format.md`](02-hypothesis-format.md).

## Citation format conventions

Format the rightmost field of each row to make the source
re-findable without clicking:

- **Papers:** `Author, Title, Venue, Year (DOI: ...)`
- **arXiv:** `Author, Title, arXiv:NNNN.NNNNN, Year`
- **RFCs / standards:** `Author(s), Title, RFC NNNN, Body, Date`
- **Books:** `Author, Title, Edition, Publisher, Year (ISBN ...)`
- **Blog posts / reports:** `Org, Title, venue/url, Date (archived)`

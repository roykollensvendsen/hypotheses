---
name: rigor framework
description: citation, assumption, and evidence-taxonomy conventions for the spec; how to ground a normative claim
tokens: 2500
load_for: [implementation, review, governance]
depends_on: ["00.5"]
kind: contract
evidence: reasoned-design
---

# 25 — Rigor framework

This doc operationalises the pattern already used in
[`00.5-foundations.md`](00.5-foundations.md) — sections C
("Assumptions") and E ("Empirical posture") — as a project-wide
standard. Every normative [spec](README.md) doc follows it; the CI gate
enforces internal consistency; the central bibliography in
[`references.md`](references.md) holds every external source.

The goal is **rigour with honesty**: claims that are backed by
research are cited; claims that are not are flagged as
assumptions with their consequence if false; design choices that
are neither (most of the spec) state their rationale. A reader —
human or agent — can tell which is which without guessing.

## Why this matters

Agents amplify what is specified. The spec drives implementation.
An unproven assumption silently encoded in a normative `HM-REQ`
becomes silently encoded in code; later reversal requires
unwinding both. Marking now costs one line per claim. Discovering
later that a load-bearing claim was unsupported requires
unwinding both spec and code, especially once a
[validator](05-validator.md), [miner](04-miner.md), or
[oracle](18-oracle.md) has been built on it.

## The four-level evidence taxonomy

Every normative spec doc declares a doc-level `evidence:` value
in its front matter (see schema). The same taxonomy applies to
individual claims within a doc.

- **`well-supported`** — the claim is backed by a peer-reviewed
  paper, a published standard (RFC / IETF / W3C / ISO), or a
  named industry source archived in `references.md`. Cite via
  `{ref:slug}`.
- **`reasoned-design`** — the claim is a design choice with a
  stated rationale. The rationale need not be cited but must be
  legible: "we choose X because Y" with Y resolvable from the
  surrounding spec. Most internal-mechanism claims (signing
  format, schema shape, commit conventions) are this level.
- **`assumption`** — the claim is empirical but unproven. It
  MUST be flagged with the standard admonition (see below) and
  MUST cross-link to a row in
  [`00.5 § C`](00.5-foundations.md#c-assumptions-the-defences-require)
  with an explicit "if false" consequence.
- **`tbd`** — deferred until a named trigger. Not a placeholder
  for "we forgot to think about it"; the trigger condition
  (phase, decision, external event) is named in the doc
  [body](01-glossary.md#body).

Doc-level `evidence:` is the ceiling — a doc whose normative
claims are all `reasoned-design` declares that level even if a
sentence somewhere happens to cite a paper. A `well-supported`
doc contains *only* well-supported normative content; one
`assumption` claim drops the whole doc to `assumption`.

## Citation conventions

Every external source goes in [`references.md`](references.md)
under a stable ID `[ref:author-year-slug]`. IDs are append-only:
once assigned, never recycled (mirrors the HM-REQ rule).

### Inline citation

Two forms, pick whichever flows better in prose:

- **Brace form**, for compact citation:
  `the {ref:munafo-2017} replication crisis informs C2`.
- **Footnote form**, for citation-heavy paragraphs:
  `see also[^munafo-2017]`, with `[^munafo-2017]:` on a separate
  line resolving to the entry.

The CI gate verifies every `{ref:slug}` and `[^slug]` resolves to
a row in `references.md`.

### Allowed source types

- Peer-reviewed papers (DOI required)
- arXiv preprints (full identifier `arXiv:NNNN.NNNNN`; version
  pin recommended)
- Standards (RFC, IETF, W3C, ISO; version dated)
- Named books (ISBN, edition, year)
- Named blog posts / industry reports (dated, archived URL,
  named author or organisation)

### NOT allowed

- Bare URLs without authorial / venue context
- "Common knowledge" without a source — if it is genuinely
  common knowledge, the claim is `reasoned-design`, not
  `well-supported`
- Citations to other spec docs (those are spec cross-references;
  use the existing `[NN-doc]` link form)

## Assumption-marker conventions

When a normative claim rests on an unproven empirical
assumption, mark it inline with this admonition:

```markdown
> **assumption: name** — claim. **If false:** consequence.
> See [00.5 § c7-ground-truth-latency](00.5-foundations.md#c7-ground-truth-latency).
```

`name` is a short kebab-case identifier matching an H3 subsection
in [`00.5 § C`](00.5-foundations.md#c-assumptions-the-defences-require)
(e.g., `c7-ground-truth-latency`, `c1-compute-cost`). Each C-row
is its own H3 subsection so the per-row anchor resolves cleanly.
The CI gate verifies every assumption admonition resolves to a
`00.5 § C` row.

If the assumption does not yet appear in `00.5 § C`, the rigor
pass that introduces it MUST add the row there in the same PR.
`00.5 § C` is the canonical home; other docs reference, never
restate (HM-REQ-0110).

## When each level is required

| claim shape | minimum level |
|-------------|---------------|
| Empirical claim about external systems (real miner behaviour, validator collusion patterns, ML reproducibility, dataset stability) | `well-supported` if research exists; `assumption` otherwise |
| Empirical claim about cryptographic / protocol primitives (ed25519 unforgeability, RFC-8785 canonicality, SHA-256 collision-resistance) | `well-supported` (cite the standard) |
| Internal-mechanism design (file layout, schema shape, commit order, CLI surface) | `reasoned-design` |
| Threat-model assertion (an attacker would do X because Y) | `well-supported` if precedent exists; `assumption` otherwise — a threat model that asserts attacker preferences without evidence is a guess, and that's fine to admit |
| Future-phase commitment (Phase 2 will ship X) | `tbd` with named trigger |

A normative `HM-REQ` whose claim shape is empirical-external
MUST resolve to either a citation or a `00.5 § C` assumption
row. The CI gate enforces this for new HM-REQs once coverage
ratchets to 100 %.

## How to add a new normative claim

Checklist for adding (or revising) a normative spec claim:

1. **Identify the level** using the table above.
2. If `well-supported`: add the source to
   [`references.md`](references.md) (or confirm it's already
   there) and use the `{ref:slug}` inline form.
3. If `assumption`: add the admonition block, name the
   assumption in kebab-case, add a row in
   [`00.5 § C`](00.5-foundations.md#c-assumptions-the-defences-require)
   with the "if false" consequence in the same PR.
4. If `reasoned-design`: state the rationale inline. No
   citation required, but the surrounding spec must make the
   "because Y" clause resolvable.
5. If `tbd`: name the trigger condition explicitly.
6. Update the doc's front-matter `evidence:` to the lowest
   level any of its normative claims declares.
7. Run `make docs-check` locally; the grounding gate (when it
   ships) will catch broken `{ref:...}` and orphaned assumption
   blocks.

## What this doc is NOT

- **Not a research mandate.** The spec does not require
  conducting novel research; it requires honesty about what is
  research-backed and what is not.
- **Not a citation requirement for every sentence.** Only
  normative claims (block-quoted `**HM-REQ-NNNN**` or table-row
  rules) need explicit grounding. Narrative prose, examples,
  and motivating context do not.
- **Not a substitute for the threat model.** Threats live in
  [`16-threat-model.md`](16-threat-model.md); foundations in
  [`00.5-foundations.md`](00.5-foundations.md). This doc only
  governs how those docs and their dependents *cite and flag*.
- **Not a replacement for review.** A claim can be marked
  `well-supported` with a real citation and still be a bad
  claim if the citation doesn't actually support it. Reviewers
  spot-check that cited claims match the citation's actual
  text.

## Cross-references

- [`00.5 § C — Assumptions the defences require`](00.5-foundations.md#c-assumptions-the-defences-require)
  — the canonical home for unproven claims.
- [`00.5 § E — Empirical posture`](00.5-foundations.md#e-empirical-posture--whats-proven-vs-whats-a-bet)
  — the original distinction between proven and bet-on
  content; this doc generalises that distinction across the
  whole spec.
- [`references.md`](references.md) — the central bibliography.
- [`requirements.md`](requirements.md) — every HM-REQ-NNNN; the
  gate (when it ships) verifies surface-observable HM-REQs
  resolve to either `well-supported` evidence or a `00.5 § C`
  assumption row.
- [`12-implementation-constraints.md § Documentation
  discipline`](12-implementation-constraints.md#documentation-discipline)
  — HM-REQ-0110 single-source rule applies: `references.md` is
  the canonical home for citations; other docs link, never
  restate.
- [`docs/adr/0005-rigor-framework.md`](../adr/0005-rigor-framework.md)
  — the rationale for this framework and the alternatives
  considered.

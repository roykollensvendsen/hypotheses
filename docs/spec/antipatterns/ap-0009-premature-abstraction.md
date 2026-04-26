<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0009 — Premature abstraction

## Narrative

A `Provider` interface, an `AbstractFactory`, or a plugin registry
introduced before there are concrete callers to share it. The cost
of an abstraction is paid by every reader who has to chase the
indirection; the benefit is paid only when a second and third
caller appear. Until they do, the abstraction is pure overhead —
and worse, it locks in a shape that the eventual real callers will
not fit, forcing a rework on top of the original speculation.

## Bad code

```bad-code
class HypothesisProvider(Protocol):
    def get(self, hyp_id: str) -> Hypothesis: ...
    def list(self) -> list[HypothesisSummary]: ...

class FilesystemHypothesisProvider:
    """The only implementation; IPFSProvider planned for Phase 2."""
    def get(self, hyp_id: str) -> Hypothesis:
        return Hypothesis.from_markdown((ROOT / f"{hyp_id}.md").read_text())
    def list(self) -> list[HypothesisSummary]:
        return [_summary(p) for p in ROOT.glob("*.md")]

class HypothesisProviderFactory:
    @staticmethod
    def default() -> HypothesisProvider:
        return FilesystemHypothesisProvider()
```

## Why

- One implementation does not need a `Protocol`. The "Phase 2
  IPFS" caller does not exist yet; designing for it now encodes a
  guess about what its shape will be. When IPFS lands, the real
  surface (async, retries, CID resolution) will not match this
  one, and the protocol becomes a refactor cost.
- Three layers of indirection — protocol, class, factory — for
  what is fundamentally `read a file from disk`. Readers chase
  the indirection; agents loading the file see noise where
  signal belongs.
- This violates [`AGENTS.md § Non-negotiable rules § Scope
  discipline`](../../../AGENTS.md#non-negotiable-rules): no
  speculative features, no "we might want X later" hooks.

## Correct pattern

```good-code
def load_hypothesis(hyp_id: str) -> Hypothesis:
    return Hypothesis.from_markdown((ROOT / f"{hyp_id}.md").read_text())
```

When IPFS arrives, write the IPFS function next to this one. If
the two share enough structure on the third caller, *that* is when
a small adapter shows up — and it will fit, because it follows
real callers rather than imagined ones.

## Spec reference

- [AGENTS.md § Non-negotiable rules](../../../AGENTS.md#non-negotiable-rules)
- [24 § D-4](../24-design-heuristics.md) — don't abstract until you
  have three concrete callers.
- [12 § dependencies policy](../12-implementation-constraints.md#dependencies-policy)
  — minimal runtime deps; speculative abstractions usually drag
  speculative deps with them.

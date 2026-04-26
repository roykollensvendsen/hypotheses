---
name: design heuristics
description: positive structural rules for human and agent contributors; module shape, types, validation, abstraction, naming, testing, PR shape
tokens: 3000
load_for: [implementation, review]
depends_on: ["03", "12"]
kind: contract
---

# 24 — Design heuristics

This doc complements [`12-implementation-constraints.md`](12-implementation-constraints.md).
That one locks the mechanics — toolchain, TDD order, `fail-fast`,
mutation, SPDX, coverage. This one codifies the structural choices
the mechanics leave open: when to extract, how deep to go, what to
validate, when not to abstract, how to shape a PR.

The audience is both human and agent. Tacit conventions don't
transfer to agents; only documented ones do. Agents amplify what is
specified — strong rules multiply, weak ones collapse faster. The
goal is not a 50-rule manifesto (those age into dogma) but six tight
rules with concrete Bad/Good pairs, citable in PR review by name.

For the named LLM-failure-mode shapes referenced below
(`ap-0008` … `ap-0013`), see
[`antipatterns/`](antipatterns/).

## D-1. Deep modules over shallow ones

Modules earn their cost when they hide complexity behind a narrow
interface. A class that wraps stdlib one method per call is a
shallow module; it adds an indirection without removing any work.

> *Bad — shallow:*
>
> ```python
> class JsonStore:
>     def __init__(self, path: Path) -> None:
>         self.path = path
>
>     def read(self) -> dict[str, Any]:
>         return json.loads(self.path.read_text())
>
>     def write(self, data: dict[str, Any]) -> None:
>         self.path.write_text(json.dumps(data))
> ```

> *Good — deep:*
>
> ```python
> def sign(payload: bytes, hotkey: Hotkey) -> bytes:
>     """Canonical-JSON + ed25519, single call."""
>     ...
> ```
>
> The interface is one function; the implementation hides the
> RFC-8785 canonicalization, the `from cryptography import` setup,
> the error-mapping to `SignatureInvalid`. Callers don't see any of
> that.

Cite this rule when a PR adds a class that exists only to forward
calls, or splits one file into three for symmetry rather than to
hide work.

References: Ousterhout, *A Philosophy of Software Design* (deep
modules); HM-REQ-0110 (one canonical home).

## D-2. Make illegal states unrepresentable

Use the type system to rule out errors that runtime checks would
otherwise catch. Pyright is strict in this repo; lean on it.

> *Bad — runtime check:*
>
> ```python
> def serve(transport: str) -> None:
>     if transport not in ("stdio", "http"):
>         raise ValueError(f"bad transport: {transport}")
>     ...
> ```

> *Good — types:*
>
> ```python
> Transport = Literal["stdio", "http"]
>
> def serve(transport: Transport) -> None:
>     ...
> ```
>
> Now the error is caught at every call site at type-check time,
> and the runtime check is dead code that can be deleted.

Same shape applies to enums (don't use `str` for a closed set),
optional fields (don't use sentinels when `None` works), and
mutually exclusive arguments (don't use bools when a literal pair
makes the relationship explicit). See `ap-0012` for the boolean
flag failure mode.

References: [`12 § code style`](12-implementation-constraints.md#code-style),
[`12 § fail-fast`](12-implementation-constraints.md#fail-fast-policy).

## D-3. Validate at boundaries; trust internal callers

Validation belongs at the *edge* of the system: the CLI parser,
the MCP receive handler, the JSON-Schema load. Once data has
crossed a typed boundary, internal functions trust their types and
do not re-check them. Re-validating everywhere costs lines without
catching anything new and obscures where the real authority lies.

> *Bad — defensive everywhere:*
>
> ```python
> def score(submission: Submission) -> ScoreVector:
>     assert isinstance(submission, Submission)
>     assert submission.miner_hotkey is not None
>     if not submission.artifact_cid:
>         raise ValueError("...")
>     ...
> ```

> *Good — validate once, trust onwards:*
>
> ```python
> # at the boundary (e.g., synapse handler)
> submission = Submission.model_validate(payload)
>
> # internal scoring trusts the type
> def score(submission: Submission) -> ScoreVector:
>     ...
> ```
>
> If `submission` is malformed it never reaches `score()`; the
> typed exception comes out of `model_validate` with full context,
> and the boundary is the only place that knows about the wire
> format.

The errors.py taxonomy ([`12 § fail-fast`](12-implementation-constraints.md#fail-fast-policy))
exists precisely so the boundary can raise the right typed
exception once. See `ap-0008` for the defensive-overhandling
failure mode.

## D-4. Don't abstract until you have three concrete callers

The cost of an abstraction is paid by every reader who has to
chase the indirection; the benefit is paid only by the callers
that share it. Until there are three real callers, the cost
exceeds the benefit. Write the concrete code; on the third
duplication the right abstraction reveals itself, and it is rarely
the one you would have guessed at the second.

> *Bad — speculative:*
>
> ```python
> class HypothesisProvider(Protocol):
>     def get(self, id: str) -> Hypothesis: ...
>
> class FilesystemHypothesisProvider(HypothesisProvider):
>     ...  # the only implementation
>
> class HypothesisProviderFactory:
>     ...  # constructs the only kind there is
> ```

> *Good — the concrete thing, until pressure builds:*
>
> ```python
> def load_hypothesis(id: str) -> Hypothesis:
>     path = HYPOTHESES_DIR / f"{id}.md"
>     return Hypothesis.from_markdown(path.read_text())
> ```
>
> When a second backend (e.g., IPFS) lands in Phase 2, *that's*
> when a narrow, obvious adapter shows up — not before.

See `ap-0009` for the premature-abstraction failure mode and
[`AGENTS.md § Non-negotiable rules § Scope discipline`](../../AGENTS.md#non-negotiable-rules)
for the broader rule.

## D-5. Optimize for the reader (human and agent)

Code is read more times than it is written. The reader is
sometimes a human reviewer, sometimes an agent loading the file
into context. Both want the same things: identifiers that compound
naturally, control flow that stays flat, and functions whose size
is an *outcome* of what they do, not a target.

- **Names compound** — `verify_signature`, not `vfy_sig` and not
  `signature_verification_helper_function`. Prefer subject + verb
  for actions, noun for data.
- **Flat over nested** — early returns and guard clauses beat
  five-deep `if`/`else` ladders. Aim for two levels of nesting in
  most functions.
- **Extraction reduces complexity, or it doesn't happen** —
  splitting a 30-line function into ten three-line functions makes
  the reader chase ten files for what one paragraph already said.
  Extract when extraction *hides* a self-contained sub-problem
  (D-1), not because "more functions = better."
- **Comments explain WHY, never WHAT** — see `ap-0010`.

References: [`12 § code style`](12-implementation-constraints.md#code-style),
[`12 § documentation discipline`](12-implementation-constraints.md#documentation-discipline).

## D-6. Tests assert behaviour at the surface; properties assert invariants

The test pyramid in this repo is layered for a reason. Each layer
asserts a different kind of thing; mixing them makes tests brittle
and signal weak.

- **Unit tests** assert the contract of one function with mocked
  I/O only (per [`12 § testing strategy`](12-implementation-constraints.md#testing-strategy)).
- **Property tests** under `tests/properties/` assert HM-INV
  invariants over generated inputs.
- **Integration tests** exercise real adapters end-to-end.
- **System tests** (`tests/system/`) drive the running subnet
  through its public surfaces only — see
  [`23 — System tests`](23-system-tests.md).

> *Bad — internal-coupling test:*
>
> ```python
> def test_score_calls_oracle(monkeypatch):
>     calls = []
>     monkeypatch.setattr("hypotheses.scoring.query_oracle",
>                         lambda *a: calls.append(a))
>     score(submission)
>     assert len(calls) == 1
> ```
>
> This test passes when the function is renamed, fails when an
> internal refactor stops calling `query_oracle` directly even
> though behaviour is identical. It asserts implementation, not
> contract.

> *Good — surface assertion:*
>
> ```python
> def test_oracle_disagreement_zeros_improvement():
>     submission = build_submission(oracle_verdict="disagree")
>     vector = score(submission)
>     assert vector.improvement == 0.0
> ```
>
> Tests the observable rule from the [spec](README.md); survives any internal
> refactor that preserves the contract.

## What about PR shape?

The 500-LoC cap on PR size is the *outcome* of the rules, not the
design constraint. A PR is well-shaped when:

- It addresses **one concern**. "Refactor X *and* fix Y *and*
  rename Z" is three PRs.
- The first commit is `test:` and is red on its own (HM-REQ-0040);
  the next is `feat:`/`fix:` and turns it green.
- The PR description names the **why** — what problem this solves,
  what alternatives were considered briefly, and how to verify
  end-to-end. A reviewer (human or agent) can load
  the description and the diff and have full context.
- It cites the heuristics or antipatterns it relies on, by ID,
  when relevant. "This follows D-1 — the new module hides X" is a
  one-line review answer.

Most of the rest follows: tight PRs are easier to review *because*
they have one concern, not because the LoC cap is a virtue.

## What this doc is NOT

- Not a style guide for formatting — that's ruff plus the
  conventions in [`12 § code style`](12-implementation-constraints.md#code-style).
- Not a complete catalogue of bad shapes — those live in
  [`antipatterns/`](antipatterns/) and are referenced by ID
  (`ap-NNNN`).
- Not exhaustive — when a real PR raises a structural question
  these rules don't answer, the right move is an ADR under
  [`docs/adr/`](../adr/), not extending this doc with another
  rule.

## References

- [`03 — Architecture`](03-architecture.md) — module taxonomy
  D-1 and D-3 build on.
- [`12 — Implementation constraints`](12-implementation-constraints.md)
  — mechanics this doc complements without duplicating.
- [`23 — System tests`](23-system-tests.md) — the surface-level
  test contract D-6 references.
- [`antipatterns/`](antipatterns/) — `ap-0001` … `ap-0013`,
  named negative shapes citable by ID.
- [`AGENTS.md § Non-negotiable rules`](../../AGENTS.md) —
  scope discipline and TDD rules these heuristics build on.
- [`docs/adr/0004-design-heuristics.md`](../adr/0004-design-heuristics.md)
  — the rationale for this doc and the alternatives considered.

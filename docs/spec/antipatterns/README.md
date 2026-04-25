<!-- antipattern-content -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Antipatterns

Machine-readable "do **NOT** do this" patterns. The implementing
agent is expected to recognise each one and refuse to produce the
bad shape — even if asked nicely, even if it looks shorter, even if
a test incidentally passes.

Every file in this directory opens with the comment

```markdown
<!-- antipattern-content -->
```

so [`scripts/check_prompt_injection.py`](../../../scripts/check_prompt_injection.py)
allow-lists it: antipattern bodies may contain directive-like text
that would otherwise trip the scanner (that's exactly the point —
these files name the failure mode so the agent can avoid it).

## File shape

Each `ap-NNNN-<slug>.md` contains:

1. **Narrative** — one paragraph framing the failure.
2. **Bad code** — fenced `bad-code` block showing the shape to avoid.
3. **Why** — what breaks or regresses if it lands.
4. **Correct pattern** — the positive alternative.
5. **Spec reference** — the normative statement the antipattern violates.

## Index

| id | antipattern | spec reference |
|----|-------------|----------------|
| [`ap-0001`](ap-0001-oracle-fallback.md) | Falling back to scoring-without-oracle when one is declared | [06 § Oracles](../06-scoring.md#oracles), [18](../18-oracle.md) |
| [`ap-0002`](ap-0002-llm-in-scoring.md) | LLM output anywhere in the scoring pipeline | [05 § two layers](../05-validator.md#two-layers-deterministic-core-and-operator-layer), [12 § fail-fast](../12-implementation-constraints.md#fail-fast-policy) |
| [`ap-0003`](ap-0003-bare-except.md) | Bare `except:` or generic `Exception` catches | [12 § fail-fast](../12-implementation-constraints.md#fail-fast-policy) |
| [`ap-0004`](ap-0004-skip-tdd.md) | Re-ordering `test:` and `feat:` commits to satisfy the gate | [12 § test-driven development](../12-implementation-constraints.md#test-driven-development-mandatory) |
| [`ap-0005`](ap-0005-synthesize-spec-field.md) | Inventing a field not in the JSON Schema | [02 § schema validation](../02-hypothesis-format.md#schema-validation) |
| [`ap-0006`](ap-0006-cli-only-path.md) | CLI capability without matching MCP tool and SDK method | [13 § parity rule](../13-agent-integration.md) |
| [`ap-0007`](ap-0007-floating-action-ref.md) | GitHub Action referenced by tag instead of 40-char SHA | [15 § pinning policy](../15-ci-cd.md#pinning-policy) |

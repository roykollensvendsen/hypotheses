<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0010 — Comments that restate the code

## Narrative

A line comment that paraphrases the next line, or a docstring that
expands the function name into a sentence, adds nothing the reader
could not infer from the code itself — and ages worse than the
code, because comments are not type-checked, run, or covered by
tests. Restatement comments are the canonical LLM-slop tell: they
look thorough but carry no information.

[`12 § code style`](../12-implementation-constraints.md#code-style)
is explicit: "no comments unless WHY is non-obvious; never restate
code behavior."

## Bad code

```bad-code
def verify_signature(announcement: Announcement) -> None:
    """Verify the signature on an announcement.

    This function takes an announcement and verifies its signature.

    Args:
        announcement: The announcement whose signature to verify.

    Raises:
        SignatureInvalid: If the signature is invalid.
    """
    # Get the canonical JSON of the announcement body
    canonical = canonical_json(announcement.body)
    # Verify the signature using ed25519
    ed25519.verify(announcement.signature, canonical, announcement.miner_hotkey)
```

## Why

- The docstring's first three lines paraphrase the function name;
  the `Args` and `Raises` sections paraphrase the type signature.
  A reader who can read Python sees all of it without the
  docstring.
- Line comments narrate the next line. If the line itself is
  unclear, the fix is to rename a variable, not to add prose. If
  the line is clear, the prose is friction.
- Restatement comments rot silently. When the implementation
  changes, no test fails to flag the now-wrong comment; the
  docstring becomes a quietly misleading authority.

## Correct pattern

```good-code
def verify_signature(announcement: Announcement) -> None:
    canonical = canonical_json(announcement.body)
    ed25519.verify(announcement.signature, canonical, announcement.miner_hotkey)
```

A comment is justified only when the WHY is non-obvious — a hidden
constraint, a workaround for a specific bug, behaviour that would
surprise a reader. If the next sentence in your head is "obviously
…", the comment is restatement and should not land.

## Spec reference

- [12 § code style](../12-implementation-constraints.md#code-style)
  — "no comments unless WHY is non-obvious; never restate code
  behavior."
- [12 § documentation discipline](../12-implementation-constraints.md#documentation-discipline)
  — public functions get a one-line summary docstring; nothing
  more is owed.
- [24 § D-5](../24-design-heuristics.md) — optimize for the
  reader.

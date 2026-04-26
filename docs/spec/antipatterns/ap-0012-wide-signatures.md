<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0012 — Wide signatures

## Narrative

A function that takes `**kwargs`, an `options: dict[str, Any]`
"bag", or a stack of boolean flags hides what it actually requires
and what it does. The caller cannot tell from the signature what
is permitted; pyright cannot enforce it; and a reader (human or
agent) has to read the body to know the shape. This is the LLM
failure mode that produces "flexible" helpers nobody can use
correctly.

## Bad code

```bad-code
def submit(
    handle: RunHandle,
    dry_run: bool = False,
    auto: bool = False,
    confirm: bool = True,
    skip_oracle: bool = False,
    force: bool = False,
    **kwargs: Any,
) -> Announcement:
    """Submit a run with various options."""
    options = kwargs.get("options", {})
    if options.get("strict"):
        ...
    ...

submit(handle, dry_run=True, force=True, confirm=False)  # what does this mean?
```

## Why

- The caller `submit(handle, dry_run=True, force=True,
  confirm=False)` has six independent booleans, two of which
  (`auto`/`confirm`) are mutually exclusive in the spec. The type
  system permits 64 combinations; only a handful are coherent.
- `**kwargs: Any` discards the type-check entirely. A typo
  (`stict=True` instead of `strict=True`) silently does nothing,
  and there is no way for a reviewer or pyright to catch it.
- The "options dict" pattern hides required fields and lets
  optional ones drift: callers cannot tell what keys the function
  reads without reading the body.

## Correct pattern

```good-code
class ConfirmMode(StrEnum):
    AUTO = "auto"
    CONFIRM = "confirm"
    DRY_RUN = "dry-run"

def submit(handle: RunHandle, mode: ConfirmMode = ConfirmMode.CONFIRM) -> Announcement:
    ...

submit(handle, mode=ConfirmMode.DRY_RUN)
```

The mutually exclusive set becomes one enum-typed parameter. The
mode value is exhaustive (pyright checks `match` cases), and the
call site reads as English. Where multiple genuinely independent
inputs exist, name them as keyword-only parameters with concrete
types — not as a `**kwargs` bag.

## Spec reference

- [12 § code style](../12-implementation-constraints.md#code-style)
  — "type hints on every function; `Any` requires
  `# pyright: ignore[reportExplicitAny]` with a reason."
- [13 § write-gating](../13-agent-integration.md) — confirmation
  modes are an enum (`auto`, `dry-run`, `confirm`), not three
  booleans.
- [24 § D-2](../24-design-heuristics.md) — make illegal states
  unrepresentable.

<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0003 — Bare `except`

## Narrative

Every failure mode in the validator pipeline has a typed exception
in `src/hypotheses/errors.py` with a row in the fail-fast table at
[12 § fail-fast](../12-implementation-constraints.md#fail-fast-policy).
Catching `Exception` or using a bare `except:` swallows context,
prevents the rejection reason from being attributed to a real
threat, and creates silent-failure bugs the mutation gate cannot
see.

## Bad code

```bad-code
def verify_signature(announcement):
    try:
        ed25519.verify(announcement.signature, canonical_json(announcement.body), announcement.miner_hotkey)
    except Exception:
        return False
    return True
```

## Why

- Attribution is lost: a `SignatureInvalid` and a
  `DatasetHashMismatch` would collapse into the same `False` return,
  breaking the operator runbook mapping in [19](../19-operations.md).
- `except Exception` also catches `KeyboardInterrupt`-class
  surprises on Python versions where they inherit `Exception`, which
  hides operator-initiated cancellations.
- The fail-fast table lists specific exception types; a bare catch
  maps to *none* of them, so structured logging loses the `msg` key
  the operator's dashboards rely on.

## Correct pattern

```good-code
def verify_signature(announcement: Announcement) -> None:
    try:
        ed25519.verify(
            announcement.signature,
            canonical_json(announcement.body),
            announcement.miner_hotkey,
        )
    except ed25519.VerificationError as e:
        raise SignatureInvalid(str(announcement.body_hash)) from e
```

Let unexpected exceptions bubble. The pipeline's top-level handler
logs them once, emits a `validator.submission.rejected` event with
the typed reason, and moves on — surprise exceptions become a
visible bug, not a silent `False`.

## Spec reference

- [12 § fail-fast](../12-implementation-constraints.md#fail-fast-policy)
- [19 § events.jsonl](../19-operations.md#eventsjsonl) — rejection
  events carry `data.reason` keyed on the typed exception name.

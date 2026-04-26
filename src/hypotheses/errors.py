# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Typed exception taxonomy for the subnet.

One subclass per row in
[`docs/spec/12-implementation-constraints.md`](../../docs/spec/12-implementation-constraints.md)
§ fail-fast policy. Every subclass accepts arbitrary keyword fields
and exposes them via ``.details``; callers raise the typed exception
with structured context, and the top-level handler logs it once and
emits a matching event per ``docs/spec/19`` § events.jsonl.

spec: HM-REQ-0040
spec: HM-REQ-0042
"""

from __future__ import annotations

__all__ = [
    "ArtifactCorrupt",
    "DatasetHashMismatch",
    "EnvMismatch",
    "HypothesisError",
    "MetricMissing",
    "ReproductionFailed",
    "SandboxLimit",
    "SignatureInvalid",
    "SpecInvalid",
    "StorageUnavailable",
    "UnsupportedSchema",
]


class HypothesisError(Exception):
    """Base for every typed failure mode in the pipeline."""

    def __init__(self, **details: object) -> None:
        super().__init__(self.__class__.__name__)
        self.details: dict[str, object] = dict(details)

    def __str__(self) -> str:
        if not self.details:
            return self.__class__.__name__
        rendered = ", ".join(f"{k}={v!r}" for k, v in self.details.items())
        return f"{self.__class__.__name__}({rendered})"


class StorageUnavailable(HypothesisError):
    """IPFS unreachable when publishing."""


class MetricMissing(HypothesisError):
    """Declared metric absent from a run."""


class SpecInvalid(HypothesisError):
    """Hypothesis spec fails JSON-Schema validation."""


class SignatureInvalid(HypothesisError):
    """Manifest or synapse signature does not verify."""


class ReproductionFailed(HypothesisError):
    """Validator rerun disagrees with the miner-declared metric beyond tolerance."""


class EnvMismatch(HypothesisError):
    """Miner's env.lock does not match the validator's reproduction environment."""


class UnsupportedSchema(HypothesisError):
    """Synapse carries a schema_version this build does not understand."""


class ArtifactCorrupt(HypothesisError):
    """Artifact bytes do not hash to the declared CID."""


class SandboxLimit(HypothesisError):
    """Sandbox wallclock or memory ceiling breached."""


class DatasetHashMismatch(HypothesisError):
    """Dataset revision hash differs from the spec-declared pin."""

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Tests for the typed exception taxonomy.

spec: docs/spec/12-implementation-constraints.md § fail-fast policy
spec: HM-REQ-0040 (TDD)
spec: HM-REQ-0042 (SPDX headers)
"""

from __future__ import annotations

# spec: HM-REQ-0040
# spec: HM-REQ-0042

import pytest

from hypotheses.errors import (
    ArtifactCorrupt,
    DatasetHashMismatch,
    EnvMismatch,
    HypothesisError,
    MetricMissing,
    ReproductionFailed,
    SandboxLimit,
    SignatureInvalid,
    SpecInvalid,
    StorageUnavailable,
    UnsupportedSchema,
)

ALL_SUBCLASSES: tuple[type[HypothesisError], ...] = (
    StorageUnavailable,
    MetricMissing,
    SpecInvalid,
    SignatureInvalid,
    ReproductionFailed,
    EnvMismatch,
    UnsupportedSchema,
    ArtifactCorrupt,
    SandboxLimit,
    DatasetHashMismatch,
)


def test_base_inherits_from_exception() -> None:
    assert issubclass(HypothesisError, Exception)


def test_subclass_count_matches_fail_fast_table() -> None:
    assert len(ALL_SUBCLASSES) == 10


@pytest.mark.parametrize("cls", ALL_SUBCLASSES)
def test_subclass_inherits_from_base(cls: type[HypothesisError]) -> None:
    assert issubclass(cls, HypothesisError)
    assert cls is not HypothesisError


@pytest.mark.parametrize("cls", ALL_SUBCLASSES)
def test_class_name_preserved(cls: type[HypothesisError]) -> None:
    exc = cls()
    assert type(exc).__name__ == cls.__name__


@pytest.mark.parametrize("cls", ALL_SUBCLASSES)
def test_no_arg_construction_yields_empty_details(
    cls: type[HypothesisError],
) -> None:
    exc = cls()
    assert exc.details == {}


@pytest.mark.parametrize("cls", ALL_SUBCLASSES)
def test_kwargs_round_trip_into_details(cls: type[HypothesisError]) -> None:
    exc = cls(reason="boundary", count=3, hotkey="5G...")
    assert exc.details == {"reason": "boundary", "count": 3, "hotkey": "5G..."}


@pytest.mark.parametrize("cls", ALL_SUBCLASSES)
def test_details_dict_is_independent_of_construction_kwargs(
    cls: type[HypothesisError],
) -> None:
    exc = cls(reason="boundary")
    exc.details["mutated"] = True
    fresh = cls(reason="boundary")
    assert "mutated" not in fresh.details


def test_str_without_details_is_class_name() -> None:
    assert str(SpecInvalid()) == "SpecInvalid"


def test_str_with_details_includes_class_name_and_fields() -> None:
    rendered = str(SpecInvalid(field="metrics", missing=True))
    assert "SpecInvalid" in rendered
    assert "field" in rendered
    assert "metrics" in rendered


def test_positional_args_rejected() -> None:
    with pytest.raises(TypeError):
        SpecInvalid("metrics")  # type: ignore[call-arg]


def test_details_field_is_typed_dict() -> None:
    exc = SignatureInvalid(reason="bad-padding")
    assert isinstance(exc.details, dict)
    assert exc.details["reason"] == "bad-padding"

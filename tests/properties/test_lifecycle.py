# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Lifecycle property tests — HM-INV-0001..6 + HM-REQ-0002/3/70.

Phase 1: replace each skip with a Hypothesis-based property test.
"""

import pytest


# spec: HM-INV-0001
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0001")
def test_preregistration() -> None:
    raise NotImplementedError


# spec: HM-INV-0002
# spec: HM-REQ-0002
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0002 / HM-REQ-0002")
def test_immutability() -> None:
    raise NotImplementedError


# spec: HM-INV-0003
# spec: HM-REQ-0003
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0003 / HM-REQ-0003")
def test_version_ordering() -> None:
    raise NotImplementedError


# spec: HM-INV-0004
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0004")
def test_terminal_per_version() -> None:
    raise NotImplementedError


# spec: HM-INV-0005
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0005")
def test_withdrawal_absorbing() -> None:
    raise NotImplementedError


# spec: HM-INV-0006
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0006")
def test_author_withdraw() -> None:
    raise NotImplementedError


# spec: HM-REQ-0070
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0070")
def test_two_tier_settlement() -> None:
    raise NotImplementedError

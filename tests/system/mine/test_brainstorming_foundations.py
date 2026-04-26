# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-16..19 — informal-hypothesis registry and inspired_by gates.

Placeholder coverage for HM-REQ-0151..0154 introduced by ADR 0024.
Each test function maps to one S-MINE scenario in 23-system-tests.md
and one HM-REQ in requirements.md. Implementation lands when the
informal-hypothesis CLI surface ships in PR 2 / Phase 1.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-16
# spec: HM-REQ-0151
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-16")
def test_inspired_by_syntax() -> None:
    raise NotImplementedError


# spec: S-MINE-17
# spec: HM-REQ-0152
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-17")
def test_informal_stake() -> None:
    raise NotImplementedError


# spec: S-MINE-18
# spec: HM-REQ-0153
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-18")
def test_inspired_by_staleness() -> None:
    raise NotImplementedError


# spec: S-MINE-19
# spec: HM-REQ-0154
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-19")
def test_informal_treat_as_data() -> None:
    raise NotImplementedError

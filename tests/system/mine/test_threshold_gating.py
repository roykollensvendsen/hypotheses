# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-20..22 — threshold-gated execution and refund mechanics.

Placeholder coverage for HM-REQ-0160..0162 introduced by ADR 0025.
Each test function maps to one S-MINE scenario in 23-system-tests.md
and one HM-REQ in requirements.md. Implementation lands when the
threshold-gating CLI surface ships in PR B / Phase 1.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-20
# spec: HM-REQ-0160
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-20")
def test_pending_funding_rejects_submissions() -> None:
    raise NotImplementedError


# spec: S-MINE-21
# spec: HM-REQ-0161
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-21")
def test_funding_window_expiry_refund() -> None:
    raise NotImplementedError


# spec: S-MINE-22
# spec: HM-REQ-0162
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-22")
def test_min_pool_tao_formula() -> None:
    raise NotImplementedError

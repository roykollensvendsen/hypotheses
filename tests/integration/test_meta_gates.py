# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Meta-gate tests — HM-REQ-0040/41/42/90/100/110.

Today these rules are enforced by CI workflows; the placeholders
exist so the test-docstring scanner maps every HM-REQ.
"""

import pytest


# spec: HM-REQ-0040
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0040")
def test_tdd_gate() -> None:
    raise NotImplementedError


# spec: HM-REQ-0041
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0041")
def test_action_pin_check() -> None:
    raise NotImplementedError


# spec: HM-REQ-0042
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0042")
def test_spdx_headers() -> None:
    raise NotImplementedError


# spec: HM-REQ-0090
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0090")
def test_adversarial_coverage() -> None:
    raise NotImplementedError


# spec: HM-REQ-0100
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0100")
def test_security_bounty_embargo() -> None:
    raise NotImplementedError


# spec: HM-REQ-0110
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0110")
def test_single_source_principle() -> None:
    raise NotImplementedError

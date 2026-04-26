# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-13 — gated-tier hardware_profile without sponsorship is rejected.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-13
# spec: HM-REQ-0120
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-13")
def test_gated_profile_sponsorship() -> None:
    raise NotImplementedError

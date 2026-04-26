# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-15 — community-pool sponsorship caps are enforced at acceptance.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-15
# spec: HM-REQ-0140
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-15")
def test_community_pool_caps() -> None:
    raise NotImplementedError

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-10 — MCP list_hypotheses parity with hypo ls.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-10
# spec: HM-REQ-0001
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-10")
def test_mcp_list() -> None:
    raise NotImplementedError

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-VAL-06 — MCP get_score_history matches hypo scores byte-for-byte.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-VAL-06
# spec: HM-REQ-0010
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-VAL-06")
def test_mcp_score_parity() -> None:
    raise NotImplementedError

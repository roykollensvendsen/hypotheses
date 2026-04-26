# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-09 — SDK propose matches CLI propose for the same input.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-09
# spec: HM-REQ-0001
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-09")
def test_sdk_cli_parity() -> None:
    raise NotImplementedError

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-01 — happy-path propose+run+submit through the CLI.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-01
# spec: HM-REQ-0010
# spec: HM-REQ-0020
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-01")
def test_happy_path_cli() -> None:
    raise NotImplementedError

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-08 — propose without a registered hotkey exits non-zero.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-08
# spec: HM-REQ-0030
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-08")
def test_unregistered_hotkey() -> None:
    raise NotImplementedError

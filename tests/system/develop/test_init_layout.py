# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-DEV-03 — hypo init produces the documented directory layout.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-DEV-03
# spec: HM-REQ-0001
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-DEV-03")
def test_init_layout() -> None:
    raise NotImplementedError

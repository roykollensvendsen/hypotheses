# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-DEV-01 — hypo doctor exits 0 on a clean Phase-1 install.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-DEV-01
# spec: HM-REQ-0001
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-DEV-01")
def test_doctor_clean() -> None:
    raise NotImplementedError

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-VAL-03 — out-of-band metric zeros the reproduction component.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-VAL-03
# spec: HM-REQ-0010
# spec: HM-REQ-0020
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-VAL-03")
def test_rerun_tolerance() -> None:
    raise NotImplementedError

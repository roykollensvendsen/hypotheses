# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-05 — single-seed run refused when spec demands more.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-05
# spec: HM-REQ-0050
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-05")
def test_seed_required() -> None:
    raise NotImplementedError

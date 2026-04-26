# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-12 — multi-oracle hypothesis without composition is rejected.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-12
# spec: HM-REQ-0080
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-12")
def test_oracle_composition() -> None:
    raise NotImplementedError

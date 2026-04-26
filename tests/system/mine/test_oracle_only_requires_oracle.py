# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-14 — verification: oracle-only without an oracle block is rejected.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-14
# spec: HM-REQ-0130
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-14")
def test_oracle_only_requires_oracle() -> None:
    raise NotImplementedError

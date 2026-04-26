# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-VAL-04 — a validator skips scoring its own miner hotkey.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-VAL-04
# spec: HM-REQ-0012
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-VAL-04")
def test_no_self_score() -> None:
    raise NotImplementedError

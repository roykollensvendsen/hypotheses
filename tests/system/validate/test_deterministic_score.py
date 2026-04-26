# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-VAL-02 — two runs over the same submission produce identical scores.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-VAL-02
# spec: HM-REQ-0010
# spec: HM-REQ-0011
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-VAL-02")
def test_deterministic_score() -> None:
    raise NotImplementedError

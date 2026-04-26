# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-VAL-01 — validate serve picks up a fresh submission and scores it.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-VAL-01
# spec: HM-REQ-0010
# spec: HM-REQ-0020
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-VAL-01")
def test_discover_score() -> None:
    raise NotImplementedError

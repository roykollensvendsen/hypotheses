# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-VAL-05 — novelty tiebreak: block height, then in-block index, then SS58.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-VAL-05
# spec: HM-REQ-0021
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-VAL-05")
def test_novelty_tiebreak() -> None:
    raise NotImplementedError

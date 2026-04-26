# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""End-to-end smoke: H-0001 through miner → validator → scoring.

The safe-explore anchor (per docs/spec/05-validator.md): once
green, any refactor that breaks the pipeline fails this test.
"""

import pytest


# spec: HM-REQ-0010
# spec: HM-REQ-0020
@pytest.mark.skip(reason="phase-1 implementation pending: smoke pipeline")
def test_h0001_end_to_end() -> None:
    raise NotImplementedError

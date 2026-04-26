# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-11 — propose rejects a hypothesis with no external anchor.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-11
# spec: HM-REQ-0060
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-11")
def test_external_anchor_required() -> None:
    raise NotImplementedError

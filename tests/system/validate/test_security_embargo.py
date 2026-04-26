# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-VAL-08 — security hypothesis without prior advisory has improvement zeroed.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-VAL-08
# spec: HM-REQ-0100
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-VAL-08")
def test_security_embargo() -> None:
    raise NotImplementedError

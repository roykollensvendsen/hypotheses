# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-02 — malformed ed25519 signature on submit is rejected.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-02
# spec: HM-REQ-0030
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-02")
def test_bad_signature() -> None:
    raise NotImplementedError

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-DEV-04 — Client.from_env honours env-var precedence over config.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-DEV-04
# spec: HM-REQ-0001
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-DEV-04")
def test_client_from_env() -> None:
    raise NotImplementedError

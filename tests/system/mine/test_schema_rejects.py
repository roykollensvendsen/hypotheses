# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-04 — schema-invalid hypothesis at propose is rejected.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-04
# spec: HM-REQ-0001
# spec: HM-REQ-0050
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-04")
def test_schema_rejects() -> None:
    raise NotImplementedError

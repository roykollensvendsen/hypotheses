# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-MINE-03 — signature over non-RFC-8785 JSON fails verification.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-MINE-03
# spec: HM-REQ-0031
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-MINE-03")
def test_non_canonical_json() -> None:
    raise NotImplementedError

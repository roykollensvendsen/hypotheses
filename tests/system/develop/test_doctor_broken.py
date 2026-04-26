# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""S-DEV-02 — hypo doctor exits non-zero with a structured diagnostic.

spec: docs/spec/23-system-tests.md
"""

import pytest


# spec: S-DEV-02
# spec: HM-REQ-0001
@pytest.mark.system_local
@pytest.mark.skip(reason="phase-1 implementation pending: S-DEV-02")
def test_doctor_broken() -> None:
    raise NotImplementedError

# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Runtime property tests — HM-INV-0020..21 (HM-REQ-0010 covered)."""

import pytest


# spec: HM-INV-0020
# spec: HM-REQ-0010
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0020")
def test_determinism_bytes() -> None:
    raise NotImplementedError


# spec: HM-INV-0021
@pytest.mark.skip(reason="phase-1 implementation pending: HM-INV-0021")
def test_dataset_hash_pin() -> None:
    raise NotImplementedError

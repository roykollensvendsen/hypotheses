# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Synapse signing tests — HM-REQ-0030 (ed25519), HM-REQ-0031 (RFC 8785)."""

import pytest


# spec: HM-REQ-0030
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0030")
def test_synapse_signed() -> None:
    raise NotImplementedError


# spec: HM-REQ-0031
@pytest.mark.skip(reason="phase-1 implementation pending: HM-REQ-0031")
def test_canonical_json_signing() -> None:
    raise NotImplementedError

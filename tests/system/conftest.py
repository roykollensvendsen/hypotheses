# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Fixtures for the black-box system-test harness.

Contract: ``docs/spec/23-system-tests.md``. Every fixture here is a
Phase-1 placeholder; concrete implementations land alongside the
runtime code that backs each surface. Tests under ``tests/system/``
are all skipped today, so the ``raise NotImplementedError`` paths
are unreachable; replacing each test's ``skip`` marker with a real
assertion is the safe-explore entry point per
``docs/spec/05-validator.md``.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def tmp_registry(tmp_path: Path) -> Path:
    """Fresh on-disk registry rooted under pytest's ``tmp_path``.

    Each scenario gets its own registry; nothing is shared across
    tests. xdist-safe because ``tmp_path`` is per-worker.
    """
    raise NotImplementedError("phase-1 implementation pending: tmp_registry")


@pytest.fixture
def fake_hotkey(request: pytest.FixtureRequest) -> Any:
    """Deterministic ed25519 keypair derived from the test nodeid.

    Stable across re-runs; never collides across xdist workers.
    """
    raise NotImplementedError("phase-1 implementation pending: fake_hotkey")


@pytest.fixture
def system_seed(request: pytest.FixtureRequest) -> int:
    """Per-scenario seed; flake budget is zero (see spec §Pass/fail)."""
    raise NotImplementedError("phase-1 implementation pending: system_seed")


@pytest.fixture
def clock() -> Any:
    """Controllable clock for scenarios that touch epoch boundaries.

    Pulls through the validator's clock seam (``docs/spec/05-validator.md``);
    never wall-clock-``sleep()``.
    """
    raise NotImplementedError("phase-1 implementation pending: clock")


@pytest.fixture
def port_pool() -> Any:
    """Per-worker port allocator for HTTP-MCP scenarios (Phase-2 hook)."""
    raise NotImplementedError("phase-1 implementation pending: port_pool")


@pytest.fixture
def validator_proc(tmp_registry: Path, fake_hotkey: Any) -> Iterator[Any]:
    """Supervised ``hypo validate serve`` subprocess.

    Yields a handle the driver uses to read stderr / structured logs;
    SIGTERM at teardown.
    """
    raise NotImplementedError("phase-1 implementation pending: validator_proc")


@pytest.fixture
def mcp_proc(tmp_registry: Path) -> Iterator[Any]:
    """Supervised ``hypo mcp serve`` subprocess (read-only in Phase 1).

    stdio transport per ``docs/spec/13-agent-integration.md``.
    """
    raise NotImplementedError("phase-1 implementation pending: mcp_proc")


@pytest.fixture
def mcp_client(mcp_proc: Any) -> Any:
    """Stdio MCP client wired to ``mcp_proc``; speaks JSON-RPC."""
    raise NotImplementedError("phase-1 implementation pending: mcp_client")

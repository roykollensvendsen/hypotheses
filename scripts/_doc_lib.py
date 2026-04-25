# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Shared helpers for documentation-quality checker scripts.

Modules under `scripts/check_*.py` import from here to share
front-matter parsing, link extraction, and token-count estimation.
Each script is run with `uv run`; PEP-723 inline metadata in the
script (not this library) declares the dependency on `pyyaml`.

This file is not a runnable script. Importing it has no
side-effects.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
RELATIVE_MD_LINK_RE = re.compile(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)")


def parse_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str, str]:
    """Return ``(frontmatter, body, error)``.

    On success ``error`` is empty. On a parse failure ``frontmatter``
    is ``None`` and ``error`` describes the cause; ``body`` is the
    raw file text in that case so callers can still inspect it.
    """
    text = path.read_text()
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text, "no `---`-fenced YAML front-matter at start of file"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, text, f"YAML parse error: {exc}"
    if not isinstance(data, dict):
        return None, text, f"front-matter must be a mapping, got {type(data).__name__}"
    body = text[match.end() :]
    return data, body, ""


def estimate_tokens(text: str) -> int:
    """Heuristic token count for prose.

    Strips HTML comments and counts whitespace-separated words, then
    multiplies by 1.3 — the same factor AGENTS.md documents for the
    declared ``tokens:`` budgets. Rough; for "is the declared value
    in the right order of magnitude" rather than exact accounting.
    """
    no_comments = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    words = no_comments.split()
    return int(len(words) * 1.3)


def extract_md_links(text: str) -> list[str]:
    """Return relative `.md` link targets found in a markdown body.

    Strips fragment identifiers and skips bare URLs. Handles only
    inline links (``[text](path.md)``) — reference-style links are
    not used in this repo today.
    """
    return [m.group(1) for m in RELATIVE_MD_LINK_RE.finditer(text)]

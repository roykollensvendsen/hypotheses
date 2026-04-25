# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Detect orphan markdown files.

BFS from a fixed set of root entry points (root governance files
that are loaded directly by humans/CI, not by following links)
over relative `.md` links found in inline-link form
(``[text](path.md)``). Any tracked `.md` not reachable from a root
is reported.

This catches: a doc moved without redirect; a doc accidentally
landed without being linked from anywhere; a stale file from a
deleted feature. It does *not* catch broken links — that is
lychee's job.

Used by `.github/workflows/orphan-docs.yml`.

Allow-list rationale:
- Antipattern files are linked transitively only by
  `docs/spec/antipatterns/README.md` listing them as a directory;
  that is enough to count as reachable, so no allow-list entry.
- Experiment READMEs link to and from their hypothesis spec; if
  the hypothesis is reachable, the experiment is reachable.
- Files under `agents/examples/` are Phase-1 placeholders.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _doc_lib import extract_md_links  # noqa: E402

ROOTS: tuple[Path, ...] = (
    Path("README.md"),
    Path("AGENTS.md"),
    Path("VISION.md"),
    Path("GOVERNANCE.md"),
    Path("SECURITY.md"),
    Path("CONTRIBUTING.md"),
    Path("CODE_OF_CONDUCT.md"),
    Path("CHANGELOG.md"),
    Path(".github/PULL_REQUEST_TEMPLATE.md"),
    Path("docs/spec/README.md"),
    Path("docs/spec/antipatterns/README.md"),
    Path("docs/spec/formal/README.md"),
    Path("docs/adr/README.md"),
    Path("docs/tasks/README.md"),
    Path("agents/README.md"),
    Path("agents/examples/README.md"),
    Path("hypotheses/HYPOTHESIS_TEMPLATE.md"),
    Path("src/hypotheses/spec/schema/README.md"),
    Path("tests/golden/README.md"),
    Path("tests/golden/adversarial/README.md"),
)

# Each `experiments/H-NNNN/README.md` is a directly-loaded entry
# point: an operator runs `hypo run H-NNNN` and reads it. The
# hypothesis spec → experiment relationship is via YAML
# `code_ref:`, not a markdown link, so a strict link-graph BFS
# does not reach them. Glob them as roots instead of allow-listing.
ROOT_GLOBS: tuple[str, ...] = ("experiments/*/README.md",)

EXCLUDE_DIR_PARTS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        ".ruff_cache",
        ".vale",
    }
)

ALLOW_LIST: frozenset[Path] = frozenset()


def all_md_files() -> list[Path]:
    out: list[Path] = []
    for path in Path().rglob("*.md"):
        if any(part in EXCLUDE_DIR_PARTS for part in path.parts):
            continue
        out.append(path)
    return sorted(out)


def normalize(path: Path) -> Path:
    return Path(path).resolve().relative_to(Path().resolve())


def resolve_link(source: Path, link: str) -> Path | None:
    target = (source.parent / link).resolve()
    repo = Path().resolve()
    try:
        rel = target.relative_to(repo)
    except ValueError:
        return None
    return rel


def main() -> int:
    all_md = all_md_files()
    seen: set[Path] = set()

    queue: deque[Path] = deque()
    static_roots = list(ROOTS) + sorted(p for g in ROOT_GLOBS for p in Path().glob(g))
    for root in static_roots:
        if root.exists():
            seen.add(root)
            queue.append(root)

    while queue:
        node = queue.popleft()
        try:
            text = node.read_text()
        except OSError:
            continue
        for link in extract_md_links(text):
            target = resolve_link(node, link)
            if target is None or not target.exists():
                continue
            if target in seen:
                continue
            seen.add(target)
            queue.append(target)

    orphans = [p for p in all_md if p not in seen and p not in ALLOW_LIST]

    if orphans:
        print("orphan markdown files (unreachable from any root):")
        for p in orphans:
            print(f"  {p}")
        print(
            f"\n{len(orphans)} orphan(s). Either link from an existing doc, "
            "promote to a root in scripts/check_orphan_docs.py, or add to "
            "the script's ALLOW_LIST with a justification comment."
        )
        return 1
    print(f"orphan check OK: {len(seen)} reachable .md, 0 orphans")
    return 0


if __name__ == "__main__":
    sys.exit(main())

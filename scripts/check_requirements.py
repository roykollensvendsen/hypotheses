# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Verify HM-REQ-NNNN tags are consistent across the spec tree.

Parses:

- `docs/spec/requirements.md` — the authoritative index.
- Every `docs/spec/**/*.md` — inline tags in the form
  `**HM-REQ-NNNN**` (typically inside a block-quote).
- Every `src/**/*.py` and `tests/**/*.py` — future back-references
  from code as `# spec: HM-REQ-NNNN` (Phase 1+). Informational today.

Fails on:

- Duplicate inline definitions of the same ID.
- IDs in the index that are not defined inline in any spec doc.
- IDs defined inline that do not appear in the index.
- Malformed tags.

Used by `.github/workflows/requirements.yml`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TAG_RE = re.compile(r"\bHM-(?P<kind>REQ|INV)-(?P<num>\d{4})\b")
INDEX_PATH = Path("docs/spec/requirements.md")
INVARIANTS_INDEX_PATH = Path("docs/spec/invariants.md")
SPEC_DOCS_ROOT = Path("docs/spec")
CODE_ROOTS = (Path("src"), Path("tests"))
CODE_REF_RE = re.compile(r"#\s*spec:\s*HM-(?:REQ|INV)-\d{4}")


def parse_index_ids(path: Path) -> dict[str, tuple[str, int]]:
    """Return {ID: (first-match-snippet, line_no)} — table rows only.

    The index is a markdown table; only lines that start with a pipe
    and have at least three pipes qualify. Prose examples elsewhere
    in the doc are ignored.
    """
    if not path.exists():
        return {}
    ids: dict[str, tuple[str, int]] = {}
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.lstrip()
        if not stripped.startswith("|") or stripped.count("|") < 3:
            continue
        if (
            set(stripped.replace("|", "").replace("-", "").replace(":", "").strip())
            == set()
        ):
            continue  # table separator row: |---|---|
        for match in TAG_RE.finditer(line):
            full = f"HM-{match.group('kind')}-{match.group('num')}"
            if full not in ids:
                ids[full] = (line.strip()[:200], i)
    return ids


def find_inline_definitions() -> dict[str, list[tuple[Path, int, str]]]:
    """Inline definitions are `**HM-REQ-NNNN**` (or inside block-quotes)."""
    defs: dict[str, list[tuple[Path, int, str]]] = {}
    if not SPEC_DOCS_ROOT.exists():
        return defs
    for p in SPEC_DOCS_ROOT.rglob("*.md"):
        if p.name == "requirements.md" or p.name == "invariants.md":
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            if "**HM-" not in line:
                continue
            for match in TAG_RE.finditer(line):
                if f"**HM-{match.group('kind')}-{match.group('num')}**" in line:
                    tag = f"HM-{match.group('kind')}-{match.group('num')}"
                    defs.setdefault(tag, []).append((p, i, line.strip()[:200]))
    return defs


def find_code_references() -> dict[str, list[tuple[Path, int]]]:
    refs: dict[str, list[tuple[Path, int]]] = {}
    for root in CODE_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            for i, line in enumerate(
                p.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if not CODE_REF_RE.search(line):
                    continue
                for match in TAG_RE.finditer(line):
                    tag = f"HM-{match.group('kind')}-{match.group('num')}"
                    refs.setdefault(tag, []).append((p, i))
    return refs


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    index_reqs = parse_index_ids(INDEX_PATH)
    index_invs = parse_index_ids(INVARIANTS_INDEX_PATH)
    indexed = {**index_reqs, **index_invs}
    definitions = find_inline_definitions()

    # Duplicate definitions
    for tag, sites in definitions.items():
        if len(sites) > 1:
            for p, i, _ in sites:
                errors.append(
                    f"::error file={p},line={i}::{tag} has multiple inline "
                    f"definitions across the spec; keep exactly one canonical home."
                )

    defined_set = set(definitions)
    indexed_set = set(indexed)

    # Indexed but not defined inline
    for tag in sorted(indexed_set - defined_set):
        snippet, line_no = indexed[tag]
        errors.append(
            f"::error file={INDEX_PATH},line={line_no}::{tag} is in the "
            f"index but has no inline **{tag}** block-quote in a spec doc."
        )

    # Defined inline but not indexed
    for tag in sorted(defined_set - indexed_set):
        p, i, _ = definitions[tag][0]
        errors.append(
            f"::error file={p},line={i}::{tag} is defined inline but is "
            f"not listed in docs/spec/requirements.md or docs/spec/invariants.md."
        )

    # Informational: code back-references to missing IDs.
    code_refs = find_code_references()
    for tag in sorted(set(code_refs) - indexed_set):
        for p, i in code_refs[tag]:
            warnings.append(
                f"::warning file={p},line={i}::{tag} referenced from code "
                f"but missing from index (informational until Phase 1 code lands)."
            )

    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    if errors:
        print(
            f"\n{len(errors)} requirement-consistency error(s). "
            f"See docs/spec/requirements.md and docs/spec/invariants.md.",
            file=sys.stderr,
        )
        return 1
    print(
        f"requirements.md + invariants.md: {len(index_reqs)} HM-REQ, "
        f"{len(index_invs)} HM-INV; all consistent."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

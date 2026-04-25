# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Validate `CITATION.cff` against the CFF v1.2.0 essentials.

A native Python check that replaces the third-party
`dieghernan/cff-validator` action (whose SHA we couldn't pin
reliably without a confirmed lookup). Catches the editing
mistakes the project actually cares about:

- Missing or malformed YAML.
- Missing required top-level fields (`cff-version`, `message`,
  `title`, `authors`).
- Recognised `cff-version` value (1.2.x).
- At least one author with either `name` (organisation form) or
  `family-names` (person form).

Does **not** attempt full CFF schema coverage; for that, run
`cffconvert --validate` locally (it pulls the published JSON
Schema). This script catches the common failures and fits the
project's "stdlib + pyyaml + jsonschema" toolchain.

Used by `.github/workflows/citation-validate.yml`.

Exit codes:
    0 — CITATION.cff is well-formed
    1 — validation errors
    2 — internal error (file missing)
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

CITATION_PATH = Path("CITATION.cff")
REQUIRED_TOP_LEVEL: tuple[str, ...] = (
    "cff-version",
    "message",
    "title",
    "authors",
)
SUPPORTED_CFF_VERSIONS: tuple[str, ...] = ("1.2.0",)


def main() -> int:
    if not CITATION_PATH.exists():
        print(f"error: {CITATION_PATH} not found", file=sys.stderr)
        return 2
    try:
        data = yaml.safe_load(CITATION_PATH.read_text())
    except yaml.YAMLError as exc:
        print(f"error: YAML parse failure: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print(
            f"error: top-level must be a mapping, got {type(data).__name__}",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []
    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            errors.append(f"missing required field: {field!r}")

    cff_version = data.get("cff-version")
    if cff_version is not None and str(cff_version) not in SUPPORTED_CFF_VERSIONS:
        errors.append(
            f"cff-version: {cff_version!r} not in supported set "
            f"{SUPPORTED_CFF_VERSIONS}; bump SUPPORTED_CFF_VERSIONS in this "
            "script if upstream releases a new version we want to adopt."
        )

    authors = data.get("authors")
    if authors is not None:
        if not isinstance(authors, list) or not authors:
            errors.append("authors: must be a non-empty list")
        else:
            for i, author in enumerate(authors):
                if not isinstance(author, dict):
                    errors.append(f"authors[{i}]: must be a mapping")
                    continue
                if "name" not in author and "family-names" not in author:
                    errors.append(
                        f"authors[{i}]: must declare either 'name' "
                        "(organisation form) or 'family-names' (person form)"
                    )

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        print(f"\n{len(errors)} CITATION.cff validation error(s)", file=sys.stderr)
        return 1
    print(
        f"CITATION.cff OK: cff-version={cff_version}, {len(data.get('authors', []))} "
        "author entry/ies"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jsonschema>=4.20",
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Validate every hypothesis under `hypotheses/` against the JSON Schema.

Parses the YAML front matter out of each `hypotheses/H-*.md` file and
validates it against `src/hypotheses/spec/schema/hypothesis.schema.json`.
Used by `.github/workflows/spec-validate.yml`.

Excludes `HYPOTHESIS_TEMPLATE.md` — the template contains `TBD`
placeholders for enum fields that are not valid hypothesis values.

Exit codes:
    0 — every hypothesis validates
    1 — one or more validation errors
    2 — internal error (missing schema, bad script args)
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path("src/hypotheses/spec/schema/hypothesis.schema.json")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
EXCLUDE_NAMES = frozenset({"HYPOTHESIS_TEMPLATE.md"})


def normalize(value: Any) -> Any:
    """Coerce YAML-native dates to ISO strings so the JSON Schema matches."""
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    return value


def parse_front_matter(text: str) -> dict:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError("file does not start with YAML front matter")
    return normalize(yaml.safe_load(match.group(1)))


def hypothesis_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.glob("H-*.md") if p.is_file() and p.name not in EXCLUDE_NAMES
    )


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("hypotheses")
    if not root.is_dir():
        print(f"::error::hypotheses root {root} does not exist", file=sys.stderr)
        return 2
    if not SCHEMA_PATH.is_file():
        print(f"::error::schema {SCHEMA_PATH} not found", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    files = hypothesis_files(root)
    if not files:
        print(f"no hypotheses in {root}")
        return 0

    total_errors = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        try:
            data = parse_front_matter(text)
        except (ValueError, yaml.YAMLError) as e:
            print(f"::error file={path}::{e}")
            total_errors += 1
            continue

        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        for err in errors:
            loc = "/".join(str(part) for part in err.path) or "<root>"
            print(f"::error file={path}::{loc}: {err.message}")
        total_errors += len(errors)

    if total_errors:
        print(
            f"\n{total_errors} validation error(s) across {len(files)} hypothesis file(s)",
            file=sys.stderr,
        )
        return 1

    print(f"all {len(files)} hypothesis file(s) validate")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

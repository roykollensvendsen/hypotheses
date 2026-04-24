# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jsonschema>=4.20",
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Verify the hypothesis spec doc and its JSON Schema agree.

Extracts the worked-example YAML block under the `## Spec fields`
section of `docs/spec/02-hypothesis-format.md` and validates it
against `src/hypotheses/spec/schema/hypothesis.schema.json`. If the
example fails validation, doc and schema have drifted.

Used by `.github/workflows/spec-validate.yml`.
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

DOC_PATH = Path("docs/spec/02-hypothesis-format.md")
SCHEMA_PATH = Path("src/hypotheses/spec/schema/hypothesis.schema.json")

EXAMPLE_RE = re.compile(
    r"##\s+Spec\s+fields.*?```yaml\s*\n(?P<body>.*?)\n```",
    re.DOTALL,
)


def normalize(value: Any) -> Any:
    """Coerce YAML-native dates to ISO strings so the JSON Schema matches."""
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    return value


def extract_example(doc_text: str) -> dict:
    match = EXAMPLE_RE.search(doc_text)
    if not match:
        raise RuntimeError(f"no ```yaml block under '## Spec fields' in {DOC_PATH}")
    return normalize(yaml.safe_load(match.group("body")))


def main() -> int:
    if not DOC_PATH.is_file():
        print(f"::error::spec doc {DOC_PATH} not found", file=sys.stderr)
        return 2
    if not SCHEMA_PATH.is_file():
        print(f"::error::schema {SCHEMA_PATH} not found", file=sys.stderr)
        return 2

    doc_text = DOC_PATH.read_text(encoding="utf-8")
    try:
        example = extract_example(doc_text)
    except (RuntimeError, yaml.YAMLError) as e:
        print(f"::error::{e}", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
    if errors:
        print(
            f"::error::spec example in {DOC_PATH} does not validate against {SCHEMA_PATH}:"
        )
        for err in errors:
            loc = "/".join(str(part) for part in err.path) or "<root>"
            print(f"::error::  {loc}: {err.message}")
        return 1

    print(f"spec example in {DOC_PATH} validates against {SCHEMA_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jsonschema>=4.20",
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Validate spec-doc YAML front matter against the schema.

For every file under `docs/spec/` that should carry front-matter
(numbered specs, requirements/invariants indexes, README.md, and
the formal/ index), parses the leading `---`-fenced YAML block and
validates it against
`docs/spec/_schemas/spec-frontmatter.schema.json`.

Additional graph-shape check beyond the schema:

- Every entry in `depends_on` resolves to an existing
  `docs/spec/NN-*.md` (or `docs/spec/NN.5-*.md`). An unresolved
  reference is a typo or a deletion that did not propagate.

`depends_on` is intentionally allowed to contain cycles
(e.g. `10-repo-layout.md` and `12-implementation-constraints.md`
reference each other) since the field is a "you benefit from
reading this for context" hint rather than a strict DAG.

Skipped: `docs/spec/antipatterns/` files, whose layout starts with a
`<!-- antipattern-content -->` marker on line 1 (load-bearing for
the prompt-injection scanner) and which do not carry YAML
front-matter today. PR-7 of the documentation-quality sprint adds
a `protects:` HTML-comment field to those files; the
prompt-injection scanner — not this script — validates it.

Used by `.github/workflows/frontmatter.yml`.

Exit codes:
    0 — every file validates and graph is acyclic
    1 — one or more validation errors
    2 — internal error (missing schema, bad script args)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path("docs/spec/_schemas/spec-frontmatter.schema.json")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)

SCAN_GLOBS: tuple[str, ...] = (
    "docs/spec/*.md",
    "docs/spec/formal/*.md",
)

# Files matching these names are not part of the spec-frontmatter
# system. Antipatterns carry their own line-1 marker; ADR/_schema
# directories live alongside the spec but do not host prose.
EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        "antipatterns",
        "_schemas",
    }
)


def iter_files() -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for glob in SCAN_GLOBS:
        for path in sorted(Path().glob(glob)):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path in seen:
                continue
            seen.add(path)
            out.append(path)
    return out


def normalize_depends_on(value: Any) -> Any:
    """Coerce numeric YAML depends_on entries to canonical NN(.5) strings.

    `depends_on: [02, 18]` parses as `[2, 18]` because YAML strips the
    leading zero. `depends_on: [0.5]` parses as `[0.5]` because YAML
    treats it as a float. Both forms are common in spec front-matter;
    this script normalizes them to `"02"`, `"18"`, `"00.5"` so the
    schema can require strings consistently.
    """
    if isinstance(value, bool):  # bool is subclass of int; reject early
        return value
    if isinstance(value, int):
        return f"{value:02d}"
    if isinstance(value, float):
        whole = int(value)
        frac = value - whole
        if abs(frac - 0.5) < 1e-9:
            return f"{whole:02d}.5"
        return str(value)
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str]:
    text = path.read_text()
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, "no `---`-fenced YAML front-matter at start of file"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, f"YAML parse error: {exc}"
    if not isinstance(data, dict):
        return None, f"front-matter must be a mapping, got {type(data).__name__}"
    if isinstance(data.get("depends_on"), list):
        data["depends_on"] = [normalize_depends_on(v) for v in data["depends_on"]]
    return data, ""


def resolve_depends_on(value: str) -> Path | None:
    """Return the spec file that `NN` (or `NN.5`) refers to, or None."""
    candidates = list(Path("docs/spec").glob(f"{value}-*.md"))
    return candidates[0] if candidates else None


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(f"error: schema not found at {SCHEMA_PATH}", file=sys.stderr)
        return 2
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)

    files = iter_files()
    if not files:
        print("error: no spec files matched scan globs", file=sys.stderr)
        return 2

    errors: list[str] = []

    for path in files:
        data, parse_err = parse_frontmatter(path)
        if data is None:
            errors.append(f"{path}: {parse_err}")
            continue
        schema_errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        for err in schema_errors:
            location = "/".join(str(p) for p in err.path) or "<root>"
            errors.append(f"{path}: schema: {location}: {err.message}")
        for dep in data.get("depends_on", []):
            if not isinstance(dep, str):
                # Schema error already raised above.
                continue
            if resolve_depends_on(dep) is None:
                errors.append(
                    f"{path}: depends_on: '{dep}' does not resolve to any "
                    f"docs/spec/NN-*.md file"
                )

    if errors:
        for err in errors:
            print(err)
        print(f"\n{len(errors)} error(s) across {len(files)} file(s)")
        return 1
    print(f"front-matter OK: {len(files)} file(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

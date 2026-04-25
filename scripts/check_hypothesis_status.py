# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Validate hypothesis `status:` field against the lifecycle spec.

Parses the State table from `docs/spec/17-hypothesis-lifecycle.md`
to learn the allowed `status:` values, then walks every
`hypotheses/H-*.md` and asserts the front-matter `status:` is in
that set.

The state list is read live from the spec doc — this script never
hard-codes a copy. That is the point: adding a new state is one
edit to the spec, not two.

PR-diff transition validation (e.g., `accepted -> settled-supported`
requires a validator artifact reference) is **deferred**. It needs
Phase-1 runtime artifacts to assert against. Once `tests/` ships
real fixtures the check extends in place. See the
`# TODO(phase-1)` markers in this file.

Used by `.github/workflows/hypothesis-status.yml`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _doc_lib import parse_frontmatter  # noqa: E402

LIFECYCLE_DOC = Path("docs/spec/17-hypothesis-lifecycle.md")
HYPOTHESES_GLOB = "hypotheses/H-*.md"
STATE_ROW_RE = re.compile(r"^\|\s*`(?P<state>[a-z][a-z-]+)`\s*\|", re.MULTILINE)


def parse_states() -> set[str]:
    if not LIFECYCLE_DOC.exists():
        print(f"error: lifecycle doc missing at {LIFECYCLE_DOC}", file=sys.stderr)
        sys.exit(2)
    text = LIFECYCLE_DOC.read_text()
    # Find the table after '## States'
    states_section = text.split("## States", 1)
    if len(states_section) != 2:
        print("error: '## States' header not found in lifecycle doc", file=sys.stderr)
        sys.exit(2)
    body = states_section[1].split("\n## ", 1)[0]
    states = {m.group("state") for m in STATE_ROW_RE.finditer(body)}
    if not states:
        print("error: no state rows parsed from lifecycle doc", file=sys.stderr)
        sys.exit(2)
    return states


def main() -> int:
    allowed = parse_states()
    errors: list[str] = []
    checked = 0

    for path in sorted(Path().glob(HYPOTHESES_GLOB)):
        if path.name == "HYPOTHESIS_TEMPLATE.md":
            continue
        data, _, err = parse_frontmatter(path)
        if data is None:
            errors.append(f"{path}: {err}")
            continue
        status = data.get("status")
        if not isinstance(status, str):
            errors.append(f"{path}: status: missing or not a string")
            continue
        if status not in allowed:
            errors.append(
                f"{path}: status: '{status}' is not a known lifecycle state. "
                f"Allowed: {sorted(allowed)}"
            )
            continue
        checked += 1
        # TODO(phase-1): on PR diff, validate transition is legal per the
        # transition table in 17-hypothesis-lifecycle.md, and that
        # authority-bearing transitions (accepted -> settled-*, settled-* ->
        # confirmed) carry a CODEOWNER `lifecycle/admin-override` label or
        # a validator-artifact reference (the latter requires Phase 1).

    if errors:
        for err in errors:
            print(f"error: {err}")
        print(f"\n{len(errors)} error(s) over {checked} hypothesis file(s)")
        return 1
    print(
        f"hypothesis-status OK: {checked} file(s); "
        f"{len(allowed)} states from {LIFECYCLE_DOC}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Audit declared `tokens:` against measured prose body length.

For every `docs/spec/*.md` (and `docs/spec/formal/*.md`) that
declares a `tokens:` value in front-matter, computes a heuristic
token estimate of the body and compares it to the declared value.

Tolerances:
- Diff up to 40 % from declared: silently OK.
- 40-100 %: warning printed, exit 0 (does not fail CI).
- > 100 %: fail.

The 100 % outer tolerance is deliberately lax. AGENTS.md documents
the declared values as rough planning estimates — the goal is
"the declared budget is in the right order of magnitude", not
exact accounting. Tightening the bound is a follow-up after a
calibration pass that re-aligns AGENTS.md routing-table totals.

Used by `.github/workflows/token-budget.yml`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _doc_lib import estimate_tokens, parse_frontmatter  # noqa: E402

WARN_RATIO = 0.40
FAIL_RATIO = 1.00

SCAN_GLOBS: tuple[str, ...] = (
    "docs/spec/*.md",
    "docs/spec/formal/*.md",
)


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    checked = 0

    paths = sorted({p for glob in SCAN_GLOBS for p in Path().glob(glob)})
    for path in paths:
        if "antipatterns" in path.parts or "_schemas" in path.parts:
            continue
        data, body, err = parse_frontmatter(path)
        if data is None:
            failures.append(f"{path}: {err}")
            continue
        declared = data.get("tokens")
        if not isinstance(declared, int):
            continue  # tokens: optional in some indexes; covered by check_frontmatter
        measured = estimate_tokens(body)
        diff_ratio = abs(measured - declared) / declared if declared else 0.0
        checked += 1
        if diff_ratio > FAIL_RATIO:
            failures.append(
                f"{path}: tokens: declared {declared}, measured ~{measured} "
                f"(off by {diff_ratio:.0%}, > {FAIL_RATIO:.0%} fail threshold)"
            )
        elif diff_ratio > WARN_RATIO:
            warnings.append(
                f"{path}: tokens: declared {declared}, measured ~{measured} "
                f"(off by {diff_ratio:.0%})"
            )

    for warn in warnings:
        print(f"warning: {warn}")
    if failures:
        for fail in failures:
            print(f"error: {fail}")
        print(
            f"\n{len(failures)} error(s), {len(warnings)} warning(s) over {checked} file(s)"
        )
        return 1
    print(
        f"token budget OK: {checked} file(s) within ±{FAIL_RATIO:.0%} "
        f"of declared ({len(warnings)} warning(s) outside ±{WARN_RATIO:.0%})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

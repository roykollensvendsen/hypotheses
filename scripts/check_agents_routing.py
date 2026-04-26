# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Validate the AGENTS.md `## Context routing` table.

Two layers of check:

1. **Doc resolution (error)**. Every summand in the `load`
   column must resolve to an existing file. Recognised shapes:
   - `NN`, `NN.5`             → docs/spec/NN-*.md
   - `invariants`, `requirements`, `traceability`
                              → docs/spec/<name>.md
   - `antipatterns/`          → docs/spec/antipatterns/ directory
   - `antipatterns/ap-NNNN`   → docs/spec/antipatterns/ap-NNNN-*.md
   - `existing H-...`         → at least one hypotheses/H-*.md exists

2. **Arithmetic (warning)**. Where a summand carries a
   `(~Ntokens)` parenthetical, it should match the referenced
   doc's front-matter `tokens:` within ±25 %. The row's
   `≈ total` should match the sum of summands within ±25 %.
   Both are warning-level today; AGENTS.md documents the values
   as rough planning estimates. Tightening the bound is a
   follow-up after a calibration pass.

Used by `.github/workflows/agents-routing.yml`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _doc_lib import parse_frontmatter  # noqa: E402

AGENTS_PATH = Path("AGENTS.md")
SPEC_DIR = Path("docs/spec")

ARITHMETIC_TOLERANCE = 0.10

# Parenthetical shapes allowed after a doc reference:
#   (~1500)                       — single value
#   (~800–2500)                   — range; range_max captures the upper end
#   (~3800, only if X-flavoured)  — single value with trailing comment
TOKENS_PAREN = (
    r"(?:\s*\(\s*\~?\s*(?P<tokens>\d+)"
    r"(?:\s*[–-]\s*(?P<tokens_max>\d+))?"
    r"(?:\s*,[^)]*)?\s*\))?"
)

SUMMAND_SHAPES = (
    re.compile(r"^(?P<n>\d{2}(?:\.\d+)?)" + TOKENS_PAREN + r"$"),
    re.compile(
        r"^(?P<name>invariants|requirements|traceability)" + TOKENS_PAREN + r"$"
    ),
    re.compile(r"^antipatterns/(?P<ap>ap-\d{4})" + TOKENS_PAREN + r"$"),
    re.compile(r"^antipatterns/?" + TOKENS_PAREN + r"$"),
    re.compile(r"^existing\s+H-\d+x?" + TOKENS_PAREN + r"$"),
)

TOTAL_RE = re.compile(r"(?:≈|=)?\s*(\d+)(?:\s*[–-]\s*(\d+))?")


def find_routing_table(text: str) -> list[str]:
    """Return the rows of the GFM table under '## Context routing'."""
    lines = text.splitlines()
    rows: list[str] = []
    in_section = False
    in_table = False
    for line in lines:
        if line.startswith("## "):
            in_section = "context routing" in line.lower()
            in_table = False
            continue
        if not in_section:
            continue
        if line.startswith("|"):
            in_table = True
            rows.append(line)
        elif in_table and not line.strip():
            break
    return rows


def parse_summand(summand: str) -> dict | None:
    summand = summand.strip()
    if not summand:
        return None
    for pattern in SUMMAND_SHAPES:
        m = pattern.match(summand)
        if m:
            d: dict[str, str | int | None] = dict(m.groupdict())
            return d
    return None


def resolve_summand(parsed: dict) -> Path | None:
    if "n" in parsed and parsed["n"]:
        candidates = list(SPEC_DIR.glob(f"{parsed['n']}-*.md"))
        return candidates[0] if candidates else None
    if "name" in parsed and parsed["name"]:
        target = SPEC_DIR / f"{parsed['name']}.md"
        return target if target.exists() else None
    if "ap" in parsed and parsed["ap"]:
        candidates = list((SPEC_DIR / "antipatterns").glob(f"{parsed['ap']}-*.md"))
        return candidates[0] if candidates else None
    # bare antipatterns/ or existing H-...: treat directory existence
    return SPEC_DIR / "antipatterns"


def parse_total(cell: str) -> tuple[int, int] | None:
    m = TOTAL_RE.search(cell)
    if not m:
        return None
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    return lo, hi


def main() -> int:
    if not AGENTS_PATH.exists():
        print(f"error: {AGENTS_PATH} not found", file=sys.stderr)
        return 2

    rows = find_routing_table(AGENTS_PATH.read_text())
    if len(rows) < 3:
        print("error: did not find a multi-row table under '## Context routing'")
        return 1

    # rows[0] header, rows[1] separator, rows[2:] data
    data_rows = rows[2:]
    errors: list[str] = []

    for row in data_rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) != 3:
            errors.append(f"row has {len(cells)} cells, expected 3: {row}")
            continue
        task, summand_cell, total_cell = cells
        summands = [s.strip() for s in summand_cell.split("+")]
        sum_min = 0
        sum_max = 0
        for raw in summands:
            parsed = parse_summand(raw)
            if parsed is None:
                errors.append(f"row '{task}': cannot parse summand '{raw}'")
                continue
            target = resolve_summand(parsed)
            if target is None or not target.exists():
                errors.append(
                    f"row '{task}': summand '{raw}' does not resolve to an "
                    "existing file"
                )
                continue
            tokens = parsed.get("tokens")
            tokens_max = parsed.get("tokens_max")
            if isinstance(tokens, str) and tokens.isdigit():
                lo = int(tokens)
                hi = (
                    int(tokens_max)
                    if isinstance(tokens_max, str) and tokens_max.isdigit()
                    else lo
                )
                sum_min += lo
                sum_max += hi
                if (parsed.get("n") or parsed.get("name")) and lo == hi:
                    data, _, _ = parse_frontmatter(target)
                    if data and isinstance(data.get("tokens"), int):
                        declared = data["tokens"]
                        if declared:
                            ratio = abs(lo - declared) / declared
                            if ratio > ARITHMETIC_TOLERANCE:
                                errors.append(
                                    f"row '{task}': summand '{raw}' parenthetical "
                                    f"{lo} differs from {target.name} "
                                    f"front-matter tokens={declared} (off by {ratio:.0%})"
                                )

        total = parse_total(total_cell)
        if total and sum_min > 0:
            lo, hi = total
            if not (
                sum_min * (1 - ARITHMETIC_TOLERANCE) <= hi
                and sum_max * (1 + ARITHMETIC_TOLERANCE) >= lo
            ):
                errors.append(
                    f"row '{task}': total cell '{total_cell}' does not match "
                    f"sum of summands ({sum_min}-{sum_max}) within "
                    f"±{ARITHMETIC_TOLERANCE:.0%}"
                )

    if errors:
        for err in errors:
            print(f"error: {err}")
        print(f"\n{len(errors)} error(s) over {len(data_rows)} rows")
        return 1
    print(f"agents routing OK: {len(data_rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())

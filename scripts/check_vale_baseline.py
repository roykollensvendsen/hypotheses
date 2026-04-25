# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Compare current Vale offence counts to `.vale/baseline.json`.

Vale prose linting is enforced via a *ratchet*. The baseline file
records, per file per rule, the number of pre-existing offences
that the maintainer has agreed to live with for now. CI fails if
any file:rule pair *increases*. Decreases are surfaced so the
baseline can be ratcheted down — the path to deletion is
"every cell goes to zero, then the baseline file goes away."

Why a baseline rather than a flat reformat:
- The spec is large (~30 docs, hand-curated prose). A one-shot
  rewrite would bury workflow review and impose stylistic calls
  the maintainer has not opted into.
- The Vale rules under `.vale/styles/AgentSpec/` are deliberately
  strict ("hedging", "weasel words", "quantifierless"); some
  pre-existing prose deliberately uses such language and needs a
  considered edit, not a global replace.

This script runs `vale --output=JSON` against the same paths the
`vale.yml` workflow scans, parses the JSON, and computes
per-file per-rule counts. It then diffs against
`.vale/baseline.json`. Nonzero exit on any increase.

Used by `.github/workflows/vale.yml`.

Exit codes:
    0 — no increases
    1 — at least one file:rule increased over baseline
    2 — internal error (vale missing, baseline missing, parse error)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASELINE_PATH = Path(".vale/baseline.json")
SCAN_TARGETS = ("docs/spec/", "VISION.md")


def run_vale() -> dict:
    if shutil.which("vale") is None:
        print("error: vale not on PATH", file=sys.stderr)
        sys.exit(2)
    proc = subprocess.run(
        ["vale", "--output=JSON", *SCAN_TARGETS],
        capture_output=True,
        text=True,
    )
    if not proc.stdout.strip():
        print(f"error: vale produced no output\n{proc.stderr}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"error: vale JSON parse failure: {exc}", file=sys.stderr)
        print(f"stderr: {proc.stderr}", file=sys.stderr)
        sys.exit(2)


def count_offences(vale_output: dict) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for path, alerts in vale_output.items():
        for alert in alerts:
            rule = alert.get("Check", "<unknown>")
            counts.setdefault(path, {}).setdefault(rule, 0)
            counts[path][rule] += 1
    return counts


def main() -> int:
    if not BASELINE_PATH.exists():
        print(f"error: baseline missing at {BASELINE_PATH}", file=sys.stderr)
        return 2
    baseline = json.loads(BASELINE_PATH.read_text())
    current = count_offences(run_vale())

    increases: list[str] = []
    decreases: list[str] = []
    for path in sorted(set(baseline) | set(current)):
        base_counts = baseline.get(path, {})
        cur_counts = current.get(path, {})
        for rule in sorted(set(base_counts) | set(cur_counts)):
            base = base_counts.get(rule, 0)
            cur = cur_counts.get(rule, 0)
            if cur > base:
                increases.append(f"{path}: {rule}: {base} -> {cur}")
            elif cur < base:
                decreases.append(f"{path}: {rule}: {base} -> {cur}")

    for d in decreases:
        print(f"info: improved (update baseline): {d}")
    if increases:
        for i in increases:
            print(f"error: regressed: {i}")
        print(
            f"\n{len(increases)} regression(s). Either fix the new offences "
            "or update .vale/baseline.json downward (regressions never raise "
            "the baseline — only fixes can lower it)."
        )
        return 1
    total = sum(sum(c.values()) for c in current.values())
    print(
        f"vale baseline OK: {total} total offence(s) within baseline "
        f"({len(decreases)} ratchet-down opportunity/ies)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

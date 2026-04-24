# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Verify SPDX license and copyright headers in source files.

Every tracked `.py` or `.sh` file under `src/`, `scripts/`, `tests/`,
or `experiments/` must carry both lines within the first 10 lines:

    SPDX-License-Identifier: AGPL-3.0-or-later
    SPDX-FileCopyrightText: <year> <holder>

Used by `.github/workflows/spdx.yml`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKED_SUFFIXES = (".py", ".sh")
CHECKED_ROOTS = ("src", "scripts", "tests", "experiments")
HEADER_LINE_LIMIT = 10
LICENSE_MARKER = "SPDX-License-Identifier: AGPL-3.0-or-later"
COPYRIGHT_MARKER = "SPDX-FileCopyrightText:"


def tracked_files() -> list[Path]:
    existing_roots = [r for r in CHECKED_ROOTS if Path(r).is_dir()]
    if not existing_roots:
        return []
    out = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            *existing_roots,
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [Path(line) for line in out.splitlines() if line.endswith(CHECKED_SUFFIXES)]


def check(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        head = "\n".join(
            path.read_text(encoding="utf-8").splitlines()[:HEADER_LINE_LIMIT]
        )
    except OSError as e:
        return [f"{path}: could not read ({e})"]
    if LICENSE_MARKER not in head:
        problems.append(
            f"{path}: missing '{LICENSE_MARKER}' in first {HEADER_LINE_LIMIT} lines"
        )
    if COPYRIGHT_MARKER not in head:
        problems.append(
            f"{path}: missing '{COPYRIGHT_MARKER} <year> <holder>' in first {HEADER_LINE_LIMIT} lines"
        )
    return problems


def main() -> int:
    files = tracked_files()
    errors: list[str] = []
    for path in files:
        errors.extend(check(path))
    if errors:
        for e in errors:
            print(f"::error::{e}")
        print(
            f"\n{len(errors)} SPDX header violation(s). See docs/spec/15-ci-cd.md#license-marking.",
            file=sys.stderr,
        )
        return 1
    print(f"All {len(files)} source files carry SPDX headers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Require an ADR file when pinned toolchain or deps change.

A PR that modifies `pyproject.toml` or `uv.lock` must include a new
file under `docs/adr/` capturing the decision. Used by
`.github/workflows/adr-required.yml`.
"""

from __future__ import annotations

import subprocess
import sys

TRIGGERING_PATHS = (
    "pyproject.toml",
    "uv.lock",
)


def changed_files(base: str, head: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def added_files(base: str, head: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: check_adr_required.py <base> <head>", file=sys.stderr)
        return 2
    base, head = argv[1], argv[2]

    changed = changed_files(base, head)
    triggering = [f for f in changed if f in TRIGGERING_PATHS]
    if not triggering:
        print("no triggering paths changed; ADR not required")
        return 0

    added = added_files(base, head)
    new_adrs = [f for f in added if f.startswith("docs/adr/") and f.endswith(".md")]
    if not new_adrs:
        print(
            f"::error::PR changes {triggering} without adding a new "
            f"docs/adr/*.md file. Capture the decision in an ADR."
        )
        return 1

    print(f"ADR requirement satisfied by: {new_adrs}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

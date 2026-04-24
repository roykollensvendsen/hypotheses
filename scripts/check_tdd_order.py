# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Check that tests precede implementation in a PR's commit range.

Walks commits in `<base>..<head>` oldest-first. For every commit whose
conventional-commit type is `feat` or `fix` and which touches any path
under `src/`, there must have been at least one earlier `test:` commit
in the same range. Used by `.github/workflows/tdd-gate.yml`.

Exit codes:
    0 — no violations (or no `src/` touched in the range)
    1 — one or more violations
    2 — internal error
"""

from __future__ import annotations

import re
import subprocess
import sys

TYPE_RE = re.compile(r"^([a-z]+)(\([^)]+\))?!?: ")
EXEMPT_TYPES = frozenset(
    {"docs", "chore", "style", "ci", "build", "perf", "revert", "refactor"}
)


def commits_in_range(base: str, head: str) -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "log", "--reverse", "--format=%H%x09%s", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not out:
        return []
    commits: list[tuple[str, str]] = []
    for line in out.splitlines():
        sha, _, subject = line.partition("\t")
        commits.append((sha, subject))
    return commits


def files_in_commit(sha: str) -> list[str]:
    out = subprocess.run(
        ["git", "show", "--name-only", "--format=", sha],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def touches_src(files: list[str]) -> bool:
    return any(f.startswith("src/") for f in files)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: check_tdd_order.py <base-ref> <head-ref>", file=sys.stderr)
        return 2
    base, head = argv[1], argv[2]

    commits = commits_in_range(base, head)
    if not commits:
        print("no commits in range; skipping TDD check")
        return 0

    test_seen = False
    violations: list[str] = []

    for sha, subject in commits:
        match = TYPE_RE.match(subject)
        if not match:
            continue
        ctype = match.group(1)
        if ctype == "test":
            test_seen = True
            continue
        if ctype in EXEMPT_TYPES:
            continue
        if ctype in ("feat", "fix"):
            files = files_in_commit(sha)
            if touches_src(files) and not test_seen:
                violations.append(
                    f"commit {sha[:7]} ({ctype}: ...) touches src/ "
                    f"without a preceding test: commit in this PR range"
                )

    if violations:
        for v in violations:
            print(f"::error::{v}")
        print(
            "\nTDD violation: write failing tests in a test: commit "
            "before implementing them in a feat:/fix: commit. See "
            "docs/spec/12-implementation-constraints.md.",
            file=sys.stderr,
        )
        return 1

    print("TDD check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

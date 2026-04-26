# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Spec-doc staleness signal.

For every spec doc the script:

1. Reads `last_updated:` from front-matter (optional).
2. Reads the actual last commit date from `git log`.
3. If `last_updated:` is present, asserts it matches git within
   ±1 day (drift fails).
4. Surfaces *relational* staleness: when a doc has not moved in
   ``STALE_DAYS`` (default 90) days but a doc it depends on (or
   that depends on it) was touched in the last
   ``RECENT_DAYS`` (default 30) days, the older doc is reported
   as potentially out of sync with its neighbours.

Output is informational by default — the script exits 0 unless
a declared `last_updated:` value disagrees with git or git is
unavailable. Relational staleness produces warnings the
maintainer can review; this is a signal, not a gate.

Modes:
  default       — report and exit
  --update      — overwrite each spec doc's `last_updated:` with
                  its git last-modified date (commits a single
                  edit per file). Useful for the initial backfill
                  or after a batch refactor.

Used by `.github/workflows/staleness.yml` (weekly schedule, posts
the report to the job summary).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import yaml

STALE_DAYS = 90
RECENT_DAYS = 30
DRIFT_TOLERANCE = dt.timedelta(days=1)

SCAN_GLOBS: tuple[str, ...] = (
    "docs/spec/*.md",
    "docs/spec/formal/*.md",
    "docs/adr/*.md",
)
EXCLUDE_DIRS: frozenset[str] = frozenset({"antipatterns", "_schemas"})

FRONT_MATTER_RE = re.compile(r"\A(---\n)(.*?)(\n---\n?)", re.DOTALL)
LAST_UPDATED_RE = re.compile(r"^last_updated:.*$", re.MULTILINE)


def iter_targets() -> list[Path]:
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


def git_last_modified(path: Path) -> dt.date | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not out:
        return None
    try:
        return dt.datetime.fromisoformat(out).date()
    except ValueError:
        return None


def parse_frontmatter(path: Path) -> tuple[dict, str, str] | None:
    text = path.read_text()
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(2)) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    body = text[m.end() :]
    return data, m.group(2), body


def write_last_updated(path: Path, new_date: dt.date) -> None:
    text = path.read_text()
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return
    yaml_block = m.group(2)
    new_line = f"last_updated: {new_date.isoformat()}"
    if LAST_UPDATED_RE.search(yaml_block):
        new_block = LAST_UPDATED_RE.sub(new_line, yaml_block, count=1)
    else:
        new_block = yaml_block.rstrip() + "\n" + new_line
    path.write_text(text[: m.start(2)] + new_block + text[m.end(2) :])


def collect_depends_on(data: dict) -> set[str]:
    deps = data.get("depends_on") or []
    return {str(d) for d in deps}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update",
        action="store_true",
        help="overwrite last_updated: with each file's git last-modified date",
    )
    args = parser.parse_args()

    today = dt.date.today()
    targets = iter_targets()
    if not targets:
        print("error: no targets matched scan globs", file=sys.stderr)
        return 2

    info: dict[Path, tuple[dt.date | None, dt.date | None]] = {}
    declared_drift: list[str] = []
    git_unavailable: list[Path] = []

    for path in targets:
        parsed = parse_frontmatter(path)
        if parsed is None:
            continue
        data, _yaml, _body = parsed
        declared_raw = data.get("last_updated")
        declared = (
            dt.date.fromisoformat(declared_raw)
            if isinstance(declared_raw, str)
            else None
        )
        git_date = git_last_modified(path)
        if git_date is None:
            git_unavailable.append(path)
        info[path] = (declared, git_date)

        if args.update and git_date is not None:
            if declared != git_date:
                write_last_updated(path, git_date)
                print(f"updated {path}: last_updated -> {git_date.isoformat()}")
            continue

        if declared is not None and git_date is not None:
            if abs((declared - git_date).days) > DRIFT_TOLERANCE.days:
                declared_drift.append(
                    f"{path}: last_updated={declared} disagrees with git "
                    f"last-modified={git_date} (drift "
                    f"{(declared - git_date).days:+d} days)"
                )

    if args.update:
        return 0

    # Relational staleness: a stale doc whose neighbour just moved.
    stale_warnings: list[str] = []
    by_dep_token: dict[str, Path] = {}
    for path in info:
        m = re.match(r"docs/spec/(\d{2}(?:\.\d+)?)-", str(path))
        if m:
            by_dep_token[m.group(1)] = path

    for path, (_decl, git_date) in info.items():
        if git_date is None:
            continue
        age = (today - git_date).days
        if age < STALE_DAYS:
            continue
        parsed = parse_frontmatter(path)
        if parsed is None:
            continue
        data, _, _ = parsed
        deps = collect_depends_on(data)
        for dep in deps:
            target = by_dep_token.get(dep)
            if target is None:
                continue
            _, dep_date = info.get(target, (None, None))
            if dep_date is None:
                continue
            if (today - dep_date).days <= RECENT_DAYS:
                stale_warnings.append(
                    f"{path}: stale ({age} days since last touch); depends on "
                    f"{target.name} which moved {(today - dep_date).days} day(s) ago"
                )

    if declared_drift:
        for d in declared_drift:
            print(f"error: {d}")
    if stale_warnings:
        for w in stale_warnings:
            print(f"warning: {w}")
    if git_unavailable:
        for p in git_unavailable:
            print(f"info: git log unavailable for {p}")
    if declared_drift:
        print(
            f"\n{len(declared_drift)} declared-vs-git drift error(s). "
            "Either update the file's last_updated: field or run "
            "`python3 scripts/check_staleness.py --update`."
        )
        return 1
    print(
        f"staleness OK: {len(info)} doc(s) inspected, "
        f"{len(stale_warnings)} relational warning(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

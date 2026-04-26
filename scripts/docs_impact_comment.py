# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Spec-doc impact analysis for a pull request.

Produces a four-section markdown report given a base ref and a
head ref:

1. **HM-REQ/HM-INV IDs added/removed** — block-quoted definitions
   (`**HM-REQ-NNNN**`) that appear in head but not base, and vice
   versa.
2. **Reverse `depends_on`** — for each touched
   `docs/spec/NN-*.md`, the set of other spec docs that declare
   it in their `depends_on:` front-matter.
3. **Role-prompt references** — each `agents/prompts/*-system.md`
   that mentions the touched spec doc by relative path.
4. **load_for budget shifts** — `load_for:` tags whose summed
   token totals change between base and head.

Output is markdown on stdout. The wrapper workflow
`docs-impact.yml` captures it and posts to the GitHub Actions
job summary.

Usage:
    python3 scripts/docs_impact_comment.py <base-ref> <head-ref>

Examples:
    # CI: compare PR head to its base
    python3 scripts/docs_impact_comment.py origin/main HEAD

    # Local: any commit pair
    python3 scripts/docs_impact_comment.py main mybranch~3
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
TAG_DEFINE_RE = re.compile(r"\*\*(HM-(?:REQ|INV)-\d{4})\*\*")
SPEC_GLOB_PREFIX = "docs/spec/"


def git_show(ref: str, path: str) -> str | None:
    """Return file contents at ref, or None if absent."""
    try:
        return subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None


def changed_files(base: str, head: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return sorted(line for line in out.splitlines() if line)


def parse_frontmatter(text: str | None) -> dict | None:
    if text is None:
        return None
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def extract_tag_defines(text: str | None) -> set[str]:
    if text is None:
        return set()
    return set(TAG_DEFINE_RE.findall(text))


def reverse_depends_on(ref: str) -> dict[str, list[str]]:
    """Map ``NN`` → list of paths whose front-matter depends_on includes it."""
    out: dict[str, list[str]] = defaultdict(list)
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "docs/spec/"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for path in listing.splitlines():
        if not path.endswith(".md"):
            continue
        data = parse_frontmatter(git_show(ref, path))
        if not data:
            continue
        for dep in data.get("depends_on") or []:
            token = (
                f"{int(dep):02d}"
                if isinstance(dep, int)
                else f"{int(dep):02d}.5"
                if isinstance(dep, float) and abs(dep - int(dep) - 0.5) < 1e-9
                else str(dep)
            )
            out[token].append(path)
    return out


def numeric_token(path: str) -> str | None:
    m = re.match(r"docs/spec/(\d{2}(?:\.\d+)?)-", path)
    return m.group(1) if m else None


def role_prompt_refs(touched: list[str]) -> dict[str, list[str]]:
    """For each touched spec path, list role-prompt files that reference it."""
    out: dict[str, list[str]] = defaultdict(list)
    for prompt in sorted(Path("agents/prompts").glob("*-system.md")):
        text = prompt.read_text()
        for path in touched:
            if path in text:
                out[path].append(str(prompt))
    return out


def load_for_totals(ref: str) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "docs/spec/"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for path in listing.splitlines():
        if not path.endswith(".md") or "antipatterns" in path or "_schemas" in path:
            continue
        data = parse_frontmatter(git_show(ref, path))
        if not data:
            continue
        tokens = data.get("tokens") or 0
        for tag in data.get("load_for") or []:
            totals[str(tag)] += tokens if isinstance(tokens, int) else 0
    return totals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", help="base git ref (e.g. origin/main)")
    parser.add_argument("head", help="head git ref (e.g. HEAD)")
    args = parser.parse_args()

    files = changed_files(args.base, args.head)
    spec_files = [f for f in files if f.startswith(SPEC_GLOB_PREFIX)]

    print("# Spec impact")
    print()
    if not spec_files:
        print(
            f"No `{SPEC_GLOB_PREFIX}` files changed between `{args.base}` and `{args.head}`."
        )
        return 0
    print(
        f"Comparing `{args.base}` ↦ `{args.head}`. {len(spec_files)} spec doc(s) touched."
    )

    print("\n## HM-REQ / HM-INV IDs added or removed\n")
    any_change = False
    for path in spec_files:
        base_tags = extract_tag_defines(git_show(args.base, path))
        head_tags = extract_tag_defines(git_show(args.head, path))
        added = sorted(head_tags - base_tags)
        removed = sorted(base_tags - head_tags)
        if added or removed:
            any_change = True
            print(f"- `{path}`:")
            for t in added:
                print(f"  - **+{t}**")
            for t in removed:
                print(f"  - **−{t}**")
    if not any_change:
        print("(none)")

    print("\n## Reverse `depends_on` — docs that load these\n")
    reverse = reverse_depends_on(args.head)
    any_dep = False
    for path in spec_files:
        token = numeric_token(path)
        if token is None:
            continue
        consumers = reverse.get(token, [])
        if consumers:
            any_dep = True
            print(f"- `{path}` is loaded by:")
            for c in consumers:
                print(f"  - `{c}`")
    if not any_dep:
        print("(none — touched docs are leaves of the depends_on graph)")

    print("\n## Role-prompt references\n")
    refs = role_prompt_refs(spec_files)
    if not refs:
        print("(none — no `agents/prompts/*-system.md` references the touched paths)")
    else:
        for path, prompts in refs.items():
            print(f"- `{path}` referenced by:")
            for p in prompts:
                print(f"  - `{p}`")

    print("\n## `load_for` budget shifts\n")
    base_totals = load_for_totals(args.base)
    head_totals = load_for_totals(args.head)
    any_shift = False
    for tag in sorted(set(base_totals) | set(head_totals)):
        b = base_totals.get(tag, 0)
        h = head_totals.get(tag, 0)
        if b != h:
            any_shift = True
            delta = h - b
            sign = "+" if delta > 0 else ""
            print(f"- `{tag}`: {b} → {h} ({sign}{delta})")
    if not any_shift:
        print("(none — total tokens per `load_for` tag unchanged)")

    return 0


if __name__ == "__main__":
    sys.exit(main())

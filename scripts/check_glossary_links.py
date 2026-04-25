# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Glossary-link discipline ratchet.

For every term defined in `docs/spec/01-glossary.md` (parsed live
from the `## Terms` section's `###`-headings), checks every other
prose doc under `docs/spec/` for a *first plain-text mention* of
that term. The first mention should be a markdown link — to the
glossary anchor, or to a more specific canonical home (e.g.,
`oracle` first-mentioned in a doc about scoring may legitimately
link to `18-oracle.md` instead of the glossary entry).

The check uses a per-doc per-term baseline file
(`.vale/glossary-baseline.json`) for ratchet semantics: the
current state is captured as the floor, new violations fail,
fewer violations on a future run signal the baseline can be
ratcheted down. Identical structure to the Vale baseline added
in PR-5.

Used by `.github/workflows/glossary-links.yml`. Treat as
warning-level discipline rather than strict spec rule — the
baseline absorbs every existing offence on first roll-out.

Exit codes:
    0 — no regressions vs baseline (also emits info: lines for
        decreases the baseline can be ratcheted down to)
    1 — at least one (doc, term) pair regressed
    2 — internal error (glossary missing, baseline parse error)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GLOSSARY_PATH = Path("docs/spec/01-glossary.md")
BASELINE_PATH = Path(".vale/glossary-baseline.json")
SCAN_GLOB = "docs/spec/*.md"
EXCLUDE_NAMES: frozenset[str] = frozenset(
    {
        "01-glossary.md",
        "_schemas",
    }
)
EXCLUDE_DIRS: frozenset[str] = frozenset({"antipatterns", "formal", "_schemas"})

FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---\n?", re.DOTALL)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
TERM_HEADING_RE = re.compile(r"^### (.+?)\s*$", re.MULTILINE)


def slugify(heading: str) -> str:
    """Best-effort match for GitHub's heading anchor slugs."""
    s = heading.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def parse_glossary_terms() -> dict[str, str]:
    """Return ``{term_text: anchor_slug}`` from the `## Terms` section."""
    text = GLOSSARY_PATH.read_text()
    terms: dict[str, str] = {}
    in_terms = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_terms = line.strip() == "## Terms"
            continue
        if in_terms:
            m = re.match(r"^### (.+?)\s*$", line)
            if m:
                term = m.group(1).strip()
                terms[term] = slugify(term)
    return terms


def strip_noise(text: str) -> str:
    """Remove front-matter, fenced/inline code, and heading lines."""
    text = FRONT_MATTER_RE.sub("", text, count=1)
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def link_text_spans(body: str) -> list[tuple[int, int]]:
    return [(m.start(1), m.end(1)) for m in LINK_RE.finditer(body)]


def first_unlinked_mention(body: str, term: str) -> bool:
    """Return True iff the first occurrence of *term* is not inside a link."""
    pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
    spans = link_text_spans(body)
    for m in pattern.finditer(body):
        pos = m.start()
        if any(s <= pos < e for s, e in spans):
            return False  # first mention IS linked
        return True  # first mention is plain text
    return False  # term not present at all


def iter_targets() -> list[Path]:
    out: list[Path] = []
    for p in sorted(Path().glob(SCAN_GLOB)):
        if p.name in EXCLUDE_NAMES:
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def main() -> int:
    if not GLOSSARY_PATH.exists():
        print(f"error: glossary missing at {GLOSSARY_PATH}", file=sys.stderr)
        return 2
    terms = parse_glossary_terms()
    if not terms:
        print(
            f"error: no terms parsed from {GLOSSARY_PATH} '## Terms' section",
            file=sys.stderr,
        )
        return 2

    baseline: dict[str, dict[str, int]] = (
        json.loads(BASELINE_PATH.read_text()) if BASELINE_PATH.exists() else {}
    )

    current: dict[str, dict[str, int]] = {}
    for path in iter_targets():
        body = strip_noise(path.read_text())
        per_term: dict[str, int] = {}
        for term in terms:
            if first_unlinked_mention(body, term):
                per_term[term] = per_term.get(term, 0) + 1
        if per_term:
            current[str(path)] = per_term

    increases: list[str] = []
    decreases: list[str] = []
    for path in sorted(set(baseline) | set(current)):
        base = baseline.get(path, {})
        cur = current.get(path, {})
        for term in sorted(set(base) | set(cur)):
            b = base.get(term, 0)
            c = cur.get(term, 0)
            if c > b:
                increases.append(f"{path}: {term!r}: {b} -> {c}")
            elif c < b:
                decreases.append(f"{path}: {term!r}: {b} -> {c}")

    for d in decreases:
        print(f"info: improved (update baseline): {d}")
    if increases:
        for i in increases:
            print(f"error: regressed: {i}")
        print(
            f"\n{len(increases)} regression(s). Either link the new mention "
            "or update .vale/glossary-baseline.json downward (regressions "
            "never raise the baseline — only fixes lower it)."
        )
        return 1
    total = sum(sum(v.values()) for v in current.values())
    print(
        f"glossary-links OK: {total} unlinked first-mention(s) within "
        f"baseline ({len(decreases)} ratchet-down opportunity/ies)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

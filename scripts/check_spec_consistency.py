# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Cross-reference consistency checker.

Two orthogonal checks run against every `.md` file under
`docs/spec/`, plus `VISION.md`, `AGENTS.md`, and `CONTRIBUTING.md`:

**1. Cross-reference integrity.** Every in-prose reference to an
opaque identifier (`HM-REQ-NNNN`, `HM-INV-NNNN`, `T-NNN`, `T-P<k>-NNN`,
`T-ACC`, `T-SUP`, `T-REF`, `T-RUN`, `T-VER`, `T-WDP`, `T-WDA`,
`T-PROP`, `T-WITH`) MUST resolve to a definition somewhere in the
scanned tree. An unresolved reference is either a typo or a lie.

**2. Canonical constants.** A marker of the form
`<!-- canonical:KEY=VALUE -->` anywhere in the tree pins a
spec-wide constant. Every other inline mention of `KEY` that ships
with a colon-separated value is cross-checked: a different value
raises an error, so a prose edit that inadvertently drops a
`rerun_fraction=0.4` next to `rerun_fraction=0.5` in another doc
fails CI.

Used by `.github/workflows/spec-consistency.yml`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCAN_TARGETS: tuple[Path, ...] = (
    Path("VISION.md"),
    Path("AGENTS.md"),
    Path("CONTRIBUTING.md"),
    Path("docs/spec"),
    Path("docs/tasks"),
)

# Opaque IDs we expect to resolve. Each entry is (name, regex). The
# regexes intentionally match the *whole* token (word boundaries) so
# they don't catch substrings.
ID_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("HM-REQ", re.compile(r"\bHM-REQ-\d{4}\b")),
    ("HM-INV", re.compile(r"\bHM-INV-\d{4}\b")),
    ("T-threat", re.compile(r"\bT-\d{3}\b")),
    ("T-phase-task", re.compile(r"\bT-P\d-\d{3}\b")),
    ("T-lifecycle", re.compile(r"\bT-(?:ACC|SUP|REF|RUN|VER|WDP|WDA|PROP|WITH)\b")),
    ("AP", re.compile(r"\bAP-\d{4}\b")),
)

DEF_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # HM-REQ / HM-INV: defined inline with bold wrappers or indexed
    # in a table row. We accept either.
    ("HM-REQ", re.compile(r"(\*\*HM-REQ-\d{4}\*\*|\|\s*HM-REQ-\d{4}\b)")),
    ("HM-INV", re.compile(r"(\*\*HM-INV-\d{4}\*\*|\|\s*HM-INV-\d{4}\b)")),
    # T-threat: defined in the threat model tables.
    ("T-threat", re.compile(r"\|\s*T-\d{3}\b")),
    # Phase-task IDs: defined as YAML `id: T-P<k>-NNN` or inline.
    ("T-phase-task", re.compile(r"(^\s*-\s*id:\s*T-P\d-\d{3}\b|T-P\d-\d{3}\b)")),
    # Lifecycle transition IDs: defined in bold header form.
    ("T-lifecycle", re.compile(r"\*\*T-(?:ACC|SUP|REF|RUN|VER|WDP|WDA|PROP|WITH)\*\*")),
    # Antipatterns: defined as a heading `# AP-NNNN`.
    ("AP", re.compile(r"^#\s+AP-\d{4}\b", re.MULTILINE)),
)

CANONICAL_RE = re.compile(r"<!--\s*canonical:([A-Za-z_][\w.]*)=([^\s-][^>]*?)\s*-->")


def iter_scan_files() -> list[Path]:
    out: list[Path] = []
    for t in SCAN_TARGETS:
        if not t.exists():
            continue
        if t.is_file() and t.suffix == ".md":
            out.append(t)
        elif t.is_dir():
            for p in t.rglob("*.md"):
                out.append(p)
            for p in t.rglob("*.yml"):
                out.append(p)
    return sorted(set(out))


def collect_definitions(files: list[Path]) -> dict[str, set[str]]:
    """Return {kind: set(id)} of every ID that is *defined* in the tree."""
    defs: dict[str, set[str]] = {kind: set() for kind, _ in ID_PATTERNS}
    token_re: dict[str, re.Pattern[str]] = {kind: pat for kind, pat in ID_PATTERNS}
    for path in files:
        text = path.read_text(encoding="utf-8")
        for kind, def_pat in DEF_MARKERS:
            for m in def_pat.finditer(text):
                for tok_match in token_re[kind].finditer(m.group(0)):
                    defs[kind].add(tok_match.group(0))
    return defs


def collect_references(
    files: list[Path],
) -> dict[str, dict[str, list[tuple[Path, int]]]]:
    """Return {kind: {id: [(path, line_no), ...]}}."""
    refs: dict[str, dict[str, list[tuple[Path, int]]]] = {
        kind: {} for kind, _ in ID_PATTERNS
    }
    for path in files:
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for kind, pat in ID_PATTERNS:
                for m in pat.finditer(line):
                    refs[kind].setdefault(m.group(0), []).append((path, lineno))
    return refs


def canonical_constants(files: list[Path]) -> dict[str, tuple[str, Path, int]]:
    """Return {key: (value, origin-path, line_no)} for every marker."""
    pins: dict[str, tuple[str, Path, int]] = {}
    errors: list[str] = []
    for path in files:
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for m in CANONICAL_RE.finditer(line):
                key, val = m.group(1), m.group(2).strip()
                if key in pins and pins[key][0] != val:
                    prev_val, prev_path, prev_line = pins[key]
                    errors.append(
                        f"::error file={path},line={lineno}::"
                        f"canonical constant '{key}' has conflicting pins: "
                        f"'{val}' here, '{prev_val}' in {prev_path}:{prev_line}."
                    )
                else:
                    pins[key] = (val, path, lineno)
    if errors:
        for e in errors:
            print(e)
    return pins


def check_canonical_usage(
    files: list[Path], pins: dict[str, tuple[str, Path, int]]
) -> list[str]:
    """Scan prose for mentions of `KEY = VALUE` or `KEY=VALUE` whose VALUE
    disagrees with the canonical pin. Only flags exact token matches.
    """
    errors: list[str] = []
    for key, (pinned_val, origin_path, _) in pins.items():
        # Capture the value token up to whitespace, a closing paren, a
        # trailing comma/semicolon, or a trailing period that is NOT
        # followed by a digit (so "0.4" reads intact, but "0.4." at
        # the end of a sentence strips the final period).
        usage_re = re.compile(
            rf"\b{re.escape(key)}\s*[=:]\s*(\S+?)(?=[\s),;`]|\.(?!\d)|$)"
        )
        for path in files:
            if path == origin_path:
                continue
            if path.name == "check_spec_consistency.py":
                continue
            for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if "canonical:" in line:
                    continue
                for m in usage_re.finditer(line):
                    raw = m.group(1).rstrip(",.;:)")
                    if raw != pinned_val:
                        errors.append(
                            f"::error file={path},line={lineno}::"
                            f"'{key}' is mentioned with value '{raw}', but the "
                            f"canonical pin in {origin_path} is '{pinned_val}'."
                        )
    return errors


def main() -> int:
    files = iter_scan_files()
    refs = collect_references(files)
    defs = collect_definitions(files)

    errors: list[str] = []

    for kind, ids_seen in refs.items():
        known = defs.get(kind, set())
        for tok, sites in ids_seen.items():
            if tok in known:
                continue
            for path, lineno in sites[:5]:  # cap to 5 per undefined id
                errors.append(
                    f"::error file={path},line={lineno}::"
                    f"reference to '{tok}' ({kind}) has no definition in the spec tree."
                )

    pins = canonical_constants(files)
    errors.extend(check_canonical_usage(files, pins))

    for e in errors:
        print(e)

    if errors:
        print(
            f"\n{len(errors)} spec-consistency violation(s). "
            f"See docs/spec/15-ci-cd.md.",
            file=sys.stderr,
        )
        return 1

    totals = ", ".join(f"{k}={len(v)}" for k, v in defs.items())
    print(
        f"Spec consistency OK. Defined IDs: {totals}. Canonical constants: {len(pins)}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

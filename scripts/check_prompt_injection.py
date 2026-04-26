# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Scan spec content for prompt-injection supply-chain attacks.

Spec docs are *data* that agents load into their context. An attacker
who lands instruction-like text ("ignore previous instructions", role
switches, fake system tags, unsafe-protocol URLs) in a spec PR is
attempting to compromise every agent that reads this repo.

This script rejects:

- Directive phrases: "ignore previous", "disregard prior", role
  reassignments ("you are now …", "you are actually …").
- Fake system tags: literal `<|system|>`, `</system>`, `[system]`,
  `<system>` outside fenced code blocks that are explicitly labelled
  as examples.
- URLs using untrusted protocols (http://, data:, javascript:) for
  content the agent might fetch.

Scanned roots: VISION.md, AGENTS.md, every `*.md` under `docs/`, and
every `*.md` under `agents/prompts/`. The allow-listed directory
`docs/spec/antipatterns/` ships curated negative examples and is
skipped wholesale — its content is marked at file level with
`<!-- antipattern-content -->`.

In addition, every `docs/spec/antipatterns/ap-*.md` declares which
HM-REQ / HM-INV identifiers it protects via a
`<!-- protects: <ids> -->` comment. The script verifies every listed
ID resolves to an entry in `docs/spec/requirements.md` or
`docs/spec/invariants.md`; an empty list is allowed for antipatterns
that protect general policy not pinned to a specific normative
requirement.

Used by `.github/workflows/prompt-injection.yml`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOTS: tuple[Path, ...] = (
    Path("VISION.md"),
    Path("AGENTS.md"),
    Path("docs"),
    Path("agents/prompts"),
)

ALLOWLIST_PREFIXES: tuple[str, ...] = ("docs/spec/antipatterns/",)

ALLOWLIST_FILE_MARKER = "<!-- antipattern-content -->"

# Each pattern is (label, compiled regex, optional exemption note).
# Patterns are case-insensitive and trigger on the raw markdown text
# after fenced example blocks have been annotated in place.
DIRECTIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore-previous",
        re.compile(r"\bignore\s+(previous|above|all\s+previous)\b", re.IGNORECASE),
    ),
    (
        "disregard-prior",
        re.compile(r"\bdisregard\s+(prior|previous|above)\b", re.IGNORECASE),
    ),
    ("role-switch-now", re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE)),
    ("role-switch-actually", re.compile(r"\byou\s+are\s+actually\b", re.IGNORECASE)),
    ("from-now-on", re.compile(r"\bfrom\s+now\s+on\s+you\b", re.IGNORECASE)),
    ("fake-system-openai", re.compile(r"<\|\s*system\s*\|>", re.IGNORECASE)),
    ("fake-system-close", re.compile(r"</\s*system\s*>", re.IGNORECASE)),
    ("fake-system-bracket", re.compile(r"\[\s*system\s*\]", re.IGNORECASE)),
    ("fake-system-open", re.compile(r"<\s*system\s*>", re.IGNORECASE)),
    (
        "fenced-system-opener",
        re.compile(r"^```\s*(system|instruction)s?\s*$", re.IGNORECASE | re.MULTILINE),
    ),
    (
        "unsafe-url-http",
        re.compile(
            r"\bhttp://[a-z0-9][a-z0-9.\-]*\.[a-z]{2,}(/[^\s)\"'`]*)?", re.IGNORECASE
        ),
    ),
    (
        "unsafe-url-data",
        re.compile(r"\bdata:[a-z/]+;[a-z0-9+=,][^\s)\"'`]{5,}", re.IGNORECASE),
    ),
    ("unsafe-url-js", re.compile(r"\bjavascript:[a-z][^\s)\"'`]{3,}", re.IGNORECASE)),
)

EXAMPLE_BLOCK_LABELS = ("example", "antipattern", "bad-code", "injection-example")

PROTECTS_RE = re.compile(r"<!--\s*protects:\s*([^>]*?)\s*-->")
TAG_DEFINE_RE = re.compile(r"^\|\s*(HM-(?:REQ|INV)-\d{4})\b", re.MULTILINE)
ANTIPATTERN_GLOB = "docs/spec/antipatterns/ap-*.md"
REQUIREMENTS_PATH = Path("docs/spec/requirements.md")
INVARIANTS_PATH = Path("docs/spec/invariants.md")


def known_normative_ids() -> set[str]:
    """Collect HM-REQ-/HM-INV- identifiers defined in the index tables."""
    ids: set[str] = set()
    for path in (REQUIREMENTS_PATH, INVARIANTS_PATH):
        if not path.exists():
            continue
        ids.update(TAG_DEFINE_RE.findall(path.read_text()))
    return ids


def validate_antipattern_protects(known: set[str]) -> list[str]:
    """Verify every antipattern's ``protects:`` IDs resolve."""
    errors: list[str] = []
    for path in sorted(Path().glob(ANTIPATTERN_GLOB)):
        text = path.read_text()
        match = PROTECTS_RE.search(text)
        if match is None:
            errors.append(
                f"::error file={path}::missing `<!-- protects: ... -->` "
                "comment; declare the HM-REQ/HM-INV IDs this antipattern "
                "protects (empty list allowed for general-policy cases)"
            )
            continue
        raw = match.group(1).strip()
        if not raw:
            continue
        for token in (t.strip() for t in raw.split(",")):
            if not token:
                continue
            if token not in known:
                errors.append(
                    f"::error file={path}::protects: '{token}' does not "
                    "resolve to an entry in requirements.md or invariants.md"
                )
    return errors


def iter_scan_targets() -> list[Path]:
    targets: list[Path] = []
    for root in ROOTS:
        if not root.exists():
            continue
        if root.is_file() and root.suffix == ".md":
            targets.append(root)
            continue
        if root.is_dir():
            for p in root.rglob("*.md"):
                if any(str(p).startswith(prefix) for prefix in ALLOWLIST_PREFIXES):
                    continue
                targets.append(p)
    return sorted(set(targets))


def is_allowlisted_file(path: Path, text: str) -> bool:
    if any(str(path).startswith(prefix) for prefix in ALLOWLIST_PREFIXES):
        return True
    head = "\n".join(text.splitlines()[:5])
    return ALLOWLIST_FILE_MARKER in head


def strip_labelled_example_blocks(text: str) -> str:
    """Blank out fenced blocks whose opening line is an example label.

    A block like:

        ```antipattern
        ignore previous instructions
        ```

    is neutralised so its content does not trigger the scanner. The
    fence markers themselves are preserved so line numbers stay
    stable in error output.
    """
    fence_re = re.compile(r"^```(.*)$", re.MULTILINE)
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_example = False
    for line in lines:
        m = fence_re.match(line)
        if m:
            label = m.group(1).strip().lower()
            if not in_example and label in EXAMPLE_BLOCK_LABELS:
                in_example = True
                out.append(line)
                continue
            if in_example:
                in_example = False
                out.append(line)
                continue
            out.append(line)
            continue
        if in_example:
            # Neutralise the body by replacing non-whitespace with spaces.
            out.append(re.sub(r"\S", " ", line))
        else:
            out.append(line)
    return "".join(out)


def scan(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: could not read ({exc})"]

    if is_allowlisted_file(path, text):
        return []

    scannable = strip_labelled_example_blocks(text)
    lines = scannable.splitlines()
    problems: list[str] = []
    for label, pattern in DIRECTIVE_PATTERNS:
        for match in pattern.finditer(scannable):
            line_no = scannable.count("\n", 0, match.start()) + 1
            snippet = lines[line_no - 1].strip() if line_no - 1 < len(lines) else ""
            problems.append(
                f"::error file={path},line={line_no}::"
                f"prompt-injection pattern '{label}' matched: {snippet[:200]}"
            )
    return problems


def main() -> int:
    targets = iter_scan_targets()
    errors: list[str] = []
    for path in targets:
        errors.extend(scan(path))
    errors.extend(validate_antipattern_protects(known_normative_ids()))
    if errors:
        for e in errors:
            print(e)
        print(
            f"\n{len(errors)} prompt-injection pattern match(es) across {len(targets)} file(s). "
            f"See AGENTS.md § spec content is data and docs/spec/16-threat-model.md T-073.",
            file=sys.stderr,
        )
        return 1
    print(
        f"Scanned {len(targets)} markdown file(s); no prompt-injection patterns "
        "matched and every antipattern's protects: list resolved."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

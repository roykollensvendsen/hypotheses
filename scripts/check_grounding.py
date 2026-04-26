# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Grounding-discipline gate.

Enforces the conventions defined in
`docs/spec/25-rigor-framework.md`:

1. **Reference resolution (strict).** Every ``{ref:slug}`` (brace
   form) or ``[^slug]`` (footnote form, excluding definitions
   ``[^slug]:``) appearing in a spec or ADR doc resolves to a row
   in ``docs/spec/references.md``. Any unresolved reference is an
   error.

2. **Evidence-field coverage (ratchet).** Every ``kind: contract``
   doc under ``docs/spec/`` should declare an ``evidence:`` field
   in front matter (one of ``well-supported``, ``reasoned-design``,
   ``assumption``, ``tbd``). Coverage ratchets via
   ``.vale/grounding-baseline.json``: docs currently without the
   field are listed there and pass; new contract docs not on the
   baseline that lack the field fail. Docs that gain the field
   trigger an info-level "ratchet opportunity" message.

Used by ``.github/workflows/grounding.yml`` and registered with
``scripts/docs_doctor.py`` for ``make docs-check`` parity.

Exit codes:
    0 — no errors (info messages may still print for ratchet)
    1 — at least one unresolved reference or new uncovered doc
    2 — internal error (registry missing, malformed front matter)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

SPEC_DIR = Path("docs/spec")
ADR_DIR = Path("docs/adr")
REFERENCES_PATH = SPEC_DIR / "references.md"
BASELINE_PATH = Path(".vale/grounding-baseline.json")

REF_BRACE_RE = re.compile(r"\{ref:([a-z0-9-]+)\}")
REF_FOOTNOTE_RE = re.compile(r"(?<!\\)\[\^([a-z0-9-]+)\]")
REGISTRY_ID_RE = re.compile(r"^\|\s*`\[ref:([a-z0-9-]+)\]`")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def parse_front_matter(text: str) -> dict[str, object]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}
    parsed = yaml.safe_load(m.group(1)) or {}
    return parsed if isinstance(parsed, dict) else {}


def parse_registry() -> set[str]:
    """Return the set of valid ``[ref:slug]`` IDs from ``references.md``."""
    if not REFERENCES_PATH.exists():
        return set()
    ids: set[str] = set()
    for line in REFERENCES_PATH.read_text(encoding="utf-8").splitlines():
        m = REGISTRY_ID_RE.match(line)
        if m:
            ids.add(m.group(1))
    return ids


def _strip_code(text: str) -> str:
    """Replace fenced and inline code with blanks of the same length.

    Same-length replacement keeps line numbers stable so error
    annotations point at the original source location.
    """
    text = FENCED_CODE_RE.sub(lambda m: re.sub(r"\S", " ", m.group(0)), text)
    text = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), text)
    return text


def find_references_in(text: str) -> list[tuple[str, int]]:
    """Return ``(slug, line_no)`` for every brace or footnote citation use.

    References inside fenced or inline code spans are skipped — those
    are usually documentation of the citation syntax itself, not real
    citations. Footnote *definitions* (``[^slug]:`` at line start) are
    also skipped; only *uses* count.
    """
    stripped = _strip_code(text)
    out: list[tuple[str, int]] = []
    for i, line in enumerate(stripped.splitlines(), start=1):
        for m in REF_BRACE_RE.finditer(line):
            out.append((m.group(1), i))
        for m in REF_FOOTNOTE_RE.finditer(line):
            after = line[m.end() :]
            if after.startswith(":"):
                continue
            out.append((m.group(1), i))
    return out


def iter_scan_targets() -> list[Path]:
    """Spec docs (excluding references.md and antipattern bodies) and ADRs."""
    targets: list[Path] = []
    for path in sorted(SPEC_DIR.rglob("*.md")):
        if path == REFERENCES_PATH:
            continue
        targets.append(path)
    for path in sorted(ADR_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        targets.append(path)
    return targets


def iter_contract_docs() -> list[Path]:
    """Spec docs declaring ``kind: contract`` in front matter."""
    out: list[Path] = []
    for path in sorted(SPEC_DIR.rglob("*.md")):
        if path == REFERENCES_PATH:
            continue
        text = path.read_text(encoding="utf-8")
        fm = parse_front_matter(text)
        if fm.get("kind") == "contract":
            out.append(path)
    return out


def main() -> int:
    if not REFERENCES_PATH.exists():
        print(f"error: {REFERENCES_PATH} missing", file=sys.stderr)
        return 2

    valid_ids = parse_registry()
    if not valid_ids:
        print(
            f"error: no `[ref:slug]` entries parsed from {REFERENCES_PATH}",
            file=sys.stderr,
        )
        return 2

    errors: list[str] = []

    # Check 1: every {ref:slug} / [^slug] resolves.
    for path in iter_scan_targets():
        text = path.read_text(encoding="utf-8")
        for slug, line_no in find_references_in(text):
            if slug not in valid_ids:
                errors.append(
                    f"::error file={path},line={line_no}::unresolved "
                    f"reference {{ref:{slug}}} — add a row to "
                    f"{REFERENCES_PATH} or fix the slug"
                )

    # Check 2: every kind: contract doc declares evidence: (ratchet).
    baseline_data: dict[str, object] = (
        json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        if BASELINE_PATH.exists()
        else {"docs_without_evidence": []}
    )
    raw_baselined = baseline_data.get("docs_without_evidence", [])
    baselined: set[str] = (
        {s for s in raw_baselined if isinstance(s, str)}
        if isinstance(raw_baselined, list)
        else set()
    )

    contract_docs_without_evidence: set[str] = set()
    for path in iter_contract_docs():
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        if "evidence" not in fm:
            contract_docs_without_evidence.add(str(path))

    new_uncovered = sorted(contract_docs_without_evidence - baselined)
    ratchet_down = sorted(baselined - contract_docs_without_evidence)

    for path_str in new_uncovered:
        errors.append(
            f"::error file={path_str}::kind: contract doc missing "
            "`evidence:` field; declare one of well-supported / "
            "reasoned-design / assumption / tbd per "
            "docs/spec/25-rigor-framework.md"
        )

    for e in errors:
        print(e)
    for d in ratchet_down:
        print(
            f"info: ratchet opportunity: {d} now declares evidence:; "
            f"remove it from {BASELINE_PATH}"
        )

    if errors:
        print(
            f"\n{len(errors)} grounding error(s); see "
            "docs/spec/25-rigor-framework.md for the rules.",
            file=sys.stderr,
        )
        return 1

    total_contract = sum(1 for _ in iter_contract_docs())
    covered = total_contract - len(contract_docs_without_evidence)
    print(
        f"grounding OK: {len(valid_ids)} bibliography ID(s); "
        f"{covered} of {total_contract} contract doc(s) declare "
        f"evidence: ({len(ratchet_down)} ratchet opportunit(ies))"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Enforce the HM-REQ <-> scenario <-> system-test linkage.

Implements the spec-test sync workflow from
`docs/spec/23-system-tests.md`:

- Every non-internal HM-REQ in `requirements.md` MUST be cited by
  at least one scenario in the `traceability.md` System-test
  scenarios table.
- Every scenario MUST cite at least one HM-REQ that exists in
  `requirements.md`.
- Every scenario's target test file MUST exist, contain the named
  function, and carry `# spec: <S-ID>` plus `# spec: <HM-REQ>`
  annotations matching its row.
- The optional `internal_only` list in `requirements.md` front
  matter exempts CI-only / non-surface-observable requirements
  (TDD order, action pinning, license headers, etc.) from the
  coverage rule.

Used by `.github/workflows/system-tests.yml` and registered with
`scripts/docs_doctor.py` for `make docs-check` parity.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REQUIREMENTS_PATH = Path("docs/spec/requirements.md")
TRACEABILITY_PATH = Path("docs/spec/traceability.md")

SCENARIO_ID_RE = re.compile(r"^S-[A-Z]+-\d{2}$")
HM_REQ_RE = re.compile(r"\bHM-REQ-\d{4}\b")
TEST_PATH_RE = re.compile(r"^(?P<file>tests/system/[^:]+\.py)::(?P<func>test_\w+)$")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True)
class Scenario:
    """A single row from the traceability System-test scenarios table."""

    sid: str
    hm_reqs: tuple[str, ...]
    test_file: Path
    test_func: str
    line_no: int


def parse_front_matter(text: str) -> dict[str, object]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}
    parsed = yaml.safe_load(m.group(1)) or {}
    return parsed if isinstance(parsed, dict) else {}


def parse_requirements() -> tuple[set[str], set[str]]:
    """Return ``(all_ids, internal_only_ids)`` from requirements.md."""
    text = REQUIREMENTS_PATH.read_text(encoding="utf-8")
    fm = parse_front_matter(text)
    internal = {s for s in (fm.get("internal_only") or []) if isinstance(s, str)}
    ids: set[str] = set()
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("| HM-REQ-"):
            continue
        for m in HM_REQ_RE.finditer(stripped):
            ids.add(m.group(0))
    return ids, internal


def parse_scenarios() -> list[Scenario]:
    """Parse the System-test scenarios table from traceability.md."""
    scenarios: list[Scenario] = []
    text = TRACEABILITY_PATH.read_text(encoding="utf-8")
    in_section = False
    for i, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            in_section = line.strip() == "## System-test scenarios"
            continue
        if not in_section:
            continue
        stripped = line.lstrip()
        if not stripped.startswith("| S-"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        sid, refs_cell, test_cell, _status = cells[0], cells[1], cells[2], cells[3]
        if not SCENARIO_ID_RE.match(sid):
            continue
        m = TEST_PATH_RE.match(test_cell)
        if not m:
            print(
                f"::error file={TRACEABILITY_PATH},line={i}::scenario {sid}: "
                f"test path {test_cell!r} does not match "
                "tests/system/<file>.py::<func> shape"
            )
            continue
        refs = tuple(sorted(set(HM_REQ_RE.findall(refs_cell))))
        scenarios.append(
            Scenario(
                sid=sid,
                hm_reqs=refs,
                test_file=Path(m.group("file")),
                test_func=m.group("func"),
                line_no=i,
            )
        )
    return scenarios


def check_test_file(scenario: Scenario) -> list[str]:
    """Return error strings for a scenario's test file."""
    errors: list[str] = []
    if not scenario.test_file.exists():
        errors.append(
            f"::error file={TRACEABILITY_PATH},line={scenario.line_no}::"
            f"{scenario.sid}: test file {scenario.test_file} does not exist"
        )
        return errors

    body = scenario.test_file.read_text(encoding="utf-8")

    if not re.search(rf"^def {re.escape(scenario.test_func)}\(", body, re.MULTILINE):
        errors.append(
            f"::error file={scenario.test_file}::{scenario.sid}: "
            f"function {scenario.test_func}(...) not defined; "
            f"traceability.md:{scenario.line_no} expects it"
        )

    if not re.search(rf"#\s*spec:\s*{re.escape(scenario.sid)}\b", body):
        errors.append(
            f"::error file={scenario.test_file}::{scenario.sid}: "
            f"missing `# spec: {scenario.sid}` annotation"
        )

    for req in scenario.hm_reqs:
        if not re.search(rf"#\s*spec:\s*{re.escape(req)}\b", body):
            errors.append(
                f"::error file={scenario.test_file}::{scenario.sid}: "
                f"missing `# spec: {req}` annotation (cited in "
                f"traceability.md:{scenario.line_no})"
            )

    return errors


def main() -> int:
    if not REQUIREMENTS_PATH.exists():
        print(f"error: {REQUIREMENTS_PATH} missing", file=sys.stderr)
        return 2
    if not TRACEABILITY_PATH.exists():
        print(f"error: {TRACEABILITY_PATH} missing", file=sys.stderr)
        return 2

    all_reqs, internal_reqs = parse_requirements()
    if not all_reqs:
        print(
            f"error: no HM-REQ ids parsed from {REQUIREMENTS_PATH}",
            file=sys.stderr,
        )
        return 2

    unknown_internal = internal_reqs - all_reqs
    errors: list[str] = []
    for tag in sorted(unknown_internal):
        errors.append(
            f"::error file={REQUIREMENTS_PATH}::front-matter `internal_only` "
            f"lists {tag} but it is not in the requirements table"
        )

    scenarios = parse_scenarios()
    seen_sids: set[str] = set()
    cited_reqs: set[str] = set()
    for sc in scenarios:
        if sc.sid in seen_sids:
            errors.append(
                f"::error file={TRACEABILITY_PATH},line={sc.line_no}::"
                f"duplicate scenario id {sc.sid}"
            )
        seen_sids.add(sc.sid)

        if not sc.hm_reqs:
            errors.append(
                f"::error file={TRACEABILITY_PATH},line={sc.line_no}::"
                f"{sc.sid} cites no HM-REQ; every scenario must cite >=1"
            )
        for req in sc.hm_reqs:
            if req not in all_reqs:
                errors.append(
                    f"::error file={TRACEABILITY_PATH},line={sc.line_no}::"
                    f"{sc.sid} cites {req} which is not in requirements.md"
                )
            cited_reqs.add(req)

        errors.extend(check_test_file(sc))

    surface_reqs = all_reqs - internal_reqs
    uncovered = sorted(surface_reqs - cited_reqs)
    for tag in uncovered:
        errors.append(
            f"::error file={REQUIREMENTS_PATH}::{tag} has no system-test "
            f"scenario; either add a row to {TRACEABILITY_PATH} citing "
            f"it, or list it in the `internal_only:` front-matter array "
            f"with a one-line justification in the doc body"
        )

    for e in errors:
        print(e)

    if errors:
        print(
            f"\n{len(errors)} system-test traceability error(s) "
            f"({len(scenarios)} scenarios over {len(surface_reqs)} "
            f"surface-observable HM-REQ(s); "
            f"{len(internal_reqs)} internal-only).",
            file=sys.stderr,
        )
        return 1

    print(
        f"system-test traceability OK: {len(scenarios)} scenarios cover "
        f"{len(cited_reqs)} of {len(surface_reqs)} surface HM-REQ(s); "
        f"{len(internal_reqs)} internal-only exempt"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

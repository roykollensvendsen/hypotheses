# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Documentation health check orchestrator.

Runs every documentation check registered in `CHECKS` and reports a
single pass/fail summary. This mirrors the CI doc-quality gates;
running it locally before opening a PR catches the same failures CI
catches.

Each check is a `(name, command)` pair. Commands run as subprocesses
with the repo root as `cwd`; nonzero exit means failure. Optional
checks (link checker, prose linter) skip silently when the underlying
binary is not installed.

New checks register here as later sub-PRs in the
documentation-quality sprint land. See `docs/CONTRIBUTING-DOCS.md`
for the rationale and full register layout.

Used by `make docs-check`.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]
    optional: bool = False


CHECKS: tuple[Check, ...] = (
    Check("spec-consistency", ["python3", "scripts/check_spec_consistency.py"]),
    Check("requirements", ["python3", "scripts/check_requirements.py"]),
    Check("schema-matches-doc", ["python3", "scripts/check_schema_matches_doc.py"]),
    Check("validate-hypotheses", ["python3", "scripts/validate_hypotheses.py"]),
    Check("frontmatter", ["python3", "scripts/check_frontmatter.py"]),
    Check("agents-routing", ["python3", "scripts/check_agents_routing.py"]),
    Check("token-budget", ["python3", "scripts/check_token_budget.py"]),
    Check("orphan-docs", ["python3", "scripts/check_orphan_docs.py"]),
    Check("prompt-injection", ["python3", "scripts/check_prompt_injection.py"]),
    Check("spdx-headers", ["python3", "scripts/check_spdx_headers.py"]),
    Check("links", ["lychee", "--no-progress", "."], optional=True),
    Check("vale", ["python3", "scripts/check_vale_baseline.py"], optional=True),
    Check("typos", ["typos"], optional=True),
    Check(
        "markdownlint",
        ["npx", "--yes", "markdownlint-cli2@0.14.0", "**/*.md"],
        optional=True,
    ),
)


def run(check: Check) -> tuple[bool, str]:
    if check.optional and shutil.which(check.command[0]) is None:
        return True, f"skipped: {check.command[0]} not on PATH"
    try:
        proc = subprocess.run(
            check.command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return check.optional, f"missing tool: {exc}"
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output


def main() -> int:
    failures: list[str] = []
    for check in CHECKS:
        ok, output = run(check)
        marker = "PASS" if ok else "FAIL"
        print(f"[{marker}] {check.name}")
        if output and (not ok or output.startswith("skipped")):
            for line in output.splitlines():
                print(f"    {line}")
        if not ok:
            failures.append(check.name)
    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print("all documentation checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

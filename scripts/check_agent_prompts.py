# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Validate agent role prompts under `agents/prompts/`.

Two enforced contracts:

1. **Length**: each `agents/prompts/*-system.md` must be ≤200
   non-blank, non-comment lines. The role prompts are deliberately
   short — the spec is the contract; the prompt only frames the
   role and references the spec.

2. **Model-neutral**: provider-specific model or vendor names
   (`Claude`, `GPT-4`, `GPT-4o`, `Gemini`, `Anthropic`, `OpenAI`)
   must not appear outside fenced code blocks. The role prompt is
   the contract for *any* agent runtime; baking in a vendor name
   would fork the contract per provider.

Scans only `agents/prompts/`. Never scans `AGENTS.md`, whose own
quoted attack examples and trust-boundary discussion would
otherwise trigger the banned-shape check.

Used by `.github/workflows/agent-prompts.yml`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROMPT_GLOB = "agents/prompts/*-system.md"
MAX_LINES = 200

BANNED_TOKENS = (
    "Claude",
    "GPT-4",
    "GPT-4o",
    "ChatGPT",
    "Gemini",
    "Anthropic",
    "OpenAI",
)
BANNED_RE = re.compile(r"\b(" + "|".join(BANNED_TOKENS) + r")\b")
FENCE_RE = re.compile(r"^```")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def lint_file(path: Path) -> list[str]:
    raw = path.read_text()
    # Strip HTML comments (SPDX header) before line counting.
    no_comments = HTML_COMMENT_RE.sub("", raw)
    non_blank = sum(1 for ln in no_comments.splitlines() if ln.strip())
    errors: list[str] = []
    if non_blank > MAX_LINES:
        errors.append(
            f"{path}: {non_blank} non-blank lines exceeds the {MAX_LINES}-line "
            "cap; spec content belongs in docs/spec/, not in the prompt."
        )
    in_fence = False
    inline_code_re = re.compile(r"`[^`]*`")
    for lineno, line in enumerate(raw.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Strip inline backtick-code spans before scanning. A vendor name
        # quoted as code is a reference (e.g., to a forbidden commit
        # trailer), not a directive.
        prose = inline_code_re.sub("", line)
        for match in BANNED_RE.finditer(prose):
            errors.append(
                f"{path}:{lineno}: provider-specific name '{match.group(1)}' "
                f"outside a fenced code block; prompts must be model-neutral."
            )
    return errors


def main() -> int:
    paths = sorted(Path().glob(PROMPT_GLOB))
    if not paths:
        print(f"error: no files matched {PROMPT_GLOB}", file=sys.stderr)
        return 2
    errors: list[str] = []
    for path in paths:
        errors.extend(lint_file(path))
    if errors:
        for err in errors:
            print(f"error: {err}")
        print(f"\n{len(errors)} error(s) over {len(paths)} prompt(s)")
        return 1
    print(f"agent-prompts OK: {len(paths)} prompt(s) within budget and model-neutral")
    return 0


if __name__ == "__main__":
    sys.exit(main())

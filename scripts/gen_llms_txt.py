# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors

"""Generate `llms.txt` and `llms-full.txt` at the repo root.

Adopts the llmstxt.org convention so an LLM session that lands
on the repo can discover the canonical entry points and a
self-contained narrative bundle without crawling the tree.

`llms.txt` is the index — name, summary, and grouped links to
the important docs. `llms-full.txt` is the concatenated narrative:
VISION.md, AGENTS.md, every `docs/spec/NN-*.md` in numeric order,
the antipatterns corpus, role prompts.

Both files are derived. They carry `<!-- generated:by=... -->`
headers, are committed to the tree, and are snapshot-checked by
`.github/workflows/llms-txt.yml` (`git diff --exit-code`). The
canonical homes for every fact remain in their original files
(VISION.md, the spec docs, role prompts); these generated files
only restate by quoting whole bodies, never by paraphrasing.

Run:
    uv run scripts/gen_llms_txt.py

Used by `.github/workflows/llms-txt.yml`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _doc_lib import parse_frontmatter  # noqa: E402

LLMS_TXT_PATH = Path("llms.txt")
LLMS_FULL_PATH = Path("llms-full.txt")
HEADER_TEMPLATE = (
    "<!-- generated:by=scripts/gen_llms_txt.py from={sources}; "
    "do not edit by hand. See docs/CONTRIBUTING-DOCS.md. -->\n\n"
)


def collect_spec_docs() -> list[Path]:
    """Numbered spec docs in numeric order, plus index files."""
    out = sorted(
        p
        for p in Path("docs/spec").glob("*.md")
        if not p.name == "README.md" and not p.name.startswith("_")
    )
    return out


def collect_antipatterns() -> list[Path]:
    return sorted(Path("docs/spec/antipatterns").glob("ap-*.md"))


def collect_role_prompts() -> list[Path]:
    return sorted(Path("agents/prompts").glob("*-system.md"))


def collect_hypotheses() -> list[Path]:
    return sorted(Path("hypotheses").glob("H-*.md"))


def gen_llms_txt() -> str:
    out = [
        HEADER_TEMPLATE.format(sources="VISION.md, AGENTS.md, docs/spec/README.md"),
        "# hypotheses\n\n",
        "> A permissionless scientific hypothesis market on Bittensor. "
        "Miners preregister falsifiable claims about machine learning, "
        "run the experiments themselves, and earn TAO when validators "
        "confirm their results reproduce and improve on declared "
        "baselines. Agent-first by design, with a human CLI as the "
        "escape hatch.\n\n",
        "Phase 0 — spec freeze. The runtime under `src/hypotheses/` is "
        "not yet implemented; only the JSON Schema contracts and the "
        "spec/CI/collaboration infrastructure ship today.\n\n",
        "## Read first\n\n",
        "- [VISION.md](VISION.md): canonical statement of mission and design pillars.\n",
        "- [AGENTS.md](AGENTS.md): entry point for autonomous agents; trust boundary, role catalogue, context routing.\n",
        "- [docs/spec/README.md](docs/spec/README.md): the spec index.\n",
        "- [docs/spec/00.5-foundations.md](docs/spec/00.5-foundations.md): the why behind every design decision.\n\n",
        "## Spec docs\n\n",
    ]
    for path in collect_spec_docs():
        data, _, _ = parse_frontmatter(path)
        desc = data.get("description", "") if data else ""
        out.append(f"- [{path}]({path}): {desc}.\n")
    out.append("\n## Hypotheses (preregistered claims)\n\n")
    for path in collect_hypotheses():
        data, _, _ = parse_frontmatter(path)
        title = data.get("title", "") if data else ""
        out.append(f"- [{path}]({path}): {title}.\n")
    out.append("\n## Antipatterns (do NOT do this)\n\n")
    for path in collect_antipatterns():
        out.append(f"- [{path}]({path})\n")
    out.append("\n## Agent role prompts\n\n")
    for path in collect_role_prompts():
        role = path.stem.removesuffix("-system")
        out.append(f"- [{path}]({path}): system prompt for the {role} role.\n")
    out.append("\n## Governance and contributing\n\n")
    out.append("- [GOVERNANCE.md](GOVERNANCE.md): decision authority and process.\n")
    out.append("- [CONTRIBUTING.md](CONTRIBUTING.md): four contribution tracks.\n")
    out.append("- [SECURITY.md](SECURITY.md): private vulnerability disclosure.\n")
    out.append(
        "- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): Contributor Covenant 2.1.\n"
    )
    return "".join(out)


def gen_llms_full() -> str:
    sources = ["VISION.md", "AGENTS.md"]
    sources.extend(str(p) for p in collect_spec_docs())
    sources.extend(str(p) for p in collect_antipatterns())
    sources.extend(str(p) for p in collect_role_prompts())
    out = [
        HEADER_TEMPLATE.format(
            sources="VISION.md, AGENTS.md, docs/spec/, agents/prompts/"
        )
    ]
    for src in sources:
        path = Path(src)
        if not path.exists():
            continue
        out.append(f"\n\n========== BEGIN {src} ==========\n\n")
        out.append(path.read_text())
        out.append(f"\n========== END {src} ==========\n")
    return "".join(out)


def main() -> int:
    LLMS_TXT_PATH.write_text(gen_llms_txt())
    LLMS_FULL_PATH.write_text(gen_llms_full())
    print(f"wrote {LLMS_TXT_PATH} ({LLMS_TXT_PATH.stat().st_size} bytes)")
    print(f"wrote {LLMS_FULL_PATH} ({LLMS_FULL_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

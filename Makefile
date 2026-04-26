# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
#
# Documentation maintenance and CI-mirror targets.
#
# `make docs-check` runs every documentation check that CI runs.
# `make precommit-install` wires local hooks.
# Additional targets land incrementally with the documentation-quality
# sprint; see docs/CONTRIBUTING-DOCS.md for the catalog.

.PHONY: help docs-check test test-watch links vale typos markdownlint precommit-install

help:
	@echo "Available targets:"
	@echo "  docs-check          run all documentation checks (mirrors CI)"
	@echo "  test                run pytest once (mirrors CI; reports coverage)"
	@echo "  test-watch          re-run relevant tests on every save (pytest-watcher)"
	@echo "  links               run lychee link checker"
	@echo "  vale                run vale prose linter"
	@echo "  typos               run typos spell-checker"
	@echo "  markdownlint        run markdownlint-cli2 (requires npm)"
	@echo "  precommit-install   install pre-commit and commit-msg hooks"

docs-check:
	@python3 scripts/docs_doctor.py

test:
	@uv run --extra dev pytest --cov=hypotheses --cov-report=term-missing -n auto

# Fast inner loop. Re-runs the relevant tests on every save under tests/
# and src/. Skipped placeholders stay green; replacing one with a
# real (failing) test is the safe-explore entry point.
test-watch:
	@uv run --extra dev ptw --runner "pytest --cov=hypotheses -n auto" tests src

links:
	@lychee --no-progress .

vale:
	@vale docs/spec/ VISION.md

typos:
	@typos

markdownlint:
	@npx --yes markdownlint-cli2@0.14.0 "**/*.md" "!**/.venv/**" "!**/.pytest_cache/**" "!**/node_modules/**"

precommit-install:
	@pre-commit install --hook-type pre-commit --hook-type commit-msg

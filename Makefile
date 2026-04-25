# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
#
# Documentation maintenance and CI-mirror targets.
#
# `make docs-check` runs every documentation check that CI runs.
# `make precommit-install` wires local hooks.
# Additional targets land incrementally with the documentation-quality
# sprint; see docs/CONTRIBUTING-DOCS.md for the catalog.

.PHONY: help docs-check links vale typos markdownlint precommit-install

help:
	@echo "Available targets:"
	@echo "  docs-check          run all documentation checks (mirrors CI)"
	@echo "  links               run lychee link checker"
	@echo "  vale                run vale prose linter"
	@echo "  typos               run typos spell-checker"
	@echo "  markdownlint        run markdownlint-cli2 (requires npm)"
	@echo "  precommit-install   install pre-commit and commit-msg hooks"

docs-check:
	@python3 scripts/docs_doctor.py

links:
	@lychee --no-progress .

vale:
	@vale docs/spec/ VISION.md

typos:
	@typos

markdownlint:
	@npx --yes markdownlint-cli2@0.14.0 "**/*.md"

precommit-install:
	@pre-commit install --hook-type pre-commit --hook-type commit-msg

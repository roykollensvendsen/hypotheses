#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
#
# Fail if any workflow or composite action references a non-SHA ref.
#
# A SHA ref is 40 hex chars; anything else (tag like @v1, branch like @main)
# is rejected. Used by .github/workflows/action-pin-check.yml.

set -euo pipefail

shopt -s nullglob globstar

VIOLATIONS=0

# Match: `uses: owner/repo@<ref>` — capture the ref. Skip `./local-action`
# references (start with `./`) and docker:// refs (start with `docker://`).
PATTERN='uses:[[:space:]]+([^[:space:]./][^[:space:]]*)@([^[:space:]]+)'

for file in .github/workflows/*.yml .github/workflows/*.yaml \
            .github/actions/**/*.yml .github/actions/**/*.yaml; do
    [ -f "$file" ] || continue
    lineno=0
    while IFS= read -r line; do
        lineno=$((lineno + 1))
        # Strip leading whitespace for matching
        if [[ "$line" =~ $PATTERN ]]; then
            action="${BASH_REMATCH[1]}"
            ref="${BASH_REMATCH[2]}"
            # Accept 40-char hex SHA only
            if [[ ! "$ref" =~ ^[0-9a-f]{40}$ ]]; then
                echo "::error file=$file,line=$lineno::action $action is pinned by ref '$ref', not a full SHA"
                VIOLATIONS=$((VIOLATIONS + 1))
            fi
        fi
    done < "$file"
done

if [ "$VIOLATIONS" -gt 0 ]; then
    echo ""
    echo "Found $VIOLATIONS tag-pinned action(s). See docs/spec/15-ci-cd.md#pinning-policy."
    exit 1
fi

echo "All actions SHA-pinned."

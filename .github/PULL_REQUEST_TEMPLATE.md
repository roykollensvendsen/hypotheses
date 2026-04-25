## Summary

<what this PR does and why, in 1–3 sentences>

## TDD checklist

- [ ] Failing tests were committed first, as a `test:` commit.
- [ ] The implementation commit (`feat:` / `fix:`) makes them pass.
- [ ] Any refactoring happened under green.
- [ ] Mutation score for touched modules is ≥ 75% locally
      (`uv run mutmut run` + `scripts/check_mutation_score.py`).

## Spec alignment

- [ ] If this changes behaviour documented in `docs/spec/`, the spec
      is updated in the same PR.
- [ ] If this changes a schema, the JSON Schema and the human-readable
      doc agree (`scripts/check_schema_matches_doc.py` passes).

## Notes

<!-- anything else reviewers should know -->

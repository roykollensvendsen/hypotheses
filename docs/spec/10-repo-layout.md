---
name: repo layout
description: target directory structure for the full subnet codebase
---

# 10 — Repo layout

```
.
├── README.md                       # project intro, pointer to spec
├── LICENSE                         # AGPL-3.0-or-later
├── pyproject.toml                  # single package: hypotheses
├── uv.lock                         # pinned deps
├── .commitlintrc.mjs               # conventional commits, ≤72 chars
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md    # TDD + spec alignment checklist
│   └── workflows/
│       ├── ci.yml                  # lint, typecheck, tests
│       ├── commitlint.yml          # conventional commit enforcement
│       ├── tdd-gate.yml            # tests precede implementation
│       ├── mutation.yml            # nightly mutation-score gate
│       ├── spec-validate.yml       # hypothesis schema validation on PR
│       └── spec-mirror.yml         # mirror specs to IPFS on merge
├── docs/
│   ├── initial-discord-conversation.md
│   ├── research-notes/             # free-form essays and questions
│   └── spec/                       # the authoritative specification
│       ├── README.md
│       ├── 00-overview.md
│       ├── 01-glossary.md
│       ├── 02-hypothesis-format.md
│       ├── 03-architecture.md
│       ├── 04-miner.md
│       ├── 05-validator.md
│       ├── 06-scoring.md
│       ├── 07-incentive.md
│       ├── 08-experiment-runtime.md
│       ├── 09-protocol.md
│       ├── 10-repo-layout.md
│       └── 11-roadmap.md
├── hypotheses/                     # the registry
│   ├── HYPOTHESIS_TEMPLATE.md
│   └── H-NNNN-<slug>.md            # one per hypothesis
├── agents/                         # starter llm-agent configurations
│   ├── README.md
│   ├── prompts/                    # system-prompt templates
│   ├── examples/                   # runnable reference agents
│   └── eval/
├── experiments/                    # executable code per hypothesis
│   └── H-NNNN/
│       ├── run.py                  # entrypoint
│       ├── model.yaml              # or other config files
│       ├── pyproject.toml          # pinned env for this experiment
│       └── README.md               # experiment-local notes
├── src/
│   └── hypotheses/
│       ├── __init__.py
│       ├── cli/                    # `hypo` unified entry point
│       │   ├── __init__.py         # top-level dispatcher: main()
│       │   ├── read.py             # ls, show, search, submissions, scores
│       │   ├── miner.py            # propose, run, submit, register miner
│       │   ├── validator.py        # validate *, register validator
│       │   ├── mcp.py              # mcp *
│       │   ├── doctor.py
│       │   └── init.py
│       ├── client/                 # public typed SDK (hypotheses.client)
│       │   ├── __init__.py
│       │   ├── sync.py             # Client
│       │   ├── aio.py              # AsyncClient
│       │   └── models.py           # pydantic models re-exported
│       ├── mcp/                    # `hypo mcp *` server implementation
│       │   ├── server.py
│       │   ├── tools.py            # tool surface per 13-agent-integration
│       │   └── schema/             # per-tool argument schemas
│       ├── spec/
│       │   ├── schema/
│       │   │   └── hypothesis.schema.json
│       │   ├── parser.py
│       │   └── validator.py
│       ├── protocol/
│       │   ├── synapses.py         # ResultsAnnouncement, GetManifest, ...
│       │   └── signing.py          # ed25519, canonical JSON
│       ├── runtime/
│       │   ├── sandbox/            # container invocation
│       │   ├── data/               # dataset adapters
│       │   ├── metrics.py          # metrics.report()
│       │   └── run.py              # Run harness
│       ├── miner/
│       │   ├── proposer.py         # propose command
│       │   ├── runner.py           # run command
│       │   └── submitter.py        # submit command
│       ├── validator/
│       │   ├── pipeline.py         # discover → validate → rerun → score
│       │   ├── rerun.py
│       │   └── weights.py
│       ├── scoring/
│       │   ├── rigor.py
│       │   ├── reproduction.py
│       │   ├── improvement.py
│       │   ├── novelty.py
│       │   ├── cost.py
│       │   ├── composite.py
│       │   └── stats/
│       │       ├── welch_t.py
│       │       ├── bootstrap.py
│       │       └── mann_whitney.py
│       ├── storage/
│       │   ├── ipfs.py
│       │   └── local_cache.py
│       └── oracle/
│           ├── base.py
│           └── sn42.py             # TBD adapter
├── tests/
│   ├── spec/                       # schema and parser tests
│   ├── scoring/
│   ├── runtime/
│   ├── protocol/
│   └── integration/
│       └── smoke_submit_score.py   # full miner→validator round-trip
└── scripts/
    ├── register_subnet.sh          # one-off registration script
    ├── dev-miner.sh
    ├── dev-validator.sh
    ├── check_schema_matches_doc.py # spec ↔ schema consistency
    ├── check_tdd_order.py          # PR gate: test: commits before feat:/fix:
    └── check_mutation_score.py     # parse mutmut output, enforce minimum
```

## Package surface

The project is one importable package: `hypotheses`. Two console scripts
are exported:

```toml
[project.scripts]
hypo = "hypotheses.cli:main"
```

Anything outside `src/` is consumed as data (the spec, the hypotheses
registry, the experiment code) — `experiments/` specifically is NOT
imported by the package at runtime. The runtime mounts it into the
sandbox per-run.

## Why this layout

- **`hypotheses/` and `experiments/` are siblings.** The spec (registry
  entry) and its runnable implementation live side by side. A PR that
  touches one must typically touch the other.
- **`src/` is framework, not content.** Moving a hypothesis from
  "proposed" to "settled" never requires changing `src/`.
- **Schema + docs co-located.** The JSON schema for the spec lives under
  `src/hypotheses/spec/schema/` but the human-readable definition lives
  in `docs/spec/02-hypothesis-format.md`. CI enforces they agree via
  `scripts/check_schema_matches_doc.py`, run in
  `.github/workflows/spec-validate.yml`. The script parses the `## Spec
  fields` YAML block from the doc and compares required/optional fields
  and types against the JSON Schema; divergence fails CI.

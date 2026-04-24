---
name: repo layout
description: target directory structure for the full subnet codebase
---

# 10 — Repo layout

```
.
├── README.md                       # project intro, pointer to VISION/spec
├── VISION.md                       # canonical vision + mission
├── AGENTS.md                       # entry point for LLM agents
├── CONTRIBUTING.md                 # three contribution tracks
├── CODE_OF_CONDUCT.md              # Contributor Covenant 2.1
├── GOVERNANCE.md                   # maintainer model + decision process
├── SECURITY.md                     # private vuln advisory flow
├── CHANGELOG.md                    # release-please generated
├── LICENSE                         # AGPL-3.0-or-later
├── .editorconfig                   # cross-editor formatting
├── .gitignore                      # standard Python / uv / IDE ignores
├── pyproject.toml                  # single package: hypotheses
├── uv.lock                         # pinned deps
├── .commitlintrc.mjs               # conventional commits, ≤72 chars
├── .github/
│   ├── CODEOWNERS                  # path → reviewer routing
│   ├── PULL_REQUEST_TEMPLATE.md    # TDD + spec alignment checklist
│   ├── dependabot.yml              # weekly deps, monthly actions
│   ├── labeler.yml                 # paths → PR labels
│   ├── ISSUE_TEMPLATE/
│   │   ├── config.yml              # disable blank issues; discussion redirect
│   │   ├── hypothesis-proposal.yml # primary on-ramp
│   │   ├── spec-question.yml
│   │   └── bug.yml
│   └── workflows/
│       ├── ci.yml                  # lint, typecheck, tests
│       ├── commitlint.yml          # conventional commit enforcement
│       ├── tdd-gate.yml            # tests precede implementation
│       ├── mutation.yml            # nightly mutation-score gate
│       ├── spec-validate.yml       # hypothesis schema validation on PR
│       ├── spec-mirror.yml         # mirror specs to IPFS on merge
│       ├── pip-audit.yml           # weekly CVE scan on pinned deps
│       ├── bandit.yml              # python security lint on PR
│       ├── vulture.yml             # dead-code detector on PR
│       ├── link-check.yml          # lychee on docs/
│       ├── adr-required.yml        # ADR required on dep/tool changes
│       ├── action-pin-check.yml    # every action ref is a 40-char SHA
│       ├── zizmor.yml              # workflow static-analysis
│       ├── scorecard.yml           # OpenSSF Scorecard, weekly
│       ├── spdx.yml                # SPDX license headers on sources
│       ├── typos.yml               # spell check
│       ├── pr-title.yml            # conventional PR title
│       ├── pr-size.yml             # size labels + 500 LoC gate
│       ├── labeler.yml             # auto-label PRs by changed paths
│       ├── stale.yml               # close 30/60-day inactive issues/PRs
│       └── release-please.yml      # generate release PRs from commits
├── docs/
│   ├── initial-discord-conversation.md
│   ├── implementation-handoff.md   # phase 1 kickoff prompt for an agent
│   ├── adr/                        # architecture decision records (MADR)
│   │   ├── README.md
│   │   └── NNNN-<slug>.md
│   ├── research-notes/             # free-form essays and questions
│   └── spec/                       # the authoritative specification
│       ├── README.md
│       ├── antipatterns/           # machine-readable do-NOT-do patterns
│       │   ├── README.md
│       │   └── ap-NNNN-<slug>.md
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
│   │   ├── implementer-system.md
│   │   ├── miner-system.md
│   │   ├── validator-operator-system.md
│   │   ├── proposer-system.md
│   │   └── reviewer-system.md
│   ├── examples/                   # runnable reference agents (Phase 1+)
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
│       │   │   ├── hypothesis.schema.json
│       │   │   ├── synapses.schema.json
│       │   │   ├── run-manifest.schema.json
│       │   │   └── events.schema.json
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
│   ├── golden/                     # frozen JSON i/o fixtures (no code)
│   │   ├── scoring/
│   │   ├── hypothesis-parsing/
│   │   └── protocol/
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
    ├── check_mutation_score.py     # parse mutmut output, enforce minimum
    ├── check_adr_required.py       # ADR required on dep/tool changes
    ├── check_action_pins.sh        # every action ref must be a 40-char SHA
    ├── check_spdx_headers.py       # SPDX headers on every .py and .sh source
    └── validate_hypotheses.py      # JSON Schema validate all hypotheses/
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

## Self-audit

This doc is done when:

- Every path listed exists on the filesystem, or is explicitly
  marked "Phase N planned."
- Every `src/hypotheses/<module>/` entry has a matching build-order
  step in [12 § build order](12-implementation-constraints.md#build-order).
- Every workflow listed exists in `.github/workflows/` and is
  catalogued in [15](15-ci-cd.md#workflow-catalog).
- `pyproject.toml` script entries match the CLI verbs in
  [14](14-cli.md).
- Agent directories match [13-agent-integration.md](13-agent-integration.md).

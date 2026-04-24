---
name: operations
description: observability, alerting, runbooks, and disaster recovery for operators
tokens: 3800
load_for: [agent-operator, implementation, review]
depends_on: [12, 16]
---

# 19 — Operations: observability and runbook

An operator running a miner, a validator, or the subnet's
infrastructure needs three things to stay sane:

1. **Visibility** — structured signals that reveal the current
   state.
2. **Alerts** — rules that fire when the state diverges from
   healthy.
3. **Runbooks** — a named response for each alert.

This document specifies all three. It cross-references
[12 § logging](12-implementation-constraints.md#logging--observability)
(log format) and
[05 — Validator](05-validator.md),
[04 — Miner](04-miner.md) (the roles).

## Logs and events

### Log format

Every component emits line-delimited JSON to stderr via `structlog`,
with the mandatory fields from
[12 § logging](12-implementation-constraints.md#logging--observability):

| field | required | type | notes |
|-------|----------|------|-------|
| `ts` | yes | ISO-8601 UTC string | millisecond precision |
| `level` | yes | `debug`\|`info`\|`warning`\|`error` | |
| `msg` | yes | string | machine-stable, not a sentence |
| `component` | yes | string | dotted, e.g. `miner.runner` |
| `cycle_id` | contextual | string | set for validator cycles |
| `hypothesis_id` | contextual | string | set when a hypothesis is in scope |
| `miner_hotkey` | contextual | string | set when a miner is in scope |
| `spec_version` | contextual | int | set when a hypothesis is in scope |
| `announcement_cid` | contextual | string | set when scoring a submission |

Additional keys are free-form per component; no component names a
field that conflicts with the above.

### `events.jsonl`

In addition to stderr, miners and validators each maintain an
append-only `events.jsonl` alongside their data directory. Events
are a **subset** of the log stream — durable, replay-friendly, and
bounded to records that matter for audit or post-incident review.

A record has all the mandatory log fields plus:

| field | type | notes |
|-------|------|-------|
| `event` | string | one of the enum values below |
| `data` | object | event-specific payload |

**Recognised event types** (stable across versions; new ones get
added, old ones never renamed):

| event | emitted by | when |
|-------|------------|------|
| `miner.run.start` | miner | `hypo run` begins |
| `miner.run.seed.done` | miner | one seed completes (per condition) |
| `miner.run.done` | miner | all seeds done, manifest written |
| `miner.submit.broadcast` | miner | signed announcement on-chain |
| `miner.submit.failed` | miner | broadcast rejected |
| `validator.cycle.start` | validator | discover phase begins |
| `validator.cycle.end` | validator | weights committed |
| `validator.submission.scored` | validator | one submission's score vector committed |
| `validator.submission.rejected` | validator | per the fail-fast table in 12 |
| `validator.rerun.disagreement` | validator | rerun out of tolerance |
| `validator.oracle.disagreement` | validator | cross-cycle oracle disagreement (see 18) |
| `validator.rate_limit_exceeded` | validator | per-hotkey announcement cap hit |
| `runtime.sandbox.killed` | runtime | wallclock / mem / egress kill |
| `runtime.dataset.hash_mismatch` | runtime | pinned revision hash failed |

Operators consuming `events.jsonl` should treat unrecognised event
names as skippable (forward-compatibility); validators and miners
should not change semantics of existing event names.

#### Schema

Top-level event record shape is machine-checkable via
[`src/hypotheses/spec/schema/events.schema.json`](../../src/hypotheses/spec/schema/events.schema.json).
The `event` enum is authoritative — new values are added, old values
are never renamed. Per-event `data` payloads are currently untyped at
this tier; per-event sub-schemas may land under
`src/hypotheses/spec/schema/events/` in a follow-up PR if downstream
consumers need them.

## Service-level indicators

SLIs are the metrics an operator dashboards off. They're derived
from the event stream; no new emission paths are required.

### Miner SLIs

| sli | definition | healthy range |
|-----|------------|---------------|
| submission-success-rate | fraction of `miner.submit.broadcast` that are NOT followed by a `validator.submission.rejected` for the same `announcement_cid` | ≥ 0.95 over a 24h window |
| reproduction-pass-rate | fraction of rerun-sampled seeds that agree with declared metrics | ≥ 0.98 over a 24h window |
| wallclock-per-submission (p50, p95) | time from `miner.run.start` to `miner.submit.broadcast` | within the declared `hardware_profile`'s wallclock cap |
| novelty-capture-rate | fraction of submissions that earn novelty ≥ 0.5 | operator-choice; informational |

### Validator SLIs

| sli | definition | healthy range |
|-----|------------|---------------|
| cycle-duration (p50, p95) | `validator.cycle.end.ts − validator.cycle.start.ts` | p95 ≤ 20 minutes (the cadence) |
| rerun-agreement-rate | fraction of rerun-sampled seeds agreeing with miner-declared metrics | ≥ 0.98 (low rate = spec bug or dishonest miners) |
| rejection-reason distribution | counts of `validator.submission.rejected` by `data.reason` | no single reason > 20% over 24h |
| weight-commit-success-rate | fraction of cycles that successfully set weights | ≥ 0.99 |
| consensus-outlier-distance | cosine distance between this validator's weight vector and the network consensus | ≤ 0.05 (persistent outlier = bug or collusion signal) |

### Subnet-wide SLIs (for the maintainer)

| sli | definition |
|-----|------------|
| registry health | count of hypotheses by status, per week |
| settlement latency | time from `accepted` to first `settled-*`, per hypothesis |
| oracle verdict latency | p95 wallclock for `OracleVerdict` queries |
| CI health | pass rate of `main`-branch CI runs over 7 days |
| mutation-score trend | per-module trend week over week |

## Service-level objectives

SLOs are operator-local — each miner or validator sets their own.
The spec defines only defaults; operators who care about reputation
target tighter numbers.

**Default SLO targets:**

- **Miner:** submission-success-rate ≥ 0.95 over a 7-day window.
- **Validator:** cycle-duration p95 ≤ 20 minutes over a 24h window.
- **Validator:** consensus-outlier-distance ≤ 0.05.

A validator persistently outside the consensus-outlier SLO risks
YUMA-downweighting; that's the economic feedback loop, not an
alert.

## Alerts

Alerts convert SLI breaches into named conditions that point at
runbooks. The spec defines which conditions exist; the alerting
tooling (Prometheus, Grafana, operator scripts) is operator-choice.

### Miner alerts

| name | condition | runbook |
|------|-----------|---------|
| `miner.submission_failure_cluster` | >3 `miner.submit.failed` within 1h | [R-M1](#r-m1--submission-rejected) |
| `miner.reproduction_regression` | reproduction-pass-rate < 0.90 over 24h | [R-M2](#r-m2--reproduction-failing) |
| `miner.sandbox_killed` | any `runtime.sandbox.killed` | [R-M3](#r-m3--sandbox-kill) |
| `miner.artifact_unreachable` | validator `get_artifact` failures against this hotkey | [R-M4](#r-m4--artifact-unreachable) |

### Validator alerts

| name | condition | runbook |
|------|-----------|---------|
| `validator.cycle_stalled` | no `validator.cycle.end` for > 2× cadence | [R-V1](#r-v1--cycle-stalled) |
| `validator.rerun_disagreement_spike` | rerun-agreement-rate < 0.90 over 1h | [R-V2](#r-v2--rerun-disagreement-spike) |
| `validator.oracle_outage` | ≥ 24h continuous oracle unavailable | [R-V3](#r-v3--oracle-outage) |
| `validator.ipfs_outage` | `StorageUnavailable` rate > 10% over 1h | [R-V4](#r-v4--ipfs-outage) |
| `validator.consensus_outlier` | consensus-outlier-distance > 0.05 for 3 consecutive cycles | [R-V5](#r-v5--consensus-outlier) |
| `validator.weight_commit_rejected` | any `set_weights` extrinsic rejected | [R-V6](#r-v6--weight-commit-rejected) |

### Repo / CI alerts

Repo-level alerts fire from GitHub notifications or the maintainer's
watch of the Security / Actions tabs. No separate alerting
infrastructure — GitHub is the pager.

| name | condition | runbook |
|------|-----------|---------|
| `ci.main_red` | any workflow failure on `main` | [R-R1](#r-r1--main-ci-red) |
| `ci.secret_detected` | push-protection or secret-scanning fires | [R-R2](#r-r2--secret-detected) |
| `ci.advisory_critical` | `pip-audit` or CodeQL publishes a critical finding | [R-R3](#r-r3--critical-advisory) |
| `ci.mutation_regression` | mutation score drops > 5 points week over week | [R-R4](#r-r4--mutation-regression) |

## Runbooks

Each runbook has the same shape: **trigger → impact → diagnose →
mitigate → rollback / close**. Keep commands readable; assume `gh`
and `uv` are available.

### R-M1 — Submission rejected

- **Trigger.** Cluster of `miner.submit.failed` events.
- **Impact.** Miner hotkey emits nothing this epoch.
- **Diagnose.** Check `events.jsonl` for the `data.reason` — the
  fail-fast table in
  [12](12-implementation-constraints.md#fail-fast-policy) lists
  every rejection cause. Most common: `SignatureInvalid`,
  `EnvMismatch`, `ArtifactCorrupt`.
- **Mitigate.** Signature issues: re-sign (the MCP server's
  signing key may have rotated). Env mismatch: rebuild the pinned
  env from `uv.lock`. Artifact corrupt: re-upload from the canonical
  `run.manifest.json`.
- **Close.** Next epoch's submission lands cleanly.

### R-M2 — Reproduction failing

- **Trigger.** `miner.reproduction_regression` alert.
- **Impact.** Validators score miner zero until the underlying
  cause is fixed.
- **Diagnose.** Pull a failing rerun via
  `hypo submissions show <cid>`, compare declared metrics to the
  validator's rerun. Likely causes: non-determinism (unpinned
  CUDA/BLAS env, missing
  `torch.use_deterministic_algorithms(True)`), dataset hash drift,
  or hardware-profile mismatch.
- **Mitigate.** Re-run locally in the exact hardware profile's
  sandbox image; verify byte-identical `metrics.jsonl` across two
  seed=0 runs. If identical locally but diverging in validator
  runs, raise a
  [`spec-question` issue](../../.github/ISSUE_TEMPLATE/spec-question.yml)
  — the hypothesis's `rerun_tolerance` may be tighter than the
  profile supports.
- **Close.** Bump the hypothesis's `version` with a corrected
  protocol if the issue is spec-side; otherwise resubmit.

### R-M3 — Sandbox kill

- **Trigger.** `runtime.sandbox.killed`.
- **Impact.** That seed's metrics are absent; submission fails.
- **Diagnose.** `data.reason` names the cap hit: `wallclock`,
  `memory`, `egress`. Check `stderr.log` in the artifact bundle
  for the last lines.
- **Mitigate.** Wallclock: move to a larger hardware profile via a
  hypothesis version bump. Memory: same. Egress: the experiment
  reached out to a non-allowlisted URL — fix the code, never the
  allowlist.
- **Close.** Successful run on the next attempt.

### R-M4 — Artifact unreachable

- **Trigger.** Validators report `StorageUnavailable` on
  `GetArtifact` against this miner.
- **Impact.** Validator reruns cannot complete; submission stays
  `pending`; at the cycle deadline (24h) the validator moves on
  and this submission never scores.
- **Diagnose.** `ipfs pin ls | grep <cid>` on the miner's node.
  If the CID is missing, it was evicted or never pinned.
- **Mitigate.** Re-pin the bundle from the local cache. If the
  local cache is gone, the submission is unrecoverable —
  resubmission against the same version after the miner's bundle
  is re-produced and re-uploaded.
- **Close.** Validator `get_artifact` succeeds on next rerun.

### R-V1 — Cycle stalled

- **Trigger.** `validator.cycle_stalled`.
- **Impact.** This validator misses the epoch's weight-set window;
  scores aren't committed.
- **Diagnose.** Check validator stderr for the last log line. Most
  common cause: the rerun of one submission hangs. Look for a
  missing `validator.submission.scored` between two
  `cycle.start`s.
- **Mitigate.** Kill and restart the validator. The next cycle
  picks up remaining submissions.
- **Close.** Two consecutive cycles complete inside cadence.

### R-V2 — Rerun disagreement spike

- **Trigger.** `validator.rerun_disagreement_spike`.
- **Impact.** Either dishonest miners (expected, caught by the
  design) or a spec bug (hypothesis's `rerun_tolerance` too tight
  for the profile) or a runtime bug (this validator's sandbox is
  nondeterministic in a way peers aren't).
- **Diagnose.** Group `validator.rerun.disagreement` events by
  `data.hypothesis_id`. If >1 hypothesis affected, suspect a
  runtime bug on this validator. If 1 hypothesis across many
  miners, suspect the spec.
- **Mitigate.** Runtime bug → restart with a fresh sandbox image.
  Spec bug → open a
  [`spec-question`](../../.github/ISSUE_TEMPLATE/spec-question.yml)
  issue and notify the maintainer.
- **Close.** Rate returns above 0.95.

### R-V3 — Oracle outage

- **Trigger.** `validator.oracle_outage`.
- **Impact.** Oracle-gated submissions stay `pending`; miners wait.
- **Diagnose.** `hypo validate rescore <cid> --dry-run` reveals the
  oracle adapter's last exception. Cross-reference with the oracle
  subnet's status (for SN42: check SN42 dashboard).
- **Mitigate.** This is typically an upstream issue; wait. If the
  adapter itself is broken (traceback in the validator log, not a
  network timeout), upgrade the CLI. Do NOT skip the oracle check
  per
  [18 § outage handling](18-oracle.md#outage-handling).
- **Close.** A successful oracle verdict lands; pending submissions
  resume scoring.

### R-V4 — IPFS outage

- **Trigger.** `validator.ipfs_outage`.
- **Impact.** Validator can't fetch manifests or artifacts; cycles
  stall or skip.
- **Diagnose.** `ipfs id` on the local kubo node; if dead, daemon
  issue. If live, test with a known CID from a recent successful
  cycle.
- **Mitigate.** Restart kubo. If the pinning service is degraded,
  submissions remain unscored; they catch up when IPFS returns.
- **Close.** Fetch rate above 95% for one full cycle.

### R-V5 — Consensus outlier

- **Trigger.** `validator.consensus_outlier` for 3+ cycles.
- **Impact.** YUMA down-weights this validator; dividends drop.
- **Diagnose.** Compare this validator's score vector entry-by-entry
  against the consensus (`hypo validate audit <hotkey>` on a
  differing submission). If this validator disagrees on structural
  rejections (signature, schema), investigate for code drift. If
  on numerical reruns, investigate determinism.
- **Mitigate.** Bring the validator binary to `main` HEAD (or a
  known-good tag); restart. If the divergence persists, file a
  spec-question issue — disagreement on deterministic checks is a
  bug.
- **Close.** Consensus-outlier-distance ≤ 0.05 for 3 cycles.

### R-V6 — Weight commit rejected

- **Trigger.** `set_weights` extrinsic rejected by the chain.
- **Impact.** This cycle's scoring is not on-chain; emission unaffected
  if recovered next cycle.
- **Diagnose.** Typically: insufficient stake, validator not
  registered, or chain-side transient. Check wallet stake.
- **Mitigate.** If stake-related, top up. If transient, retry next
  cycle.
- **Close.** Successful `set_weights` on the following cycle.

### R-R1 — `main` CI red

- **Trigger.** Any workflow fails on `main`.
- **Impact.** Release tooling stalls; downstream users see a red
  README badge.
- **Diagnose.** `gh run view <run-id>`; identify the failing gate.
- **Mitigate.** Open a `fix:` PR with the minimum change to make
  the gate pass. Do NOT revert unless the root cause is a merged
  regression in this repo.
- **Close.** All gates green on the next `main` commit.

### R-R2 — Secret detected

- **Trigger.** GitHub push-protection blocks a push, or secret
  scanning fires post-push.
- **Impact.** Depends on what leaked; often trivial (dummy token)
  but always audited.
- **Diagnose.** Read the GitHub advisory; identify the secret and
  where it landed.
- **Mitigate.**
  - If blocked pre-push: remove the secret, force-push the amended
    commit.
  - If post-push: rotate the secret immediately; open a security
    advisory (not an issue) per
    [`SECURITY.md`](../../SECURITY.md); git history rewrite only
    if the maintainer authorises.
- **Close.** Secret invalidated at the source; advisory published
  after rotation.

### R-R3 — Critical advisory

- **Trigger.** `pip-audit` or CodeQL reports CRITICAL / HIGH.
- **Impact.** Exploitability window open.
- **Diagnose.** Read the advisory; determine whether the
  vulnerable path is reachable in our usage.
- **Mitigate.** Bump the dep; Dependabot typically has an open PR
  already. Merge, test, release patch. If no upstream fix exists,
  pin around the issue or vendor a patched copy — in both cases,
  ADR required.
- **Close.** `pip-audit` green on next scheduled run.

### R-R4 — Mutation regression

- **Trigger.** Nightly mutation score drops > 5 points week over
  week.
- **Impact.** Tests are weaker than they were; real regressions
  may slip.
- **Diagnose.** `mutmut results --survived` highlights surviving
  mutants. Group by module.
- **Mitigate.** Strengthen the weakest tests; the 75% per-module
  floor is a hard gate but not the goal. A good suite sits at 85+%.
- **Close.** Score returns above last week's baseline.

## Disaster recovery

Low-frequency, high-impact scenarios.

### Lost coldkey

An operator's coldkey is the economic identity for a miner or
validator. If lost:

- **Emission already accrued is lost** (there's no Bittensor-side
  recovery).
- **Immediately rotate** the hotkeys attached to that coldkey (if
  possible from a backup) onto a new coldkey.
- **Re-register** the replacement on the subnet; prior reputation
  does not transfer.

Prevent: offline / hardware-wallet custody of coldkeys per
Bittensor's own recommendations.

### Lost hotkey

Miner/validator hotkey. Same operational flow as lost coldkey,
scoped to one role:

- Unregister the lost hotkey (if possible).
- Register a new hotkey on the same coldkey.
- Announce the rotation in public channels — prior submissions tied
  to the old hotkey keep their attribution forever (public on-chain
  history), but new submissions come from the new hotkey.

### Corrupt artifact cache

Local validator cache hash mismatches. Not a subnet-level incident:

- Stop the validator.
- `rm -rf <cache-dir>` and restart; the cache repopulates from
  re-fetch.
- If cache corruption recurs, underlying disk is failing — replace
  hardware before resuming.

### IPFS pinning service failure

The subnet operator's kubo node (pinning manifests) fails:

- Spin up a replacement kubo node and re-pin all manifests from the
  on-chain announcement log. A script to re-pin is shipped in
  `scripts/` when the pinning service ships (Phase 2).
- Bulk artifacts (weights, etc.) are the miner's responsibility per
  [09 § storage](09-protocol.md#storage); re-pinning is not the
  subnet's job.
- Prevent: the pinning node backs up its pinset daily (operator
  concern, not spec'd here).

### Compromised maintainer account

Worst case, and the reason
[`GOVERNANCE.md`](../../GOVERNANCE.md) exists. If the maintainer's
GitHub account is compromised:

- **Freeze `main`.** Temporary branch protection, merge lock, or —
  if unavoidable — revoke the maintainer's write access until
  recovery.
- **Audit** every commit from the suspect window for malicious
  inserts. SHA-pinned actions help: a tampered commit would
  include a changed SHA reference.
- **Rotate credentials.** New GPG key for signed commits (if
  adopted), new GitHub PAT if any is in use by automation.
- **Post-mortem ADR** documenting the incident and lessons.

AGPL provides a forking escape hatch: if the maintainer cannot
recover, contributors can fork the repo and continue. That's not a
recovery — it's a last-ditch continuity option.

## Non-goals

- **Prescribing a specific observability stack.** Operators choose
  Prometheus, VictoriaMetrics, OpenTelemetry, or just grepping
  `events.jsonl`. The spec defines the *signal*; the *sink* is
  local.
- **Paging rotations.** Who answers which alert, on what schedule,
  is operator-choice. The spec names the alerts; the roster is not
  its business.
- **Custom dashboards.** The SLI definitions are enough for an
  operator to build whatever dashboard they want.

## References

- [12 § logging](12-implementation-constraints.md#logging--observability)
  — log format is spec'd here.
- [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy)
  — every alert maps to a typed exception.
- [05 — Validator](05-validator.md) — the role being operated.
- [04 — Miner](04-miner.md) — same, for miners.
- [18 § outage](18-oracle.md#outage-handling) — oracle-specific.
- [`SECURITY.md`](../../SECURITY.md) — private advisory flow.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) — who has authority during
  incidents.

## Self-audit

This doc is done when:

- Every alert name maps to exactly one runbook.
- Every runbook has trigger, impact, diagnose, mitigate, close —
  no hand-waving.
- Every event name in the `events.jsonl` table is emitted by a
  specific component in `src/hypotheses/`.
- Every DR scenario names the affected asset from
  [16 § assets](16-threat-model.md#assets).
- No observability stack is prescribed (operator-choice), but
  every SLI is derivable from the spec'd event stream.

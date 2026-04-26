---
name: oracle contract
description: interface, composition, outage semantics, and SN42 adapter for ground-truth oracles
tokens: 3300
load_for: [implementation, agent-operator, review]
depends_on: [02, 06]
kind: contract
---

# 18 — Oracle contract

Some hypotheses make claims the subnet can't verify by reproducing a
training run: "this model's prediction matches the correct answer
for task X." When the answer is knowable through an external source,
we call that source an **oracle**. This document specifies the
contract every oracle adapter must satisfy — what it's asked, what
it returns, how disagreements and outages are handled, and how a
new oracle is added to the subnet.

The first supported oracle is SN42 (known-answer). The contract is
written oracle-agnostic so new ones plug in without disturbing
validator or scoring logic.

## What an oracle provides

An oracle turns a pair `(task_ref, declared_answer)` into a verdict:

```text
query(task_ref, declared_answer, tolerance) -> OracleVerdict
```

- `task_ref` — opaque-to-the-subnet identifier that the oracle
  understands. For SN42 this is a task index in the oracle's
  published manifest.
- `declared_answer` — the miner's claimed output for that task,
  copied verbatim from the submission manifest.
- `tolerance` — numerical envelope within which declared and oracle
  answers count as agreeing. Exact meaning depends on the metric
  space; the oracle adapter defines it per task-type.

The verdict is the oracle's judgment, not the subnet's. The scoring
pipeline combines it with reproduction and improvement checks per
[06 § oracles](06-scoring.md#oracles).

## Oracle classes

Exactly one class per adapter. Classes differ in how the answer is
produced and how confidence is established.

### Known-answer

The oracle has ground truth — an answer it considers correct
independent of any miner's claim. SN42 is the first example:
pre-computed answers are published; the oracle verifies the miner's
claim against them.

Properties:

- **Deterministic.** Two queries with the same
  `(task_ref, declared_answer)` return the same verdict within a
  single oracle-state window.
- **Stateless-from-the-subnet's-view.** Validators don't need to
  coordinate; each queries independently and gets the same answer.
- **No staleness concerns for finalized tasks.** If `task_ref`
  refers to a finalized oracle task, the answer does not change.

### Consensus-answer

The oracle aggregates multiple sources (typically a Bittensor subnet
of its own) and returns the consensus at query time. Example: a
future subnet whose validators vote on a prediction's correctness.

Properties:

- **Eventually deterministic.** The oracle's own consensus needs to
  settle. Querying before settlement may return a provisional
  verdict flagged `final: false`.
- **Confidence-bearing.** The verdict carries the consensus fraction
  and the set of contributing hotkeys so validators can reason
  about quorum.

### Private oracles

**Not in scope.** Oracles hosted behind auth walls violate the
subnet's "bottom-up, not top-down" commitment and would create
privileged validator relationships. If a hypothesis needs a private
source, it cannot declare `oracle: ...` and must rely on
reproduction + baseline comparison alone.

## The `OracleVerdict`

Adapters return a structure equivalent to:

```python
@dataclass(frozen=True)
class OracleVerdict:
    agrees: bool                            # declared matches oracle within tolerance
    oracle_answer: object                   # what the oracle says is correct
    distance: float                         # metric-specific; 0.0 when agrees=True in an exact match
    oracle_class: Literal["known-answer", "consensus-answer"]
    at_block: int                           # bittensor block height of the query
    final: bool                             # known-answer: always True; consensus-answer: True once oracle settled
    # populated only for consensus-answer:
    consensus_fraction: float | None        # in [0, 1]
    source_hotkeys: list[str] | None        # validator set that contributed
    # always set:
    adapter_version: str                    # e.g. "sn42-omron/1.3.0"
    query_wallclock_ms: int
```

This dataclass is the wire contract. The serialised form is
canonical JSON; adapters produce identical byte-level output for
identical inputs (same oracle-state window).

Failure to produce a verdict (oracle unreachable, adapter crash,
malformed response) is NOT an empty verdict. It's an exception —
see "Outage handling" below.

## Registering an oracle

Adding a new oracle is a spec change:

1. **ADR** under `docs/adr/` naming the oracle, its class, the
   authority model behind it, and the registration rationale.
2. **Adapter skeleton** committed under
   `src/hypotheses/oracle/<name>.py` (Phase 1+; stub acceptable
   until Phase 2).
3. **Allow-list entry** in
   [`hypothesis.schema.json`](../../src/hypotheses/spec/schema/hypothesis.schema.json)
   if the adapter exposes a new `subnet` integer or new task-ref
   format.
4. **Threat entries** in
   [16 — Threat model § G](16-threat-model.md#g-oracle-attacks)
   for oracle-specific attack surfaces the new adapter introduces.
5. **Maintainer approval.** Oracle additions are governance-
   sensitive (they become scoring gates) and require maintainer
   sign-off per [`GOVERNANCE.md`](../../GOVERNANCE.md).

New oracles do not appear to validators until the adapter is
released with the CLI version that understands them. Cross-version
behaviour: a validator running an older CLI that encounters a
newer-oracle hypothesis refuses to score rather than silently
skipping the oracle check.

## Composition

> **HM-REQ-0080** When a hypothesis declares an `oracle.oracles`
> array of length ≥ 2, it MUST also declare `oracle.composition`.
> Composition rules MUST resolve disagreement deterministically —
> no LLM judgment, no timing-dependent ordering, no per-validator
> tiebreaks.

The `oracle` field admits two shapes:

- **Single oracle** (the `oracle_single` form, equivalent to the
  legacy singular block). One oracle, mandatory agreement. Scores
  zero on disagreement; stays `pending` on outage.
- **Composed oracles** (the `oracle_composed` form: an `oracles`
  array plus a `composition` rule). Defends against single-oracle
  corruption (cf. [00.5 § F3](00.5-foundations.md#f3--oracle-corruption)).

### Composition rules

| rule | semantics | passes when | scores zero when | stays pending when |
|------|-----------|-------------|------------------|---------------------|
| `all_agree` | logical AND | every oracle agrees within its own tolerance | any oracle disagrees | any oracle is unavailable |
| `majority` | simple majority | > 50% of oracles agree | ≥ 50% disagree | < 50% have responded |
| `weighted_majority` | stake-weighted | weighted sum of agreeing oracles > 0.5 | weighted sum of disagreeing > 0.5 | weighted sum of responded ≤ 0.5 |

Outage is *never* silently treated as agreement or disagreement.
Per HM-REQ-0070's two-tier settlement, oracle-pending submissions
remain `pending` until either the oracle returns or the rerun
window expires.

### When to use which

- `all_agree` is the conservative default for high-stakes claims
  where any single corrupted oracle would mislead the score. Use
  when 2–3 oracles cover the *same* underlying truth (mirror
  oracles, redundant data sources). Cost: brittle to outage.
- `majority` is appropriate when oracles are independent estimators
  of a noisy ground truth (different model families on the same
  task, different data slices). Tolerates one outlier or one
  outage among 3+ oracles.
- `weighted_majority` is for when oracles have *known* differing
  reliability — e.g., a trusted on-chain oracle weighted higher
  than a community-run mirror. Weights are declared per-oracle in
  the hypothesis spec; they MUST sum to a value where 0.5 is the
  effective threshold (no implicit normalisation).

### Backwards compatibility

Existing hypotheses (H-0001…H-0006) keep the singular `oracle`
form. The schema's `oneOf` admits both shapes; validators dispatch
on shape at scoring time. A hypothesis MAY upgrade from singular
to composed via a `version` bump (HM-INV-0002 invalidates the prior
version's settlements as usual).

### Why these three and not others

- **Why no `unanimous` separate from `all_agree`?** Same semantics;
  `all_agree` is the canonical name.
- **Why no `quorum` (e.g., "any 2-of-3")?** `weighted_majority`
  with equal weights subsumes it; explicit quorum can land later
  if a hypothesis needs it without weights.
- **Why no `trust_root` (one oracle is authoritative, the rest
  advisory)?** This collapses to `single` with the others as
  metadata; we don't need a new composition mode for it.

Adding a fourth composition rule requires a spec PR + ADR +
acceptance scenarios in this section.

## Disagreement handling (same-oracle, cross-cycle)

Scenario: validator A queries the oracle on cycle N and gets
`agrees=True`; validator B queries the same oracle on cycle N+1 and
gets `agrees=False` for the same `(task_ref, declared_answer)`.

Rules:

1. **Known-answer oracles MUST NOT disagree with themselves on a
   finalized task.** If they do, the adapter reports
   `OracleInconsistent` via an `errors.py`-defined exception. The
   validator operator layer flags it; the submission stays
   `pending` for this cycle; no score is committed.
2. **Consensus-answer oracles may legitimately evolve.** The
   scoring layer requires **N consecutive consistent verdicts**
   across validator cycles before accepting the verdict as final.
   Default `N = 3`, configurable per oracle adapter; lower bound 1
   for known-answer oracles (trivially satisfied).
3. **Miners are not penalised for cycle-transient disagreement.**
   Their submission sits `pending` until the oracle stabilises or
   the operator escalates.
4. **Logging.** Every disagreement gets an `events.jsonl` entry
   with `oracle.disagreement` and the two verdicts side by side.
   Persistent disagreement across >24 hours raises an operational
   alert per [15 § 18-operations.md](15-ci-cd.md#deferred--planned).

## Outage handling

When an oracle query cannot complete (network, adapter crash, rate
limit, upstream down), the adapter raises the appropriate typed
exception from
[`src/hypotheses/errors.py`](../../src/hypotheses/spec/schema/hypothesis.schema.json)
per the fail-fast table in
[12 § fail-fast](12-implementation-constraints.md#fail-fast-policy).

Validator behaviour:

- Mark the submission `pending` on this cycle.
- Re-examine on the next cycle.
- After **24 hours** continuously unable to reach the oracle,
  surface an alert to the operator (the operator layer's
  responsibility; not the scoring layer's).
- **Do NOT** degrade to "skip the oracle and score anyway." This is
  the spec's fail-fast commitment — missing the oracle when one was
  declared is exactly the wrong moment to be lenient.

Mining against an oracle-backed hypothesis during an oracle outage
is safe for the miner — their submission is preserved and will be
scored when the oracle returns. There is no deadline within a cycle
beyond which a submission is lost.

## SN42 adapter (first implementation)

SN42 is a known-answer oracle. The adapter specification:

- **Adapter path:** `src/hypotheses/oracle/sn42.py`
- **Adapter version string:** `sn42-omron/<release>`
- **Task-ref format:** an opaque string of the form
  `sn42:<task-index>` where `<task-index>` is the position in the
  SN42-published task manifest at the time of the miner's
  submission. The task-index is fixed across oracle-state windows
  for finalized tasks.
- **`declared_answer` shape:** exactly what SN42 expects per the
  task type; the hypothesis spec's `oracle.task_ref` uniquely
  determines the shape.
- **Tolerance interpretation:** for numeric tasks, `tolerance` is
  the absolute difference between declared and oracle answer beyond
  which `agrees=False`; for boolean/categorical tasks, `tolerance`
  must be `null` and agreement is strict equality.
- **Query mechanism:** via Bittensor dendrite to SN42 validators;
  the response payload is SN42-defined. The adapter normalises the
  response into an `OracleVerdict`.
- **Stability guarantee:** SN42's published task answers are
  immutable once finalized. If SN42 publishes a correction, that
  correction is a new task-index, not a mutation of an existing
  one; hypotheses that referenced the old index keep their verdicts
  stable.

**Phase alignment.** The adapter ships as a stub in Phase 1
(`raise NotImplementedError` for non-null oracle hypotheses — same
behaviour as "no supported oracle"). The real SN42 adapter lands
before the Phase 2 exit; the Phase 1 exit does NOT require it.

## Interaction with scoring

From [06 § oracles](06-scoring.md#oracles), the scoring pipeline's
oracle step is a **hard gate**:

```python
if oracle.subnet is set:
    verdict = adapter.query(task_ref, declared_answer, tolerance)
    if not verdict.final:
        return ScoreVector.pending()      # re-examine next cycle
    if not verdict.agrees:
        return ScoreVector.zero()
    # continue to other score components
```

`ScoreVector.pending()` is a distinct sentinel from `.zero()` —
pending submissions do not yet have a score, rather than having
scored zero. This distinction matters for rigor and cost
accounting.

## Threats and mitigations

The oracle attack surface is captured in
[16 § G](16-threat-model.md#g-oracle-attacks). Summary with
pointers:

- **T-060 — miner games SN42.** Hard gate defence: scoring zero
  when the oracle disagrees within tolerance. Miners cannot tune
  around this; the oracle answer is the ground truth.
- **T-061 — oracle disagrees with itself across cycles.** Mitigated
  by the consistency requirement (N consecutive matching verdicts)
  plus operator-layer alerting on persistent disagreement. The
  former defers attribution; the latter surfaces the spec bug.
- **T-062 — oracle subnet outage.** Fail-fast: submission stays
  `pending`; no degraded scoring. Aligns with
  [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy).

## Non-goals

- **Human-in-the-loop oracles.** Oracles are automated only.
  Manual-review answer sources aren't verifiable per-validator and
  create privileged relationships.
- **Off-chain oracles.** If the oracle's authority depends on a
  server the subnet doesn't control, it's out. Bittensor-internal
  oracles or cryptographically-verifiable external oracles only.
- **Oracle-as-scoring.** An oracle gates the score; it does not
  produce it. Scoring stays deterministic per
  [05 § two layers](05-validator.md#two-layers-deterministic-core-and-operator-layer).

## References

- [06 § oracles](06-scoring.md#oracles) — how verdicts enter the
  composite score.
- [02 § spec fields](02-hypothesis-format.md#spec-fields) — where a
  hypothesis declares its oracle.
- [16 § G](16-threat-model.md#g-oracle-attacks) — oracle attack
  surface.
- [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy)
  — why outage = pending, not score-anyway.
- [17 § edge cases](17-hypothesis-lifecycle.md#oracle-unavailable) —
  what "pending" means for lifecycle transitions.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) — oracle additions require
  maintainer approval.

## Acceptance scenarios

```gherkin
Scenario: Oracle agrees — submission scored normally
  Given hypothesis H declares oracle.subnet = 42
  And oracle.tolerance = 0.01
  And a miner submits a declared_answer of 0.710
  And the oracle returns ground truth 0.715
  When the validator runs the scoring pipeline
  Then |declared_answer − oracle_answer| = 0.005 ≤ tolerance
  And the deterministic core proceeds to composite scoring
```

```gherkin
Scenario: Oracle disagrees — submission zeroed
  Given hypothesis H declares oracle.subnet = 42
  And oracle.tolerance = 0.01
  And a miner submits declared_answer = 0.800
  And the oracle returns 0.710
  When the validator runs the scoring pipeline
  Then |declared − oracle| = 0.090 > tolerance
  And the composite score vector is zero
  And the rejection is logged as "OracleDisagreement"
```

```gherkin
Scenario: Oracle outage — submission stays pending, never silently skipped
  Given hypothesis H declares oracle.subnet = 42
  And the oracle subnet responds with OracleUnavailable
  When the validator attempts to score the submission
  Then the submission's status is pending (not rejected, not settled)
  And the pipeline retries on the next cycle
  And at no point does the validator compute a composite without the oracle check
```

```gherkin
Scenario: all_agree composition — one disagreeing oracle zeros the score
  # spec: HM-REQ-0080
  Given hypothesis H declares oracle.composition = "all_agree"
  And oracle.oracles is [{sn:42}, {sn:43}]
  And the miner submits declared_answer = 0.710
  And oracle 42 returns 0.712 (within tolerance)
  And oracle 43 returns 0.795 (outside tolerance)
  When the validator runs the scoring pipeline
  Then the composite score vector is zero
  And the rejection is logged as "OracleDisagreement(all_agree)"
```

```gherkin
Scenario: majority composition — one disagreeing oracle does not zero the score
  # spec: HM-REQ-0080
  Given hypothesis H declares oracle.composition = "majority"
  And oracle.oracles is [{sn:42}, {sn:43}, {sn:44}]
  And oracles 42 and 44 agree within tolerance
  And oracle 43 disagrees
  When the validator runs the scoring pipeline
  Then 2 of 3 oracles agreed → majority threshold met
  And the deterministic core proceeds to composite scoring
```

```gherkin
Scenario: weighted_majority composition — high-weight oracle decides
  # spec: HM-REQ-0080
  Given hypothesis H declares oracle.composition = "weighted_majority"
  And oracle.oracles is [{sn:42, weight:0.6}, {sn:43, weight:0.4}]
  And oracle 42 agrees within tolerance
  And oracle 43 disagrees
  When the validator runs the scoring pipeline
  Then weighted-agreement = 0.6 > 0.5 threshold
  And the deterministic core proceeds to composite scoring
  And the rejection log notes oracle 43 disagreed but did not block
```

```gherkin
Scenario: weighted_majority — partial outage stays pending when threshold unreachable
  # spec: HM-REQ-0080
  Given hypothesis H declares oracle.composition = "weighted_majority"
  And oracle.oracles is [{sn:42, weight:0.6}, {sn:43, weight:0.4}]
  And oracle 42 is unavailable
  And oracle 43 agrees within tolerance
  When the validator runs the scoring pipeline
  Then responded weight = 0.4 ≤ 0.5 threshold
  And the submission stays pending (not zeroed, not settled)
  And at no point does the validator silently skip the unresponded oracle
```

## Self-audit

This doc is done when:

- The interface signature (`query(...)` and `OracleVerdict`) is
  implementable as a pure-function stub in `src/hypotheses/oracle/`
  without further clarification.
- Every oracle class has enforceable criteria distinguishing it
  from the others.
- The disagreement and outage rules are compatible with the
  fail-fast policy in
  [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy).
- Registration process requires the same artifacts (ADR, adapter,
  schema entry, threat entry) in every case.
- Multi-oracle composition is either specified or explicitly
  deferred — no half-state.

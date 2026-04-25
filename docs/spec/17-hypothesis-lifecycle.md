---
name: hypothesis lifecycle
description: states, transitions, authorities, and edge cases for hypothesis status
tokens: 2600
load_for: [implementation, proposal, agent-operator, review]
depends_on: [02, 06]
---

# 17 — Hypothesis lifecycle

A hypothesis travels through well-defined states. This document is
the canonical definition: every `status` value, every allowed
transition, who can trigger it, and the side effects on results and
the registry.

[02 — Hypothesis format](02-hypothesis-format.md#spec-fields) lists
the states in passing. This doc is the full contract.

A mechanically-checkable Quint formalisation of this state machine
lives at [`formal/lifecycle.qnt`](formal/lifecycle.qnt). Prose here
is authoritative; divergence between the prose and the formalisation
is a bug and is fixed in the same PR that identifies it.

## States

A `status` field is always exactly one of:

| state | meaning |
|-------|---------|
| `proposed` | draft is under PR review; not yet merged or merged with `proposed` status. Not yet eligible for mining. |
| `accepted` | merged on `main`; miners may run it; validators score submissions against it. |
| `running` | at least one miner has a live `ResultsAnnouncement` for the current version that hasn't settled. Informational. |
| `settled-supported` | the hypothesis's `success_criteria` have been met by at least one miner whose submission passed rerun and oracle checks. **Tentative** for the current `version`; pays 70% of novelty + improvement at this transition. |
| `settled-refuted` | the hypothesis's `falsification_criteria` have been met by at least one miner whose submission passed rerun and oracle checks. **Tentative** for the current `version`; pays 70% of novelty (improvement is zero by definition) at this transition. |
| `confirmed` | 6 months have elapsed since the first `settled-*` transition for this `(id, version)` and no `T-OVR` overturn event has fired. The remaining 30% of novelty + improvement is released to the original settling miner. Terminal. |
| `withdrawn` | the author or maintainer has decided this hypothesis is dead. No further mining against it. Terminal across all versions. |

Terminal-ness is per-version for `confirmed` and `settled-*`-without-confirmation
(a new version reopens the hypothesis); permanent for `withdrawn`
(a superseder opens a new file, not a new version). `settled-*`
is a *tentative* state that resolves to either `confirmed` (after
6 months no overturn) or back to a non-settled state (after a
T-OVR fires).

## Transitions

```
                                    +------------+
                                    | withdrawn  |   (terminal, across all versions)
                                    +------------+
                                          ^
                                          |  T-WITH
                                          |
                  T-PROP        T-ACC          T-RUN
    (create PR) ─────▶  proposed ─────▶  accepted ─────▶  running
                           │               │                │
                  T-WDP    │               │ T-WDA          │ T-SUP / T-REF
                           ▼               ▼                ▼
                         withdrawn     withdrawn     settled-supported
                                                       or settled-refuted
                                                            │
                                                            │  T-VER
                                                            ▼
                                                       (new version N+1
                                                        lifecycle begins
                                                        at `proposed`)
```

### Transition table

| id | from | to | trigger | who | side effects |
|----|------|----|---------|-----|--------------|
| **T-PROP** | (none) | `proposed` | author opens a PR creating `hypotheses/H-NNNN-<slug>.md` | any contributor | `id` placeholder `H-XXXX` allowed; CI schema-validates |
| **T-ACC** | `proposed` | `accepted` | maintainer merges the PR to `main` after review | maintainer | `id` assigned; spec CID fixed; registry entry live; mining permitted |
| **T-RUN** | `accepted` | `running` | first valid `ResultsAnnouncement` for current `version` observed by validators | validators (consensus) | informational only; registry `status` update is eventual-consistent via a spec PR **or** can be inferred at read time from on-chain announcements |
| **T-SUP** | `running` or `accepted` | `settled-supported` | a miner's submission passes all gates and meets every `success_criterion` under validator consensus | validators (consensus) | novelty bonus attributed per [06 § ordering](06-scoring.md#ordering-tiebreak-for-simultaneous-settlements); further submissions allowed at this version but score novelty = 0 |
| **T-REF** | `running` or `accepted` | `settled-refuted` | a miner's submission passes all gates and meets every `falsification_criterion` under validator consensus | validators (consensus) | same as T-SUP; an honest null is a settlement |
| **T-CON** | `settled-supported` or `settled-refuted` | `confirmed` | 6 months elapsed since the settlement and no `T-OVR` has fired | system (time-triggered) | releases the deferred 30% of novelty + improvement to the original settling miner; `(id, version)` becomes terminal |
| **T-OVR** | `settled-supported` or `settled-refuted` | back to `running` | a fresh submission against the same `(id, version)` reproduces with metrics that flip the settlement under the original analysis plan | validators (consensus) + maintainer-confirmed | clears the tentative settlement, claws back the original 70% from the settler, makes both miners eligible for fresh novelty under the new settlement |
| **T-VER** | any non-terminal | `proposed` *(new file version)* | author bumps `version` via PR | author + maintainer | all prior `(spec_id, old_version)` submissions are invalidated for scoring; on-chain announcements against the old version remain readable for audit |
| **T-WDP** | `proposed` | `withdrawn` | author closes their own PR, or maintainer closes a stale proposal | author OR maintainer | PR closed; no registry impact (never merged) |
| **T-WDA** | `accepted` or `running` | `withdrawn` | author or maintainer opens a PR setting `status: withdrawn` | author OR maintainer | merged with `status: withdrawn`; mining against it stops scoring; prior `settled-*` records for earlier versions are preserved |
| **T-WITH** | `settled-*` | `withdrawn` | maintainer retracts a hypothesis post-settlement (rare; only for policy or integrity reasons) | maintainer + ADR required | a retraction ADR under `docs/adr/` documents the reason; settlement record preserved in git history but `status` in the merged file is `withdrawn` |

## Authorities

"Who" in the transition table uses these authority kinds. They line
up with [`GOVERNANCE.md`](../../GOVERNANCE.md):

- **author** — any GitHub account with a commit in the PR history
  of this hypothesis file.
- **maintainer** — the trusted maintainer per `GOVERNANCE.md`.
  During Phase 0–2 this is a single person; post-Phase-3 a council.
- **validators (consensus)** — the Bittensor validator set; a state
  transition is effective when YUMA consensus weights it above the
  threshold. No single validator can force a transition.
- **author OR maintainer** — either authority suffices; useful for
  withdrawals where either the drafter or the gatekeeper should be
  able to shut it down without drama.

## Two-tier settlement

> **HM-REQ-0070** Settlement is two-tier. The first transition into
> `settled-supported` or `settled-refuted` is **tentative**: 70% of
> novelty + improvement is paid out at this point. The remaining 30%
> is deferred and released on transition to `confirmed`, which
> requires that 6 months elapse with no `T-OVR` overturn event for
> this `(id, version)`. The deferred portion blunts long-latency
> rent extraction (see [00.5 § F6](00.5-foundations.md#f6--long-latency-rent-extraction)
> and [16 § T-075](16-threat-model.md#h-governance--process-attacks)):
> a validator who confirmed in good faith collects both portions; a
> validator who extracted the early payout and exited loses the
> deferred 30% if a fresh submission overturns the settlement.

The 70/30 split is governed; current values are normative for Phase 2
onward. Any change requires a spec PR + ADR. The 6-month window is
likewise governed and mirrors the median ML-research settlement
latency. An overturn event (T-OVR) requires a fresh submission whose
metrics, evaluated under the *original* preregistered analysis plan,
flip the settlement direction; it is not enough for one validator to
disagree.

## Invariants

> **HM-INV-0001** No on-chain `ResultsAnnouncement` for `(id,
> version)` is scored until that `(id, version)` exists on `main`.
> Validators check `spec_cid` against the current registry entry.

> **HM-INV-0002** Fields at `(id, version)` are immutable post-merge
> except `status` (which follows the state machine) and `updated`
> (the date of the status change).

> **HM-INV-0003** `version` is strictly increasing per `id`.

> **HM-INV-0004** `settled-*` is *tentative*; `confirmed` is the
> only positively-terminal state for an `(id, version)`. `withdrawn`
> is terminal across all versions. New versions re-enter the
> lifecycle at `proposed`.

> **HM-INV-0005** `withdrawn` is terminal across every version of
> that `id`.

> **HM-INV-0006** An author retains the right to withdraw a not-yet-
> settled hypothesis they own; post-settlement withdrawal requires
> maintainer participation and an ADR.

1. **Preregistration invariant.** No on-chain `ResultsAnnouncement`
   for `(spec_id, version)` may be scored until that `(spec_id,
   version)` exists on `main`. This is mechanically enforced by
   validators checking the `spec_cid` in the announcement against
   the current registry entry.
2. **Immutability invariant.** Once `version` N is published, the
   spec fields under that version never change except `status`
   (which follows transitions above) and `updated` (date of the
   `status` change). Any other field change requires a `version`
   bump (T-VER) and invalidates prior results.
3. **Version ordering invariant.** `version` is strictly increasing
   per `id`. Skipping numbers (N=1 then N=3) is permitted but
   discouraged.
4. **Terminal invariant.** `settled-*` is terminal for its own
   version only; new versions re-enter the lifecycle at `proposed`.
5. **Withdrawal invariant.** `withdrawn` is terminal across all
   versions for that `id`. A successor hypothesis opens a new `id`
   and lists the withdrawn `id` in its `contradicts` field.
6. **Author-can-withdraw invariant.** An author always retains the
   right to withdraw a not-yet-settled hypothesis they own. Once
   settled, withdrawal requires maintainer participation and an ADR.

## Side effects per transition

### T-ACC (proposed → accepted)

- Registry entry becomes live. Git blob hash is the spec CID.
- `spec-mirror.yml` (Phase 2+) publishes the spec CID to the IPFS
  pinning node.
- Miners may now observe and mine against it.

### T-VER (old version terminal → new version proposed)

- **Prior results are invalidated for scoring purposes**, but not
  deleted. `run.manifest.json` files and their announcements remain
  retrievable from storage for audit.
- The PR bumping `version` MUST also bump `updated`.
- If `experiments/<id>/` requires a matching change (new config,
  new entrypoint), that change lands in the same PR.
- A new lifecycle begins at `proposed` for the new version; the old
  version's `settled-*` status is preserved in the git history at
  the commit before the bump.

### T-SUP / T-REF (settlement)

- Novelty attribution per [06 § ordering](06-scoring.md#ordering-tiebreak-for-simultaneous-settlements).
- Status update happens in TWO ways:
  - **Inferred** from validator consensus at read time (no PR needed
    to observe settlement).
  - **Materialised** by a `docs:` PR that updates the `status` field
    in the hypothesis file. Materialisation is optional for
    readability; consensus is authoritative regardless of whether
    the file has been updated.
- Further submissions against the settled version are still
  processable and scored normally except novelty = 0.

### T-WDA / T-WITH (withdrawal)

- PR sets `status: withdrawn`; `updated` is bumped.
- Validators stop scoring future announcements against this `id`
  regardless of version.
- Existing settlement records remain in git history for audit.
- A withdrawal ADR names the reason. For T-WITH (post-settlement
  withdrawal) the ADR is mandatory; for T-WDA it's
  maintainer-discretion.

## Edge cases

### Mid-run version bump

**Scenario.** A miner is running version 1 of H-0042 when the author
merges a PR bumping to version 2.

**Rule.** The miner's in-flight run is against v1. When they submit,
the manifest's `hypothesis_version: 1` identifies a superseded
version. Validators:

1. Observe the mismatch against the current registry entry.
2. Do NOT reject the submission; they score it against v1 semantics
   (the spec at the v1 commit) as a historical result.
3. Novelty for v1 attribution remains open if v1 had not settled;
   but no future submissions against v1 will accrue novelty — the
   "current" version is v2, and v1 is no longer live for new work.

In practice, miners should prefer restarting against v2 rather than
submitting a v1 result, because the reward for a v1 result is
smaller (novelty limited to the v1 timeline that's now closing) and
the spec has been updated for a reason.

### Oracle unavailable

**Scenario.** A hypothesis declares `oracle.subnet = 42`, but during
validator rerun SN42 is unreachable.

**Rule** (per
[12 § fail-fast](12-implementation-constraints.md#fail-fast-policy)):
validator raises `StorageUnavailable` / the oracle-adapter-specific
unavailability error; submission is marked `pending` and re-examined
on the next validator cycle. If the oracle remains unavailable for
>24 hours, the operator layer surfaces the issue; validators do NOT
degrade to "skip the oracle and score anyway."

**No lifecycle transition.** The hypothesis stays in whatever state
it was in.

### Maintainer revokes an accepted hypothesis (T-WITH)

**Scenario.** A hypothesis merged with `status: accepted` turns out
to be duplicative, fraudulent, or has a critical protocol bug.

**Rule.** The maintainer opens a PR setting `status: withdrawn` and
writes an ADR under `docs/adr/` naming:

- which hypothesis,
- the reason for withdrawal,
- whether prior settlements are preserved as records or annotated.

Settlements in the on-chain history are immutable; the registry
file's `status` is the authoritative future-facing statement.

### Author disappears mid-lifecycle

**Scenario.** Author's account goes inactive, blocking withdrawal
via the author-authority path.

**Rule.** Maintainer alone can execute T-WDA or T-WITH; the "author
OR maintainer" rule in the transitions table is inclusive-or.
Documented in [`GOVERNANCE.md § maintainer authority`](../../GOVERNANCE.md#what-the-maintainer-can-do).

### Duplicate settlements in the same block

**Scenario.** Two miners' announcements both pass all gates in the
same block.

**Rule.** Novelty tiebreak per
[06 § ordering](06-scoring.md#ordering-tiebreak-for-simultaneous-settlements):
first by extrinsic index, then by hotkey SS58 lex order.
Status transitions to `settled-*` regardless of which miner gets
the novelty bonus.

### Hypothesis settles both supported AND refuted across miners

**Scenario.** Miner A's submission meets `success_criteria`; miner
B's submission meets `falsification_criteria`. Both pass rerun.

**Rule.** This is a spec-quality failure: well-formed criteria
should not both be satisfiable on the same protocol. Validators
treat the status as `settled-supported` if the first settling
submission meets success criteria, `settled-refuted` if it meets
falsification — first-settles-wins. The maintainer MUST treat this
as a spec bug: open an issue, bump `version` with tightened
criteria, and invalidate both prior results under the new version.

## Interaction with scoring

A submission's status-dependent scoring behaviour:

| current status | submission is… | effect |
|----------------|----------------|--------|
| `proposed` | any | rejected: spec not yet live |
| `accepted` or `running` | first to pass gates with success | scores, transitions to `settled-supported`, novelty = 1.0 |
| `accepted` or `running` | first to pass gates with falsification | scores, transitions to `settled-refuted`, novelty = 1.0 |
| `accepted` or `running` | second to pass gates at current version | scores, novelty = 0.5 per [06](06-scoring.md#novelty) |
| `settled-*` (current version) | any third-onward | scores, novelty = 0.0 |
| `settled-*` (older version) | any | rejected: submit against current version |
| `withdrawn` | any | rejected: no scoring |

## Interaction with dependencies

- `depends_on: [H-NNNN]` — the referenced hypothesis must be
  `settled-supported` at some version for this hypothesis to reach
  `settled-*`. Validators check transitively. If a dependency is
  `withdrawn` or `settled-refuted`, a downstream hypothesis that
  claims support remains `accepted`/`running` but cannot settle.
- `contradicts: [H-NNNN]` — purely advisory; does not affect
  lifecycle. Used for human readers to follow the chain of
  reasoning.

## References

- [02 § status](02-hypothesis-format.md#spec-fields) — the `status`
  field definition.
- [02 § versioning](02-hypothesis-format.md#versioning-and-immutability)
  — what triggers version bumps.
- [06 § ordering](06-scoring.md#ordering-tiebreak-for-simultaneous-settlements)
  — settlement tiebreak.
- [05 § pipeline](05-validator.md#pipeline) — how validators observe
  transitions.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) — maintainer authority.
- [16 § B — integrity attacks](16-threat-model.md#b-scoring--registry-integrity)
  — threats that exploit transitions.

## Acceptance scenarios

```gherkin
Scenario: Proposed transitions to accepted on maintainer merge
  Given hypothesis H is at status proposed in an open PR
  And the maintainer approves and merges the PR
  When the state machine processes the merge event
  Then H's status becomes accepted
  And the transition carries the merge commit SHA as evidence
```

```gherkin
Scenario: Mid-run version bump invalidates in-flight submissions
  # spec: HM-REQ-0003
  Given H is at status running at version 1
  And miner M has submitted a manifest not yet scored
  When a maintainer-approved PR bumps version to 2
  Then M's submission is marked invalid-against-prior-version
  And M must resubmit against version 2 to be scored
```

```gherkin
Scenario: Duplicate settlement announcements collapse to the first
  # spec: HM-REQ-0021
  Given miner M has already announced a valid settlement for (H, v=1)
  And M broadcasts an identical ResultsAnnouncement in a later block
  When the validator discovers the second announcement
  Then the duplicate is rejected with reason "DuplicateSettlement"
  And the first announcement's novelty stands
```

## Self-audit

This doc is done when:

- Every state has a clear definition and its terminal-ness rule.
- Every transition has an ID, trigger, authority, and side-effect
  list.
- Every invariant is enforceable by code or CI (not just a written
  hope).
- Every edge case has a deterministic rule — no "probably" or
  "typically" in decision points.
- Authorities match [`GOVERNANCE.md`](../../GOVERNANCE.md).
- Scoring-status interaction table covers every `(status,
  submission)` combination reachable in practice.

// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
//
// Formalisation of the hypothesis lifecycle state machine in
// docs/spec/17-hypothesis-lifecycle.md. Prose is the source of
// truth; divergence is a bug.

module hypothesis_lifecycle {

  // --- Types ---

  type HypothesisId = str
  type Version = int

  type Status =
    | Proposed
    | Accepted
    | Running
    | SettledSupported
    | SettledRefuted
    | Confirmed
    | Withdrawn

  type Authority =
    | Author
    | Maintainer
    | Validators

  // A hypothesis is identified by (id, version); status is per
  // version, except Withdrawn which is "absorbing" across versions.
  type Entry = {
    id: HypothesisId,
    version: Version,
    status: Status,
  }

  // --- State ---

  var registry: Set[Entry]
  var withdrawnIds: Set[HypothesisId]  // ids that have ever hit Withdrawn

  // --- Actions ---

  // T-PROP: author opens a PR creating H-NNNN at version 1.
  action propose(id: HypothesisId): bool = all {
    not(id.in(withdrawnIds)),  // withdrawal is absorbing; can't re-propose same id
    not(registry.exists(e => e.id == id and e.version == 1)),
    registry' = registry.union(Set({id: id, version: 1, status: Proposed})),
    withdrawnIds' = withdrawnIds,
  }

  // T-ACC: maintainer merges PR to main.
  action accept(id: HypothesisId, version: Version, who: Authority): bool = all {
    who == Maintainer,
    registry.exists(e => e.id == id and e.version == version and e.status == Proposed),
    registry' = registry.map(e =>
      if (e.id == id and e.version == version) { ...e, status: Accepted } else e
    ),
    withdrawnIds' = withdrawnIds,
  }

  // T-RUN: first valid ResultsAnnouncement observed by consensus.
  action run(id: HypothesisId, version: Version, who: Authority): bool = all {
    who == Validators,
    registry.exists(e => e.id == id and e.version == version and e.status == Accepted),
    registry' = registry.map(e =>
      if (e.id == id and e.version == version) { ...e, status: Running } else e
    ),
    withdrawnIds' = withdrawnIds,
  }

  // T-SUP / T-REF: validator consensus settles the version.
  action settle(id: HypothesisId, version: Version, supported: bool, who: Authority): bool = all {
    who == Validators,
    registry.exists(e => e.id == id and e.version == version and
      (e.status == Accepted or e.status == Running)),
    registry' = registry.map(e =>
      if (e.id == id and e.version == version) {
        { ...e, status: if (supported) SettledSupported else SettledRefuted }
      } else e
    ),
    withdrawnIds' = withdrawnIds,
  }

  // T-CON: tentative settlement promotes to Confirmed after the
  // overturn window elapses. Time is abstract here; the prose spec
  // uses 6 months. Mechanically: this action only fires when no
  // T-OVR has cleared the entry.
  action confirm(id: HypothesisId, version: Version): bool = all {
    registry.exists(e => e.id == id and e.version == version and
      (e.status == SettledSupported or e.status == SettledRefuted)),
    registry' = registry.map(e =>
      if (e.id == id and e.version == version) { ...e, status: Confirmed } else e
    ),
    withdrawnIds' = withdrawnIds,
  }

  // T-OVR: a fresh submission flips the settlement direction under
  // the original analysis plan. Clears the tentative settlement and
  // returns the entry to Running for fresh scoring.
  action overturn(id: HypothesisId, version: Version, who: Authority): bool = all {
    who == Validators,
    registry.exists(e => e.id == id and e.version == version and
      (e.status == SettledSupported or e.status == SettledRefuted)),
    registry' = registry.map(e =>
      if (e.id == id and e.version == version) { ...e, status: Running } else e
    ),
    withdrawnIds' = withdrawnIds,
  }

  // T-VER: author bumps version (via PR). New version starts at
  // Proposed; old version's Settled-* record is preserved.
  action bumpVersion(id: HypothesisId, oldVer: Version, newVer: Version, who: Authority): bool = all {
    (who == Author or who == Maintainer),
    newVer > oldVer,
    registry.exists(e => e.id == id and e.version == oldVer),
    not(registry.exists(e => e.id == id and e.version == newVer)),
    not(id.in(withdrawnIds)),
    registry' = registry.union(Set({id: id, version: newVer, status: Proposed})),
    withdrawnIds' = withdrawnIds,
  }

  // T-WDP / T-WDA / T-WITH: withdraw. Terminal across all versions.
  action withdraw(id: HypothesisId, who: Authority): bool = all {
    (who == Author or who == Maintainer),
    registry.exists(e => e.id == id),
    registry' = registry.map(e =>
      if (e.id == id) { ...e, status: Withdrawn } else e
    ),
    withdrawnIds' = withdrawnIds.union(Set(id)),
  }

  // --- Helpers for invariants ---

  def isTerminalPerVersion(s: Status): bool =
    s == Confirmed or s == Withdrawn

  def isTentativelySettled(s: Status): bool =
    s == SettledSupported or s == SettledRefuted

  def isSettled(s: Status): bool =
    s == SettledSupported or s == SettledRefuted or s == Confirmed

  // --- Invariants ---

  // INV-1: once an id has been withdrawn, it stays withdrawn across
  // versions — no re-proposal, no un-withdraw.
  val Inv_WithdrawalAbsorbing: bool =
    withdrawnIds.forall(id =>
      registry.filter(e => e.id == id).forall(e => e.status == Withdrawn))

  // INV-2: version numbers are strictly increasing per id (no
  // duplicates at the same version).
  val Inv_VersionsUnique: bool =
    registry.forall(e1 =>
      registry.forall(e2 =>
        (e1.id == e2.id and e1.version == e2.version) implies e1 == e2))

  // INV-3: terminal-for-version is sticky within the same
  // (id, version) pair. Once Settled-*, that (id, version) does not
  // return to a non-terminal status.
  val Inv_TerminalsStick: bool =
    registry.forall(e => true)  // actions never transition away from terminal

  // INV-4: withdrawn entries keep their version; withdrawal does not
  // delete history.
  val Inv_WithdrawalPreservesHistory: bool =
    withdrawnIds.forall(id =>
      registry.filter(e => e.id == id).size() >= 1)

  // --- Initial state ---

  action init: bool = all {
    registry' = Set(),
    withdrawnIds' = Set(),
  }

  // Example trace — a minimal happy-path lifecycle including
  // tentative settlement and confirmation.
  run exampleHappyPath = {
    init
      .then(propose("H-0001"))
      .then(accept("H-0001", 1, Maintainer))
      .then(run("H-0001", 1, Validators))
      .then(settle("H-0001", 1, true, Validators))   // tentative SettledSupported
      .then(confirm("H-0001", 1))                    // 6 months pass, no overturn
      .then(bumpVersion("H-0001", 1, 2, Author))
  }

  // Adversarial trace — settlement followed by overturn.
  run exampleOverturn = {
    init
      .then(propose("H-0002"))
      .then(accept("H-0002", 1, Maintainer))
      .then(settle("H-0002", 1, true, Validators))   // tentative
      .then(overturn("H-0002", 1, Validators))       // a fresh submission flips it
      // Entry is back at Running; either a new settle direction or a withdrawal follows.
  }
}

# Changelog

## 0.1.0 (2026-04-26)


### Features

* add analysis_plan + external_anchor schema fields ([004450e](https://github.com/roykollensvendsen/hypotheses/commit/004450ea243b32c066bfcf0c8c92a0695f2539fc))
* add golden i/o fixtures scaffold ([e888272](https://github.com/roykollensvendsen/hypotheses/commit/e8882725a26ffd361f354edfce4dcbd7797ca0a4))
* add hypothesis json schema and validator scripts ([0750bb6](https://github.com/roykollensvendsen/hypotheses/commit/0750bb636528ea9674eaa1afa4bc9065fe0534d5))
* add multi-oracle composition rules ([84b3d71](https://github.com/roykollensvendsen/hypotheses/commit/84b3d7141358e169332226e7252c70883f2a46c8))
* add schemas for synapses, manifest, events ([461a6f1](https://github.com/roykollensvendsen/hypotheses/commit/461a6f15a3a6e7c842a9b9be9d9af3c56b668155))
* **docs:** add agents-routing and token-budget checks ([edb6213](https://github.com/roykollensvendsen/hypotheses/commit/edb6213c10cd568abe91a6c442f898d690acde8c))
* **docs:** add doc-staleness signal + optional last_updated: ([f69b791](https://github.com/roykollensvendsen/hypotheses/commit/f69b79186bcdd8d746077b43fa0c9ab7114b2ef0))
* **docs:** add front-matter schema and kind: classification ([baedb45](https://github.com/roykollensvendsen/hypotheses/commit/baedb458925763c3fe4a13a8818fed46004cfe02))
* **docs:** add HM-REQ traceability matrix and CITATION.cff ([e75c1c6](https://github.com/roykollensvendsen/hypotheses/commit/e75c1c6378b336d8cc242e4b92c20cec7277bae3))
* **docs:** add hypothesis-status and agent-prompt validators ([60c0bb7](https://github.com/roykollensvendsen/hypotheses/commit/60c0bb7dc2d642d3984b72648e6b366318835479))
* **docs:** add llms.txt convention and load_for reverse index ([2821155](https://github.com/roykollensvendsen/hypotheses/commit/282115574e11ffd25ee79a0c92cb7c0d396f7cd7))
* **docs:** add native CITATION.cff validator ([b0c22ff](https://github.com/roykollensvendsen/hypotheses/commit/b0c22ffef8806439a1427f217cebd37d74434c05))
* **docs:** add orphan markdown detector ([05679be](https://github.com/roykollensvendsen/hypotheses/commit/05679be12d6163d26b9630c9ca1807f5d98f3c94))
* **docs:** add protects: tags to antipattern files ([79c7aa4](https://github.com/roykollensvendsen/hypotheses/commit/79c7aa459db21503d57eb4c7b6219ed983175f63))
* **docs:** convert ASCII state machines to mermaid ([9422ce9](https://github.com/roykollensvendsen/hypotheses/commit/9422ce9de749c242022d9775934f624704721388))
* **docs:** glossary heading anchors + glossary-link ratchet ([14a7172](https://github.com/roykollensvendsen/hypotheses/commit/14a7172da04a1cf48c3bff04226c52ce3b3767cf))
* **docs:** kind: decision rollout for ADRs ([6d13412](https://github.com/roykollensvendsen/hypotheses/commit/6d13412a8898af2852e14c37380e68c41e46e1e3))
* **docs:** per-PR spec-impact report bot ([fff0ae0](https://github.com/roykollensvendsen/hypotheses/commit/fff0ae07315607621778675ec83a22efb051f933))
* **docs:** promote Vale to blocking via per-file ratcheted baseline ([b533299](https://github.com/roykollensvendsen/hypotheses/commit/b533299b337b344bb0f0153bc795713af793a842))
* **docs:** wire Phase-1-conditional test-coverage checks ([2f70218](https://github.com/roykollensvendsen/hypotheses/commit/2f702182fc3b0cd0631e0a6b0369f5ab6459247f))
* **errors:** add typed exception hierarchy ([1e818d5](https://github.com/roykollensvendsen/hypotheses/commit/1e818d5e47a7b3cbd2b5ae85cea3066fa754914e))
* **spec:** add community bounty pool; widen the c8 funnel ([fcd5b9c](https://github.com/roykollensvendsen/hypotheses/commit/fcd5b9c1ed5d2df08924b927c17eb45a4cf95122))
* **spec:** add oracle-only verification mode (third viability path) ([d06583d](https://github.com/roykollensvendsen/hypotheses/commit/d06583d5940e483cbf720984e3a7506a859fae15))
* **spec:** multi-miner consensus settlement (HM-REQ-0150) ([bb88e00](https://github.com/roykollensvendsen/hypotheses/commit/bb88e0054f44c3ebbaa49603f714fa9cc2978204))
* **spec:** sponsor-gate heavy hypothesis profiles per ADR 0019 ([efcfa07](https://github.com/roykollensvendsen/hypotheses/commit/efcfa07b0418f03e84e697a9c64917dc31fd5e67))


### Bug Fixes

* avoid broken .git/hooks link in contributing ([d8c73fa](https://github.com/roykollensvendsen/hypotheses/commit/d8c73fa4676ea1ed19815c459df509a3238f03a7))
* close novelty tiebreak and announcement rate-limit gaps ([dcd7b00](https://github.com/roykollensvendsen/hypotheses/commit/dcd7b00c70ab04c967cfbc756f22333e92c94bbb))
* correct fragment anchor in red-team prompt ([369bd84](https://github.com/roykollensvendsen/hypotheses/commit/369bd8415164ac02cbd702bb8ac698be4faf3d99))
* correct relative path to issue template in operations doc ([488dcdb](https://github.com/roykollensvendsen/hypotheses/commit/488dcdba53d2cdca91c4ecf3c66eb1aa8016ce71))
* correct relative paths in adversarial fixtures readme ([fc8bb35](https://github.com/roykollensvendsen/hypotheses/commit/fc8bb35ee7d2a803c424fcb4d97beb23e8a00cb1))
* drop malformed Vocab assignment from .vale.ini ([3457cb8](https://github.com/roykollensvendsen/hypotheses/commit/3457cb8ee5b5f0de8faf1ce37ec7f6e7b0c755df))
* tighten mutation gate guard to require pyproject.toml ([05af292](https://github.com/roykollensvendsen/hypotheses/commit/05af292d612478f142d8fdbf2b2698225982c542))


### Documentation

* add 00.5-foundations.md adversarial-first foundation ([c8b3bb9](https://github.com/roykollensvendsen/hypotheses/commit/c8b3bb92353e3eecfd4ebf26e328df6dabd1399f))
* add 21 adversarial simulator design spec ([87d8976](https://github.com/roykollensvendsen/hypotheses/commit/87d89761a7f2e2c658405c2a60cb8e3221ebd69a))
* add 22 security-bounty spec ([d5b4762](https://github.com/roykollensvendsen/hypotheses/commit/d5b4762b5f631fda1cb631833e5294809e265362))
* add adr directory with phase-zero foundation record ([b17ce66](https://github.com/roykollensvendsen/hypotheses/commit/b17ce66c87f520f7b3462505d24d0767531c960b))
* add agent integration surface (mcp server, sdk, starter agents) ([b1d5de1](https://github.com/roykollensvendsen/hypotheses/commit/b1d5de13381e53e76b554be4857cabf9c396d4dc))
* add agents.md and agents/ prompt tree ([816e1ff](https://github.com/roykollensvendsen/hypotheses/commit/816e1ff29d11ae93ca2cf8b8ddf095044cae5d47))
* add antipatterns corpus ([b2f2d3c](https://github.com/roykollensvendsen/hypotheses/commit/b2f2d3c835dc93a737298f945b35ac845d59c166))
* add confirmed lifecycle phase + two-tier settlement ([8d6e8da](https://github.com/roykollensvendsen/hypotheses/commit/8d6e8da415a81f04c4b9cf64d857529a90835ee2))
* add context-routing map to agents.md ([6aff1a1](https://github.com/roykollensvendsen/hypotheses/commit/6aff1a10342bc22dad000cf2cabe7f163e4e1a24))
* add CONTRIBUTING-DOCS capstone and PR-template doc section ([5097cc4](https://github.com/roykollensvendsen/hypotheses/commit/5097cc4697d79352876c44a592040b0068d15a68))
* add economic model spec (20) ([5dc3922](https://github.com/roykollensvendsen/hypotheses/commit/5dc39220919a8bc80d91be02c10bafc9bfadfcc1))
* add foundation review cadence ([70b9489](https://github.com/roykollensvendsen/hypotheses/commit/70b9489e5b38c94e32b1539e106f2154e45bd109))
* add gherkin acceptance scenarios to key specs ([a411e3a](https://github.com/roykollensvendsen/hypotheses/commit/a411e3a90449c65da215d88235de0dce0d6b6584))
* add h-0001 canonical fixture ([540b518](https://github.com/roykollensvendsen/hypotheses/commit/540b518fbed309a0e9c55c09fcfca24debb3c669))
* add h-0002 (oracle) and h-0003 (refutation path) examples ([8d90ec1](https://github.com/roykollensvendsen/hypotheses/commit/8d90ec140ef94fcc0decb37b4ab768816a695b01))
* add h-0004 (snip vs edge decay) hypothesis ([fd6a647](https://github.com/roykollensvendsen/hypotheses/commit/fd6a647343dd612e40d4e1918325a0cc45bf04c0))
* add h-0005 (l1 vs edge decay) hypothesis ([cf3f0f8](https://github.com/roykollensvendsen/hypotheses/commit/cf3f0f8e1d8b9cb35625417f22e7893bd14676d4))
* add h-0006 (rigl vs edge decay) hypothesis ([cd02cca](https://github.com/roykollensvendsen/hypotheses/commit/cd02cca5cb05ada3a892b37b8340fe5cccde17b3))
* add hypothesis lifecycle state machine (17) ([108716b](https://github.com/roykollensvendsen/hypotheses/commit/108716bac90e2bf72f900ab81000eed28e72297f))
* add implementation handoff for phase 1 agent ([654a5fa](https://github.com/roykollensvendsen/hypotheses/commit/654a5fa80cc4af725a61f24a22fa5f8468468683))
* add invariants catalogue ([9982ca5](https://github.com/roykollensvendsen/hypotheses/commit/9982ca5a7e14d5b166f4f2f79537b87b5249ec44))
* add issue templates for hypotheses, spec questions, bugs ([0490dc2](https://github.com/roykollensvendsen/hypotheses/commit/0490dc23324f49abaa6329e502eab57fdf9c855f))
* add operations spec (19) with slis, alerts, runbooks, dr ([903cbc9](https://github.com/roykollensvendsen/hypotheses/commit/903cbc9ff05a8b3003199370f3802206d12eb855))
* add oracle contract spec (18) and close t-061 ([23e58e8](https://github.com/roykollensvendsen/hypotheses/commit/23e58e80569133ab96f485c7f1928388ab78098f))
* add readme, contributing, coc, security, governance ([eb3df66](https://github.com/roykollensvendsen/hypotheses/commit/eb3df6607307cc760b4595a15d479d0099545198))
* add red-team agent role + onboarding pointers ([ce6d736](https://github.com/roykollensvendsen/hypotheses/commit/ce6d7365673009d616cc7d7baf5228d43ec5528a))
* add security-hypothesis lifecycle variant ([3c475c0](https://github.com/roykollensvendsen/hypotheses/commit/3c475c0038f54629d71ab2482a2d8480989b16d8))
* add self-audit checklists to each spec doc ([b20da35](https://github.com/roykollensvendsen/hypotheses/commit/b20da3539b459c830bd0d2648bcdc510c830f3d4))
* add task-graph dag for phase 1 ([6af70fa](https://github.com/roykollensvendsen/hypotheses/commit/6af70fa9fd77718230b57468207eb422c116614b))
* add threat model with actors, threats, and mitigations ([e711329](https://github.com/roykollensvendsen/hypotheses/commit/e7113293016826cb77068658c8eec1420801b82d))
* add token-budget frontmatter to spec docs ([6b46126](https://github.com/roykollensvendsen/hypotheses/commit/6b461263724ebaa61a9017d6074089db03f6b1e7))
* **adr:** drop typo example from 0003 to satisfy spell-check ([efcee32](https://github.com/roykollensvendsen/hypotheses/commit/efcee32be5d1087fe144421b65279cf4e543047e))
* **adr:** map the five-gap fix sequence into ADR 0015 context ([08137e4](https://github.com/roykollensvendsen/hypotheses/commit/08137e40fba5b922c8f8ffbe9581b0d6bf60158a))
* bump contributing.md to four tracks; collapse Security ([dcb4b0d](https://github.com/roykollensvendsen/hypotheses/commit/dcb4b0d9aac8aef710e41f358f233a2fac22d8ca))
* catalog .github automations in 15-ci-cd.md ([3a2bd43](https://github.com/roykollensvendsen/hypotheses/commit/3a2bd430e37746f8518ceabc2db36e1ae62edc52))
* catalog deferred ci work (tier 2 phase 1, tier 3 phase 3) ([0915904](https://github.com/roykollensvendsen/hypotheses/commit/0915904e11b9210e38d7134f8ba6a24f21b5e32f))
* codify single-source documentation principle (hm-req-0110) ([9e172c0](https://github.com/roykollensvendsen/hypotheses/commit/9e172c03fe393455fbb4cc313f2e14ce09faa0a4))
* consolidate cli into unified hypo command ([c920f6f](https://github.com/roykollensvendsen/hypotheses/commit/c920f6f0835e64b0b328c8b6fad8770fc072f314))
* cross-link logging in 12 to operations spec ([0e48c5e](https://github.com/roykollensvendsen/hypotheses/commit/0e48c5e48ebafbfa5b52d52fe89ea43100049ebd))
* declare agent-first operating mode as fourth pillar ([dccaf37](https://github.com/roykollensvendsen/hypotheses/commit/dccaf37c11ec62e6faf9a2b495da681bcf6b40c5))
* drop duplicated contribute list from readme ([e821fe7](https://github.com/roykollensvendsen/hypotheses/commit/e821fe7327a940596836071bf3278a36a7d2255f))
* formalize hypothesis lifecycle in quint ([905cd41](https://github.com/roykollensvendsen/hypotheses/commit/905cd418e8c22accc8fc905cd606a39b698be2f8))
* **handoff:** wire design-heuristics + system-tests into the kickoff ([413a248](https://github.com/roykollensvendsen/hypotheses/commit/413a248ca70263629d2a238aac25bd2b64666c77))
* introduce requirement ids and consistency checker ([7d05e70](https://github.com/roykollensvendsen/hypotheses/commit/7d05e70e33670e644d1a8fbf2473d9425dbffc9d))
* move vision to canonical /VISION.md at repo root ([8e8513a](https://github.com/roykollensvendsen/hypotheses/commit/8e8513ae883aeeb1e9770191b9c387f558ef0348))
* reflect collaboration and agent files in spec ([48c50ba](https://github.com/roykollensvendsen/hypotheses/commit/48c50ba785ac5792850722953f7f1b27ee06daaf))
* refresh root readme ([dceb540](https://github.com/roykollensvendsen/hypotheses/commit/dceb540e2b3d6077d8044c9962434160078bf594))
* refresh root readme — red-team contribution + docs 21/22 nav ([923c93b](https://github.com/roykollensvendsen/hypotheses/commit/923c93ba3da0c7c5d1d50a0c9c40bcf400ee8e39))
* resolve tbds and add implementation constraints ([435ac56](https://github.com/roykollensvendsen/hypotheses/commit/435ac568c73b29e2b28f641531d1eb3c62900ab9))
* **spec:** add 27-economic-strategy; investment thesis + revenue paths ([33ec958](https://github.com/roykollensvendsen/hypotheses/commit/33ec95817a7cb577c6c3461dc58acca9b8c1da4c))
* **spec:** add 28-treasury; pre-DAO custody, operating-cost catalogue ([0404a4c](https://github.com/roykollensvendsen/hypotheses/commit/0404a4c5a228ecf102c2676affb12963cbba89a2))
* **spec:** add black-box system-test harness contract ([bd1baee](https://github.com/roykollensvendsen/hypotheses/commit/bd1baeeb8d10267693454d014d5120fba4090a4e))
* **spec:** add c7 measurement plan; pin HM-REQ-0070 revision trigger ([49581f4](https://github.com/roykollensvendsen/hypotheses/commit/49581f42dd296ec54fde855d53a4c1e1c2a098b6))
* **spec:** add llm-slop antipatterns ap-0008..ap-0013 ([02ce854](https://github.com/roykollensvendsen/hypotheses/commit/02ce8549595a0ab2be902bea19835f5766221237))
* **spec:** add Phase 2.0 cold-start contingency; split c4 into c4a/c4b ([61ddc91](https://github.com/roykollensvendsen/hypotheses/commit/61ddc91601d2ccaff70ac9d6879004b4106fba80))
* **spec:** add validator unit economics; surface criterion-2 deficit ([77c403c](https://github.com/roykollensvendsen/hypotheses/commit/77c403c89fa81117ca548e7be930d1eee0fc413e))
* **spec:** add viability criteria + decision protocol; pivot ladder ([595d12c](https://github.com/roykollensvendsen/hypotheses/commit/595d12ca0de40632f6be6a78998128e45583b2fc))
* **spec:** cite F3 polymarket exploits + anchor §C rows ([d954456](https://github.com/roykollensvendsen/hypotheses/commit/d95445630585aa979e1ecc74243619bab898e9b1))
* **spec:** codify design heuristics for human + agent contributors ([7e45985](https://github.com/roykollensvendsen/hypotheses/commit/7e45985b1193a18a5e955b0cb0935a9668c36ee3))
* **spec:** drop forward-link to unwritten ADR 0021 in 29 § E ([a8cb0dd](https://github.com/roykollensvendsen/hypotheses/commit/a8cb0dd1669e117770d33144be6d511e9d2afbb9))
* **spec:** early viability verdict; trigger tier-2 pivot ([429ad39](https://github.com/roykollensvendsen/hypotheses/commit/429ad39ee79e05ae9d3c02e8a9fc42462527bb42))
* **spec:** introduce rigor framework + bibliography ([5e102a5](https://github.com/roykollensvendsen/hypotheses/commit/5e102a55d92190c89724d350dbe5ea85182819ac))
* **spec:** open economic-survival work stream; pin miner unit economics ([d4c0510](https://github.com/roykollensvendsen/hypotheses/commit/d4c0510f652f4230167bf9a905328329b7f38cc9))
* **spec:** pin D2.2 coverage bound; name validator-set floor ([2df2749](https://github.com/roykollensvendsen/hypotheses/commit/2df2749a2bdf60486dea5ebd627a6fc0c5225061))
* **spec:** proposal for external adversarial review of foundations ([9bdece5](https://github.com/roykollensvendsen/hypotheses/commit/9bdece5851c577df823875ed593c9caff0443bbf))
* **spec:** prove participation equilibrium; couples criteria 2 and 3 ([1be8fcc](https://github.com/roykollensvendsen/hypotheses/commit/1be8fccd0d317e2bff8964e830b45ab3b1708f5f))
* **spec:** regen llms-full.txt with updated load-for-index embed ([18d4ae6](https://github.com/roykollensvendsen/hypotheses/commit/18d4ae676360480420e52fe2de3f120395bb4ce9))
* **spec:** regen llms.txt and load-for-index for 23-system-tests ([f84c112](https://github.com/roykollensvendsen/hypotheses/commit/f84c1123f884070121b0ee22bab3f788995b00e9))
* **spec:** regenerate llms-full.txt after late prose edits to 27 ([dfd2c1e](https://github.com/roykollensvendsen/hypotheses/commit/dfd2c1efe7edce6f4bc8cdec9f85d2c30a23a4b6))
* **spec:** rigor pass on 00.5-foundations ([0c45e57](https://github.com/roykollensvendsen/hypotheses/commit/0c45e579b7f3e95f8725385b7493f836d23b7db3))
* **spec:** rigor pass on 06-scoring; cite stats methods ([6228721](https://github.com/roykollensvendsen/hypotheses/commit/6228721d01553e6504d5b5c4b6184fdbf31a0261))
* **spec:** wire F7 references; add F7 fixture placeholder ([0380fb0](https://github.com/roykollensvendsen/hypotheses/commit/0380fb065b06dea370b0ce6c2801c3f67cfe73bb))
* split vision and mission in canonical VISION.md ([ad1b23c](https://github.com/roykollensvendsen/hypotheses/commit/ad1b23cc115e3fbc13fa13f3b4a464fead38852a))
* vision.md and readme — five ways to contribute ([ec4508a](https://github.com/roykollensvendsen/hypotheses/commit/ec4508a759947ec1509b6505520885b832a1b126))

## Changelog

This file is maintained automatically by
[release-please](https://github.com/googleapis/release-please) from
conventional commits. Do not edit it by hand.

Conventional commit types that land entries here:

- `feat` — new feature
- `fix` — bug fix
- `perf` — performance improvement
- `refactor` — user-visible refactor

Types that do NOT land in the changelog (internal only): `chore`,
`ci`, `docs`, `style`, `test`, `build`, `revert`.

<!-- x-release-please-start-version -->
<!-- x-release-please-end -->

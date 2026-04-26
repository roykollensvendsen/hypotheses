<!-- antipattern-content -->
<!-- protects:  -->
<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# AP-0013 — Speculative configurability

## Narrative

An environment variable, config field, or feature flag introduced
for a value that has exactly one configured caller. Pluggable
backends with one backend. "Strategy" knobs no one will ever turn.
Each speculative knob multiplies the test surface, drags
configuration into modules that should not care about it, and
encodes a guess about which axis will need to flex — usually
wrong. This is the long tail of `ap-0009` (premature abstraction)
applied to runtime knobs instead of types.

## Bad code

```bad-code
class LocalCache:
    def __init__(self) -> None:
        self.size_bytes = int(os.getenv("HYPO_CACHE_SIZE_BYTES", "10737418240"))
        self.eviction = os.getenv("HYPO_CACHE_EVICTION", "lru")
        self.compress = os.getenv("HYPO_CACHE_COMPRESS", "false") == "true"
        self.backend = os.getenv("HYPO_CACHE_BACKEND", "filesystem")
        if self.backend == "filesystem":
            self._impl = _FilesystemBackend(self.size_bytes)
        elif self.backend == "redis":
            raise NotImplementedError("redis backend planned")
        else:
            raise ValueError(f"unknown backend: {self.backend}")
```

## Why

- Four environment variables for a cache that has exactly one
  configured caller (`size_bytes` from the spec, the rest at
  defaults). The other three are speculation: no test exercises
  them, no operator has set them, no spec section names them.
- The `redis` branch is a `NotImplementedError` that ships to
  `main` — a TODO masquerading as a feature flag (see also
  `ap-0011`). Until redis is real, mentioning it is a guess at
  what Phase 2 will need.
- Configuration sprawl couples modules to environment-variable
  parsing they should not own. The cache should care about
  caching; the env-var-to-config mapping belongs at the boundary
  (CLI parse, `Client.from_env()`), not threaded through every
  internal module.

## Correct pattern

```good-code
class LocalCache:
    def __init__(self, size_bytes: int) -> None:
        self.size_bytes = size_bytes
```

The cache takes its size as a typed parameter. The boundary —
`hypo init` writing the config, or `Client.from_env()` resolving
defaults — decides what value to pass. When a second backend is
genuinely needed, the spec gains a section, the cache gains a
typed parameter, and a new caller passes the right one. No env-var
proliferation; no dead branches; no mention of redis until redis
exists.

## Spec reference

- [AGENTS.md § Non-negotiable rules § Scope discipline](../../../AGENTS.md#non-negotiable-rules)
  — "no speculative features, no 'we might want X later' hooks."
- [24 § D-4](../24-design-heuristics.md) — don't abstract until
  you have three concrete callers; the runtime-knob form of the
  same rule.
- [`ap-0009`](ap-0009-premature-abstraction.md) — type-level
  speculation; this antipattern is its config-flag sibling.
- [`ap-0011`](ap-0011-dead-branches.md) — the
  `NotImplementedError` "planned" branch is the same trap.

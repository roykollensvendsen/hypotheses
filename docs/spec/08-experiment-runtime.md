---
name: experiment runtime
description: sandbox, determinism, resource limits, hardware profiles
---

# 08 — Experiment Runtime

Experiments must be cheap to run, deterministic enough to rerun across
hosts, and safe to run on untrusted code authored by miners.

## Hardware profiles

A fixed set of named profiles. A spec declares exactly one. Validators
maintain a sandbox image per profile and refuse to rerun specs that
declare an unknown profile.

| profile name       | GPU           | host RAM | wallclock cap | disk |
|--------------------|---------------|---------:|--------------:|-----:|
| `cpu-small`        | none          |    8 GiB |           5 m | 2 GiB |
| `cpu-large`        | none          |   32 GiB |          30 m | 8 GiB |
| `single-gpu-24gb`  | 1× 24 GiB     |   32 GiB |          60 m | 16 GiB |
| `single-gpu-80gb`  | 1× 80 GiB     |   64 GiB |         120 m | 32 GiB |
| `multi-gpu-4x80gb` | 4× 80 GiB     |  256 GiB |         240 m | 64 GiB |

Caps are per condition per seed. A spec with `seeds: [0,1,2,3,4]` and two
conditions on `single-gpu-24gb` therefore has a worst-case wallclock of
`5 × 2 × 60 m = 10 h` per submitting node.

## Sandbox

The runtime executes experiment code inside a container with:

- **Network:** egress allow-list only (Hugging Face datasets mirror,
  `pypi.org`, `github.com` raw content, configured artifact store). No
  arbitrary outbound.
- **Filesystem:** read-only code layer, writable `/work` scratch (capped
  per profile), writable `/artifacts` target. Host filesystem not
  mounted.
- **User:** non-root, no sudo.
- **Capabilities:** dropped to the minimum required for GPU passthrough.
- **Timeouts:** `wallclock cap` enforced by runtime, not by the
  experiment.

**Decision:** `podman` 4.x with `nvidia-container-toolkit` for GPU
passthrough. No Docker. Firecracker/gVisor considered and rejected as
too niche for Phase 0–3.

## Determinism

Every experiment runs with:

- `PYTHONHASHSEED` = declared seed
- `CUBLAS_WORKSPACE_CONFIG=:4096:8`
- `CUDA_LAUNCH_BLOCKING=1` (only when explicitly requested; default off
  for performance)
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`
- `torch.use_deterministic_algorithms(True)` (if torch is used)
- RNG state dumped to `rng.state` at the start and end of each run.

Where full bitwise determinism is impossible (e.g. nondeterministic CUDA
kernels), the spec must declare an appropriate `rerun_tolerance` override.

## Environment lock

Experiment code must ship a pinned environment:

- `experiments/<id>/pyproject.toml` or `requirements.txt` with
  **hash-pinned** entries (`package==X.Y.Z --hash=sha256:...`).
- `experiments/<id>/Dockerfile` or a reference to a base image tag
  (digest pinned, not just tag) declared in the profile.

Validators materialise the environment from the pinned spec. A mismatch
between the miner-submitted `env.lock` and the pin in the repo is a
rejection.

## Dataset handling

Datasets are accessed via a thin adapter:

```python
from hypotheses.runtime.data import load("huggingface:uoft-cs/cifar10@<commit>")
```

The adapter:

- verifies the revision hash against the spec's `dataset_revision`,
- caches by hash,
- forbids direct filesystem or network access to datasets outside the
  adapter (enforced by egress allow-list).

Adding a new dataset source requires a PR against
`src/hypotheses/runtime/data/adapters/`.

## Entrypoint contract

```python
# experiments/H-0001/run.py
from hypotheses.runtime import Run, metrics

def main(run: Run) -> None:
    seed = run.seed
    cond = run.condition            # dict from variable name to value
    data = run.load_dataset()

    ...
    metrics.report("flops_to_target_loss", flops)
    metrics.report("final_test_accuracy", acc)

if __name__ == "__main__":
    Run.from_env().execute(main)
```

`Run` takes care of seeding, env pinning, metric buffering, artifact
writing, and timeouts. Miners write the `main` function; everything else
is framework.

## Failure policy

- OOM or wallclock timeout: condition marked `failed`, metrics absent. A
  spec whose declared conditions routinely fail on the declared profile
  is not a miner problem — it's an accepted-hypothesis problem, and the
  spec should not have passed review.
- Network egress violation: hard kill, condition marked `failed`, miner
  receives zero for this submission.
- Dataset hash mismatch: hard kill as above.

## Non-goals

- Running arbitrary user workloads.
- Supporting proprietary model weights that can't be freely downloaded
  inside the sandbox (use `weights` artifact output instead, produced by
  the run).
- Running multi-node distributed training in v1. `multi-gpu-4x80gb` is a
  single-host profile; distributed profiles are a Phase 3+ question.

## Self-audit

This doc is done when:

- Every `hardware_profile` enum value in the JSON Schema has a row
  in the profiles table with concrete caps.
- Every sandbox failure mode maps to a typed exception in
  [12 § fail-fast](12-implementation-constraints.md#fail-fast-policy).
- Determinism rules cover every non-determinism source in the
  declared toolchain (Python, PyTorch, BLAS, CUDA).
- The entrypoint contract matches
  [04 § artifact contract](04-miner.md#submit-artifact-contract).
- Dataset and environment pinning rules are enforceable by
  `runtime/data/` and `runtime/sandbox/` respectively.

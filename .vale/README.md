<!--
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-FileCopyrightText: 2026 The hypotheses subnet contributors
-->

# Vale prose linting

This directory holds the prose-style configuration. Top-level
`.vale.ini` drives where `vale` runs; styles live under
`styles/AgentSpec/`; the per-file per-rule offence count the
project has agreed to live with sits in `baseline.json`.

## Ratchet semantics

`.github/workflows/vale.yml` does not run `vale` directly. It
calls `scripts/check_vale_baseline.py`, which:

1. Runs `vale --output=JSON docs/spec/ VISION.md`.
2. Computes per-file per-rule offence counts.
3. Compares each `(file, rule)` cell to the matching cell in
   `baseline.json`.
4. **Fails** if any cell *increases*. Decreases are surfaced as
   `info:` lines so the baseline can be ratcheted down.

The baseline is **monotonically non-increasing**. New offences
are blocked by CI; the only legitimate way to change a cell is
to fix the offence and lower the count.

## Updating the baseline

After fixing offences in a doc, regenerate the baseline locally:

```bash
python3 -c "
import json, subprocess
out = subprocess.run(
    ['vale', '--output=JSON', 'docs/spec/', 'VISION.md'],
    capture_output=True, text=True,
).stdout
data = json.loads(out)
baseline = {}
for path, alerts in data.items():
    counts = {}
    for a in alerts:
        counts[a['Check']] = counts.get(a['Check'], 0) + 1
    if counts:
        baseline[path] = counts
with open('.vale/baseline.json', 'w') as f:
    json.dump(baseline, f, indent=2, sort_keys=True)
    f.write('\n')
"
```

Commit the new baseline alongside the prose fix.

## Path to deletion

Once every cell reaches zero, the baseline file is no longer
needed: every offence is a regression. At that point delete
`.vale/baseline.json` and update `vale.yml` to call `vale`
directly. The wrapper script will be retired in the same PR.

"""Parse mutmut output and enforce a minimum mutation score.

Runs `mutmut results` and computes `killed / (killed + survived)`.
Fails if the score falls below the provided floor. Used by
`.github/workflows/mutation.yml`.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, default=75.0, dest="minimum")
    args = parser.parse_args()

    try:
        out = subprocess.run(
            ["uv", "run", "mutmut", "results"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        print(f"mutmut invocation failed: {e}", file=sys.stderr)
        return 2

    killed_match = re.search(r"killed[^0-9]*(\d+)", out)
    survived_match = re.search(r"survived[^0-9]*(\d+)", out)
    if not killed_match or not survived_match:
        print("could not parse mutmut output", file=sys.stderr)
        print(out, file=sys.stderr)
        return 2

    killed = int(killed_match.group(1))
    survived = int(survived_match.group(1))
    total = killed + survived
    if total == 0:
        print("no mutants run; skipping score check")
        return 0

    score = 100.0 * killed / total
    print(f"mutation score: {score:.1f}% (killed={killed}, survived={survived})")
    if score < args.minimum:
        print(
            f"::error::mutation score {score:.1f}% below minimum {args.minimum:.1f}%",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

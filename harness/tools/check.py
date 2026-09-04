#!/usr/bin/env python3
"""Run harness checks from the repository root.

    python3 harness/tools/check.py                    # all contracts, all spec pairs, src/   (make check)
    python3 harness/tools/check.py <object>           # one object's contract and spec pair
    python3 harness/tools/check.py --ready <object>   # the readiness checklist               (make ready OBJ=…)
    python3 harness/tools/check.py --owners OWNERS.md # every component has a named owner (central harness, before handover)

Exit 0 only if every check passes. This is what CI and `make check` call.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def run(*args: str) -> int:
    print(f"\n$ {' '.join(args)}", flush=True)
    return subprocess.call([sys.executable, *args])


def owners(path: str) -> int:
    missing = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0] and not set(cells[0]) <= set("-: ") and cells[0] != "Component":
            if not cells[3]:
                missing.append(cells[0])
    for m in missing:
        print(f"  ✗ no named owner: {m}")
    print(f"owners: {len(missing)} component(s) without a named owner" if missing else "owners: every component has a named owner")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--ready"] and len(argv) == 2:
        return subprocess.call([sys.executable, str(TOOLS / "ready.py"), argv[1]])
    if argv[:1] == ["--owners"] and len(argv) == 2:
        return owners(argv[1])
    rc = 0
    if argv:
        obj = argv[0]
        contract = Path(f"docs/10-contract/{obj}.contract.md")
        impl = Path(f"docs/20-impl-spec/{obj}.impl.md")
        if not contract.exists():
            print(f"no contract at {contract}. Start with: python3 harness/tools/scaffold.py {obj} --tier N")
            return 1
        rc |= run(str(TOOLS / "contract_check.py"), str(contract))
        if impl.exists():
            rc |= run(str(TOOLS / "trace_check.py"), str(contract), str(impl))
    else:
        rc |= run(str(TOOLS / "contract_check.py"))
        rc |= run(str(TOOLS / "trace_check.py"))
    if Path("src").is_dir():
        rc |= run(str(TOOLS / "lint_naming.py"), "src")
    print("\nharness checks:", "FAIL" if rc else "PASS")
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

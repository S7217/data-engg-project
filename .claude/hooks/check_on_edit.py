#!/usr/bin/env python3
"""PostToolUse hook: run the matching harness check after an edit and report back to the agent.

  docs/10-contract/X.contract.md  → contract_check (+ trace_check if X.impl.md exists)
  docs/20-impl-spec/X.impl.md     → trace_check against X.contract.md
  src/**.sql|.py                  → lint_naming on that file

Never blocks. When a check fails, the agent gets a count and the first few issues (not the full output).
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_LINES = 6


def run(root: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, *args], cwd=root, capture_output=True, text=True, timeout=60)
    return p.returncode, (p.stdout + p.stderr).strip()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ".").resolve()
    tools = root / "harness" / "tools"
    fp = (payload.get("tool_input") or {}).get("file_path", "")
    if not fp or not tools.is_dir():
        return 0
    try:
        rel = Path(fp).resolve().relative_to(root)
    except ValueError:
        return 0
    r = rel.as_posix()

    outputs = []
    if r.startswith("docs/10-contract/") and r.endswith(".contract.md"):
        obj = rel.name.removesuffix(".contract.md")
        outputs.append(run(root, str(tools / "contract_check.py"), r))
        impl = f"docs/20-impl-spec/{obj}.impl.md"
        if (root / impl).exists():
            outputs.append(run(root, str(tools / "trace_check.py"), r, impl))
    elif r.startswith("docs/20-impl-spec/") and r.endswith(".impl.md"):
        obj = rel.name.removesuffix(".impl.md")
        contract = f"docs/10-contract/{obj}.contract.md"
        if (root / contract).exists():
            outputs.append(run(root, str(tools / "trace_check.py"), contract, r))
    elif r.startswith("src/") and rel.suffix in (".sql", ".py"):
        outputs.append(run(root, str(tools / "lint_naming.py"), r))

    failed = [out for rc, out in outputs if rc != 0]
    if failed:
        # Short on purpose: this fires on every edit while a document is being drafted.
        lines = [ln for out in failed for ln in out.splitlines()
                 if re.search(r"ERROR|UNRECORDED|ABSENT|✗|FAIL|N\d ", ln)]
        shown = "\n".join(lines[:MAX_LINES])
        more = f"\n… {len(lines) - MAX_LINES} more. Run the check to see all" if len(lines) > MAX_LINES else ""
        msg = f"Harness check after this edit: {len(lines)} issue(s).\n{shown}{more}"
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

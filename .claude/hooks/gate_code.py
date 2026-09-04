#!/usr/bin/env python3
"""PreToolUse hook (Write/Edit): no pipeline code before a gated contract.

Applies to model files: src/pipelines/<bronze|silver|gold>/<object>.(py|sql).
Blocks (exit 2) unless harness/tools/ready.py --code passes for <object>:
contract exists and is clean, gate verdict permits implementation, impl spec exists,
pins the current contract version, and its §13 'Ready to generate' is fully ticked.

Helpers outside the layer directories, tests and docs are never gated.
"""

import json
import os
import re
import sys
from pathlib import Path


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ".").resolve()
    fp = (payload.get("tool_input") or {}).get("file_path", "")
    tools = root / "harness" / "tools"
    if not fp or not tools.is_dir():
        return 0
    try:
        rel = Path(fp).resolve().relative_to(root).as_posix()
    except ValueError:
        return 0
    m = re.match(r"^src/pipelines/(bronze|silver|gold)/([a-z0-9_]+)\.(py|sql)$", rel)
    if not m:
        return 0
    obj = m.group(2)
    sys.path.insert(0, str(tools))
    os.chdir(root)
    import ready  # noqa: E402

    items = ready.code_gate(obj, root)
    failed = [(label, detail) for ok, label, detail in items if not ok]
    if not failed:
        return 0
    lines = "\n".join(f"  ✗ {label}" + (f": {detail}" if detail else "") for label, detail in failed)
    print(f"BLOCKED by harness code gate: {rel} implements {obj}, which isn't ready for code.\n{lines}\n"
          f"Finish the spec chain first (/design-spec {obj}, then /gate). Check with: make ready OBJ={obj}",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

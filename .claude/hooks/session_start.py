#!/usr/bin/env python3
"""SessionStart hook: say which permission layer is active, and warn when none is.

harness/tools/claude-layer.sh exports HARNESS_LAYER. A bare `claude` launch runs with
only the stable settings: always-on denies and hooks, but no layer allowlist.
"""

import os

layer = os.environ.get("HARNESS_LAYER")
if layer:
    print(f"Harness: permission layer '{layer}' is active.")
else:
    print("Harness: NO permission layer is active (session not started with harness/tools/claude-layer.sh). "
          "Tell the user once, at the start of your first reply, and suggest restarting with "
          "`harness/tools/claude-layer.sh exploration` or `... delivery`.")

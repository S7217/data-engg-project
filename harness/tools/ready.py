#!/usr/bin/env python3
"""Is <object> ready? One checklist, used by people, by CI and by the code-gate hook.

    python3 harness/tools/ready.py <object>            # full checklist (make ready OBJ=<object>)
    python3 harness/tools/ready.py <object> --code     # only what must hold before code is written

Before code (--code), all of:
  C1 contract exists                          docs/10-contract/<object>.contract.md
  C2 contract passes contract_check
  C3 gate verdict: PASS, or HUMAN_REVIEW with open items accepted by a named person (§15)
  C4 tier 2-3 PASS has a named decider
  C5 implementation spec exists               docs/20-impl-spec/<object>.impl.md
  C6 impl spec pins the current contract version
  C7 impl spec §13 'Ready to generate' fully ticked
Then, for publication:
  P1 trace_check clean (or every failure recorded in §14)
  P2 implementation review (impl §15) recorded: PASS, or HUMAN_REVIEW with steward sign-off
  P3 naming clean for the object's model file
Exit 0 = ready, 1 = not ready.
"""

from __future__ import annotations

import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contract_check  # noqa: E402
import lint_naming  # noqa: E402
import mdspec  # noqa: E402
import trace_check  # noqa: E402
from mdspec import clean  # noqa: E402


def code_gate(obj: str, root: Path = Path(".")) -> list[tuple[bool, str, str]]:
    out: list[tuple[bool, str, str]] = []
    cpath = root / f"docs/10-contract/{obj}.contract.md"
    ipath = root / f"docs/20-impl-spec/{obj}.impl.md"

    if not cpath.exists():
        return [(False, "C1 contract exists", f"{cpath} missing. Run /design-spec {obj}")]
    out.append((True, "C1 contract exists", str(cpath)))

    errors, _, _ = contract_check.check(str(cpath))
    out.append((not errors, "C2 contract_check clean", errors[0] if errors else ""))

    c = mdspec.load(cpath)
    g = contract_check.gate_state(c)
    tier = g["tier"] or 3
    d = g["decision"]
    ok3 = d == "PASS" or (d == "HUMAN_REVIEW" and bool(g["accepted_by"]))
    detail = {None: "not gated. Run /gate on the contract", "FAIL": "gate verdict is FAIL",
              "HUMAN_REVIEW": "HUMAN_REVIEW: open items not yet accepted by a named person (§15)"}.get(d, "") if not ok3 else d
    out.append((ok3, "C3 gate verdict permits implementation", detail))
    if d == "PASS" and tier >= 2:
        out.append((bool(g["decider"]), "C4 named decider", g["decider"] or "§15 Decider blank or pending"))

    if not ipath.exists():
        out.append((False, "C5 implementation spec exists", f"{ipath} missing. /design-spec phase 3"))
        return out
    out.append((True, "C5 implementation spec exists", str(ipath)))

    s = mdspec.load(ipath)
    pin = re.search(r"pinned:?\s*(\d+\.\d+)", clean(s.header_value("Contract")))
    ok6 = bool(pin and g["version"] and pin.group(1) == g["version"])
    out.append((ok6, "C6 impl pins current contract version",
                f"pins {pin.group(1) if pin else 'nothing'}, contract is {g['version']}"))

    boxes = re.findall(r"^\s*-\s*\[( |x|X)\]", s.body(13), re.M)
    unticked = sum(1 for b in boxes if b == " ")
    out.append((bool(boxes) and unticked == 0, "C7 §13 ready to generate",
                f"{unticked} of {len(boxes)} unticked" if boxes else "no §13 checklist found"))
    return out


def publish_gate(obj: str, root: Path = Path(".")) -> list[tuple[bool, str, str]]:
    out: list[tuple[bool, str, str]] = []
    cpath, ipath = root / f"docs/10-contract/{obj}.contract.md", root / f"docs/20-impl-spec/{obj}.impl.md"
    if not (cpath.exists() and ipath.exists()):
        return out
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = trace_check.run(str(cpath), str(ipath), None, str(root / "tests"))
    last = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip()][-1]
    out.append((rc == 0, "P1 trace_check", last))

    s = mdspec.load(ipath)
    kv = {k.lower(): clean(v) for t in s.tables(15) for k, v in t.keyvalue().items()}
    dec = next((v for k, v in kv.items() if k.startswith("decision")), "")
    found = [x for x in ("PASS", "FAIL", "HUMAN_REVIEW") if re.search(rf"\b{x}\b", dec)]
    out.append((len(found) == 1 and found[0] != "FAIL", "P2 implementation review recorded (impl §15)",
                found[0] if len(found) == 1 else "not reviewed. Run /gate on the impl spec"))

    models = [p for p in (root / "src").rglob(f"{obj}.*") if p.suffix in (".py", ".sql")] if (root / "src").is_dir() else []
    v = [x for m in models for x in lint_naming.lint_file(m)]
    out.append((bool(models) and not v, "P3 model exists and naming clean",
                v[0] if v else ("" if models else f"no src/**/{obj}.py|.sql")))
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    obj, code_only = argv[0], "--code" in argv
    items = code_gate(obj) + ([] if code_only else publish_gate(obj))
    print(f"{obj}: {'ready to write code?' if code_only else 'ready?'}")
    for ok, label, detail in items:
        print(f"  {'✓' if ok else '✗'} {label}" + (f"  ({detail})" if detail else ""))
    if not code_only:
        print("  ⚠ manual: if this changes a published object, a lineage-impact-reviewer assessment is linked in the PR")
    ready = all(ok for ok, _, _ in items)
    print("READY" if ready else "NOT READY")
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

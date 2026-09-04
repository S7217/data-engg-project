#!/usr/bin/env python3
"""Create the spec-chain files for one object, scaled to its risk tier.

    python3 harness/tools/scaffold.py <object> --tier 1|2|3 [--catalog-schema prod.sales_gold]

Creates (never overwrites):
  docs/00-brd/<object>.brd.md                  paste the requirement here, verbatim
  docs/10-contract/<object>.contract.md         header filled; at tier 1, §7-§13 pre-marked N/A
  docs/20-impl-spec/<object>.impl.md            header filled, contract path and version pinned
  tests/unit/test_<object>.py                   T- test stub with the traceability comment
  tests/golden/<object>/README.md               tier 2-3: golden record + golden data template

The templates are the v1.1 shapes, unchanged. Scaffolding only removes typing; every
decision in the documents is still made by people and checked by the tools.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
LAYER = re.compile(r"^(stg|int|dim|fct)_[a-z0-9_]+$")
NOT_MANDATORY_T1 = range(7, 14)


def write(path: Path, text: str) -> None:
    if path.exists():
        print(f"  kept     {path} (exists)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  created  {path}")


def contract(obj: str, tier: int, fqn: str) -> str:
    t = (TEMPLATES / "acceptance-contract.md").read_text(encoding="utf-8")
    t = t.replace("| **Artefact** | `catalog.schema.object` |", f"| **Artefact** | `{fqn}` |", 1)
    t = t.replace("| **Requirement source** | BRD reference · Jira key |",
                  f"| **Requirement source** | `docs/00-brd/{obj}.brd.md` |", 1)
    t = t.replace("| **Risk tier** | 1 · 2 · 3 |", f"| **Risk tier** | {tier} |", 1)
    t = t.replace("| **Date** | |", f"| **Date** | {dt.date.today()} |", 1)
    t = t.replace("| **Implementation Spec** | path · written after this passes |",
                  f"| **Implementation Spec** | `docs/20-impl-spec/{obj}.impl.md` · written after this passes |", 1)
    if tier == 1:
        for n in NOT_MANDATORY_T1:
            t = re.sub(rf"(^## {n} · [^\n]*\n)(.*?)(?=^---\s*$)",
                       lambda m: m.group(1) + "\nN/A: not mandatory at Tier 1 (`standards/risk-tiers.md`). "
                       "Write it in if the object needs it.\n\n",
                       t, count=1, flags=re.S | re.M)
    return t


def impl(obj: str, fqn: str) -> str:
    t = (TEMPLATES / "implementation-spec.md").read_text(encoding="utf-8")
    t = t.replace("| **Artefact** | `catalog.schema.object` |", f"| **Artefact** | `{fqn}` |", 1)
    t = t.replace("| **Contract** | path · **version pinned:** `1.0` |",
                  f"| **Contract** | `docs/10-contract/{obj}.contract.md` · **version pinned:** `1.0` |", 1)
    t = t.replace("| **Date** | |", f"| **Date** | {dt.date.today()} |", 1)
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("object")
    ap.add_argument("--tier", type=int, choices=(1, 2, 3), required=True,
                    help="see harness/standards/risk-tiers.md 'Choosing the tier'")
    ap.add_argument("--catalog-schema", default="<catalog>.<schema>", help="e.g. prod.sales_gold")
    a = ap.parse_args()
    obj = a.object
    if not LAYER.match(obj):
        print(f"'{obj}' needs a layer prefix and snake_case: stg_ / int_ / dim_ / fct_ (standards/naming-conventions.md)")
        return 1
    fqn = f"{a.catalog_schema}.{obj}"
    print(f"scaffold {obj} · tier {a.tier}")
    write(Path(f"docs/00-brd/{obj}.brd.md"),
          f"# Requirement: {obj}\n\n<!-- Paste the requirement exactly as it arrived (BRD, ticket, email). "
          "Don't paraphrase it: the contract cites this file. -->\n")
    write(Path(f"docs/10-contract/{obj}.contract.md"), contract(obj, a.tier, fqn))
    write(Path(f"docs/20-impl-spec/{obj}.impl.md"), impl(obj, fqn))
    write(Path(f"tests/unit/test_{obj}.py"),
          f'"""Tests for {obj}. One test per §10 row in docs/20-impl-spec/{obj}.impl.md."""\n\n'
          "from conftest import assert_rows, assert_unique  # noqa: F401\n\n\n"
          "# T-01 · asserts <BR-/DQ-/J-> · traces to <M-, AE->\n"
          f"def test_t01_(spark):\n    ...\n")
    if a.tier >= 2:
        write(Path(f"tests/golden/{obj}/README.md"), (TEMPLATES / "golden-set.md").read_text(encoding="utf-8"))
    print(f"\nnext: fill docs/10-contract/{obj}.contract.md (or /design-spec {obj}) → "
          f"python3 harness/tools/contract_check.py docs/10-contract/{obj}.contract.md → /gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())

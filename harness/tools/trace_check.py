#!/usr/bin/env python3
"""Traceability check: implementation spec §12, both directions.

    python3 harness/tools/trace_check.py <contract.md> <impl.md> [--glossary PATH] [--tests DIR]
    python3 harness/tools/trace_check.py            # every docs/10-contract/X.contract.md
                                                    # paired with docs/20-impl-spec/X.impl.md

Checks (numbered as in the implementation spec §12):
  0  the documents parse: contract §6 and impl §1/§10 have rows (and contract §8/§11 at tier 2-3);
     IDs are well-formed. Nothing parsed is a failure, never a pass
  1  every contract BR- is cited in impl §1/§3/§4/§5/§8           → NOT-IMPLEMENTED
  2  every impl §1 row cites a contract BR-, PASSTHROUGH or SURROGATE → UNREQUESTED
  3  every §2 join states a cardinality and names a §10 test
  4  every contract DQ- appears in impl §9
  5  every contract AE- is traced by a test in impl §10 (a sign-off AE by a named decider in contract §15)
  6  every GL- in the contract resolves in the glossary (and is approved, at tier 2-3)
  7  the contract version pinned in impl §0 matches the contract
  8  every contract §2 input with an upstream contract is pinned in impl §7
  9  every test ID in impl §10 exists somewhere under tests/

A failure is RECORDED only by its own §14 row: a row containing the failing ID, or, for
failures without an ID (checks 0, 7, 8, NOT CHECKED), one row per failure whose
From-check cell names '#<check>'. Exit 0 = every failure recorded, 1 = otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mdspec  # noqa: E402
from contract_check import gate_state, tier_of  # noqa: E402
from mdspec import clean, ids  # noqa: E402

DEFAULT_GLOSSARIES = ["docs/glossary.yml", "glossary.yml"]


def first_col_ids(doc, section: int, prefix: str) -> list[str]:
    out: list[str] = []
    for t in doc.tables(section):
        for row in t.rows:
            c = clean(row[0])
            if re.match(rf"{prefix}-\d{{2,4}}$", c) and c not in out:
                out.append(c)
    return out


def glossary_entries(text: str) -> dict[str, str]:
    """GL-nnnn -> status ('approved' when unstated). Comment lines ignored."""
    entries: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = re.match(r"^(GL-\d{4})\s*:", line)
        if m:
            current = m.group(1)
            entries[current] = "approved"
            continue
        s = re.match(r"^\s+status\s*:\s*['\"]?(\w+)", line)
        if s and current:
            entries[current] = s.group(1).lower()
    return entries


def run(contract_path: str, impl_path: str, glossary: str | None, tests_dir: str) -> int:
    c = mdspec.load(contract_path)
    s = mdspec.load(impl_path)
    tier = tier_of(c) or 3
    R: list[tuple[int, str, list[tuple[str, str]]]] = []  # (check, name, [(key, message)])

    c_br, c_dq, c_ae = first_col_ids(c, 6, "BR"), first_col_ids(c, 8, "DQ"), first_col_ids(c, 11, "AE")
    s_m, s_j, s_t = first_col_ids(s, 1, "M"), first_col_ids(s, 2, "J"), first_col_ids(s, 10, "T")

    # 0 · parse sanity: silence is not success
    f0 = []
    for label, items, needed in (("contract §6 BR-", c_br, True), ("contract §8 DQ-", c_dq, tier >= 2),
                                 ("contract §11 AE-", c_ae, tier >= 2), ("impl §1 M-", s_m, True),
                                 ("impl §10 T-", s_t, True)):
        if needed and not items:
            f0.append(("#0", f"no {label} rows parsed. Missing section, wrong heading, or wrong ID format"))
    for bad in mdspec.malformed_ids(c, (6, 8, 11)) + mdspec.malformed_ids(s, (1, 2, 9, 10)):
        f0.append(("#0", f"malformed ID {bad}: use two to four digits (M-01, BR-0001)"))
    R.append((0, "documents parse", f0))

    # 1 · BR implemented
    impl_text = "".join(s.body(n) for n in (1, 3, 4, 5, 8))
    R.append((1, "contract BR- implemented",
              [(br, f"{br} in contract §6, not cited in impl §1/3/4/5/8 → NOT-IMPLEMENTED")
               for br in c_br if not re.search(rf"\b{br}\b", impl_text)]))

    # 2 · mapping rows trace to a rule
    f2 = []
    for t in s.tables(1):
        idx = t.col("implements")
        if idx is None:
            continue
        for row in t.rows:
            mid = clean(row[0])
            if not re.match(r"M-\d{2,4}$", mid):
                continue
            impl = clean(t.cell(row, idx))
            if re.search(r"\b(PASSTHROUGH|SURROGATE)\b", impl, re.I):
                continue
            cited = ids(impl, "BR")
            if not cited:
                f2.append((mid, f"{mid} cites no BR-, PASSTHROUGH or SURROGATE → UNREQUESTED"))
            f2 += [(mid, f"{mid} cites {br}, which is not in contract §6") for br in cited if br not in c_br]
    R.append((2, "mapping rows trace to a rule", f2))

    # 3 · joins: cardinality + named test
    f3 = []
    for t in s.tables(2):
        card, assertion = t.col("expected cardinality", "cardinality"), t.col("assertion")
        for row in t.rows:
            jid = clean(row[0])
            if jid not in s_j:
                continue
            if not re.search(r"\b[1N]\s*:\s*[1NM]\b", clean(t.cell(row, card))):
                f3.append((jid, f"{jid} states no cardinality (1:1 · 1:N · N:1)"))
            named = ids(t.cell(row, assertion), "T")
            if not named:
                f3.append((jid, f"{jid} names no assertion test"))
            f3 += [(jid, f"{jid} names {tid}, which is not in §10") for tid in named if tid not in s_t]
    R.append((3, "joins state cardinality and a test", f3))

    # 4 · DQ in §9
    R.append((4, "contract DQ- implemented in §9",
              [(dq, f"{dq} in contract §8, missing from impl §9") for dq in c_dq if not re.search(rf"\b{dq}\b", s.body(9))]))

    # 5 · AE traced by a test. A sign-off item is evidenced by the named decider in contract §15 instead
    traced = " ".join(t.cell(r, t.col("traces")) for t in s.tables(10) for r in t.rows)
    signoff = {clean(r[0]) for t in c.tables(11) for r in t.rows if re.search(r"sign-?off", t.cell(r, t.col("evidence")), re.I)}
    decider = gate_state(c)["decider"]
    f5 = []
    for ae in c_ae:
        if ae in signoff:
            if not decider:
                f5.append((ae, f"{ae} is a sign-off; contract §15 has no named decider yet"))
        elif not re.search(rf"\b{ae}\b", traced):
            f5.append((ae, f"{ae} in contract §11, no §10 test traces to it"))
    R.append((5, "contract AE- realised (test, or sign-off by named decider)", f5))

    # 6 · glossary
    gl_cited = ids(c.text, "GL")
    gpath = glossary or next((g for g in DEFAULT_GLOSSARIES if Path(g).exists()), None)
    f6 = []
    if gl_cited and not gpath:
        f6.append(("#6", f"NOT CHECKED: {len(gl_cited)} GL- cited, no glossary found (docs/glossary.yml or --glossary)"))
    elif gl_cited:
        entries = glossary_entries(Path(gpath).read_text(encoding="utf-8"))
        for gl in gl_cited:
            if gl not in entries:
                f6.append((gl, f"{gl} cited in contract, not defined in {gpath}"))
            elif tier >= 2 and entries[gl] != "approved":
                f6.append((gl, f"{gl} is '{entries[gl]}' in {gpath}; tier {tier} needs an approved term"))
    R.append((6, "glossary terms resolve", f6))

    # 7 · contract version pinned
    c_ver = re.search(r"\d+\.\d+", clean(c.header_value("Version")))
    pin = re.search(r"pinned:?\s*(\d+\.\d+)", clean(s.header_value("Contract")))
    f7 = []
    if not c_ver:
        f7.append(("#7", "contract §0 has no version"))
    elif not pin:
        f7.append(("#7", "impl §0 does not pin a contract version ('version pinned: x.y')"))
    elif pin.group(1) != c_ver.group(0):
        f7.append(("#7", f"impl pins contract {pin.group(1)}, contract is {c_ver.group(0)} → stale, re-run §12"))
    R.append((7, "contract version pinned", f7))

    # 8 · upstream contracts pinned in §7
    f8 = []
    for t in c.tables(2):
        idx = t.col("upstream")
        if idx is None:
            continue
        for row in t.rows:
            up = clean(t.cell(row, idx))
            if not up or up.lower() in ("none", "n/a", "-", "—"):
                continue
            ref = re.split(r"\s*·\s*|\s+", up)[0]
            if ref and ref not in s.body(7):
                f8.append(("#8", f"input {clean(row[0])}: upstream contract '{ref}' not pinned in impl §7"))
    R.append((8, "upstream contracts pinned", f8))

    # 9 · tests exist
    tdir = Path(tests_dir)
    f9 = []
    if s_t and tdir.is_dir():
        corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in tdir.rglob("*.py"))
        f9 = [(tid, f"{tid} in §10, not found under {tests_dir}/") for tid in s_t if not re.search(rf"\b{tid}\b", corpus)]
    elif s_t:
        f9 = [("#9", f"NOT CHECKED: {tests_dir}/ does not exist")]
    R.append((9, "§10 tests exist in code", f9))

    # Recorded in §14? One row per failure.
    rows14 = [" | ".join(clean(x) for x in r) for t in s.tables(14) for r in t.rows]
    used: dict[int, int] = {}
    unrecorded = 0
    print(f"{contract_path}  ⇄  {impl_path}")
    print(f"  parsed: tier {tier} · BR {len(c_br)} · DQ {len(c_dq)} · AE {len(c_ae)} · M {len(s_m)} · J {len(s_j)} · T {len(s_t)}")
    for n, name, fails in R:
        if not fails:
            print(f"  ✓ {n} {name}")
            continue
        print(f"  ✗ {n} {name}")
        for key, msg in fails:
            if key.startswith("#"):
                available = sum(1 for r in rows14 if re.search(rf"#\s*{n}\b", r))
                rec = available > used.get(n, 0)
                used[n] = used.get(n, 0) + 1
            else:
                rec = any(re.search(rf"\b{re.escape(key)}\b", r) for r in rows14)
            print(f"      {'recorded  ' if rec else 'UNRECORDED'}  {msg}")
            unrecorded += 0 if rec else 1
    if unrecorded:
        print(f"  FAIL: {unrecorded} unrecorded failure(s). Fix the spec, or add one §14 row per failure")
        return 1
    print("  PASS" if all(not f for _, _, f in R) else "  OK: every failure recorded in §14")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("contract", nargs="?")
    ap.add_argument("impl", nargs="?")
    ap.add_argument("--glossary")
    ap.add_argument("--tests", default="tests")
    a = ap.parse_args()
    if a.contract and a.impl:
        return run(a.contract, a.impl, a.glossary, a.tests)
    rc, pairs = 0, 0
    for cp in sorted(Path("docs/10-contract").glob("*.contract.md")):
        ip = Path("docs/20-impl-spec") / cp.name.replace(".contract.md", ".impl.md")
        if ip.exists():
            pairs += 1
            rc |= run(str(cp), str(ip), a.glossary, a.tests)
        else:
            print(f"{cp}  (no implementation spec yet, skipped)")
    if not pairs:
        print("trace_check: no contract/impl-spec pairs found")
    return rc


if __name__ == "__main__":
    sys.exit(main())

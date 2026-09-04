#!/usr/bin/env python3
"""Acceptance contract check: mechanical pre-gate validation.

    python3 harness/tools/contract_check.py [docs/10-contract/<object>.contract.md ...]

Checks:
  1. Risk tier is chosen (1, 2 or 3)
  2. Every mandatory section for the tier is present (§14 and §15 at every tier)
  3. Every status cell opens with exactly one of PRESENT / INFERRED / ABSENT / N/A
  4. Every PRESENT has a source (Source column, or text after the status in 'Status · Source')
  5. Every section with ABSENT or INFERRED has a row in §14 naming that section
  6. IDs follow the template format (BR-01 / BR-0001, not BR-1)
  7. Tier 2-3: the delivery envelope (§13) has no blank answers
  8. Tier 2-3: a PASS while any ABSENT remains is an error
  9. A PASS needs the verification level the tier requires (risk-tiers.md)
 10. Tier 2-3: a PASS needs a named decider (not blank, not 'pending')

This check doesn't grade content. That's the gate's job. A contract can pass this
check and still FAIL at the gate. Exit 0 = clean, 1 = errors.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mdspec  # noqa: E402
from mdspec import clean, source_after_status, status_of  # noqa: E402

MANDATORY = {1: [1, 2, 3, 4, 5, 6, 14, 15], 2: list(range(1, 16)), 3: list(range(1, 16))}
STATUS_SECTIONS = range(1, 13)  # §13 has answers, not statuses
LEVELS = {"self-review": 1, "context-separated": 2, "independent authority": 3}
PLACEHOLDER = re.compile(r"^(|pending.*|tbd|-|—|\[name\]|name)$", re.I)


def tier_of(doc) -> int | None:
    digits = re.findall(r"\b[123]\b", clean(doc.header_value("Risk tier")))
    return int(digits[0]) if len(digits) == 1 else None


def gate_state(doc) -> dict:
    """What §15 records: decision, decider, verification level, accepted open items."""
    kv: dict[str, str] = {}
    for t in doc.tables(15):
        kv.update({k.lower(): clean(v) for k, v in t.keyvalue().items()})

    def get(prefix: str) -> str:
        return next((v for k, v in kv.items() if k.startswith(prefix)), "")

    found = [d for d in ("PASS", "FAIL", "HUMAN_REVIEW") if re.search(rf"\b{d}\b", get("decision"))]
    lv = [n for name, n in LEVELS.items() if name in get("verification level").lower()]
    accepted = get("open items accepted by")
    return {
        "tier": tier_of(doc),
        "decision": found[0] if len(found) == 1 else None,
        "decider": "" if PLACEHOLDER.match(get("decider")) else get("decider"),
        "level": lv[0] if len(lv) == 1 else None,
        "accepted_by": "" if PLACEHOLDER.match(accepted) or "name · date" in accepted else accepted,
        "version": (re.search(r"\d+\.\d+", clean(doc.header_value("Version"))) or [None])[0],
    }


def check(path: str) -> tuple[list[str], list[str], dict]:
    doc = mdspec.load(path)
    errors: list[str] = []
    found: dict[str, list[str]] = {"ABSENT": [], "INFERRED": [], "PRESENT": [], "N/A": []}
    by_section: dict[int, set[str]] = {}
    g = gate_state(doc)

    tier = g["tier"]
    if tier is None:
        errors.append("§0 Risk tier not chosen: write exactly one of 1, 2, 3")
        tier = 3  # check against the strictest set until it is chosen

    for n in MANDATORY[tier]:
        if n not in doc.sections:
            errors.append(f"§{n} missing: mandatory at tier {tier}. Mark it N/A with a reason rather than omitting it")

    def record(n: int, label: str, s: str | None, source: str, title: str) -> None:
        if s is None:
            errors.append(f"§{n} {title}: '{label}' has no single status (PRESENT / INFERRED / ABSENT / N/A)")
            return
        found[s].append(f"§{n} {label}")
        by_section.setdefault(n, set()).add(s)
        if s == "PRESENT" and source is not None and source.strip() in ("", "-", "—"):
            errors.append(f"§{n} {title}: '{label}' is PRESENT with no source. Cite document + section")

    for n in STATUS_SECTIONS:
        if n not in doc.sections:
            continue
        title, body = doc.sections[n]
        if n not in MANDATORY[tier] and re.search(r"\bN/A\b", body) and not doc.tables(n):
            continue
        for t in doc.tables(n):
            idx = t.col("status")
            if idx is not None:
                src = t.col("source")
                for row in t.rows:
                    label = clean(row[0]) or "(row)"
                    record(n, label, status_of(t.cell(row, idx)), clean(t.cell(row, src)) if src is not None else None, title)
            else:
                for k, v in t.keyvalue().items():
                    if k.lower().startswith("status"):
                        record(n, title, status_of(v), source_after_status(v) if "source" in k.lower() else None, title)

    open_sections: set[int] = set()
    for t in doc.tables(14):
        idx = t.col("section")
        for row in t.rows:
            open_sections.update(int(m) for m in re.findall(r"\d+", clean(t.cell(row, idx))))
    for n, statuses in sorted(by_section.items()):
        gaps = statuses & {"ABSENT", "INFERRED"}
        if gaps and n not in open_sections:
            errors.append(f"§{n} has {'/'.join(sorted(gaps))} but no §14 open-item row naming §{n}")

    for bad in mdspec.malformed_ids(doc, (2, 6, 8, 11, 12)):
        errors.append(f"malformed ID {bad}: use two to four digits (BR-01, DQ-0001)")

    if tier >= 2:
        for t in doc.tables(13):
            idx = t.col("answer")
            for row in t.rows:
                if idx is not None and not clean(t.cell(row, idx)):
                    errors.append(f"§13 delivery envelope: '{clean(row[0])}' unanswered (required at tier {tier})")

    if g["decision"] == "PASS":
        if tier >= 2 and found["ABSENT"]:
            errors.append(f"§15 PASS with {len(found['ABSENT'])} ABSENT item(s). ABSENT blocks the gate at tier {tier}")
        if g["level"] is None:
            errors.append("§15 PASS without a single 'Verification level used'")
        elif g["level"] < tier:
            need = [k for k, v in LEVELS.items() if v == tier][0]
            errors.append(f"§15 PASS at tier {tier} needs verification level '{need}'")
        if tier >= 2 and not g["decider"]:
            errors.append(f"§15 PASS at tier {tier} without a named decider. A verdict without a named decider is an opinion")

    notes = [f"tier {tier} · gate: {g['decision'] or 'not yet gated'}"]
    stats = {k: len(v) for k, v in found.items()}
    stats["absent_items"] = found["ABSENT"]
    return errors, notes, stats


def main(argv: list[str]) -> int:
    paths = argv or sorted(str(p) for p in Path("docs/10-contract").glob("*.contract.md"))
    if not paths:
        print("contract_check: no contracts found (docs/10-contract/*.contract.md)")
        return 0
    rc = 0
    for p in paths:
        errors, notes, s = check(p)
        print(f"{'✗' if errors else '✓'} {p}  [{'; '.join(notes)}]  "
              f"PRESENT {s['PRESENT']} · INFERRED {s['INFERRED']} · ABSENT {s['ABSENT']} · N/A {s['N/A']}")
        for e in errors:
            print(f"    ERROR  {e}")
        for a in s["absent_items"]:
            print(f"    ABSENT {a}: goes back to the business")
        rc |= 1 if errors else 0
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

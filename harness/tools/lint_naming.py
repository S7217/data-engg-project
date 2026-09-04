#!/usr/bin/env python3
"""Naming check against harness/standards/naming-conventions.md.

    python3 harness/tools/lint_naming.py [PATH ...]     # default: src/

Model files are .sql/.py files under a bronze/, silver/ or gold/ directory.
  N1  model file name starts with a layer prefix (stg_, int_, dim_, fct_)
  N2  dim_/fct_ models state their grain on line 1:  -- grain: ...  or  # grain: ...
  N3  column names are snake_case
  N4  TIMESTAMP columns end _at; DATE columns end _date
  N5  BOOLEAN columns start is_ or has_
  N6  money columns (amount/revenue/price/cost/fee/…) end _cents and are integer types
Columns are read from CREATE TABLE definitions, `AS alias` in SQL, and
withColumn/alias/withColumnRenamed in PySpark. Exit 0 = clean, 1 = violations.

Change the constants below when the standard changes, in the same commit.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LAYER_DIRS = {"bronze", "silver", "gold"}
LAYER_PREFIXES = ("stg_", "int_", "dim_", "fct_")
GRAIN_REQUIRED = ("dim_", "fct_")
MONEY_WORDS = re.compile(r"(^|_)(amount|amt|revenue|price|cost|fee|mrr|arr|balance|total_value)(_|$)")
SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
SQL_KEYWORDS = {"constraint", "primary", "foreign", "unique", "check", "partitioned", "cluster", "using", "comment", "tblproperties", "location"}

COLDEF = re.compile(r"^\s*`?([A-Za-z_][A-Za-z0-9_]*)`?\s+(BIGINT|INT|INTEGER|SMALLINT|TINYINT|DECIMAL|NUMERIC|DOUBLE|FLOAT|REAL|STRING|VARCHAR|CHAR|BOOLEAN|BOOL|DATE|TIMESTAMP_NTZ|TIMESTAMP|BINARY|ARRAY|MAP|STRUCT|VARIANT)\b", re.I)
SQL_ALIAS = re.compile(r"\bAS\s+`?([A-Za-z_][A-Za-z0-9_]*)`?\s*(?:,|$|\n|FROM\b)", re.I)
SQL_CAST_ALIAS = re.compile(r"CAST\s*\(.+?\bAS\s+(\w+)(?:\([^)]*\))?\s*\)\s+AS\s+`?([A-Za-z_]\w*)`?", re.I)
PY_COL = re.compile(r"""\.(?:withColumn|alias)\(\s*["']([^"']+)["']""")
PY_RENAME = re.compile(r"""\.withColumnRenamed\(\s*["'][^"']+["']\s*,\s*["']([^"']+)["']""")


def check_column(name: str, typ: str | None, where: str) -> list[str]:
    v = []
    if not SNAKE.match(name):
        v.append(f"N3 {where}: '{name}' is not snake_case")
        return v
    t = (typ or "").upper()
    if t.startswith("TIMESTAMP") and not name.endswith("_at"):
        v.append(f"N4 {where}: TIMESTAMP '{name}' should end _at (UTC)")
    if t == "DATE" and not name.endswith("_date"):
        v.append(f"N4 {where}: DATE '{name}' should end _date")
    if t in ("BOOLEAN", "BOOL") and not name.startswith(("is_", "has_")):
        v.append(f"N5 {where}: BOOLEAN '{name}' should start is_ / has_")
    if MONEY_WORDS.search(name) and not name.endswith("_cents") and not name.endswith(("_count", "_pct", "_rate")):
        v.append(f"N6 {where}: money column '{name}' should end _cents (integer)")
    if name.endswith("_cents") and t and t not in ("BIGINT", "INT", "INTEGER", "LONG"):
        v.append(f"N6 {where}: '{name}' is {t}; _cents columns are integer")
    return v


def lint_file(p: Path) -> list[str]:
    v: list[str] = []
    text = p.read_text(encoding="utf-8", errors="ignore")
    is_model = bool(LAYER_DIRS & set(p.parts)) and p.suffix in (".sql", ".py") and p.name != "__init__.py"
    if is_model:
        if not p.stem.startswith(LAYER_PREFIXES):
            v.append(f"N1 {p}: model name should start with one of {', '.join(LAYER_PREFIXES)}")
        if p.stem.startswith(GRAIN_REQUIRED):
            first = text.lstrip("﻿").splitlines()[0] if text.strip() else ""
            if not re.match(r"^\s*(--|#)\s*grain\s*:", first, re.I):
                v.append(f"N2 {p}:1: {p.stem} must state its grain on line 1  (-- grain: ...)")
    if not SNAKE.match(p.stem) and p.stem != "__init__":
        v.append(f"N3 {p}: file name is not snake_case")

    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        where = f"{p}:{i}"
        if p.suffix == ".sql":
            m = COLDEF.match(line)
            if m and m.group(1).lower() not in SQL_KEYWORDS:
                v += check_column(m.group(1), m.group(2), where)
                continue
            for cm in SQL_CAST_ALIAS.finditer(line):
                v += check_column(cm.group(2), cm.group(1), where)
            casted = {cm.group(2) for cm in SQL_CAST_ALIAS.finditer(line)}
            for am in SQL_ALIAS.finditer(line):
                if am.group(1) not in casted and am.group(1).upper() not in ("SELECT",):
                    v += check_column(am.group(1), None, where)
        elif p.suffix == ".py":
            for m in PY_COL.finditer(line):
                v += check_column(m.group(1), None, where)
            for m in PY_RENAME.finditer(line):
                v += check_column(m.group(1), None, where)
    return v


def main(argv: list[str]) -> int:
    roots = [Path(a) for a in argv] or [Path("src")]
    files: list[Path] = []
    for r in roots:
        if r.is_file():
            files.append(r)
        elif r.is_dir():
            files += [f for f in sorted(r.rglob("*")) if f.suffix in (".sql", ".py") and f.is_file()]
    violations = [x for f in files for x in lint_file(f)]
    if violations:
        print(f"✗ naming: {len(violations)} violation(s) in {len(files)} file(s)")
        for x in violations:
            print(f"    {x}")
        return 1
    print(f"✓ naming: {len(files)} file(s) clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

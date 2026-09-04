"""Minimal parser for harness documents: numbered sections and markdown tables.

Harness documents use headings of the form `## 6 · Business rules`. Tables are
GitHub-flavoured pipe tables. Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# "## 6 · Business rules" (harness v1.1) and "## Section 6: Business rules" (older filled examples)
SECTION_RE = re.compile(r"^##\s+(?:Section\s+)?(\d+)\s*[·:\-–—.]\s*(.+?)\s*$", re.MULTILINE)
SEPARATOR_RE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
ID_RE = r"(?:BR|DQ|AE|M|J|T|GL|I)-\d{2,4}"
STATUSES = ("PRESENT", "INFERRED", "ABSENT", "N/A")


def clean(cell: str) -> str:
    """Strip markdown emphasis and code ticks from a cell."""
    return re.sub(r"[*`]", "", cell).strip()


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


@dataclass
class Table:
    header: list[str]
    rows: list[list[str]] = field(default_factory=list)

    def col(self, *names: str) -> int | None:
        """Index of the first header cell starting with any of the names (case-insensitive)."""
        for i, h in enumerate(self.header):
            h = clean(h).lower()
            if any(h.startswith(n.lower()) for n in names):
                return i
        return None

    def cell(self, row: list[str], idx: int | None) -> str:
        if idx is None or idx >= len(row):
            return ""
        return row[idx]

    def keyvalue(self) -> dict[str, str]:
        """For two-column `| key | value |` tables. The header row counts as a pair too."""
        pairs = {}
        for r in [self.header, *self.rows]:
            if len(r) >= 2 and clean(r[0]):
                pairs[clean(r[0])] = r[1]
        return pairs


def tables(text: str) -> list[Table]:
    out: list[Table] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and SEPARATOR_RE.match(lines[i + 1].strip()):
            t = Table(header=split_row(lines[i]))
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                t.rows.append(split_row(lines[i]))
                i += 1
            out.append(t)
        else:
            i += 1
    return out


@dataclass
class Doc:
    path: Path
    text: str
    sections: dict[int, tuple[str, str]]  # number -> (title, body)

    def body(self, n: int) -> str:
        return self.sections.get(n, ("", ""))[1]

    def tables(self, n: int) -> list[Table]:
        return tables(self.body(n))

    def header_value(self, *keys: str) -> str:
        """Value from the §0 key/value header table."""
        for t in self.tables(0):
            kv = t.keyvalue()
            for k, v in kv.items():
                if any(k.lower().startswith(key.lower()) for key in keys):
                    return v
        return ""


def load(path: str | Path) -> Doc:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    matches = list(SECTION_RE.finditer(text))
    sections: dict[int, tuple[str, str]] = {}
    for m, nxt in zip(matches, [*matches[1:], None]):
        end = nxt.start() if nxt else len(text)
        sections[int(m.group(1))] = (m.group(2), text[m.end():end])
    return Doc(path=path, text=text, sections=sections)


def ids(text: str, prefix: str) -> list[str]:
    """IDs with the given prefix, in order of first appearance."""
    seen: dict[str, None] = {}
    for m in re.finditer(rf"\b{prefix}-\d{{2,4}}\b", text):
        seen.setdefault(m.group(0), None)
    return list(seen)


def status_of(cell: str) -> str | None:
    """The status a cell opens with: 'PRESENT · BRD §2 (absent from Jira)' -> PRESENT.

    Only the leading token counts, case-sensitive, so prose later in the cell can't
    create a second match. A cell offering several ('PRESENT / INFERRED') has none.
    """
    c = clean(cell)
    m = re.match(r"(PRESENT|INFERRED|ABSENT|N/A)\b(?!\s*/\s*(PRESENT|INFERRED|ABSENT|N/A))", c)
    return m.group(1) if m else None


def source_after_status(cell: str) -> str:
    """Text after the leading status, e.g. 'PRESENT · BRD §2' -> 'BRD §2'."""
    return re.sub(r"^(PRESENT|INFERRED|ABSENT|N/A)\s*[·:\-–—,]?\s*", "", clean(cell)).strip()


MALFORMED_ID = re.compile(r"^(BR|DQ|AE|M|J|T|GL)-\d+$")
WELLFORMED_ID = re.compile(r"^(BR|DQ|AE|M|J|T)-\d{2,4}$|^GL-\d{4}$")


def malformed_ids(doc, sections) -> list[str]:
    """First-column cells that look like IDs but don't match the template format (M-1, BR-00001)."""
    bad = []
    for n in sections:
        for t in doc.tables(n):
            for row in t.rows:
                c = clean(row[0]) if row else ""
                if MALFORMED_ID.match(c) and not WELLFORMED_ID.match(c):
                    bad.append(f"§{n} '{c}'")
    return bad

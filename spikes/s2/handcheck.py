"""Spike S2: lay out one day for the hand check. Throwaway code.

Usage: python3.14 handcheck.py YYYYMMDD

Writes two plain-text listings to out/ in the same layout, one item per block:

- out/<date>-reader.txt: the visible text of the bulletin's HTML summary page, as a person
  reads it on bocm.es, with the download-link labels removed. It does not reuse the
  retrieval program's parser.
- out/<date>-program.txt: what retrieve.py extracted from the items' XML, with the section,
  department and number written as the summary page shows them.

The two are then read side by side (`diff -u`) and every difference is looked at by hand.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from fetch import fetch_raw

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LINK_LABELS = {"Descargar", "pdf", "HTML", "epub", "XML", "Json"}
BLOCK_TAGS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "article"}


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def clean(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip()
    return re.sub(r"^[–•-]\s*", "", line)


def reader_view(url: str) -> list[str]:
    parser = VisibleText()
    parser.feed(fetch_raw(url)[2].decode("utf-8"))
    lines = [clean(line) for line in "".join(parser.parts).split("\n")]
    lines = [line for line in lines if line and line not in LINK_LABELS]
    start = next(i for i, line in enumerate(lines) if line.startswith("Sección:"))
    end = next(i for i, line in enumerate(lines) if line == "Comunidad de Madrid" and i > start)
    return lines[start:end]


def program_view(items: list[dict]) -> list[str]:
    sys.path.insert(0, str(HERE))
    from retrieve import summary_heading

    lines: list[str] = []
    last_section = last_department = None
    for item in items:
        section, department = summary_heading(item)
        if section != last_section:
            lines.append(f"Sección: {section}")
            last_section, last_department = section, None
        if department and department != last_department:
            lines.append(department)
            last_department = department
        if item["sub_body"]:
            lines.append(item["sub_body"])
        lines.append(item["identifier"].rsplit("-", 1)[1])
        lines.extend(clean(part) for part in item["title"].split("\n") if clean(part))
    return lines


def main(date: str) -> None:
    data = json.loads((OUT / f"{date}.json").read_text())
    reader = reader_view(data["bulletin"]["summary_url"])
    program = program_view(data["items"])
    (OUT / f"{date}-reader.txt").write_text("\n".join(reader) + "\n")
    (OUT / f"{date}-program.txt").write_text("\n".join(program) + "\n")
    print(f"reader: {len(reader)} lines, program: {len(program)} lines")


if __name__ == "__main__":
    main(sys.argv[1])

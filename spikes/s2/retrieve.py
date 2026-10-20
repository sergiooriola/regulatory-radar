"""Spike S2: retrieve the 20 most recent BOCM publication days. Throwaway code.

Usage: python3.14 -I retrieve.py

Sources, all official and all allowed by https://www.bocm.es/robots.txt:

1. https://www.bocm.es/sumarios.rss lists the last 20 bulletins and every item's CVE
   (the bulletin's identifier for an item).
2. For each bulletin, the HTML summary https://www.bocm.es/boletin-completo/BOCM-<date>/<no>
   gives each item's number, section, department and title as a reader sees them.
3. For each item, https://www.bocm.es/boletin/CM_Orden_BOCM/<y>/<m>/<d>/<CVE>.xml gives its
   metadata in XML. This is what the program extracts; 1 and 2 are cross-checks.

The bulletin-level XML (/boletin/CM_Boletin_BOCM/...xml) would give the whole summary in one
request, but robots.txt disallows /boletin/CM_Boletin_BOCM/, so it is not used.

Writes out/<date>.json (git-ignored: titles can name people) and results.csv (counts and
check results only).
"""

import csv
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from fetch import fetch_raw

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FEED = "https://www.bocm.es/sumarios.rss"
REQUIRED = ("identifier", "title", "section", "department", "pdf", "published")


def norm(text: str | None) -> str:
    """Collapse whitespace and normalise Unicode, for comparisons only."""
    text = unicodedata.normalize("NFC", text or "")
    return re.sub(r"\s+", " ", text).strip()


def norm_title(text: str | None) -> str:
    """Titles start with "–" in some places and "•" in others; ignore both."""
    return norm(re.sub(r"^[\s–•-]+", "", text or ""))


def issuer(xml_department: str | None, section: str | None, title: str | None) -> str:
    """The body that issues an item.

    Section I gives it in <departamento>. Section IV gives the court there as "– Tribunal
    Superior de Justicia:". Section III (town councils) leaves it empty: the council is the
    title's first sentence ("– Madrid. Organización y funcionamiento. ..."), as in the summary.
    """
    department = norm(re.sub(r"^[\s–•-]+|:\s*$", "", xml_department or ""))
    if not department and norm(section).startswith("III."):
        department = norm_title(title).split(".", 1)[0]
    return department


def get(url: str) -> bytes:
    status, _, body = fetch_raw(url)
    if status != 200:
        raise RuntimeError(f"{url}: HTTP {status}")
    return body


def bulletins_from_feed() -> list[dict]:
    root = ET.fromstring(get(FEED))
    bulletins = []
    for item in root.iter("item"):
        link = item.findtext("link")
        match = re.search(r"/BOCM-(\d{8})/(\d+)$", link)
        cves = re.findall(r'href="/bocm-(\d{8}-\d+)"', item.findtext("description"))
        bulletins.append(
            {
                "date": match.group(1),
                "number": int(match.group(2)),
                "summary_url": link,
                "feed_cves": ["BOCM-" + cve for cve in cves],
            }
        )
    return bulletins


class SummaryParser(HTMLParser):
    """Items of an HTML summary page, with the headings they sit under."""

    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict] = []
        self.section = ""
        self.department = ""
        self.sub_body = ""
        self._capture: str | None = None
        self._buffer: list[str] = []
        self._item: dict | None = None
        self._div_depth = 0

    def _start(self, what: str) -> None:
        self._capture, self._buffer = what, []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        cls = a.get("class") or ""
        if tag == "h3" and self._item is None:
            self._start("section")
        elif tag == "h4":
            self._start("department")
        elif tag == "div" and "sub-organismo" in cls:
            self._start("sub_body")
        elif tag == "article" and (a.get("about") or "").startswith("/bocm-"):
            self._item = {
                "identifier": a["about"][1:].upper(),
                "section": self.section,
                "department": self.department,
                "sub_body": self.sub_body,
            }
        elif self._item is not None and tag == "div" and "field-name-field-order-number" in cls:
            self._start("number")
            self._div_depth = 0
        elif self._item is not None and tag == "div" and "field-name-field-short-description" in cls:
            self._start("title")
            self._div_depth = 0
        elif self._item is not None and tag == "a" and (a.get("href") or "").endswith(".PDF"):
            self._item.setdefault("pdf", a["href"])
        elif tag == "br" and self._capture == "title":
            self._buffer.append("\n")
        if tag == "div" and self._capture in ("number", "title"):
            self._div_depth += 1

    def handle_endtag(self, tag: str) -> None:
        text = "".join(self._buffer)
        if self._capture == "section" and tag == "h3":
            # "Sección: I. COMUNIDAD DE MADRID | B) Autoridades y Personal"
            self.section = norm(text.replace("Sección:", ""))
            self.department = self.sub_body = ""
            self._capture = None
        elif self._capture == "department" and tag == "h4":
            self.department = norm(text)
            self.sub_body = ""
            self._capture = None
        elif self._capture == "sub_body" and tag == "div":
            self.sub_body = norm(text)
            self._capture = None
        elif self._capture in ("number", "title") and tag == "div":
            self._div_depth -= 1
            if self._div_depth == 0:
                self._item[self._capture] = text.strip()
                self._capture = None
        elif tag == "article" and self._item is not None:
            self.items.append(self._item)
            self._item = None

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)


def summary_items(url: str) -> list[dict]:
    parser = SummaryParser()
    parser.feed(get(url).decode("utf-8"))
    return parser.items


def xml_url(identifier: str) -> str:
    date = identifier.split("-")[1]
    return (
        f"https://www.bocm.es/boletin/CM_Orden_BOCM/{date[:4]}/{date[4:6]}/{date[6:]}/"
        f"{identifier}.xml"
    )


def item_from_xml(identifier: str) -> dict:
    root = ET.fromstring(get(xml_url(identifier)))
    meta, analysis = root.find("metadatos"), root.find("analisis")
    return {
        "identifier": meta.findtext("identificador"),
        "number": None,  # the XML has no item number; it is the CVE's last part
        "title": meta.findtext("titulo"),
        "section": analysis.findtext("seccion"),
        "subsection": analysis.findtext("apartado"),
        "department": issuer(
            meta.findtext("departamento") or analysis.findtext("organismo"),
            analysis.findtext("seccion"),
            meta.findtext("titulo"),
        ),
        "rank": meta.findtext("rango"),
        "disposition_date": meta.findtext("fecha_disposicion"),
        "published": meta.findtext("fecha_publicacion"),
        "bulletin_number": meta.findtext("diario_numero"),
        "pages": [meta.findtext("pagina_inicial"), meta.findtext("pagina_final")],
        "html": meta.findtext("url_html"),
        "pdf": meta.findtext("url_pdf"),
        "text_chars": len(root.findtext("texto") or ""),
    }


def summary_heading(item: dict) -> tuple[str, str]:
    """What the HTML summary should show above the item: its section line and <h4>.

    Section I: "I. COMUNIDAD DE MADRID | B) Autoridades y Personal" and the department.
    Section IV: "IV. ADMINISTRACIÓN DE JUSTICIA | Tribunal Superior de Justicia:" and nothing.
    Section III: "III. ADMINISTRACIÓN LOCAL AYUNTAMIENTOS" and nothing.
    """
    section = norm(item["section"])
    if item["subsection"]:
        return f"{section} | {norm(item['subsection'])}", item["department"]
    if section.startswith("III."):
        return section, ""
    return f"{section} | {item['department']}:", ""


def check_day(bulletin: dict) -> dict:
    date = bulletin["date"]
    summary = summary_items(bulletin["summary_url"])
    by_summary = {item["identifier"]: item for item in summary}
    extracted = []
    for cve in bulletin["feed_cves"]:
        print(f"{date} {cve}", file=sys.stderr)
        extracted.append(item_from_xml(cve))
    OUT.mkdir(exist_ok=True)
    (OUT / f"{date}.json").write_text(
        json.dumps({"bulletin": bulletin, "items": extracted, "summary": summary},
                   ensure_ascii=False, indent=1)
    )

    feed_ids = bulletin["feed_cves"]
    numbers = [int(cve.rsplit("-", 1)[1]) for cve in feed_ids]
    missing_fields = [
        (item["identifier"], field)
        for item in extracted
        for field in REQUIRED
        if not norm(item.get(field))
    ]
    mismatches = []
    for item in extracted:
        seen = by_summary.get(item["identifier"])
        if seen is None:
            mismatches.append((item["identifier"], "not in summary"))
            continue
        if norm_title(item["title"]) != norm_title(seen.get("title")):
            mismatches.append((item["identifier"], "title"))
        section, department = summary_heading(item)
        if section != norm(seen["section"]):
            mismatches.append((item["identifier"], "section"))
        if department != seen["department"]:
            mismatches.append((item["identifier"], "department"))
        if item["pdf"] != seen.get("pdf"):
            mismatches.append((item["identifier"], "pdf"))
        if item["published"].replace("/", "") != date:
            mismatches.append((item["identifier"], "published"))
        if int(item["bulletin_number"]) != bulletin["number"]:
            mismatches.append((item["identifier"], "bulletin number"))
    return {
        "date": date,
        "bulletin": bulletin["number"],
        "items_feed": len(feed_ids),
        "items_summary": len(summary),
        "items_xml": len(extracted),
        "numbering_contiguous": sorted(numbers) == list(range(1, len(numbers) + 1)),
        "same_items": set(feed_ids) == set(by_summary),
        "missing_fields": len(missing_fields),
        "mismatches": len(mismatches),
        "details": "; ".join(f"{cve} {what}" for cve, what in missing_fields + mismatches),
    }


def main() -> None:
    bulletins = bulletins_from_feed()
    rows = [check_day(bulletin) for bulletin in bulletins]
    with open(HERE / "results.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()

"""Spike S1: BOE open data. Throwaway code, never imported by anything else.

Standard library only. Every response is cached under cache/ (git-ignored), so a
re-run never fetches the same URL twice; requests are at least 1.1 s apart, carry
a User-Agent naming the project, and are checked against www.boe.es/robots.txt.

    python3.14 -I s1.py sumarios --until 2026-10-20 --days 60
    python3.14 -I s1.py links
    python3.14 -I s1.py relations
    python3.14 -I s1.py probes
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
RESULTS = HERE / "results"
BASE = "https://www.boe.es"
UA = "regulatory-radar-spike-s1/0.1 (+https://github.com/sergiooriola/regulatory-radar)"
MIN_INTERVAL = 1.1  # seconds between any two requests
MAX_ATTEMPTS = 5
RETRYABLE = {None, 429, 500, 502, 503, 504}

_last_request = 0.0
_robots = None


# --- polite HTTP -------------------------------------------------------------


def _robots_rules():
    """Rules of the only group in BOE's robots.txt (User-agent: *)."""
    global _robots
    if _robots is None:
        path = CACHE / "robots.txt"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            status, _, body, _ = _request(f"{BASE}/robots.txt", None, "GET")
            if status != 200:
                sys.exit(f"robots.txt returned {status}")
            path.write_bytes(body)
        rules, applies = [], False
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            key, value = (s.strip() for s in line.split(":", 1))
            key = key.lower()
            if key == "user-agent":
                applies = value == "*"
            elif applies and key in ("allow", "disallow") and value:
                pattern = "^" + re.escape(value).replace(r"\*", ".*")
                if pattern.endswith(r"\$"):
                    pattern = pattern[:-2] + "$"
                rules.append((key == "allow", len(value), re.compile(pattern)))
        _robots = rules
    return _robots


def robots_allowed(url):
    """Longest matching rule wins; Allow wins a tie (RFC 9309)."""
    path = re.sub(r"^https?://[^/]+", "", url) or "/"
    best = None
    for allow, length, pattern in _robots_rules():
        if pattern.match(path) and (best is None or (length, allow) > best):
            best = (length, allow)
    return best is None or best[1]


def _request(url, accept, method):
    global _last_request
    wait = _last_request + MIN_INTERVAL - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers, method=method)
    error = None
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status, resp_headers, body = resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        status, resp_headers, body = e.code, dict(e.headers), e.read()
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        status, resp_headers, body, error = None, {}, b"", repr(e)
    finally:
        _last_request = time.monotonic()
    return status, resp_headers, body, error


def fetch(url, accept="application/xml", method="GET", retry_failed=False):
    """Fetch once, with retries, and cache the outcome. Returns (meta, body)."""
    key = hashlib.sha256(f"{method} {accept} {url}".encode()).hexdigest()[:32]
    meta_path = CACHE / "http" / f"{key}.json"
    body_path = CACHE / "http" / f"{key}.body"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if not (retry_failed and meta["status"] != 200):
            return meta, body_path.read_bytes()
        attempts = meta["attempts"]
    else:
        attempts = []
    if not robots_allowed(url):
        sys.exit(f"robots.txt disallows {url}")
    while True:
        started = time.monotonic()
        at = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
        status, headers, body, error = _request(url, accept, method)
        attempts.append({"at": at, "status": status, "error": error,
                         "seconds": round(time.monotonic() - started, 2)})
        if status not in RETRYABLE or len(attempts) >= MAX_ATTEMPTS:
            break
        retry_after = headers.get("Retry-After", "")
        time.sleep(int(retry_after) if retry_after.isdigit() else 2 ** len(attempts))
    meta = {"url": url, "method": method, "accept": accept, "status": status,
            "headers": headers, "bytes": len(body), "attempts": attempts}
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    body_path.write_bytes(body)
    return meta, body


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# --- daily summaries ---------------------------------------------------------


def sumario_url(day):
    return f"{BASE}/datosabiertos/api/boe/sumario/{day:%Y%m%d}"


def parse_sumario(body):
    """Yield (diario, seccion, departamento, item) elements of a summary."""
    root = ET.fromstring(body)
    for diario in root.iterfind("./data/sumario/diario"):
        for seccion in diario.iterfind("seccion"):
            for dep in seccion.iterfind("departamento"):
                for item in dep.iter("item"):
                    yield diario, seccion, dep, item


def text(el, path):
    found = el.find(path)
    return (found.text or "").strip() if found is not None else ""


def check_item(item, seccion, dep):
    ident = text(item, "identificador")
    pdf = text(item, "url_pdf")
    return {
        "identifier": bool(re.fullmatch(r"BOE-[A-Z]-\d{4}-\d+", ident)),
        "title": bool(text(item, "titulo")),
        "section": bool(seccion.get("codigo") and seccion.get("nombre")),
        "department": bool(dep.get("codigo") and dep.get("nombre")),
        # The signed PDF is the only official and authentic format (BOE FAQ).
        "official_link": bool(ident) and bool(re.fullmatch(
            rf"https://www\.boe\.es/boe/dias/\d{{4}}/\d{{2}}/\d{{2}}/pdfs/{re.escape(ident)}\.pdf",
            pdf)),
        "html_link": text(item, "url_html").startswith("https://www.boe.es/"),
    }


def cmd_sumarios(args):
    until = dt.date.fromisoformat(args.until)
    rows, day, publication_days = [], until, 0
    while publication_days < args.days:
        meta, body = fetch(sumario_url(day), retry_failed=args.retry_failed)
        row = {"date": day.isoformat(), "weekday": f"{day:%a}", "http_status": meta["status"],
               "attempts": len(meta["attempts"]), "retrieved": False, "issues": "",
               "sumario_ids": "", "items": 0}
        checks = ("identifier", "title", "section", "department", "official_link", "html_link")
        row |= {f"with_{c}": 0 for c in checks}
        row |= {"items_complete": 0, "sections": "", "bytes": meta["bytes"],
                "seconds": meta["attempts"][-1]["seconds"]}
        if meta["status"] == 200:
            root = ET.fromstring(body)
            diarios = root.findall("./data/sumario/diario")
            date_ok = text(root, "./data/sumario/metadatos/fecha_publicacion") == f"{day:%Y%m%d}"
            row["issues"] = " ".join(d.get("numero", "?") for d in diarios)
            row["sumario_ids"] = " ".join(text(d, "sumario_diario/identificador") for d in diarios)
            sections, seen = {}, set()
            for _, seccion, dep, item in parse_sumario(body):
                ident = text(item, "identificador")
                if ident in seen:
                    print(f"{day} duplicate item {ident}", file=sys.stderr)
                seen.add(ident)
                result = check_item(item, seccion, dep)
                row["items"] += 1
                for c in checks:
                    row[f"with_{c}"] += result[c]
                row["items_complete"] += all(result[c] for c in checks[:5])
                code = seccion.get("codigo")
                sections[code] = sections.get(code, 0) + 1
            row["sections"] = " ".join(f"{k}:{v}" for k, v in sections.items())
            row["retrieved"] = bool(diarios) and date_ok and row["items"] > 0
            publication_days += row["retrieved"]
        rows.append(row)
        print(f"{row['date']} {row['weekday']} {row['http_status']} "
              f"issues={row['issues'] or '-'} items={row['items']} "
              f"complete={row['items_complete']}")
        day -= dt.timedelta(days=1)
        if (until - day).days > 120:
            sys.exit("no 60 publication days found within 120 calendar days")
    rows.reverse()
    write_csv(RESULTS / "sumarios.csv", rows)
    check_numbering(rows)


def check_numbering(rows):
    """Issue numbers restart each year and run consecutively; a gap is a missed issue."""
    numbers = sorted(int(n) for r in rows for n in r["issues"].split())
    gaps = [(a, b) for a, b in zip(numbers, numbers[1:]) if b != a + 1]
    print(f"issues {numbers[0]}..{numbers[-1]}: {len(numbers)} issues, gaps: {gaps or 'none'}")


# --- links to the official text ----------------------------------------------


def cmd_links(args):
    """Resolve the PDF link of one item per publication day, chosen at random."""
    rng = random.Random(args.seed)
    rows = []
    with (RESULTS / "sumarios.csv").open(encoding="utf-8") as f:
        days = [r for r in csv.DictReader(f) if r["retrieved"] == "True"]
    for r in days:
        day = dt.date.fromisoformat(r["date"])
        _, body = fetch(sumario_url(day))
        items = [item for *_, item in parse_sumario(body)]
        item = rng.choice(items)
        pdf = text(item, "url_pdf")
        meta, _ = fetch(pdf, accept=None, method="HEAD")
        rows.append({"date": r["date"], "identifier": text(item, "identificador"),
                     "url_pdf": pdf, "status": meta["status"],
                     "content_type": meta["headers"].get("Content-Type", ""),
                     "attempts": len(meta["attempts"])})
        print(rows[-1]["date"], rows[-1]["identifier"], rows[-1]["status"],
              rows[-1]["content_type"])
    write_csv(RESULTS / "links.csv", rows)


# --- amendment and repeal relations ------------------------------------------


def cmd_relations(args):
    rows = []
    with (HERE / "relations.csv").open(encoding="utf-8") as f:
        relations = list(csv.DictReader(f))
    for rel in relations:
        affected, amending = rel["affected_id"], rel["amending_id"]
        api = f"{BASE}/datosabiertos/api/legislacion-consolidada/id/{affected}"
        meta_m, body_m = fetch(f"{api}/metadatos")
        meta_a, body_a = fetch(f"{api}/analisis")
        row = {"n": rel["n"], "affected_id": affected, "amending_id": amending,
               "expected": rel["relation"], "metadatos_status": meta_m["status"],
               "analisis_status": meta_a["status"], "estado_consolidacion": "",
               "fecha_actualizacion": "", "found": False, "relations_found": "",
               "texts_found": ""}
        if meta_m["status"] == 200:
            m = ET.fromstring(body_m).find("./data/metadatos")
            row["estado_consolidacion"] = text(m, "estado_consolidacion")
            row["fecha_actualizacion"] = text(m, "fecha_actualizacion")
        if meta_a["status"] == 200:
            matches = [p for p in ET.fromstring(body_a).iterfind(
                "./data/analisis/referencias/posteriores/posterior")
                if text(p, "id_norma") == amending]
            row["found"] = bool(matches)
            row["relations_found"] = " | ".join(
                f"{p.find('relacion').get('codigo')} {text(p, 'relacion')}" for p in matches)
            row["texts_found"] = " | ".join(text(p, "texto") for p in matches)
        rows.append(row)
        print(f"{row['n']:>2} {affected} <- {amending}: found={row['found']} "
              f"{row['relations_found']} [{row['estado_consolidacion']}]")
    write_csv(RESULTS / "relations.csv", rows)
    print(f"{sum(r['found'] for r in rows)} of {len(rows)} relations found")


# --- behaviour the design must know ------------------------------------------


def cmd_probes(args):
    """A handful of requests that show formats, errors and headers."""
    rows = []
    probes = [
        ("sumario, no Accept header", sumario_url(dt.date.fromisoformat(args.weekday)), None),
        ("sumario, JSON", sumario_url(dt.date.fromisoformat(args.weekday)), "application/json"),
        ("sumario, a Sunday", sumario_url(dt.date.fromisoformat(args.sunday)), "application/xml"),
        ("sumario, tomorrow", sumario_url(dt.date.fromisoformat(args.tomorrow)),
         "application/xml"),
        ("sumario, malformed date", f"{BASE}/datosabiertos/api/boe/sumario/2026-10-19",
         "application/xml"),
        ("consolidated, unknown id",
         f"{BASE}/datosabiertos/api/legislacion-consolidada/id/BOE-A-2026-999999/metadatos",
         "application/xml"),
        ("text index, JSON",
         f"{BASE}/datosabiertos/api/legislacion-consolidada/id/{args.law}/texto/indice",
         "application/json"),
        ("text block, JSON",
         f"{BASE}/datosabiertos/api/legislacion-consolidada/id/{args.law}/texto/bloque/a1",
         "application/json"),
        ("text block, no Accept header",
         f"{BASE}/datosabiertos/api/legislacion-consolidada/id/{args.law}/texto/bloque/a1", None),
        ("text block, XML",
         f"{BASE}/datosabiertos/api/legislacion-consolidada/id/{args.law}/texto/bloque/a1",
         "application/xml"),
    ]
    for name, url, accept in probes:
        meta, body = fetch(url, accept=accept)
        h = meta["headers"]
        rows.append({"probe": name, "url": url, "accept": accept or "", "status": meta["status"],
                     "content_type": h.get("Content-Type", ""), "bytes": meta["bytes"],
                     "cache_headers": " ".join(f"{k}={v}" for k, v in h.items() if k.lower() in (
                         "cache-control", "etag", "last-modified", "expires", "age")),
                     "rate_limit_headers": " ".join(f"{k}={v}" for k, v in h.items()
                                                    if "rate" in k.lower() or "limit" in k.lower()),
                     "body_start": body[:160].decode("utf-8", "replace").replace("\n", " ")})
        print(json.dumps(rows[-1], ensure_ascii=False))
    write_csv(RESULTS / "probes.csv", rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(required=True)
    p = sub.add_parser("sumarios", help="fetch the daily summaries")
    p.add_argument("--until", required=True, help="last date, YYYY-MM-DD")
    p.add_argument("--days", type=int, default=60, help="publication days to collect")
    p.add_argument("--retry-failed", action="store_true", help="refetch cached failures")
    p.set_defaults(func=cmd_sumarios)
    p = sub.add_parser("links", help="resolve one official PDF link per day")
    p.add_argument("--seed", type=int, default=1)
    p.set_defaults(func=cmd_links)
    p = sub.add_parser("relations", help="check the relations fixed in relations.csv")
    p.set_defaults(func=cmd_relations)
    p = sub.add_parser("probes", help="record formats, errors and headers")
    p.add_argument("--weekday", default="2026-10-19")
    p.add_argument("--sunday", default="2026-10-18")
    p.add_argument("--tomorrow", default="2026-10-21")
    p.add_argument("--law", default="BOE-A-2015-10565")
    p.set_defaults(func=cmd_probes)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

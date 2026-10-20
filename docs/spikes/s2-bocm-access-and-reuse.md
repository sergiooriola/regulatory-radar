# S2. BOCM access and reuse

- **Issue:** [#3](https://github.com/sergiooriola/regulatory-radar/issues/3)
- **Risk:** R04
- **Status:** Done. Threshold met: BOCM is in the first version.
- **Run:** 2026-10-20. Every source below was read on that date.
- **Code:** [`spikes/s2/`](../../spikes/s2/), throwaway

## Question

Can the Comunidad de Madrid's official bulletin be read by a program every publication day, and
do its terms allow automated reuse?

## Threshold, as fixed in the [spike plan](README.md#s2-bocm-access-and-reuse)

20 of 20 days retrieved, the three hand checks match item for item, and the terms allow
automated reuse. Otherwise BOCM is left out of the first version and every notice says so (risk
R04).

## Hand-check days, chosen before the run

The 20 days are the 20 most recent bulletins up to 2026-10-20. Three are checked by hand, chosen
to cover a weekday, a Saturday and the largest bulletin of the window:

| Date | Bulletin | Why |
| --- | --- | --- |
| 2026-10-20 | 250 | Today's bulletin, a weekday |
| 2026-10-17 | 248 | A Saturday, a smaller bulletin |
| 2026-10-09 | 241 | The largest bulletin of the window by number of items |

## Result

**Pass.** All three parts of the threshold are met.

| Part of the threshold | Result |
| --- | --- |
| 20 of 20 days retrieved | 20 of 20: bulletins 231 to 250 (2026-09-28 to 2026-10-20), 1,439 items, every request answered 200 at the first attempt, no retries |
| The three hand checks match item for item | 3 of 3: 65, 23 and 121 items, every number, section, department, sub-body and title the same as the summary a reader sees |
| The terms allow automated reuse | Yes, with conditions: follow robots.txt, cite the BOCM and link to the official text, do not alter it, and treat personal data under data protection law |

The official machine-readable sources are an RSS feed and one XML file per item; no API, no
bulk download and no open-data dataset exist. They are enough: the extraction from them
agreed with the HTML summary on every item of every day, once the comparison was taught how
the summary lays out each section (see [Retrieval](#retrieval)).

## What is published, and what a program may read

The 2026-10-19 note in R04 ("no API or RSS feed") is out of date. The BOCM publishes RSS feeds
and per-item XML and JSON; there is still no documented API and no open-data dataset.

| Source | What it gives | robots.txt | Used |
| --- | --- | --- | --- |
| [`/sumarios.rss`](https://www.bocm.es/sumarios.rss) | The last 20 bulletins: date, number, link to the HTML summary, and every item's CVE with links to its PDF and EPUB | Allowed | Yes: the list of days and items |
| [`/boletines.rss`](https://www.bocm.es/boletines.rss) | The last 20 bulletins with links to the full-bulletin PDF and the summary PDF | Allowed (the PDFs it links are not) | No |
| [`/ultimo-boletin.xml`](https://www.bocm.es/ultimo-boletin.xml) | Today's items only, with title and CVE | Allowed | No (one day only) |
| `/boletin-completo/BOCM-<yyyymmdd>/<no>` (HTML summary) | Every item of a bulletin under its section, sub-section, department and sub-body, with number, title and links | Allowed | Yes: cross-check and hand check |
| `/boletin/CM_Orden_BOCM/<yyyy>/<mm>/<dd>/<CVE>.xml` and `.json` (per item) | Identifier, department and sub-bodies, rank, dates, title, section, sub-section, bulletin number, pages, links, full text | Allowed, except items listed one by one (see below) | Yes: the extraction |
| `/boletin/CM_Boletin_BOCM/...` (summary PDF, full-bulletin PDF and a summary XML per bulletin) | The whole summary in one file | **Disallowed** | No |
| `/eli/...` and RDFa in item pages | ELI identifiers and metadata, only for regulations (laws, decrees, orders) | Allowed | No |
| [datos.comunidad.madrid](https://datos.comunidad.madrid/robots.txt) | The regional open-data catalogue | **Disallowed** for every agent but named search engines (`User-agent: *` / `Disallow: /`) | No |

Sources: [RSS page](https://www.bocm.es/rss), [robots.txt](https://www.bocm.es/robots.txt),
[ELI page](https://www.bocm.es/identificador-europeo-de-legislacion), the bulletin page
[`/boletin/bocm-20261020-250`](https://www.bocm.es/boletin/bocm-20261020-250) and its
[summary](https://www.bocm.es/boletin-completo/BOCM-20261020/250), all read 2026-10-20.

**robots.txt** ([www.bocm.es/robots.txt](https://www.bocm.es/robots.txt), 1,976 lines, read
2026-10-20) has one group, for every user agent, with `Crawl-delay: 10`. It disallows
`/boletin/CM_Boletin_BOCM/` (whole bulletins), `/search/`, `*.epub` and about 1,800 individual
item files under `/boletin/CM_Orden_BOCM/` and `/boletin/CM_Seccion_BOCM/`. The individual
entries are the BOCM's way of honouring de-indexing requests: its
[right-to-erasure page](https://www.bocm.es/ejercicio-del-derecho-de-supresion-al-olvido) asks
applicants to list "los enlaces y documentos que quiere desindexar". Python's
`urllib.robotparser` does not implement the `*` and `$` wildcards these rules use, so the spike
matches rules itself following RFC 9309.

**No open data.** The BOCM's "Bases de datos públicas"
[page](https://www.bocm.es/enlaces-y-servicios/bases-de-datos-publicas) says "Actualmente no
hay contenido clasificado con este término". The national catalogue datos.gob.es, which
federates the regional ones, has no dataset whose title contains "Oficial de la Comunidad de
Madrid" ([API query](https://datos.gob.es/apidata/catalog/dataset/title/Oficial%20de%20la%20Comunidad%20de%20Madrid.json));
the only "BOCM" datasets are one town council's lists of its own publications
([API query](https://datos.gob.es/apidata/catalog/dataset/title/BOCM.json)). Other regions do
publish their bulletins there (the Basque Country, Asturias, Castilla y León). The regional
catalogue itself could not be searched by a program because its robots.txt forbids it; a search
engine restricted to that domain found no BOCM dataset.

## What was done

1. Read the BOCM site's robots.txt, RSS page, legal notice, FAQ, governing rules and ELI page,
   and the reuse laws they point to (below).
2. [`fetch.py`](../../spikes/s2/fetch.py): every request goes through one helper with a
   User-Agent that names the project and links to the repository, RFC 9309 robots.txt matching,
   the host's `Crawl-delay` (10 s on bocm.es, at least 1 s elsewhere), a per-host lock, retries
   on server errors, and a local cache so nothing is fetched twice.
3. [`retrieve.py`](../../spikes/s2/retrieve.py) reads `/sumarios.rss`, which lists exactly the
   20 most recent bulletins, and for each one the HTML summary and the XML of every item. It
   extracts each item's metadata from the XML and checks, per day:
   - the feed, the HTML summary and the XML give the same set of items, numbered 1 to N with no
     gap;
   - every item has an identifier, title, section, department (issuer), publication date and a
     link to the official PDF;
   - title, section and sub-section, department, sub-body, PDF link, date and bulletin number
     agree between the XML and the summary.
4. [`handcheck.py`](../../spikes/s2/handcheck.py) lays out, for each hand-check day, the
   summary page as a reader sees it (its own text extraction, not the program's parser) and the
   program's extraction in the same layout. The two were read side by side, item by item.

Titles are kept in a git-ignored folder because many name people (appointments, staff
selections, judges of the peace); only counts and check results are committed, in
[`results.csv`](../../spikes/s2/results.csv).

## Retrieval

One run on 2026-10-20 from 09:58 to 14:14 (Madrid time) made 1,460 requests to bocm.es: the
feed, 20 HTML summaries and 1,439 item XML files, one every 10 seconds as robots.txt asks. All
answered 200 at the first attempt. Each check was then re-run from the local cache, with no new
requests.

| Date | Day | Bulletin | Items | Same items in feed, summary and XML | Numbered 1 to N | Missing fields, first run / fixed | Differences, first run / fixed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-20 | Tue | 250 | 65 | Yes | Yes | 0 / 0 | 0 / 0 |
| 2026-10-19 | Mon | 249 | 89 | Yes | Yes | 0 / 0 | 0 / 0 |
| 2026-10-17 | Sat | 248 | 23 | Yes | Yes | 0 / 0 | 0 / 0 |
| 2026-10-16 | Fri | 247 | 82 | Yes | Yes | 0 / 0 | 6 / 0 |
| 2026-10-15 | Thu | 246 | 80 | Yes | Yes | 3 / 0 | 7 / 0 |
| 2026-10-14 | Wed | 245 | 89 | Yes | Yes | 0 / 0 | 3 / 0 |
| 2026-10-13 | Tue | 244 | 99 | Yes | Yes | 0 / 0 | 5 / 0 |
| 2026-10-12 | Mon | 243 | 22 | Yes | Yes | 0 / 0 | 2 / 0 |
| 2026-10-10 | Sat | 242 | 28 | Yes | Yes | 0 / 0 | 9 / 0 |
| 2026-10-09 | Fri | 241 | 121 | Yes | Yes | 0 / 0 | 7 / 0 |
| 2026-10-08 | Thu | 240 | 89 | Yes | Yes | 0 / 0 | 3 / 0 |
| 2026-10-07 | Wed | 239 | 69 | Yes | Yes | 1 / 0 | 5 / 0 |
| 2026-10-06 | Tue | 238 | 64 | Yes | Yes | 2 / 0 | 7 / 0 |
| 2026-10-05 | Mon | 237 | 83 | Yes | Yes | 0 / 0 | 5 / 0 |
| 2026-10-03 | Sat | 236 | 20 | Yes | Yes | 0 / 0 | 0 / 0 |
| 2026-10-02 | Fri | 235 | 82 | Yes | Yes | 0 / 0 | 1 / 0 |
| 2026-10-01 | Thu | 234 | 88 | Yes | Yes | 1 / 0 | 102 / 0 |
| 2026-09-30 | Wed | 233 | 101 | Yes | Yes | 9 / 0 | 124 / 0 |
| 2026-09-29 | Tue | 232 | 60 | Yes | Yes | 0 / 0 | 62 / 0 |
| 2026-09-28 | Mon | 231 | 85 | Yes | Yes | 1 / 0 | 93 / 0 |

Sundays are not published; the national holiday of 12 October was. That matches the
publication rule on the BOCM's [about page](https://www.bocm.es/que-es-bocm) (read
2026-10-20): every day except Sundays, Good Friday, 25 December and 1 January.

**The first comparison found 441 differences and 17 missing issuers.** Every one was looked
at. None was a difference in content; all came from the comparison not knowing how the source
lays out some items. The program was corrected, the comparison re-run from the cache, and both
results are in the history ([first](https://github.com/sergiooriola/regulatory-radar/commit/f06cd5a),
[after the fix](https://github.com/sergiooriola/regulatory-radar/commit/d0f2b19)).

| Cause | Differences | Fix |
| --- | --- | --- |
| Up to 2026-10-01, the XML starts each line of a title with "." where the summary has "—" | 333 titles, every item of 4 days | Ignore the separator at the start of each line, not only of the title |
| The summary shows the department and sub-body only in section I; sections II, III and V show the section line alone, and IV the court | 35 section lines, 73 sub-bodies | Compare the headings the summary actually shows for each section |
| Section V (other notices: cooperatives, foundations, private universities) has no `<departamento>` and only empty `<organismo>` elements | 16 missing issuers | Take the issuer from the first heading of the item's text, the one the PDF prints in capitals |
| One section III item's title starts with "." | 1 missing issuer | Same separator fix |

## Hand checks

For each of the three days, [`handcheck.py`](../../spikes/s2/handcheck.py) wrote the summary
page's visible text and the program's extraction in the same layout. A line-by-line diff
showed no difference on any of the three days. The reader's view was then read item by item:
every number from 1 to N present once, under the right section, department and sub-body, with
the right title.

| Date | Bulletin | Items | Lines in each view | Differences | Sections covered |
| --- | --- | --- | --- | --- | --- |
| 2026-10-20 | 250 | 65 | 208 | 0 | I B, I C, I D, III, IV |
| 2026-10-17 | 248 | 23 | 76 | 0 | I C, I D |
| 2026-10-09 | 241 | 121 | 368 | 0 | I A, I B, I C, I D, II, III |

Between them the three days cover every section except V, which the 20-day comparison covers
(16 items).

## Reuse terms

**What the BOCM itself says.** Neither the site nor Decreto 126/2022, which governs the electronic
edition, states reuse terms or a licence for the bulletin's content.

- The [legal notice](https://www.bocm.es/aviso-legal) (read 2026-10-20) is the generic one of the
  Comunidad de Madrid's websites. Its only restriction is about the site as a work: "Los derechos
  de propiedad intelectual de este canal de Internet, su diseño gráfico y los códigos que
  contiene, son titularidad de la Comunidad de Madrid, a no ser que se indique una titularidad
  diferente. La reproducción, distribución, comercialización o transformación no autorizadas de
  estas obras, a no ser que sea para uso personal y privado, constituye una infracción de los
  derechos de propiedad intelectual de la Comunidad de Madrid o de aquél que sea titular."
- [Decreto 126/2022](https://www.bocm.es/boletin/CM_Orden_BOCM/2022/12/12/BOCM-20221212-1.PDF)
  ([ELI](https://www.bocm.es/eli/es-md/d/2022/12/07/126)), listed as current on the BOCM's
  [governing rules page](https://www.bocm.es/normativa-reguladora) (read 2026-10-20; no amending
  act was found), guarantees free access and a free database but does not mention reuse:
  - art. 7.1: "el acceso universal y gratuito a la edición electrónica del BOLETÍN OFICIAL DE LA
    COMUNIDAD DE MADRID";
  - art. 8: "una base de datos gratuita que permita la búsqueda, recuperación e impresión de las
    disposiciones y actos publicados";
  - art. 6: the electronic edition uses "estándares abiertos";
  - additional provision 2: whoever orders an insertion decides "la finalidad, contenido y uso
    de los datos de carácter personal publicados, así como la posibilidad de bloqueo de los
    mismos cuando hayan dejado de ser necesarios o pertinentes".

**What the law says.** With no conditions set by the BOCM, the general rules apply:

- The bulletin's legal content is not protected by copyright. Real Decreto Legislativo 1/1996,
  [art. 13](https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930#a13): "No son objeto de propiedad
  intelectual las disposiciones legales o reglamentarias y sus correspondientes proyectos, las
  resoluciones de los órganos jurisdiccionales y los actos, acuerdos, deliberaciones y dictámenes
  de los organismos públicos". The legal notice's restriction on "estas obras" therefore reaches
  the site's design and code, not the rules and acts it publishes.
- [Ley 37/2007](https://www.boe.es/buscar/act.php?id=BOE-A-2007-19814) on the reuse of
  public-sector information (consolidated text, last update published 2023-05-09) applies to "las
  Administraciones de las Comunidades Autónomas" and their public bodies (art. 2.a and 2.b), so
  to the BOCM, an autonomous body. Art. 4.2: "La reutilización de documentos no estará sujeta a
  condiciones a menos que estas sean objetivas, proporcionadas, no discriminatorias y estén
  justificadas por un objetivo de interés público. En los supuestos de sujeción, las condiciones
  se fijarán en una licencia." No licence has been published. Art. 4.4: public bodies "no
  ejercerán el derecho del fabricante de una base de datos … para evitar la reutilización".
  Art. 8 lists the usual general conditions a body may impose: content not altered, meaning not
  distorted, "Que se cite la fuente", "Que se mencione la fecha de la última actualización".
- [Ley 10/2019](https://www.boe.es/buscar/act.php?id=BOE-A-2019-10102), the Comunidad de
  Madrid's transparency law (consolidated text, last update published 2024-12-27), applies to
  "Los organismos autónomos" of the region (art. 2.1.b). Art. 6.f: "La información pública podrá
  ser reutilizada con cualquier objetivo legítimo, en especial la reproducción y divulgación, por
  cualquier medio, de los datos objeto de publicidad activa y la creación de productos o
  servicios de información basados en estos datos." Its additional provision 1.3 makes it apply
  to information "destinada a la reutilización" where the specific rules say nothing.
- Personal data is the limit. Ley 37/2007 art. 4.6: "La reutilización de documentos que
  contengan datos de carácter personal se regirá por lo dispuesto en la Ley Orgánica 3/2018";
  art. 3.4 excludes information where data protection prevails.

**Automated access.** The BOCM publishes RSS feeds and per-item XML and JSON for programs to
read, and its robots.txt admits every user agent to them at one request every 10 seconds.

**Conclusion.** The terms allow automated reuse of the bulletin's metadata and texts for the
radar's purpose, under conditions: follow robots.txt, cite the BOCM and link to the official
publication, do not alter the content, and treat the personal data in items under data
protection law. The one ambiguity is the legal notice's general wording ("La utilización no
autorizada de la información contenida en este canal …"), which does not distinguish the site
from the official texts. Art. 13 of the copyright act and art. 4.2 of Ley 37/2007 resolve it in
favour of reuse. A written answer from the Organismo Autónomo BOCM would settle it beyond doubt.
Writing to them is outward-facing, so it is left to the owner (see the pull request).

## Decision

**BOCM is in the first version.** R04's fallback (leave BOCM out and say so in every notice)
does not apply. R04's description is out of date: the BOCM does publish RSS feeds and per-item
XML (see the pull request for the suggested change to the risk register).

The reading of the reuse terms is the engineer's, from the law cited above, not a lawyer's.
Whether to ask the BOCM for written confirmation is left to the owner.

## What the design must know

- **Sources.** `/sumarios.rss` lists the last 20 bulletins with every item's CVE. The HTML
  summary of a bulletin gives, in one request, each item's number, section, department,
  sub-body, title and PDF link; over 1,439 items it agreed with the item XML on all of them, so
  it is enough to triage a day. The item XML adds rank, dates, pages and the full text.
- **Rate.** robots.txt asks for 10 seconds between requests. A day costs one request for the
  summary plus one per item: about 12 minutes for the window's average of 72 items, 21 minutes
  for its largest day (121). A standard AWS Lambda function stops after 900 seconds (15
  minutes); only Lambda Managed Instances invoked asynchronously reach 90 minutes
  ([Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html),
  read 2026-10-20). So either the summary is used for triage and the XML fetched only for
  candidates, or the fetch is spread over several runs or done by a longer-running task.
- **Catch-up.** The feed holds 20 bulletins, a little over three weeks. A daily job that stops
  for longer than that loses days from the feed; the summary URL needs the bulletin number,
  which is sequential within the year. Catching up through it was not tested.
- **The format changes without notice.** Two changes fell inside the 20-day window: the title
  separator in the XML ("." until 2026-10-01, "–" from 2026-10-02), and section III's first `<organismo>`,
  which gave the town until 2026-10-19 and is missing on 2026-10-20 and on some earlier items.
  A daily self-check (the same items in the feed, the summary and the XML, numbered 1 to N)
  catches both kinds of change.
- **Where the issuer is.** Sections I and II: `<departamento>`. Section IV:
  `<departamento>` is the court ("Tribunal Superior de Justicia"). Section III: the first
  `<organismo>` (the town) or, when it is missing, the text's first heading ("AYUNTAMIENTO
  DE …"); the design needs one form for both. Section V: only the text's first heading. The
  source is not always consistent with itself: one item's heading says "NOROESTE" where its
  title says "Noreste". Sub-bodies are the later `<organismo>` elements.
- **robots.txt changes.** About 1,800 individual items are disallowed, added as people ask to
  be de-indexed. The radar should read robots.txt every day, never fetch a disallowed item, and
  decide what to do with stored copies of items that become disallowed.
- **Personal data.** Many titles and texts name people (appointments, selection lists, judges
  of the peace, notifications). Storing them falls under data protection law; the design must
  set what is kept and for how long.
- **Time of publication.** Not established. The feed's `Last-Modified` header changes when the
  site regenerates it, not when a bulletin is published, so the radar should poll and compare
  bulletin numbers.
- **The bulletin's own summary XML** (`/boletin/CM_Boletin_BOCM/…`) would give a whole day in
  one request, but robots.txt disallows it. Asking the BOCM for permission is a decision for
  the owner.
- **Attribution.** Each notice should cite the BOCM, the bulletin number and date, and link to
  the item's official PDF.

## Deviations from the method

- **The hand checks used the HTML summary, not the summary PDF.** The method allows either
  ("the official PDF or the page a person would read"), but the PDF was the first choice.
  robots.txt disallows `/boletin/CM_Boletin_BOCM/`, where the summary PDF lives, so a program
  may not fetch it. A person can open it in a browser; that spot check has not been done.
- **The hand checks were done by the engineer running the spike** (an AI agent), reading the
  reader's view with a diff as an aid, not by an independent person.
- **The comparison was corrected after the first run**, for the four causes listed under
  [Retrieval](#retrieval). The days, the threshold and the hand-check days did not change, and
  both results are committed.
- **Time box.** Two days allowed; one used, most of it waiting on the 10-second crawl delay.

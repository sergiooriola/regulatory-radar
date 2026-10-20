# S2. BOCM access and reuse

- **Issue:** [#3](https://github.com/sergiooriola/regulatory-radar/issues/3)
- **Risk:** R04
- **Status:** RESULT_STATUS
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

RESULT_SUMMARY

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

**No open data.** The BOCM's
["Bases de datos públicas" page](https://www.bocm.es/enlaces-y-servicios/bases-de-datos-publicas) says "Actualmente no
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

RESULT_RETRIEVAL

## Hand checks

RESULT_HANDCHECK

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

RESULT_DECISION

## What the design must know

RESULT_DESIGN

## Deviations from the method

RESULT_DEVIATIONS

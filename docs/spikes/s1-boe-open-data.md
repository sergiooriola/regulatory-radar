# S1. BOE open data

- **Status:** passed
- **Run on:** 2026-10-20
- **Code and data:** [spikes/s1/](../../spikes/s1/README.md)

## Question

Do the BOE open-data APIs return, for every publication day, every item with the metadata the
radar needs, and do they expose which rules amend or repeal a given rule?

## Threshold, as fixed

Quoted from [the spike plan](README.md#s1-boe-open-data), approved on 2026-10-19:

- **Method:** Fetch the daily summary (`/datosabiertos/api/boe/sumario/{yyyymmdd}`) for 60
  consecutive publication days. For ten amendment or repeal relations chosen and recorded before
  the run, query the consolidated-legislation API for the affected rule and check its
  references.
- **Threshold:** 60 of 60 days retrieved (retries allowed); every item has an identifier, title,
  section, department and a link to the official text; 10 of 10 relations found.
- **Time box:** 2 days.

## Result

| Part of the threshold | Result | Verdict |
| --- | --- | --- |
| 60 of 60 publication days retrieved | 60 of 60, each on the first attempt | Pass |
| Every item has identifier, title, section, department and a link to the official text | 11,718 of 11,718 items | Pass |
| 10 of 10 relations found | 10 of 10, each with the expected relation type | Pass |
| Time box of 2 days | Less than half a day | Within |

**Decision:** the BOE open-data APIs are fit to be the radar's source for the daily watch and for
detecting amendments and repeals of the rules in the map. The design can rely on them, with the
constraints listed under [What the design must know](#what-the-design-must-know).

## Sources

All were read on 2026-10-20.

| Source | URL |
| --- | --- |
| Open-data API page (endpoints, formats, error codes) | <https://www.boe.es/datosabiertos/api/api.php> |
| API documentation for the BOE summaries, dated 28 June 2024 | <https://www.boe.es/datosabiertos/documentos/APIsumarioBOE.pdf> |
| API documentation for consolidated legislation, dated 2 September 2025 | <https://www.boe.es/datosabiertos/documentos/APIconsolidada.pdf> |
| FAQ on the BOE summary API | <https://www.boe.es/datosabiertos/faq/boe.php> |
| FAQ on the consolidated-legislation API | <https://www.boe.es/datosabiertos/faq/consolidada.php> |
| Reuse conditions (licence approved by the Agency's resolution of 27 June 2024) | <https://www.boe.es/informacion/aviso_legal/index.php#reutilizacion> |
| robots.txt | <https://www.boe.es/robots.txt> |

`https://www.boe.es/datosabiertos/` redirects to the API page. No official source states a rate
limit or a usage quota for these APIs: none of the documents above mentions one.

## What was done

Every API request went through [spikes/s1/s1.py](../../spikes/s1/s1.py): Python 3.14, standard
library only, at least 1.1 s between requests, a User-Agent naming the project and linking to
this repository, every URL checked against robots.txt before it was requested, and every
response cached locally (git-ignored) so nothing was fetched twice. The documentation, the texts
of the candidate rules and the ELI pages were fetched with curl under the same User-Agent, pause
and cache; every URL requested is allowed by robots.txt. The spike made about 190 requests in
total.

### Daily summaries

1. Requested the summary for every calendar day from 2026-10-20 backwards until 60 days had a
   bulletin: 70 calendar days, from 2026-08-12 to 2026-10-20, in XML (`Accept:
   application/xml`). Failed requests could be retried up to five times; none needed it.
2. A day counted as retrieved when the API answered 200, the response's publication date matched
   the requested date, and it held at least one issue with at least one item.
3. For each item, checked that it had an identifier of the form `BOE-X-yyyy-n`, a non-empty
   title, a section code and name, a department code and name, and a link to the official text.
   The BOE says that the electronically signed PDF is the only official and authentic format
   (FAQ on the summary API), so the link checked is `url_pdf`, which must point to
   `https://www.boe.es/boe/dias/yyyy/mm/dd/pdfs/<identifier>.pdf`. The HTML link (`url_html`)
   was recorded as well.
4. Resolved the PDF link of one item per publication day, chosen at random with a fixed seed.

Per-day results are in [results/sumarios.csv](../../spikes/s1/results/sumarios.csv) and the
link checks in [results/links.csv](../../spikes/s1/results/links.csv).

#### How publication days were known

Three independent signals agree:

- The BOE states that the bulletin "se publica todos los días del año, salvo los domingos", with
  occasional extraordinary issues (FAQ on the summary API).
- The ten days without a bulletin in the window are exactly the ten Sundays, and for each of them
  the API answered 404 "La información solicitada no existe".
- Issue numbers are consecutive within a year. The 64 issues in the window run from 197 to 260
  with no gap, so no issue, ordinary or extraordinary, was published on a day the API reported
  as empty.

Saturdays and public holidays are publication days: 12 October, a national holiday, had a
bulletin with 86 items.

### Amendment and repeal relations

1. Chose ten relations from the text of rules published in the window (each rule's own repealing
   or final provision, read in its official HTML version), resolved each affected rule's
   identifier through its ELI permalink to the original gazette version, and committed the list
   ([spikes/s1/relations.csv](../../spikes/s1/relations.csv), commit `77f8c5d`) before any
   request to the consolidated-legislation API. How they were chosen is set out in
   [spikes/s1/README.md](../../spikes/s1/README.md).
2. For each affected rule, requested `/legislacion-consolidada/id/{id}/analisis` and
   `/legislacion-consolidada/id/{id}/metadatos`, and looked for a later reference
   (`referencias/posteriores/posterior`) whose `id_norma` is the amending rule.

Results are in [results/relations.csv](../../spikes/s1/results/relations.csv).

## Results in detail

### Summaries in figures

| Measure | Value |
| --- | --- |
| Calendar days requested | 70 (2026-08-12 to 2026-10-20) |
| Publication days | 60, all retrieved on the first attempt |
| Days without a bulletin | 10, all Sundays, all answered 404 |
| Issues | 64: one per publication day plus 4 extraordinary issues |
| Items | 11,718 (4,299 `BOE-A`, 7,419 `BOE-B`) |
| Items per publication day | min 86 (12 October), median 183.5, mean 195.3, max 378 |
| Items with all five required fields | 11,718 (100 %) |
| Items with an HTML link as well | 11,718 (100 %) |
| PDF links resolved (one per day) | 60 of 60 answered 200 `application/pdf` |
| Response size (XML) | 78 KB to 251 KB a day |

Items by section over the 60 days:

| Section | Items |
| --- | --- |
| I. Disposiciones generales (`1`) | 190 |
| II.A. Nombramientos, situaciones e incidencias (`2A`) | 735 |
| II.B. Oposiciones y concursos (`2B`) | 1,769 |
| III. Otras disposiciones (`3`) | 1,600 |
| IV. Administración de Justicia (`4`) | 2,044 |
| V.A. Contratación del Sector Público (`5A`) | 2,333 |
| V.B. Otros anuncios oficiales (`5B`) | 2,988 |
| V.C. Anuncios particulares (`5C`) | 54 |
| Tribunal Constitucional (`T`) | 5 |

### Relations found

| # | Affected rule | Amending rule | Expected | Found in the affected rule's later references |
| --- | --- | --- | --- | --- |
| 1 | Real Decreto 1659/1998 (`BOE-A-1998-19580`) | Real Decreto 723/2026 (`BOE-A-2026-19200`) | Repeal | 210 SE DEROGA |
| 2 | Estatuto de los Trabajadores, RDLeg 2/2015 (`BOE-A-2015-11430`) | Ley 4/2026 (`BOE-A-2026-20528`) | Amendment | 270 SE MODIFICA "el art. 37.6" |
| 3 | Ley 35/2006, IRPF (`BOE-A-2006-20764`) | Real Decreto-ley 23/2026 (`BOE-A-2026-18828`) | Amendment | 270 SE MODIFICA |
| 4 | Real Decreto 1684/1997 (`BOE-A-1997-24617`) | Real Decreto 722/2026 (`BOE-A-2026-18998`) | Amendment | 270 SE MODIFICA |
| 5 | RDLeg 1/2013, derechos de las personas con discapacidad (`BOE-A-2013-12632`) | Ley 4/2026 (`BOE-A-2026-20528`) | Amendment | 270 SE MODIFICA |
| 6 | Real Decreto 1414/2006 (`BOE-A-2006-22080`) | Real Decreto 707/2026 (`BOE-A-2026-18509`) | Repeal | 210 SE DEROGA, effective 2 January 2027 |
| 7 | Real Decreto 366/2007 (`BOE-A-2007-6239`) | Real Decreto 707/2026 (`BOE-A-2026-18509`) | Amendment | 270 SE MODIFICA, effective 2 January 2027 |
| 8 | Real Decreto 760/2021 (`BOE-A-2021-14318`) | Real Decreto 808/2026 (`BOE-A-2026-20911`) | Amendment | 270 SE MODIFICA |
| 9 | Real Decreto 1205/2011, seguridad de los juguetes (`BOE-A-2011-14252`) | Orden PJC/903/2026 (`BOE-A-2026-18261`) | Amendment | 270 SE MODIFICA "el anexo II" |
| 10 | Ley 39/2006, dependencia (`BOE-A-2006-21990`) | Ley 4/2026 (`BOE-A-2026-20528`) | Amendment | 270 SE MODIFICA |

All ten affected rules had consolidation status "Finalizado". For five of them (rows 4, 6, 7, 8
and 9) the record's last update (`fecha_actualizacion`) falls on the morning the amending rule was
published, at 08:25 to 10:35 UTC, which shows the reference was in place on the day of
publication. The FAQ says a new consolidated text takes one to three days, so the reference can
arrive before the consolidated text does.

## Deviations from the method

- **Link to the official text.** The threshold asks that every item has a link. Every item's
  `url_pdf` was checked for presence and form; only one per day (60) was actually requested.
  Requesting all 11,718 at one request per second would take more than three hours of load on
  the BOE for no change to the verdict.
- **One relation replaced before the run.** A regional relation (a Comunidad de Madrid law
  amending a regional legislative decree) was dropped while the list was being built, because
  the amended rule has no ELI permalink on boe.es (the request answered 404), so its identifier
  could not be resolved independently. It was replaced before the list was committed, and both
  facts are recorded in [spikes/s1/README.md](../../spikes/s1/README.md).
- **Independence of the relations.** Each relation comes from the amending rule's own text. The
  ELI pages used to resolve the affected rules' identifiers also show BOE's analysis of those
  rules; only the identifier in the page title was used.
- **Recency.** Relations were taken only from rules published by 8 October, twelve days before
  the run, because of the one-to-three-day consolidation delay. The spike therefore says nothing
  about how soon after publication a relation appears, beyond the five same-day cases above.

## What the design must know

### Formats and behaviour

- **The `Accept` header is mandatory.** Without it both endpoints tested, the daily summary and
  a text block, answer 400 "No reconocido el formato de la cabecera Accept". A text block
  (`/texto/bloque/{id}`) asked for JSON answers 400 "No soportado ningún mime type de la
  cabecera Accept"; the documentation lists XML as the only format for text blocks, the full
  text and the whole rule, and XML or JSON for summaries, metadata, analysis and the text
  index.
- **Prefer XML.** In JSON, a node with one child is an object and a node with several is an
  array (seen for `departamento` and `item` on 19 October), so every consumer has to normalise
  both shapes. The XML has one shape.
- **A day without a bulletin is a 404**, the same answer as a day not yet published (tomorrow
  returned 404 too). A malformed date is a 400. An unknown consolidated identifier is a 404.
  Errors come with a small XML body whose `status/text` says why.
- **Extraordinary issues share the day's summary.** On four days the summary held a second
  issue. Nothing marks it as extraordinary: it has the next issue number and is listed first.
  Each held one or two items, signed the same day they were published: three royal decrees of
  the Presidency of the Government and, on 2 October, the Congress's agreements repealing Real
  Decreto-ley 26/2026 and 27/2026, which it had not validated. Because the summaries were read
  days later, the spike cannot say at what time these issues appeared. A job that reads the
  summary once, early in the morning, may miss them, so it should read the previous day's
  summary again the next morning and compare issue numbers.
- **Issue numbers detect gaps.** They are consecutive within a year, so a missing number means
  a missed issue.
- **Relations carry a code and free text.** Relation types come from a controlled vocabulary
  (`/datosabiertos/api/datos-auxiliares/relaciones-posteriores`: 210 SE DEROGA, 270 SE MODIFICA,
  407 SE AÑADE, 235 SE SUPRIME and about forty more). The free text is written by hand and is not
  reliable to parse: row 4 reads "por Real Decreto 2026/722" for Real Decreto 722/2026. Use
  `id_norma` and the code; show the text to people.
- **Repeals can be dated in the future.** Row 6 has `estatus_derogacion` N and
  `fecha_derogacion` 2027-01-02, so "repealed" has to be computed from the date, not read from
  the flag.
- **Not every rule is consolidated.** The collection covers "the most relevant" rules, mainly
  those with the rank of law, state and regional, plus selected others (FAQ on consolidated
  legislation). A rule outside it answers 404, and its amendments cannot be detected this way.
  Whether regional rules that the BOE does not republish (decrees, for example) are in the
  collection was not tested. Whether every rule in the client's map is in it is for S5 and the
  design to check.
- **Volume for S7.** 195 items per publication day on average (11,718 in 60 days), about 5,100
  a month at 26 publication days a month; 3.2 Section I items a day on average.
- **Response times were not measured.** The script's timings include its own pause between
  requests.

### robots.txt

`/datosabiertos/` is not disallowed, nor are the PDF links (except a few specific dates listed
in robots.txt, none in the window) or the HTML links (`/diario_boe/txt.php?id=...`). The XML
link that the summary gives for each item (`url_xml`, `/diario_boe/xml.php?id=...`) **is
disallowed**. The radar should take an item's full text from the HTML or the PDF, not from
`url_xml`, unless the BOE confirms that this path is open to API reusers.

### Reuse conditions

From the reuse conditions (licence approved by the Agency's resolution of 27 June 2024), which
bind anyone who reuses the data:

- Commercial and non-commercial reuse is allowed, including derived products and value-added
  services.
- The source must be cited with a link to <https://www.boe.es>. For a derived product such as the
  radar, the wording is "Basado en datos de la Agencia Estatal Boletín Oficial del Estado".
- Consolidated legislation must say, in every reused text, that it is a consolidated text of
  merely informative character. Only the signed PDF of the bulletin is official and authentic.
- The date of the last update must be shown when the source document includes one.
- Reuse must not suggest that the BOE takes part in, sponsors or supports it, and must not
  suggest an official character.
- Modifications must be identified as such.
- Items with personal data (appointments, notices) must be reused in line with the GDPR and the
  Ley Orgánica 3/2018.
- The BOE does not guarantee continuity of the service and may deny access to anyone breaking
  the conditions.

# Spike S1: BOE open data

Throwaway code for [spike S1](../../docs/spikes/README.md#s1-boe-open-data). Nothing here is
imported by anything else. The report is
[docs/spikes/s1-boe-open-data.md](../../docs/spikes/s1-boe-open-data.md).

| File | What it is |
| --- | --- |
| `s1.py` | The script (Python 3.14, standard library only); `python3.14 -I s1.py --help` |
| `relations.csv` | The ten amendment or repeal relations, fixed before the consolidated-legislation API was queried |
| `results/` | Small summaries of each run; raw responses stay in `cache/`, which git ignores |

## How the ten relations were chosen

They were chosen and committed before any request to the consolidated-legislation API, so the
git history shows they were fixed in advance.

- **Source of each relation:** the text of a rule published in the BOE during the 60-day window
  (12 August to 20 October 2026), read in its official HTML version
  (`/diario_boe/txt.php?id=...`). Each row names the provision that states the amendment or
  repeal ("Disposición derogatoria única", "Disposición final décima", ...). The analysis
  section of those pages was not used.
- **Identifier of the affected rule:** resolved from the citation in that text (type, number and
  date) through its ELI permalink to the original gazette version (`/eli/es/.../dof/spa/html`),
  not through the consolidated collection.
- **Selection:** rules relevant to education, labour, inclusion and food first, as the spike
  brief asks; at most three relations from one amending rule; only amending rules published by
  8 October 2026, at least twelve days before the run, because the BOE says a consolidated
  version takes one to three days to produce. No rule in the window amends the data protection
  laws, so none of the ten is about data protection.
- **One substitution before the run:** a regional rule (Ley 5/2026 de la Comunidad de Madrid,
  final provision one, which amends Decreto Legislativo 1/2010 of that region) was dropped
  because the amended rule has no ELI permalink on boe.es (the request returned 404): it was
  published only in the regional bulletin, so its identifier could not be resolved
  independently. Row 10 replaced it.

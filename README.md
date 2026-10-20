# regulatory-radar

Tells an organisation which regulations apply to it, reads the official bulletins every
publication day for new rules and for changes to the ones that apply, and sends a weekly notice
with what changed, what to do and by when.

> [!NOTE]
> **Status: discovery.** There is no product code yet. The project runs as a consultancy
> engagement: discovery, feasibility spikes and design are documented and independently audited
> before anything is built. The [project plan](docs/project-plan.md) says where it stands.

## Why

A small regulated organisation (a private school, a clinic, a care home) has no legal
department. The hard part is not reading a regulation once someone hands it over: it is knowing
which regulations apply in the first place, and noticing when one is published, amended or
repealed. A missed obligation costs far more than a few minutes spent dismissing a false alarm.

## What it will do

1. **Applicability map.** From the organisation's profile (what it is, where, what services it
   runs), the regulations that apply, each with the article that makes it apply, what it
   requires and from when. A person reviews the map before it is used.
2. **Daily watch.** Every item the Spanish official bulletin (BOE) publishes is classified as
   *affects*, *may affect* or *does not affect* the profile; amendments and repeals of the rules
   in the map are detected from the consolidated-legislation references. The regional bulletin
   of Madrid (BOCM) is included if the feasibility spike shows it can be read and reused.
3. **Weekly notice.** What is new, what changes, what to do and by when, each item with its
   reasoning and a link to the official publication.

## Design goals

- **Recall first.** Saying "does not apply" about a rule that applies is the error that
  matters. When in doubt, the radar reports.
- **Every claim cites its article.** A classification without the provision behind it is not
  shown.
- **A person decides.** The radar is an aid, not legal advice.
- **Cost is a requirement.** The running cost has a ceiling agreed with the client, measured
  before the design is approved.

## Documentation

| Document | What it answers |
| --- | --- |
| [Project plan](docs/project-plan.md) | Phases, gates, deliverables and where each one lives |
| [Requirements](docs/requirements.md) | What the radar must do and how well, each with how it will be checked |
| [Risk register](docs/risk-register.md) | What could go wrong and what is done about it |
| [Feasibility spikes](docs/spikes/README.md) | The questions to answer before design, with pass thresholds fixed in advance |
| [Architecture decisions](docs/adr/README.md) | Each significant decision, with the options that were discarded |

## License

[MIT](LICENSE).

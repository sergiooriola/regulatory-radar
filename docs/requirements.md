# Requirements

- **Phase:** 1, discovery
- **Last updated:** 2026-10-20

## Purpose and scope

This document states what the radar must do, how well, and how each requirement will be
checked. It is derived from the proposal the client accepted (version 1.0, on 2026-10-20, kept
in the client's private repository), the [project plan](project-plan.md), the
[risk register](risk-register.md), the [feasibility spikes](spikes/README.md) and
[ADR 0002][ADR 0002].

The proposal is the agreed scope. A requirement the proposal does not support is not here, and
a point the proposal leaves open is listed under [open questions](#open-questions) instead of
being answered.

The radar has four parts, which the requirements below follow:

1. **Applicability map.** From a school's profile, the rules that apply to it, each with the
   provision that makes it apply, what it requires and from when.
2. **Map review page.** A private web page on which the client sponsor reviews the map row by
   row.
3. **Daily watch.** Every publication day, every item in the official bulletin is classified
   against the profile, and changes to the rules in the map are detected.
4. **Weekly notice.** An email with what is new, what changes, what to do and by when.

### Out of scope

From the proposal:

- **Legal advice.** The radar flags and reasons; the decision, and the responsibility for it,
  belong to the person who reads it.
- **Instructions the regional education authority sends directly to schools** without
  publishing them in a bulletin. The radar cannot see them, and every notice says so (risk
  [R05]).
- **Interpretation of the collective agreement and other labour matters.** The radar reports
  that a change has been published; reading it is for the client's labour adviser.
- **In the first version:** municipal bulletins, the Official Journal of the European Union, the
  law of the foreign country whose education system the client follows, and the requirements of
  the client's accreditation body.
- **Carrying out the obligations detected.** The radar notifies; the client acts.
- **The regional bulletin (BOCM)**, unless spike [S2] shows it can be read and reused (risk
  [R04]).

From the project plan:

- **Use by organisations other than the client.** Whether the radar becomes a product for
  others is decided in phase 7. The radar still takes the profile as input (FR-1), as
  [ADR 0002] requires.
- **Learning-scope tools.** The plan's technology map lists candidate tools; none of them is a
  requirement. A tool that ends up in the product must meet the non-functional requirements
  here.

### Constraints

These are fixed by the proposal or the plan and bound every design choice.

| ID | Constraint | Source |
| --- | --- | --- |
| C-1 | The radar runs in a cloud account owned and paid for by the client and administered by the owner, so that the service and its data belong to the client. | Proposal, running cost |
| C-2 | Development has no cost to the client. The client pays only the running cost: cloud services and the AI model. | Proposal, running cost |
| C-3 | The feasibility and design experiments of phases 2 and 3 cost less than 25 USD in total. | Proposal, running cost |
| C-4 | No product code is written before the gate. | Plan, principles |
| C-5 | The client's time is asked for at three moments only: accepting the proposal, reviewing the map once, and signing acceptance. Any question about a notice is prepared so that a yes or a no answers it. | Proposal, how the work runs |
| C-6 | A change of scope is proposed in writing, by email, with its effect on schedule and cost, and is not applied without the client's approval. | Proposal, changes and approval |

## Users and their goals

| User | Who | Goals | How they use the radar |
| --- | --- | --- | --- |
| Client sponsor | The head of the client, who accepted the proposal | Know which rules apply to the school and why; learn in time about rules that are published, changed or repealed; know what to do and by when; decide with the reasoning and the sources in front of them; spend as little time as possible | Reads the weekly notice; reviews the map once on the review page; signs acceptance at the end of the pilot |
| Owner | The engineer who builds and runs the radar | Meet the quality bar (recall first, every citation verified); stay under the cost ceiling; run the radar with little effort; publish the work without any client data | Reviews the map before the sponsor sees it; receives the weekly notice; receives operational and cost alerts |

The client's labour adviser is not a user: the client passes on to them the labour items that a
notice refers to them (FR-27).

## Conventions

- **Quality practice:** each requirement is written and checked against the NASA Systems
  Engineering Handbook, Appendix C, "How to Write a Good Requirement — Checklist"
  ([NASA SEH App. C]), using "must" where the checklist uses "shall".
- **The standard behind it:** ISO/IEC/IEEE 29148-2018 "defines the construct of a good
  requirement, provides attributes and characteristics of requirements" and is active, with a
  revision authorised ([IEEE 29148]). Its text is not freely available and was not read, so this
  document does not claim to conform to it.
- **Identifiers** are never reused. A requirement that is dropped keeps its row, marked as
  withdrawn, with the reason.
- **Verification methods:**
  - **Spike:** the threshold of a feasibility spike, fixed in [spikes](spikes/README.md) before
    it runs.
  - **Eval:** an automated run against a labelled set, repeated before each release.
  - **Test:** an automated test of the built radar.
  - **Review:** an inspection of a document, configuration or output, by the owner or by the
    independent reviewer at the gate.
  - **Pilot:** an observation during the four weeks of real notices in phase 5.
- **Sources** of each requirement are the proposal (by section), the plan, the README, an ADR or
  a risk. Facts about external services are cited with their URL and the date read under
  [sources](#sources).

## Profile data model

A school's profile is the input that decides which rules apply. The attributes below are the
ones the proposal asks a school about; the client's values are kept in its private repository
and never here ([ADR 0002]).

| Attribute | What it records |
| --- | --- |
| Type of centre | Ownership and funding (public, publicly funded private, or private) and education system (the Spanish one, or a named foreign one) |
| Holder | The legal form of the entity that holds the school's authorisation |
| Location | Autonomous community, municipality and the education authority's territorial area |
| Education levels | The levels authorised for the current school year and, for a foreign system, their Spanish equivalents |
| Children under three | Whether children under three attend, in any programme or service |
| Pupils | Approximate number, with its date |
| Staff | Number of workers, with its date |
| Canteen | None, own kitchen, or a catering company |
| Transport | None, own routes, contracted routes, or both |
| Out-of-school activities | Extracurricular activities, holiday camps, and trips with nights away from home |
| Health facilities | Swimming pool, infirmary, health staff |
| Video surveillance | Whether there are surveillance cameras |
| Data protection officer | Whether one has been appointed |
| Pupils in a foreign-system school | Whether Spanish pupils take Spanish Language and Culture, and whether pupils seek recognition of the foreign qualification |
| Accreditations | The bodies that accredit the school (their requirements are out of scope) |

The weekly notice's recipients and the cost ceiling are configuration, not profile: they do
not decide applicability.

## Open questions

Points the proposal leaves open, for the design phase. Each names who decides. None of them is
answered here.

## Sources

External sources, each read on 2026-10-20. Where an official source could not be read, that is
stated.

| Source | Used for | Notes |
| --- | --- | --- |
| [BOE, legal notice, reuse conditions][BOE reuse] | NFR on reuse and attribution | Conditions approved by resolution of the BOE agency of 27 June 2024, as the page states |
| [NASA Systems Engineering Handbook, Appendix C][NASA SEH App. C] | Quality practice | Page last updated 26 July 2023 |
| [IEEE SA, ISO/IEC/IEEE 29148-2018][IEEE 29148] | Status of the standard | The ISO pages for the standard (72089 and 94091) returned HTTP 403 to automated reading and were not read |

<!-- Link references -->

[ADR 0002]: adr/0002-keep-client-data-in-a-private-repository.md
[BOE reuse]: https://www.boe.es/informacion/aviso_legal/index.php#reutilizacion
[IEEE 29148]: https://standards.ieee.org/ieee/29148/6937/
[NASA SEH App. C]: https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/
[R04]: risk-register.md
[R05]: risk-register.md
[S2]: spikes/README.md#s2-bocm-access-and-reuse

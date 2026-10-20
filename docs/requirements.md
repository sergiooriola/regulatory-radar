# Requirements

- **Phase:** 1, discovery
- **Last updated:** 2026-10-20

## Purpose and scope

This document states what the radar must do, how well, and how each requirement will be
checked. It is derived from the proposal the client accepted (version 1.0, on 2026-10-20, kept
in the client's private repository), the [project plan](project-plan.md), the
[risk register](risk-register.md), the [feasibility spikes](spikes/README.md) and
[ADR 0002].

The proposal is the agreed scope. A requirement the proposal does not support is not here, and
a point the proposal leaves open is listed under [open questions](#open-questions) instead of
being answered.

The radar has four parts, which the requirements below follow:

1. **Applicability map.** From a school's profile, the rules that apply to it, each with the
   provision that makes it apply, what it requires and from when.
2. **Map review page.** A private web page on which the client sponsor reviews the map row by
   row.
3. **Daily watch.** Every publication day, every item in the official bulletins watched (the
   BOE and, under FR-16, the BOCM) is classified against the profile, and changes to the rules
   in the map are detected.
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
- **The regional bulletin (BOCM), if** the owner's spot check of one summary PDF, the last open
  part of spike [S2], finds a difference from the program's extraction. S2 otherwise passed on
  2026-10-20, so the BOCM is in the first version (FR-16); if the spot check fails, it is left
  out and every notice says so (FR-29, risk [R04]).

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
  withdrawn, with the reason. A requirement added later takes the next free number and goes in
  the section it belongs to, so numbers within a section are not always in order.
- **Verification methods:**
  - **Spike:** the threshold of a feasibility spike, fixed in [spikes](spikes/README.md) before
    it runs.
  - **Eval:** an automated run against a labelled set, repeated before each release.
  - **Test:** an automated test of the built radar.
  - **Review:** an inspection of a document, configuration or output, by the owner or by the
    independent reviewer at the gate.
  - **Pilot:** an observation during the four weeks of real notices in phase 5.
- **Sources** of each requirement are the proposal (by section), the plan, the README, an ADR or
  a risk. "Quality baseline" marks a quality the owner requires of the agreed scope where the
  proposal does not state it, such as multi-factor authentication; it adds no capability. Facts
  about external services are cited with their URL and the date read under [sources](#sources).

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

## Functional requirements

### Profile

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| FR-1 | The radar must take a school's profile as structured input that follows the profile data model, with no profile value written into the code. | Test: the radar runs end to end on a synthetic profile whose values differ from the client's. The client-identifier check passes on every change. | [ADR 0002] |
| FR-2 | Each profile value must record its source, the date it was obtained and whether the client confirmed it. | Review: the profile used at the gate is checked attribute by attribute. | Proposal, annex A |

### Applicability map

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| FR-3 | From the profile, the radar must produce a map of the rules that apply to the school. | Spike: [S5] threshold. From the gate on, evals use the client's reviewed map as the reference (NFR-4). | Proposal, scope; [R01], [R12] |
| FR-4 | Each map row must state the rule, the provision that makes it apply, what the rule requires and the date from which it applies. | Test: every row validates against the map schema. Review: the map at the gate. | Proposal, the problem and the proposal |
| FR-5 | Each map row must give the reasoning behind it, naming the profile attributes it depends on, and a link to the rule's official publication. | Test: every row validates against the map schema. Review: the map at the gate. | Proposal, the problem and the proposal; README, design goals |
| FR-6 | Where it is uncertain whether a rule applies to the school, its row must say so and give the reasoning and the provisions it rests on, leaving the decision to the client sponsor. | Review: every uncertain row in the [S5] output and in the map for review has its reasoning and at least one verified provision. | Proposal, the problem and the proposal |
| FR-7 | The radar must not show the map to the client sponsor until the owner has approved it. | Test: before the owner's approval, the review page shows no map to the client sponsor's account. | Proposal, scope |

### Map review page

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| FR-8 | The radar must provide a private web page on which the client sponsor reviews the map row by row. | Review: demonstrated to the owner before the gate. Access is covered by NFR-15. | Proposal, scope |
| FR-9 | For each row, the review page must let the client sponsor either confirm it or correct it with a comment. | Test: a confirmation and a correction are each recorded for a test row. | Proposal, how the work runs; [R08] |
| FR-10 | The review page must record each row's decision with its date. | Test: after a decision, the stored record has the row, the decision, any comment and the date. | Proposal, changes and approval |
| FR-11 | Each row on the review page must show everything FR-4 and FR-5 require, so that it can be confirmed or corrected without opening another document. | Review: the owner does a dry run of the whole review before the gate. | Proposal, how the work runs; [R08] |

### Daily watch

The spikes found these sources; the design chooses which one it reads for each step, within the
requirements on [access to the sources](#access-to-the-sources).

- **BOE** ([S1 report]): the open-data daily summary
  (`/datosabiertos/api/boe/sumario/{yyyymmdd}`) lists every item of every issue of the day,
  extraordinary issues included, with links to the signed PDF, the only official and authentic
  format, and to the HTML. The consolidated-legislation API gives each consolidated rule's later
  amendments and repeals.
- **BOCM** ([S2 report]): there is no API, bulk download or open-data dataset. `/sumarios.rss`
  lists the last 20 bulletins with every item's identifier (CVE); a bulletin's HTML summary gives
  every item's number, section, department, sub-body, title and PDF link in one request; the XML
  of each item adds its rank, dates, pages and full text.

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| FR-12 | On each BOE publication day, the radar must retrieve every item that day's BOE publishes, in all its sections. | Spike: [S1] threshold. Test: each day, the number of items retrieved equals the number in the day's summary. | Proposal, scope |
| FR-13 | The radar must classify every retrieved item as *affects*, *may affect* or *does not affect* the profile. | Spike: [S3] and [S4] thresholds. Eval: NFR-1 and NFR-2. | Proposal, the problem and the proposal |
| FR-14 | Each item classified as *affects* or *may affect* must carry the reasoning and the provision on which its classification rests. | Test: every such item validates against the classification schema. Spike: [S4] threshold. | Proposal, the problem and the proposal; [R01] |
| FR-15 | The radar must detect every change to, and every repeal of, a rule in the map that the BOE publishes. | Spike: [S1] threshold for relations. Pilot: NFR-5. | Proposal, the problem and the proposal; README |
| FR-16 | The radar must apply FR-12 to FR-15 to the BOCM as well, unless the owner's spot check of one summary PDF, which completes spike [S2], finds a difference; then FR-29 applies instead. | Spike: [S2] threshold, met on the engineer's checks on 2026-10-20 (20 of 20 days, 1,439 items, 3 of 3 hand checks, reuse allowed with conditions); the owner's spot check is pending. Test: as for FR-12, the items retrieved each day equal those in the day's BOCM HTML summary. | Proposal, scope; [S2 report]; [R04] |
| FR-17 | If an item or a publication day cannot be retrieved or classified, the radar must report it in the next weekly notice instead of skipping it. | Test: with a simulated failure of the source, the next notice lists the unprocessed day or item. | Proposal, the problem and the proposal; [R01] |
| FR-30 | Each run must read again the BOE summary of the previous publication day and retrieve every issue and item added to it since the radar last read it. An extraordinary issue shares the day's summary and nothing marks it as extraordinary. | Test: when the second read of a day's summary holds an issue the first did not, that issue's items are retrieved, classified and listed in the next notice under FR-23. | [S1 report]: four extraordinary issues in 60 days, one with the Congress's repeal of two royal decree-laws; [R17] |
| FR-31 | The radar must check that the issue numbers it has retrieved for each watched bulletin are consecutive within the year, and must treat a missing number as a missed issue, to be retrieved or else reported under FR-17. | Test: with one issue left out of the retrieved data, the gap is found and the issue is retrieved or listed in the next notice. | [S1 report] (BOE issue numbers are consecutive within a year); [S2 report] (the BOCM bulletin number is sequential within the year); [R17], [R22] |
| FR-32 | Before it classifies a bulletin's items for a publication day, the radar must check that bulletin's extraction: every source it reads for the bulletin lists the same items; where the bulletin numbers its items, as the BOCM does, the numbers run from 1 to N with no gap; and every item has an identifier, a title, a section, a department or other issuer, and a link to the official text. | Test: each of these faults, injected, fails the check: an item missing from one source, a gap in the numbering, and an item without one of the fields. Spike: [S2] ran the same check on 20 days. | [S1 report], [S2 report] (two unannounced BOCM format changes in 20 days); [R20] |
| FR-33 | If the check of FR-32 fails, the radar must not classify that bulletin's items for that day, and must report the failure in the next notice, naming the bulletin, the day and what failed, as an unprocessed day under FR-17. | Test: with a fault of FR-32 injected, no item of that bulletin and day is classified, and the next notice names the bulletin, the day and the failed check. | [S2 report]; [R20], [R01] |

### Citation check

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| FR-18 | Before a cited provision is shown in the map, on the review page or in a notice, the radar must check that the provision exists in the BOE consolidated text or, for a rule not yet consolidated, in its official publication. | Spike: zero invented citations in [S4] and [S5]. Test: a citation of a provision that does not exist is caught. | [R06] |
| FR-19 | Where the radar quotes a provision, it must check that the quotation matches the text it was checked against. | Test: an altered quotation is caught. | [R06] |
| FR-20 | A citation that fails FR-18 or FR-19 must not be shown. | Test: the failed citation in the tests of FR-18 and FR-19 does not appear in any output. | [R06]; README, design goals |
| FR-21 | An item or map row must not be dropped because one of its citations failed the check. | Test: the item in the tests of FR-18 and FR-19 still reaches the owner. How it is shown is an [open question](#open-questions). | [R01] |

### Weekly notice

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| FR-22 | The radar must send a notice by email once a week to the recipients the client designates and to the owner. | Pilot: four notices in four weeks, each received by every recipient. | Proposal, the problem and the proposal |
| FR-23 | The notice must list every item classified as *affects* or *may affect*, and every change or repeal of a rule in the map, that no earlier notice has listed. | Test: the items classified in the period match the items in the notice, one for one. | Proposal, the problem and the proposal |
| FR-24 | For each item, the notice must state its classification, what is new or what changes, what the client has to do and by when, the reasoning, the provision it rests on and a link to the official publication. | Test: every notice item validates against the notice schema. Pilot: the owner reviews each notice. | Proposal, the problem and the proposal |
| FR-25 | When a week has nothing to report, the radar must still send the notice, saying so. | Test: a week with no items produces a notice that says there is nothing new. | Proposal, the problem and the proposal |
| FR-26 | Every notice must state that it is an aid, not legal advice, and that a person decides. | Test: the statement is present in every notice. | Proposal, the problem and the proposal; [R10] |
| FR-27 | For an item about the collective agreement or another labour matter, the notice must report its publication and refer its interpretation to the client's labour adviser, without interpreting it. | Review: the [S4] output and the pilot notices for every such item. | Proposal, out of scope; [R10] |
| FR-28 | Every notice must state that instructions sent directly to schools by the regional education authority, without being published in a bulletin, are not covered. | Test: the statement is present in every notice. | Proposal, out of scope; [R05] |
| FR-29 | While the BOCM is not watched, every notice must say so. This is R04's fallback: it applies from the start if the owner's spot check that completes [S2] finds a difference, and at any later time the BOCM is not watched. | Test: with the BOCM disabled, the statement is present in every notice. | Proposal, risks; [S2 report]; [R04] |

## Non-functional requirements

### Accuracy and recall

Saying "does not affect" about a rule that affects the school is the error that matters; a false
alarm costs a few minutes. The thresholds are those fixed in [spikes](spikes/README.md) before
any spike runs, restated here so that they keep holding after the spikes: the evals repeat
them before each release (NFR-34).

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-1 | The classification of items must flag 100 % of the items labelled *affects* and at least 95 % of those labelled *may affect*, while passing no more than 10 % of all items on to deep analysis. | Spike: [S3] threshold. Eval: the same thresholds on the [S3] labelled set. | Proposal, the problem and the proposal; [R01] |
| NFR-2 | The deep analysis must classify no item labelled *affects* as *does not affect*, and must agree with the owner's label on at least 90 % of items. | Spike: [S4] threshold. Eval: the same thresholds on the [S4] labelled set. | [R01] |
| NFR-3 | The map and the notices must contain zero invented citations. | Spike: [S4] and [S5] thresholds. Test: FR-18 and FR-19. | [R06] |
| NFR-4 | The map produced from a profile must contain at least 90 % of the rules in the reference list. | Spike: [S5] threshold. Eval: from the gate on, the client's reviewed map replaces the reference list. | Proposal, risks; [R01], [R12] |
| NFR-5 | The radar must miss no change to, or repeal of, a rule in the map. | Spike: [S1] threshold for relations. Pilot: at its end, the owner checks the consolidated text of every rule in the map for changes published during the pilot, and finds each one in a notice. | Proposal, the problem and the proposal |

### Completeness and recovery

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-6 | Every item of every publication day must be classified before the notice that covers that day is sent. | Test: a daily reconciliation of items retrieved, classified and in the day's summary. Pilot: every publication day reconciles. | Proposal, scope; [R01] |
| NFR-7 | The radar must not cap the number of items it classifies in a day. | Test: the radar classifies every item of the largest publication day observed in [S1]. | Proposal, scope |
| NFR-8 | After a run that fails or does not start, a later run must process the publication days it missed. | Test: with one scheduled run suppressed, the next run processes both days. | [R01] |
| NFR-38 | While the BOCM is watched, the radar must retrieve every BOCM bulletin published while it was not running, even when it stopped for longer than the 20 bulletins the BOCM feed lists, a little over three weeks. | Test: after a simulated outage of more than 20 BOCM bulletins, the following runs retrieve every bulletin of the outage and FR-31 finds no gap. [S2] did not test a way to catch up. | [S2 report]; [R22]; NFR-8 |
| NFR-39 | The retrieval of each publication day from every watched bulletin must complete within the run or runs the design provides, with no item left out and no request sooner than the source's crawl delay allows. At the BOCM's 10-second crawl delay, the summary plus every item's XML takes about 12 minutes for an average day of [S2] (72 items) and 21 minutes for its largest (121); the design chooses how to fit it, for example by triaging from the summary and fetching only the candidates' XML, or by spreading the fetch over several runs. | Review: the design shows how the largest BOCM day observed fits within the time limit of the compute it runs on (900 seconds for a standard AWS Lambda function, [S2 report]). Test: a simulated BOCM day of 121 items, served with a 10-second crawl delay, is retrieved in full. | [S2 report]; [R04], [R22]; NFR-7 |

### Cost

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-9 | The running cost billed to the client's account for the radar must not exceed 15 USD in any calendar month. | Spike: [S7] projects a monthly cost at or below the ceiling. Pilot: each month's bill is at or below it. | Proposal, running cost; plan, status log; [R07] |
| NFR-10 | The owner must receive an alert when the month's cost reaches 50 %, 80 % and 100 % of the ceiling. | Review: the alert configuration. Test: a test alert reaches the owner. | Proposal, running cost; [R07] |
| NFR-11 | No component may bill by the hour while the radar is idle, unless an ADR justifies it. | Review: the itemised cost estimate in the design phase has no hourly idle charge without an ADR. | Plan, principles; [R15] |
| NFR-12 | Before the monthly cost exceeds the ceiling, the owner must send the client a written proposal. | Review: the operations runbook contains the procedure. | Proposal, running cost; [R07] |

### EU data residency

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-13 | All data the radar stores, including logs and traces, must be stored in the European Union. | Review: the region of every service in the design, the observability service included; a service that cannot guarantee it is not used. | Proposal, data and confidentiality |
| NFR-14 | All processing, including the AI model's inference, must take place in the European Union. | Spike: [S6] threshold (both models invoked through the EU inference profile). Review: as for NFR-13. | Proposal, data and confidentiality; [R03] |

### Security

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-15 | The review page must be reachable only by authenticated users whom the owner has authorised. | Test: requests without authentication, or from an unauthorised user, are refused. | Proposal, scope and data and confidentiality |
| NFR-16 | Every human access to the client's cloud account must require multi-factor authentication. | Review: the account's users and their settings. | Quality baseline; C-1 |
| NFR-17 | Credentials and keys must not be stored in the repository or in the code. | Test: a secret scan of the repository history finds none. | Quality baseline; [ADR 0002] |
| NFR-18 | Each component's permissions must grant only the actions and resources it uses; no permission may use a wildcard unless an ADR justifies it. | Review: the permission policies in the infrastructure code. | Quality baseline |
| NFR-19 | Bulletin text must be passed to the model as data, never as instructions. | Test: an item whose text contains instructions to the model is classified as if they were not there. | [R14] |
| NFR-20 | Every model output must be validated against a schema; an output that fails must not be used and must be recorded. | Test: a malformed output is rejected and appears in the run record. | [R14] |
| NFR-21 | Data must be encrypted in transit. | Review: every connection in the infrastructure code uses TLS. | Quality baseline; proposal, data and confidentiality |
| NFR-22 | Data must be encrypted at rest. | Review: every store in the infrastructure code has encryption enabled. | Quality baseline; proposal, data and confidentiality |

### Data protection

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-23 | The radar must not process personal data of pupils, families or staff. Its inputs are official publications, the school's profile and the email addresses of the notice's recipients. | Review: the data protection note in the design phase lists every data item and its source. | Proposal, data and confidentiality |
| NFR-24 | The client's profile, map and documents must be kept only in private storage, and never in the public repository. | Test: the client-identifier check passes on every change. Review: the storage of each item in the design. | Proposal, data and confidentiality; [ADR 0002] |

### Access to the sources

Both bulletins are public services that may restrict or deny automated access: the BOE's reuse
conditions say access may be denied to anyone breaking them, and the BOCM honours requests to
de-index items by disallowing them one by one in its robots.txt, about 1,800 on 2026-10-20
([S1 report], [S2 report]; risks [R19], [R21]).

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-40 | In each run, before its first request to a host, the radar must read that host's robots.txt, and it must not request any URL that robots.txt disallows to the radar, honouring the `*` and `$` patterns in its rules. What happens to stored copies of items that a robots.txt later disallows is decided under OQ-15. | Test: with a robots.txt that disallows one item through a `*` or `$` pattern, a run reads robots.txt before any other request to that host and makes no request to that item. Review: the request log of a pilot day has no request to a disallowed path, such as the BOE's `/diario_boe/xml.php` or the BOCM's `/boletin/CM_Boletin_BOCM/`. | [S1 report], [S2 report]; [R19], [R21] |
| NFR-41 | Between two requests to the same host, the radar must wait at least the `Crawl-delay` that host's robots.txt sets, and at least 1 second where it sets none. The BOCM's was 10 seconds on 2026-10-20. | Test: with a robots.txt that sets a crawl delay, the request log shows no two requests to that host closer together than the delay. Pilot: the same on every run's request log. | [S2 report]; [R19], [R21]; quality baseline |
| NFR-42 | Every request to a bulletin's site must carry a User-Agent that names the radar and gives a URL at which its operator can be reached. | Test: every request in a run's request log carries it. | [R19] |
| NFR-43 | Every request to the BOE open-data APIs must carry an `Accept` header that asks for XML. Without the header both endpoints [S1] tried answer 400; text blocks, the full text and the whole rule are offered only in XML; and in JSON a node with one child is an object but with several an array, so XML is the one format with a single shape on every endpoint. | Test: every request to `/datosabiertos/api/` in a run's request log carries `Accept: application/xml`. | [S1 report], formats and behaviour; [R20] |

### Reuse and attribution

The BOE's reuse conditions bind anyone who reuses its documents ([BOE reuse], second
condition). The notice and the review page adapt and summarise them, which the conditions call
a derived work or value-added service.

The BOCM publishes no licence or reuse conditions of its own. [S2] read the general law (the
copyright act, Ley 37/2007 on the reuse of public-sector information and the Comunidad de
Madrid's Ley 10/2019) as allowing the radar's automated reuse, on conditions: follow robots.txt,
cite the BOCM and link to the official text, do not alter the content, and treat personal data
under data protection law ([S2 report], reuse terms). That reading is the engineer's, not a
lawyer's; asking the BOCM to confirm it in writing is for the owner to decide ([R04]).

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-25 | Every notice, and the review page, must cite the source as "Basado en datos de la Agencia Estatal Boletín Oficial del Estado", with a link to <https://www.boe.es>. | Test: the citation and the link are present in every notice and on the page. | [BOE reuse], fourth condition; [R11] |
| NFR-26 | Wherever a consolidated text is reused, the radar must state that it is a consolidated text for information only ("texto consolidado de carácter meramente informativo"). | Test: the statement accompanies every reused consolidated text. | [BOE reuse], fourth condition; [R11] |
| NFR-27 | Wherever a BOE document is reused, the radar must state the date of its last update when the original document gives one. | Test: the date is shown for a document that has one. | [BOE reuse], fourth condition; [R11] |
| NFR-28 | The radar must not suggest that what it shows is official, or that the BOE agency takes part in, sponsors or supports it. | Review: the wording of the notice and of the page. | [BOE reuse], fourth condition |
| NFR-29 | Every summary, extract or other adaptation of a BOE document must be identified as such, distinct from the original text. | Review: the notice and the page against the conditions. | [BOE reuse], fourth condition |
| NFR-30 | Wherever the radar reuses a BOCM item, it must cite the BOCM as the source with the bulletin's number and date, link to the item's official PDF, and identify any summary or other adaptation as such, distinct from the original text. | Spike: [S2] threshold (the terms allow automated reuse). Test: every BOCM item in a notice and on the review page has the citation, the number, the date and the link. Review: the notice and the page against the conditions in the [S2 report]. | [S2 report], reuse terms; [R04] |

### Maintainability

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-31 | All cloud infrastructure must be created from code in the repository, apart from documented bootstrap steps. | Review: a drift check finds no difference between the code and the account. | [R13] |
| NFR-32 | An operations runbook must let another engineer run, recover and change the radar. | Review: the independent reviewer follows the runbook for one recovery. | Plan, deliverables; [R13] |
| NFR-33 | Each significant design decision must be recorded as an ADR in MADR format, with the options discarded. | Review: at the gate, each technology in the design has an ADR. | Plan, principles; [ADR 0001] |
| NFR-34 | A change to the model, the prompts or the classification logic must pass the evals of NFR-1 to NFR-4 before it is released. | Review: the release record of each such change shows the eval results. | [R01], [R06] |

### Observability

| ID | Requirement | Acceptance criterion | Source and links |
| --- | --- | --- | --- |
| NFR-35 | Each run must record the publication days it processed, the items retrieved from each bulletin, the items in each class, the tokens and the estimated cost for each model, its duration and its errors. | Test: a run's record has every field. | [R07], [R13] |
| NFR-36 | The owner must receive an alert when a scheduled run fails or does not start, or when a notice is not sent. | Test: each of the three faults, injected, produces an alert. | [R01], [R13] |
| NFR-37 | Each classification must be kept with its reasoning and citations, so that any item, in a notice or not, can be explained afterwards. | Test: the record of a classified item returns its class, reasoning and citations. | [R01]; README, design goals |

## Open questions

Points the proposal leaves open, for the design phase. Each names who decides. None of them is
answered here. Where an answer would add to the client's workload or to the cost, it is a
change of scope and follows C-6.

| ID | Question | Affects | Decides |
| --- | --- | --- | --- |
| OQ-1 | On which day and at what time is the weekly notice sent, and which publication days does each notice cover? | FR-22, FR-23 | Owner, confirmed with the client |
| OQ-2 | By what time must a publication day's run finish? The proposal sets none. | NFR-6, NFR-36, NFR-39 | Owner |
| OQ-3 | In which language are the notice and the review page written? The proposal does not say. | FR-8, FR-24 | Owner, confirmed with the client |
| OQ-4 | Does the owner approve each notice before it is sent? The plan's technology map mentions a pause for human approval; the proposal says only that the notice goes to the client and the owner. | FR-22 | Owner |
| OQ-5 | How does a new rule, change or repeal that a person confirms enter the map, and does a changed map go back to the client sponsor, whose review the proposal limits to once (C-5)? | FR-3, FR-7, FR-15 | Owner; the client if it asks for more of its time |
| OQ-6 | How is the profile kept current, for example a staff count near a legal threshold, and does a change to the profile produce a new map? | FR-1, FR-3 | Owner, with the client |
| OQ-7 | Should the map list rules that do not apply only because of a threshold in the profile, so that a change to the threshold is watched? FR-15 watches only rules in the map. | FR-3, FR-15 | Owner |
| OQ-8 | Should the notice remind the client of approaching dates in rules already in the map, such as a provision that applies from a later date? | FR-23, FR-24 | Owner; the client if it is a change of scope |
| OQ-9 | Should the notice order or mark its items by priority? | FR-24 | Owner |
| OQ-10 | How is an item or row whose citation failed the check shown: to the owner only, or in the notice with a warning? | FR-21 | Owner |
| OQ-11 | How long are classifications and run records kept? | NFR-35, NFR-37 | Owner, in the data protection note |
| OQ-12 | Who may change the notice's recipients, and how? | FR-22 | Owner, with the client |
| OQ-13 | Is the 15 USD ceiling before or after any taxes on the bill, and which costs count against it, for example evals run after the gate? | NFR-9 | Owner, confirmed with the client |
| OQ-14 | Which account pays for evals and other development runs after the gate, given that development has no cost to the client (C-2)? | NFR-9, NFR-34 | Owner |
| OQ-15 | Bulletin items may contain personal data; the BOE's conditions require its reuse to respect the GDPR and the Spanish data protection act ([BOE reuse], fourth condition). S2 found the same in BOCM items, where many titles name people. How is personal data inside bulletin items handled, and the login data of the review page? What happens to stored copies of items that a bulletin's robots.txt later disallows, as the BOCM does for de-indexed items ([R21])? | NFR-15, NFR-23, NFR-40 | Owner, in the data protection note |
| OQ-16 | Can the observability service in the plan's technology map keep its data in the EU on its free plan? The plan lists this as to be confirmed. | NFR-13 | Owner, in an ADR |
| OQ-17 | Which acceptance tests, drawn from these requirements, does the client sign at the end of the pilot? | All | Owner, in the test plan |

## Sources

External sources, each read on 2026-10-20. Where an official source could not be read, that is
stated.

Facts about the BOE and the BOCM taken from the spike reports (sources, formats, robots.txt,
crawl delay, reuse terms) are cited through the [S1 report] and the [S2 report], which give the
URL of each source and the date it was read, 2026-10-20. They were not read again for this
document.

| Source | Used for | Notes |
| --- | --- | --- |
| [BOE, legal notice, reuse conditions][BOE reuse] | NFR on reuse and attribution | Conditions approved by resolution of the BOE agency of 27 June 2024, as the page states |
| [NASA Systems Engineering Handbook, Appendix C][NASA SEH App. C] | Quality practice | Page last updated 26 July 2023 |
| [IEEE SA, ISO/IEC/IEEE 29148-2018][IEEE 29148] | Status of the standard | The ISO pages for the standard (72089 and 94091) returned HTTP 403 to automated reading and were not read |

<!-- Link references -->

[ADR 0001]: adr/0001-record-architecture-decisions-with-madr.md
[ADR 0002]: adr/0002-keep-client-data-in-a-private-repository.md
[BOE reuse]: https://www.boe.es/informacion/aviso_legal/index.php#reutilizacion
[IEEE 29148]: https://standards.ieee.org/ieee/29148/6937/
[NASA SEH App. C]: https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/
[R01]: risk-register.md
[R03]: risk-register.md
[R04]: risk-register.md
[R05]: risk-register.md
[R06]: risk-register.md
[R07]: risk-register.md
[R08]: risk-register.md
[R10]: risk-register.md
[R11]: risk-register.md
[R12]: risk-register.md
[R13]: risk-register.md
[R14]: risk-register.md
[R15]: risk-register.md
[R17]: risk-register.md
[R19]: risk-register.md
[R20]: risk-register.md
[R21]: risk-register.md
[R22]: risk-register.md
[S1]: spikes/README.md#s1-boe-open-data
[S1 report]: spikes/s1-boe-open-data.md
[S2]: spikes/README.md#s2-bocm-access-and-reuse
[S2 report]: spikes/s2-bocm-access-and-reuse.md
[S3]: spikes/README.md#s3-triage-recall
[S4]: spikes/README.md#s4-deep-analysis
[S5]: spikes/README.md#s5-map-discovery

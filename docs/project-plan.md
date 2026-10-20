# Project plan

- **Owner:** Sergio Oriola Díaz
- **Phase:** 2, feasibility. Phase 1 closes when the owner sends the client the discovery
  report, version 1.0
- **Last updated:** 2026-10-20

## Problem

The first client is a private school in the Comunidad de Madrid that follows a foreign
education system. Asked what costs most in dealing with regulation, the school answered:
keeping up with rules as they are published or repealed, "and above all, being clear about
which rules apply". Much of the regulation written for Spanish schools does not apply to a
foreign-system school, some of it does, and the boundary is not obvious.

The radar addresses that problem in three parts, described in the [README](../README.md): an
applicability map, a daily watch of the official bulletins and a weekly notice.

## Principles

- **No product code before the gate.** Feasibility spikes produce throwaway code under
  `spikes/`, which is not reused in the product.
- **Thresholds before results.** Every spike states its pass threshold before it runs
  ([spikes](spikes/README.md)).
- **Decisions are recorded with their alternatives** as ADRs in [MADR](adr/README.md) format.
- **Cost is designed, not discovered.** The design is reviewed against the cost pillar of the
  AWS Well-Architected Generative AI Lens (model right-sizing, fewer tokens, prompt caching,
  stop conditions for agents) before the gate.
- **Pay only while it runs.** The radar works for a few minutes per publication day, so no
  component may bill by the hour while idle unless an ADR justifies it. The usual traps are an
  always-on database instance, a NAT gateway, public IPv4 addresses and vector stores with a
  minimum monthly charge.
- **Nothing about the client lives in this repository.** The client's profile, its map, the
  labelled samples and every client document are kept in a separate private repository
  ([ADR 0002](adr/0002-keep-client-data-in-a-private-repository.md)).

## Constraints

The owner builds the radar partly to demonstrate a specific set of tools: Python, Claude on
Amazon Bedrock in an EU region, LangChain and LangGraph, retrieval over the bulletin stream,
PostgreSQL, Terraform, an MCP server and a TypeScript review page. Each of these still gets an
ADR that weighs the alternatives and says when it would not be the right choice. Where a
learning goal conflicts with the client's cost ceiling, the ceiling wins and the goal is met
outside the client's account.

Kubernetes is learning scope, not part of the client's product: a local cluster for
development and CI, and an EKS cluster created with Terraform, demonstrated and destroyed within
hours in a separate sandbox account. A job that runs once a day does not justify a cluster that
runs all day; production uses pay-per-use services.

## Technology map

What each planned technology is for, where it runs and who pays for it. "Planned" means it is a
candidate: each one is confirmed or rejected by an ADR in the design phase, and a technology
that cannot justify itself in the product moves to learning scope. The client's proposal
names none of them, because the client buys outcomes, not tools; the plain-language solution
summary in phase 3 describes the pieces without the jargon.

| Technology | What it does in the radar | Runs in | Cost to the client | Decided in |
| --- | --- | --- | --- | --- |
| Python | Language for everything except the review page | — | None (free software) | Phase 3 |
| Claude Haiku 5.5 and Sonnet 5.5 on Amazon Bedrock | Classify and analyse publications; draft the notice | Client's AWS account, EU processing | The model line of the estimate | S4, then an ADR |
| LangChain (`langchain-aws`) | Standard interface to the model, document loading and splitting, vector-store integration | Inside the daily job | None (free software) | ADR |
| LangGraph | The daily flow as explicit steps, with a pause for human approval | Inside the daily job | None (free software); its saved state needs a database | ADR |
| Embeddings and a vector store | Retrieval: find the rules in the map related to each new publication | Client's AWS account | A few cents a month, inside the AWS line | ADR |
| Database (PostgreSQL on Aurora Serverless v2 with auto-pause, or DynamoDB) | The profile, the map, the history of classifications, LangGraph state | Client's AWS account | 0 to about 3.4 USD a month, inside the AWS line; see R15 | ADR |
| Amazon SQS | Queue of publications waiting for analysis | Client's AWS account | Free up to 1 million requests a month, against roughly 21,000 (send, receive and delete for each of about 7,000 publications: 5,100 from the BOE measured in S1, 1,900 from the BOCM measured in S2) | ADR, which must show a queue is needed at this volume |
| Scheduled compute (Lambda or a container task) | Runs the job each publication day | Client's AWS account | Inside monthly free allowances | ADR |
| Amazon SES | Sends the weekly notice | Client's AWS account | Cents | ADR |
| TypeScript and React | The page where the client reviews the map | Client's AWS account | Inside the AWS line | ADR |
| Terraform | Creates and changes all infrastructure from code | Owner's computer and CI | None to use; its state file costs cents | ADR |
| Docker | Packages the job the same way locally and in AWS | Owner's computer, CI, AWS | None (free software) | ADR |
| LangSmith | Traces of each run: steps, tokens, cost and latency | LangChain's cloud; EU region on the free plan to be confirmed | None on the free plan: 5,000 traces a month, one seat. One trace per daily run is about 26 a month | ADR, together with the data protection note |
| MCP server | Lets the owner ask Claude about the map from a desktop client | Owner's computer | None to the client | ADR |
| Kubernetes (kind or k3d locally, EKS for a demonstration) | Learning scope: not part of the product | Owner's computer; a separate sandbox AWS account paid by the owner | None to the client | ADR explaining why production does not use it |
| GitHub and GitHub Actions | Code hosting, reviews, continuous integration | GitHub | None to the client | — |

The AWS line of the proposal's estimate (0 to 4 USD a month) is a first approximation. The
design phase replaces it with an itemised estimate, one row per service, from the AWS Pricing
Calculator and the measurements of S7.

## Phases

Durations are indicative. The work is part-time with variable hours, so each phase's dates are
set when the previous phase closes.

| Phase | Question it answers | Exit criterion | Indicative duration |
| --- | --- | --- | --- |
| 0. Proposal | Is this worth doing, and on what terms? | The client accepts the proposal | 1 week |
| 1. Discovery | What exactly is the problem, for whom, and what counts as success? | Profile confirmed; success criteria and cost ceiling agreed | 1–2 weeks |
| 2. Feasibility | Can it be built to the bar, within the cost? | Every spike passes its threshold, or a decision is recorded | 2–3 weeks |
| 3. Design | How will it be built, run and paid for? | Design documents complete and self-reviewed | 1–2 weeks |
| Gate | Go or no-go | Independent audit, owner's go and the client's review of the draft map | 1 week |
| 4. Build | — | Acceptance tests pass | 6–10 weeks |
| 5. Pilot | Does it work in real use? | Four weeks of real notices; the client signs acceptance | 4 weeks |
| 6. Production and operation | — | Closure report delivered | Ongoing |
| 7. SaaS decision | Should it become a product for other organisations? | Decision recorded, on evidence from the pilot | Later |

## Deliverables

Client documents are written in Spanish, generated as Word and PDF from Markdown in the private
repository, and sent in the owner's name. Technical documents are written in English and live
here as Markdown, unless they contain client data.

| Phase | For the client (private repository) | Technical (this repository unless noted) |
| --- | --- | --- |
| 0. Proposal | Proposal and scope | Project plan, risk register |
| 1. Discovery | Discovery report | Requirements |
| 2. Feasibility | A short note only if a spike fails and changes the scope | One report per spike; labelled data stays private |
| 3. Design | Solution summary and running-cost budget | Architecture document, ADRs, data protection note, test plan, cost estimate |
| Gate | Regulatory map for review; go-ahead record | Independent audit |
| 4. Build | Short progress note per delivery | Changelog |
| 5. Pilot | Acceptance tests to sign; user guide | Test results |
| 6. Production | Closure report | Operations runbook |

The client's load is kept to three moments: accepting the proposal, reviewing the map once, and
signing acceptance. Everything else is available to read but never required.

## Roles

| Role | Who | Responsibility |
| --- | --- | --- |
| Owner and engineer | Sergio Oriola Díaz | Everything not listed below |
| Client sponsor | The school's CEO | Accepts the proposal, reviews the map, signs acceptance |
| Labour adviser | The school's external adviser | Questions about the collective agreement |
| Independent reviewer | A second AI model (Codex) | Audits the design and the spike reports at the gate |

## Status log

| Date | Event |
| --- | --- |
| 2026-10-19 | Project started. Proposal drafted; spike thresholds proposed. |
| 2026-10-19 | Owner found the first estimate (25–55 USD a month) too high. Re-estimated at 2–8 USD with pay-per-use services and the small model doing most of the work; ceiling 15 USD. Spike thresholds approved. |
| 2026-10-19 | Client answered the profile questions and agreed the 15 USD ceiling, ahead of discovery. Proposal issued as 1.0; written acceptance pending. |
| 2026-10-20 | Client confirmed its profile and accepted proposal 1.0. Phase 0 closed; discovery and S6 start. Repositories published. |
| 2026-10-20 | S1 passed: 60 of 60 days, 11,718 of 11,718 items complete, 10 of 10 relations. Measured volume about 195 items per publication day (about 5,100 a month, below the 6,000 the estimate assumed). Risks R17 to R19 added. |
| 2026-10-20 | S2 passed on the engineer's checks: 20 of 20 BOCM days (1,439 items), 3 of 3 hand checks, reuse allowed with conditions; the owner's spot check of one summary PDF is pending. BOCM's 10 s crawl delay makes a full day take 12 to 21 minutes, which the design must fit. Risks R20 to R22 added. |
| 2026-10-20 | Phase 1 exit: requirements updated with the S1 and S2 findings (FR-30 to FR-34, NFR-38 to NFR-43); every risk reviewed; discovery report 1.0, with the success criteria, ready in the private repository. With both bulletins the volume is about 7,000 items a month, above the 6,000 the estimate assumed from the BOE alone; S7 counts both. Phase 1 closes when the owner sends the report. |
